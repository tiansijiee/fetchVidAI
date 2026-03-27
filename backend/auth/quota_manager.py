"""
次数配额管理器
支持游客（fingerprint）和登录用户（user_id）的次数管理
- 游客：解析1次/天，下载1次/天
- 普通用户：解析3次/天，下载3次/天
- VIP用户：无限制
"""
import sqlite3
import os
import datetime
from typing import Dict, Optional, Tuple
from functools import wraps
from flask import request, jsonify, g


class QuotaManager:
    """次数配额管理器"""

    # 次数配置
    QUOTA_LIMITS = {
        'guest': {'parse': 1, 'download': 1},
        'user': {'parse': 3, 'download': 3},
        'premium': {'parse': -1, 'download': -1}  # -1表示无限
    }

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.db')
        self.db_path = db_path
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建用户次数表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quota (
                user_id INTEGER,
                date DATE NOT NULL,
                parse_count INTEGER DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        ''')

        # 创建游客次数表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guest_quota (
                fingerprint VARCHAR(255),
                date DATE NOT NULL,
                parse_count INTEGER DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                PRIMARY KEY (fingerprint, date)
            )
        ''')

        # 创建幂等记录表（防止重复扣次）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_log (
                request_id VARCHAR(255) PRIMARY KEY,
                user_id INTEGER,
                fingerprint VARCHAR(255),
                action VARCHAR(50),
                consumed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _get_today(self) -> str:
        """获取今天的日期字符串"""
        return datetime.date.today().isoformat()

    def _get_role(self, user_id: Optional[int]) -> str:
        """获取用户角色"""
        if user_id is None:
            return 'guest'

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()

            if user:
                role = user['role']

                # 检查会员是否过期
                if role == 'premium':
                    cursor.execute('SELECT membership_expire FROM users WHERE id = ?', (user_id,))
                    expire_data = cursor.fetchone()
                    if expire_data and expire_data['membership_expire']:
                        try:
                            expire_time = datetime.datetime.fromisoformat(expire_data['membership_expire'])
                            if expire_time < datetime.datetime.now():
                                # 会员过期，降级为普通用户
                                role = 'user'
                                cursor.execute('UPDATE users SET role = ?, membership_expire = NULL WHERE id = ?',
                                               (role, user_id))
                                conn.commit()
                        except:
                            pass

                return role
            return 'guest'
        except Exception as e:
            print(f"[QUOTA] 获取用户角色失败: {e}", file=__import__('sys').stderr)
            return 'guest'
        finally:
            conn.close()

    def check_quota(self, user_id: Optional[int] = None, fingerprint: Optional[str] = None,
                    action: str = 'parse') -> Tuple[bool, str, Dict]:
        """
        检查次数配额

        Args:
            user_id: 用户ID（登录用户）
            fingerprint: 游客指纹
            action: 操作类型 ('parse' 或 'download')

        Returns:
            (是否允许, 消息, 剩余次数信息)
        """
        role = self._get_role(user_id)

        # VIP用户无限制
        if role == 'premium':
            return True, '无限制', {'remaining': '无限', 'limit': -1, 'role': role}

        # 获取限制配置
        limits = self.QUOTA_LIMITS.get(role, self.QUOTA_LIMITS['guest'])
        limit = limits.get(action, 0)

        if limit == -1:
            return True, '无限制', {'remaining': '无限', 'limit': -1, 'role': role}

        # 获取当前使用次数
        count = self._get_count(user_id, fingerprint, action)

        if count >= limit:
            remaining = 0
            message = self._get_exceeded_message(role, action)
            return False, message, {'remaining': remaining, 'limit': limit, 'role': role}

        remaining = limit - count
        return True, 'OK', {'remaining': remaining, 'limit': limit, 'role': role}

    def _get_exceeded_message(self, role: str, action: str) -> str:
        """获取次数超限提示消息"""
        action_name = '解析' if action == 'parse' else '下载'

        if role == 'guest':
            return f'今日{action_name}次数已用完，注册后每日3次'
        else:
            return f'今日{action_name}次数已用完，开通VIP无限使用'

    def _get_count(self, user_id: Optional[int], fingerprint: Optional[str], action: str) -> int:
        """获取已使用次数"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            today = self._get_today()

            if user_id is not None:
                # 登录用户
                cursor.execute('''
                    SELECT {action}_count FROM user_quota
                    WHERE user_id = ? AND date = ?
                '''.format(action=action), (user_id, today))

                result = cursor.fetchone()
                return result['{}_count'.format(action)] if result else 0

            elif fingerprint:
                # 游客
                cursor.execute('''
                    SELECT {action}_count FROM guest_quota
                    WHERE fingerprint = ? AND date = ?
                '''.format(action=action), (fingerprint, today))

                result = cursor.fetchone()
                return result['{}_count'.format(action)] if result else 0

            return 0

        except Exception as e:
            print(f"[QUOTA] 获取次数失败: {e}", file=__import__('sys').stderr)
            return 0
        finally:
            conn.close()

    def consume_quota(self, user_id: Optional[int] = None, fingerprint: Optional[str] = None,
                     action: str = 'parse', request_id: Optional[str] = None) -> bool:
        """
        消耗次数配额（带幂等检查）

        Args:
            user_id: 用户ID（登录用户）
            fingerprint: 游客指纹
            action: 操作类型 ('parse' 或 'download')
            request_id: 请求ID（用于幂等检查）

        Returns:
            是否成功扣减次数
        """
        # 幂等检查
        if request_id and self._is_consumed(request_id):
            print(f"[QUOTA] 请求 {request_id} 已扣次，跳过", file=__import__('sys').stderr)
            return True

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            today = self._get_today()

            if user_id is not None:
                # 登录用户
                cursor.execute('''
                    INSERT OR IGNORE INTO user_quota (user_id, date, parse_count, download_count)
                    VALUES (?, ?, 0, 0)
                ''', (user_id, today))

                column = f'{action}_count'
                cursor.execute(f'''
                    UPDATE user_quota
                    SET {column} = {column} + 1
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today))

                # 记录幂等
                if request_id:
                    cursor.execute('''
                        INSERT OR REPLACE INTO request_log (request_id, user_id, action, consumed)
                        VALUES (?, ?, ?, 1)
                    ''', (request_id, user_id, action))

                conn.commit()
                print(f"[QUOTA] 用户 {user_id} 消耗 {action} 次数成功", file=__import__('sys').stderr)
                return True

            elif fingerprint:
                # 游客
                cursor.execute('''
                    INSERT OR IGNORE INTO guest_quota (fingerprint, date, parse_count, download_count)
                    VALUES (?, ?, 0, 0)
                ''', (fingerprint, today))

                column = f'{action}_count'
                cursor.execute(f'''
                    UPDATE guest_quota
                    SET {column} = {column} + 1
                    WHERE fingerprint = ? AND date = ?
                ''', (fingerprint, today))

                # 记录幂等
                if request_id:
                    cursor.execute('''
                        INSERT OR REPLACE INTO request_log (request_id, fingerprint, action, consumed)
                        VALUES (?, ?, ?, 1)
                    ''', (request_id, fingerprint, action))

                conn.commit()
                print(f"[QUOTA] 游客 {fingerprint[:8]}... 消耗 {action} 次数成功", file=__import__('sys').stderr)
                return True

            return False

        except Exception as e:
            print(f"[QUOTA] 消耗次数失败: {e}", file=__import__('sys').stderr)
            conn.rollback()
            return False
        finally:
            conn.close()

    def _is_consumed(self, request_id: str) -> bool:
        """检查请求是否已扣次"""
        if not request_id:
            return False

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT consumed FROM request_log WHERE request_id = ?', (request_id,))
            result = cursor.fetchone()
            return result and result['consumed'] == 1
        except Exception:
            return False
        finally:
            conn.close()

    def get_remaining(self, user_id: Optional[int] = None, fingerprint: Optional[str] = None) -> Dict:
        """
        获取剩余次数

        Returns:
            {'parse_remaining': int, 'download_remaining': int, 'role': str}
        """
        role = self._get_role(user_id)

        if role == 'premium':
            return {
                'parse_remaining': '无限',
                'download_remaining': '无限',
                'role': role
            }

        limits = self.QUOTA_LIMITS.get(role, self.QUOTA_LIMITS['guest'])

        parse_limit = limits.get('parse', 0)
        download_limit = limits.get('download', 0)

        parse_count = self._get_count(user_id, fingerprint, 'parse')
        download_count = self._get_count(user_id, fingerprint, 'download')

        parse_remaining = max(0, parse_limit - parse_count) if parse_limit != -1 else '无限'
        download_remaining = max(0, download_limit - download_count) if download_limit != -1 else '无限'

        return {
            'parse_remaining': parse_remaining,
            'download_remaining': download_remaining,
            'parse_count': parse_count,
            'download_count': download_count,
            'parse_limit': parse_limit,
            'download_limit': download_limit,
            'role': role
        }

    def get_identity_from_request(self) -> Tuple[Optional[int], Optional[str]]:
        """
        从请求中提取用户身份

        Returns:
            (user_id, fingerprint)
        """
        # 尝试从Authorization头获取token
        auth_header = request.headers.get('Authorization')
        user_id = None

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from auth.auth import AuthManager
                payload = AuthManager.decode_token(token)
                if payload:
                    user_id = payload.get('user_id')
            except Exception as e:
                print(f"[QUOTA] Token解析失败: {e}", file=__import__('sys').stderr)

        # 从请求头获取fingerprint
        fingerprint = request.headers.get('X-Fingerprint')

        return user_id, fingerprint


# 创建全局实例
quota_manager = QuotaManager()


def require_quota(action: str, consume_on_success: bool = True):
    """
    权限检查装饰器

    Args:
        action: 操作类型 ('parse' 或 'download')
        consume_on_success: 是否在成功时消耗次数

    用法:
        @app.route('/api/parse', methods=['POST'])
        @require_quota('parse', consume_on_success=False)
        def parse_video():
            # 业务逻辑
            pass

        @app.route('/api/summarize', methods=['POST'])
        @require_quota('parse', consume_on_success=True)
        def summarize_video():
            # 业务逻辑完成后自动扣次
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取用户身份
            user_id, fingerprint = quota_manager.get_identity_from_request()

            # 获取request_id用于幂等检查
            request_id = request.headers.get('X-Request-ID')

            # 检查次数配额
            allowed, message, info = quota_manager.check_quota(user_id, fingerprint, action)

            if not allowed:
                return jsonify({
                    'error': message,
                    'code': 'QUOTA_EXCEEDED',
                    'info': info,
                    'require_login': info.get('role') == 'guest',
                    'user_role': info.get('role', 'guest')
                }), 403

            # 存储身份信息到g对象
            g.quota_user_id = user_id
            g.quota_fingerprint = fingerprint
            g.quota_request_id = request_id
            g.quota_action = action
            g.quota_consume = consume_on_success

            # 执行业务逻辑
            result = f(*args, **kwargs)

            # 如果成功且需要扣次
            if consume_on_success:
                status_code = 200
                if isinstance(result, tuple):
                    response, status_code = result[0], result[1]
                else:
                    response = result

                # 只在2xx成功响应时扣次
                if 200 <= status_code < 300:
                    quota_manager.consume_quota(user_id, fingerprint, action, request_id)

            return result

        return decorated_function
    return decorator


def consume_parse_quota():
    """
    手动触发解析次数扣减（用于SSE流式结束等场景）
    需要在业务逻辑中调用
    """
    if hasattr(g, 'quota_user_id') and hasattr(g, 'quota_fingerprint') and hasattr(g, 'quota_request_id'):
        quota_manager.consume_quota(
            g.quota_user_id,
            g.quota_fingerprint,
            'parse',
            g.quota_request_id
        )
        return True
    return False


def consume_download_quota():
    """
    手动触发下载次数扣减
    需要在业务逻辑中调用
    """
    if hasattr(g, 'quota_user_id') and hasattr(g, 'quota_fingerprint') and hasattr(g, 'quota_request_id'):
        quota_manager.consume_quota(
            g.quota_user_id,
            g.quota_fingerprint,
            'download',
            g.quota_request_id
        )
        return True
    return False
