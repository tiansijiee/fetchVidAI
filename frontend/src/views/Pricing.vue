<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white font-sans">
    <!-- 导航栏 -->
    <header class="bg-gradient-to-r from-blue-50/90 via-white/95 to-blue-50/90 backdrop-blur-xl border-b border-blue-100/50 sticky top-0 z-50 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo区域 -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div class="flex flex-col">
              <span class="text-lg font-bold text-gray-900 leading-tight">FetchVid</span>
              <span class="text-xs text-gray-500 leading-tight">智能视频下载</span>
            </div>
          </div>

          <!-- 导航入口 -->
          <nav class="hidden lg:flex items-center gap-8">
            <router-link to="/download" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">视频下载</router-link>
            <router-link to="/pricing" class="nav-link text-base font-semibold text-blue-600">套餐价格</router-link>
            <router-link to="/features" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">功能特性</router-link>
            <router-link to="/tutorial" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">使用教程</router-link>
          </nav>

          <!-- VIP入口 & 用户菜单 -->
          <div class="flex items-center gap-3">
            <button
              @click="handleUpgrade"
              class="hidden sm:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-xl font-medium transition-all duration-200 shadow-md shadow-purple-500/30 hover:shadow-lg hover:shadow-purple-500/40 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
              </svg>
              <span>开通VIP</span>
            </button>
            <UserMenu />
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
      <!-- 标题区域 -->
      <div class="text-center mb-12 lg:mb-16">
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
          <span class="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 bg-clip-text text-transparent">选择适合您的套餐</span>
        </h1>
        <p class="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
          解锁无限使用权限，享受更多高级功能
        </p>
      </div>

      <!-- 套餐卡片 -->
      <div class="grid md:grid-cols-3 gap-6 lg:gap-8 mb-12">
        <!-- 免费版 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 lg:p-8 hover:shadow-xl transition-shadow">
          <div class="text-center mb-6">
            <h3 class="text-xl font-bold text-gray-800 mb-2">免费版</h3>
            <div class="text-4xl font-bold text-gray-900 mb-2">¥0</div>
            <p class="text-gray-500">永久免费</p>
          </div>

          <ul class="space-y-4 mb-8">
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700">每日 1 次视频解析</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700">每日 1 次视频下载</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700">支持 100+ 视频平台</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-gray-300 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-400">AI 智能总结</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-gray-300 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-400">AI 问答功能</span>
            </li>
          </ul>

          <button
            @click="goToDownload"
            class="w-full py-3 px-6 border-2 border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
          >
            开始使用
          </button>
        </div>

        <!-- 月度会员 - 推荐 -->
        <div class="bg-white rounded-2xl shadow-xl border-2 border-blue-500 p-6 lg:p-8 relative hover:shadow-2xl transition-shadow">
          <div class="absolute -top-4 left-1/2 transform -translate-x-1/2">
            <span class="bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm px-4 py-1 rounded-full font-medium shadow-lg">最受欢迎</span>
          </div>

          <div class="text-center mb-6">
            <h3 class="text-xl font-bold text-gray-800 mb-2">月度会员</h3>
            <div class="flex items-baseline justify-center gap-1">
              <span class="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">¥29</span>
              <span class="text-gray-500">/月</span>
            </div>
            <p class="text-gray-500 text-sm mt-1">30天有效期</p>
          </div>

          <ul class="space-y-4 mb-8">
            <li class="flex items-start">
              <svg class="w-5 h-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">无限视频解析</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">无限视频下载</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">AI 智能总结</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">AI 问答功能</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">思维导图导出</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">字幕提取下载</span>
            </li>
          </ul>

          <button
            @click="handleUpgrade"
            class="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5"
          >
            立即开通
          </button>
        </div>

        <!-- 年度会员 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 lg:p-8 hover:shadow-xl transition-shadow">
          <div class="text-center mb-6">
            <h3 class="text-xl font-bold text-gray-800 mb-2">年度会员</h3>
            <div class="flex items-baseline justify-center gap-1">
              <span class="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">¥288</span>
              <span class="text-gray-500">/年</span>
            </div>
            <p class="text-purple-600 text-sm font-medium mt-1">省 ¥60，仅 ¥24/月</p>
          </div>

          <ul class="space-y-4 mb-8">
            <li class="flex items-start">
              <svg class="w-5 h-5 text-purple-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">月度会员全部权益</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-purple-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">优先技术支持</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-purple-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">新功能优先体验</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-purple-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-700 font-medium">更高并发限制</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-yellow-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              <span class="text-yellow-600 font-medium">超值划算</span>
            </li>
          </ul>

          <button
            @click="handleUpgrade"
            class="w-full py-3 px-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-medium hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5"
          >
            立即开通
          </button>
        </div>
      </div>

      <!-- 常见问题 -->
      <div class="max-w-3xl mx-auto mt-16">
        <h2 class="text-2xl font-bold text-center text-gray-900 mb-8">常见问题</h2>
        <div class="space-y-4">
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">如何支付？</h3>
            <p class="text-gray-600 text-sm">支持支付宝、微信支付、银行卡等多种支付方式，支付过程安全加密。</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">会员到期后会自动续费吗？</h3>
            <p class="text-gray-600 text-sm">不会，会员到期后需要手动续费。我们不会自动扣费。</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">可以退款吗？</h3>
            <p class="text-gray-600 text-sm">开通7天内，如对服务不满意，可申请全额退款。</p>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-200 mt-16 lg:mt-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center text-gray-500 text-sm">
          <p>&copy; 2024 FetchVid. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import UserMenu from '../components/UserMenu.vue'

const router = useRouter()

const handleUpgrade = () => {
  router.push('/upgrade')
}

const goToDownload = () => {
  router.push('/download')
}
</script>

<style scoped>
.nav-link {
  position: relative;
  padding-bottom: 6px;
  transition: all 0.2s ease;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(to right, #3b82f6, #8b5cf6);
  transition: width 0.2s ease;
}

.nav-link:hover::after {
  width: 100%;
}
</style>
