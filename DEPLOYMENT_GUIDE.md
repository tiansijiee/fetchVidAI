# FetchVid AI 生产环境部署指南

## 📋 部署方案概述

### 推荐架构

```
                     ┌─────────────────┐
                     │   用户浏览器     │
                     └────────┬────────┘
                              │
                    ┌─────────▼─────────┐
                    │   前端 (免费托管)   │
                    │   Vercel/Netlify  │
                    └─────────┬─────────┘
                              │ HTTPS API调用
                    ┌─────────▼─────────┐
                    │  后端 (阿里云ECS)  │
                    │  Flask + Gunicorn │
                    │  68元/年 1核2G    │
                    └───────────────────┘
```

### 费用预估

| 项目 | 平台 | 配置 | 费用 |
|------|------|------|------|
| **前端** | Vercel/Netlify | 静态托管 | **免费** |
| **后端** | 阿里云ECS | 1核2G, 1Mbps | **68元/年** |
| **域名** | 阿里云/腾讯云 | .com | **~60元/年** |
| **SSL证书** | Let's Encrypt | 自动续期 | **免费** |
| **API费用** | DeepSeek | 按量付费 | **~1元/百万tokens** |
| **月度成本** | - | - | **~15-25元** |

---

## 🚀 第一部分：前端部署（免费）

### 方案1: Vercel (推荐)

**优势：**
- 全球CDN加速
- 自动HTTPS
- GitHub集成，自动部署
- 无限制带宽
- 免费额度：100GB带宽/月

**部署步骤：**

```bash
# 1. 前端配置更新
cd frontend
```

**2. 修改 `vite.config.js` 添加生产环境API地址：**

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://your-backend-ip:5000',
        changeOrigin: true
      }
    }
  }
})
```

**3. 在 `frontend/src` 创建 `.env.production`：**

```env
VITE_API_BASE_URL=https://your-domain.com/api
```

**4. Vercel部署：**
- 访问 https://vercel.com
- 使用GitHub账号登录
- 导入项目仓库
- 选择 `frontend` 目录
- 点击部署

**5. 配置自定义域名（可选）：**
- 在Vercel添加域名
- 在域名DNS设置中添加CNAME记录

### 方案2: Netlify (备选)

**优势：**
- 免费额度更大（300GB/月）
- 支持表单处理
- 易于使用

---

## 🖥️ 第二部分：后端部署（阿里云）

### 服务器配置建议

**最低配置（68元/年）：**
- CPU: 1核
- 内存: 2GB
- 带宽: 1Mbps
- 系统盘: 40GB

**推荐配置（约200元/年）：**
- CPU: 2核
- 内存: 4GB
- 带宽: 3Mbps

### 部署步骤

#### 1. 购买阿里云ECS

1. 访问阿里云官网
2. 选择 "轻量应用服务器"
3. 选择系统: Ubuntu 22.04
4. 选择套餐: 1核2G (约68元/年)

#### 2. 服务器初始化

```bash
# 连接服务器
ssh root@your-server-ip

# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y git curl wget vim nginx python3-pip python3-venv

# 安装FFmpeg (视频处理必需)
apt install -y ffmpeg

# 安装Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
```

#### 3. 配置Python环境

```bash
# 创建项目目录
cd /opt
mkdir fetchvid
cd fetchvid

# 克隆代码
git clone https://github.com/your-username/fetchVidAI.git .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt

# 安装生产服务器
pip install gunicorn gevent
```

#### 4. 配置环境变量

```bash
# 创建 .env 文件
cat > /opt/fetchvid/backend/.env << 'EOF'
# DeepSeek API
DEEPSEEK_API_KEY=your_api_key_here

# Flask配置
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your_random_secret_key_here
EOF
```

#### 5. 配置系统服务 (systemd)

```bash
cat > /etc/systemd/system/fetchvid.service << 'EOF'
[Unit]
Description=FetchVid Backend Application
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

[Install]
WantedBy=multi-user.target
EOF

# 创建日志目录
mkdir -p /var/log/fetchvid
chown www-data:www-data /var/log/fetchvid

# 启动服务
systemctl daemon-reload
systemctl enable fetchvid
systemctl start fetchvid
```

#### 6. 配置Nginx反向代理

```bash
cat > /etc/nginx/sites-available/fetchvid << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ai/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_buffering off;
        proxy_cache off;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/fetchvid /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 7. 配置SSL证书

```bash
# 安装 Certbot
apt install -y certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d your-domain.com
```

---

## ⚠️ 第三部分：上线前必须优化项

### 1. 安全性优化

**添加API限流：**

```python
# backend/requirements.txt 添加
Flask-Limiter>=3.5.0

# backend/app.py 添加
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app=app, key_func=get_remote_address)

@app.route('/api/parse', methods=['POST'])
@limiter.limit("20 per minute")
def parse_video():
    # ...
```

### 2. 错误处理优化

```python
# backend/app.py 添加全局错误处理
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return jsonify({
        'success': False,
        'message': '服务器内部错误，请稍后重试'
    }), 500
```

### 3. 日志配置

```python
# backend/app.py 添加日志
import logging
from logging.handlers import RotatingFileHandler

if not os.path.exists('logs'):
    os.mkdir('logs')

handler = RotatingFileHandler('logs/error.log', maxBytes=1024*1024, backupCount=10)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)
```

### 4. 数据备份

```bash
# 添加到 crontab
crontab -e

# 每天凌晨2点备份数据库
0 2 * * * sqlite3 /opt/fetchvid/backend/fetchvid.db ".backup /opt/backups/fetchvid_$(date +\%Y\%m\%d).db"
```

---

## ✅ 上线前检查清单

### 安全检查
- [ ] 修改默认密码
- [ ] 配置防火墙 (`ufw allow 80; ufw allow 443`)
- [ ] 启用SSL证书
- [ ] 配置CORS白名单
- [ ] 添加API限流
- [ ] 移除调试代码

### 功能检查
- [ ] 视频解析正常
- [ ] 下载功能正常
- [ ] AI总结功能正常
- [ ] 支付功能正常

### 性能检查
- [ ] 缓存功能正常
- [ ] 日志正常记录

### 法律检查
- [ ] 添加版权声明
- [ ] 添加用户协议
- [ ] 添加隐私政策

---

## 📈 扩展升级路径

当用户量增长时，可以考虑：

1. **升级服务器**: 2核4G → 4核8G
2. **添加Redis**: 缓存热数据
3. **使用CDN**: 加速静态资源
4. **数据库升级**: SQLite → PostgreSQL

---

**祝部署顺利！🚀**