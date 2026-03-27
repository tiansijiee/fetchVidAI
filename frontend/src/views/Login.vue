<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">FetchVid AI</h1>
        <p class="text-gray-600 mt-2">智能视频下载与分析平台</p>
      </div>

      <!-- 登录/注册卡片 -->
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <!-- Tab 切换 -->
        <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            @click="isLogin = true"
            :class="[
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all',
              isLogin ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-800'
            ]"
          >
            登录
          </button>
          <button
            @click="isLogin = false"
            :class="[
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all',
              !isLogin ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-800'
            ]"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <form v-if="isLogin" @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
            <input
              v-model="loginForm.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="请输入邮箱"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="loginForm.password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="请输入密码"
            >
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- 注册表单 -->
        <form v-else @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
            <input
              v-model="registerForm.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="请输入邮箱"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="registerForm.password"
              type="password"
              required
              minlength="6"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="请输入密码（至少6位）"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
            <input
              v-model="registerForm.confirmPassword"
              type="password"
              required
              minlength="6"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="请再次输入密码"
            >
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>

        <!-- 权限说明 -->
        <div class="mt-6 pt-6 border-t border-gray-200">
          <p class="text-sm text-gray-600 mb-3 font-medium">使用权限对比</p>
          <div class="space-y-2 text-xs">
            <div class="flex justify-between">
              <span class="text-gray-500">视频下载</span>
              <span class="text-gray-700">游客 2次/日 | 注册用户 5次/日</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">AI 总结</span>
              <span class="text-gray-700">游客 1次/日 | 注册用户 3次/日</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">AI 问答</span>
              <span class="text-gray-700">游客 3轮/日 | 注册用户 10轮/日</span>
            </div>
            <div class="flex justify-between text-blue-600">
              <span>会员用户</span>
              <span>无限使用 + 高级功能</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 返回首页 -->
      <div class="text-center mt-6">
        <router-link
          to="/"
          class="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          ← 返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import auth from '../auth/auth'

const router = useRouter()
const isLogin = ref(true)
const loading = ref(false)

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  email: '',
  password: '',
  confirmPassword: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    const result = await auth.login(loginForm.value.email, loginForm.value.password)

    if (result.success) {
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error(result.error)
    }
  } catch (error) {
    ElMessage.error('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  // 验证密码
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  if (registerForm.value.password.length < 6) {
    ElMessage.error('密码长度至少为6位')
    return
  }

  loading.value = true
  try {
    const result = await auth.register(
      registerForm.value.email,
      registerForm.value.password
    )

    if (result.success) {
      ElMessage.success('注册成功，请登录')
      isLogin.value = true
      loginForm.value.email = registerForm.value.email
      registerForm.value = {
        email: '',
        password: '',
        confirmPassword: ''
      }
    } else {
      ElMessage.error(result.error)
    }
  } catch (error) {
    ElMessage.error('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>
