<template>
  <div class="user-menu">
    <!-- 未登录状态 -->
    <template v-if="!isLoggedIn">
      <button
        @click="showLoginDialog = true"
        class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-all duration-200 shadow-md shadow-blue-500/30 hover:shadow-lg hover:shadow-blue-500/40"
      >
        登录 / 注册
      </button>
    </template>

    <!-- 已登录状态 - 悬浮卡片式菜单 -->
    <template v-else>
      <el-dropdown trigger="click" @command="handleCommand" class="user-dropdown">
        <div class="flex items-center space-x-3 cursor-pointer bg-white/80 backdrop-blur-sm hover:bg-white rounded-xl px-4 py-2.5 transition-all duration-200 shadow-sm hover:shadow-md border border-gray-200/50">
          <!-- 用户头像 -->
          <div class="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-medium shadow-md">
            {{ userInitial }}
          </div>

          <!-- 用户信息 -->
          <div class="hidden md:block text-left">
            <div class="text-sm font-semibold text-gray-800 flex items-center gap-2">
              {{ auth.user?.email }}
              <span v-if="auth.isPremium()" class="text-xs bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-2 py-0.5 rounded-full font-medium">VIP</span>
            </div>
            <div class="text-xs text-gray-500">{{ roleText }}</div>
          </div>

          <!-- 下拉图标 -->
          <el-icon class="text-gray-400">
            <ArrowDown />
          </el-icon>
        </div>

        <template #dropdown>
          <el-dropdown-menu class="custom-dropdown-menu">
            <!-- 用户信息卡片 -->
            <div class="p-4 border-b border-gray-100">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-medium">
                  {{ userInitial }}
                </div>
                <div class="flex-1">
                  <div class="text-sm font-semibold text-gray-800 truncate max-w-[150px]">{{ auth.user?.email }}</div>
                  <div class="text-xs text-gray-500">{{ roleText }}</div>
                  <div v-if="auth.isMembershipValid()" class="text-xs text-purple-600 mt-1">
                    会员到期: {{ formatDate(auth.user?.membership_expire) }}
                  </div>
                </div>
              </div>

              <!-- 使用次数进度条 -->
              <div v-if="!auth.isPremium()" class="space-y-3">
                <div>
                  <div class="flex justify-between text-xs mb-1.5">
                    <span class="text-gray-600">解析次数</span>
                    <span :class="getQuotaClass('parse')" class="font-medium">{{ getQuotaText('parse') }}</span>
                  </div>
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-300"
                      :class="getProgressBarClass('parse')"
                      :style="{ width: getProgressBarWidth('parse') }"
                    ></div>
                  </div>
                </div>
                <div>
                  <div class="flex justify-between text-xs mb-1.5">
                    <span class="text-gray-600">下载次数</span>
                    <span :class="getQuotaClass('download')" class="font-medium">{{ getQuotaText('download') }}</span>
                  </div>
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-300"
                      :class="getProgressBarClass('download')"
                      :style="{ width: getProgressBarWidth('download') }"
                    ></div>
                  </div>
                </div>
                <!-- 次数不足提示 -->
                <div v-if="isQuotaLow" class="mt-3 p-2 bg-orange-50 border border-orange-200 rounded-lg">
                  <p class="text-xs text-orange-700">次数即将用完，<span class="font-semibold">升级VIP</span>无限使用</p>
                </div>
              </div>
              <div v-else class="mt-3 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
                  </svg>
                  <span class="text-xs text-purple-700 font-medium">VIP 会员，无限使用</span>
                </div>
              </div>
            </div>

            <!-- 菜单项 -->
            <div v-if="!auth.isPremium()" class="py-2 border-t border-gray-100">
              <el-dropdown-item @click="handleUpgrade" class="menu-item-upgrade">
                <el-icon class="mr-2"><Star /></el-icon>
                升级会员
              </el-dropdown-item>
            </div>

            <div v-else class="py-2 border-t border-gray-100">
              <el-dropdown-item @click="handleUpgrade">
                <el-icon class="mr-2"><RefreshRight /></el-icon>
                续费会员
              </el-dropdown-item>
            </div>

            <el-dropdown-item @click="showHistoryDialog = true" class="py-3">
              <el-icon class="mr-2"><Tickets /></el-icon>
              支付历史
            </el-dropdown-item>

            <div class="border-t border-gray-100 py-2">
              <el-dropdown-item @click="handleLogout" class="text-red-600">
                <el-icon class="mr-2"><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </div>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </template>

    <!-- 登录弹窗 - 优化样式 -->
    <el-dialog
      v-model="showLoginDialog"
      :title="null"
      width="420px"
      :center="true"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      append-to-body
      class="login-dialog"
    >
      <div class="p-6">
        <!-- 标题 -->
        <div class="text-center mb-6">
          <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ loginMode ? '欢迎回来' : '创建账户' }}</h3>
          <p class="text-sm text-gray-500">{{ loginMode ? '登录以继续使用' : '注册享受更多功能' }}</p>
        </div>

        <!-- 切换标签 -->
        <div class="flex bg-gray-100 rounded-xl p-1 mb-6">
          <button
            @click="loginMode = true"
            :class="[
              'flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all duration-200',
              loginMode ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-800'
            ]"
          >
            登录
          </button>
          <button
            @click="loginMode = false"
            :class="[
              'flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all duration-200',
              !loginMode ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-800'
            ]"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <el-form v-if="loginMode" :model="loginForm" label-position="top">
          <el-form-item label="邮箱">
            <el-input
              v-model="loginForm.email"
              type="email"
              placeholder="请输入邮箱"
              size="large"
              class="custom-input"
            />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              show-password
              size="large"
              class="custom-input"
            />
          </el-form-item>
        </el-form>

        <!-- 注册表单 -->
        <el-form v-else :model="registerForm" label-position="top">
          <el-form-item label="邮箱">
            <el-input
              v-model="registerForm.email"
              type="email"
              placeholder="请输入邮箱"
              size="large"
              class="custom-input"
            />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="至少6位"
              show-password
              size="large"
              class="custom-input"
            />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="再次输入密码"
              show-password
              size="large"
              class="custom-input"
            />
          </el-form-item>
        </el-form>

        <!-- 权限说明 - 底部小字灰色 -->
        <div class="mt-6 pt-4 border-t border-gray-200">
          <p class="text-xs text-gray-500 mb-2">权限说明：</p>
          <div class="grid grid-cols-3 gap-2 text-xs text-gray-400">
            <div class="flex items-center gap-1">
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
              游客: 1次/日
            </div>
            <div class="flex items-center gap-1">
              <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              注册: 3次/日
            </div>
            <div class="flex items-center gap-1">
              <span class="w-1.5 h-1.5 bg-purple-500 rounded-full"></span>
              会员: 无限
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="px-6 pb-6 flex gap-3">
          <el-button @click="showLoginDialog.value = false" class="flex-1" size="large">取消</el-button>
          <el-button
            type="primary"
            @click="handleAuthAction"
            :loading="authLoading"
            class="flex-1"
            size="large"
          >
            {{ loginMode ? '登录' : '注册' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 支付历史弹窗 -->
    <el-dialog
      v-model="showHistoryDialog"
      title="支付历史"
      width="600px"
      :center="true"
      :destroy-on-close="true"
      append-to-body
    >
      <el-table :data="paymentHistory" v-loading="historyLoading" stripe>
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            ¥{{ (row.amount / 100).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="currency" label="货币" width="60" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" />
      </el-table>

      <template #footer>
        <el-button @click="showHistoryDialog.value = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, Star, RefreshRight, Tickets, SwitchButton } from '@element-plus/icons-vue'
import auth from '../auth/auth'

const router = useRouter()
const showLoginDialog = ref(false)
const showHistoryDialog = ref(false)
const loginMode = ref(true)
const authLoading = ref(false)
const historyLoading = ref(false)
const paymentHistory = ref([])

// 强制刷新触发器
const refresh = ref(0)

const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ email: '', password: '', confirmPassword: '' })

// 实时响应 auth 状态变化
const isLoggedIn = computed(() => {
  refresh.value
  return auth.isAuthenticated()
})

const roleText = computed(() => {
  refresh.value
  const role = auth.getRole()
  const roleMap = { guest: '游客', user: '注册用户', premium: '会员用户' }
  return roleMap[role] || '未知'
})

const userInitial = computed(() => {
  refresh.value
  const email = auth.user?.email || ''
  return email.charAt(0).toUpperCase()
})

// 判断是否次数不足
const isQuotaLow = computed(() => {
  if (auth.isPremium()) return false
  const quota = auth.quota
  if (quota) {
    const parseRem = quota.parse_remaining
    const downloadRem = quota.download_remaining
    if (typeof parseRem === 'number' && parseRem <= 1) return true
    if (typeof downloadRem === 'number' && downloadRem <= 1) return true
  }
  return false
})

// 获取进度条宽度
const getProgressBarWidth = (type) => {
  if (auth.isPremium()) return '100%'
  const quota = auth.quota
  if (quota) {
    const remaining = quota[`${type}_remaining`]
    const limit = quota[`${type}_limit`] || 3
    if (typeof remaining === 'number') {
      return `${(remaining / limit) * 100}%`
    }
  }
  return '0%'
}

// 获取进度条颜色类
const getProgressBarClass = (type) => {
  if (auth.isPremium()) return 'bg-gradient-to-r from-purple-500 to-pink-500'
  const quota = auth.quota
  if (quota) {
    const remaining = quota[`${type}_remaining`]
    if (typeof remaining === 'number') {
      if (remaining === 0) return 'bg-red-500'
      if (remaining === 1) return 'bg-orange-500'
      return 'bg-gradient-to-r from-blue-500 to-purple-500'
    }
  }
  return 'bg-gradient-to-r from-blue-500 to-purple-500'
}

// 处理命令
const handleCommand = (command) => {
  switch (command) {
    case 'upgrade': handleUpgrade(); break
    case 'history': showHistoryDialog.value = true; loadPaymentHistory(); break
    case 'logout': handleLogout(); break
  }
}

// 处理登录/注册
const handleAuthAction = async () => {
  if (loginMode.value) {
    if (!loginForm.value.email || !loginForm.value.password) {
      ElMessage.warning('请填写邮箱和密码')
      return
    }
    authLoading.value = true
    try {
      const result = await auth.login(loginForm.value.email, loginForm.value.password)
      if (result.success) {
        ElMessage.success('登录成功')
        showLoginDialog.value = false
        loginForm.value = { email: '', password: '' }
      } else {
        ElMessage.error(result.error)
      }
    } finally { authLoading.value = false }
  } else {
    if (!registerForm.value.email || !registerForm.value.password) {
      ElMessage.warning('请填写邮箱和密码')
      return
    }
    if (registerForm.value.password.length < 6) {
      ElMessage.warning('密码至少6位')
      return
    }
    if (registerForm.value.password !== registerForm.value.confirmPassword) {
      ElMessage.warning('两次密码不一致')
      return
    }
    authLoading.value = true
    try {
      const result = await auth.register(registerForm.value.email, registerForm.value.password)
      if (result.success) {
        ElMessage.success('注册成功')
        loginMode.value = true
        loginForm.value.email = registerForm.value.email
        registerForm.value = { email: '', password: '', confirmPassword: '' }
      } else {
        ElMessage.error(result.error)
      }
    } finally { authLoading.value = false }
  }
}

// 处理登出
const handleLogout = () => {
  auth.logout()
  ElMessage.success('已退出登录')
}

// 处理升级
const handleUpgrade = () => {
  router.push('/upgrade')
}

// 加载支付历史
const loadPaymentHistory = async () => {
  historyLoading.value = true
  try {
    const res = await fetch('/api/payment/history', {
      headers: { Authorization: `Bearer ${auth.getToken()}` }
    })
    if (res.ok) paymentHistory.value = (await res.json()).payments || []
  } finally { historyLoading.value = false }
}

// 获取剩余次数文本
const getQuotaText = (type) => {
  refresh.value

  // VIP用户无限
  if (auth.isPremium()) return '无限'

  // 优先使用quota数据
  const quota = auth.quota
  if (quota) {
    const remaining = quota[`${type}_remaining`]
    if (remaining === '无限') return '无限'
    if (typeof remaining === 'number') {
      const limit = quota[`${type}_limit`] || (auth.getRole() === 'guest' ? 1 : 3)
      return `${remaining}/${limit}`
    }
  }

  // 降级：使用旧的usage数据
  const count = auth.usage?.[`${type}_count`] || 0
  const limit = auth.getRole() === 'guest' ? 1 : 3
  return `${Math.max(0, limit - count)}/${limit}`
}

const getQuotaClass = (type) => {
  refresh.value

  // VIP用户紫色
  if (auth.isPremium()) return 'text-purple-600'

  // 优先使用quota数据
  const quota = auth.quota
  if (quota) {
    const remaining = quota[`${type}_remaining`]
    if (remaining === '无限') return 'text-purple-600'
    if (typeof remaining === 'number') {
      if (remaining === 0) return 'text-red-600'
      if (remaining === 1) return 'text-orange-500'
      return 'text-green-600'
    }
  }

  // 降级：使用旧的usage数据
  const count = auth.usage?.[`${type}_count`] || 0
  const limit = auth.getRole() === 'guest' ? 1 : 3
  const rem = Math.max(0, limit - count)
  if (rem === 0) return 'text-red-600'
  if (rem === 1) return 'text-orange-500'
  return 'text-green-600'
}

// 格式化日期
const formatDate = (s) => s ? new Date(s).toLocaleDateString('zh-CN') : ''

// 状态
const getStatusType = (s) => ({ succeeded: 'success', pending: 'warning', failed: 'danger' }[s] || 'info')
const getStatusText = (s) => ({ succeeded: '成功', pending: '处理中', failed: '失败', canceled: '已取消' }[s] || s)

// 订阅 auth 状态更新
let removeListener = null

onMounted(() => {
  removeListener = auth.addListener(() => {
    refresh.value++
  })

  // 刷新剩余次数
  auth.refreshQuota()

  // 事件监听
  const a = () => showLoginDialog.value = true
  const b = handleUpgrade
  window.addEventListener('auth:login-required', a)
  window.addEventListener('auth:upgrade-required', b)
  onUnmounted(() => {
    window.removeEventListener('auth:login-required', a)
    window.removeEventListener('auth:upgrade-required', b)
    if (removeListener) removeListener()
  })
})

onUnmounted(() => {
  if (removeListener) removeListener()
})
</script>

<style scoped>
.user-menu :deep(.el-dropdown-menu__item.user-info-item),
.user-menu :deep(.el-dropdown-menu__item.usage-item) { cursor: default; }
.user-menu :deep(.el-dropdown-menu__item.user-info-item:hover),
.user-menu :deep(.el-dropdown-menu__item.usage-item:hover) { background: transparent; }

/* 自定义下拉菜单样式 */
:deep(.custom-dropdown-menu) {
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  padding: 8px;
}

:deep(.custom-dropdown-menu .el-dropdown-menu__item) {
  border-radius: 8px;
  padding: 10px 16px;
  margin: 0;
  transition: all 0.2s;
}

:deep(.custom-dropdown-menu .el-dropdown-menu__item:hover) {
  background-color: rgba(59, 130, 246, 0.05);
}

:deep(.custom-dropdown-menu .menu-item-upgrade) {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(219, 39, 119, 0.1) 100%);
  color: #9333ea;
  font-weight: 600;
}

/* 登录弹窗样式 */
:deep(.login-dialog .el-dialog) {
  border-radius: 20px;
}

:deep(.login-dialog .el-dialog__header) {
  padding: 0;
}

:deep(.login-dialog .el-dialog__body) {
  padding: 0;
}

:deep(.login-dialog .el-dialog__footer) {
  padding: 0;
  border-top: 1px solid #f3f4f6;
}

/* 自定义输入框样式 */
:deep(.custom-input .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

:deep(.custom-input .el-input__wrapper:hover) {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
}

/* 按钮样式 */
:deep(.login-dialog .el-button--primary) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.2s;
}

:deep(.login-dialog .el-button--primary:hover) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
</style>