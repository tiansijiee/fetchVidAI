# Bug修复总结 - 知识点记录

## 修复日期：2025-03-29

---

## 问题1：B站字幕提取错误（获取弹幕而非字幕）

### 问题描述
B站视频字幕提取时，获取到的是弹幕内容而不是真正的字幕文本。

### 根本原因
**API选择错误**：B站提供了多个API接口，返回不同类型的数据

| API接口 | 返回数据 | 用途 |
|---------|---------|------|
| `/x/web-interface/view` | 视频基本信息 + 弹幕列表 | 获取视频元数据 |
| `/x/v2/dm/view` | 弹幕数据 + **CC字幕/AI字幕** | 获取字幕内容 |

### 知识点：B站API结构
```python
# ❌ 错误的API（返回弹幕）
view_url = "https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
view_data['data']['subtitle']  # 这个字段可能包含弹幕而非字幕

# ✅ 正确的API（返回CC字幕/AI字幕）
dm_url = "https://api.bilibili.com/x/v2/dm/view?aid={aid}&oid={cid}&type=1"
dm_data['data']['subtitle']['subtitles']  # 真正的字幕列表
```

### 修复方案
1. 先调用 `web-interface/view` 获取 `aid` 和 `cid`
2. 再调用 `dm/view` 获取字幕列表
3. 从 `subtitle_url` 下载实际的字幕JSON文件

### 技术要点
- **API调用链**：需要两步调用才能获取字幕
- **数据结构**：字幕URL需要拼接 `https:` 前缀
- **字幕格式**：B站字幕JSON格式为 `{"body": [{"from": 0.0, "to": 3.0, "content": "文本"}]}`

---

## 问题2：B站视频下载失败 - API返回异常

### 问题描述
下载B站视频时偶尔报错："B站API返回异常，可能是网络波动或限流"

### 根本原因
**B站API限流机制**：
1. B站对API请求有频率限制
2. JSON解析失败通常是因为API返回了限流页面而非正常JSON
3. 网络波动导致请求超时

### 知识点：网络请求重试策略

#### 指数退避（Exponential Backoff）
```python
'retry_sleep_functions': {
    'http': lambda n: min(10, n * 2),      # 2, 4, 6, 8, 10秒
    'fragment': lambda n: min(5, n),       # 1, 2, 3, 4, 5秒
    'file_access': lambda n: min(5, n * 2),
}
```

#### 关键参数配置
| 参数 | 原值 | 新值 | 说明 |
|------|------|------|------|
| `retries` | 10 | 15 | 总重试次数 |
| `fragment_retries` | 10 | 15 | 分片重试次数 |
| `socket_timeout` | 120 | 180 | 超时时间（秒） |
| `concurrent_fragment_downloads` | - | 2 | 降低并发避免限流 |

### 修复方案
1. 增加重试次数和超时时间
2. 实现指数退避策略
3. 降低并发下载数量
4. 提供更友好的错误提示

---

## 问题3：思维导图PNG导出失败 - CORS错误

### 问题描述
导出思维导图为PNG时报错：`Failed to execute 'toBlob' on 'HTMLCanvasElement': Tainted canvases may not be exported`

### 根本原因
**Canvas污染（Tainted Canvas）**：浏览器安全机制

当Canvas绘制了跨域资源后，会被标记为"污染"，禁止导出。

### 知识点：CORS和Canvas安全

#### Canvas污染触发条件
```javascript
// ❌ 会触发Canvas污染的情况
const img = new Image()
img.src = 'https://other-domain.com/image.png'  // 跨域图片
ctx.drawImage(img, 0, 0)
canvas.toBlob()  // 报错：Tainted canvas

// ❌ Blob URL也可能被浏览器视为潜在跨域资源
const svgBlob = new Blob([svgData], {type: 'image/svg+xml'})
const svgUrl = URL.createObjectURL(svgBlob)
img.src = svgUrl  // 可能触发CORS检查
```

#### Data URL的优势
```javascript
// ✅ Data URL不会触发CORS检查
const svgBase64 = btoa(unescape(encodeURIComponent(svgData)))
const svgDataUrl = `data:image/svg+xml;base64,${svgBase64}`
img.src = svgDataUrl  // 安全，同源
```

### 修复方案
1. 将SVG转换为Base64编码的Data URL
2. 设置 `img.crossOrigin = 'anonymous'`
3. 移除不必要的Blob URL清理

### 技术要点
```javascript
// 修复前（使用Blob URL）
const svgBlob = new Blob([svgData], {type: 'image/svg+xml'})
const svgUrl = URL.createObjectURL(svgBlob)  // 可能触发CORS

// 修复后（使用Data URL）
const svgBase64 = btoa(unescape(encodeURIComponent(svgData)))
const svgDataUrl = `data:image/svg+xml;base64,${svgBase64}`  // 安全
```

---

## 相关技术知识点

### 1. 同源策略（Same-Origin Policy）
- 浏览器安全机制，限制跨域资源访问
- Canvas导出、Cookie访问等受此策略限制

### 2. CORS（Cross-Origin Resource Sharing）
- 允许服务器声明哪些源可以访问资源
- `crossOrigin = 'anonymous'` 表示不带凭据的请求

### 3. Data URL vs Blob URL
| 特性 | Data URL | Blob URL |
|------|----------|----------|
| 格式 | `data:[<mediatype>][;base64],<data>` | `blob:<origin>/<uuid>` |
| 同源性 | 总是同源 | 继承创建时的origin |
| 大小限制 | 较小 | 较大 |
| 适用场景 | 小图片、SVG | 大文件、二进制数据 |

### 4. API限流处理
- 指数退避：重试间隔逐渐增加
- 降低并发：减少同时请求数
- 超时配置：给予足够的响应时间

---

## 最佳实践总结

### B站API调用
1. 优先使用官方API而非爬虫
2. 遵守API调用频率限制
3. 实现合理的重试机制

### 前端图片处理
1. 优先使用Data URL处理小图片
2. 设置正确的crossOrigin属性
3. 避免Canvas被跨域资源污染

### 错误处理
1. 提供友好的错误提示
2. 给出具体的解决建议
3. 记录详细的错误日志

---

## 代码变更文件

| 文件 | 修改内容 |
|------|---------|
| `backend/subtitle_extractor.py` | 修复B站字幕API调用 |
| `backend/app.py` | 优化B站下载重试机制 |
| `frontend/src/views/VideoDownload.vue` | 修复PNG导出CORS问题 |
