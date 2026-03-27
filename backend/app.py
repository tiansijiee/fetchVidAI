"""
万能视频下载 API 服务
使用 Flask + yt-dlp 实现视频解析

方案1: 无需ffmpeg的下载方案 - 优先使用单格式下载
"""
from flask import Flask, request, jsonify, send_from_directory, Response, send_file
from flask_cors import CORS
import os
import requests
from video_parser import VideoParser
import sys
import tempfile
import yt_dlp
import uuid
import threading
import time

# AI功能模块（新增）
try:
    from ai_routes import ai_bp, init_ai_routes
    AI_ENABLED = True
except ImportError as e:
    print(f"[APP] AI模块导入失败: {e}", file=sys.stderr)
    AI_ENABLED = False

# 认证模块（新增）
AUTH_ENABLED = False
try:
    from auth.auth import create_auth_routes
    AUTH_ENABLED = True
except ImportError as e:
    print(f"[APP] 认证模块导入失败: {e}", file=sys.stderr)

# 支付模块（新增，可选）
PAYMENT_ENABLED = False
try:
    from payment.stripe_handler import create_payment_routes
    PAYMENT_ENABLED = True
except ImportError as e:
    print(f"[APP] 支付模块导入失败（需要 stripe）: {e}", file=sys.stderr)

# 创建 Flask 应用
app = Flask(__name__, static_folder='../frontend/dist')

# 全局配置
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# 启用 CORS - 支持所有开发端口
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# 全局下载任务存储
download_tasks = {}


def check_ffmpeg_available():
    """检查ffmpeg是否可用"""
    import shutil
    import platform

    # 首先尝试使用 shutil.which 查找
    if shutil.which('ffmpeg') is not None:
        return True

    # Windows 系统检查常见安装路径
    if platform.system() == 'Windows':
        common_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            os.path.expanduser(r'~\AppData\Local\Programs\ffmpeg\bin\ffmpeg.exe'),
        ]
        for path in common_paths:
            if os.path.exists(path):
                print(f"[FFMPEG] Found at: {path}", file=sys.stderr)
                return True

    print(f"[FFMPEG] Not found in PATH or common paths", file=sys.stderr)
    return False


def get_download_dir():
    """确保下载目录存在"""
    download_dir = os.path.join(tempfile.gettempdir(), 'video_downloads')
    os.makedirs(download_dir, exist_ok=True)
    return download_dir


def get_cookies_dir():
    """确保cookies目录存在"""
    cookies_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies')
    os.makedirs(cookies_dir, exist_ok=True)
    return cookies_dir


@app.route('/')
def index():
    """前端页面入口"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '万能视频下载服务运行中',
        'supported_platforms': ['B站', '微博', '知乎', 'YouTube', 'Twitter', 'TikTok', 'Instagram', 'Vimeo'],
        'ffmpeg_available': os.path.exists('/usr/bin/ffmpeg') or os.path.exists('C:\\ffmpeg\\bin\\ffmpeg.exe')
    })


@app.route('/api/parse', methods=['POST', 'OPTIONS'])
def parse_video():
    """视频解析接口"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        url = data.get('url', '').strip()
        if not url:
            return jsonify({'success': False, 'message': '请输入视频链接'}), 400

        # 权限检查（可选：解析不算入次数限制）
        # 解析本身不消耗次数，只在下载时统计

        # 快速解析：使用 extract_flat 获取基本信息
        fast_parse = data.get('fast', False)

        if fast_parse:
            # 快速模式：只获取基本信息，不获取详细格式
            return _fast_parse_video(url)

        # 完整解析：获取所有格式信息
        return _full_parse_video(url)

    except Exception as e:
        print(f"[ERROR] Parse error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({'success': False, 'message': f'解析失败: {str(e)}'}), 500


def _fast_parse_video(url: str):
    """快速解析视频（只获取基本信息）"""
    try:
        import yt_dlp

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # 不下载详细格式信息
            'socket_timeout': 10,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return jsonify({
                'success': True,
                'data': {
                    'platform': VideoParser.identify_platform(url),
                    'title': info.get('title', '未知标题'),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', info.get('channel', '')),
                    'duration_seconds': info.get('duration', 0),
                    'view_count': info.get('view_count'),
                    'webpage_url': info.get('webpage_url', url),
                    'fast_mode': True  # 标记为快速模式
                }
            }), 200

    except Exception as e:
        print(f"[FAST-PARSE] Error: {e}", file=sys.stderr)
        # 如果快速解析失败，降级到完整解析
        return _full_parse_video(url)


def _full_parse_video(url: str):
    """完整解析视频（获取所有格式信息）"""
    # 抖音使用专用解析器
    platform = VideoParser.identify_platform(url)

    if platform == 'douyin':
        print(f"[PARSE] Using Douyin专用解析器 for: {url[:50]}", file=sys.stderr)
        try:
            from douyin_downloader import DouyinDownloader
            douyin_result = DouyinDownloader.parse(url)

            if douyin_result.get('success'):
                # 转换为统一格式
                return jsonify({
                    'success': True,
                    'data': {
                        'platform': 'douyin',
                        'title': douyin_result.get('title'),
                        'thumbnail': douyin_result.get('cover'),
                        'duration': DouyinDownloader.format_duration(douyin_result.get('duration', 0)),
                        'duration_seconds': douyin_result.get('duration', 0),
                        'uploader': douyin_result.get('author'),
                        'description': f"作者: {douyin_result.get('author', '')}\n点赞: {douyin_result.get('statistics', {}).get('digg_count', 0)}",
                        'formats': [{
                            'ext': 'mp4',
                            'format_id': 'douyin_mp4',
                            'quality': '原画',
                            'height': douyin_result.get('height'),
                            'width': douyin_result.get('width'),
                            'url': douyin_result.get('video_url'),
                            'http_headers': {
                                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
                                'Referer': 'https://www.douyin.com/'
                            }
                        }]
                    }
                }), 200
            else:
                return jsonify({'success': False, 'message': douyin_result.get('error', '抖音视频解析失败')}), 400

        except Exception as e:
            print(f"[PARSE] Douyin解析失败: {e}, 降级到yt-dlp", file=sys.stderr)
            # 降级到 yt-dlp
            pass

    # 其他平台使用 yt-dlp
    result = VideoParser.parse(url)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """获取支持的平台列表"""
    return jsonify({
        'success': True,
        'data': [
            {'id': 'bilibili', 'name': 'B站', 'domains': ['bilibili.com', 'b23.tv']},
            {'id': 'weibo', 'name': '微博', 'domains': ['weibo.com', 'weibo.cn']},
            {'id': 'zhihu', 'name': '知乎', 'domains': ['zhihu.com', 'zhuanlan.zhihu.com']},
            {'id': 'youtube', 'name': 'YouTube', 'domains': ['youtube.com', 'youtu.be']},
            {'id': 'twitter', 'name': 'Twitter', 'domains': ['twitter.com', 'x.com']},
            {'id': 'tiktok', 'name': 'TikTok', 'domains': ['tiktok.com']},
            {'id': 'instagram', 'name': 'Instagram', 'domains': ['instagram.com']},
            {'id': 'vimeo', 'name': 'Vimeo', 'domains': ['vimeo.com']}
        ]
    })


@app.route('/api/cache/clear', methods=['POST'])
def clear_parse_cache():
    """清空解析缓存"""
    try:
        from video_parser import VideoParser
        VideoParser.clear_cache()
        return jsonify({'success': True, 'message': '缓存已清空'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'清空缓存失败: {str(e)}'}), 500


@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """获取缓存统计信息"""
    try:
        from video_parser import VideoParser
        cache_size = len(VideoParser._cache)
        return jsonify({
            'success': True,
            'data': {
                'cache_size': cache_size,
                'cache_ttl': VideoParser._cache_ttl,
                'cache_enabled': True
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取缓存信息失败: {str(e)}'}), 500


@app.route('/api/proxy/thumbnail', methods=['GET'])
def proxy_thumbnail():
    """缩略图代理接口"""
    thumbnail_url = request.args.get('url')
    if not thumbnail_url:
        return '', 400

    try:
        resp = requests.get(thumbnail_url, timeout=10, stream=True)
        return Response(resp.content, content_type=resp.headers.get('Content-Type', 'image/jpeg'))
    except Exception as e:
        print(f"[ERROR] Thumbnail error: {e}", file=sys.stderr)
        return '', 404


@app.route('/api/proxy/download', methods=['POST', 'OPTIONS'])
def proxy_download():
    """
    下载代理接口 - 异步任务模式
    方案1: 优先使用单格式下载，避免需要ffmpeg合并
    """
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        video_url = data.get('video_url', '').strip()
        filename = data.get('filename', 'video.mp4')
        format_id = data.get('format_id')

        if not video_url:
            return jsonify({'success': False, 'message': '缺少视频链接'}), 400

        # 权限检查
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = auth.auth.AuthManager.decode_token(token)
            if payload:
                user_id = payload.get('user_id')

        # 检查下载次数限制
        if user_id:
            allowed, message, info = auth.auth.check_rate_limit(user_id, 'download')
            if not allowed:
                return jsonify({
                    'success': False,
                    'message': message,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'info': info
                }), 403
        else:
            # 游客模式 - 使用 session 或 IP 限制
            # 这里简化处理，允许游客使用
            pass

        # 清理文件名
        def is_safe_char(c):
            if c.isalnum():
                return True
            if c in (' ', '-', '_', '.'):
                return True
            try:
                return '\u4e00' <= c <= '\u9fff'
            except:
                return False

        safe_filename = ''.join(c for c in filename if is_safe_char(c))
        if not safe_filename or safe_filename == '.' * len(safe_filename):
            safe_filename = 'video'
        if not safe_filename.endswith('.mp4'):
            safe_filename += '.mp4'

        # 创建下载任务
        task_id = str(uuid.uuid4())
        download_dir = get_download_dir()
        output_path = os.path.join(download_dir, f'{task_id}.mp4')

        download_tasks[task_id] = {
            'status': 'pending',
            'filename': safe_filename,
            'progress': 0,
            'error': None,
            'output_path': output_path,
            'created_at': time.time(),
            'user_id': user_id,  # 记录用户ID
            'video_url': video_url
        }

        print(f"[DOWNLOAD-{task_id[:8]}] Task created for: {video_url[:50]}", file=sys.stderr)

        # 启动后台下载任务
        def download_task():
            try:
                download_tasks[task_id]['status'] = 'downloading'

                platform = VideoParser.identify_platform(video_url)

                # ========== 抖音专用处理：使用专用下载器 ==========
                if platform == 'douyin':
                    print(f"[DOWNLOAD-{task_id[:8]}] Using Douyin专用下载器", file=sys.stderr)
                    try:
                        from douyin_downloader import DouyinDownloader

                        # 使用抖音专用下载器
                        douyin_result = DouyinDownloader.download(video_url, output_path)

                        if douyin_result.get('success'):
                            file_size = os.path.getsize(output_path)
                            download_tasks[task_id]['status'] = 'completed'
                            download_tasks[task_id]['file_size'] = file_size
                            download_tasks[task_id]['progress'] = 100
                            print(f"[DOWNLOAD-{task_id[:8]}] ✓ Douyin下载完成: {file_size} bytes", file=sys.stderr)
                            return  # 成功，直接返回

                        # 专用下载器失败，记录错误但继续用 yt-dlp
                        print(f"[DOWNLOAD-{task_id[:8]}] DouyinDownloader失败: {douyin_result.get('error')}, 降级到yt-dlp", file=sys.stderr)
                        # 继续到下面的 yt-dlp 流程

                    except ImportError:
                        print(f"[DOWNLOAD-{task_id[:8]}] DouyinDownloader未导入，使用yt-dlp", file=sys.stderr)
                    except Exception as e:
                        print(f"[DOWNLOAD-{task_id[:8]}] DouyinDownloader异常: {e}, 降级到yt-dlp", file=sys.stderr)

                # 检查ffmpeg是否可用
                has_ffmpeg = check_ffmpeg_available()
                print(f"[DOWNLOAD-{task_id[:8]}] FFmpeg available: {has_ffmpeg}", file=sys.stderr)

                # ========== 核心修复：平台特定的格式选择器 ==========
                # 基础配置 - 添加通用请求头，避免 HTTP 400 错误
                # 使用目录路径而不是完整文件路径，让 yt-dlp 自动命名
                ydl_opts = {
                    'outtmpl': os.path.join(download_dir, f'{task_id}.%(ext)s'),  # 使用模板，让yt-dlp决定扩展名
                    'quiet': False,  # 改为 False，以便查看详细日志
                    'no_warnings': False,  # 显示警告信息
                    'nocheckcertificate': True,  # 跳过证书验证
                    'socket_timeout': 30,  # 统一超时设置
                    # 确保输出为 mp4 格式
                    'merge_output_format': 'mp4',
                }

                # 只有在需要格式转换时才使用后处理器
                # if has_ffmpeg:
                #     ydl_opts['postprocessors'] = [{
                #         'key': 'FFmpegVideoConvertor',
                #         'preferedformat': 'mp4',
                #     }]

                # 如果有ffmpeg，设置ffmpeg路径（Windows需要）
                if has_ffmpeg:
                    import platform as plt
                    if plt.system() == 'Windows':
                        # 尝试常见路径
                        ffmpeg_paths = [
                            r'C:\ffmpeg\bin\ffmpeg.exe',
                            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                        ]
                        for path in ffmpeg_paths:
                            if os.path.exists(path):
                                ydl_opts['ffmpeg_location'] = path
                                print(f"[DOWNLOAD-{task_id[:8]}] Using ffmpeg at: {path}", file=sys.stderr)
                                break

                # 平台特定配置
                if platform == 'bilibili':
                    # B站使用DASH格式，音视频分离
                    # 添加B站专用的重试和超时配置
                    ydl_opts.update({
                        'retries': 10,  # 重试次数
                        'file_access_retries': 10,
                        'fragment_retries': 10,  # 分片重试次数
                        'skip_unavailable_fragments': False,  # 不跳过失败片段
                        'ignoreerrors': False,  # 遇到错误停止，这样可以知道真正的问题
                        'nocheckcertificate': True,  # 跳过证书检查
                        # B站专用请求头（避免HTTP 400错误）
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
                            'Origin': 'https://www.bilibili.com',
                        },
                        # DASH配置
                        'extractor_args': {
                            'bilibili': {
                                'prefer_formats': 'dash-flv,_dash-mp4,aac-flv,mp4-flv'
                            }
                        },
                        # 添加额外的网络配置
                        'socket_timeout': 60,  # 增加超时时间到60秒
                        'concurrent_fragment_downloads': 4,  # 增加并发下载数
                    })

                    # 根据用户选择的格式ID设置下载格式
                    if format_id and format_id != 'best':
                        # 用户指定了特定格式 - 不覆盖 http_headers
                        if has_ffmpeg:
                            # 有ffmpeg时，可以合并音视频
                            ydl_opts.update({
                                'format': f'{format_id}+bestaudio/best',
                                'merge_output_format': 'mp4',
                            })
                            print(f"[DOWNLOAD-{task_id[:8]}] Using format_id: {format_id} + audio merge", file=sys.stderr)
                        else:
                            # 无ffmpeg时，只下载视频流
                            ydl_opts.update({
                                'format': format_id,
                                'merge_output_format': None,
                            })
                            print(f"[DOWNLOAD-{task_id[:8]}] Using format_id: {format_id} (no audio merge)", file=sys.stderr)
                    elif format_id == 'best' or not format_id:
                        # 最佳质量或默认 - 不覆盖 http_headers
                        if has_ffmpeg:
                            # 有ffmpeg时，下载最高质量并合并音视频
                            ydl_opts.update({
                                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/bestvideo+bestaudio/best',
                                'merge_output_format': 'mp4',
                            })
                            print(f"[DOWNLOAD-{task_id[:8]}] Using best format with audio merge", file=sys.stderr)
                        else:
                            # 无ffmpeg时，使用单格式
                            ydl_opts.update({
                                'format': 'bestvideo[ext=mp4][height<=1080]/bestvideo[ext=mp4]/best[height<=1080]/best',
                                'merge_output_format': None,
                                'postprocessors': [],
                            })
                            print(f"[DOWNLOAD-{task_id[:8]}] Using best format (no ffmpeg)", file=sys.stderr)
                    else:
                        # 默认格式
                        ydl_opts.update({
                            'format': 'bestvideo[ext=mp4][height<=720]/bestvideo[ext=mp4]/best[height<=720]/best',
                            'merge_output_format': None,
                            'postprocessors': [],
                        })
                elif platform == 'xiaohongshu':
                    # 小红书需要cookies支持
                    cookies_dir = get_cookies_dir()
                    cookie_file = os.path.join(cookies_dir, 'xiaohongshu_cookies.txt')

                    if os.path.exists(cookie_file):
                        # 使用手动配置的cookies文件
                        ydl_opts.update({
                            'format': 'best[protocol=http]/best[ext=mp4]/best',
                            'merge_output_format': None,
                            'cookiefile': cookie_file,
                            'http_headers': {
                                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                                'Referer': 'https://www.xiaohongshu.com/'
                            }
                        })
                        print(f"[DOWNLOAD-{task_id[:8]}] Using cookie file for Xiaohongshu", file=sys.stderr)
                    else:
                        # 自动从浏览器读取cookies
                        ydl_opts.update({
                            'format': 'best[protocol=http]/best[ext=mp4]/best',
                            'merge_output_format': None,
                            'cookiesfrombrowser': ('chrome', 'edge', 'firefox'),
                            'http_headers': {
                                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                                'Referer': 'https://www.xiaohongshu.com/'
                            }
                        })
                        print(f"[DOWNLOAD-{task_id[:8]}] Using browser cookies for Xiaohongshu", file=sys.stderr)
                else:
                    # YouTube 和其他平台 - 添加通用请求头
                    base_headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.9',
                    }

                    # 根据平台设置特定的 Referer
                    if platform == 'youtube':
                        base_headers['Referer'] = 'https://www.youtube.com/'
                    elif platform == 'weibo':
                        base_headers['Referer'] = 'https://weibo.com/'
                    elif platform == 'zhihu':
                        base_headers['Referer'] = 'https://www.zhihu.com/'
                    else:
                        # 使用视频页面作为 referer
                        base_headers['Referer'] = video_url if video_url.startswith('http') else 'https://www.google.com'

                    ydl_opts['http_headers'] = base_headers

                    if has_ffmpeg:
                        ydl_opts.update({
                            'format': 'bestvideo+bestaudio/best',
                            'merge_output_format': 'mp4',
                        })
                    else:
                        ydl_opts.update({
                            'format': 'best',
                            'merge_output_format': None,
                        })

                # 进度钩子
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        downloaded = d.get('downloaded_bytes', 0)
                        total = d.get('total_bytes') or d.get('filesize') or 1
                        progress = int(downloaded / total * 100) if total > 0 else 0

                        # 对于DASH下载，使用更平滑的进度显示
                        # 如果进度突然下降（新段开始），保持之前的进度
                        current_progress = download_tasks[task_id].get('progress', 0)
                        if progress < current_progress and progress < 90:
                            # 进度倒退，可能是新段开始，保持当前进度
                            progress = current_progress

                        # 限制最高进度为95%，为后处理预留空间
                        display_progress = min(progress, 95)

                        # 只在进度增加时更新，避免跳变
                        if display_progress > current_progress:
                            download_tasks[task_id]['progress'] = display_progress

                        if progress % 20 == 0 or progress == 100:  # 每20%打印一次
                            print(f"[DOWNLOAD-{task_id[:8]}] Progress: {progress}% ({downloaded}/{total})", file=sys.stderr)
                    elif d['status'] == 'finished':
                        # 下载完成，开始后处理
                        download_tasks[task_id]['progress'] = 95  # 后处理时保持95%
                        print(f"[DOWNLOAD-{task_id[:8]}] Download finished, processing...", file=sys.stderr)

                ydl_opts['progress_hooks'] = [progress_hook]

                print(f"[DOWNLOAD-{task_id[:8]}] Starting download for platform: {platform}", file=sys.stderr)
                print(f"[DOWNLOAD-{task_id[:8]}] Output path: {output_path}", file=sys.stderr)
                print(f"[DOWNLOAD-{task_id[:8]}] Download directory exists: {os.path.exists(os.path.dirname(output_path))}", file=sys.stderr)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                # 检查文件
                print(f"[DOWNLOAD-{task_id[:8]}] Download finished, checking file...", file=sys.stderr)

                # 检查可能的文件路径（因为 yt-dlp 可能使用不同的扩展名）
                # 使用外部定义的 download_dir，而不是重新定义
                base_name = task_id  # 使用 task_id 作为基础名称

                # 列出目录中所有以 task_id 开头的文件
                if os.path.exists(download_dir):
                    all_files = os.listdir(download_dir)
                    matching_files = [f for f in all_files if f.startswith(base_name)]
                    print(f"[DOWNLOAD-{task_id[:8]}] Matching files: {matching_files}", file=sys.stderr)

                    if matching_files:
                        # 使用第一个匹配的文件
                        actual_file = os.path.join(download_dir, matching_files[0])
                        file_size = os.path.getsize(actual_file)
                        print(f"[DOWNLOAD-{task_id[:8]}] Found file: {actual_file}, size: {file_size} bytes", file=sys.stderr)

                        if file_size >= 1000:  # 至少1KB
                            download_tasks[task_id]['status'] = 'completed'
                            download_tasks[task_id]['file_size'] = file_size
                            download_tasks[task_id]['progress'] = 100  # 只在真正完成时才设置为100%
                            # 更新实际文件路径
                            download_tasks[task_id]['actual_file_path'] = actual_file

                            # 增加用户下载次数
                            user_id = download_tasks[task_id].get('user_id')
                            if user_id:
                                db_manager.increment_usage(user_id, 'download')
                                print(f"[DOWNLOAD-{task_id[:8]}] ✓ Completed: {file_size} bytes (counted for user {user_id})", file=sys.stderr)
                            else:
                                print(f"[DOWNLOAD-{task_id[:8]}] ✓ Completed: {file_size} bytes (guest mode)", file=sys.stderr)
                        else:
                            download_tasks[task_id]['status'] = 'error'
                            download_tasks[task_id]['error'] = f'下载文件太小 ({file_size} bytes)'
                            print(f"[DOWNLOAD-{task_id[:8]}] ✗ File too small: {file_size} bytes", file=sys.stderr)
                    else:
                        download_tasks[task_id]['status'] = 'error'
                        download_tasks[task_id]['error'] = '文件未创建，请检查视频是否可用或稍后重试'
                        print(f"[DOWNLOAD-{task_id[:8]}] ✗ No file created. All files in directory: {all_files}", file=sys.stderr)
                else:
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = '下载目录不存在'
                    print(f"[DOWNLOAD-{task_id[:8]}] ✗ Download directory does not exist: {download_dir}", file=sys.stderr)

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                print(f"[DOWNLOAD-{task_id[:8]}] ✗ yt-dlp error: {error_msg}", file=sys.stderr)

                # 解析具体错误类型
                if 'ffmpeg' in error_msg.lower() or 'ffmpeg' in error_msg:
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = '视频需要合并组件，请安装ffmpeg或尝试其他视频'
                elif 'Requested format is not available' in error_msg or 'no suitable format' in error_msg.lower():
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = '该视频格式暂不支持下载，请尝试其他平台视频'
                elif 'HTTP Error 403' in error_msg:
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = '视频访问被拒绝，可能需要登录'
                elif 'HTTP Error 404' in error_msg:
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = '视频不存在或已被删除'
                elif 'sign in' in error_msg.lower() or 'login' in error_msg.lower():
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = '该视频需要登录才能访问'
                elif 'timed out' in error_msg.lower() or 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = '网络连接超时，请检查网络后重试'
                elif 'bilivideo' in error_msg.lower():
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = 'B站CDN连接失败，请稍后重试'
                elif 'JSONDecodeError' in error_msg or 'parse JSON' in error_msg or 'Failed to parse JSON' in error_msg:
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = 'B站API解析失败，请稍后重试或尝试其他视频'
                else:
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = f'下载失败，请稍后重试'  # 简化错误消息，避免暴露技术细节

            except Exception as e:
                error_msg = str(e)
                print(f"[DOWNLOAD-{task_id[:8]}] ✗ Exception: {error_msg}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)

                # 检查是否已经设置了错误消息（在 DownloadError 处理中）
                if download_tasks[task_id].get('status') != 'error':
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = f'下载异常: {error_msg[:150]}'

        # 启动后台下载任务
        thread = threading.Thread(target=download_task, daemon=True)
        thread.start()

        # 立即返回任务ID
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '下载任务已启动'
        })

    except Exception as e:
        print(f"[ERROR] Download start error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({'success': False, 'message': f'启动下载失败: {str(e)}'}), 500


@app.route('/api/proxy/download/status/<task_id>', methods=['GET'])
def get_download_status(task_id):
    """获取下载任务状态"""
    task = download_tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    return jsonify({
        'status': task['status'],
        'progress': task.get('progress', 0),
        'filename': task['filename'],
        'error': task.get('error'),
        'file_size': task.get('file_size')
    })


@app.route('/api/proxy/download/file/<task_id>', methods=['GET'])
def download_file(task_id):
    """下载完成的文件"""
    print(f"[DOWNLOAD-FILE] Request for task: {task_id[:8]}", file=sys.stderr)

    task = download_tasks.get(task_id)
    if not task:
        print(f"[DOWNLOAD-FILE] Task not found", file=sys.stderr)
        return jsonify({'error': '任务不存在'}), 404

    if task['status'] != 'completed':
        print(f"[DOWNLOAD-FILE] Task not completed, status: {task.get('status')}", file=sys.stderr)
        return jsonify({'error': '文件未准备好'}), 404

    # 优先使用实际文件路径，否则使用 output_path
    output_path = task.get('actual_file_path') or task.get('output_path')

    if not output_path or not os.path.exists(output_path):
        print(f"[DOWNLOAD-FILE] File not found: {output_path}", file=sys.stderr)
        print(f"[DOWNLOAD-FILE] Task data: {task}", file=sys.stderr)
        return jsonify({'error': '文件不存在'}), 404

    # 获取文件大小
    file_size = os.path.getsize(output_path)
    print(f"[DOWNLOAD-FILE] Serving file: {output_path} ({file_size} bytes)", file=sys.stderr)

    # 简化文件名处理 - 使用ASCII安全的文件名
    filename = task.get('filename', 'video.mp4')
    # 只保留字母数字和基本符号，替换其他字符
    safe_filename = ''.join(c if c.isalnum() or c in '._-' else '_' for c in filename)
    if not safe_filename.endswith('.mp4'):
        safe_filename += '.mp4'

    print(f"[DOWNLOAD-FILE] Filename: {filename} -> {safe_filename}", file=sys.stderr)

    try:
        # 使用 send_file 代替手动流式传输，更可靠
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='video/mp4'
        )

        # 清理文件和任务
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(output_path)
                print(f"[DOWNLOAD-{task_id[:8]}] File deleted", file=sys.stderr)
            except Exception as e:
                print(f"[DOWNLOAD-{task_id[:8]}] Cleanup error: {e}", file=sys.stderr)
            if task_id in download_tasks:
                del download_tasks[task_id]

        print(f"[DOWNLOAD-FILE] Sending response", file=sys.stderr)
        return response

    except Exception as e:
        print(f"[DOWNLOAD-FILE] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({'error': f'下载失败: {str(e)}'}), 500


@app.route('/api/proxy/download/cleanup', methods=['POST'])
def cleanup_old_tasks():
    """清理超过1小时的旧任务"""
    try:
        current_time = time.time()
        expired_tasks = []

        for task_id, task in download_tasks.items():
            if current_time - task.get('created_at', 0) > 3600:
                expired_tasks.append(task_id)
                output_path = task.get('output_path')
                if output_path and os.path.exists(output_path):
                    try:
                        os.unlink(output_path)
                    except:
                        pass

        for task_id in expired_tasks:
            del download_tasks[task_id]

        return jsonify({'success': True, 'cleaned': len(expired_tasks)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'message': '请求的资源不存在'
    }), 404


@app.errorhandler(500)
def server_error(e):
    """500 错误处理"""
    print(f"[ERROR] Server error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    return jsonify({
        'success': False,
        'message': '服务器内部错误，请稍后重试'
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    print("=" * 50)
    print("万能视频下载服务启动中...")
    print(f"访问地址: http://localhost:{port}")
    print(f"API 地址: http://localhost:{port}/api")
    print(f"调试模式: {debug}")

    # 初始化AI功能（新增）
    if AI_ENABLED:
        ai_ok = init_ai_routes()
        if ai_ok:
            app.register_blueprint(ai_bp)
            print("AI summarization feature: Enabled")
        else:
            print("AI总结功能: 未配置（请在 backend/.env 中设置 DEEPSEEK_API_KEY）")
    else:
        print("AI总结功能: 模块未安装")

    # 初始化认证功能（新增）
    if AUTH_ENABLED:
        create_auth_routes(app)
        print("用户认证功能: Enabled")
    else:
        print("用户认证功能: 模块未安装")

    # 初始化支付功能（新增，可选）
    if PAYMENT_ENABLED:
        create_payment_routes(app)
        print("Stripe 支付功能: Enabled")
    else:
        print("Stripe 支付功能: 未配置")

    print("=" * 50)

    app.run(host='0.0.0.0', port=port, debug=debug)
