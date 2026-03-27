"""
认证模块 - JWT + bcrypt 用户认证系统
支持用户注册、登录、Token验证
"""
import jwt
import bcrypt
import datetime
from functools import wraps
from flask import request, jsonify, g
import sqlite3
import os
from typing import Dict, Optional, Tuple


# JWT 配置
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7天过期


class AuthManager:
    """认证管理器"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        使用 bcrypt 对密码进行哈希加盐

        Args:
            password: 明文密码

        Returns:
            哈希后的密码
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        验证密码

        Args:
            password: 明文密码
            hashed: 哈希密码

        Returns:
            验证是否通过
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def generate_token(user_id: int, email: str, role: str) -> str:
        """
        生成 JWT Token

        Args:
            user_id: 用户ID
            email: 用户邮箱
            role: 用户角色

        Returns:
            JWT Token
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        解码并验证 JWT Token

        Args:
            token: JWT Token

        Returns:
            解码后的 payload，验证失败返回 None
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("[AUTH] Token已过期", file=__import__('sys').stderr)
            return None
        except jwt.InvalidTokenError:
            print("[AUTH] 无效的Token", file=__import__('sys').stderr)
            return None


class DatabaseManager:
    """数据库管理器"""

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

        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'guest',
                membership_expire TIMESTAMP DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建使用记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                download_count INTEGER DEFAULT 0,
                summary_count INTEGER DEFAULT 0,
                qa_count INTEGER DEFAULT 0,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
            )
        ''')

        # 创建支付记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stripe_payment_intent_id VARCHAR(255) UNIQUE,
                amount INTEGER NOT NULL,
                currency VARCHAR(3) DEFAULT 'CNY',
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def create_user(self, email: str, password: str, role: str = 'user') -> Tuple[bool, Optional[int], str]:
        """
        创建新用户

        Args:
            email: 邮箱
            password: 密码
            role: 角色

        Returns:
            (成功, 用户ID, 消息)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # 检查邮箱是否已存在
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return False, None, '该邮箱已被注册'

            # 哈希密码
            password_hash = AuthManager.hash_password(password)

            # 创建用户
            cursor.execute('''
                INSERT INTO users (email, password_hash, role)
                VALUES (?, ?, ?)
            ''', (email, password_hash, role))

            user_id = cursor.lastrowid

            # 初始化使用记录
            today = datetime.date.today().isoformat()
            cursor.execute('''
                INSERT INTO user_usage (user_id, date, download_count, summary_count, qa_count)
                VALUES (?, ?, 0, 0, 0)
            ''', (user_id, today))

            conn.commit()
            return True, user_id, '注册成功'

        except Exception as e:
            conn.rollback()
            return False, None, f'注册失败: {str(e)}'
        finally:
            conn.close()

    def verify_user(self, email: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """
        验证用户登录

        Args:
            email: 邮箱
            password: 密码

        Returns:
            (成功, 用户信息, 消息)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, email, password_hash, role, membership_expire
                FROM users WHERE email = ?
            ''', (email,))

            user = cursor.fetchone()

            if not user:
                return False, None, '邮箱或密码错误'

            # 验证密码
            if not AuthManager.verify_password(password, user['password_hash']):
                return False, None, '邮箱或密码错误'

            # 检查会员是否过期
            role = user['role']
            if user['membership_expire']:
                expire_time = datetime.datetime.fromisoformat(user['membership_expire'])
                if expire_time < datetime.datetime.now():
                    # 会员过期，降级为普通用户
                    role = 'user'
                    cursor.execute('UPDATE users SET role = ?, membership_expire = NULL WHERE id = ?',
                                   (role, user['id']))
                    conn.commit()

            user_info = {
                'id': user['id'],
                'email': user['email'],
                'role': role,
                'membership_expire': user['membership_expire']
            }

            return True, user_info, '登录成功'

        except Exception as e:
            return False, None, f'登录失败: {str(e)}'
        finally:
            conn.close()

    def get_user(self, user_id: int) -> Optional[Dict]:
        """
        获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            用户信息
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, email, role, membership_expire, created_at
                FROM users WHERE id = ?
            ''', (user_id,))

            user = cursor.fetchone()

            if user:
                return dict(user)
            return None

        except Exception as e:
            print(f"[DB] 获取用户失败: {e}", file=__import__('sys').stderr)
            return None
        finally:
            conn.close()

    def get_user_usage(self, user_id: int) -> Dict:
        """
        获取用户今日使用情况

        Args:
            user_id: 用户ID

        Returns:
            今日使用情况
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            today = datetime.date.today().isoformat()

            cursor.execute('''
                SELECT download_count, summary_count, qa_count, last_reset
                FROM user_usage
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))

            usage = cursor.fetchone()

            if usage:
                # 检查是否需要重置（跨天）
                last_reset = datetime.datetime.fromisoformat(usage['last_reset'])
                today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

                if last_reset < today_start:
                    # 重置计数
                    cursor.execute('''
                        UPDATE user_usage
                        SET download_count = 0, summary_count = 0, qa_count = 0, last_reset = ?
                        WHERE user_id = ? AND date = ?
                    ''', (datetime.datetime.now().isoformat(), user_id, today))
                    conn.commit()
                    return {'download_count': 0, 'summary_count': 0, 'qa_count': 0}

                return dict(usage)
            else:
                # 创建今日记录
                cursor.execute('''
                    INSERT INTO user_usage (user_id, date, download_count, summary_count, qa_count)
                    VALUES (?, ?, 0, 0, 0)
                ''', (user_id, today))
                conn.commit()
                return {'download_count': 0, 'summary_count': 0, 'qa_count': 0}

        except Exception as e:
            print(f"[DB] 获取使用情况失败: {e}", file=__import__('sys').stderr)
            return {'download_count': 0, 'summary_count': 0, 'qa_count': 0}
        finally:
            conn.close()

    def increment_usage(self, user_id: int, usage_type: str) -> bool:
        """
        增加使用次数

        Args:
            user_id: 用户ID
            usage_type: 使用类型 (download/summary/qa)

        Returns:
            是否成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            today = datetime.date.today().isoformat()

            # 确保今日记录存在
            cursor.execute('''
                INSERT OR IGNORE INTO user_usage (user_id, date, download_count, summary_count, qa_count)
                VALUES (?, ?, 0, 0, 0)
            ''', (user_id, today))

            # 增加计数
            column = f'{usage_type}_count'
            cursor.execute(f'''
                UPDATE user_usage
                SET {column} = {column} + 1
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))

            conn.commit()
            return True

        except Exception as e:
            print(f"[DB] 更新使用次数失败: {e}", file=__import__('sys').stderr)
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_user_role(self, user_id: int, role: str, expire_days: int = None) -> bool:
        """
        更新用户角色

        Args:
            user_id: 用户ID
            role: 新角色
            expire_days: 过期天数（None表示永不过期）

        Returns:
            是否成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if expire_days:
                expire_time = datetime.datetime.now() + datetime.timedelta(days=expire_days)
                cursor.execute('''
                    UPDATE users SET role = ?, membership_expire = ?
                    WHERE id = ?
                ''', (role, expire_time.isoformat(), user_id))
            else:
                cursor.execute('''
                    UPDATE users SET role = ?, membership_expire = NULL
                    WHERE id = ?
                ''', (role, user_id))

            conn.commit()
            return True

        except Exception as e:
            print(f"[DB] 更新用户角色失败: {e}", file=__import__('sys').stderr)
            conn.rollback()
            return False
        finally:
            conn.close()

    def create_payment(self, user_id: int, payment_intent_id: str, amount: int,
                       currency: str = 'CNY') -> Tuple[bool, int]:
        """
        创建支付记录

        Args:
            user_id: 用户ID
            payment_intent_id: Stripe支付意图ID
            amount: 金额（分）
            currency: 货币

        Returns:
            (成功, 支付记录ID)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO payments (user_id, stripe_payment_intent_id, amount, currency)
                VALUES (?, ?, ?, ?)
            ''', (user_id, payment_intent_id, amount, currency))

            payment_id = cursor.lastrowid
            conn.commit()
            return True, payment_id

        except Exception as e:
            print(f"[DB] 创建支付记录失败: {e}", file=__import__('sys').stderr)
            conn.rollback()
            return False, 0
        finally:
            conn.close()

    def update_payment_status(self, payment_intent_id: str, status: str) -> bool:
        """
        更新支付状态

        Args:
            payment_intent_id: Stripe支付意图ID
            status: 状态

        Returns:
            是否成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE payments SET status = ?
                WHERE stripe_payment_intent_id = ?
            ''', (status, payment_intent_id))

            conn.commit()
            return True

        except Exception as e:
            print(f"[DB] 更新支付状态失败: {e}", file=__import__('sys').stderr)
            conn.rollback()
            return False
        finally:
            conn.close()


# 全局数据库实例
db_manager = DatabaseManager()


def require_auth(f):
    """
    认证装饰器 - 验证JWT Token

    用法:
        @app.route('/api/protected')
        @require_auth
        def protected_route():
            user = g.current_user
            return jsonify(user)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取Token
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': '未提供认证令牌'}), 401

        # 检查Bearer格式
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': '无效的认证格式'}), 401

        token = auth_header.split(' ')[1]

        # 验证Token
        payload = AuthManager.decode_token(token)
        if not payload:
            return jsonify({'error': '认证令牌无效或已过期'}), 401

        # 获取用户信息
        user = db_manager.get_user(payload['user_id'])
        if not user:
            return jsonify({'error': '用户不存在'}), 401

        # 存储到Flask的g对象
        g.current_user = user
        g.user_id = user['id']
        g.user_role = user['role']

        return f(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles):
    """
    角色权限装饰器 - 验证用户角色

    用法:
        @app.route('/api/premium')
        @require_auth
        @require_role('premium', 'admin')
        def premium_route():
            return jsonify({'message': '会员专属内容'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user_role'):
                return jsonify({'error': '未认证'}), 401

            if g.user_role not in allowed_roles:
                return jsonify({
                    'error': '权限不足',
                    'message': f'该功能需要以下角色之一: {", ".join(allowed_roles)}'
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def check_rate_limit(user_id: int, action: str) -> Tuple[bool, str, Dict]:
    """
    检查用户使用次数限制

    Args:
        user_id: 用户ID
        action: 操作类型 (download/summary/qa)

    Returns:
        (是否允许, 消息, 剩余次数)
    """
    # 获取用户信息
    user = db_manager.get_user(user_id)
    if not user:
        return False, '用户不存在', {}

    role = user['role']
    usage = db_manager.get_user_usage(user_id)

    # 权限配置（统一：游客1次，用户3次，会员无限）
    limits = {
        'guest': {
            'download': 1,
            'summary': 1,
            'qa': 1
        },
        'user': {
            'download': 3,
            'summary': 3,
            'qa': 3
        },
        'premium': {
            'download': -1,  # -1表示无限
            'summary': -1,
            'qa': -1
        }
    }

    role_limits = limits.get(role, limits['guest'])
    limit = role_limits.get(action, 0)

    # 会员无限制
    if limit == -1:
        return True, '无限制', {'remaining': '无限', 'limit': -1}

    # 获取当前使用次数
    count = usage.get(f'{action}_count', 0)

    if count >= limit:
        return False, f'今日{action}次数已达上限({limit}次)', {'remaining': 0, 'limit': limit}

    return True, 'OK', {'remaining': limit - count, 'limit': limit}


# Flask 路由辅助函数
def create_auth_routes(app):
    """
    创建认证相关路由

    Args:
        app: Flask应用实例
    """
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """用户注册"""
        data = request.get_json()

        email = data.get('email', '').strip()
        password = data.get('password', '')

        # 验证输入
        if not email or not password:
            return jsonify({'error': '邮箱和密码不能为空'}), 400

        if len(password) < 6:
            return jsonify({'error': '密码长度至少6位'}), 400

        # 创建用户
        success, user_id, message = db_manager.create_user(email, password)

        if success:
            return jsonify({
                'message': message,
                'user_id': user_id
            }), 201
        else:
            return jsonify({'error': message}), 400

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """用户登录"""
        data = request.get_json()

        email = data.get('email', '').strip()
        password = data.get('password', '')

        # 验证输入
        if not email or not password:
            return jsonify({'error': '邮箱和密码不能为空'}), 400

        # 验证用户
        success, user_info, message = db_manager.verify_user(email, password)

        if success:
            # 生成Token
            token = AuthManager.generate_token(
                user_info['id'],
                user_info['email'],
                user_info['role']
            )

            # 获取今日使用情况
            usage = db_manager.get_user_usage(user_info['id'])

            # 获取剩余次数配额
            quota = None
            try:
                from auth.quota_manager import quota_manager
                quota = quota_manager.get_remaining(user_info['id'], None)
            except Exception as e:
                print(f"[AUTH] 获取剩余次数失败: {e}", file=__import__('sys').stderr)

            return jsonify({
                'message': message,
                'token': token,
                'user': {
                    'id': user_info['id'],
                    'email': user_info['email'],
                    'role': user_info['role'],
                    'membership_expire': user_info['membership_expire']
                },
                'usage': usage,
                'quota': quota  # 新增：返回剩余次数
            }), 200
        else:
            return jsonify({'error': message}), 401

    @app.route('/api/auth/me', methods=['GET'])
    @require_auth
    def get_current_user():
        """获取当前用户信息"""
        usage = db_manager.get_user_usage(g.user_id)

        return jsonify({
            'user': g.current_user,
            'usage': usage
        }), 200

    @app.route('/api/auth/usage', methods=['GET'])
    @require_auth
    def get_usage():
        """获取使用情况"""
        usage = db_manager.get_user_usage(g.user_id)

        return jsonify({
            'usage': usage,
            'user_role': g.user_role
        }), 200

    @app.route('/api/auth/check-permission', methods=['POST'])
    @require_auth
    def check_permission():
        """检查权限"""
        data = request.get_json()
        action = data.get('action', '')

        allowed, message, info = check_rate_limit(g.user_id, action)

        return jsonify({
            'allowed': allowed,
            'message': message,
            'info': info
        }), 200

    @app.route('/api/quota/remaining', methods=['GET'])
    def get_quota_remaining():
        """获取剩余次数（支持游客和登录用户）"""
        try:
            # 导入quota_manager
            from auth.quota_manager import quota_manager

            # 获取用户身份
            auth_header = request.headers.get('Authorization')
            user_id = None

            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                payload = AuthManager.decode_token(token)
                if payload:
                    user_id = payload.get('user_id')

            # 获取fingerprint
            fingerprint = request.headers.get('X-Fingerprint')

            # 获取剩余次数
            result = quota_manager.get_remaining(user_id, fingerprint)

            return jsonify({
                'success': True,
                'data': result
            }), 200

        except Exception as e:
            print(f"[QUOTA] 获取剩余次数失败: {e}", file=__import__('sys').stderr)
            return jsonify({
                'success': False,
                'error': '获取剩余次数失败'
            }), 500


if __name__ == '__main__':
    # 测试代码
    db = DatabaseManager(':memory:')

    # 测试注册
    success, user_id, msg = db.create_user('test@example.com', 'password123')
    print(f"注册: {success}, {user_id}, {msg}")

    # 测试登录
    success, user_info, msg = db.verify_user('test@example.com', 'password123')
    print(f"登录: {success}, {user_info}, {msg}")

    # 测试Token
    if success:
        token = AuthManager.generate_token(user_info['id'], user_info['email'], user_info['role'])
        print(f"Token: {token}")

        payload = AuthManager.decode_token(token)
        print(f"解码: {payload}")
