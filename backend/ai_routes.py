"""
AI功能路由模块 - 生产版本
使用真实的字幕提取和AI总结，禁止测试模式
支持4个Tab功能：视频总结、字幕文本、思维导图、AI问答
"""
import sys
import json
import os
from flask import Blueprint, request, jsonify, Response, stream_with_context

# 导入字幕提取器
from subtitle_extractor import SubtitleExtractor

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

                # 调用AI生成总结（非流式，因为需要完整的JSON结构）
                result = summarizer.summarize_video(
                    subtitle_text=subtitle_text,
                    video_title=video_title,
                    video_description=video_description
                )

                if result.get('success'):
                    # 发送最终结果
                    yield f"data: {json.dumps({'type': 'result', 'data': result}, ensure_ascii=False)}\n\n"
                    print(f"[AI] ✓ 总结生成成功!", file=sys.stderr)
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': result.get('message', 'AI总结失败')}, ensure_ascii=False)}\n\n"

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
                yield f"data: {json.dumps({'type': 'start', 'message': '开始生成回答'}, ensure_ascii=False)}\n\n"

                # 流式输出内容
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield f"data: {json.dumps({'type': 'content', 'content': content}, ensure_ascii=False)}\n\n"

                # 发送完成事件
                yield f"data: {json.dumps({'type': 'complete', 'message': '回答完成'}, ensure_ascii=False)}\n\n"

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
        source = 'subtitle'  # 字幕来源标识

        if result.get('success') and result.get('has_subtitle'):
            subtitle_text = result.get('full_text', '')
            subtitles = result.get('subtitles', [])
            print(f"[AI] ✓ 字幕提取成功! 长度: {len(subtitle_text)}字符", file=sys.stderr)
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
                        source = 'asr'
                        print(f"[AI] ✓ ASR转写成功! 长度: {len(subtitle_text)}字符", file=sys.stderr)
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

        # 返回字幕数据
        return jsonify({
            'success': True,
            'subtitles': subtitles,
            'full_text': subtitle_text,
            'language': result.get('language', 'zh'),
            'subtitle_count': len(subtitles),
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
