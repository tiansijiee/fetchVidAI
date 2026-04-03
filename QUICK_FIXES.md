# 🚨 上线前必须修复的问题清单

## 必须立即修复（代码修改）

### 1. CORS配置修复

**文件：** `backend/app.py`

**第68行，修改：**
```python
# ❌ 修改前
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", ...],
    }
})

# ✅ 修改后
import os
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Fingerprint", "X-Request-ID"],
        "supports_credentials": True
    }
})
```

### 2. 添加健康检查接口

**文件：** `backend/app.py`

**在文件末尾添加：**
```python
@app.route('/health')
def health_check():
    """健康检查接口"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'message': str(e)
        }), 500
```

### 3. 修改调试模式

**文件：** `backend/app.py`

**第1264行，修改：**
```python
# ❌ 修改前
debug = os.environ.get('DEBUG', 'True').lower() == 'true'

# ✅ 修改后
debug = os.environ.get('DEBUG', 'False').lower() == 'true'
```

### 4. 前端生产配置

**创建文件：** `frontend/.env.production`
```
VITE_API_BASE_URL=https://your-domain.com/api
```

**修改文件：** `frontend/vite.config.js`
```javascript
export default defineConfig({
  // ...其他配置
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // 移除console.log
        drop_debugger: true
      }
    }
  }
})
```

---

## 服务器环境准备

### 安装必要的Python包

**在服务器上运行：**
```bash
pip install gunicorn gevent Flask-Limiter
```

### 创建生产环境配置

**在服务器创建：** `/opt/fetchvid/backend/.env`
```env
# Flask配置
FLASK_ENV=production
DEBUG=False
SECRET_KEY=使用python3 -c "import secrets; print(secrets.token_urlsafe(32))"生成

# CORS配置
ALLOWED_ORIGINS=https://your-domain.com

# DeepSeek API
DEEPSEEK_API_KEY=你的密钥

# JWT密钥
JWT_SECRET_KEY=使用python3 -c "import secrets; print(secrets.token_urlsafe(32))"生成
```

---

## 验证清单

部署后逐项检查：

- [ ] 访问 https://your-domain.com 显示前端
- [ ] 访问 https://your-domain.com/health 返回健康状态
- [ ] 测试视频解析功能正常
- [ ] 测试AI总结功能正常
- [ ] 测试下载功能正常
- [ ] 检查浏览器控制台无错误
- [ ] 检查服务器日志无报错