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
        提取视频字幕 - 增强版，支持B站公开字幕无需Cookie

        Args:
            url: 视频链接
            lang: 字幕语言 (zh-Hans: 简体中文, en: 英语, etc.)

        Returns:
            {
                'success': bool,
                'has_subtitle': bool,
                'subtitles': List[{'time': str, 'text': str}],
                'full_text': str,
                'language': str,
                'message': str
            }
        """
        try:
            # 检查平台支持
            platform = cls.identify_platform(url)
            if not platform:
                return {
                    'success': False,
                    'has_subtitle': False,
                    'message': f'该平台暂不支持字幕提取，目前仅支持B站和YouTube'
                }

            print(f"[SUBTITLE] Platform: {platform}, URL: {url[:50]}", file=sys.stderr)

            # ========== 核心修复：B站字幕提取优化 ==========
            if platform == 'bilibili':
                return cls._extract_bilibili_subtitles(url, lang)

            # ========== YouTube等其他平台 ==========
            return cls._extract_generic_subtitles(url, lang, platform)

        except Exception as e:
            error_msg = str(e)
            print(f"[SUBTITLE] Error details: {error_msg}", file=sys.stderr)
            print(f"[SUBTITLE] Error type: {type(e).__name__}", file=sys.stderr)

            return {
                'success': False,
                'has_subtitle': False,
                'can_fallback_to_audio': True,  # 标识可以降级到音频转写
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
        直接从B站API获取字幕（降级方案）

        Args:
            bvid: B站视频ID
            info: yt-dlp获取的视频信息

        Returns:
            字幕提取结果
        """
        import requests

        try:
            cid = info.get('cid') or info.get('chapter_id')
            if not cid:
                print("[SUBTITLE-BILI-API] 缺少cid，无法调用API", file=sys.stderr)
                return {'success': False, 'has_subtitle': False}

            # B站字幕API
            api_url = f"https://api.bilibili.com/x/player/v2"
            params = {
                'bvid': bvid,
                'cid': cid
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': f'https://www.bilibili.com/video/{bvid}',
                'Accept': 'application/json',
            }

            print(f"[SUBTITLE-BILI-API] 请求: {api_url}", file=sys.stderr)

            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()

            data = response.json()

            if data.get('code') != 0:
                print(f"[SUBTITLE-BILI-API] API错误: {data.get('message')}", file=sys.stderr)
                return {'success': False, 'has_subtitle': False}

            # 解析字幕数据
            subtitle_info = data.get('data', {}).get('subtitle', {})
            subtitles_list = subtitle_info.get('subtitles', [])

            if not subtitles_list:
                print("[SUBTITLE-BILI-API] 无字幕数据", file=sys.stderr)
                return {'success': False, 'has_subtitle': False}

            # 下载第一个可用字幕
            subtitle_item = subtitles_list[0]
            subtitle_url = subtitle_item.get('subtitle_url')

            if not subtitle_url:
                print("[SUBTITLE-BILI-API] 字幕URL缺失", file=sys.stderr)
                return {'success': False, 'has_subtitle': False}

            # 下载字幕内容
            full_subtitle_url = f"https:{subtitle_url}" if not subtitle_url.startswith('http') else subtitle_url

            sub_response = requests.get(full_subtitle_url, headers=headers, timeout=15)
            sub_response.raise_for_status()

            subtitle_content = sub_response.json()

            # 解析B站JSON字幕格式
            formatted_subtitles = cls._parse_bilibili_subtitle(subtitle_content)

            if formatted_subtitles:
                full_text = '\n'.join([s['text'] for s in formatted_subtitles])

                return {
                    'success': True,
                    'has_subtitle': True,
                    'subtitles': formatted_subtitles,
                    'full_text': full_text,
                    'language': 'zh-Hans',
                    'subtitle_count': len(formatted_subtitles),
                    'message': '字幕提取成功（API降级方案）'
                }

            return {'success': False, 'has_subtitle': False}

        except Exception as e:
            print(f"[SUBTITLE-BILI-API] 异常: {str(e)[:100]}", file=sys.stderr)
            return {'success': False, 'has_subtitle': False}

    @classmethod
    def _parse_bilibili_subtitle(cls, subtitle_data: dict) -> List[Dict]:
        """
        解析B站JSON字幕格式

        B站字幕格式示例:
        {
            "body": [
                {"from": 0, "to": 5, "location": 2, "content": "字幕内容"},
                ...
            ]
        }
        """
        result = []

        try:
            body = subtitle_data.get('body', [])

            for item in body:
                start_time = item.get('from', 0)  # 秒
                end_time = item.get('to', 0)  # 秒
                content = item.get('content', '')

                if content.strip():
                    start_str = cls._format_seconds(start_time)
                    end_str = cls._format_seconds(end_time)

                    result.append({
                        'time': f"{start_str} --> {end_str}",
                        'start_time': start_str,
                        'end_time': end_str,
                        'text': content.strip()
                    })

            return result

        except Exception as e:
            print(f"[SUBTITLE-BILI] 解析B站字幕失败: {str(e)}", file=sys.stderr)
            return []

    @classmethod
    def _extract_generic_subtitles(cls, url: str, lang: str, platform: str) -> Dict:
        """
        通用字幕提取（YouTube等平台）
        """
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang, 'zh', 'zh-Hans', 'zh-Hant', 'en'],
            'subtitlesformat': 'json',
            'extract_flat': False,
            'nocheckcertificate': True,
            'verbose': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return cls._process_subtitle_info(info, lang, url)

        except Exception as e:
            error_msg = str(e)
            print(f"[SUBTITLE-{platform.upper()}] Error: {error_msg[:200]}", file=sys.stderr)

            return {
                'success': False,
                'has_subtitle': False,
                'can_fallback_to_audio': True,
                'message': f'字幕提取失败: {error_msg[:200]}'
            }

    @classmethod
    def _process_subtitle_info(cls, info: dict, lang: str, url: str) -> Dict:
        """处理视频信息中的字幕数据"""
        try:
            # 检查字幕
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})

            print(f"[SUBTITLE] Available subtitles: {list(subtitles.keys())}", file=sys.stderr)
            print(f"[SUBTITLE] Automatic captions: {list(automatic_captions.keys())}", file=sys.stderr)

            # 合并字幕和自动字幕
            all_subtitles = {**subtitles, **automatic_captions}

            print(f"[SUBTITLE] Total available subtitle tracks: {len(all_subtitles)}", file=sys.stderr)

            if not all_subtitles:
                print(f"[SUBTITLE] No subtitles found for this video", file=sys.stderr)
                return {
                    'success': False,
                    'has_subtitle': False,
                    'can_analyze_without_subtitle': True,  # 标识可以尝试无字幕分析
                    'message': '该视频暂无可用字幕。但您可以尝试基于标题和描述进行AI分析。'
                }

            # 选择可用的字幕（优先选择指定语言）
            subtitle_data = None
            subtitle_lang = None
            has_danmaku_only = False  # 标识是否只有弹幕

            # 尝试按优先级获取字幕
            for lang_code in [lang, 'zh-Hans', 'zh', 'zh-Hant', 'en']:
                if lang_code in all_subtitles:
                    subtitle_data = all_subtitles[lang_code]
                    subtitle_lang = lang_code
                    break

            if not subtitle_data and all_subtitles:
                # 如果没有匹配的语言，使用第一个可用字幕
                first_key = list(all_subtitles.keys())[0]
                subtitle_data = all_subtitles[first_key]
                subtitle_lang = first_key

                # 检查是否只有弹幕
                if first_key == 'danmaku':
                    has_danmaku_only = True
                    print(f"[SUBTITLE] 只有弹幕可用，将尝试提取弹幕内容用于AI分析", file=sys.stderr)

            if not subtitle_data:
                return {
                    'success': False,
                    'has_subtitle': False,
                    'can_analyze_without_subtitle': True,
                    'message': '该视频暂无可用字幕。但您可以尝试基于标题和描述进行AI分析。'
                }

            # 解析字幕数据
            if isinstance(subtitle_data, list) and len(subtitle_data) > 0:
                # 获取字幕URL
                subtitle_url = subtitle_data[0].get('url') if isinstance(
                    subtitle_data[0], dict) else None

                if subtitle_url:
                    # 下载字幕内容 - 添加必要的请求头
                    import requests
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': 'https://www.bilibili.com/',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    }
                    response = requests.get(subtitle_url, headers=headers, timeout=30)
                    response.raise_for_status()

                    # 解析JSON字幕
                    try:
                        subtitle_content = response.json()

                        # 检查是否是弹幕格式
                        if subtitle_lang == 'danmaku':
                            print(f"[SUBTITLE] 检测到弹幕格式，使用弹幕处理逻辑", file=sys.stderr)
                            formatted_subtitles = cls._parse_danmaku(subtitle_content)
                            full_text = '\n'.join([s['text'] for s in formatted_subtitles])

                            # 弹幕内容作为补充，标识为弹幕模式
                            return {
                                'success': True,
                                'has_subtitle': True,
                                'is_danmaku': True,  # 标识这是弹幕
                                'subtitles': formatted_subtitles,
                                'full_text': full_text,
                                'language': subtitle_lang,
                                'subtitle_count': len(formatted_subtitles),
                                'message': '弹幕提取成功（可作为AI分析的补充素材）'
                            }
                        else:
                            # 正常字幕处理
                            formatted_subtitles = cls._parse_subtitle_json(subtitle_content)
                            full_text = '\n'.join([s['text'] for s in formatted_subtitles])

                            return {
                                'success': True,
                                'has_subtitle': True,
                                'subtitles': formatted_subtitles,
                                'full_text': full_text,
                                'language': subtitle_lang,
                                'subtitle_count': len(formatted_subtitles),
                                'message': '字幕提取成功'
                            }
                    except json.JSONDecodeError:
                        # 尝试其他格式解析
                        pass

            # 如果JSON解析失败，尝试直接从信息中提取
            return cls._extract_from_info(info, lang)

        except Exception as e:
            return {
                'success': False,
                'has_subtitle': False,
                'message': f'字幕处理失败: {str(e)}'
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

        # B站弹幕格式
        if 'elements' in danmaku_data:
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

        # 如果是数组格式
        elif isinstance(danmaku_data, list):
            for item in danmaku_data:
                if isinstance(item, dict):
                    content = item.get('content', '') or item.get('text', '')
                    time_ms = item.get('time', 0) or item.get('progress', 0)

                    if content.strip():
                        start_time = cls._format_timestamp(time_ms)
                        result.append({
                            'time': start_time,
                            'start_time': start_time,
                            'end_time': start_time,
                            'text': content.strip()
                        })

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
