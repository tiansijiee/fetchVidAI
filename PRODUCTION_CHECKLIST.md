# FetchVid AI 项目上线分析报告

## 🔍 当前项目状态排查

### ✅ 已完成的功能
- [x] 视频解析和下载功能
- [x] AI视频总结功能
- [x] 字幕提取功能
- [x] 思维导图生成
- [x] 用户认证系统
- [x] 视频缓存优化

### ⚠️ 上线前必须处理的问题

#### 🔴 高优先级（必须修复）

| 问题 | 影响 | 修复方案 |
|------|------|----------|
| **CORS配置硬编码** | 只能本地访问 | 修改为生产域名 |
| **调试模式开启** | 安全风险 | 关闭DEBUG模式 |
| **无API限流** | 易被滥用 | 添加Flask-Limiter |
| **敏感信息泄露** | 密钥暴露 | 检查.gitignore |
| **无错误监控** | 问题难以排查 | 添加日志系统 |

#### 🟡 中优先级（建议修复）

| 问题 | 影响 | 修复方案 |
|------|------|----------|
| 前端无生产配置 | 需要手动改API地址 | 添加.env.production |
| 无健康检查接口 | 无法监控服务状态 | 添加/health端点 |
| 缓存无自动清理 | 磁盘可能占满 | 添加定时清理任务 |
| 无数据备份 | 数据丢失风险 | 添加自动备份 |

#### 🟢 低优先级（可选优化）

- 添加性能监控
- 优化前端打包体积
- 添加CDN加速
- 数据库升级到PostgreSQL

---

## 📋 完整部署流程详解

### 📊 部署流程总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        部署流程总览                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1️⃣ 准备阶段 ──────────────────────────────────────────────────►   │
│     ├─ 购买服务器和域名                                            │
│     ├─ 本地代码优化                                                │
│     └─ 准备配置文件                                                │
│                                                                     │
│  2️⃣ 前端部署 ──────────────────────────────────────────────────►   │
│     ├─ 修改API配置                                                  │
│     ├─ 打包构建                                                    │
│     └─ 上传到Vercel/Netlify                                        │
│                                                                     │
│  3️⃣ 后端部署 ──────────────────────────────────────────────────►   │
│     ├─ 连接服务器                                                  │
│     ├─ 安装环境                                                    │
│     ├─ 部署代码                                                    │
│     └─ 配置Nginx+SSL                                               │
│                                                                     │
│  4️⃣ 测试验证 ──────────────────────────────────────────────────►   │
│     ├─ 功能测试                                                    │
│     ├─ 性能测试                                                    │
│     └─ 安全检查                                                    │
│                                                                     │
│  5️⃣ 监控维护 ──────────────────────────────────────────────────►   │
│     ├─ 日志监控                                                    │
│     ├─ 数据备份                                                    │
│     └─ 定期更新                                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📝 第一部分：准备阶段（本地操作）

### 步骤1: 修复CORS配置

**问题：** 后端CORS只允许本地访问

**位置：** `backend/app.py` 第68-75行

**修改前：**
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", ...],  # ❌ 只允许本地
        ...
    }
})
```

**修改后：**
```python
# 从环境变量读取允许的域名
import os
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
if not ALLOWED_ORIGINS:
    # 开发环境默认值
    ALLOWED_ORIGINS = ["http://localhost:3000"]

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,  # ✅ 支持配置
        ...
    }
})
```

### 步骤2: 创建生产环境配置

**创建文件：** `backend/.env.production`

```env
# 生产环境配置
DEBUG=False
FLASK_ENV=production
SECRET_KEY=在这里生成一个随机密钥

# CORS允许的域名（用逗号分隔）
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# DeepSeek API
DEEPSEEK_API_KEY=你的API密钥

# JWT密钥（至少32位）
JWT_SECRET_KEY=你的JWT密钥至少32位

# Stripe支付（如果启用）
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
```

### 步骤3: 前端生产配置

**创建文件：** `frontend/.env.production`

```env
# 生产环境API地址
VITE_API_BASE_URL=https://your-domain.com/api
```

**修改文件：** `frontend/vite.config.js`

```javascript
export default defineConfig({
  // ... 其他配置
  build: {
    // 生产环境移除console
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  }
})
```

### 步骤4: 生成安全密钥

**运行命令：**

```bash
# 方法1: 使用Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法2: 使用OpenSSL
openssl rand -base64 32
```

**将生成的密钥填入 `.env.production` 的 `SECRET_KEY` 和 `JWT_SECRET_KEY`**

---

## 🌐 第二部分：前端部署（Vercel）

### 什么是Vercel？

**Vercel** 是一个免费的静态网站托管平台，专门用于前端项目部署。

**为什么用Vercel？**
- ✅ 完全免费（个人项目）
- ✅ 全球CDN加速
- ✅ 自动HTTPS
- ✅ Git集成，推送代码自动部署
- ✅ 自定义域名支持

### 部署步骤详解

#### 步骤1: 准备GitHub仓库

```bash
# 1. 在GitHub创建新仓库
# 2. 推送代码到GitHub
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin master
```

#### 步骤2: 注册Vercel

```
1. 访问 https://vercel.com
2. 点击 "Sign Up"
3. 使用GitHub账号登录（推荐）
4. 授权Vercel访问你的GitHub仓库
```

#### 步骤3: 导入项目

```
1. 登录后点击 "New Project"
2. 选择你的GitHub仓库
3. Vercel会自动检测到这是一个Vite + Vue项目
```

#### 步骤4: 配置项目

**Vercel会自动识别配置，但需要确认以下设置：**

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

#### 步骤5: 环境变量配置

**在Vercel项目设置中添加：**

```
Settings → Environment Variables

Name: VITE_API_BASE_URL
Value: https://your-domain.com/api
Environment: Production
```

#### 步骤6: 部署

```
1. 点击 "Deploy" 按钮
2. 等待部署完成（大约1-2分钟）
3. 部署成功后会得到一个 .vercel.app 域名
   例如: https://your-project.vercel.app
```

#### 步骤7: 自定义域名（可选）

```
1. 在Vercel项目 → Settings → Domains
2. 添加你的域名: your-domain.com
3. Vercel会显示DNS配置
4. 在你的域名服务商添加CNAME记录:
   类型: CNAME
   名称: @
   值: cname.vercel-dns.com
```

---

## 🖥️ 第三部分：后端部署（阿里云）

### 什么是阿里云ECS？

**ECS** = Elastic Compute Service（云服务器）

**通俗解释：**
- 就是租了一台远程电脑
- 你可以通过SSH连接控制它
- 24小时开机，公网可访问
- 按配置付费，68元/年是最低配置

### 为什么需要服务器？

**前端（Vercel）只能托管静态文件：**
- HTML、CSS、JS等
- 无法运行Python代码
- 无法直接连接数据库
- 无法处理视频下载

**后端（阿里云）负责：**
- 运行Flask应用
- 调用yt-dlp下载视频
- 连接DeepSeek API
- 处理用户认证
- 操作数据库

### 部署步骤详解

#### 步骤1: 购买服务器

```
1. 访问 https://aliyun.com
2. 注册/登录账号
3. 搜索 "轻量应用服务器"
4. 选择配置：
   - 镜像: Ubuntu 22.04
   - 套餐: 1核2G (约68元/年)
   - 时长: 1年
5. 购买并设置root密码（记住这个密码！）
6. 等待服务器创建完成（5-10分钟）
```

#### 步骤2: 连接服务器

**方法1: 使用阿里云控制台（推荐新手）**
```
1. 进入阿里云控制台
2. 找到你的服务器实例
3. 点击 "远程连接"
4. 选择 "VNC连接" 或 "Workbench"
5. 输入root密码登录
```

**方法2: 使用SSH（推荐熟悉命令行的）**
```bash
# 在本地终端执行
ssh root@你的服务器公网IP

# 输入密码后即可进入服务器
```

#### 步骤3: 初始化服务器环境

**登录服务器后执行以下命令：**

```bash
# === 更新系统 ===
apt update && apt upgrade -y

# === 安装基础工具 ===
apt install -y git curl wget vim unzip

# === 安装Python3和pip ===
apt install -y python3 python3-pip python3-venv

# === 安装Node.js 18 ===
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# === 安装FFmpeg（视频处理必需）===
apt install -y ffmpeg

# === 验证安装 ===
python3 --version  # 应显示 Python 3.x
node --version     # 应显示 v18.x.x
ffmpeg -version    # 应显示 ffmpeg 版本
```

**每个命令做什么？**

| 命令 | 作用 |
|------|------|
| `apt update` | 更新软件包列表 |
| `apt upgrade` | 升级已安装的软件 |
| `git` | 版本控制，用于下载代码 |
| `curl/wget` | 下载工具 |
| `python3` | 运行后端代码 |
| `nodejs` | 构建前端代码 |
| `ffmpeg` | 处理视频文件 |

#### 步骤4: 创建项目目录

```bash
# 创建项目目录
mkdir -p /opt/fetchvid
cd /opt/fetchvid

# 克隆代码（两种方式选一种）

# 方式1: 如果代码在GitHub
git clone https://github.com/你的用户名/fetchVidAI.git .

# 方式2: 使用SCP从本地上传
# 在本地终端执行：
scp -r d:/project/AI-agent/fetchVidAI root@服务器IP:/opt/fetchvid
```

#### 步骤5: 配置后端环境

```bash
# 进入后端目录
cd /opt/fetchvid/backend

# 创建Python虚拟环境（隔离项目依赖）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装生产服务器
pip install gunicorn gevent

# === 什么是虚拟环境？===
# 虚拟环境就像一个独立的Python空间
# 不同项目的依赖互不影响
# 例如: 项目A用Django 2.0，项目B用Django 3.0，互不冲突
```

#### 步骤6: 创建生产配置

```bash
# 创建生产环境配置文件
cat > /opt/fetchvid/backend/.env << 'EOF'
# Flask配置
FLASK_ENV=production
DEBUG=False
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# CORS配置
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# DeepSeek API
DEEPSEEK_API_KEY=你的API密钥

# JWT密钥
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# 其他配置
MAX_CONTENT_LENGTH=104857600
EOF

# 保护配置文件权限
chmod 600 .env
```

#### 步骤7: 创建系统服务

**什么是systemd服务？**
- 让你的应用在后台持续运行
- 服务器重启后自动启动
- 可以用systemctl命令管理

```bash
# 创建服务配置文件
cat > /etc/systemd/system/fetchvid.service << 'EOF'
[Unit]
Description=FetchVid Backend Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/fetchvid/backend
Environment="PATH=/opt/fetchvid/venv/bin"
EnvironmentFile=/opt/fetchvid/backend/.env
ExecStart=/opt/fetchvid/venv/bin/gunicorn \
    --workers 2 \
    --worker-class gevent \
    --worker-connections 1000 \
    --timeout 120 \
    --bind 0.0.0.0:5000 \
    --access-logfile /var/log/fetchvid/access.log \
    --error-logfile /var/log/fetchvid/error.log \
    app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 创建日志目录
mkdir -p /var/log/fetchvid

# 设置文件权限
chown -R www-data:www-data /opt/fetchvid
chown -R www-data:www-data /var/log/fetchvid

# === 配置说明 ===
# workers: 工作进程数（建议: CPU核数 × 2 + 1）
# worker-class: 工作模式（gevent支持高并发）
# timeout: 请求超时时间（秒）
# bind: 绑定地址和端口
```

#### 步骤8: 安装和配置Nginx

**什么是Nginx？**
- 反向代理服务器
- 处理HTTP请求，转发给后端
- 提供静态文件服务
- SSL/HTTPS支持
- 负载均衡

```bash
# 安装Nginx
apt install -y nginx

# 创建站点配置
cat > /etc/nginx/sites-available/fetchvid << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    # 最大上传大小
    client_max_body_size 100M;

    # 超时设置
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;

    # API代理
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSE流式响应特殊处理
    location /ai/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
EOF

# 启用站点
ln -s /etc/nginx/sites-available/fetchvid /etc/nginx/sites-enabled/

# 删除默认站点
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 启动Nginx
systemctl start nginx
systemctl enable nginx
```

#### 步骤9: 配置SSL证书

**什么是SSL？**
- SSL = Secure Sockets Layer（安全套接层）
- 让网站从 http:// 变成 https://
- 数据传输加密，保护用户隐私
- 浏览器会显示"安全"标识

```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d your-domain.com

# 按提示操作：
# 1. 输入邮箱地址
# 2. 同意服务条款
# 3. 选择是否共享邮箱
# 4. 证书自动安装并配置

# 验证自动续期
certbot renew --dry-run
```

#### 步骤10: 启动应用

```bash
# 重载systemd配置
systemctl daemon-reload

# 启动应用
systemctl start fetchvid

# 设置开机自启
systemctl enable fetchvid

# 检查状态
systemctl status fetchvid

# 查看日志
tail -f /var/log/fetchvid/error.log
```

---

## ✅ 第四部分：测试验证

### 测试清单

```bash
# 1. 检查服务状态
systemctl status fetchvid
systemctl status nginx

# 2. 检查端口监听
netstat -tlnp | grep :5000  # 后端
netstat -tlnp | grep :80    # HTTP
netstat -tlnp | grep :443   # HTTPS

# 3. 测试API连接
curl https://your-domain.com/health

# 4. 测试视频解析
curl -X POST https://your-domain.com/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.bilibili.com/video/BV1xx411c7mD"}'

# 5. 检查日志
tail -f /var/log/fetchvid/error.log
tail -f /var/log/nginx/error.log
```

### 浏览器测试

```
1. 访问前端: https://your-domain.com
2. 检查控制台是否有错误
3. 测试视频解析功能
4. 测试下载功能
5. 测试AI总结功能
```

---

## 🔒 第五部分：安全加固

### 配置防火墙

```bash
# 安装ufw防火墙
apt install -y ufw

# 默认拒绝所有入站
ufw default deny incoming

# 允许所有出站
ufw default allow outgoing

# 允许SSH（重要！先设置这个）
ufw allow 22/tcp

# 允许HTTP和HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# 启用防火墙
ufw enable

# 查看状态
ufw status
```

### 定时任务

```bash
# 编辑crontab
crontab -e

# 添加以下任务：

# 每天凌晨2点备份数据库
0 2 * * * sqlite3 /opt/fetchvid/backend/fetchvid.db ".backup /opt/backups/fetchvid_$(date +\%Y\%m\%d).db"

# 每天凌晨3点清理缓存
0 3 * * * rm -rf /opt/fetchvid/backend/temp_downloads/* && rm -rf /opt/fetchvid/backend/video_cache/*

# 每周日凌晨4点清理日志
0 4 * * 0 find /var/log/fetchvid -name "*.log" -mtime +30 -delete
```

---

## 📊 第六部分：监控和维护

### 添加健康检查端点

**在 `backend/app.py` 添加：**

```python
@app.route('/health')
def health_check():
    """健康检查接口"""
    import psutil
    import os

    # 检查磁盘空间
    disk = psutil.disk_usage('/')
    disk_free_percent = (disk.free / disk.total) * 100

    # 检查内存
    memory = psutil.virtual_memory()

    return jsonify({
        'status': 'healthy' if disk_free_percent > 10 else 'warning',
        'disk_free_percent': round(disk_free_percent, 2),
        'memory_percent': memory.percent,
        'timestamp': time.time()
    })
```

### 日志查看命令

```bash
# 实时查看应用日志
tail -f /var/log/fetchvid/error.log

# 查看Nginx访问日志
tail -f /var/log/nginx/access.log

# 查看系统日志
journalctl -u fetchvid -f
```

---

## 💰 成本总结

### 月度成本预估

| 项目 | 费用 | 说明 |
|------|------|------|
| 服务器 | 68元/年 ÷ 12 = **5.7元/月** | 阿里云1核2G |
| 域名 | 60元/年 ÷ 12 = **5元/月** | 可选 |
| 前端托管 | **免费** | Vercel |
| SSL证书 | **免费** | Let's Encrypt |
| DeepSeek API | **按量付费** | 约1元/百万tokens |
| **总计** | **~10-20元/月** | 不含API费用 |

### 节省成本技巧

1. **前端用Vercel** - 完全免费
2. **SSL用Let's Encrypt** - 自动续期免费
3. **API缓存** - 减少API调用
4. **定期清理缓存** - 节省磁盘空间

---

## 🆘 常见问题解决

### 问题1: 连接服务器超时

```bash
# 检查服务器安全组
阿里云控制台 → ECS实例 → 安全组
添加规则: 允许入站 TCP 22端口
```

### 问题2: 502 Bad Gateway

```bash
# 检查后端服务状态
systemctl status fetchvid

# 查看后端日志
tail -f /var/log/fetchvid/error.log

# 重启后端
systemctl restart fetchvid
```

### 问题3: 磁盘满了

```bash
# 查看磁盘使用
df -h

# 清理缓存
rm -rf backend/temp_downloads/*
rm -rf backend/video_cache/*

# 查找大文件
du -sh * | sort -rh | head -10
```

---

## 📞 需要帮助？

如果遇到问题，可以：
1. 查看日志: `tail -f /var/log/fetchvid/error.log`
2. 检查服务状态: `systemctl status fetchvid`
3. 重启服务: `systemctl restart fetchvid`

---

**祝你部署顺利！🚀**