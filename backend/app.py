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

# 创建 Flask 应用
app = Flask(__name__, static_folder='../frontend/dist')

# 全局配置
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# 启用 CORS - 支持所有开发端口
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
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

        # 识别平台
        platform = VideoParser.identify_platform(url)

        # 抖音使用专用解析器
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

    except Exception as e:
        print(f"[ERROR] Parse error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({'success': False, 'message': f'解析失败: {str(e)}'}), 500


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
        format_id = data.get('format_id')  # 新增：用户选择的格式ID

        if not video_url:
            return jsonify({'success': False, 'message': '缺少视频链接'}), 400

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
                # 基础配置
                ydl_opts = {
                    'outtmpl': output_path,
                    'quiet': True,
                    'no_warnings': True,
                }

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
                        'retries': 10,  # 增加重试次数
                        'file_access_retries': 10,
                        'fragment_retries': 10,  # 分片重试次数
                        'skip_unavailable_fragments': False,  # 不跳过失败片段
                        'ignoreerrors': False,  # 遇到错误时停止
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
                        },
                        # 网络配置
                        'socket_timeout': 30,
                        # DASH配置
                        'extractor_args': {
                            'bilibili': {
                                'prefer_formats': 'dash-flv,_dash-mp4,aac-flv,mp4-flv'
                            }
                        }
                    })

                    # 根据用户选择的格式ID设置下载格式
                    if format_id and format_id != 'best':
                        # 用户指定了特定格式
                        if has_ffmpeg:
                            # 有ffmpeg时，可以合并音视频
                            ydl_opts.update({
                                'format': f'{format_id}+bestaudio/best',
                                'merge_output_format': 'mp4',
                                'http_headers': {
                                    'Referer': video_url,
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                                }
                            })
                            print(f"[DOWNLOAD-{task_id[:8]}] Using format_id: {format_id} + audio merge", file=sys.stderr)
                        else:
                            # 无ffmpeg时，只下载视频流
                            ydl_opts.update({
                                'format': format_id,
                                'merge_output_format': None,
                                'http_headers': {
                                    'Referer': video_url,
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                                }
                            })
                            print(f"[DOWNLOAD-{task_id[:8]}] Using format_id: {format_id} (no audio merge)", file=sys.stderr)
                    elif format_id == 'best' or not format_id:
                        # 最佳质量或默认
                        if has_ffmpeg:
                            # 有ffmpeg时，下载最高质量并合并音视频
                            ydl_opts.update({
                                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/bestvideo+bestaudio/best',
                                'merge_output_format': 'mp4',
                                'http_headers': {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                                    'Referer': 'https://www.bilibili.com/',
                                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                }
                            })
                            print(f"[DOWNLOAD-{task_id[:8]}] Using best format with audio merge", file=sys.stderr)
                        else:
                            # 无ffmpeg时，使用单格式
                            ydl_opts.update({
                                'format': 'bestvideo[ext=mp4][height<=1080]/bestvideo[ext=mp4]/best[height<=1080]/best',
                                'merge_output_format': None,
                                'postprocessors': [],
                                'http_headers': {
                                    'Referer': video_url,
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                                }
                            })
                            print(f"[DOWNLOAD-{task_id[:8]}] Using best format (no ffmpeg)", file=sys.stderr)
                    else:
                        # 无ffmpeg时，使用B站专用的下载格式
                        ydl_opts.update({
                            'format': 'bestvideo[ext=mp4][height<=720]/bestvideo[ext=mp4]/best[height<=720]/best',
                            'merge_output_format': None,
                            'postprocessors': [],
                            'http_headers': {
                                'Referer': video_url,
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                            }
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
                            'nocheckcertificate': True,
                            'socket_timeout': 60,
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
                            'nocheckcertificate': True,
                            'socket_timeout': 60,
                            'http_headers': {
                                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                                'Referer': 'https://www.xiaohongshu.com/'
                            }
                        })
                        print(f"[DOWNLOAD-{task_id[:8]}] Using browser cookies for Xiaohongshu", file=sys.stderr)
                else:
                    # YouTube 和其他平台
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
                        download_tasks[task_id]['progress'] = progress
                        if progress % 20 == 0:  # 每20%打印一次
                            print(f"[DOWNLOAD-{task_id[:8]}] Progress: {progress}% ({downloaded}/{total})", file=sys.stderr)

                ydl_opts['progress_hooks'] = [progress_hook]

                print(f"[DOWNLOAD-{task_id[:8]}] Starting download for platform: {platform}", file=sys.stderr)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                # 检查文件
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    if file_size >= 1000:  # 至少1KB
                        download_tasks[task_id]['status'] = 'completed'
                        download_tasks[task_id]['file_size'] = file_size
                        download_tasks[task_id]['progress'] = 100
                        print(f"[DOWNLOAD-{task_id[:8]}] ✓ Completed: {file_size} bytes", file=sys.stderr)
                    else:
                        download_tasks[task_id]['status'] = 'error'
                        download_tasks[task_id]['error'] = f'下载文件太小 ({file_size} bytes)'
                        print(f"[DOWNLOAD-{task_id[:8]}] ✗ File too small", file=sys.stderr)
                else:
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = '文件未创建'
                    print(f"[DOWNLOAD-{task_id[:8]}] ✗ No file created", file=sys.stderr)

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
                else:
                    download_tasks[task_id]['status'] = 'error'
                    download_tasks[task_id]['error'] = f'下载失败: {error_msg[:100]}'

            except Exception as e:
                error_msg = str(e)
                download_tasks[task_id]['status'] = 'error'
                download_tasks[task_id]['error'] = f'下载异常: {error_msg[:150]}'
                print(f"[DOWNLOAD-{task_id[:8]}] ✗ Exception: {error_msg}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)

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

    output_path = task.get('output_path')
    if not output_path or not os.path.exists(output_path):
        print(f"[DOWNLOAD-FILE] File not found: {output_path}", file=sys.stderr)
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
            print("AI summarization feature: Not configured (please set DEEPSEEK_API_KEY in backend/.env)")
    else:
        print("AI总结功能: 模块未安装")

    print("=" * 50)

    app.run(host='0.0.0.0', port=port, debug=debug)
