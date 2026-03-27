"""
Stripe 支付处理模块
支持会员订阅支付、Webhook 验证
"""
import os
import stripe
import json
import hmac
import hashlib
from flask import request, jsonify, Response
from typing import Dict, Optional, Tuple
from auth.auth import db_manager, require_auth


# Stripe 配置
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID', '')  # 会员订阅价格ID

# 初始化 Stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


class StripeHandler:
    """Stripe 支付处理器"""

    # 会员套餐配置（单位：分）
    MEMBERSHIP_PLANS = {
        'monthly': {
            'name': '月度会员',
            'price': 2900,  # 29元
            'duration_days': 30
        },
        'quarterly': {
            'name': '季度会员',
            'price': 7900,  # 79元
            'duration_days': 90
        },
        'yearly': {
            'name': '年度会员',
            'price': 28800,  # 288元（约24元/月）
            'duration_days': 365
        }
    }

    @staticmethod
    def create_payment_intent(user_id: int, plan_type: str = 'monthly') -> Tuple[bool, Optional[Dict], str]:
        """
        创建支付意图

        Args:
            user_id: 用户ID
            plan_type: 套餐类型 (monthly/quarterly/yearly)

        Returns:
            (成功, 支付信息, 消息)
        """
        try:
            if not STRIPE_SECRET_KEY:
                return False, None, '支付服务未配置'

            plan = StripeHandler.MEMBERSHIP_PLANS.get(plan_type)
            if not plan:
                return False, None, '无效的套餐类型'

            # 创建支付意图
            intent = stripe.PaymentIntent.create(
                amount=plan['price'],
                currency='cny',
                metadata={
                    'user_id': str(user_id),
                    'plan_type': plan_type,
                    'duration_days': str(plan['duration_days'])
                },
                description=f"{plan['name']} - FetchVid AI"
            )

            # 创建支付记录
            db_manager.create_payment(user_id, intent.id, plan['price'], 'cny')

            return True, {
                'client_secret': intent.client_secret,
                'publishable_key': STRIPE_PUBLISHABLE_KEY,
                'amount': plan['price'],
                'plan_name': plan['name'],
                'plan_type': plan_type
            }, '支付意图创建成功'

        except stripe.error.StripeError as e:
            return False, None, f'Stripe 错误: {str(e)}'
        except Exception as e:
            return False, None, f'创建支付失败: {str(e)}'

    @staticmethod
    def confirm_payment(payment_intent_id: str) -> Tuple[bool, str]:
        """
        确认支付状态

        Args:
            payment_intent_id: 支付意图ID

        Returns:
            (成功, 消息)
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == 'succeeded':
                # 更新支付状态
                db_manager.update_payment_status(payment_intent_id, 'succeeded')

                # 更新用户角色
                user_id = int(intent.metadata.get('user_id', 0))
                duration_days = int(intent.metadata.get('duration_days', 30))

                db_manager.update_user_role(user_id, 'premium', duration_days)

                return True, '支付成功，会员已开通'
            elif intent.status == 'pending':
                return False, '支付处理中'
            elif intent.status in ['canceled', 'failed']:
                db_manager.update_payment_status(payment_intent_id, intent.status)
                return False, f'支付{intent.status}'
            else:
                return False, f'支付状态: {intent.status}'

        except stripe.error.StripeError as e:
            return False, f'Stripe 错误: {str(e)}'
        except Exception as e:
            return False, f'确认支付失败: {str(e)}'

    @staticmethod
    def verify_webhook(payload: bytes, sig_header: str) -> Tuple[bool, Optional[Dict]]:
        """
        验证 Stripe Webhook 签名

        Args:
            payload: 请求体
            sig_header: Stripe签名头

        Returns:
            (验证成功, 事件数据)
        """
        try:
            if not STRIPE_WEBHOOK_SECRET:
                return False, None

            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )

            return True, event

        except ValueError:
            # 无效的 payload
            return False, None
        except stripe.error.SignatureVerificationError:
            # 无效的签名
            return False, None
        except Exception as e:
            print(f"[STRIPE] Webhook验证错误: {e}", file=__import__('sys').stderr)
            return False, None

    @staticmethod
    def handle_webhook_event(event: Dict) -> Tuple[bool, str]:
        """
        处理 Webhook 事件

        Args:
            event: Stripe 事件对象

        Returns:
            (处理成功, 消息)
        """
        try:
            event_type = event['type']
            data = event['data']['object']

            if event_type == 'payment_intent.succeeded':
                # 支付成功
                payment_intent_id = data['id']
                user_id = int(data.get('metadata', {}).get('user_id', 0))
                duration_days = int(data.get('metadata', {}).get('duration_days', 30))

                # 更新支付状态
                db_manager.update_payment_status(payment_intent_id, 'succeeded')

                # 更新用户角色
                if user_id > 0:
                    db_manager.update_user_role(user_id, 'premium', duration_days)

                return True, '支付成功，会员已开通'

            elif event_type == 'payment_intent.payment_failed':
                # 支付失败
                payment_intent_id = data['id']
                db_manager.update_payment_status(payment_intent_id, 'failed')

                return True, '支付失败'

            elif event_type == 'payment_intent.canceled':
                # 支付取消
                payment_intent_id = data['id']
                db_manager.update_payment_status(payment_intent_id, 'canceled')

                return True, '支付已取消'

            else:
                return True, f'事件已记录: {event_type}'

        except Exception as e:
            return False, f'处理事件失败: {str(e)}'


def create_payment_routes(app):
    """
    创建支付相关路由

    Args:
        app: Flask应用实例
    """

    @app.route('/api/payment/plans', methods=['GET'])
    def get_plans():
        """获取会员套餐列表"""
        return jsonify({
            'plans': StripeHandler.MEMBERSHIP_PLANS,
            'publishable_key': STRIPE_PUBLISHABLE_KEY
        }), 200

    @app.route('/api/payment/create-intent', methods=['POST'])
    @require_auth
    def create_payment_intent():
        """创建支付意图"""
        data = request.get_json()
        plan_type = data.get('plan_type', 'monthly')

        success, result, message = StripeHandler.create_payment_intent(g.user_id, plan_type)

        if success:
            return jsonify({
                'message': message,
                'payment': result
            }), 200
        else:
            return jsonify({'error': message}), 400

    @app.route('/api/payment/confirm', methods=['POST'])
    @require_auth
    def confirm_payment():
        """确认支付状态"""
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')

        if not payment_intent_id:
            return jsonify({'error': '缺少支付意图ID'}), 400

        success, message = StripeHandler.confirm_payment(payment_intent_id)

        if success:
            # 获取更新后的用户信息
            user = db_manager.get_user(g.user_id)

            return jsonify({
                'message': message,
                'user': user
            }), 200
        else:
            return jsonify({'error': message}), 400

    @app.route('/api/payment/webhook', methods=['POST'])
    def stripe_webhook():
        """Stripe Webhook 接收端"""
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature', '')

        # 验证 webhook
        success, event = StripeHandler.verify_webhook(payload, sig_header)

        if not success:
            return jsonify({'error': '无效的签名'}), 400

        # 处理事件
        success, message = StripeHandler.handle_webhook_event(event)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400

    @app.route('/api/payment/history', methods=['GET'])
    @require_auth
    def get_payment_history():
        """获取支付历史"""
        import sqlite3

        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, amount, currency, status, created_at
                FROM payments
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (g.user_id,))

            payments = [dict(row) for row in cursor.fetchall()]

            return jsonify({'payments': payments}), 200

        except Exception as e:
            return jsonify({'error': f'获取历史失败: {str(e)}'}), 500
        finally:
            conn.close()


# 导出配置
def get_stripe_config():
    """获取 Stripe 配置"""
    return {
        'publishable_key': STRIPE_PUBLISHABLE_KEY,
        'plans': StripeHandler.MEMBERSHIP_PLANS,
        'enabled': bool(STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY)
    }
