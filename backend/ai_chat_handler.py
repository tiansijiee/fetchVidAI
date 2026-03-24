"""
AI对话处理器 - 管理视频总结任务的AI对话会话
"""
import uuid
import time
from typing import Dict, List, Optional
from ai_summarizer import AISummarizer


class ChatSession:
    """对话会话"""

    def __init__(self, session_id: str, subtitle_text: str, video_info: Dict = None):
        self.session_id = session_id
        self.subtitle_text = subtitle_text
        self.video_info = video_info or {}
        self.messages = []  # 对话历史
        self.created_at = time.time()
        self.last_activity = time.time()

    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': time.time()
        })
        self.last_activity = time.time()

    def get_chat_history(self, limit: int = 20) -> List[Dict]:
        """获取对话历史（用于AI上下文）"""
        # 转换为OpenAI格式
        history = []
        for msg in self.messages[-limit:]:
            history.append({
                'role': msg['role'],
                'content': msg['content']
            })
        return history

    def is_expired(self, timeout: int = 3600) -> bool:
        """检查会话是否过期"""
        return (time.time() - self.last_activity) > timeout


class AIChatHandler:
    """AI对话处理器 - 管理多个对话会话"""

    # 会话存储
    sessions: Dict[str, ChatSession] = {}

    def __init__(self):
        """初始化AI对话处理器"""
        try:
            self.summarizer = AISummarizer()
        except ValueError as e:
            print(f"[AI_CHAT] 初始化失败: {e}")
            self.summarizer = None

    def create_session(self, subtitle_text: str,
                      video_info: Dict = None) -> Dict:
        """
        创建新的对话会话

        Args:
            subtitle_text: 字幕文本
            video_info: 视频信息

        Returns:
            {
                'success': bool,
                'session_id': str,
                'message': str
            }
        """
        if not self.summarizer:
            return {
                'success': False,
                'message': 'AI服务未初始化，请检查API配置'
            }

        try:
            session_id = str(uuid.uuid4())
            session = ChatSession(session_id, subtitle_text, video_info)
            self.sessions[session_id] = session

            return {
                'success': True,
                'session_id': session_id,
                'message': '会话创建成功'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'创建会话失败: {str(e)}'
            }

    def chat(self, session_id: str, question: str) -> Dict:
        """
        发送问题并获取回答

        Args:
            session_id: 会话ID
            question: 用户问题

        Returns:
            {
                'success': bool,
                'answer': str,
                'message': str
            }
        """
        if not self.summarizer:
            return {
                'success': False,
                'answer': None,
                'message': 'AI服务未初始化'
            }

        # 检查会话是否存在
        session = self.sessions.get(session_id)
        if not session:
            return {
                'success': False,
                'answer': None,
                'message': '会话不存在或已过期'
            }

        try:
            # 添加用户问题到历史
            session.add_message('user', question)

            # 获取对话历史
            chat_history = session.get_chat_history()

            # 调用AI生成回答
            result = self.summarizer.chat_about_video(
                question=question,
                subtitle_text=session.subtitle_text,
                chat_history=chat_history
            )

            if result['success']:
                # 添加AI回答到历史
                session.add_message('assistant', result['answer'])

                return {
                    'success': True,
                    'answer': result['answer'],
                    'message': '问答成功'
                }
            else:
                return {
                    'success': False,
                    'answer': None,
                    'message': result.get('message', '问答失败')
                }

        except Exception as e:
            return {
                'success': False,
                'answer': None,
                'message': f'问答失败: {str(e)}'
            }

    def get_session_info(self, session_id: str) -> Dict:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话信息或None
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            'session_id': session.session_id,
            'created_at': session.created_at,
            'last_activity': session.last_activity,
            'message_count': len(session.messages),
            'video_info': session.video_info
        }

    def cleanup_expired_sessions(self, timeout: int = 3600) -> int:
        """
        清理过期的会话

        Args:
            timeout: 超时时间（秒）

        Returns:
            清理的会话数量
        """
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(timeout)
        ]

        for sid in expired_ids:
            del self.sessions[sid]

        return len(expired_ids)


# 全局AI对话处理器实例
chat_handler = AIChatHandler()


# 便捷函数
def create_chat_session(subtitle_text: str, video_info: Dict = None) -> Dict:
    """创建对话会话的便捷函数"""
    return chat_handler.create_session(subtitle_text, video_info)


def chat_with_ai(session_id: str, question: str) -> Dict:
    """与AI对话的便捷函数"""
    return chat_handler.chat(session_id, question)
