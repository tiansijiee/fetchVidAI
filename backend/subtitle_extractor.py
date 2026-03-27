"""
字幕提取器 - 使用yt-dlp提取视频字幕
支持平台：B站、YouTube等支持字幕的平台
"""
import yt_dlp
import json
import re
import sys
from typing import Dict, List, Optional, Tuple
from datetime import timedelta

# 繁体字转简体字 - 使用 opencc-python-reimplemented（推荐方案）
# 这是一个纯Python实现的轻量级库，无需C依赖，转换准确率高
_converter = None

def get_converter():
    """获取繁简转换器实例（延迟加载）"""
    global _converter
    if _converter is None:
        try:
            from opencc import OpenCC
            _converter = OpenCC('t2s')  # 繁体转简体
            print("[SUBTITLE] 繁简转换器已启用 (OpenCC)", file=sys.stderr)
        except ImportError:
            print("[SUBTITLE] 警告: opencc未安装，繁简转换功能不可用。请运行: pip install opencc-python-reimplemented", file=sys.stderr)
            _converter = False
    return _converter

def traditional_to_simplified(text: str) -> str:
    """
    繁体字转简体字（使用OpenCC）

    Args:
        text: 繁体文本

    Returns:
        简体文本
    """
    if not text:
        return text

    converter = get_converter()
    if converter:
        try:
            return converter.convert(text)
        except Exception as e:
            print(f"[SUBTITLE] 繁简转换出错: {e}", file=sys.stderr)
            return text
    return text


class SubtitleExtractor:
    """字幕提取器"""

    # 支持字幕的平台
    SUBTITLE_PLATFORMS = {
        'bilibili': ['bilibili.com', 'b23.tv'],
        'youtube': ['youtube.com', 'youtu.be'],
    }

    @classmethod
    def identify_platform(cls, url: str) -> Optional[str]:
        """识别视频平台"""
        for platform, domains in cls.SUBTITLE_PLATFORMS.items():
            if any(domain in url for domain in domains):
                return platform
        return None

    @classmethod
    def is_subtitle_supported(cls, url: str) -> bool:
        """检查是否支持字幕提取"""
        platform = cls.identify_platform(url)
        return platform is not None

    @classmethod
    def extract_subtitles(cls, url: str, lang: str = 'zh-Hans') -> Dict:
        """
        提取视频字幕 - 严格遵守优先级

        优先级（必须遵守）：
        1. B站专用API路径（api.bilibili.com → dm/view）
        2. 其他平台统一走yt-dlp提取字幕
        3. 若以上两种方式都提取失败，最后兜底走ASR视频语音识别

        Args:
            url: 视频链接
            lang: 字幕语言 (zh-Hans: 简体中文, en: 英语, etc.)

        Returns:
            {
                'success': bool,
                'has_subtitle': bool,
                'segments': List[{'start': float, 'end': float, 'text': str}],  # 统一格式
                'full_text': str,
                'language': str,
                'message': str,
                'can_fallback_to_asr': bool  # 是否可以降级到ASR
            }
        """
        try:
            # 检查平台支持
            platform = cls.identify_platform(url)
            print(f"[SUBTITLE] ========== 开始字幕提取 ==========", file=sys.stderr)
            print(f"[SUBTITLE] 平台: {platform}, URL: {url[:50]}", file=sys.stderr)
            print(f"[SUBTITLE] 目标语言: {lang}", file=sys.stderr)

            # ========== 优先级1: B站专用API路径 ==========
            if platform == 'bilibili':
                print("[SUBTITLE] B站视频，优先使用API获取字幕", file=sys.stderr)

                # 先获取视频信息（用于提取bvid和cid）
                info = cls._get_video_info(url)
                bvid = info.get('id') or info.get('bvid')

                print(f"[SUBTITLE] 获取到bvid: {bvid}", file=sys.stderr)

                if bvid:
                    # 直接调用B站API
                    result = cls._fetch_bilibili_subtitles_api(bvid, info)

                    print(f"[SUBTITLE] B站API结果: success={result.get('success')}, has_subtitle={result.get('has_subtitle')}", file=sys.stderr)

                    if result.get('success') and result.get('has_subtitle'):
                        print(f"[SUBTITLE] ✓ B站API获取字幕成功! 字幕长度: {len(result.get('full_text', ''))}", file=sys.stderr)
                        return result

                    print(f"[SUBTITLE] B站API返回: {result.get('message', 'Unknown')}", file=sys.stderr)
                    print("[SUBTITLE] B站API获取失败，尝试yt-dlp", file=sys.stderr)

            # ========== 优先级2: yt-dlp通用路径 ==========
            print("[SUBTITLE] 使用yt-dlp提取字幕", file=sys.stderr)
            result = cls._extract_with_ydl(url, lang, platform)

            print(f"[SUBTITLE] yt-dlp结果: success={result.get('success')}, has_subtitle={result.get('has_subtitle')}", file=sys.stderr)

            if result.get('success') and result.get('has_subtitle'):
                print(f"[SUBTITLE] ✓ yt-dlp字幕提取成功! 字幕长度: {len(result.get('full_text', ''))}", file=sys.stderr)
                return result

            # ========== 优先级3: ASR兜底（返回标识，由调用方处理）==========
            print(f"[SUBTITLE] 所有字幕提取方式失败", file=sys.stderr)
            print(f"[SUBTITLE] 返回can_fallback_to_asr=True，由AI路由处理ASR", file=sys.stderr)
            return {
                'success': False,
                'has_subtitle': False,
                'can_fallback_to_asr': True,  # 标识可以降级到ASR
                'message': '字幕提取失败，可使用ASR语音识别生成字幕'
            }

        except Exception as e:
            error_msg = str(e)
            print(f"[SUBTITLE] Error details: {error_msg}", file=sys.stderr)
            print(f"[SUBTITLE] Error type: {type(e).__name__}", file=sys.stderr)

            return {
                'success': False,
                'has_subtitle': False,
                'can_fallback_to_asr': True,  # 标识可以降级到ASR
                'message': f'字幕提取失败: {error_msg[:200]}'
            }

    @classmethod
    def _get_video_info(cls, url: str) -> Dict:
        """
        获取视频基本信息（用于提取bvid、cid等）

        Args:
            url: 视频链接

        Returns:
            视频信息字典，包含 id, bvid, cid 等字段
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
            'nocheckcertificate': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"[SUBTITLE] 获取视频信息失败: {str(e)[:100]}", file=sys.stderr)
            return {}

    @classmethod
    def _extract_with_ydl(cls, url: str, lang: str, platform: str) -> Dict:
        """
        使用yt-dlp提取字幕（通用路径）- 增强版

        处理流程：
        1. 调用yt-dlp的extract_info方法，设置writesubtitles=True
        2. 处理返回的VTT/WebVTT格式字幕
        3. 解析为统一的segments格式（start/end/text）

        Args:
            url: 视频链接
            lang: 字幕语言
            platform: 平台标识

        Returns:
            字幕提取结果
        """
        # 扩展语言选项，增加更多可能的字幕语言代码
        expanded_langs = [
            lang, 'zh-Hans', 'zh', 'zh-Hant', 'zh-CN', 'zh-TW', 'zh-HK',
            'zh-SG', 'zh-MY', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru'
        ]

        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': expanded_langs,
            'subtitlesformat': 'json',  # 优先使用JSON格式
            'extract_flat': False,
            'nocheckcertificate': True,
            'verbose': False,
            # B站专用配置 - 增强获取能力
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web', 'ios'],
                }
            } if platform == 'bilibili' else {},
        }

        print(f"[SUBTITLE-YDLP] 扩展语言列表: {expanded_langs}", file=sys.stderr)

        try:
            print(f"[SUBTITLE-YDLP] 开始提取字幕...", file=sys.stderr)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # 打印更详细的调试信息
                print(f"[SUBTITLE-YDLP] 视频标题: {info.get('title', 'N/A')[:50]}", file=sys.stderr)
                print(f"[SUBTITLE-YDLP] 字幕keys: {list(info.get('subtitles', {}).keys())}", file=sys.stderr)
                print(f"[SUBTITLE-YDLP] 自动字幕keys: {list(info.get('automatic_captions', {}).keys())}", file=sys.stderr)
                print(f"[SUBTITLE-YDLP] 所有可用字幕轨道数: {len(info.get('subtitles', {})) + len(info.get('automatic_captions', {}))}", file=sys.stderr)

                return cls._process_subtitle_info(info, lang, url)

        except Exception as e:
            error_msg = str(e)
            print(f"[SUBTITLE-YDLP] Error: {error_msg[:200]}", file=sys.stderr)

            return {
                'success': False,
                'has_subtitle': False,
                'can_fallback_to_asr': True,
                'message': f'字幕提取失败: {error_msg[:200]}'
            }

    @classmethod
    def _extract_bilibili_subtitles(cls, url: str, lang: str) -> Dict:
        """
        B站专用字幕提取 - 无需Cookie的优化方案

        策略：
        1. 尝试获取CC字幕（公开字幕）
        2. 尝试获取AI自动生成字幕
        3. 使用优化的请求头模拟正常访问
        """
        import requests

        # B站专用配置 - 更宽松的超时和重试
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang, 'zh-Hans', 'zh', 'zh-Hant', 'en'],
            'subtitlesformat': 'json',
            'extract_flat': False,
            'nocheckcertificate': True,
            'verbose': True,  # 开启详细日志以便调试
            # 网络配置
            'socket_timeout': 30,
            'retries': 3,
            # 关键：使用真实的请求头
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Referer': 'https://www.bilibili.com/',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
            }
        }

        try:
            print("[SUBTITLE-BILI] 开始提取B站字幕...", file=sys.stderr)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                print(f"[SUBTITLE-BILI] 视频标题: {info.get('title', 'N/A')[:50]}", file=sys.stderr)

                # 检查字幕
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})

                print(f"[SUBTITLE-BILI] 手动字幕: {list(subtitles.keys())}", file=sys.stderr)
                print(f"[SUBTITLE-BILI] 自动字幕: {list(automatic_captions.keys())}", file=sys.stderr)

                # 尝试处理字幕
                result = cls._process_subtitle_info(info, lang, url)

                # 如果成功找到字幕，直接返回
                if result.get('success') and result.get('has_subtitle'):
                    print("[SUBTITLE-BILI] ✓ 字幕提取成功！", file=sys.stderr)
                    return result

                # ========== 降级方案：尝试直接从B站API获取字幕 ==========
                print("[SUBTITLE-BILI] 尝试B站API降级方案...", file=sys.stderr)

                # 提取视频ID
                bvid = info.get('id') or info.get('bvid')
                if bvid:
                    api_result = cls._fetch_bilibili_subtitles_api(bvid, info)
                    if api_result.get('success'):
                        print("[SUBTITLE-BILI] ✓ API降级方案成功！", file=sys.stderr)
                        return api_result

                # 如果所有方法都失败，返回可以降级到音频转写的标识
                print("[SUBTITLE-BILI] ✗ 所有字幕提取方法失败", file=sys.stderr)
                return {
                    'success': False,
                    'has_subtitle': False,
                    'can_fallback_to_audio': True,
                    'message': '该视频暂无可用字幕。将自动使用音频转写生成字幕。'
                }

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            print(f"[SUBTITLE-BILI] DownloadError: {error_msg[:200]}", file=sys.stderr)

            # 特殊错误处理
            if 'sign in' in error_msg.lower() or 'login' in error_msg.lower():
                return {
                    'success': False,
                    'has_subtitle': False,
                    'can_fallback_to_audio': True,
                    'message': '该视频需要登录才能访问字幕。将自动使用音频转写生成字幕。'
                }
            elif '404' in error_msg or 'not found' in error_msg.lower():
                return {
                    'success': False,
                    'has_subtitle': False,
                    'can_fallback_to_audio': True,
                    'message': '视频不存在或已被删除。'
                }
            else:
                return {
                    'success': False,
                    'has_subtitle': False,
                    'can_fallback_to_audio': True,
                    'message': f'网络错误，将自动使用音频转写: {error_msg[:100]}'
                }
        except Exception as e:
            print(f"[SUBTITLE-BILI] Exception: {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
            return {
                'success': False,
                'has_subtitle': False,
                'can_fallback_to_audio': True,
                'message': f'字幕提取异常: {str(e)[:100]}'
            }

    @classmethod
    def _fetch_bilibili_subtitles_api(cls, bvid: str, info: dict) -> Dict:
        """
        直接从B站API获取字幕 - 修复版本

        正确的B站字幕API调用方式：
        1. 优先从yt-dlp的info中获取subtitle_url（最可靠）
        2. 备选：调用 /x/web-interface/view 获取字幕信息
        3. 下载JSON字幕并解析为统一格式

        注意：/x/v2/dm/view 是弹幕API，不是字幕API！
        字幕数据在 info['subtitles'] 或 subtitle_url 中

        Args:
            bvid: B站视频ID
            info: yt-dlp获取的视频信息

        Returns:
            字幕提取结果，格式: { success, has_subtitle, segments: [{start, end, text}], full_text, ... }
        """
        import requests

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': f'https://www.bilibili.com/video/{bvid}',
                'Accept': 'application/json',
            }

            # ========== 方法1: 优先从yt-dlp info中获取字幕URL（最可靠）==========
            print("[SUBTITLE-BILI-API] 方法1: 尝试从yt-dlp info获取字幕...", file=sys.stderr)

            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})

            print(f"[SUBTITLE-BILI-API] 手动字幕: {list(subtitles.keys())}", file=sys.stderr)
            print(f"[SUBTITLE-BILI-API] 自动字幕: {list(automatic_captions.keys())}", file=sys.stderr)

            # 合并所有可用字幕
            all_subtitles = {**subtitles, **automatic_captions}
            print(f"[SUBTITLE-BILI-API] 所有可用字幕: {list(all_subtitles.keys())}", file=sys.stderr)

            # 优先中文字幕
            for lang_key in ['zh-Hans', 'zh', 'zh-Hant', 'en']:
                if lang_key in all_subtitles:
                    subtitle_data = all_subtitles[lang_key]
                    if isinstance(subtitle_data, list) and len(subtitle_data) > 0:
                        subtitle_url = subtitle_data[0].get('url') if isinstance(subtitle_data[0], dict) else None

                        if subtitle_url:
                            print(f"[SUBTITLE-BILI-API] 找到字幕URL: {subtitle_url}", file=sys.stderr)

                            # 下载字幕内容
                            full_url = f"https:{subtitle_url}" if not subtitle_url.startswith('http') else subtitle_url

                            try:
                                sub_response = requests.get(full_url, headers=headers, timeout=15)
                                sub_response.raise_for_status()
                                subtitle_content = sub_response.json()

                                # 解析为统一格式
                                segments = cls._parse_bilibili_subtitle_to_segments(subtitle_content)

                                if segments:
                                    full_text = '\n'.join([s['text'] for s in segments])
                                    print(f"[SUBTITLE-BILI-API] ✓ 方法1成功! 提取{len(segments)}条字幕", file=sys.stderr)

                                    return {
                                        'success': True,
                                        'has_subtitle': True,
                                        'segments': segments,
                                        'subtitles': segments,
                                        'full_text': full_text,
                                        'language': 'zh-Hans',
                                        'subtitle_count': len(segments),
                                        'message': '字幕提取成功（yt-dlp）'
                                    }
                            except Exception as e:
                                print(f"[SUBTITLE-BILI-API] 下载字幕失败: {str(e)[:100]}", file=sys.stderr)

            # 如果没有找到字幕，尝试其他语言
            if all_subtitles:
                first_key = list(all_subtitles.keys())[0]
                subtitle_data = all_subtitles[first_key]
                if isinstance(subtitle_data, list) and len(subtitle_data) > 0:
                    subtitle_url = subtitle_data[0].get('url') if isinstance(subtitle_data[0], dict) else None

                    if subtitle_url:
                        print(f"[SUBTITLE-BILI-API] 尝试其他语言字幕: {first_key}", file=sys.stderr)

                        full_url = f"https:{subtitle_url}" if not subtitle_url.startswith('http') else subtitle_url

                        try:
                            sub_response = requests.get(full_url, headers=headers, timeout=15)
                            sub_response.raise_for_status()
                            subtitle_content = sub_response.json()

                            segments = cls._parse_bilibili_subtitle_to_segments(subtitle_content)

                            if segments:
                                full_text = '\n'.join([s['text'] for s in segments])
                                print(f"[SUBTITLE-BILI-API] ✓ 方法1成功(备选语言)! 提取{len(segments)}条字幕", file=sys.stderr)

                                return {
                                    'success': True,
                                    'has_subtitle': True,
                                    'segments': segments,
                                    'subtitles': segments,
                                    'full_text': full_text,
                                    'language': first_key,
                                    'subtitle_count': len(segments),
                                    'message': f'字幕提取成功（语言: {first_key}）'
                                }
                        except Exception as e:
                            print(f"[SUBTITLE-BILI-API] 备选语言下载失败: {str(e)[:100]}", file=sys.stderr)

            # ========== 方法2: 从B站 Web API 获取字幕信息（备选方案）==========
            print("[SUBTITLE-BILI-API] 方法1失败，尝试方法2: 从B站 Web API获取...", file=sys.stderr)

            view_api_url = "https://api.bilibili.com/x/web-interface/view"
            view_params = {'bvid': bvid}

            print(f"[SUBTITLE-BILI-API] 调用 {view_api_url}?bvid={bvid}", file=sys.stderr)

            view_response = requests.get(view_api_url, params=view_params, headers=headers, timeout=15)
            view_response.raise_for_status()
            view_data = view_response.json()

            if view_data.get('code') != 0:
                print(f"[SUBTITLE-BILI-API] View API错误: {view_data.get('message')}", file=sys.stderr)
                return {'success': False, 'has_subtitle': False}

            # 从响应中提取字幕信息
            video_data = view_data.get('data', {})
            subtitle_info = video_data.get('subtitle', {})

            print(f"[SUBTITLE-BILI-API] 字幕信息: {subtitle_info}", file=sys.stderr)

            # 检查是否有字幕列表
            subtitles_list = subtitle_info.get('subtitles', [])

            if not subtitles_list:
                print("[SUBTITLE-BILI-API] 该视频无字幕", file=sys.stderr)
                return {'success': False, 'has_subtitle': False}

            # 下载第一个可用字幕
            subtitle_item = subtitles_list[0]
            subtitle_url = subtitle_item.get('subtitle_url')

            if not subtitle_url:
                print("[SUBTITLE-BILI-API] 字幕URL缺失", file=sys.stderr)
                return {'success': False, 'has_subtitle': False}

            # 下载字幕内容
            full_subtitle_url = f"https:{subtitle_url}" if not subtitle_url.startswith('http') else subtitle_url

            print(f"[SUBTITLE-BILI-API] 下载字幕: {full_subtitle_url}", file=sys.stderr)

            sub_response = requests.get(full_subtitle_url, headers=headers, timeout=15)
            sub_response.raise_for_status()

            subtitle_content = sub_response.json()

            # 解析为统一格式
            segments = cls._parse_bilibili_subtitle_to_segments(subtitle_content)

            if segments:
                full_text = '\n'.join([s['text'] for s in segments])
                print(f"[SUBTITLE-BILI-API] ✓ 方法2成功! 提取{len(segments)}条字幕", file=sys.stderr)

                return {
                    'success': True,
                    'has_subtitle': True,
                    'segments': segments,
                    'subtitles': segments,
                    'full_text': full_text,
                    'language': 'zh-Hans',
                    'subtitle_count': len(segments),
                    'message': '字幕提取成功（B站API）'
                }

            print("[SUBTITLE-BILI-API] 所有方法均失败", file=sys.stderr)
            return {'success': False, 'has_subtitle': False}

        except requests.exceptions.RequestException as e:
            print(f"[SUBTITLE-BILI-API] 网络请求异常: {str(e)[:100]}", file=sys.stderr)
            return {'success': False, 'has_subtitle': False}
        except Exception as e:
            print(f"[SUBTITLE-BILI-API] 异常: {str(e)[:100]}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {'success': False, 'has_subtitle': False}

    @staticmethod
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

    @classmethod
    def _parse_bilibili_subtitle_to_segments(cls, subtitle_data: dict) -> List[Dict]:
        """
        解析B站JSON字幕格式为统一segments格式: [{start, end, text, time}]

        B站字幕格式:
        {
            "body": [
                {"from": 0, "to": 5, "location": 2, "content": "字幕内容"},
                ...
            ]
        }

        Returns:
            [{start: float, end: float, text: str, time: str}]
        """
        result = []

        try:
            body = subtitle_data.get('body', [])

            for item in body:
                start = item.get('from', 0)  # 秒
                end = item.get('to', 0)  # 秒
                content = item.get('content', '')

                if content.strip():
                    # 格式化时间字符串
                    time_str = cls._format_seconds_to_time(start)

                    result.append({
                        'start': float(start),
                        'end': float(end),
                        'text': content.strip(),
                        'time': time_str  # 添加time字段
                    })

            return result

        except Exception as e:
            print(f"[SUBTITLE-BILI] 解析B站字幕失败: {str(e)}", file=sys.stderr)
            return []

    @classmethod
    def _process_subtitle_info(cls, info: dict, lang: str, url: str) -> Dict:
        """处理视频信息中的字幕数据 - 增强版，更宽松地处理字幕"""
        try:
            # 检查字幕
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})

            print(f"[SUBTITLE] Available subtitles: {list(subtitles.keys())}", file=sys.stderr)
            print(f"[SUBTITLE] Automatic captions: {list(automatic_captions.keys())}", file=sys.stderr)

            # 合并字幕和自动字幕
            all_subtitles = {**subtitles, **automatic_captions}

            print(f"[SUBTITLE] Total available subtitle tracks: {len(all_subtitles)}", file=sys.stderr)
            print(f"[SUBTITLE] 字幕轨道详情: {list(all_subtitles.keys())}", file=sys.stderr)
            # 打印每个轨道的数据类型信息
            for key, value in list(all_subtitles.items())[:5]:  # 限制输出数量
                if isinstance(value, list):
                    print(f"[SUBTITLE] 轨道 '{key}': list[{len(value)}]", file=sys.stderr)
                    if len(value) > 0:
                        print(f"[SUBTITLE]   首元素类型: {type(value[0])}", file=sys.stderr)
                        if isinstance(value[0], dict):
                            print(f"[SUBTITLE]   首元素keys: {list(value[0].keys())[:5]}", file=sys.stderr)
                            if 'url' in value[0]:
                                print(f"[SUBTITLE]   URL: {str(value[0]['url'])[:80]}...", file=sys.stderr)

            if not all_subtitles:
                print(f"[SUBTITLE] No subtitles found for this video", file=sys.stderr)
                return {
                    'success': False,
                    'has_subtitle': False,
                    'can_fallback_to_asr': True,
                    'message': '该视频暂无可用字幕。将自动使用ASR语音识别。'
                }

            # 选择可用的字幕（优先选择指定语言）
            subtitle_data = None
            subtitle_lang = None
            has_danmaku_only = False  # 标识是否只有弹幕

            # 扩展语言优先级列表（包含弹幕作为备选）
            lang_priority = [lang, 'zh-Hans', 'zh-CN', 'zh', 'zh-Hant', 'zh-TW', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'danmaku']

            # 尝试按优先级获取字幕
            for lang_code in lang_priority:
                if lang_code in all_subtitles:
                    subtitle_data = all_subtitles[lang_code]
                    subtitle_lang = lang_code
                    print(f"[SUBTITLE] 找到匹配语言字幕: {lang_code}", file=sys.stderr)
                    break

            if not subtitle_data and all_subtitles:
                # 如果没有匹配的语言，使用第一个可用字幕
                first_key = list(all_subtitles.keys())[0]
                subtitle_data = all_subtitles[first_key]
                subtitle_lang = first_key
                print(f"[SUBTITLE] 使用第一个可用字幕: {first_key}", file=sys.stderr)

                # 检查是否只有弹幕
                if first_key == 'danmaku':
                    has_danmaku_only = True
                    print(f"[SUBTITLE] 检测到弹幕轨道，尝试作为字幕处理", file=sys.stderr)

            if not subtitle_data:
                print(f"[SUBTITLE] 无法获取字幕数据", file=sys.stderr)
                return {
                    'success': False,
                    'has_subtitle': False,
                    'can_fallback_to_asr': True,
                    'message': '该视频暂无可用字幕。将自动使用ASR语音识别。'
                }

            # 解析字幕数据
            if isinstance(subtitle_data, list) and len(subtitle_data) > 0:
                print(f"[SUBTITLE] 字幕数据是数组，长度: {len(subtitle_data)}", file=sys.stderr)
                print(f"[SUBTITLE] 第一个元素类型: {type(subtitle_data[0])}", file=sys.stderr)
                if isinstance(subtitle_data[0], dict):
                    print(f"[SUBTITLE] 第一个元素keys: {list(subtitle_data[0].keys())}", file=sys.stderr)

                # 获取字幕URL
                subtitle_url = None
                if isinstance(subtitle_data[0], dict):
                    subtitle_url = subtitle_data[0].get('url')
                elif isinstance(subtitle_data[0], str) and subtitle_data[0].startswith('http'):
                    subtitle_url = subtitle_data[0]

                if subtitle_url:
                    print(f"[SUBTITLE] 找到字幕URL: {subtitle_url[:80]}...", file=sys.stderr)

                    # 下载字幕内容 - 添加必要的请求头
                    import requests
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://www.bilibili.com/',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    }
                    response = requests.get(subtitle_url, headers=headers, timeout=30)
                    response.raise_for_status()

                    # 检查内容类型
                    content_type = response.headers.get('Content-Type', '')
                    url_lower = subtitle_url.lower()

                    print(f"[SUBTITLE] URL扩展名: {url_lower[-10:]}, Content-Type: {content_type}", file=sys.stderr)

                    # 如果是XML格式（B站弹幕）
                    if url_lower.endswith('.xml') or 'xml' in content_type.lower():
                        print(f"[SUBTITLE] 检测到XML格式，使用XML解析", file=sys.stderr)

                        # 直接使用原始字节流解码UTF-8，避免response.text的编码问题
                        try:
                            xml_content = response.content.decode('utf-8')
                            print(f"[SUBTITLE] UTF-8解码成功，XML长度: {len(xml_content)}", file=sys.stderr)
                        except UnicodeDecodeError as e:
                            print(f"[SUBTITLE] UTF-8解码失败: {e}，尝试忽略错误", file=sys.stderr)
                            xml_content = response.content.decode('utf-8', errors='ignore')

                        formatted_subtitles = cls._parse_danmaku_xml(xml_content)
                        full_text = '\n'.join([s['text'] for s in formatted_subtitles])

                        if formatted_subtitles:
                            print(f"[SUBTITLE] ✓ XML弹幕提取成功! 提取{len(formatted_subtitles)}条弹幕", file=sys.stderr)
                            return {
                                'success': True,
                                'has_subtitle': True,
                                'is_danmaku': True,
                                'subtitles': formatted_subtitles,
                                'segments': formatted_subtitles,
                                'full_text': full_text,
                                'language': subtitle_lang,
                                'subtitle_count': len(formatted_subtitles),
                                'message': '弹幕提取成功（XML格式）'
                            }

                    # 解析JSON字幕
                    try:
                        subtitle_content = response.json()

                        # 检查是否是弹幕格式
                        if subtitle_lang == 'danmaku':
                            print(f"[SUBTITLE] 开始解析弹幕内容，数据类型: {type(subtitle_content)}", file=sys.stderr)
                            formatted_subtitles = cls._parse_danmaku(subtitle_content)
                            full_text = '\n'.join([s['text'] for s in formatted_subtitles])

                            if formatted_subtitles:
                                print(f"[SUBTITLE] ✓ 弹幕提取成功! 提取{len(formatted_subtitles)}条弹幕", file=sys.stderr)
                                # 弹幕内容作为补充，标识为弹幕模式
                                return {
                                    'success': True,
                                    'has_subtitle': True,
                                    'is_danmaku': True,  # 标识这是弹幕
                                    'subtitles': formatted_subtitles,
                                    'segments': formatted_subtitles,
                                    'full_text': full_text,
                                    'language': subtitle_lang,
                                    'subtitle_count': len(formatted_subtitles),
                                    'message': '弹幕提取成功（可作为AI分析的补充素材）'
                                }
                            else:
                                print(f"[SUBTITLE] ✗ 弹幕解析失败，数据格式可能不支持", file=sys.stderr)
                                print(f"[SUBTITLE] 弹幕数据样例: {str(subtitle_content)[:500]}", file=sys.stderr)
                                # 弹幕解析失败，继续尝试其他方法

                        # 正常字幕处理
                        else:
                            formatted_subtitles = cls._parse_subtitle_json(subtitle_content)
                            full_text = '\n'.join([s['text'] for s in formatted_subtitles])

                            if formatted_subtitles:
                                print(f"[SUBTITLE] ✓ 字幕提取成功! 提取{len(formatted_subtitles)}条字幕", file=sys.stderr)
                                return {
                                    'success': True,
                                    'has_subtitle': True,
                                    'subtitles': formatted_subtitles,
                                    'segments': formatted_subtitles,
                                    'full_text': full_text,
                                    'language': subtitle_lang,
                                    'subtitle_count': len(formatted_subtitles),
                                    'message': '字幕提取成功'
                                }
                    except json.JSONDecodeError:
                        print(f"[SUBTITLE] JSON解析失败，尝试其他格式", file=sys.stderr)

            # 如果JSON解析失败或没有URL，尝试其他方法
            print(f"[SUBTITLE] 无法通过URL获取字幕，尝试其他方法", file=sys.stderr)

            # 特殊处理：如果是弹幕且没有URL，尝试直接从数组中提取
            if subtitle_lang == 'danmaku' and isinstance(subtitle_data, list):
                print(f"[SUBTITLE] 尝试直接从弹幕数组提取数据", file=sys.stderr)
                formatted_subtitles = cls._parse_danmaku({'elements': subtitle_data})
                full_text = '\n'.join([s['text'] for s in formatted_subtitles])

                if formatted_subtitles:
                    print(f"[SUBTITLE] ✓ 直接弹幕提取成功! 提取{len(formatted_subtitles)}条弹幕", file=sys.stderr)
                    return {
                        'success': True,
                        'has_subtitle': True,
                        'is_danmaku': True,
                        'subtitles': formatted_subtitles,
                        'segments': formatted_subtitles,
                        'full_text': full_text,
                        'language': subtitle_lang,
                        'subtitle_count': len(formatted_subtitles),
                        'message': '弹幕提取成功（直接从数组提取）'
                    }

            print(f"[SUBTITLE] 尝试从info中直接提取字幕文本", file=sys.stderr)
            return cls._extract_from_info(info, lang)

        except Exception as e:
            print(f"[SUBTITLE] 处理字幕数据异常: {str(e)[:200]}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)

            return {
                'success': False,
                'has_subtitle': False,
                'can_fallback_to_asr': True,
                'message': f'字幕处理失败: {str(e)[:200]}'
            }

    @classmethod
    def _parse_subtitle_json(cls, subtitle_data: dict) -> List[Dict]:
        """
        解析JSON格式字幕为统一格式

        Args:
            subtitle_data: JSON字幕数据

        Returns:
            [{'time': '00:00:00', 'text': '字幕内容'}]
        """
        result = []

        # 处理不同的字幕格式
        if 'events' in subtitle_data:
            # YouTube DCP格式
            for event in subtitle_data.get('events', []):
                start_ms = event.get('tStartMs', 0)
                duration_ms = event.get('dDurationMs', 0)

                start_time = cls._format_timestamp(start_ms)
                end_time = cls._format_timestamp(start_ms + duration_ms)

                # 清理字幕文本
                text = event.get('segs', [])
                text_content = ''.join([seg.get('utf8', '') for seg in text])

                if text_content.strip():
                    result.append({
                        'time': f"{start_time} --> {end_time}",
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': text_content.strip()
                    })

        elif 'segments' in subtitle_data:
            # 另一种格式
            for seg in subtitle_data.get('segments', []):
                start_time = cls._format_seconds(seg.get('start', 0))
                end_time = cls._format_seconds(seg.get('end', 0))
                text = seg.get('text', '')

                if text.strip():
                    result.append({
                        'time': f"{start_time} --> {end_time}",
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': text.strip()
                    })

        return result

    @classmethod
    def _parse_danmaku_xml(cls, xml_content: str) -> List[Dict]:
        """
        解析B站弹幕XML格式

        B站弹幕XML格式:
        <?xml version="1.0" encoding="UTF-8"?>
        <i>
            <d p="时间,类型,大小,颜色,发送时间,弹幕池,发送者ID,弹幕ID">弹幕内容</d>
            ...
        </i>

        Args:
            xml_content: XML格式的弹幕内容

        Returns:
            [{'time': '00:00:00', 'text': '弹幕内容'}]
        """
        result = []

        try:
            import xml.etree.ElementTree as ET

            print(f"[DANMAKU-XML] 开始解析XML，长度: {len(xml_content)}", file=sys.stderr)

            # 确保XML内容是UTF-8编码
            if isinstance(xml_content, bytes):
                xml_content = xml_content.decode('utf-8', errors='ignore')
            else:
                # 如果是字符串，尝试重新编码为UTF-8
                try:
                    # 检测是否已经是正确的UTF-8
                    xml_content.encode('utf-8').decode('utf-8')
                except UnicodeError:
                    # 如果不是，尝试修复
                    xml_content = xml_content.encode('latin-1').decode('utf-8', errors='ignore')

            print(f"[DANMAKU-XML] XML内容样例: {xml_content[:200]}", file=sys.stderr)

            # 解析XML
            root = ET.fromstring(xml_content)

            # B站弹幕的根节点通常是 <i>
            for danmaku_elem in root.findall('d'):
                # 获取弹幕内容
                content = danmaku_elem.text

                if not content or not content.strip():
                    continue

                # 解析p属性
                p_attr = danmaku_elem.get('p', '')
                if p_attr:
                    try:
                        # p属性格式: "时间,类型,大小,颜色,发送时间,弹幕池,发送者ID,弹幕ID"
                        p_parts = p_attr.split(',')
                        time_ms = float(p_parts[0]) * 1000 if len(p_parts) > 0 else 0

                        # 格式化时间
                        start_time = cls._format_timestamp(int(time_ms))

                        result.append({
                            'time': start_time,
                            'start_time': start_time,
                            'end_time': start_time,
                            'text': content.strip()
                        })
                    except (ValueError, IndexError) as e:
                        print(f"[DANMAKU-XML] 解析p属性失败: {e}", file=sys.stderr)
                        # 即使时间解析失败，仍然保留弹幕内容
                        result.append({
                            'time': '00:00',
                            'start_time': '00:00',
                            'end_time': '00:00',
                            'text': content.strip()
                        })
                else:
                    # 没有时间信息的弹幕
                    result.append({
                        'time': '00:00',
                        'start_time': '00:00',
                        'end_time': '00:00',
                        'text': content.strip()
                    })

            print(f"[DANMAKU-XML] 解析完成，提取{len(result)}条弹幕", file=sys.stderr)
            return result

        except ET.ParseError as e:
            print(f"[DANMAKU-XML] XML解析错误: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"[DANMAKU-XML] 解析异常: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return []

    @classmethod
    def _parse_danmaku(cls, danmaku_data: dict) -> List[Dict]:
        """
        解析弹幕数据为统一格式
        弹幕虽然不是字幕，但包含用户评论和关键词，可以作为AI分析的补充素材

        Args:
            danmaku_data: 弹幕数据

        Returns:
            [{'time': '00:00:00', 'text': '弹幕内容'}]
        """
        result = []

        # 添加详细日志来调试弹幕数据格式
        print(f"[DANMAKU] 开始解析弹幕数据，类型: {type(danmaku_data)}", file=sys.stderr)

        if isinstance(danmaku_data, dict):
            print(f"[DANMAKU] 数据keys: {list(danmaku_data.keys())[:10]}", file=sys.stderr)
            # 打印部分数据样例（避免日志过长）
            for key in list(danmaku_data.keys())[:5]:
                val = danmaku_data[key]
                if isinstance(val, list):
                    print(f"[DANMAKU] {key}: list[{len(val)}]", file=sys.stderr)
                elif isinstance(val, dict):
                    print(f"[DANMAKU] {key}: dict with keys {list(val.keys())[:5]}", file=sys.stderr)
                else:
                    print(f"[DANMAKU] {key}: {str(val)[:100]}", file=sys.stderr)

        # B站弹幕格式1: elements字段
        if 'elements' in danmaku_data:
            print(f"[DANMAKU] 检测到elements格式", file=sys.stderr)
            for element in danmaku_data.get('elements', []):
                # 弹幕通常包含时间、内容、发送者等信息
                content = element.get('content', '')
                time_ms = element.get('time', 0) or element.get('progress', 0)

                if content.strip():
                    start_time = cls._format_timestamp(time_ms)
                    result.append({
                        'time': start_time,
                        'start_time': start_time,
                        'end_time': start_time,  # 弹幕没有结束时间
                        'text': content.strip()
                    })

        # B站弹幕格式2: data字段（常见格式）
        elif 'data' in danmaku_data:
            print(f"[DANMAKU] 检测到data格式", file=sys.stderr)
            data = danmaku_data.get('data', [])
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        content = item.get('content', '') or item.get('text', '') or item.get('comment', '')
                        time_ms = item.get('time', 0) or item.get('progress', 0) or item.get('mtime', 0)

                        if content.strip():
                            start_time = cls._format_timestamp(time_ms)
                            result.append({
                                'time': start_time,
                                'start_time': start_time,
                                'end_time': start_time,
                                'text': content.strip()
                            })

        # B站弹幕格式3: cmd字段（XML格式或特殊格式）
        elif 'cmd' in danmaku_data:
            print(f"[DANMAKU] 检测到cmd格式", file=sys.stderr)
            # 尝试解析cmd格式的弹幕
            cmd_data = danmaku_data.get('cmd', {})
            if isinstance(cmd_data, dict) and 'dms' in cmd_data:
                for dm in cmd_data.get('dms', []):
                    content = dm.get('content', '') or dm.get('text', '')
                    time_ms = dm.get('time', 0) or dm.get('progress', 0)

                    if content.strip():
                        start_time = cls._format_timestamp(time_ms)
                        result.append({
                            'time': start_time,
                            'start_time': start_time,
                            'end_time': start_time,
                            'text': content.strip()
                        })

        # B站弹幕格式4: 直接是数组
        elif isinstance(danmaku_data, list):
            print(f"[DANMAKU] 检测到数组格式，长度: {len(danmaku_data)}", file=sys.stderr)
            for item in danmaku_data:
                if isinstance(item, dict):
                    content = item.get('content', '') or item.get('text', '') or item.get('comment', '') or item.get('m', '')
                    time_ms = item.get('time', 0) or item.get('progress', 0) or item.get('mtime', 0)

                    if content.strip():
                        start_time = cls._format_timestamp(time_ms)
                        result.append({
                            'time': start_time,
                            'start_time': start_time,
                            'end_time': start_time,
                            'text': content.strip()
                        })
                elif isinstance(item, str) and item.strip():
                    # 纯文本弹幕
                    result.append({
                        'time': '00:00',
                        'start_time': '00:00',
                        'end_time': '00:00',
                        'text': item.strip()
                    })

        # 尝试递归搜索可能的弹幕数据
        else:
            print(f"[DANMAKU] 未知格式，尝试递归搜索", file=sys.stderr)
            result.extend(cls._search_danmaku_recursive(danmaku_data))

        print(f"[DANMAKU] 解析完成，提取{len(result)}条弹幕", file=sys.stderr)
        return result

    @classmethod
    def _search_danmaku_recursive(cls, data, depth=0, max_depth=3) -> List[Dict]:
        """
        递归搜索数据中的弹幕内容
        """
        result = []

        if depth > max_depth:
            return result

        if isinstance(data, dict):
            # 检查常见的弹幕字段名
            for key in ['content', 'text', 'comment', 'm', 'msg']:
                if key in data:
                    content = data[key]
                    if isinstance(content, str) and content.strip():
                        # 查找时间字段
                        time_ms = 0
                        for time_key in ['time', 'progress', 'mtime', 'ts']:
                            if time_key in data:
                                time_ms = data[time_key]
                                break

                        start_time = cls._format_timestamp(time_ms)
                        result.append({
                            'time': start_time,
                            'start_time': start_time,
                            'end_time': start_time,
                            'text': content.strip()
                        })
                        break

            # 递归搜索字典的值
            for value in data.values():
                result.extend(cls._search_danmaku_recursive(value, depth + 1, max_depth))

        elif isinstance(data, list) and len(data) > 0:
            # 检查第一个元素来判断数组类型
            first_item = data[0]

            if isinstance(first_item, dict):
                # 可能是弹幕数组
                if any(key in first_item for key in ['content', 'text', 'comment', 'm']):
                    for item in data:
                        if isinstance(item, dict):
                            content = item.get('content', '') or item.get('text', '') or item.get('comment', '') or item.get('m', '')
                            time_ms = item.get('time', 0) or item.get('progress', 0) or item.get('mtime', 0)

                            if content.strip():
                                start_time = cls._format_timestamp(time_ms)
                                result.append({
                                    'time': start_time,
                                    'start_time': start_time,
                                    'end_time': start_time,
                                    'text': content.strip()
                                })
                else:
                    # 递归搜索数组元素
                    for item in data[:10]:  # 限制递归数量
                        result.extend(cls._search_danmaku_recursive(item, depth + 1, max_depth))

        return result

    @classmethod
    def _extract_from_info(cls, info: dict, lang: str) -> Dict:
        """从info字典中提取字幕"""
        # 这里可以添加其他提取逻辑
        return {
            'success': False,
            'has_subtitle': False,
            'message': '暂无可用字幕'
        }

    @staticmethod
    def _format_timestamp(milliseconds: int) -> str:
        """将毫秒转换为时间戳格式 (HH:MM:SS.mmm)"""
        seconds = milliseconds / 1000
        return SubtitleExtractor._format_seconds(seconds)

    @staticmethod
    def _format_seconds(seconds: float) -> str:
        """将秒转换为时间戳格式 (HH:MM:SS)"""
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds, 3600)
        minutes, secs = divmod(remainder, 60)

        # 添加毫秒
        ms = int((seconds - int(seconds)) * 1000)

        if td.days > 0 or hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    @classmethod
    def format_for_ai(cls, subtitles: List[Dict]) -> str:
        """
        将字幕格式化为适合AI分析的文本

        Returns:
            带时间戳的字幕文本
        """
        if not subtitles:
            return ""

        formatted_lines = []
        for subtitle in subtitles:
            formatted_lines.append(f"[{subtitle['time']}] {subtitle['text']}")

        return '\n'.join(formatted_lines)


# 便捷函数
def extract_subtitles(url: str, lang: str = 'zh-Hans') -> Dict:
    """提取视频字幕的便捷函数"""
    return SubtitleExtractor.extract_subtitles(url, lang)
