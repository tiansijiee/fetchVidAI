# Python 环境配置指南

## 问题诊断
你的系统中的 Python 是 Windows 应用商店的启动器，而不是完整的 Python 安装。

## 快速解决方案

### 方法 1：从官网下载安装 Python（推荐）

1. **下载 Python**
   - 访问：https://www.python.org/downloads/
   - 下载 Python 3.11 或 3.12（推荐 64 位版本）
   - 直接下载链接：https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe

2. **安装时重要选项**
   - ✅ 必须勾选 "Add Python to PATH"
   - 选择 "Install Now" 或自定义安装

3. **验证安装**
   ```bash
   # 打开新的命令行窗口，运行：
   python --version
   pip --version
   ```

### 方法 2：使用 Windows Store 安装

1. 打开 Microsoft Store
2. 搜索 "Python 3.11" 或 "Python 3.12"
3. 点击安装（免费）

### 方法 3：使用包管理器（如果你有）

```bash
# 使用 Scoop
scoop install python

# 使用 Chocolatey
choco install python
```

## 安装完成后继续

1. **重新打开命令行窗口**（重要！）
2. 运行以下命令安装项目依赖：
   ```bash
   cd d:\project\AI-agent\fetchVidAI\backend
   pip install -r requirements.txt
   ```

3. **启动服务**
   ```bash
   # 后端
   cd backend
   python app.py

   # 前端（新开一个窗口）
   cd frontend
   npm install
   npm run dev
   ```

## 当前问题说明
- 错误代码 49 表示 Python 可执行文件不是真正的 Python 安装
- WindowsApps 中的 python 只是一个启动器
- 需要安装完整的 Python 才能运行项目

## 安装验证清单
- [ ] Python 已安装（运行 `python --version` 显示版本号）
- [ ] pip 可用（运行 `pip --version` 显示版本号）
- [ ] 可以导入模块（运行 `python -c "import sys; print(sys.version)"`）
