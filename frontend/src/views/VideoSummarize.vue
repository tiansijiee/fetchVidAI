<template>
  <div class="min-h-screen bg-gray-50">
    <div class="relative z-10">
      <!-- 顶部导航 -->
      <header class="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <span class="text-xl font-bold gradient-text">AI视频总结</span>
            </div>
            <nav class="flex items-center gap-6">
              <router-link to="/download" class="nav-link">视频下载</router-link>
              <router-link to="/summarize" class="nav-link text-primary-600">AI总结</router-link>
            </nav>
          </div>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <!-- 标题区 -->
        <div class="text-center mb-10">
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4">
            <span class="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">AI视频总结</span>
          </h1>
          <p class="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
            智能提取视频核心内容，生成摘要、思维导图和知识点
          </p>
        </div>

        <!-- 输入卡片 -->
        <div class="glass-card p-6 sm:p-8 mb-8">
          <div class="space-y-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              <span class="flex items-center gap-2">
                <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                </svg>
                粘贴视频链接
              </span>
            </label>
            <div class="flex flex-col sm:flex-row gap-3">
              <input
                v-model="videoUrl"
                type="text"
                placeholder="支持 B站/YouTube 等有字幕的视频链接"
                class="input-field flex-1"
                @keyup.enter="checkAndSummarize"
                :disabled="processing"
              >
              <button
                @click="checkAndSummarize"
                :disabled="!videoUrl.trim() || processing"
                class="btn-gradient whitespace-nowrap flex items-center justify-center gap-2"
              >
                <span v-if="!processing">AI总结</span>
                <span v-else>处理中...</span>
              </button>
            </div>

            <!-- 错误提示 -->
            <div v-if="error" class="p-4 rounded-2xl bg-red-50 border border-red-200">
              <span class="text-red-700 text-sm">{{ error }}</span>
            </div>

            <!-- 平台提示 -->
            <div class="flex flex-wrap items-center gap-2 pt-2">
              <span class="text-sm text-gray-500">支持平台：</span>
              <span class="platform-badge">📺 B站</span>
              <span class="platform-badge">▶️ YouTube</span>
              <span class="text-xs text-gray-400 ml-2">*需要有字幕的视频</span>
            </div>
          </div>
        </div>

        <!-- 处理进度 -->
        <div v-if="processing" class="glass-card p-8 mb-8 text-center">
          <div class="max-w-md mx-auto">
            <div class="w-16 h-16 mx-auto mb-4 relative">
              <div class="absolute inset-0 border-4 border-purple-200 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-purple-500 rounded-full border-t-transparent animate-spin"></div>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ processingStatus.title }}</h3>
            <p class="text-sm text-gray-600 mb-4">{{ processingStatus.desc }}</p>
            <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500" :style="{ width: processingProgress + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- 总结结果 -->
        <div v-if="summaryResult" class="space-y-8">
          <!-- 视频信息卡片 -->
          <div class="glass-card p-6">
            <div class="flex items-start gap-4">
              <img
                v-if="videoInfo.thumbnail"
                :src="getThumbnailUrl(videoInfo.thumbnail)"
                class="w-32 h-20 object-cover rounded-lg flex-shrink-0"
              >
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-bold text-gray-900 mb-2">{{ videoInfo.title }}</h3>
                <p class="text-sm text-gray-600">{{ videoInfo.uploader }}</p>
              </div>
            </div>
          </div>

          <!-- 核心总结卡片 -->
          <div class="glass-card p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                核心总结
              </h3>
              <button
                @click="copyText(summaryResult.overview || summaryResult.summary)"
                class="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
                复制
              </button>
            </div>
            <p class="text-gray-700 leading-relaxed">{{ summaryResult.overview || summaryResult.summary }}</p>
          </div>

          <!-- 内容大纲 -->
          <div v-if="summaryResult.outline && summaryResult.outline.length" class="glass-card p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
              </svg>
              内容大纲
            </h3>
            <div class="space-y-4">
              <div
                v-for="(segment, index) in summaryResult.outline"
                :key="index"
                class="border-l-4 border-purple-200 pl-4 hover:border-purple-400 transition-colors"
              >
                <h4 class="font-semibold text-gray-900 mb-1">{{ segment.title }}</h4>
                <p class="text-sm text-gray-600 mb-2">{{ segment.content }}</p>
                <span v-if="segment.timestamp" class="text-xs text-gray-400">🕐 {{ segment.timestamp }}</span>
              </div>
            </div>
          </div>

          <!-- 核心知识点 -->
          <div v-if="summaryResult.key_points && summaryResult.key_points.length" class="glass-card p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
              核心知识点
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div
                v-for="(point, index) in summaryResult.key_points"
                :key="index"
                class="p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
              >
                <div class="flex items-start gap-2">
                  <span class="text-purple-500">{{ '⭐'.repeat(Math.min(point.importance || 3, 5)) }}</span>
                  <span class="text-sm text-gray-700">{{ point.point }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 思维导图 -->
          <div v-if="summaryResult.mindmap" class="glass-card p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
              思维导图
            </h3>
            <div class="bg-gray-50 rounded-xl p-6">
              <div class="text-center font-bold text-lg text-gray-900 mb-4">
                {{ summaryResult.mindmap.root || '主题' }}
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  v-for="(branch, index) in summaryResult.mindmap.branches"
                  :key="index"
                  class="bg-white rounded-lg p-4 shadow-sm"
                >
                  <h4 class="font-semibold text-purple-600 mb-2">{{ branch.name }}</h4>
                  <ul class="space-y-1">
                    <li v-for="(child, i) in branch.children" :key="i" class="text-sm text-gray-600 flex items-center gap-2">
                      <span class="w-1.5 h-1.5 bg-purple-300 rounded-full"></span>
                      {{ child }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- AI问答面板 -->
          <div class="glass-card p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
              </svg>
              AI问答 - 深入了解视频内容
            </h3>
            <div class="space-y-4 max-h-96 overflow-y-auto mb-4" id="chatContainer">
              <div
                v-for="(msg, index) in chatMessages"
                :key="index"
                class="flex gap-3"
                :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-[80%] rounded-2xl px-4 py-2"
                  :class="msg.role === 'user' ? 'bg-purple-500 text-white' : 'bg-gray-100 text-gray-800'"
                >
                  {{ msg.content }}
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <input
                v-model="chatQuestion"
                type="text"
                placeholder="向AI提问关于视频内容的问题..."
                class="input-field flex-1"
                @keyup.enter="sendChat"
                :disabled="chatLoading"
              >
              <button
                @click="sendChat"
                :disabled="!chatQuestion.trim() || chatLoading"
                class="btn-gradient px-6"
              >
                发送
              </button>
            </div>
          </div>

          <!-- 导出按钮 -->
          <div class="flex flex-wrap gap-3 justify-center">
            <button
              @click="exportSummary('md')"
              class="flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              导出 Markdown
            </button>
            <button
              @click="checkSubtitle"
              class="flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              查看完整字幕
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- 字幕查看对话框 -->
    <el-dialog v-model="subtitleDialogVisible" title="完整字幕" width="80%" top="5vh">
      <div class="max-h-[60vh] overflow-y-auto">
        <div
          v-for="(sub, index) in subtitles"
          :key="index"
          class="mb-3 pb-3 border-b border-gray-100"
        >
          <div class="text-xs text-gray-400 mb-1">{{ sub.time }}</div>
          <div class="text-sm text-gray-700">{{ sub.text }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const videoUrl = ref('')
const processing = ref(false)
const processingProgress = ref(0)
const error = ref('')
const summaryResult = ref(null)
const videoInfo = reactive({ title: '', uploader: '', thumbnail: '' })
const chatMessages = ref([])
const chatQuestion = ref('')
const chatLoading = ref(false)
const subtitleDialogVisible = ref(false)
const subtitles = ref([])

const processingStatus = computed(() => {
  const statusMap = {
    checking: { title: '检查字幕', desc: '正在检查视频是否有字幕...' },
    extracting: { title: '提取字幕', desc: '正在提取视频字幕内容...' },
    summarizing: { title: 'AI总结中', desc: 'AI正在分析视频内容并生成总结...' },
    creating_chat: { title: '创建会话', desc: '正在创建AI问答会话...' },
    completed: { title: '完成', desc: '总结已完成！' }
  }
  const progress = processingProgress.value
  if (progress < 20) return statusMap.checking
  if (progress < 40) return statusMap.extracting
  if (progress < 80) return statusMap.summarizing
  if (progress < 100) return statusMap.creating_chat
  return statusMap.completed
})

const getThumbnailUrl = (url) => {
  if (!url) return ''
  return `/api/proxy/thumbnail?url=${encodeURIComponent(url)}`
}

const checkAndSummarize = async () => {
  const url = videoUrl.value.trim()
  if (!url) {
    error.value = '请输入视频链接'
    return
  }

  processing.value = true
  processingProgress.value = 0
  error.value = ''
  summaryResult.value = null

  try {
    // 先解析视频获取基本信息
    const parseResponse = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })

    const parseResult = await parseResponse.json()
    if (!parseResult.success) {
      throw new Error(parseResult.message)
    }

    videoInfo.title = parseResult.data.title
    videoInfo.uploader = parseResult.data.uploader
    videoInfo.thumbnail = parseResult.data.thumbnail

    processingProgress.value = 20

    // 使用流式API直接获取总结结果
    const streamResponse = await fetch('/api/ai/summarize/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        title: videoInfo.title,
        description: parseResult.data.description || ''
      })
    })

    if (!streamResponse.ok) {
      throw new Error('请求失败')
    }

    // 读取SSE流
    const reader = streamResponse.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'progress') {
              // 更新进度消息
              if (data.message.includes('分析')) processingProgress.value = 30
              else if (data.message.includes('字幕')) processingProgress.value = 50
              else if (data.message.includes('ASR') || data.message.includes('转写')) processingProgress.value = 60
              else if (data.message.includes('思考') || data.message.includes('AI')) processingProgress.value = 80
            } else if (data.type === 'result') {
              // 最终结果
              summaryResult.value = data.data
              processingProgress.value = 100
              processing.value = false
              ElMessage.success('AI总结完成！')
              return
            } else if (data.type === 'error') {
              throw new Error(data.message || '生成失败')
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e)
          }
        }
      }
    }

  } catch (err) {
    error.value = err.message || '处理失败'
    processing.value = false
    ElMessage.error(err.message)
  }
}

const sendChat = async () => {
  if (!chatQuestion.value.trim() || !videoUrl.value) return

  const question = chatQuestion.value
  chatQuestion.value = ''
  chatMessages.value.push({ role: 'user', content: question })
  chatLoading.value = true

  try {
    const response = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        url: videoUrl.value,
        video_info: {
          title: videoInfo.title
        }
      })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    // 读取SSE流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let assistantMessage = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'content') {
              assistantMessage += data.content
              // 更新最后一条消息
              const lastMsg = chatMessages.value[chatMessages.value.length - 1]
              if (lastMsg && lastMsg.role === 'assistant') {
                lastMsg.content = assistantMessage
              } else {
                chatMessages.value.push({ role: 'assistant', content: assistantMessage })
              }
              scrollToBottom()
            } else if (data.type === 'complete') {
              scrollToBottom()
            } else if (data.type === 'error') {
              throw new Error(data.message || '问答失败')
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e)
          }
        }
      }
    }

  } catch (err) {
    ElMessage.error(err.message || '网络错误')
  } finally {
    chatLoading.value = false
  }
}

const scrollToBottom = async () => {
  await nextTick()
  const container = document.getElementById('chatContainer')
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

const copyText = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}

const exportSummary = (format) => {
  if (!summaryResult.value) return

  let md = `# ${videoInfo.title || '视频总结'}\n\n`

  // 视频概述
  if (summaryResult.value.overview) {
    md += `## 🎯 视频概述\n\n${summaryResult.value.overview}\n\n`
  }

  // 内容大纲
  if (summaryResult.value.outline && summaryResult.value.outline.length) {
    md += `## 📚 内容大纲\n\n`
    summaryResult.value.outline.forEach((outline, index) => {
      md += `### ${index + 1}. ${outline.title}\n\n${outline.content}\n\n`
    })
  }

  // 核心要点
  if (summaryResult.value.key_points && summaryResult.value.key_points.length) {
    md += `## 💡 核心要点\n\n`
    summaryResult.value.key_points.forEach(point => {
      md += `- ${point.point}\n`
    })
    md += '\n'
  }

  // 总结结论
  if (summaryResult.value.conclusion) {
    md += `## 📝 总结结论\n\n`
    if (summaryResult.value.conclusion.summary) {
      md += `**总结**: ${summaryResult.value.conclusion.summary}\n\n`
    }
    if (summaryResult.value.conclusion.takeaways) {
      md += `**主要收获**:\n\n`
      summaryResult.value.conclusion.takeaways.forEach(takeaway => {
        md += `- ${takeaway}\n`
      })
      md += '\n'
    }
  }

  // 创建下载
  const blob = new Blob([md], { type: 'text/markdown' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${videoInfo.title || '视频总结'}_${Date.now()}.md`
  link.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('导出成功！')
}

const checkSubtitle = async () => {
  if (!videoUrl.value || !subtitles.value.length) {
    // 如果没有字幕，尝试获取
    try {
      const response = await fetch('/api/ai/subtitle/raw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: videoUrl.value,
          use_asr: true
        })
      })

      const result = await response.json()
      if (result.success && result.full_text) {
        // 解析字幕文本为字幕数组
        const lines = result.full_text.split('\n').filter(line => line.trim())
        subtitles.value = lines.map((line, index) => ({
          time: `${Math.floor(index * 5 / 60).toString().padStart(2, '0')}:${((index * 5) % 60).toString().padStart(2, '0')}`,
          text: line.trim()
        }))
      }
    } catch (err) {
      ElMessage.error('获取字幕失败')
    }
  }
  subtitleDialogVisible.value = true
}
</script>
