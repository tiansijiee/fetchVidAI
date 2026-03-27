/**
 * 认证管理模块
 * 负责 Token 存储、用户状态管理、登录登出逻辑
 */

import { getFingerprint } from '../utils/fingerprint'

const TOKEN_KEY = 'fetchvid_token'
const USER_KEY = 'fetchvid_user'
const USAGE_KEY = 'fetchvid_usage'
const QUOTA_KEY = 'fetchvid_quota'  // 新增：剩余次数缓存

/**
 * 认证管理类
 */
class AuthManager {
  constructor() {
    this.token = this.getToken()
    this.user = this.getUser()
    this.usage = this.getUsage()
    this.quota = this.getQuota()  // 新增：获取剩余次数
    this.listeners = new Set()
  }

  /**
   * 获取存储的 Token
   */
  getToken() {
    return localStorage.getItem(TOKEN_KEY)
  }

  /**
   * 存储 Token
   */
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
    this.token = token
    this._notifyListeners()
  }

  /**
   * 获取用户信息
   */
  getUser() {
    const userStr = localStorage.getItem(USER_KEY)
    return userStr ? JSON.parse(userStr) : null
  }

  /**
   * 存储用户信息
   */
  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    this.user = user
    this._notifyListeners()
  }

  /**
   * 获取使用情况
   */
  getUsage() {
    const usageStr = localStorage.getItem(USAGE_KEY)
    return usageStr ? JSON.parse(usageStr) : null
  }

  /**
   * 存储使用情况
   */
  setUsage(usage) {
    localStorage.setItem(USAGE_KEY, JSON.stringify(usage))
    this.usage = usage
  }

  /**
   * 获取剩余次数配额
   */
  getQuota() {
    const quotaStr = localStorage.getItem(QUOTA_KEY)
    return quotaStr ? JSON.parse(quotaStr) : null
  }

  /**
   * 存储剩余次数配额
   */
  setQuota(quota) {
    localStorage.setItem(QUOTA_KEY, JSON.stringify(quota))
    this.quota = quota
  }

  /**
   * 登录
   */
  async login(email, password) {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (response.ok) {
        this.setToken(data.token)
        this.setUser(data.user)
        this.setUsage(data.usage)
        this.setQuota(data.quota || null)  // 新增：设置配额
        return { success: true, user: data.user }
      } else {
        return { success: false, error: data.error || '登录失败' }
      }
    } catch (error) {
      return { success: false, error: '网络错误，请稍后重试' }
    }
  }

  /**
   * 注册
   */
  async register(email, password) {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (response.ok) {
        return { success: true, message: data.message }
      } else {
        return { success: false, error: data.error || '注册失败' }
      }
    } catch (error) {
      return { success: false, error: '网络错误，请稍后重试' }
    }
  }

  /**
   * 登出
   */
  logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(USAGE_KEY)
    localStorage.removeItem(QUOTA_KEY)  // 新增：清除配额
    this.token = null
    this.user = null
    this.usage = null
    this.quota = null
    this._notifyListeners()
  }

  /**
   * 检查是否已登录
   */
  isAuthenticated() {
    return !!this.token && !!this.user
  }

  /**
   * 检查是否是会员
   */
  isPremium() {
    return this.user?.role === 'premium'
  }

  /**
   * 获取用户角色
   */
  getRole() {
    return this.user?.role || 'guest'
  }

  /**
   * 刷新用户信息
   */
  async refreshUserInfo() {
    if (!this.token) return false

    try {
      const response = await fetch('/api/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        this.setUser(data.user)
        this.setUsage(data.usage)
        return true
      } else {
        // Token 可能过期，清除登录状态
        this.logout()
        return false
      }
    } catch (error) {
      console.error('刷新用户信息失败:', error)
      return false
    }
  }

  /**
   * 刷新使用情况
   */
  async refreshUsage() {
    if (!this.token) return false

    try {
      const response = await fetch('/api/auth/usage', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        this.setUsage(data.usage)

         this._notifyListeners()
        return true
      }
      return false
    } catch (error) {
      console.error('刷新使用情况失败:', error)
      return false
    }
  }

  /**
   * 刷新剩余次数配额（支持游客和登录用户）
   */
  async refreshQuota() {
    try {
      const fingerprint = getFingerprint()
      const headers = {
        'X-Fingerprint': fingerprint
      }

      // 如果已登录，添加token
      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`
      }

      const response = await fetch('/api/quota/remaining', {
        method: 'GET',
        headers
      })

      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          this.setQuota(result.data)
          this._notifyListeners()
          return true
        }
      }
      return false
    } catch (error) {
      console.error('刷新剩余次数失败:', error)
      return false
    }
  }

  /**
   * 检查权限
   */
  async checkPermission(action) {
    if (!this.token) {
      // 游客模式
      const guestLimits = {
        download: 2,
        summary: 1,
        qa: 3
      }
      return {
        allowed: true,
        remaining: guestLimits[action] || 0,
        limit: guestLimits[action] || 0
      }
    }

    try {
      const response = await fetch('/api/auth/check-permission', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      })

      if (response.ok) {
        const data = await response.json()
        return data
      } else {
        return { allowed: false, message: '权限检查失败' }
      }
    } catch (error) {
      return { allowed: false, message: '网络错误' }
    }
  }

  /**
   * 添加状态监听器
   */
  addListener(callback) {
    this.listeners.add(callback)
    return () => this.listeners.delete(callback)
  }

  /**
   * 通知所有监听器
   */
  _notifyListeners() {
    this.listeners.forEach(callback => {
      callback({
        isAuthenticated: this.isAuthenticated(),
        user: this.user,
        role: this.getRole(),
        isPremium: this.isPremium()
      })
    })
  }

  /**
   * 获取会员到期时间
   */
  getMembershipExpire() {
    if (!this.user?.membership_expire) return null
    return new Date(this.user.membership_expire)
  }

  /**
   * 检查会员是否有效
   */
  isMembershipValid() {
    if (!this.isPremium()) return false
    if (!this.user?.membership_expire) return true // 永久会员

    const expireTime = this.getMembershipExpire()
    return expireTime > new Date()
  }
}

// 创建全局实例
const auth = new AuthManager()

export default auth
