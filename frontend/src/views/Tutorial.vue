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
            <router-link to="/pricing" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">套餐价格</router-link>
            <router-link to="/features" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">功能特性</router-link>
            <router-link to="/tutorial" class="nav-link text-base font-semibold text-blue-600">使用教程</router-link>
          </nav>

          <!-- VIP入口 & 用户菜单 -->
          <div class="flex items-center gap-3">
            <!-- 语言切换按钮 -->
            <LanguageSwitcher />

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
          <span class="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 bg-clip-text text-transparent">使用教程</span>
        </h1>
        <p class="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
          简单三步，轻松下载任意视频
        </p>
      </div>

      <!-- 使用步骤 -->
      <div class="grid md:grid-cols-3 gap-6 lg:gap-8 mb-16">
        <!-- 步骤1 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300">
          <div class="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl mb-6 shadow-lg shadow-blue-500/30">
            <span class="text-3xl font-bold text-white">1</span>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3 text-center">复制视频链接</h3>
          <p class="text-gray-600 text-center mb-6">从任意视频平台复制你想要下载的视频链接</p>
          <div class="bg-gray-50 rounded-xl p-4">
            <p class="text-sm text-gray-500 mb-2 text-center">支持的平台</p>
            <div class="flex flex-wrap justify-center gap-2">
              <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">Bilibili</span>
              <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">YouTube</span>
              <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">抖音</span>
              <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">快手</span>
            </div>
          </div>
        </div>

        <!-- 步骤2 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300">
          <div class="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl mb-6 shadow-lg shadow-purple-500/30">
            <span class="text-3xl font-bold text-white">2</span>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3 text-center">粘贴并解析</h3>
          <p class="text-gray-600 text-center mb-6">将链接粘贴到输入框，点击"立即解析"按钮</p>
          <div class="bg-gray-50 rounded-xl p-4">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-sm text-gray-600">自动识别视频信息</span>
            </div>
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-sm text-gray-600">选择视频质量</span>
            </div>
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-sm text-gray-600">预览视频缩略图</span>
            </div>
          </div>
        </div>

        <!-- 步骤3 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300">
          <div class="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-pink-500 to-pink-600 rounded-2xl mb-6 shadow-lg shadow-pink-500/30">
            <span class="text-3xl font-bold text-white">3</span>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3 text-center">下载或使用AI功能</h3>
          <p class="text-gray-600 text-center mb-6">选择下载视频，或使用AI总结和问答功能</p>
          <div class="bg-gray-50 rounded-xl p-4">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-sm text-gray-600">下载视频文件</span>
            </div>
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-sm text-gray-600">AI智能总结</span>
            </div>
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              <span class="text-sm text-gray-600">AI智能问答</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细教程 -->
      <div class="max-w-4xl mx-auto">
        <h2 class="text-2xl font-bold text-center text-gray-900 mb-8">详细使用说明</h2>

        <!-- 视频下载教程 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 mb-6">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">如何下载视频</h3>
              <p class="text-gray-500 text-sm">视频下载指南</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">1</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">复制视频链接</p>
                <p class="text-sm text-gray-600">在视频平台（如B站、YouTube等）打开想要下载的视频，复制浏览器地址栏中的链接</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">2</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">粘贴并解析</p>
                <p class="text-sm text-gray-600">将链接粘贴到首页输入框，点击"立即解析"按钮，等待系统解析视频信息</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">3</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">选择质量和格式</p>
                <p class="text-sm text-gray-600">在解析结果中选择你想要的视频质量和格式（如1080p、4K等）</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">4</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">点击下载</p>
                <p class="text-sm text-gray-600">点击"下载"按钮，视频将自动下载到你的设备</p>
              </div>
            </div>
          </div>
        </div>

        <!-- AI总结教程 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 mb-6">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">如何使用AI总结</h3>
              <p class="text-gray-500 text-sm">AI总结指南</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold">1</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">解析视频</p>
                <p class="text-sm text-gray-600">先按照视频下载步骤解析视频</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold">2</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">点击"AI总结"</p>
                <p class="text-sm text-gray-600">在解析结果页面，点击"AI智能总结"按钮</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold">3</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">等待AI分析</p>
                <p class="text-sm text-gray-600">AI会自动分析视频内容，提取核心要点并生成结构化摘要</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold">4</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">查看或导出总结</p>
                <p class="text-sm text-gray-600">查看AI生成的总结内容，或导出为思维导图、文本等格式</p>
              </div>
            </div>
          </div>
        </div>

        <!-- AI问答教程 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-12 h-12 bg-gradient-to-br from-pink-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg shadow-pink-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">如何使用AI问答</h3>
              <p class="text-gray-500 text-sm">AI问答指南</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-pink-100 text-pink-600 rounded-full flex items-center justify-center text-sm font-bold">1</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">解析视频并生成总结</p>
                <p class="text-sm text-gray-600">先使用AI总结功能对视频进行分析</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-pink-100 text-pink-600 rounded-full flex items-center justify-center text-sm font-bold">2</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">进入AI问答</p>
                <p class="text-sm text-gray-600">在总结页面点击"AI问答"按钮进入问答界面</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-pink-100 text-pink-600 rounded-full flex items-center justify-center text-sm font-bold">3</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">提问</p>
                <p class="text-sm text-gray-600">在输入框中输入关于视频的任何问题，如"视频讲了什么重点？"等</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 bg-pink-100 text-pink-600 rounded-full flex items-center justify-center text-sm font-bold">4</span>
              <div>
                <p class="font-medium text-gray-900 mb-1">获取答案</p>
                <p class="text-sm text-gray-600">AI会基于视频内容给出精准答案，支持多轮对话</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 常见问题 -->
      <div class="max-w-3xl mx-auto mt-16">
        <h2 class="text-2xl font-bold text-center text-gray-900 mb-8">常见问题</h2>
        <div class="space-y-4">
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">支持哪些视频平台？</h3>
            <p class="text-gray-600 text-sm">我们支持100+视频平台，包括B站、YouTube、抖音、快手、Twitter、微博等主流平台。</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">下载次数有限制吗？</h3>
            <p class="text-gray-600 text-sm">免费用户每日可下载1次，注册用户每日3次，VIP会员无限制。</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">下载速度如何？</h3>
            <p class="text-gray-600 text-sm">我们采用高速服务器，下载速度取决于您的网络环境，最高可达带宽上限。</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">AI功能支持哪些语言？</h3>
            <p class="text-gray-600 text-sm">AI总结和问答功能支持中文、英文等多种语言的视频内容分析。</p>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="mt-16 text-center">
        <div class="bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 rounded-3xl p-8 lg:p-12 shadow-2xl shadow-blue-500/30 relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-purple-400/20 animate-pulse"></div>
          <div class="relative z-10">
            <h2 class="text-3xl font-bold text-white mb-4">准备好开始了吗？</h2>
            <p class="text-blue-100 mb-6 max-w-xl mx-auto">立即体验FetchVid的强大功能，一键下载任意视频</p>
            <button
              @click="goToDownload"
              class="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-xl font-bold hover:bg-blue-50 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
              </svg>
              开始使用
            </button>
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
import { onMounted } from 'vue'
import UserMenu from '../components/UserMenu.vue'
import { addStructuredData, generateSoftwareSchema, setCanonicalUrl } from '../utils/seo'

const router = useRouter()

const handleUpgrade = () => {
  router.push('/upgrade')
}

const goToDownload = () => {
  router.push('/download')
}

// SEO 优化
onMounted(() => {
  addStructuredData(generateSoftwareSchema('zh'))
  setCanonicalUrl('https://fetchvid.com/tutorial')
})
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
