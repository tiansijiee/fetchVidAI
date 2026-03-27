<template>
  <div class="user-menu">
    <!-- 未登录状态 -->
    <template v-if="!isLoggedIn">
      <el-button @click="showLoginDialog = true" type="primary" size="small">
        登录 / 注册
      </el-button>
    </template>

    <!-- 已登录状态 -->
    <template v-else>
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="flex items-center space-x-2 cursor-pointer hover:bg-gray-100 rounded-lg px-3 py-2">
          <!-- 用户头像 -->
          <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-medium">
            {{ userInitial }}
          </div>

          <!-- 用户信息 -->
          <div class="hidden md:block text-left">
            <div class="text-sm font-medium text-gray-800">
              {{ auth.user?.email }}
              <span v-if="auth.isPremium()" class="ml-1 text-xs bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-2 py-0.5 rounded-full">VIP</span>
            </div>
            <div class="text-xs text-gray-500">{{ roleText }}</div>
          </div>

          <!-- 下拉图标 -->
          <el-icon class="text-gray-400">
            <ArrowDown />
          </el-icon>
        </div>

        <template #dropdown>
          <el-dropdown-menu>
            <!-- 用户信息 -->
            <el-dropdown-item disabled class="user-info-item">
              <div class="py-2">
                <div class="text-sm font-medium text-gray-800">{{ auth.user?.email }}</div>
                <div class="text-xs text-gray-500 mt-1">{{ roleText }}</div>
                <div v-if="auth.isMembershipValid()" class="text-xs text-purple-600 mt-1">
                  会员到期: {{ formatDate(auth.user?.membership_expire) }}
                </div>
              </div>
            </el-dropdown-item>

            <el-dropdown-item divided />

            <!-- 使用情况 -->
            <el-dropdown-item disabled class="usage-item">
              <div class="py-1 text-xs text-gray-600">
                <div class="flex justify-between">
                  <span>今日下载:</span>
                  <span :class="getUsageClass('download')">{{ getUsageText('download') }}</span>
                </div>
                <div class="flex justify-between mt-1">
                  <span>AI 总结:</span>
                  <span :class="getUsageClass('summary')">{{ getUsageText('summary') }}</span>
                </div>
                <div class="flex justify-between mt-1">
                  <span>AI 问答:</span>
                  <span :class="getUsageClass('qa')">{{ getUsageText('qa') }}</span>
                </div>
              </div>
            </el-dropdown-item>

            <el-dropdown-item divided />

            <!-- 升级会员 -->
            <el-dropdown-item v-if="!auth.isPremium()" @click="handleUpgrade" class="text-purple-600">
              <el-icon class="mr-1"><Star /></el-icon>
              升级会员
            </el-dropdown-item>

            <!-- 续费 -->
            <el-dropdown-item v-else @click="handleUpgrade">
              <el-icon class="mr-1"><RefreshRight /></el-icon>
              续费会员
            </el-dropdown-item>

            <!-- 支付历史 -->
            <el-dropdown-item @click="showHistoryDialog = true">
              <el-icon class="mr-1"><Tickets /></el-icon>
              支付历史
            </el-dropdown-item>

            <el-dropdown-item divided />

            <!-- 登出 -->
            <el-dropdown-item @click="handleLogout" class="text-red-600">
              <el-icon class="mr-1"><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </template>

    <!-- 登录弹窗 -->
    <el-dialog
      v-model="showLoginDialog"
      title="登录 / 注册"
      width="450px"
      :center="true"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      append-to-body
    >
      <div class="space-y-4">
        <div class="flex bg-gray-100 rounded-lg p-1">
          <button
            @click="loginMode = true"
            :class="[
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all',
              loginMode ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'
            ]"
          >
            登录
          </button>
          <button
            @click="loginMode = false"
            :class="[
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all',
              !loginMode ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'
            ]"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <el-form v-if="loginMode" :model="loginForm" label-width="60px">
          <el-form-item label="邮箱">
            <el-input v-model="loginForm.email" type="email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
        </el-form>

        <!-- 注册表单 -->
        <el-form v-else :model="registerForm" label-width="80px">
          <el-form-item label="邮箱">
            <el-input v-model="registerForm.email" type="email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="registerForm.password" type="password" placeholder="至少6位" show-password />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="registerForm.confirmPassword" type="password" placeholder="再次输入密码" show-password />
          </el-form-item>
        </el-form>

        <div class="text-xs text-gray-500">
          <p>权限说明：</p>
          <p>• 游客: 1次/日（下载/总结/问答）</p>
          <p>• 注册用户: 3次/日（下载/总结/问答）</p>
          <p>• 会员: 无限使用 + 高级功能</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="showLoginDialog.value = false">取消</el-button>
        <el-button type="primary" @click="handleAuthAction" :loading="authLoading">
          {{ loginMode ? '登录' : '注册' }}
        </el-button>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
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

// 🔥 强制刷新触发器（监听 auth 变化自动更新）
const refresh = ref(0)

const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ email: '', password: '', confirmPassword: '' })

// 🔥 核心：实时响应 auth 状态变化
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

// 获取使用次数
const getUsageText = (type) => {
  refresh.value
  if (auth.isPremium()) return '无限'
  const count = auth.usage?.[`${type}_count`] || 0
  // 统一配置：游客1次，用户3次
  const limit = auth.getRole() === 'guest' ? 1 : 3
  return `${Math.max(0, limit - count)}/${limit}`
}

const getUsageClass = (type) => {
  refresh.value
  if (auth.isPremium()) return 'text-purple-600'
  const count = auth.usage?.[`${type}_count`] || 0
  // 统一配置：游客1次，用户3次
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

// ==============================================
// 🔥 🔥 🔥 关键修复：订阅 auth 变化，自动刷新页面
// ==============================================
let removeListener = null

onMounted(() => {
  // 订阅 auth 状态更新
  removeListener = auth.addListener(() => {
    refresh.value++ // 只要 auth 变了，就刷新视图
  })

  // 原有事件监听
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
</style>