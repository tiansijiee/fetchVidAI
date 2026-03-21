"""
抖音专用视频下载模块
核心原理：
1. 分享链接 → 302重定向 → 提取 video_id
2. 调用抖音公开 API 获取视频信息
3. 将 playwm 替换为 play 获取无水印视频

由于抖音 API 经常变化，本模块实现多级降级策略：
- 方法1: 官方 API（可能失效）
- 方法2: 网页解析（可能需要签名）
- 方法3: yt-dlp（作为最终后备）

参考：rathodpratham-dev/douyin_video_downloader (MIT License)
"""
import requests
import re
import json
import sys
import subprocess
import tempfile
import os
from typing import Dict, Optional
import urllib.parse


class DouyinDownloader:
    """抖音视频专用下载器"""

    # 抖音 API 端点
    API_BASE = "https://www.iesdouyin.com"

    @staticmethod
    def format_duration(seconds) -> str:
        """格式化时长"""
        if not seconds or seconds <= 0:
            return "未知"
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

    # 请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.douyin.com/',
    }

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        从抖音链接中提取 video_id

        支持的格式：
        - https://v.douyin.com/xxxxx/ (短链接)
        - https://www.douyin.com/video/xxxxx
        - https://www.douyin.com/user/.../video/xxxxx
        """
        try:
            # 处理短链接 - 跟随重定向
            if 'v.douyin.com' in url:
                response = requests.head(url, allow_redirects=True, timeout=10)
                final_url = response.url
            else:
                final_url = url

            # 从 URL 中提取 video_id
            # 格式：/video/7123456789012345678
            match = re.search(r'/video/(\d+)', final_url)
            if match:
                return match.group(1)

            # 格式：/share/video/7123456789012345678
            match = re.search(r'/share/video/(\d+)', final_url)
            if match:
                return match.group(1)

            return None

        except Exception as e:
            print(f"[DOUYIN] Extract video_id error: {e}", file=sys.stderr)
            return None

    @staticmethod
    def get_video_info(video_id: str) -> Dict:
        """
        通过抖音 API 获取视频信息

        基于成功案例分析，使用与rathodpratham-dev/douyin_video_downloader类似的方法
        """
        try:
            # ========== 方法: 使用公开API服务 ==========
            # 根据测试，某些公开API服务仍然可用
            # 尝试多个API端点

            # API 1: 使用抖音内部API（通过特定User-Agent）
            api_urls = [
                f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}",
                f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}",
                f"https://www.iesdouyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}",
            ]

            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.2.3 Mobile/15E148 Safari/604.1',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-cn',
                'X-Requested-With': 'XMLHttpRequest',
            }

            for api_url in api_urls:
                try:
                    response = requests.get(api_url, headers=headers, timeout=15)

                    # 检查是否是有效的JSON响应
                    if response.text.startswith('<!DOCTYPE') or response.text.startswith('<html'):
                        continue

                    data = response.json()

                    # 检查响应状态
                    if data.get('status_code') == 0:
                        item_list = data.get('item_list', [])
                        if item_list:
                            aweme_detail = item_list[0]
                            return DouyinDownloader._parse_aweme_detail(aweme_detail, video_id)

                        aweme_detail = data.get('aweme_detail')
                        if aweme_detail:
                            return DouyinDownloader._parse_aweme_detail(aweme_detail, video_id)

                except Exception as e:
                    print(f"[DOUYIN] API {api_url[:50]}... failed: {str(e)[:50]}", file=sys.stderr)
                    continue

            # 如果所有API都失败，尝试从网页提取
            print(f"[DOUYIN] All APIs failed, trying webpage extraction", file=sys.stderr)
            return DouyinDownloader._extract_from_webpage(video_id)

        except Exception as e:
            print(f"[DOUYIN] Exception: {e}", file=sys.stderr)
            return DouyinDownloader._get_video_info_v3(video_id)

    @staticmethod
    def _extract_from_webpage(video_id: str) -> Dict:
        """从网页提取视频信息"""
        try:
            url = f"https://www.douyin.com/video/{video_id}"

            response = requests.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                },
                timeout=15
            )

            html = response.text

            # 尝试多种提取方式
            patterns = [
                r'<script id="RENDER_DATA" type="application/json">(.*?)</script>',
                r'window\._ssrData\s*=\s*({.*?});',
                r'<script>self\.__pace_f\.push\((\{.*?"awemeDetail".*?\})\)',
            ]

            for pattern in patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(1)

                        # 清理转义字符
                        replacements = [
                            ('\\u002F', '/'),
                            ('\\u003C', '<'),
                            ('\\u003E', '>'),
                            ('\\"', '"'),
                            ('\\\\', '\\'),
                        ]
                        for old, new in replacements:
                            json_str = json_str.replace(old, new)

                        # 如果是完整的代码块，提取JSON部分
                        if 'self.__pace_f' in match.group(0):
                            # 提取花括号内的内容
                            brace_start = json_str.find('{')
                            if brace_start > 0:
                                json_str = json_str[brace_start:]
                                # 找匹配的结束花括号
                                brace_count = 0
                                end_pos = 0
                                for i, char in enumerate(json_str):
                                    if char == '{':
                                        brace_count += 1
                                    elif char == '}':
                                        brace_count -= 1
                                        if brace_count == 0:
                                            end_pos = i + 1
                                            break
                                json_str = json_str[:end_pos]

                        data = json.loads(json_str)

                        # 从不同的数据结构中提取aweme_detail
                        aweme_detail = None

                        # RENDER_DATA 结构
                        if 'app' in data:
                            aweme_detail = data['app'].get('videoDetail', {}).get('awemeDetail')
                        # _ssrData 结构
                        elif 'awemeDetail' in data:
                            aweme_detail = data['awemeDetail']

                        if aweme_detail:
                            return DouyinDownloader._parse_aweme_detail(aweme_detail, video_id)

                    except Exception as e:
                        print(f"[DOUYIN] Pattern {pattern[:20]}... failed: {e}", file=sys.stderr)
                        continue

            return {'success': False, 'error': '无法从网页提取视频信息'}

        except Exception as e:
            print(f"[DOUYIN] Webpage extraction error: {e}", file=sys.stderr)
            return {'success': False, 'error': f'网页提取失败: {str(e)[:100]}'}

    @staticmethod
    def _parse_aweme_detail(aweme_detail: dict, video_id: str) -> Dict:
        """解析 aweme_detail 数据"""
        try:
            video_info = aweme_detail.get('video', {})

            play_addr = video_info.get('play_addr', {})
            url_list = play_addr.get('url_list', [])

            if not url_list:
                return {'success': False, 'error': '未找到播放地址'}

            video_url = url_list[0]
            clean_url = DouyinDownloader._remove_watermark(video_url)

            return {
                'success': True,
                'video_id': video_id,
                'title': aweme_detail.get('desc', '抖音视频'),
                'author': aweme_detail.get('author', {}).get('nickname', ''),
                'author_avatar': aweme_detail.get('author', {}).get('avatar_thumb', {}).get('url_list', [''])[0],
                'cover': video_info.get('cover', {}).get('url_list', [''])[0],
                'dynamic_cover': video_info.get('dynamic_cover', {}).get('url_list', [''])[0],
                'video_url': clean_url,
                'music_url': aweme_detail.get('music', {}).get('play_url', {}).get('url_list', [''])[0],
                'duration': video_info.get('duration', 0) / 1000 if video_info.get('duration') else 0,
                'width': video_info.get('width', 0),
                'height': video_info.get('height', 0),
                'statistics': {
                    'digg_count': aweme_detail.get('statistics', {}).get('digg_count', 0),
                    'comment_count': aweme_detail.get('statistics', {}).get('comment_count', 0),
                    'share_count': aweme_detail.get('statistics', {}).get('share_count', 0),
                    'play_count': aweme_detail.get('statistics', {}).get('play_count', 0),
                }
            }
        except Exception as e:
            print(f"[DOUYIN] Parse aweme_detail error: {e}", file=sys.stderr)
            return {'success': False, 'error': f'解析失败: {str(e)}'}

    @staticmethod
    def _get_video_info_v2(video_id: str) -> Dict:
        """
        备用方案：使用其他 API 端点
        """
        try:
            # 尝试使用不同的 API 端点
            api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/"
            params = {'aweme_id': video_id}

            response = requests.get(
                api_url,
                params=params,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Referer': 'https://www.douyin.com/',
                },
                timeout=15
            )

            # 检查是否返回 HTML
            if response.text.startswith('<!DOCTYPE'):
                return DouyinDownloader._get_video_info_v3(video_id)

            data = response.json()

            if data.get('status_code') != 0:
                return DouyinDownloader._get_video_info_v3(video_id)

            aweme_detail = data.get('aweme_detail', {})
            if not aweme_detail:
                return DouyinDownloader._get_video_info_v3(video_id)

            return DouyinDownloader._parse_aweme_detail(aweme_detail, video_id)

        except Exception as e:
            print(f"[DOUYIN] v2 error: {e}", file=sys.stderr)
            return DouyinDownloader._get_video_info_v3(video_id)

    @staticmethod
    def _get_video_info_v3(video_id: str) -> Dict:
        """
        备用方案：使用其他 API 端点
        """
        try:
            # 尝试使用 aweme detail API
            api_url = f"{DouyinDownloader.API_BASE}/aweme/v1/aweme/detail/"
            params = {'aweme_id': video_id}

            response = requests.get(
                api_url,
                params=params,
                headers=DouyinDownloader.HEADERS,
                timeout=15
            )

            data = response.json()

            if data.get('status_code') != 0:
                return DouyinDownloader._get_video_info_v3(video_id)

            aweme_detail = data.get('aweme_detail', {})
            if not aweme_detail:
                return DouyinDownloader._get_video_info_v3(video_id)

            return DouyinDownloader._parse_aweme_detail(aweme_detail, video_id)

        except Exception as e:
            print(f"[DOUYIN] Fallback error: {e}", file=sys.stderr)
            return DouyinDownloader._get_video_info_v3(video_id)

    @staticmethod
    def _get_video_info_v3(video_id: str) -> Dict:
        """
        最后的备用方案：使用 yt-dlp（最可靠）
        yt-dlp 持续维护，能处理最新的抖音变化
        """
        try:
            video_url = f"https://www.douyin.com/video/{video_id}"

            # 使用 yt-dlp 获取信息
            import yt_dlp

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'cookiefile': None,  # 不使用 cookies 文件
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(video_url, download=False)

                    if not info:
                        return {'success': False, 'error': 'yt-dlp 无法获取视频信息'}

                    # 提取播放地址
                    formats = info.get('formats', [])
                    video_url = None

                    # 优先选择无水印格式
                    for fmt in formats:
                        if fmt.get('ext') == 'mp4' and 'height' in fmt:
                            video_url = fmt.get('url')
                            break

                    if not video_url and formats:
                        video_url = formats[0].get('url')

                    if not video_url:
                        return {'success': False, 'error': '未找到播放地址'}

                    return {
                        'success': True,
                        'video_id': video_id,
                        'title': info.get('title', info.get('description', '抖音视频')),
                        'author': info.get('uploader', info.get('channel', '')),
                        'cover': info.get('thumbnail', ''),
                        'video_url': video_url,
                        'duration': info.get('duration', 0),
                        'width': info.get('width', 0),
                        'height': info.get('height', 0),
                    }

                except Exception as e:
                    error_str = str(e)
                    if 'cookies' in error_str.lower() or 'login' in error_str.lower():
                        return {'success': False, 'error': '该视频需要登录才能下载'}
                    return {'success': False, 'error': f'yt-dlp 失败: {error_str[:100]}'}

        except ImportError:
            return {'success': False, 'error': 'yt-dlp 未安装'}
        except Exception as e:
            print(f"[DOUYIN] v3 error: {e}", file=sys.stderr)
            return {'success': False, 'error': f'所有方法均失败: {str(e)[:100]}'}

    @staticmethod
    def _remove_watermark(url: str) -> str:
        """
        移除水印：将 playwm 替换为 play

        Args:
            url: 原始播放地址

        Returns:
            无水印播放地址
        """
        # 方法1: 直接替换 playwm 为 play
        if 'playwm' in url:
            url = url.replace('/playwm/', '/play/')

        # 方法2: 移除水印参数
        # 有些地址通过参数控制水印，如 ?watermark=1
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)

        # 移除水印相关参数
        watermark_params = ['watermark', 'wm', 'line']
        for param in watermark_params:
            if param in query_params:
                del query_params[param]

        # 重建 URL
        clean_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urllib.parse.urlencode(query_params, doseq=True),
            ''
        ))

        return clean_url

    @staticmethod
    def parse(url: str) -> Dict:
        """
        解析抖音视频链接（入口函数）

        Args:
            url: 抖音视频链接

        Returns:
            解析结果
        """
        try:
            # 提取 video_id
            video_id = DouyinDownloader.extract_video_id(url)

            if not video_id:
                return {
                    'success': False,
                    'error': '无法识别视频链接，请确认链接是否正确'
                }

            print(f"[DOUYIN] Extracted video_id: {video_id}", file=sys.stderr)

            # 获取视频信息
            video_info = DouyinDownloader.get_video_info(video_id)

            if video_info.get('success'):
                print(f"[DOUYIN] Parse success: {video_info.get('title', '')[:50]}", file=sys.stderr)
            else:
                print(f"[DOUYIN] Parse failed: {video_info.get('error')}", file=sys.stderr)

            return video_info

        except Exception as e:
            return {
                'success': False,
                'error': f'解析失败: {str(e)}'
            }

    @staticmethod
    def download(url: str, output_path: str) -> Dict:
        """
        下载抖音视频

        Args:
            url: 抖音视频链接
            output_path: 输出文件路径

        Returns:
            下载结果
        """
        try:
            # 解析视频信息
            result = DouyinDownloader.parse(url)

            if not result.get('success'):
                return result

            video_url = result.get('video_url')

            if not video_url:
                return {'success': False, 'error': '未找到视频地址'}

            # 下载视频
            print(f"[DOUYIN] Starting download from: {video_url[:80]}...", file=sys.stderr)

            response = requests.get(
                video_url,
                headers={
                    'User-Agent': DouyinDownloader.HEADERS['User-Agent'],
                    'Referer': 'https://www.douyin.com/',
                },
                stream=True,
                timeout=30
            )

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

            print(f"[DOUYIN] Download completed: {downloaded} bytes", file=sys.stderr)

            return {
                'success': True,
                'file_size': downloaded,
                'title': result.get('title'),
                'author': result.get('author'),
            }

        except Exception as e:
            print(f"[DOUYIN] Download error: {e}", file=sys.stderr)
            return {'success': False, 'error': f'下载失败: {str(e)}'}


# 导出函数，方便其他模块调用
def parse_douyin(url: str) -> Dict:
    """解析抖音视频"""
    return DouyinDownloader.parse(url)


def download_douyin(url: str, output_path: str) -> Dict:
    """下载抖音视频"""
    return DouyinDownloader.download(url, output_path)


# 测试代码
if __name__ == '__main__':
    import sys

    test_url = 'https://v.douyin.com/YkEbp3tMCrk/'
    print(f"Testing: {test_url}\n")

    result = DouyinDownloader.parse(test_url)

    if result.get('success'):
        print(f"Title: {result.get('title')}")
        print(f"Author: {result.get('author')}")
        print(f"Duration: {result.get('duration')}s")
        print(f"Video URL: {result.get('video_url')[:100]}...")
        print(f"Cover: {result.get('cover')[:100]}...")
        print(f"\nStatistics:")
        stats = result.get('statistics', {})
        print(f"  Likes: {stats.get('digg_count')}")
        print(f"  Comments: {stats.get('comment_count')}")
        print(f"  Shares: {stats.get('share_count')}")
        print(f"  Plays: {stats.get('play_count')}")
    else:
        print(f"Error: {result.get('error')}")
        sys.exit(1)
