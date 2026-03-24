<template>
  <div class="video-ai-panel">
    <!-- Tab 切换栏 -->
    <div class="tab-bar bg-white rounded-t-2xl border border-b-0 border-gray-200 p-2 flex gap-2">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="flex-1 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2"
        :class="activeTab === tab.key
          ? 'bg-gradient-to-r ' + tab.color + ' text-white shadow-md'
          : 'text-gray-600 hover:bg-gray-100'"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.icon"></path>
        </svg>
        <span>{{ tab.label }}</span>
        <span v-if="tab.status === 'loading'" class="ml-1">
          <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
        <span v-else-if="tab.status === 'done'" class="ml-1">✓</span>
      </button>
    </div>

    <!-- Tab 内容区域 -->
    <div class="tab-content bg-white border border-gray-200 rounded-b-2xl rounded-tr-2xl p-6 min-h-[500px]">
      <!-- 视频总结 -->
      <VideoSummary
        v-if="activeTab === 'summary'"
        :video-url="videoUrl"
        :video-title="videoTitle"
        :video-description="videoDescription"
        :video-thumbnail="videoThumbnail"
        :is-loading="loading.summary"
        :summary-data="summaryData"
        :streaming-content="streamingContent"
        @start-analysis="loadAllFeatures"
        @seek-timestamp="$emit('seek-timestamp', $event)"
      />

      <!-- 字幕文本 -->
      <SubtitlePanel
        v-else-if="activeTab === 'subtitle'"
        :video-url="videoUrl"
        :video-title="videoTitle"
        :is-loading="loading.subtitle"
        :subtitles="subtitles"
        @seek-timestamp="$emit('seek-timestamp', $event)"
      />

      <!-- 思维导图 -->
      <MindmapPanel
        v-else-if="activeTab === 'mindmap'"
        :video-url="videoUrl"
        :video-title="videoTitle"
        :is-loading="loading.mindmap"
        :summary-data="summaryData"
        @seek-timestamp="$emit('seek-timestamp', $event)"
      />

      <!-- AI问答 -->
      <ChatPanel
        v-else-if="activeTab === 'chat'"
        :video-url="videoUrl"
        :video-title="videoTitle"
        :subtitle-text="subtitleFullText"
        :is-loading="loading.chat"
        @seek-timestamp="$emit('seek-timestamp', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import VideoSummary from './VideoSummary.vue'
import SubtitlePanel from './SubtitlePanel.vue'
import MindmapPanel from './MindmapPanel.vue'
import ChatPanel from './ChatPanel.vue'

const props = defineProps({
  videoUrl: String,
  videoTitle: String,
  videoDescription: String,
  videoThumbnail: String
})

const emit = defineEmits(['seek-timestamp'])

// Tab 配置
const tabs = ref([
  {
    key: 'summary',
    label: '视频总结',
    icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
    color: 'from-purple-500 to-pink-500',
    status: 'pending'
  },
  {
    key: 'subtitle',
    label: '字幕文本',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'from-blue-500 to-cyan-500',
    status: 'pending'
  },
  {
    key: 'mindmap',
    label: '思维导图',
    icon: 'M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2',
    color: 'from-green-500 to-teal-500',
    status: 'pending'
  },
  {
    key: 'chat',
    label: 'AI问答',
    icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z',
    color: 'from-indigo-500 to-purple-500',
    status: 'pending'
  }
])

const activeTab = ref('summary')

// 加载状态
const loading = ref({
  summary: false,
  subtitle: false,
  mindmap: false,
  chat: false
})

// 数据缓存
const summaryData = ref(null)
const streamingContent = ref('')  // 用于打字机效果的流式内容
const subtitles = ref([])
const subtitleFullText = ref('')

// 更新Tab状态
const updateTabStatus = (key, status) => {
  const tab = tabs.value.find(t => t.key === key)
  if (tab) {
    tab.status = status
  }
}

// 加载所有功能 - 并行请求
const loadAllFeatures = async () => {
  // 重置状态
  summaryData.value = null
  streamingContent.value = ''
  subtitles.value = []
  subtitleFullText.value = ''

  tabs.value.forEach(tab => {
    tab.status = 'loading'
  })

  try {
    // 并行发起所有请求
    await Promise.allSettled([
      loadSummaryStream(),
      loadSubtitles()
    ])

    // 思维导图依赖总结数据，在总结完成后自动就绪
    if (summaryData.value) {
      updateTabStatus('mindmap', 'done')
    }

    // AI问答不自动加载，等待用户提问
    updateTabStatus('chat', 'done')

    ElMessage.success('AI分析完成！')
  } catch (err) {
    console.error('并行加载失败:', err)
    ElMessage.error('AI分析失败：' + (err.message || '未知错误'))
  }
}

// 加载总结（流式）
const loadSummaryStream = async () => {
  loading.value.summary = true

  try {
    const response = await fetch('/api/ai/summarize/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: props.videoUrl,
        title: props.videoTitle,
        description: props.videoDescription || ''
      })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    const reader = response.body.getReader()
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
              // 进度更新
              streamingContent.value = data.message || ''
            } else if (data.type === 'result') {
              // 最终结果
              summaryData.value = data.data
              updateTabStatus('summary', 'done')
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
    console.error('加载总结失败:', err)
    updateTabStatus('summary', 'error')
    throw err
  } finally {
    loading.value.summary = false
  }
}

// 加载字幕
const loadSubtitles = async () => {
  loading.value.subtitle = true

  try {
    const response = await fetch('/api/ai/subtitle/raw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: props.videoUrl,
        use_asr: true  // 启用ASR回退
      })
    })

    const result = await response.json()

    if (result.success) {
      subtitleFullText.value = result.full_text || ''
      subtitles.value = parseSubtitleText(result.full_text || '')
      updateTabStatus('subtitle', 'done')
    } else {
      // 字幕获取失败不算错误，只是没有字幕
      updateTabStatus('subtitle', 'done')
    }
  } catch (err) {
    console.error('加载字幕失败:', err)
    updateTabStatus('subtitle', 'error')
  } finally {
    loading.value.subtitle = false
  }
}

// 解析字幕文本为字幕数组
const parseSubtitleText = (fullText) => {
  if (!fullText) return []

  const lines = fullText.split('\n').filter(line => line.trim())
  const subtitles = []
  let currentTime = ''
  let currentText = ''

  const timeRegex = /^\[?(\d{2}:\d{2}:\d{2})\]?\s*/

  for (const line of lines) {
    const match = line.match(timeRegex)
    if (match) {
      if (currentTime && currentText) {
        subtitles.push({
          time: currentTime.substring(0, 5),
          start_time: currentTime,
          end_time: '',
          text: currentText.trim()
        })
      }
      currentTime = match[1]
      currentText = line.replace(timeRegex, '')
    } else if (currentTime) {
      currentText += ' ' + line
    }
  }

  if (currentTime && currentText) {
    subtitles.push({
      time: currentTime.substring(0, 5),
      start_time: currentTime,
      end_time: '',
      text: currentText.trim()
    })
  }

  return subtitles
}

// 暴露方法供父组件调用
defineExpose({
  loadAllFeatures
})
</script>

<style scoped>
.video-ai-panel {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tab-bar {
  display: flex;
  gap: 0.5rem;
}

.tab-bar button {
  transition: all 0.2s ease;
}

.tab-bar button:hover {
  transform: translateY(-1px);
}

.tab-content {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
