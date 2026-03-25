# FetchVid AI - 智能视频下载与分析平台

一个支持多平台的视频下载工具，集成AI智能分析功能，使用 Flask + Vue3 + yt-dlp + DeepSeek 技术栈开发。

## 🌟 核心功能

### 视频下载
- **支持平台**：B站、微博、知乎、YouTube、Twitter、TikTok、Instagram、Vimeo 等8大平台
- **多分辨率选择**：支持360P-1080P多种画质
- **极速解析**：秒级响应，即时获取视频信息
- **安全可靠**：本地下载，保护隐私安全
- **响应式设计**：完美适配移动端和桌面端

### AI智能分析 ⭐ NEW
- **视频内容总结**：使用DeepSeek AI自动生成视频摘要
- **思维导图生成**：自动将视频内容转换为可视化思维导图
- **智能字幕提取**：支持多种字幕格式，自动时间轴对齐
- **AI问答互动**：基于视频内容的智能问答系统
- **SSE实时流式输出**：ChatGPT风格的打字机效果
- **ASR语音识别**：无字幕视频自动语音转文字（faster-whisper）

## 🛠 技术栈

### 后端
- **Python 3.8+** - 核心语言
- **Flask** - Web框架
- **yt-dlp** - 视频解析核心
- **FFmpeg** - 音视频处理
- **DeepSeek API** - AI分析服务
- **faster-whisper** - 语音识别（ASR）
- **Server-Sent Events (SSE)** - 实时流式输出

### 前端
- **Vue 3** - 前端框架（Composition API）
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Element Plus** - UI组件库
- **markmap-view** - 思维导图可视化
- **Vue Router** - 路由管理
- **axios** - HTTP客户端

## 📁 项目结构

```
fetchVidAI/
├── backend/
│   ├── app.py                  # Flask 主程序
│   ├── ai_routes.py            # AI分析路由（SSE流式输出）
│   ├── ai_summarizer.py        # AI总结模块
│   ├── subtitle_extractor.py   # 字幕提取器（B站API + yt-dlp + ASR）
│   ├── audio_transcriber.py    # ASR语音转写模块
│   ├── video_parser.py         # yt-dlp 视频解析封装
│   ├── requirements.txt        # Python 依赖
│   └── .env                    # 环境配置（不提交到Git）
├── frontend/
│   ├── src/
│   │   ├── App.vue             # 根组件
│   │   ├── main.js             # 入口文件
│   │   ├── router/             # 路由配置
│   │   │   └── index.js
│   │   ├── views/              # 页面组件
│   │   │   ├── VideoDownload.vue    # 视频下载页（集成AI分析）
│   │   │   └── VideoSummarize.vue   # AI总结页
│   │   ├── components/         # 可复用组件
│   │   │   ├── VideoAIPanel.vue     # AI分析面板
│   │   │   ├── MindmapPanel.vue     # 思维导图组件
│   │   │   ├── SubtitlePanel.vue    # 字幕显示组件
│   │   │   └── VideoSummary.vue     # 总结展示组件
│   │   └── style.css           # 全局样式
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── README.md                   # 项目说明
├── .gitignore                  # Git忽略配置
└── setup-guide.md              # 环境配置指南
```

## 🚀 安装部署

### 环境要求
- Python 3.8+
- Node.js 16+
- FFmpeg（用于B站视频音视频合并和ASR语音识别）

### 后端安装

```bash
cd backend
pip install -r requirements.txt
```

### 配置环境变量

创建 `backend/.env` 文件：

```env
# DeepSeek API配置（必需）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 可选配置
FLASK_ENV=development
FLASK_DEBUG=1
```

> 获取DeepSeek API Key：https://platform.deepseek.com/

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

## 🎯 运行项目

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

## 📖 API 文档

### 视频解析

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

### AI视频总结（SSE流式）

**请求：**
```
POST /ai/summarize/char-stream
Content-Type: application/json

{
  "url": "视频链接",
  "title": "视频标题",
  "description": "视频描述",
  "use_asr": false
}
```

**响应（SSE事件流）：**
```
event: subtitle
data: {"segments": [...], "subtitles": [...], "text": "...", "length": 2342}

event: summary
data: {"token": "视"}

event: summary
data: {"token": "频"}

event: mindmap
data: {"mindmap": "# 视频主题\n## 要点1\n- 内容..."}

event: done
data: {"message": "分析完成"}
```

### AI问答

**请求：**
```
POST /ai/chat/stream
Content-Type: application/json

{
  "question": "用户问题",
  "url": "视频链接",
  "subtitle_text": "字幕文本",
  "chat_history": []
}
```

## 🎨 功能特性详解

### 字幕提取优先级

1. **B站专用API**（优先）
   - 直接调用 `api.bilibili.com` 获取CC字幕和AI字幕
   - 支持时间轴精确对齐

2. **yt-dlp通用提取**（次选）
   - 支持YouTube等平台的自动字幕
   - 支持多种字幕格式（VTT/JSON/SRT）

3. **ASR语音识别**（兜底）
   - 使用faster-whisper进行语音转写
   - 自动生成时间轴
   - 支持中英文识别

### 思维导图可视化

- **交互式SVG**：使用markmap-view渲染
- **自动布局**：智能节点排列
- **缩放适配**：自适应容器大小
- **一键导出**：支持Markdown格式

### SSE实时流式输出

- **逐字显示**：ChatGPT风格的打字机效果
- **多事件类型**：subtitle、summary、mindmap、done、error
- **进度提示**：实时显示处理状态
- **错误恢复**：优雅的异常处理

## 💡 使用说明

### 视频下载
1. 粘贴视频链接到输入框
2. 点击"解析视频"按钮
3. 选择想要的画质
4. 点击"开始下载"即可

### AI视频分析
1. 在视频下载页面，点击"AI智能分析"标签
2. 系统自动提取字幕（或使用ASR转写）
3. AI生成总结、思维导图
4. 可进行AI问答互动

## 🔒 安全注意事项

1. **环境变量**：`.env` 文件不要提交到Git
2. **API密钥**：妥善保管DeepSeek API密钥
3. **内容版权**：下载的内容请遵守版权法律法规
4. **学习用途**：本项目仅供学习交流使用，请勿用于商业用途

## 📊 会员功能

### 免费版
- 每日5次下载
- 最高720P画质
- 基础下载速度
- AI分析每日3次

### 月度会员 (¥19.9/月)
- 每日100次下载
- 最高1080P画质
- 加速下载
- 批量下载(10个)
- AI分析每日50次

### 年度会员 (¥99/年)
- 无限次下载
- 最高4K超清
- 极速下载
- 无限批量下载
- 无限AI分析

## 🔄 更新日志

### v2.0.0 (2025-03-25) - AI智能分析版
- ✨ 新增AI视频总结功能（DeepSeek）
- ✨ 新增思维导图自动生成
- ✨ 新增智能字幕提取（B站API + yt-dlp + ASR）
- ✨ 新增AI问答互动功能
- ✨ 实现SSE实时流式输出
- ✨ 集成faster-whisper语音识别
- 🐛 修复B站字幕解析问题
- 🐛 修复ASR字幕时间戳转换问题
- ♻️ 优化代码结构，删除重复逻辑

### v1.0.0 (2024-03-21)
- 初始版本发布
- 支持8大平台视频下载
- 实现多分辨率选择
- 添加会员体系

## 📝 开源协议

MIT License

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📧 联系方式

如有问题或建议，欢迎提交 Issue。

---

**⭐ 如果觉得有用，请给个Star支持一下！**
