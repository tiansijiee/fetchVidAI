/**
 * Axios 实例配置
 * 包含请求/响应拦截器，自动处理 Token 和错误
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'
import auth from './auth'
import { getFingerprint } from '../utils/fingerprint'

/**
 * 生成请求ID（用于幂等检查）
 */
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`
}

/**
 * 创建 Axios 实例
 */
const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 * 自动添加 Authorization、X-Fingerprint、X-Request-ID 头
 */
api.interceptors.request.use(
  (config) => {
    // 添加Authorization头
    const token = auth.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加X-Fingerprint头（所有请求）
    const fingerprint = getFingerprint()
    if (fingerprint) {
      config.headers['X-Fingerprint'] = fingerprint
    }

    // 添加X-Request-ID头（用于幂等检查）
    config.headers['X-Request-ID'] = generateRequestId()

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 处理认证错误和权限限制
 */
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const { response } = error

    if (!response) {
      // 网络错误
      ElMessage.error('网络连接失败，请检查网络设置')
      return Promise.reject(error)
    }

    const { status, data } = response

    switch (status) {
      case 401:
        // 未认证或 Token 过期
        if (data.code === 'AUTH_REQUIRED' || data.require_login) {
          // 需要登录
          ElMessage.warning('请先登录')
          // 触发登录弹窗事件
          window.dispatchEvent(new CustomEvent('auth:login-required'))
        } else {
          // Token 无效，清除登录状态
          auth.logout()
          ElMessage.error('登录已过期，请重新登录')
          window.dispatchEvent(new CustomEvent('auth:logout'))
        }
        break

      case 403:
        // 权限不足
        if (data.code === 'RATE_LIMIT_EXCEEDED') {
          // 次数限制
          if (data.require_login || data.user_role === 'guest') {
            ElMessage.warning(`${data.error}，登录后可获得更多次数`)
            window.dispatchEvent(new CustomEvent('auth:login-required'))
          } else {
            ElMessage.error(data.error)
            window.dispatchEvent(new CustomEvent('auth:upgrade-required', {
              detail: data.info
            }))
          }
        } else if (data.code === 'ROLE_REQUIRED') {
          // 角色要求
          ElMessage.error(data.error)
          window.dispatchEvent(new CustomEvent('auth:upgrade-required', {
            detail: { require_role: data.require_role }
          }))
        } else {
          ElMessage.error(data.error || '权限不足')
        }
        break

      case 429:
        // 请求过于频繁
        ElMessage.error('请求过于频繁，请稍后再试')
        break

      case 500:
        // 服务器错误
        ElMessage.error('服务器错误，请稍后重试')
        break

      default:
        // 其他错误
        if (data.error) {
          ElMessage.error(data.error)
        }
    }

    return Promise.reject(error)
  }
)

/**
 * API 请求辅助函数
 */
export const apiRequest = {
  /**
   * 视频解析
   */
  async parseVideo(url) {
    return api.post('/parse', { url })
  },

  /**
   * 启动下载
   */
  async startDownload(videoInfo, options = {}) {
    return api.post('/proxy/download', {
      video_info: videoInfo,
      options
    })
  },

  /**
   * 获取下载状态
   */
  async getDownloadStatus(taskId) {
    return api.get(`/proxy/download/status/${taskId}`)
  },

  /**
   * AI 总结
   */
  async aiSummarize(url, options = {}) {
    return api.post('/ai/summarize', { url, ...options })
  },

  /**
   * 提取字幕
   */
  async extractSubtitles(url, lang = 'zh-Hans') {
    return api.post('/ai/subtitles', { url, lang })
  },

  /**
   * 生成思维导图
   */
  async generateMindmap(content) {
    return api.post('/ai/mindmap', { content })
  },

  /**
   * AI 问答
   */
  async aiAsk(question, context = {}) {
    return api.post('/ai/ask', { question, context })
  },

  /**
   * 导出思维导图
   */
  async exportMindmap(data, format = 'md') {
    return api.post('/ai/export', { data, format }, {
      responseType: format === 'pdf' ? 'blob' : 'json'
    })
  },

  /**
   * 登录
   */
  async login(email, password) {
    return api.post('/auth/login', { email, password })
  },

  /**
   * 注册
   */
  async register(email, password) {
    return api.post('/auth/register', { email, password })
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser() {
    return api.get('/auth/me')
  },

  /**
   * 获取使用情况
   */
  async getUsage() {
    return api.get('/auth/usage')
  },

  /**
   * 检查权限
   */
  async checkPermission(action) {
    return api.post('/auth/check-permission', { action })
  },

  /**
   * 获取会员套餐
   */
  async getPlans() {
    return api.get('/payment/plans')
  },

  /**
   * 创建支付意图
   */
  async createPaymentIntent(planType) {
    return api.post('/payment/create-intent', { plan_type: planType })
  },

  /**
   * 确认支付
   */
  async confirmPayment(paymentIntentId) {
    return api.post('/payment/confirm', { payment_intent_id: paymentIntentId })
  },

  /**
   * 获取支付历史
   */
  async getPaymentHistory() {
    return api.get('/payment/history')
  }
}

/**
 * 权限检查辅助函数
 */
export const checkPermission = async (action) => {
  try {
    const response = await apiRequest.checkPermission(action)
    return response.data
  } catch (error) {
    return { allowed: false, message: '权限检查失败' }
  }
}

/**
 * 获取剩余次数显示文本
 */
export const getRemainingText = (usage, action) => {
  const countKey = `${action}_count`
  const count = usage?.[countKey] || 0

  const role = auth.getRole()
  const limits = {
    guest: { download: 2, summary: 1, qa: 3 },
    user: { download: 5, summary: 3, qa: 10 },
    premium: { download: -1, summary: -1, qa: -1 }
  }

  const limit = limits[role]?.[action] || 0

  if (limit === -1) {
    return '无限'
  }

  const remaining = Math.max(0, limit - count)
  return `${remaining}/${limit}`
}

export default api
