/**
 * 浏览器指纹生成工具
 * 生成稳定的浏览器指纹，用于游客身份识别
 */

const FP_KEY = 'fetchvid_fp'

/**
 * 生成稳定的浏览器指纹
 * 基于浏览器特征生成，不使用随机UUID，确保同一浏览器多次访问生成相同的指纹
 */
export function generateFingerprint() {
  // 尝试从localStorage获取已有的指纹
  let fp = localStorage.getItem(FP_KEY)

  if (fp) {
    return fp
  }

  // 生成新的指纹
  const components = [
    // 用户代理
    navigator.userAgent,
    // 语言
    navigator.language,
    // 平台
    navigator.platform,
    // 屏幕分辨率
    `${screen.width}x${screen.height}x${screen.colorDepth}`,
    // 时区
    new Date().getTimezoneOffset().toString(),
    // Canvas指纹（可选）
    getCanvasFingerprint(),
    // WebGL指纹（可选）
    getWebGLFingerprint()
  ]

  // 组合所有特征并生成base64编码
  fp = btoa(components.join('|'))

  // 存储到localStorage
  localStorage.setItem(FP_KEY, fp)

  return fp
}

/**
 * 获取Canvas指纹
 */
function getCanvasFingerprint() {
  try {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (!ctx) return ''

    // 绘制一些文本
    ctx.textBaseline = 'top'
    ctx.font = '14px Arial'
    ctx.fillText('FetchVid Fingerprint', 2, 2)

    // 获取canvas数据
    const dataURL = canvas.toDataURL()
    return dataURL.slice(-50) // 只取最后50个字符
  } catch (e) {
    return ''
  }
}

/**
 * 获取WebGL指纹
 */
function getWebGLFingerprint() {
  try {
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
    if (!gl) return ''

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
    const renderer = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : ''

    return renderer.slice(0, 50) // 只取前50个字符
  } catch (e) {
    return ''
  }
}

/**
 * 获取指纹（带缓存）
 */
export function getFingerprint() {
  return generateFingerprint()
}

/**
 * 清除指纹（仅用于测试）
 */
export function clearFingerprint() {
  localStorage.removeItem(FP_KEY)
}

/**
 * 获取指纹的简短显示（用于调试）
 */
export function getFingerprintShort() {
  const fp = getFingerprint()
  return fp ? `${fp.substring(0, 8)}...` : 'unknown'
}

export default {
  generateFingerprint,
  getFingerprint,
  clearFingerprint,
  getFingerprintShort
}
