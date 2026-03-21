"""
平台公开 API 模块
使用第三方公开 API 获取视频，无需用户配置 cookies
"""
import requests
import re
import json
import sys
from typing import Dict, Optional


class PlatformAPI:
    """平台公开 API 调用"""

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """从 URL 中提取视频 ID"""
        # 抖音短链接
        if 'v.douyin.com' in url:
            try:
                response = requests.head(url, allow_redirects=False, timeout=10)
                location = response.headers.get('Location', '')
                # 从重定向 URL 中提取视频 ID
                match = re.search(r'/video/(\d+)', location)
                if match:
                    return match.group(1)
            except:
                pass

        # 抖音完整链接
        if '/video/' in url:
            match = re.search(r'/video/(\d+)', url)
            if match:
                return match.group(1)

        # 小红书
        if 'xiaohongshu.com' in url:
            match = re.search(r'/explore/([a-f0-9]+)', url)
            if match:
                return match.group(1)

        return None

    @staticmethod
    def get_douyin_video(url: str) -> Dict:
        """
        使用公开 API 获取抖音视频
        尝试多个 API 服务
        """
        # API 列表（按优先级排序）
        apis = [
            {
                'name': 'OuoB',
                'url': lambda u: f"https://api.ooubot.com/api/douyin?url={u}",
                'parse': lambda d: {
                    'success': d.get('code') == 200,
                    'title': d.get('data', {}).get('title', '抖音视频'),
                    'cover': d.get('data', {}).get('cover', ''),
                    'author': d.get('data', {}).get('author', {}).get('nickname', ''),
                    'url': d.get('data', {}).get('play_addr', {}).get('url_list', [''])[0],
                    'wm_url': d.get('data', {}).get('play_addr', {}).get('url_list', [''])[0],
                }
            },
            {
                'name': 'TikWM',
                'url': lambda u: f"https://www.tikwm.com/api/?url={u}",
                'parse': lambda d: {
                    'success': d.get('code') == 0 and 'data' in d,
                    'title': d.get('data', {}).get('title', '抖音视频'),
                    'cover': d.get('data', {}).get('cover', ''),
                    'author': d.get('data', {}).get('author', {}).get('nickname', ''),
                    'url': d.get('data', {}).get('play', ''),
                    'wm_url': d.get('data', {}).get('wmplay', ''),
                }
            },
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        for api in apis:
            try:
                api_url = api['url'](url)
                response = requests.get(api_url, headers=headers, timeout=15)

                # 检查是否是 HTML（被 Cloudflare 拦截）
                if response.text.startswith('<!DOCTYPE'):
                    print(f"[API] {api['name']} blocked by Cloudflare", file=sys.stderr)
                    continue

                data = response.json()
                result = api['parse'](data)
                result['api_used'] = api['name']

                if result.get('success'):
                    return result

            except Exception as e:
                print(f"[API] {api['name']} failed: {str(e)}", file=sys.stderr)
                continue

        return {'success': False, 'error': '所有 API 均无法获取视频信息'}

    @staticmethod
    def get_xiaohongshu_video(url: str) -> Dict:
        """
        使用公开 API 获取小红书视频
        """
        try:
            # 使用小红书公开 API
            api_url = "https://api.xiaohongshu.com/api/sns/web/v1/feed/aweme/v1/aweme/detail/"

            # 提取视频 ID
            video_id = PlatformAPI.extract_video_id(url)
            if not video_id:
                return {'success': False, 'error': '无法识别视频链接'}

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.xiaohongshu.com/'
            }

            # 尝试使用第三方解析 API
            # 这里使用一个通用的视频解析服务
            parse_url = f"https://api.pearktrue.com/api/v1/xhs/video?url={url}"

            response = requests.get(parse_url, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    video_data = data.get('data', {})
                    return {
                        'success': True,
                        'title': video_data.get('title', '小红书视频'),
                        'cover': video_data.get('cover', ''),
                        'url': video_data.get('url', ''),
                    }

            return {'success': False, 'error': '无法获取视频信息'}

        except Exception as e:
            return {'success': False, 'error': f'API 调用失败: {str(e)}'}

    @staticmethod
    def get_video_info(platform: str, url: str) -> Dict:
        """获取视频信息的统一入口"""
        if platform == 'douyin':
            return PlatformAPI.get_douyin_video(url)
        elif platform == 'xiaohongshu':
            return PlatformAPI.get_xiaohongshu_video(url)
        else:
            return {'success': False, 'error': '不支持的平台'}


# 测试代码
if __name__ == '__main__':
    import sys
    # 测试抖音
    test_url = 'https://v.douyin.com/YkEbp3tMCrk/'
    print(f"Testing: {test_url}")
    result = PlatformAPI.get_douyin_video(test_url)
    if result.get('success'):
        print(f"✓ Success with API: {result.get('api_used')}")
        print(f"  Title: {result.get('title')[:50]}")
        print(f"  Author: {result.get('author')}")
        print(f"  URL: {result.get('url')[:80]}")
    else:
        print(f"✗ Failed: {result.get('error')}")
