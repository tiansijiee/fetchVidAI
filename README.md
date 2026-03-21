# FetchVid - 万能视频下载器

一个支持多平台的视频下载工具，使用 Flask + Vue3 + yt-dlp 技术栈开发。

## 功能特点

- 支持平台：B站、微博、知乎、YouTube、Twitter、TikTok、Instagram、Vimeo 等8大平台
- 多分辨率选择：支持360P-1080P多种画质
- 极速解析：秒级响应，即时获取视频信息
- 安全可靠：本地下载，保护隐私安全
- 响应式设计：完美适配移动端和桌面端

## 技术栈

### 后端
- Python 3.8+
- Flask - Web框架
- yt-dlp - 视频解析核心
- FFmpeg - 音视频合并

### 前端
- Vue 3 - 前端框架
- Vite - 构建工具
- Tailwind CSS - 样式框架
- Element Plus - UI组件库

## 项目结构

```
fetchVidAI/
├── backend/
│   ├── app.py              # Flask 主程序
│   ├── video_parser.py     # yt-dlp 封装
│   └── requirements.txt    # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── App.vue         # 主组件
│   │   ├── main.js         # 入口文件
│   │   └── style.css       # 全局样式
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 安装部署

### 环境要求
- Python 3.8+
- Node.js 16+
- FFmpeg（用于B站视频音视频合并）

### 后端安装

```bash
cd backend
pip install -r requirements.txt
```

### 前端安装

```bash
cd frontend
npm install
```

### FFmpeg 安装

**Windows:**
1. 下载 FFmpeg：https://ffmpeg.org/download.html
2. 解压到 `C:\ffmpeg`
3. 添加环境变量：`C:\ffmpeg\bin`

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

## 运行项目

### 启动后端

```bash
cd backend
python app.py
```

后端运行在：http://localhost:5000

### 启动前端

```bash
cd frontend
npm run dev
```

前端运行在：http://localhost:3000

## API 文档

### 解析视频

**请求：**
```
POST /api/parse
Content-Type: application/json

{
  "url": "视频链接"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "title": "视频标题",
    "thumbnail": "封面URL",
    "duration": "时长",
    "formats": [
      {
        "format_id": "格式ID",
        "quality": "画质",
        "ext": "格式",
        "size_formatted": "大小"
      }
    ]
  }
}
```

### 下载视频

**请求：**
```
POST /api/proxy/download
Content-Type: application/json

{
  "video_url": "视频链接",
  "filename": "文件名",
  "format_id": "格式ID"
}
```

**响应：**
```json
{
  "success": true,
  "task_id": "任务ID"
}
```

### 查询下载状态

**请求：**
```
GET /api/proxy/download/status/{task_id}
```

**响应：**
```json
{
  "status": "completed",
  "progress": 100,
  "filename": "视频文件名.mp4"
}
```

## 使用说明

1. 粘贴视频链接到输入框
2. 点击"解析视频"按钮
3. 选择想要的画质
4. 点击"开始下载"即可

## 会员功能

### 免费版
- 每日5次下载
- 最高720P画质
- 基础下载速度

### 月度会员 (¥19.9/月)
- 每日100次下载
- 最高1080P画质
- 加速下载
- 批量下载(10个)

### 年度会员 (¥99/年)
- 无限次下载
- 最高4K超清
- 极速下载
- 无限批量下载

## 注意事项

1. 本项目仅供学习交流使用
2. 请勿用于商业用途
3. 下载的内容请遵守版权法律法规
4. 部分平台可能需要登录才能下载

## 更新日志

### v1.0.0 (2024-03-21)
- 初始版本发布
- 支持8大平台视频下载
- 实现多分辨率选择
- 添加会员体系

## 开源协议

MIT License

## 联系方式

如有问题或建议，欢迎提交 Issue。
