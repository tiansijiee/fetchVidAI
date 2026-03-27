"""
AI功能路由模块 - 生产版本
使用真实的字幕提取和AI总结，禁止测试模式
支持4个Tab功能：视频总结、字幕文本、思维导图、AI问答
"""
import sys
import json
import os
import re
from flask import Blueprint, request, jsonify, Response, stream_with_context


def _parse_time_to_seconds(time_str: str) -> float:
    """
    将时间字符串转换为秒数

    支持格式：
    - HH:MM:SS
    - MM:SS
    - SS (秒数)
    - 直接传入秒数(float/int)

    Returns:
        float: 秒数
    """
    if not time_str:
        return 0.0

    # 如果已经是数字类型，直接返回
    if isinstance(time_str, (int, float)):
        return float(time_str)

    # 尝试直接转换为数字（秒）
    try:
        return float(time_str)
    except (ValueError, TypeError):
        pass

    # 处理 HH:MM:SS 或 MM:SS 格式
    time_str = str(time_str).strip()
    parts = time_str.split(':')

    try:
        if len(parts) == 3:
            # HH:MM:SS
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            # MM:SS
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        elif len(parts) == 1:
            # 只有数字
            return float(parts[0])
    except (ValueError, TypeError):
        pass

    return 0.0


def _format_seconds_to_time(seconds: float) -> str:
    """
    将秒数转换为时间字符串格式 (MM:SS 或 HH:MM:SS)

    Args:
        seconds: 秒数

    Returns:
        str: 时间字符串，如 "01:23" 或 "1:23:45"
    """
    if not seconds or seconds < 0:
        return "00:00"

    seconds = float(seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

# 导入字幕提取器
from subtitle_extractor import SubtitleExtractor, traditional_to_simplified

# 导入音频转写器（延迟导入，避免模块导入失败）
ASR_AVAILABLE = True  # 始终设置为True，在运行时检查
_audio_transcriber = None

def get_audio_transcriber():
    """获取音频转写器实例"""
    global _audio_transcriber
    if _audio_transcriber is None:
        try:
            from audio_transcriber import AudioTranscriber
            _audio_transcriber = AudioTranscriber
        except ImportError:
            _audio_transcriber = False
    return _audio_transcriber

# 导入AI总结器
try:
    from ai_summarizer import AISummarizer, create_summarizer
    from dotenv import load_dotenv
    load_dotenv()

    # 检查API密钥
    API_KEY = os.getenv('DEEPSEEK_API_KEY')
    if API_KEY and API_KEY != 'your_deepseek_api_key_here':
        AI_AVAILABLE = True
        summarizer = create_summarizer()
        print("[AI_ROUTES] Deepseek AI服务已启用", file=sys.stderr)
    else:
        AI_AVAILABLE = False
        summarizer = None
        print("[AI_ROUTES] 警告: DEEPSEEK_API_KEY未配置", file=sys.stderr)
except ImportError as e:
    print(f"[AI_ROUTES] AI模块导入失败: {e}", file=sys.stderr)
    AI_AVAILABLE = False
    summarizer = None

# 导入认证模块
from auth.auth import AuthManager, db_manager, check_rate_limit

# 创建蓝图
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# 全局任务存储
summarize_tasks = {}


def init_ai_routes():
    """初始化AI路由 - 生产模式"""
    if AI_AVAILABLE:
        print("[AI_ROUTES] AI服务初始化成功（生产模式）", file=sys.stderr)
        return True
    else:
        print("[AI_ROUTES] 警告: AI服务未配置，请设置DEEPSEEK_API_KEY", file=sys.stderr)
        return False


@ai_bp.route('/health', methods=['GET'])
def ai_health_check():
    """AI服务健康检查"""
    features = ['summarize', 'subtitle', 'mindmap', 'chat']

    # 动态检查ASR可用性
    AudioTranscriber = get_audio_transcriber()
    asr_enabled = False
    if AudioTranscriber:
        asr_enabled = AudioTranscriber.check_ffmpeg() and AudioTranscriber.check_whisper()

    return jsonify({
        'status': 'ok',
        'message': 'AI服务运行中',
        'ai_enabled': AI_AVAILABLE,
        'asr_enabled': asr_enabled,
        'features': features
    })


@ai_bp.route('/check-subtitle', methods=['POST'])
def check_subtitle():
    """检查视频是否有字幕"""
    try:
        print("[AI] check_subtitle called", file=sys.stderr)
        data = request.get_json()
        url = data.get('url', '').strip()

        if not url:
            return jsonify({'success': False, 'message': '请输入视频链接'}), 400

        # 尝试提取字幕
        result = SubtitleExtractor.extract_subtitles(url)

        return jsonify({
            'success': True,
            'has_subtitle': result.get('has_subtitle', False),
            'can_fallback_to_audio': result.get('can_fallback_to_audio', False),
            'message': result.get('message', '检查完成')
        })

    except Exception as e:
        print(f"[AI] 字幕检查错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            'success': False,
            'message': f'字幕检查失败: {str(e)}'
        }), 500


@ai_bp.route('/summarize/stream', methods=['POST'])
def summarize_video():
    """
    AI视频总结 - 生产版本（SSE流式输出）
    流程：
    1. 尝试提取字幕
    2. 如果没有字幕，使用ASR转写音频
    3. 使用AI生成总结（流式输出）
    """
    try:
        print("[AI] summarize_video (stream) called", file=sys.stderr)

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        url = data.get('url', '').strip()
        if not url:
            return jsonify({'success': False, 'message': '请输入视频链接'}), 400

        video_title = data.get('title', '视频内容')
        video_description = data.get('description', '')
        use_asr = data.get('use_asr', False)

        print(f"[AI] Processing: {video_title[:50]}", file=sys.stderr)

        def generate():
            """生成器函数，用于SSE流式输出"""
            try:
                # 发送开始事件
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在分析视频...'}, ensure_ascii=False)}\n\n"

                # ========== 步骤1: 尝试提取字幕 ==========
                subtitle_result = None
                subtitle_text = None

                if not use_asr:
                    yield f"data: {json.dumps({'type': 'progress', 'message': '正在提取字幕...'}, ensure_ascii=False)}\n\n"
                    subtitle_result = SubtitleExtractor.extract_subtitles(url)

                    if subtitle_result.get('success') and subtitle_result.get('has_subtitle'):
                        subtitle_text = subtitle_result.get('full_text', '')
                        print(f"[AI] ✓ 字幕提取成功! 长度: {len(subtitle_text)}字符", file=sys.stderr)
                    else:
                        print(f"[AI] ✗ 字幕提取失败", file=sys.stderr)

                # ========== 步骤2: 如果没有字幕，尝试ASR转写 ==========
                if not subtitle_text:
                    if subtitle_result and subtitle_result.get('can_fallback_to_audio'):
                        yield f"data: {json.dumps({'type': 'progress', 'message': '正在进行音频转写(ASR)，这可能需要1-2分钟...'}, ensure_ascii=False)}\n\n"

                        AudioTranscriber = get_audio_transcriber()
                        if AudioTranscriber:
                            if AudioTranscriber.check_ffmpeg() and AudioTranscriber.check_whisper():
                                asr_result = AudioTranscriber.transcribe_from_url(url, model_size='tiny')

                                if asr_result.get('success'):
                                    subtitle_text = asr_result.get('full_text', '')
                                    print(f"[AI] ✓ ASR转写成功! 长度: {len(subtitle_text)}字符", file=sys.stderr)
                                else:
                                    # ASR失败，提供更友好的错误信息
                                    error_msg = asr_result.get('message', 'Unknown')
                                    print(f"[AI] ASR失败: {error_msg}", file=sys.stderr)

                                    # 检查是否是音频下载失败
                                    if '下载' in error_msg or 'download' in error_msg.lower():
                                        yield f"data: {json.dumps({'type': 'error', 'message': '无法下载视频音频，可能是网络问题或视频限制了访问。建议：1) 检查网络连接 2) 尝试其他有字幕的视频 3) 使用YouTube视频可能更稳定'}, ensure_ascii=False)}\n\n"
                                    else:
                                        yield f"data: {json.dumps({'type': 'error', 'message': f'ASR转写失败: {error_msg}。建议尝试其他有字幕的视频。'}, ensure_ascii=False)}\n\n"
                                    return
                            else:
                                yield f"data: {json.dumps({'type': 'error', 'message': 'ASR依赖未安装。请安装ffmpeg和faster-whisper。'}, ensure_ascii=False)}\n\n"
                                return
                        else:
                            yield f"data: {json.dumps({'type': 'error', 'message': 'ASR模块未加载。'}, ensure_ascii=False)}\n\n"
                            return
                    else:
                        # 没有字幕且不支持ASR
                        yield f"data: {json.dumps({'type': 'error', 'message': '该视频没有可用的字幕，且不支持ASR音频转写。建议尝试B站带字幕的视频。'}, ensure_ascii=False)}\n\n"
                        return

                # ========== 步骤3: 检查AI服务 ==========
                if not AI_AVAILABLE:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'AI服务未配置。请在backend/.env中设置DEEPSEEK_API_KEY'}, ensure_ascii=False)}\n\n"
                    return

                # ========== 步骤4: 检查是否有文本 ==========
                if not subtitle_text:
                    yield f"data: {json.dumps({'type': 'error', 'message': '无法获取视频内容。该视频可能没有字幕，ASR转写也失败了。'}, ensure_ascii=False)}\n\n"
                    return

                # ========== 步骤5: 使用AI生成总结（流式） ==========
                yield f"data: {json.dumps({'type': 'progress', 'message': 'AI正在思考并生成总结...'}, ensure_ascii=False)}\n\n"

                # 调用AI生成总结（流式输出纯文本）
                try:
                    stream = summarizer.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {
                                'role': 'system',
                                'content': '你是一个专业的视频内容分析师，擅长总结和提炼视频的核心内容。请严格按照要求的格式输出纯文本总结：【内容大纲】必须使用编号（1. 2. 3.）且不能省略，内容点必须使用圆点符号（•）。'
                            },
                            {
                                'role': 'user',
                                'content': f"""请根据以下视频字幕内容，生成一份结构化的视频总结报告。

## 视频信息
标题: {video_title or '未知'}
描述: {video_description or '无'}

## 字幕内容
{subtitle_text}

## 要求
请严格按照以下格式输出纯文本总结：

【视频概述】
（100-150字概括视频主题和核心价值）

【内容大纲】
1. 章节标题一
   • 内容点1
   • 内容点2

2. 章节标题二
   • 内容点1
   • 内容点2

3. 章节标题三
   • 内容点1
   • 内容点2

（必须严格按此格式：每个章节必须有编号（1. 2. 3.），编号不能省略；内容点使用圆点符号（•）；共3-5个章节，每章2-4个要点）

【核心知识要点】
• 核心要点1
• 核心要点2
• 核心要点3

（提炼3-5个最重要的知识点，每点10-20字）

请直接输出纯文本格式，不要使用JSON代码块。【内容大纲】的编号（1. 2. 3.）必须存在，不能省略！"""
                            }
                        ],
                        temperature=0.7,
                        max_tokens=4000,
                        stream=True
                    )

                    # 流式输出内容
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            yield f"event: summary\ndata: {json.dumps({'token': content}, ensure_ascii=False)}\n\n"

                    # 发送完成事件
                    yield f"event: complete\ndata: {json.dumps({'message': '总结生成完成'}, ensure_ascii=False)}\n\n"
                    print(f"[AI] ✓ 总结生成成功!", file=sys.stderr)

                except Exception as e:
                    print(f"[AI] 总结生成错误: {e}", file=sys.stderr)
                    yield f"data: {json.dumps({'type': 'error', 'message': f'AI总结失败: {str(e)}'}, ensure_ascii=False)}\n\n"

            except Exception as e:
                print(f"[AI] 流式生成错误: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                yield f"data: {json.dumps({'type': 'error', 'message': f'生成失败: {str(e)}'}, ensure_ascii=False)}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        print(f"[AI] 总结错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            'success': False,
            'message': f'总结失败: {str(e)[:200]}'
        }), 500


@ai_bp.route('/chat/stream', methods=['POST'])
def chat_stream():
    """AI问答 - 基于视频内容，支持ASR回退"""
    try:
        print("[AI] chat_stream called", file=sys.stderr)
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        question = data.get('question', '').strip()
        if not question:
            return jsonify({'success': False, 'message': '请输入问题'}), 400

        url = data.get('url', '')
        subtitle_text = data.get('subtitle_text', '')
        chat_history = data.get('chat_history', [])
        video_info = data.get('video_info', {})

        if not AI_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'AI服务未配置。请在backend/.env中设置DEEPSEEK_API_KEY'
            }), 500

        # 如果没有提供字幕文本，尝试提取（包括ASR回退）
        if not subtitle_text and url:
            print("[AI] 未提供字幕文本，尝试提取...", file=sys.stderr)
            subtitle_result = SubtitleExtractor.extract_subtitles(url)

            if subtitle_result.get('success') and subtitle_result.get('has_subtitle'):
                subtitle_text = subtitle_result.get('full_text', '')
                print(f"[AI] ✓ 字幕提取成功! 长度: {len(subtitle_text)}字符", file=sys.stderr)
            elif subtitle_result.get('can_fallback_to_audio'):
                # 尝试ASR转写
                print("[AI] 字幕不可用，尝试ASR转写...", file=sys.stderr)
                AudioTranscriber = get_audio_transcriber()
                if AudioTranscriber and AudioTranscriber.check_ffmpeg() and AudioTranscriber.check_whisper():
                    asr_result = AudioTranscriber.transcribe_from_url(url, model_size='tiny')
                    if asr_result.get('success'):
                        subtitle_text = asr_result.get('full_text', '')
                        print(f"[AI] ✓ ASR转写成功! 长度: {len(subtitle_text)}字符", file=sys.stderr)

        # 构建视频上下文信息
        video_context = f"视频标题: {video_info.get('title', '未知')}\n"
        if subtitle_text:
            video_context += f"视频字幕/转写文本: {subtitle_text}\n"
        else:
            video_context += "注意: 该视频没有可用的字幕文本，回答时请说明这一点。\n"

        # 调用AI问答流式输出
        def generate():
            try:
                # 构建消息历史
                messages = [
                    {"role": "system", "content": f"你是一个专业的视频内容分析助手。\n\n{video_context}\n请根据视频内容回答用户的问题。如果视频没有字幕文本，请诚实地告知用户。"},
                ]

                # 添加历史对话
                for msg in chat_history[-10:]:  # 只保留最近10条历史
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })

                # 添加当前问题
                messages.append({"role": "user", "content": question})

                # 调用Deepseek API
                response = summarizer.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    stream=True,
                    max_tokens=2000
                )

                # 发送开始事件
                yield f"event: start\ndata: {json.dumps({'message': '开始生成回答'}, ensure_ascii=False)}\n\n"

                # 流式输出内容
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield f"event: content\ndata: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

                # 发送完成事件
                yield f"event: complete\ndata: {json.dumps({'message': '回答完成'}, ensure_ascii=False)}\n\n"

            except Exception as e:
                print(f"[AI] 流式生成错误: {e}", file=sys.stderr)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        print(f"[AI] 聊天错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'聊天失败: {str(e)[:200]}'
        }), 500


@ai_bp.route('/subtitle/raw', methods=['POST'])
def get_raw_subtitle():
    """获取原始字幕文本 - 支持ASR回退"""
    try:
        print("[AI] get_raw_subtitle called", file=sys.stderr)
        data = request.get_json()
        url = data.get('url', '').strip()
        use_asr = data.get('use_asr', True)  # 默认启用ASR回退

        if not url:
            return jsonify({'success': False, 'message': '请输入视频链接'}), 400

        # 步骤1: 尝试提取字幕
        print("[AI] 步骤1: 尝试提取字幕...", file=sys.stderr)
        result = SubtitleExtractor.extract_subtitles(url)

        subtitle_text = None
        subtitles = []
        segments = []  # 新格式: [{start, end, text}]
        source = 'subtitle'  # 字幕来源标识

        if result.get('success') and result.get('has_subtitle'):
            subtitle_text = result.get('full_text', '')
            subtitles = result.get('subtitles', [])
            segments = result.get('segments') or subtitles  # 优先使用segments
            print(f"[AI] ✓ 字幕提取成功! 长度: {len(subtitle_text)}字符, 片段: {len(segments)}条", file=sys.stderr)
        elif use_asr and result.get('can_fallback_to_audio'):
            # 步骤2: 字幕提取失败，尝试ASR转写
            print("[AI] 步骤2: 字幕不可用，启动ASR音频转写...", file=sys.stderr)

            AudioTranscriber = get_audio_transcriber()
            if AudioTranscriber:
                if AudioTranscriber.check_ffmpeg() and AudioTranscriber.check_whisper():
                    asr_result = AudioTranscriber.transcribe_from_url(url, model_size='tiny')

                    if asr_result.get('success'):
                        subtitle_text = asr_result.get('full_text', '')
                        subtitles = asr_result.get('subtitles', [])
                        segments = asr_result.get('segments') or subtitles  # 优先使用segments
                        source = 'asr'
                        print(f"[AI] ✓ ASR转写成功! 长度: {len(subtitle_text)}字符, 片段: {len(segments)}条", file=sys.stderr)
                    else:
                        print(f"[AI] ✗ ASR转写失败: {asr_result.get('message', 'Unknown')}", file=sys.stderr)
                        return jsonify({
                            'success': False,
                            'message': f'字幕获取失败: {asr_result.get("message", "未知错误")}'
                        }), 400
                else:
                    return jsonify({
                        'success': False,
                        'message': 'ASR依赖检查失败，请确保ffmpeg和whisper已安装'
                    }), 400
            else:
                return jsonify({
                    'success': False,
                    'message': '音频转写模块未加载'
                }), 400
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '字幕获取失败')
            }), 400

        # 构建兼容多种前端组件的字幕数据
        # 格式1: segments (新格式，用于时间轴) - {start, end, text}
        # 格式2: subtitles (兼容旧格式) - {time, text}
        subtitles_compatible = []
        for seg in segments:
            start = seg.get('start', 0)
            end = seg.get('end', start + 3)
            text = seg.get('text', '')

            # 应用繁简转换
            text = traditional_to_simplified(text)

            # 计算时间字符串
            time_str = _format_seconds_to_time(start)

            subtitles_compatible.append({
                'time': time_str,
                'start_time': time_str,
                'end_time': _format_seconds_to_time(end),
                'text': text,
                'start': start,
                'end': end
            })

        # 返回字幕数据
        return jsonify({
            'success': True,
            'subtitles': subtitles_compatible,
            'segments': segments,  # 新格式: [{start, end, text}]
            'full_text': subtitle_text,
            'language': result.get('language', 'zh'),
            'subtitle_count': len(segments),
            'source': source,  # 'subtitle' 或 'asr'
            'message': f'字幕获取成功 (来源: {"字幕" if source == "subtitle" else "ASR转写"})'
        })

    except Exception as e:
        print(f"[AI] 字幕获取错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'字幕获取失败: {str(e)[:200]}'
        }), 500


@ai_bp.route('/summarize/char-stream', methods=['POST'])
def summarize_video_char_stream():
    """
    AI视频总结 - SSE逐字流式输出（ChatGPT风格打字机效果）

    事件类型：
    - subtitle: 发送字幕文本（一次性）
    - summary: AI总结逐token流式发送（打字机效果）
    - mindmap: 发送思维导图（一次性）
    - quota: 发送用户配额信息
    - done: 标记完成
    - error: 错误信息
    """
    try:
        print("[AI] summarize_video_char_stream called", file=sys.stderr)

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        url = data.get('url', '').strip()
        if not url:
            return jsonify({'success': False, 'message': '请输入视频链接'}), 400

        video_title = data.get('title', '视频内容')
        video_description = data.get('description', '')
        use_asr = data.get('use_asr', False)
        client_subtitle_text = data.get('subtitle_text', '')  # 新增：接收前端传递的字幕

        print(f"[AI] Processing: {video_title[:50]}", file=sys.stderr)
        if client_subtitle_text:
            print(f"[AI] 客户端已提供字幕，长度: {len(client_subtitle_text)}字符，跳过字幕提取", file=sys.stderr)

        # 权限检查：检查解析次数限制（流结束时才扣次）
        try:
            from auth.quota_manager import quota_manager
            from auth.auth import AuthManager
            import uuid

            # 获取用户身份
            auth_header = request.headers.get('Authorization')
            user_id = None

            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                payload = AuthManager.decode_token(token)
                if payload:
                    user_id = payload.get('user_id')

            # 获取fingerprint和request_id
            fingerprint = request.headers.get('X-Fingerprint')
            request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())

            # 检查解析次数
            allowed, message, info = quota_manager.check_quota(user_id, fingerprint, 'parse')

            if not allowed:
                return jsonify({
                    'success': False,
                    'message': message,
                    'code': 'QUOTA_EXCEEDED',
                    'info': info,
                    'require_login': info.get('role') == 'guest',
                    'user_role': info.get('role', 'guest')
                }), 403

        except Exception as e:
            print(f"[AI] 权限检查失败: {e}", file=__import__('sys').stderr)
            # 权限检查失败时，继续执行（降级处理）

        def generate():
            """SSE生成器函数 - 逐字流式输出"""
            try:
                import time
                start_time = time.time()

                # ========== 步骤1: 提取字幕（严格遵守优先级）==========
                subtitle_text = None
                subtitle_segments = []  # 字幕片段 [{start, end, text}]
                source = 'unknown'

                # 优先级0: 如果前端已提供字幕，直接使用（最快！）
                if client_subtitle_text:
                    subtitle_text = client_subtitle_text
                    source = 'client_provided'
                    print(f"[AI] ✓ 使用客户端提供的字幕! 长度: {len(subtitle_text)}字符, 耗时: {time.time()-start_time:.2f}s", file=sys.stderr)

                    # 发送进度事件
                    yield f"data: {json.dumps({'type': 'progress', 'message': '使用已有字幕，开始AI分析...'}, ensure_ascii=False)}\n\n"
                # 优先级1+2: 调用字幕提取器（内部已处理B站API优先和yt-dlp）
                else:
                    print("[AI] 步骤1: 尝试提取字幕...", file=sys.stderr)
                    subtitle_result = SubtitleExtractor.extract_subtitles(url)

                    if subtitle_result.get('success') and subtitle_result.get('has_subtitle'):
                        subtitle_text = subtitle_result.get('full_text', '')
                        subtitle_segments = subtitle_result.get('segments') or subtitle_result.get('subtitles') or []
                        source = 'subtitle'
                        print(f"[AI] ✓ 字幕提取成功! 长度: {len(subtitle_text)}字符, 片段: {len(subtitle_segments)}条, 耗时: {time.time()-start_time:.2f}s", file=sys.stderr)

                    # 优先级3: ASR兜底（如果字幕提取失败）
                    # 只要没有字幕文本，就尝试ASR，不再检查 can_fallback_to_asr 标志
                    if not subtitle_text:
                        print("[AI] 字幕提取失败，尝试ASR语音识别...", file=sys.stderr)

                        AudioTranscriber = get_audio_transcriber()
                        if AudioTranscriber and AudioTranscriber.check_ffmpeg() and AudioTranscriber.check_whisper():
                            print("[AI] 开始ASR转写...", file=sys.stderr)
                            # 发送进度事件
                            yield f"data: {json.dumps({'type': 'progress', 'message': '正在进行语音识别(ASR)，这可能需要1-2分钟...'}, ensure_ascii=False)}\n\n"

                            asr_result = AudioTranscriber.transcribe_from_url(url, model_size='tiny')

                            if asr_result.get('success'):
                                subtitle_text = asr_result.get('full_text', '')
                                subtitle_segments = asr_result.get('segments') or asr_result.get('subtitles') or []
                                source = 'asr'
                                print(f"[AI] ✓ ASR转写成功! 长度: {len(subtitle_text)}字符, 片段: {len(subtitle_segments)}条", file=sys.stderr)
                            else:
                                print(f"[AI] ✗ ASR转写失败: {asr_result.get('message', 'Unknown error')}", file=sys.stderr)
                        else:
                            print("[AI] ✗ ASR不可用（缺少ffmpeg或whisper）", file=sys.stderr)

                # 检查是否有字幕
                if not subtitle_text:
                    yield f"event: error\ndata: {json.dumps({'message': '无法获取视频字幕。建议：1) 尝试B站带字幕的视频 2) 安装ffmpeg和faster-whisper启用语音识别'}, ensure_ascii=False)}\n\n"
                    return

                # ========== 步骤2: 发送字幕事件 ==========
                # 确保 subtitle_segments 包含正确的时间数据
                if not subtitle_segments and subtitle_text:
                    # 如果没有 segments 但有文本，生成简单的 segments
                    lines = subtitle_text.split('\n')

                    # 检查是否需要进一步分割（处理没有换行的长文本）
                    if len(lines) == 1 and len(lines[0]) > 200:
                        print(f"[AI] 检测到单条长文本（{len(lines[0])}字符），按句子分割", file=sys.stderr)
                        # 按句子分割：[。！？!?；;]
                        import re
                        sentences = re.split(r'[。！？!?；;]', lines[0])
                        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
                        print(f"[AI] 分割成 {len(sentences)} 个句子", file=sys.stderr)

                        subtitle_segments = []
                        for idx, sentence in enumerate(sentences):
                            start_time = idx * 5  # 每句假设5秒
                            end_time = start_time + 5
                            subtitle_segments.append({
                                'start': start_time,
                                'end': end_time,
                                'text': sentence.strip()
                            })
                    else:
                        # 正常按行分割
                        subtitle_segments = []
                        for idx, line in enumerate(lines):
                            if line.strip():
                                # 假设每行字幕约3秒
                                start_time = idx * 3
                                end_time = start_time + 3
                                subtitle_segments.append({
                                    'start': start_time,
                                    'end': end_time,
                                    'text': line.strip()
                                })
                elif subtitle_segments and len(subtitle_segments) > 0:
                    # 检查 segments 格式并转换
                    first_seg = subtitle_segments[0]

                    # 优先检查ASR格式: {time, start_time, end_time, text}
                    if 'start_time' in first_seg and 'start' not in first_seg:
                        print(f"[AI] 检测到ASR格式字幕，转换时间戳格式", file=sys.stderr)
                        converted_segments = []
                        for seg in subtitle_segments:
                            start_time = seg.get('start_time', '0:00:00')
                            end_time = seg.get('end_time', '0:00:00')
                            # 转换时间格式为秒数
                            start_seconds = _parse_time_to_seconds(start_time)
                            end_seconds = _parse_time_to_seconds(end_time)
                            converted_segments.append({
                                'start': start_seconds,
                                'end': end_seconds,
                                'text': seg.get('text', '')
                            })
                        subtitle_segments = converted_segments
                        print(f"[AI] ✓ 字幕格式转换完成，共{len(subtitle_segments)}条", file=sys.stderr)

                    # 检查旧格式: {time, text} (没有start_time/end_time)
                    elif 'time' in first_seg and 'start' not in first_seg:
                        print(f"[AI] 检测到旧格式字幕，重新生成时间戳", file=sys.stderr)
                        subtitle_segments = []
                        lines = subtitle_text.split('\n')
                        for idx, line in enumerate(lines):
                            if line.strip():
                                start_time = idx * 3
                                end_time = start_time + 3
                                subtitle_segments.append({
                                    'start': start_time,
                                    'end': end_time,
                                    'text': line.strip()
                                })

                # 构建兼容多种前端组件的字幕数据
                # 格式1: segments (新格式，用于时间轴) - {start, end, text}
                # 格式2: subtitles (兼容旧格式) - {time, text}
                subtitles_compatible = []
                for seg in subtitle_segments:
                    start = seg.get('start', 0)
                    end = seg.get('end', start + 3)
                    text = seg.get('text', '')

                    # 应用繁简转换
                    text = traditional_to_simplified(text)

                    # 计算时间字符串
                    time_str = _format_seconds_to_time(start)

                    subtitles_compatible.append({
                        'time': time_str,
                        'start_time': time_str,
                        'end_time': _format_seconds_to_time(end),
                        'text': text,
                        'start': start,
                        'end': end
                    })

                # 对full_text也应用繁简转换
                subtitle_text = traditional_to_simplified(subtitle_text)

                yield f"event: subtitle\ndata: {json.dumps({'segments': subtitle_segments, 'subtitles': subtitles_compatible, 'text': subtitle_text, 'length': len(subtitle_text)}, ensure_ascii=False)}\n\n"

                # ========== 步骤3: 检查AI服务 ==========
                if not AI_AVAILABLE:
                    yield f"event: error\ndata: {json.dumps({'message': 'AI服务未配置，请设置DEEPSEEK_API_KEY'}, ensure_ascii=False)}\n\n"
                    return

                # ========== 步骤4: Deepseek流式调用 - 逐token发送 ==========
                print(f"[AI] 开始Deepseek流式调用，字幕长度: {len(subtitle_text)}", file=sys.stderr)

                # 构建提示词 - 改为纯文本格式输出
                prompt = f"""请根据以下视频字幕内容，生成一份结构化的视频总结报告。

## 视频信息
标题: {video_title}
描述: {video_description or '无'}

## 字幕内容
{subtitle_text[:8000]}

## 要求
请严格按照以下格式输出纯文本总结：

【视频概述】
（100-150字概括视频主题和核心价值）

【内容大纲】
1. 章节标题一
   • 内容点1
   • 内容点2

2. 章节标题二
   • 内容点1
   • 内容点2

3. 章节标题三
   • 内容点1
   • 内容点2

（必须严格按此格式：每个章节必须有编号（1. 2. 3.），编号不能省略；内容点使用圆点符号（•）；共3-5个章节，每章2-4个要点）

【核心知识要点】
• 核心要点1
• 核心要点2
• 核心要点3

（提炼3-5个最重要的知识点，每点10-20字）

请直接输出纯文本格式，不要使用JSON代码块。【内容大纲】的编号（1. 2. 3.）必须存在，不能省略！"""

                # 调用Deepseek API（流式）
                stream = summarizer.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {
                            'role': 'system',
                            'content': '你是一个专业的视频内容分析师，擅长总结和提炼视频的核心内容。请严格按照要求的格式输出纯文本总结：【内容大纲】必须使用编号（1. 2. 3.）且不能省略，内容点必须使用圆点符号（•）。'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=4000,
                    stream=True
                )

                # 逐token发送 - 按字符拆分实现平滑打字机效果
                full_content = ""
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        full_content += token

                        # 将token按字符拆分（中文按字，英文按字符）
                        for char in token:
                            # 逐字符发送summary事件
                            yield f"event: summary\ndata: {json.dumps({'token': char}, ensure_ascii=False)}\n\n"

                print(f"[AI] 流式完成，总长度: {len(full_content)}", file=sys.stderr)

                # ========== 步骤5: 发送思维导图（基于实际总结内容） ==========
                # 解析总结内容生成思维导图
                mindmap_lines = []
                mindmap_lines.append(f"# {video_title}\n")

                # 解析总结内容
                lines = full_content.split('\n')
                current_section = None
                current_items = []

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # 检测章节标题
                    if line.startswith('【') and line.endswith('】'):
                        # 保存上一个章节
                        if current_section and current_items:
                            mindmap_lines.append(f"## {current_section}")
                            for item in current_items:
                                mindmap_lines.append(f"- {item}")
                            mindmap_lines.append("")

                        current_section = line[1:-1]  # 去掉【】
                        current_items = []
                    # 检测列表项
                    elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or line.startswith(('-', '•')):
                        item = line.lstrip('0123456789.-•• \t')
                        if item:
                            current_items.append(item)
                    # 普通内容
                    elif current_section:
                        current_items.append(line)

                # 保存最后一个章节
                if current_section and current_items:
                    mindmap_lines.append(f"## {current_section}")
                    for item in current_items:
                        mindmap_lines.append(f"- {item}")

                # 添加生成时间
                mindmap_lines.append(f"\n---\n*生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

                mindmap_text = '\n'.join(mindmap_lines)
                yield f"event: mindmap\ndata: {json.dumps({'text': mindmap_text}, ensure_ascii=False)}\n\n"

                # ========== 步骤6: 发送配额信息 ==========
                # 获取剩余次数
                try:
                    from auth.quota_manager import quota_manager
                    remaining_info = quota_manager.get_remaining(user_id, fingerprint)
                    yield f"event: quota\ndata: {json.dumps(remaining_info, ensure_ascii=False)}\n\n"
                except Exception as e:
                    print(f"[AI] 获取剩余次数失败: {e}", file=__import__('sys').stderr)
                    yield f"event: quota\ndata: {json.dumps({'parse_remaining': '未知', 'download_remaining': '未知'}, ensure_ascii=False)}\n\n"

                # ========== 步骤7: 扣减解析次数（只有成功完成才扣） ==========
                try:
                    from auth.quota_manager import quota_manager
                    # 扣减解析次数（使用request_id保证幂等）
                    quota_manager.consume_quota(user_id, fingerprint, 'parse', request_id)
                    user_desc = f"user {user_id}" if user_id else f"guest {fingerprint[:8]}..."
                    print(f"[AI] ✓ 扣减解析次数成功: {user_desc}", file=__import__('sys').stderr)
                except Exception as e:
                    print(f"[AI] 扣减解析次数失败: {e}", file=__import__('sys').stderr)

                # ========== 步骤8: 发送完成事件 ==========
                yield f"event: done\ndata: {json.dumps({'success': True}, ensure_ascii=False)}\n\n"

            except Exception as e:
                print(f"[AI] 流式生成错误: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                yield f"event: error\ndata: {json.dumps({'message': f'生成失败: {str(e)}'}, ensure_ascii=False)}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        print(f"[AI] 总结错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'总结失败: {str(e)[:200]}'
        }), 500
