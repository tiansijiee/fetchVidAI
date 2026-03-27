"""
视频解析模块 - 基于 yt-dlp
支持平台：抖音、B站、小红书、YouTube
"""
import yt_dlp
import re
import sys
import time
import hashlib
from typing import Dict, List, Optional
from functools import lru_cache


class VideoParser:
    """视频解析器"""

    # 支持的平台域名
    PLATFORMS = {
        'bilibili': ['bilibili.com', 'b23.tv'],
        'weibo': ['weibo.com', 'weibo.cn'],
        'zhihu': ['zhihu.com', 'zhuanlan.zhihu.com'],
        'youtube': ['youtube.com', 'youtu.be'],
        'twitter': ['twitter.com', 'x.com'],
        'tiktok': ['tiktok.com'],
        'instagram': ['instagram.com'],
        'vimeo': ['vimeo.com'],
        # 不再支持的平台（已失效或需要Cookie）
        # 'douyin': ['douyin.com', 'iesdouyin.com'],  # 已失效
        # 'xiaohongshu': ['xiaohongshu.com', 'xhslink.com'],  # 需要Cookie
    }

    # 缓存配置
    _cache = {}
    _cache_ttl = 300  # 5分钟缓存

    @classmethod
    def _get_cache_key(cls, url: str) -> str:
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()

    @classmethod
    def _get_from_cache(cls, url: str) -> Optional[Dict]:
        """从缓存获取数据"""
        cache_key = cls._get_cache_key(url)
        if cache_key in cls._cache:
            cached_data, timestamp = cls._cache[cache_key]
            if time.time() - timestamp < cls._cache_ttl:
                print(f"[CACHE] Hit for URL: {url[:50]}...", file=sys.stderr)
                return cached_data
            else:
                # 缓存过期，删除
                del cls._cache[cache_key]
        return None

    @classmethod
    def _save_to_cache(cls, url: str, data: Dict):
        """保存数据到缓存"""
        cache_key = cls._get_cache_key(url)
        cls._cache[cache_key] = (data, time.time())
        # 限制缓存大小，最多保留100个条目
        if len(cls._cache) > 100:
            oldest_key = min(cls._cache.keys(), key=lambda k: cls._cache[k][1])
            del cls._cache[oldest_key]
        print(f"[CACHE] Saved for URL: {url[:50]}...", file=sys.stderr)

    @classmethod
    def clear_cache(cls):
        """清空缓存"""
        cls._cache.clear()
        print("[CACHE] Cleared all cache", file=sys.stderr)

    @classmethod
    def identify_platform(cls, url: str) -> Optional[str]:
        """识别视频平台"""
        for platform, domains in cls.PLATFORMS.items():
            if any(domain in url for domain in domains):
                return platform
        return None

    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, str]:
        """验证 URL 格式"""
        if not url or not url.strip():
            return False, "请输入视频链接"

        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            return False, "请输入有效的链接（需以 http:// 或 https:// 开头）"

        platform = cls.identify_platform(url)
        if not platform:
            return False, "不支持的平台，请输入抖音、B站、小红书或YouTube的链接"

        return True, platform

    @staticmethod
    def format_duration(seconds) -> str:
        """格式化时长"""
        if not seconds:
            return "未知"
        # 确保是整数
        try:
            total_seconds = int(float(seconds))
        except (ValueError, TypeError):
            return "未知"

        minutes = total_seconds // 60
        secs = total_seconds % 60
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    @staticmethod
    def format_filesize(bytes: Optional[int]) -> str:
        """格式化文件大小"""
        if not bytes:
            return "未知大小"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"

    @staticmethod
    def extract_formats(info: Dict, platform: str = None) -> List[Dict]:
        """
        提取可用格式列表
        针对B站优化：支持多分辨率选择，包括DASH格式
        """
        formats = []

        # 获取所有格式
        all_formats = info.get('formats', [])

        # B站特殊处理：收集所有可用分辨率
        if platform == 'bilibili':
            # B站DASH格式：分别收集视频和音频流
            video_formats = []
            audio_formats = []

            for fmt in all_formats:
                format_id = fmt.get('format_id', '')
                vcodec = fmt.get('vcodec', 'none')
                acodec = fmt.get('acodec', 'none')

                # 跳过纯图片格式
                if fmt.get('ext') == 'jpg' or fmt.get('ext') == 'png':
                    continue

                # 视频流（有视频编码）
                if vcodec != 'none':
                    height = fmt.get('height')
                    if height:  # 只包含有明确分辨率的
                        quality_note = ''
                        # 添加画质标识
                        if 'dash-video' in format_id or fmt.get('protocol') == 'http_dash_segments':
                            if height >= 1080:
                                quality_note = ' (高清)'
                            elif height >= 720:
                                quality_note = ' (超清)'
                            elif height >= 480:
                                quality_note = ' (标清)'
                            else:
                                quality_note = ' (流畅)'

                        video_formats.append({
                            'quality': f"{height}p{quality_note}",
                            'format_id': format_id,
                            'ext': fmt.get('ext', 'mp4'),
                            'filesize': fmt.get('filesize') or fmt.get('filesize_approx'),
                            'width': fmt.get('width'),
                            'height': height,
                            'vcodec': vcodec,
                            'acodec': acodec,
                            'has_audio': acodec != 'none',
                            'url': fmt.get('url'),
                            'http_headers': fmt.get('http_headers', {}),
                            'protocol': fmt.get('protocol', ''),
                            'is_dash': 'dash' in format_id or fmt.get('protocol') == 'http_dash_segments'
                        })

                # 音频流
                elif acodec != 'none':
                    audio_formats.append({
                        'quality': "音频",
                        'format_id': format_id,
                        'ext': fmt.get('ext', 'm4a'),
                        'filesize': fmt.get('filesize') or fmt.get('filesize_approx'),
                        'acodec': acodec,
                        'abr': fmt.get('abr', 0),
                        'url': fmt.get('url'),
                        'http_headers': fmt.get('http_headers', {}),
                        'is_audio_only': True
                    })

            # 按分辨率排序视频格式
            video_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)), reverse=True)

            # 去重相同分辨率，保留最高质量
            seen_heights = {}
            unique_video_formats = []
            for fmt in video_formats:
                height = fmt.get('height')
                if height and height not in seen_heights:
                    seen_heights[height] = fmt
                    unique_video_formats.append(fmt)
                elif height and fmt.get('filesize', 0) > seen_heights[height].get('filesize', 0):
                    # 替换为文件更大的（质量更好）
                    idx = next(i for i, f in enumerate(unique_video_formats) if f.get('height') == height)
                    unique_video_formats[idx] = fmt

            # 添加最高质量的音频
            if audio_formats:
                audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
                unique_video_formats.insert(0, audio_formats[0])

            # 添加"最佳组合"选项（推荐）
            if unique_video_formats:
                best_video = next((f for f in unique_video_formats if f.get('height')), None)
                if best_video:
                    best_quality = best_video.get('height')
                    unique_video_formats.insert(0, {
                        'quality': f"🎬 最佳画质 ({best_quality}p + 音频)",
                        'format_id': 'best',
                        'ext': 'mp4',
                        'filesize': None,  # 需要合并后才知道
                        'recommended': True
                    })

            formats = unique_video_formats

        else:
            # 其他平台的格式提取
            seen_resolutions = set()
            for fmt in all_formats:
                # 跳过只有音频的格式（除非是纯音频平台）
                if fmt.get('vcodec') == 'none' and platform not in ['soundcloud', 'bandcamp']:
                    continue

                # 获取分辨率
                width = fmt.get('width')
                height = fmt.get('height')

                if width and height:
                    resolution = f"{height}p"
                    if resolution in seen_resolutions:
                        continue
                    seen_resolutions.add(resolution)

                    # 获取下载URL
                    url = fmt.get('url')
                    if not url and 'formats' in fmt:
                        for sub_fmt in fmt.get('formats', []):
                            if sub_fmt.get('url'):
                                url = sub_fmt.get('url')
                                break

                    formats.append({
                        'quality': resolution,
                        'format_id': fmt.get('format_id'),
                        'url': url,
                        'ext': fmt.get('ext', 'mp4'),
                        'filesize': fmt.get('filesize'),
                        'width': width,
                        'height': height,
                        'http_headers': fmt.get('http_headers', {})
                    })

            # 按分辨率排序（从高到低）
            formats.sort(key=lambda x: x.get('height', 0), reverse=True)

        # 如果没有找到视频格式，使用默认格式
        if not formats and 'url' in info:
            formats.append({
                'quality': '默认画质',
                'format_id': 'default',
                'url': info['url'],
                'ext': info.get('ext', 'mp4'),
                'filesize': info.get('filesize'),
                'width': info.get('width'),
                'height': info.get('height'),
                'http_headers': info.get('http_headers', {})
            })

        return formats

    @classmethod
    def parse(cls, url: str) -> Dict:
        """
        解析视频链接（带缓存优化）
        返回: {
            'success': bool,
            'message': str,
            'data': dict (视频信息)
        }
        """
        # 验证 URL
        is_valid, result = cls.validate_url(url)
        if not is_valid:
            return {
                'success': False,
                'message': result
            }

        platform = result

        # 检查缓存
        cached_result = cls._get_from_cache(url)
        if cached_result:
            return cached_result

        # 优化的 yt-dlp 配置（针对快速解析）
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,  # 跳过证书检查
            'socket_timeout': 15,  # 减少超时时间到15秒
            'extract_flat': False,  # 需要完整信息用于格式提取
            # 优化网络请求
            'concurrent_fragment_downloads': 2,  # 并发下载片段
        }

        # 平台特定优化
        if platform == 'bilibili':
            ydl_opts.update({
                'socket_timeout': 20,  # B站需要更长的超时
                'extractor_args': {
                    'bilibili': {
                        'prefer_formats': 'dash-flv,_dash-mp4,aac-flv,mp4-flv'
                    }
                }
            })
        elif platform == 'youtube':
            ydl_opts.update({
                'socket_timeout': 10,  # YouTube 响应较快
            })

        try:
            print(f"[PARSE] Starting parsing for {platform}: {url[:50]}...", file=sys.stderr)
            start_time = time.time()

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                parse_time = time.time() - start_time
                print(f"[PARSE] Completed in {parse_time:.2f}s for {platform}", file=sys.stderr)

                # 提取视频信息
                video_data = {
                    'platform': platform,
                    'title': info.get('title', '未知标题'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': cls.format_duration(info.get('duration')),
                    'duration_seconds': info.get('duration', 0),
                    'uploader': info.get('uploader', info.get('channel', '')),
                    'view_count': info.get('view_count'),
                    'description': info.get('description', '')[:200] if info.get('description') else '',
                }

                # 提取可用格式（传递平台信息）
                formats = cls.extract_formats(info, platform)
                video_data['formats'] = formats

                # 添加格式化的文件大小
                for fmt in formats:
                    fmt['size_formatted'] = cls.format_filesize(fmt.get('filesize'))

                result = {
                    'success': True,
                    'message': '解析成功',
                    'data': video_data
                }

                # 保存到缓存
                cls._save_to_cache(url, result)

                return result

        except Exception as e:
            error_msg = str(e)
            print(f"[PARSE] Error for {platform}: {error_msg[:100]}", file=sys.stderr)

            # 根据错误类型返回友好提示
            if 'Unsupported URL' in error_msg:
                return {
                    'success': False,
                    'message': '不支持的视频链接，请检查链接是否正确'
                }
            elif 'HTTP Error' in error_msg:
                return {
                    'success': False,
                    'message': '网络请求失败，请稍后重试'
                }
            elif 'Video unavailable' in error_msg:
                return {
                    'success': False,
                    'message': '视频不可用或已被删除'
                }
            elif 'Sign in' in error_msg or 'login' in error_msg.lower():
                return {
                    'success': False,
                    'message': '该视频需要登录才能访问'
                }
            elif 'timeout' in error_msg.lower():
                return {
                    'success': False,
                    'message': '解析超时，请稍后重试'
                }
            else:
                return {
                    'success': False,
                    'message': f'解析失败：{error_msg[:100]}'
                }


# 快捷函数
def parse_video(url: str) -> Dict:
    """快捷解析函数"""
    return VideoParser.parse(url)
