"""
权限校验装饰器和中间件
为核心功能接口添加使用次数限制和权限控制
"""
from functools import wraps
from flask import request, jsonify, g
from typing import Callable, Dict, List, Tuple
from auth.auth import db_manager, check_rate_limit


class PermissionError(Exception):
    """权限错误"""
    def __init__(self, message: str, code: int = 403):
        self.message = message
        self.code = code
        super().__init__(self.message)


class RateLimitError(Exception):
    """次数限制错误"""
    def __init__(self, message: str, remaining: int = 0, limit: int = 0):
        self.message = message
        self.remaining = remaining
        self.limit = limit
        super().__init__(self.message)


def check_permission(action: str, require_auth: bool = True):
    """
    权限检查装饰器

    Args:
        action: 操作类型 (download/summary/qa/mindmap)
        require_auth: 是否需要认证

    用法:
        @app.route('/api/ai/summarize', methods=['POST'])
        @check_permission('summary', require_auth=True)
        def ai_summarize():
            # 业务逻辑
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 游客模式：不需要认证但次数限制严格
            if not require_auth:
                # 检查是否有Token，有则使用用户限制
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    # 已登录，继续正常流程
                    pass
                else:
                    # 未登录，使用游客限制
                    allowed, message, info = check_rate_limit(0, action)  # user_id=0 表示游客
                    if not allowed:
                        return jsonify({
                            'error': message,
                            'code': 'RATE_LIMIT_EXCEEDED',
                            'require_login': True,
                            'info': info
                        }), 403

                    # 执行业务逻辑
                    result = f(*args, **kwargs)

                    # 如果是成功的响应，增加游客计数（使用IP或Session）
                    if isinstance(result, tuple) and len(result) >= 2:
                        response, status_code = result[0], result[1]
                    else:
                        response, status_code = result, 200

                    # TODO: 这里可以添加基于IP的计数逻辑

                    return result

            # 需要认证的情况
            if not hasattr(g, 'user_id'):
                return jsonify({
                    'error': '请先登录',
                    'code': 'AUTH_REQUIRED',
                    'require_login': True
                }), 401

            # 检查使用次数
            allowed, message, info = check_rate_limit(g.user_id, action)

            if not allowed:
                return jsonify({
                    'error': message,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'info': info,
                    'user_role': g.user_role
                }), 403

            # 执行业务逻辑
            result = f(*args, **kwargs)

            # 如果是成功的响应，增加使用计数
            if isinstance(result, tuple):
                response, status_code = result[0], result[1]
                if 200 <= status_code < 300 and status_code != 204:
                    db_manager.increment_usage(g.user_id, action)
            else:
                response = result
                db_manager.increment_usage(g.user_id, action)

            return result

        return decorated_function
    return decorator


def require_role(*roles: str):
    """
    角色要求装饰器

    Args:
        *roles: 允许的角色列表

    用法:
        @app.route('/api/export/hd', methods=['POST'])
        @require_auth
        @require_role('premium', 'admin')
        def export_hd():
            # 只有会员和管理员可用
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user_role'):
                return jsonify({
                    'error': '请先登录',
                    'code': 'AUTH_REQUIRED'
                }), 401

            if g.user_role not in roles:
                return jsonify({
                    'error': '该功能需要会员权限',
                    'code': 'ROLE_REQUIRED',
                    'require_role': roles[0] if roles else 'premium',
                    'current_role': g.user_role
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def check_feature_access(feature: str) -> Tuple[bool, Dict]:
    """
    检查功能访问权限

    Args:
        feature: 功能名称

    Returns:
        (是否允许, 限制信息)
    """
    # 功能配置
    feature_config = {
        'download': {
            'guest': {'limit': 1, 'auth_required': False},
            'user': {'limit': 3, 'auth_required': True},
            'premium': {'limit': -1, 'auth_required': False}
        },
        'summary': {
            'guest': {'limit': 1, 'auth_required': False},
            'user': {'limit': 3, 'auth_required': True},
            'premium': {'limit': -1, 'auth_required': False}
        },
        'qa': {
            'guest': {'limit': 1, 'auth_required': False},
            'user': {'limit': 3, 'auth_required': True},
            'premium': {'limit': -1, 'auth_required': False}
        },
        'mindmap_export': {
            'guest': {'formats': ['md'], 'auth_required': False},
            'user': {'formats': ['md', 'png', 'svg'], 'auth_required': True},
            'premium': {'formats': ['md', 'png', 'svg', 'pdf'], 'auth_required': False}
        }
    }

    config = feature_config.get(feature, {})

    if hasattr(g, 'user_role'):
        role_config = config.get(g.user_role, config.get('user', {}))
    else:
        role_config = config.get('guest', {})

    return True, role_config


# 权限响应辅助函数
def permission_response(error: str, code: str = 'PERMISSION_DENIED',
                        **extra) -> Tuple[Dict, int]:
    """
    生成统一的权限错误响应

    Args:
        error: 错误消息
        code: 错误代码
        **extra: 额外信息

    Returns:
        (响应字典, 状态码)
    """
    response = {
        'error': error,
        'code': code
    }
    response.update(extra)
    return response, 403


# 导出装饰器
__all__ = [
    'check_permission',
    'require_role',
    'check_feature_access',
    'permission_response',
    'PermissionError',
    'RateLimitError'
]
