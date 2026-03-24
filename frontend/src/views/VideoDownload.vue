<template>
  <div class="min-h-screen bg-gray-50 font-sans">
    <!-- 顶部导航栏 - SaveAny风格 -->
    <header class="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- 左侧：Logo + 副标题 -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div class="flex flex-col">
              <span class="text-lg font-bold text-gray-900 leading-tight">FetchVid</span>
              <span class="text-xs text-gray-500 leading-tight">万能视频下载器</span>
            </div>
          </div>

          <!-- 中间：导航入口 -->
          <nav class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">功能特性</a>
            <a href="#pricing" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">套餐价格</a>
            <a href="#platforms" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">支持平台</a>
          </nav>

          <!-- 右侧：VIP按钮 -->
          <div class="flex items-center gap-3">
            <button class="hidden sm:block px-4 py-2 bg-primary-50 text-primary-600 rounded-lg text-sm font-medium hover:bg-primary-100 transition-colors">
              开通VIP
            </button>
            <!-- 移动端菜单按钮 -->
            <button class="md:hidden p-2" @click="mobileMenuOpen = !mobileMenuOpen">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- 移动端菜单 -->
        <div v-if="mobileMenuOpen" class="md:hidden py-4 border-t border-gray-100">
          <nav class="flex flex-col gap-4">
            <a href="#features" class="text-sm text-gray-600 hover:text-gray-900">功能特性</a>
            <a href="#pricing" class="text-sm text-gray-600 hover:text-gray-900">套餐价格</a>
            <a href="#platforms" class="text-sm text-gray-600 hover:text-gray-900">支持平台</a>
            <button class="px-4 py-2 bg-primary-50 text-primary-600 rounded-lg text-sm font-medium text-left">
              开通VIP
            </button>
          </nav>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">

      <!-- 核心输入区 - 大尺寸设计 -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8 mb-8">
        <div class="space-y-6">
          <!-- 输入区域 -->
          <div class="flex flex-col lg:flex-row gap-4">
            <div class="flex-1">
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                  </svg>
                </div>
                <input
                  v-model="videoUrl"
                  type="text"
                  placeholder="粘贴视频链接，支持B站/YouTube/微博等平台"
                  class="w-full pl-12 pr-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 transition-colors"
                  @keyup.enter="parseVideo"
                  :disabled="loading"
                >
              </div>
            </div>
            <button
              @click="parseVideo"
              :disabled="!videoUrl.trim() || loading"
              class="px-8 py-4 bg-primary-500 text-white rounded-xl text-base font-medium hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 min-w-[160px]"
            >
              <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ loading ? '解析中...' : '解析视频' }}</span>
            </button>
          </div>

          <!-- 快速尝试标签 -->
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-sm text-gray-500">快速尝试：</span>
            <button
              v-for="platform in quickPlatforms"
              :key="platform.id"
              @click="fillExample(platform.example)"
              class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm transition-colors flex items-center gap-1.5"
            >
              <span>{{ platform.icon }}</span>
              <span>{{ platform.name }}</span>
            </button>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-xl">
            <div class="flex items-start gap-2">
              <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span class="text-red-700 text-sm">{{ error }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 解析结果区 - SaveAny风格 -->
      <div v-if="videoData" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <!-- 视频预览卡片 -->
        <div class="flex flex-col lg:flex-row">
          <!-- 左侧：视频预览 -->
          <div class="lg:w-2/5 relative">
            <div class="relative aspect-video bg-gray-900">
              <img
                :src="getThumbnailUrl(videoData.thumbnail)"
                :alt="videoData.title"
                class="w-full h-full object-cover"
              >
              <!-- 播放按钮 -->
              <div class="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors cursor-pointer group">
                <div class="w-16 h-16 bg-white/90 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                  <svg class="w-8 h-8 text-primary-500 ml-1" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"></path>
                  </svg>
                </div>
              </div>
              <!-- 时长标签 -->
              <div class="absolute bottom-3 right-3 bg-black/80 text-white text-sm px-2 py-1 rounded">
                {{ videoData.duration }}
              </div>
            </div>
          </div>

          <!-- 右侧：视频信息 + 操作区 -->
          <div class="lg:w-3/5 p-6 lg:p-8">
            <!-- 视频元信息 -->
            <div class="mb-6">
              <h1 class="text-xl lg:text-2xl font-bold text-gray-900 mb-4 line-clamp-2">
                {{ videoData.title }}
              </h1>
              <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                <div class="flex items-center gap-1.5">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                  <span>{{ videoData.uploader || '未知UP主' }}</span>
                </div>
                <div v-if="videoData.view_count" class="flex items-center gap-1.5">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                  <span>{{ formatViewCount(videoData.view_count) }}播放</span>
                </div>
              </div>
            </div>

            <!-- 清晰度选择 -->
            <div class="mb-6">
              <div class="text-sm text-gray-600 mb-3">选择清晰度：</div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="format in displayFormats"
                  :key="format.format_id"
                  @click="selectedFormat = format.format_id"
                  class="px-4 py-2 border rounded-lg text-sm font-medium transition-colors"
                  :class="selectedFormat === format.format_id
                    ? 'bg-primary-500 border-primary-500 text-white'
                    : 'bg-white border-gray-300 text-gray-700 hover:border-primary-500'"
                >
                  <span v-if="format.recommended" class="mr-1">👑</span>
                  {{ format.quality }}
                </button>
              </div>
              <div class="mt-2 text-xs text-gray-500">
                <span v-if="selectedFormatData">
                  {{ selectedFormatData.ext?.toUpperCase() }} · {{ selectedFormatData.size_formatted || '未知大小' }}
                </span>
              </div>
            </div>

            <!-- 操作按钮栏 -->
            <div class="flex flex-col sm:flex-row gap-3">
              <!-- 立即下载按钮 -->
              <button
                @click="downloadVideo"
                :disabled="downloading || !selectedFormat"
                class="flex-1 px-6 py-3.5 bg-primary-500 text-white rounded-xl font-medium hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <svg v-if="!downloading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ downloading ? `下载中 ${downloadProgress}%` : '立即下载' }}</span>
              </button>

              <!-- AI总结按钮 -->
              <button
                @click="toggleAIPanel"
                class="px-6 py-3.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-medium hover:from-purple-600 hover:to-pink-600 transition-colors flex items-center justify-center gap-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
                <span>AI总结</span>
              </button>
            </div>

            <!-- 下载进度 -->
            <div v-if="downloading && downloadProgress > 0" class="mt-4">
              <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="absolute inset-y-0 left-0 bg-primary-500 rounded-full transition-all duration-300"
                  :style="{ width: downloadProgress + '%' }"
                ></div>
              </div>
              <p class="text-center text-sm text-gray-600 mt-2">下载进度: {{ downloadProgress }}%</p>
            </div>
          </div>
        </div>
      </div>

      <!-- AI功能面板 -->
      <div v-if="showAIPanel && videoData" class="mt-8">
        <VideoAIPanel
          :video-url="originalUrl"
          :video-title="videoData.title"
          :video-description="videoData.description"
          :video-thumbnail="videoData.thumbnail"
          @seek-timestamp="handleSeekTimestamp"
        />
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-100 mt-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center text-sm text-gray-500">
          <p>© 2024 FetchVid · 万能视频下载器 · 支持B站/YouTube/微博等平台</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VideoAIPanel from '@/components/VideoAIPanel.vue'

const videoUrl = ref('')
const loading = ref(false)
const error = ref('')
const videoData = ref(null)
const originalUrl = ref('')
const selectedFormat = ref('')
const downloading = ref(false)
const downloadProgress = ref(0)
const downloadTaskId = ref(null)
const mobileMenuOpen = ref(false)
const showAIPanel = ref(false)

// 快速尝试平台
const quickPlatforms = [
  { id: 'youtube', name: 'YouTube', icon: '▶️', example: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' },
  { id: 'bilibili', name: 'Bilibili', icon: '📺', example: 'https://www.bilibili.com/video/BV1xx411c7mu' },
  { id: 'twitter', name: 'Twitter', icon: '🐦', example: 'https://twitter.com/user/status/123456' },
  { id: 'weibo', name: '微博', icon: '🌭', example: 'https://weibo.com/tv/show/123456' }
]

// 计算属性
const displayFormats = computed(() => {
  if (!videoData.value?.formats) return []
  return videoData.value.formats.map(f => ({
    ...f,
    recommended: f.quality === '1080p' || f.format_id === videoData.value.formats[0]?.format_id
  }))
})

const selectedFormatData = computed(() => {
  if (!videoData.value?.formats) return null
  return videoData.value.formats.find(f => f.format_id === selectedFormat.value)
})

// 方法
const getThumbnailUrl = (url) => {
  if (!url) return ''
  return `/api/proxy/thumbnail?url=${encodeURIComponent(url)}`
}

const formatViewCount = (count) => {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万'
  return count.toLocaleString()
}

const fillExample = (url) => {
  videoUrl.value = url
  error.value = ''
}

const parseVideo = async () => {
  const url = videoUrl.value.trim()
  if (!url) {
    error.value = '请输入视频链接'
    return
  }

  loading.value = true
  error.value = ''
  videoData.value = null
  showAIPanel.value = false

  try {
    const response = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })

    const result = await response.json()

    if (result.success) {
      videoData.value = result.data
      originalUrl.value = url
      if (result.data.formats && result.data.formats.length > 0) {
        // 默认选中1080p或第一个
        const format1080p = result.data.formats.find(f => f.quality === '1080p')
        selectedFormat.value = format1080p?.format_id || result.data.formats[0].format_id
      }
      ElMessage.success('解析成功！')
    } else {
      error.value = result.message
      ElMessage.error(result.message)
    }
  } catch (err) {
    error.value = '网络错误，请确保后端服务已启动'
    ElMessage.error('网络错误')
  } finally {
    loading.value = false
  }
}

const downloadVideo = async () => {
  if (!selectedFormat.value) {
    ElMessage.warning('请先选择清晰度')
    return
  }

  downloading.value = true
  downloadProgress.value = 0

  try {
    ElMessage.info('开始下载，请稍候...')

    const startResponse = await fetch('/api/proxy/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video_url: originalUrl.value,
        filename: videoData.value.title,
        format_id: selectedFormat.value
      })
    })

    const startData = await startResponse.json()
    if (!startData.success) {
      throw new Error(startData.message)
    }

    downloadTaskId.value = startData.task_id

    const pollStatus = async () => {
      try {
        const statusResponse = await fetch(`/api/proxy/download/status/${downloadTaskId.value}`)
        const status = await statusResponse.json()

        if (status.status === 'completed') {
          downloadProgress.value = 100
          const fileResponse = await fetch(`/api/proxy/download/file/${downloadTaskId.value}`)
          const blob = await fileResponse.blob()
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = status.filename
          link.click()
          window.URL.revokeObjectURL(url)
          ElMessage.success('下载完成！')
          downloading.value = false
        } else if (status.status === 'error') {
          throw new Error(status.error)
        } else {
          downloadProgress.value = status.progress || 0
          setTimeout(pollStatus, 2000)
        }
      } catch (err) {
        throw err
      }
    }

    pollStatus()
  } catch (err) {
    ElMessage.error(err.message || '下载失败')
    downloading.value = false
    downloadProgress.value = 0
  }
}

const handleSeekTimestamp = ({ time }) => {
  ElMessage.info(`跳转到时间: ${time}`)
  // TODO: 集成视频播放器跳转功能
}

const toggleAIPanel = () => {
  showAIPanel.value = !showAIPanel.value
  // 不再自动加载，用户切换Tab时按需加载
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
