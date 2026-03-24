"""
音频转写模块 - 当视频没有字幕时，使用ASR转写音频生成文本
支持：faster-whisper（轻量级，无需PyTorch）
"""
import os
import sys
import tempfile
import subprocess
import json
from typing import Dict, Optional
from pathlib import Path


class AudioTranscriber:
    """音频转写器 - 使用faster-whisper ASR（轻量级方案）"""

    @staticmethod
    def check_ffmpeg() -> bool:
        """检查ffmpeg是否可用"""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def check_whisper() -> bool:
        """检查whisper是否已安装（优先检查faster-whisper）"""
        try:
            # 优先检查 faster-whisper
            from faster_whisper import WhisperModel
            return True
        except ImportError:
            try:
                import whisper
                return True
            except ImportError:
                return False

    @staticmethod
    def get_available_asr() -> str:
        """获取可用的ASR类型"""
        try:
            from faster_whisper import WhisperModel
            return 'faster-whisper'
        except ImportError:
            pass

        try:
            import whisper
            return 'openai-whisper'
        except ImportError:
            pass

        return None

    @classmethod
    def transcribe_from_url(cls, video_url: str, model_size: str = 'base') -> Dict:
        """
        从视频URL转写音频

        Args:
            video_url: 视频URL
            model_size: 模型大小 (tiny, base, small, medium, large)

        Returns:
            {
                'success': bool,
                'text': str,
                'segments': list,
                'language': str,
                'duration': float,
                'message': str
            }
        """
        try:
            # 检查依赖
            if not cls.check_ffmpeg():
                return {
                    'success': False,
                    'message': 'ffmpeg未安装，无法提取音频。请安装ffmpeg后重试。'
                }

            # 检查whisper（支持faster-whisper或openai-whisper）
            if not cls.check_whisper():
                # 尝试自动安装faster-whisper
                print("[AUDIO-ASR] Whisper未安装，尝试安装faster-whisper...", file=sys.stderr)
                cls._install_faster_whisper()

            if not cls.check_whisper():
                return {
                    'success': False,
                    'message': 'Whisper未安装。请运行: pip install faster-whisper'
                }

            print("[AUDIO-ASR] 开始下载音频...", file=sys.stderr)

            # 下载音频
            audio_file, duration = cls._download_audio(video_url)
            if not audio_file:
                return {
                    'success': False,
                    'message': '音频下载失败'
                }

            print(f"[AUDIO-ASR] 音频下载成功，时长: {duration:.1f}秒", file=sys.stderr)
            print(f"[AUDIO-ASR] 开始转写 (模型: {model_size})...", file=sys.stderr)

            # 使用Whisper转写
            result = cls._transcribe_with_whisper(audio_file, model_size)

            # 清理临时文件
            try:
                os.unlink(audio_file)
            except:
                pass

            return result

        except Exception as e:
            error_msg = str(e)
            print(f"[AUDIO-ASR] 错误: {error_msg}", file=sys.stderr)

            return {
                'success': False,
                'message': f'音频转写失败: {error_msg[:200]}'
            }

    @staticmethod
    def _install_faster_whisper():
        """自动安装faster-whisper"""
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'faster-whisper', '-q'],
                check=True,
                capture_output=True,
                timeout=300
            )
            print("[AUDIO-ASR] faster-whisper安装成功", file=sys.stderr)
        except Exception as e:
            print(f"[AUDIO-ASR] faster-whisper安装失败: {str(e)[:100]}", file=sys.stderr)

    @classmethod
    def _download_audio(cls, video_url: str) -> tuple[Optional[str], float]:
        """
        使用yt-dlp下载音频（带B站优化）

        Returns:
            (audio_file_path, duration_seconds) or (None, 0) on failure
        """
        import yt_dlp

        temp_dir = tempfile.gettempdir()
        output_template = os.path.join(temp_dir, 'audio_%(id)s.%(ext)s')

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'prefer_ffmpeg': True,
            # 网络配置
            'socket_timeout': 60,
            'retries': 5,
            # 关键：使用真实的请求头（特别是B站）
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Referer': 'https://www.bilibili.com/',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            },
            'nocheckcertificate': True,
        }

        try:
            print(f"[AUDIO-ASR] 准备下载音频: {video_url[:50]}...", file=sys.stderr)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)

                # 获取下载的文件路径
                video_id = info.get('id', 'audio')
                expected_path = os.path.join(temp_dir, f'audio_{video_id}.mp3')

                if os.path.exists(expected_path):
                    duration = info.get('duration', 0)
                    print(f"[AUDIO-ASR] 音频下载成功: {expected_path}", file=sys.stderr)
                    return expected_path, duration

                # 尝试查找匹配的文件
                for f in os.listdir(temp_dir):
                    if f.startswith(f'audio_{video_id}'):
                        full_path = os.path.join(temp_dir, f)
                        print(f"[AUDIO-ASR] 音频下载成功: {full_path}", file=sys.stderr)
                        return full_path, info.get('duration', 0)

                print(f"[AUDIO-ASR] 音频文件未找到", file=sys.stderr)
                return None, 0

        except Exception as e:
            print(f"[AUDIO-ASR] 音频下载失败: {str(e)[:150]}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return None, 0

    @classmethod
    def _transcribe_with_whisper(cls, audio_file: str, model_size: str) -> Dict:
        """
        使用Whisper转写音频 - 支持faster-whisper和openai-whisper

        Args:
            audio_file: 音频文件路径
            model_size: 模型大小

        Returns:
            转写结果
        """
        # 设置Hugging Face镜像环境变量（用于模型下载）
        os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')

        # 优先使用faster-whisper（更快、更轻量）
        try:
            from faster_whisper import WhisperModel

            print(f"[AUDIO-ASR] 使用faster-whisper (模型: {model_size})", file=sys.stderr)

            # 使用CPU模式（兼容性更好）
            model = WhisperModel(model_size, device="cpu", compute_type="int8")

            segments, info = model.transcribe(
                audio_file,
                language='zh',  # 强制中文
                beam_size=5,
                vad_filter=True,  # 启用VAD过滤
                word_timestamps=False  # 禁用词级时间戳以提升速度
            )

            # 转换为统一格式
            formatted_subtitles = []
            full_text_parts = []

            for segment in segments:
                start_time = segment.start
                end_time = segment.end
                text = segment.text.strip()

                if text:
                    start_str = cls._format_seconds(start_time)
                    end_str = cls._format_seconds(end_time)

                    formatted_subtitles.append({
                        'time': f"{start_str} --> {end_str}",
                        'start_time': start_str,
                        'end_time': end_str,
                        'text': text
                    })
                    full_text_parts.append(text)

            full_text = ' '.join(full_text_parts)

            print(f"[AUDIO-ASR] ✓ 转写完成! 文本长度: {len(full_text)}字符", file=sys.stderr)

            return {
                'success': True,
                'has_subtitle': True,
                'subtitles': formatted_subtitles,
                'full_text': full_text,
                'language': info.language,
                'subtitle_count': len(formatted_subtitles),
                'duration': info.duration,
                'message': f'音频转写成功 (faster-whisper: {model_size})',
                'is_from_asr': True
            }

        except ImportError:
            # 降级到openai-whisper
            pass
        except Exception as e:
            print(f"[AUDIO-ASR] faster-whisper失败: {str(e)[:100]}", file=sys.stderr)

        # 使用openai-whisper作为备选
        try:
            import whisper

            print(f"[AUDIO-ASR] 使用openai-whisper (模型: {model_size})", file=sys.stderr)

            model = whisper.load_model(model_size)
            result = model.transcribe(
                audio_file,
                language='zh',
                task='transcribe',
                verbose=False
            )

            # 解析结果
            segments = result.get('segments', [])
            text = result.get('text', '')
            language = result.get('language', 'zh')
            duration = result.get('duration', 0) or 0

            # 格式化为字幕格式
            formatted_subtitles = []
            for seg in segments:
                start_time = seg.get('start', 0)
                end_time = seg.get('end', 0)
                seg_text = seg.get('text', '').strip()

                if seg_text:
                    start_str = cls._format_seconds(start_time)
                    end_str = cls._format_seconds(end_time)

                    formatted_subtitles.append({
                        'time': f"{start_str} --> {end_str}",
                        'start_time': start_str,
                        'end_time': end_str,
                        'text': seg_text
                    })

            full_text = '\n'.join([s['text'] for s in formatted_subtitles])

            print(f"[AUDIO-ASR] ✓ 转写完成! 文本长度: {len(text)}字符", file=sys.stderr)

            return {
                'success': True,
                'has_subtitle': True,
                'subtitles': formatted_subtitles,
                'full_text': full_text,
                'language': language,
                'subtitle_count': len(formatted_subtitles),
                'duration': duration,
                'message': f'音频转写成功 (openai-whisper: {model_size})',
                'is_from_asr': True
            }

        except ImportError:
            return {
                'success': False,
                'message': 'Whisper未安装。请运行: pip install faster-whisper'
            }
        except Exception as e:
            print(f"[AUDIO-ASR] whisper转写失败: {str(e)[:100]}", file=sys.stderr)
            return {
                'success': False,
                'message': f'转写失败: {str(e)[:200]}'
            }

    @staticmethod
    def _format_seconds(seconds: float) -> str:
        """将秒转换为时间戳格式 (HH:MM:SS)"""
        from datetime import timedelta
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds, 3600)
        minutes, secs = divmod(remainder, 60)

        if td.days > 0 or hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


# 便捷函数
def transcribe_audio(video_url: str, model_size: str = 'base') -> Dict:
    """转写视频音频的便捷函数"""
    return AudioTranscriber.transcribe_from_url(video_url, model_size)
