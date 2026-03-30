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

      <!-- Hero区域 -->
      <div class="text-center mb-12 lg:mb-16">
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
          <span class="bg-gradient-to-r from-red-600 via-pink-600 to-red-700 bg-clip-text text-transparent">YouTube视频下载器</span>
        </h1>
        <p class="text-xl sm:text-2xl text-gray-700 mb-8">一键下载YouTube高清视频</p>

        <!-- 核心特性标签 -->
        <div class="flex flex-wrap justify-center gap-4 mb-8">
          <span class="inline-flex items-center px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            支持4K/8K超清
          </span>
          <span class="inline-flex items-center px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            多格式选择
          </span>
          <span class="inline-flex items-center px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            AI智能总结
          </span>
          <span class="inline-flex items-center px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            全球加速
          </span>
        </div>

        <!-- CTA按钮 -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <router-link
            to="/download"
            class="px-8 py-4 bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white rounded-xl font-semibold transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 text-lg"
          >
            开始使用
          </router-link>
          <router-link
            to="/pricing"
            class="px-8 py-4 bg-white border-2 border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all text-lg"
          >
            套餐价格
          </router-link>
        </div>
      </div>

      <!-- 平台介绍 -->
      <article class="max-w-4xl mx-auto mb-16">
        <section class="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 lg:p-12">
          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 mb-6">为什么选择 FetchVid 下载抖音视频？</h2>

          <div class="space-y-6 text-gray-700 leading-relaxed">
            <p>
              <strong class="text-gray-900">FetchVid</strong> 是专业的抖音视频下载工具，支持一键无水印下载抖音短视频。无需安装软件，浏览器内直接完成，完全免费。
            </p>

            <h3 class="text-xl font-bold text-gray-900 mt-8 mb-4">核心功能</h3>

            <div class="grid md:grid-cols-2 gap-6">
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-pink-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-1">完全无水印</h4>
                  <p class="text-sm text-gray-600">下载的抖音视频完全无水印，保持原画质</p>
                </div>
              </div>

              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-1">高清原画质</h4>
                  <p class="text-sm text-gray-600">保持原视频高清画质，不压缩</p>
                </div>
              </div>

              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-1">AI智能总结</h4>
                  <p class="text-sm text-gray-600">自动提取视频要点，生成结构化摘要</p>
                </div>
              </div>

              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-1">批量下载</h4>
                  <p class="text-sm text-gray-600">支持批量下载多个抖音短视频</p>
                </div>
              </div>
            </div>

            <h3 class="text-xl font-bold text-gray-900 mt-8 mb-4">使用方法</h3>
            <ol class="list-decimal list-inside space-y-2 text-gray-700">
              <li>从抖音App复制视频链接</li>
              <li>粘贴到FetchVid输入框</li>
              <li>点击解析，确认无水印</li>
              <li>点击下载即可保存</li>
            </ol>

            <div class="mt-8 p-6 bg-pink-50 rounded-xl border border-pink-200">
              <p class="text-sm text-pink-800">
                <strong>温馨提示：</strong>请尊重抖音创作者的版权，下载的内容仅供个人学习使用，请勿用于商业用途或重新上传。
              </p>
            </div>
          </div>
        </section>
      </article>

      <!-- 常见问题 -->
      <section class="max-w-4xl mx-auto">
        <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 text-center mb-8">常见问题</h2>
        <div class="space-y-4">
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">如何下载抖音无水印视频？</h3>
            <p class="text-gray-600 text-sm">只需粘贴抖音视频分享链接，FetchVid会自动解析并提供无水印原画下载。</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">支持下载抖音直播吗？</h3>
            <p class="text-gray-600 text-sm">目前仅支持抖音已发布的短视频下载，暂不支持直播录制。</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="font-semibold text-gray-900 mb-2">下载失败怎么办？</h3>
            <p class="text-gray-600 text-sm">如遇下载失败，请检查链接是否正确，或尝试刷新页面重新解析。</p>
          </div>
        </div>
      </section>

    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-200 mt-16 lg:mt-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <!-- 品牌信息 -->
          <div>
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
              </div>
              <div>
                <div class="font-bold text-gray-900">FetchVid</div>
                <div class="text-xs text-gray-500">万能视频下载器</div>
              </div>
            </div>
            <p class="text-sm text-gray-600">支持100+视频平台，一键下载高清视频，AI智能总结视频内容。</p>
          </div>

          <!-- 快速链接 -->
          <div>
            <h4 class="font-semibold text-gray-900 mb-4">快速链接</h4>
            <ul class="space-y-2">
              <li><router-link to="/download" class="text-sm text-gray-600 hover:text-blue-600 transition-colors">视频下载</router-link></li>
              <li><router-link to="/pricing" class="text-sm text-gray-600 hover:text-blue-600 transition-colors">套餐价格</router-link></li>
              <li><router-link to="/features" class="text-sm text-gray-600 hover:text-blue-600 transition-colors">功能特性</router-link></li>
              <li><router-link to="/tutorial" class="text-sm text-gray-600 hover:text-blue-600 transition-colors">使用教程</router-link></li>
            </ul>
          </div>

          <!-- 其他平台 -->
          <div>
            <h4 class="font-semibold text-gray-900 mb-4">其他平台</h4>
            <ul class="space-y-2">
              <li><router-link to="/bilibili" class="text-sm text-gray-600 hover:text-blue-600 transition-colors">B站下载</router-link></li>
              <li><router-link to="/youtube" class="text-sm text-gray-600 hover:text-blue-600 transition-colors">YouTube下载</router-link></li>
            </ul>
          </div>
        </div>

        <div class="pt-8 border-t border-gray-200">
          <div class="text-center text-sm text-gray-500">
            <p>© 2024 FetchVid · 万能视频下载器 · 支持B站/YouTube/微博/抖音等平台</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import UserMenu from '../components/UserMenu.vue'
import { addStructuredData, generateSoftwareSchema, setCanonicalUrl } from '../utils/seo'

const router = useRouter()

// VIP升级
const handleUpgrade = () => {
  router.push('/upgrade')
}

// SEO 优化（保持搜索引擎优化）
onMounted(() => {
  addStructuredData(generateSoftwareSchema('zh'))
  setCanonicalUrl('https://fetchvid.com/douyin')
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
