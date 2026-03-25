<template>
  <div class="video-ai-panel">
    <!-- Tab 切换栏 -->
    <div class="tab-bar bg-white rounded-2xl border-2 border-gray-200 p-2 flex gap-2 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="flex-1 min-w-[120px] px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2"
        :class="activeTab === tab.key
          ? 'bg-gradient-to-r ' + tab.color + ' text-white shadow-md transform scale-[1.02]'
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
        <span v-else-if="tab.status === 'done'" class="ml-1 flex items-center justify-center w-5 h-5 bg-white/30 rounded-full">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
        </span>
      </button>
    </div>

    <!-- Tab 内容区域 -->
    <div class="tab-content glass-card p-6 min-h-[500px]">
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
        :progress-message="progressMessage"
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
        :markdown="mindmapMarkdown"
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
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import VideoSummary from './VideoSummary.vue'
import SubtitlePanel from './SubtitlePanel.vue'
import MindmapPanel from './MindmapPanel.vue'
import ChatPanel from './ChatPanel.vue'

const props = defineProps({
  videoUrl: String,
  videoTitle: String,
  videoDescription: String,
  videoThumbnail: String,
  autoStart: {
    type: Boolean,
    default: false
  },
  aiSummaryData: Object,
  aiSubtitles: Array
})

const emit = defineEmits(['seek-timestamp', 'analysis-complete'])

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
    color: 'from-primary-500 to-cyan-500',
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
const streamingContent = ref('')
const progressMessage = ref('')
const subtitles = ref([])
const subtitleFullText = ref('')
const mindmapMarkdown = ref('')

// ==============================================
// 【调试模式】监听 mindmapMarkdown 变化
// ==============================================
watch(mindmapMarkdown, (newVal) => {
  console.log('🔍 [VideoAIPanel] mindmapMarkdown 发生变化')
  console.log('📥 [VideoAIPanel] 新值长度:', newVal?.length || 0)
  console.log('📄 [VideoAIPanel] 新值预览:', newVal ? newVal.substring(0, 200) + '...' : '空字符串')
  console.log('📝 [VideoAIPanel] 当前 activeTab:', activeTab.value)
})

// 监听 activeTab 切换
watch(activeTab, (newTab) => {
  console.log('🔄 [VideoAIPanel] activeTab 切换到:', newTab)
  console.log('📊 [VideoAIPanel] mindmapMarkdown 长度:', mindmapMarkdown.value?.length || 0)
  if (newTab === 'mindmap') {
    console.log('🎯 [VideoAIPanel] 切换到思维导图 tab')
    console.log('📝 [VideoAIPanel] mindmapMarkdown 内容:', mindmapMarkdown.value ? '有数据' : '无数据')
  }
})

// 清空数据
const clearData = () => {
  summaryData.value = null
  streamingContent.value = ''
  subtitles.value = []
  subtitleFullText.value = ''

  tabs.value.forEach(tab => {
    tab.status = 'pending'
  })

  loading.value = {
    summary: false,
    subtitle: false,
    mindmap: false,
    chat: false
  }
}

// 更新Tab状态
const updateTabStatus = (key, status) => {
  const tab = tabs.value.find(t => t.key === key)
  if (tab) {
    tab.status = status
  }
}

// 加载所有功能 - 并行请求
const loadAllFeatures = async () => {
  // 清空旧数据
  clearData()

  // 设置所有Tab为加载状态
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
    emit('analysis-complete', { summaryData: summaryData.value })
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
    let currentEventType = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        // 解析SSE事件: event: xxx\ndata: xxx\n\n
        if (line.startsWith('event: ')) {
          currentEventType = line.slice(7).trim()
          continue
        }

        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (currentEventType === 'subtitle') {
              // 字幕事件 - 更新字幕数据
              const subtitlesData = data.subtitles || data.segments || []
              if (Array.isArray(subtitlesData) && subtitlesData.length > 0) {
                subtitles.value = subtitlesData
                subtitleFullText.value = data.text || subtitlesData.map(s => s.text).join('\n')
                console.log('[VideoAIPanel] 字幕已更新:', subtitleFullText.value.length, '字符')
              } else if (data.text) {
                subtitleFullText.value = data.text
                subtitles.value = parseSubtitleText(data.text)
                console.log('[VideoAIPanel] 字幕已更新:', subtitleFullText.value.length, '字符')
              }
            }
            else if (currentEventType === 'summary') {
              // 总结事件 - 处理流式总结内容
              if (data.token) {
                streamingContent.value += data.token
                console.log('[VideoAIPanel] 总结token:', data.token.length, '字符')
              }
            }
            else if (currentEventType === 'mindmap') {
              // 思维导图事件 - 后端直接生成的思维导图
              console.log('🎨 [VideoAIPanel] 收到 mindmap 事件')
              console.log('📝 [VideoAIPanel] mindmap 数据:', data)
              mindmapMarkdown.value = data.text || ''
              console.log('✅ [VideoAIPanel] mindmapMarkdown 已从后端数据赋值')
            }
            else if (currentEventType === 'complete' || currentEventType === 'done') {
              // 完成事件 - 生成总结数据和思维导图
              console.log('🎉 [VideoAIPanel] 总结完成 (' + currentEventType + ' 事件)')
              console.log('📝 [VideoAIPanel] streamingContent 长度:', streamingContent.value.length)
              console.log('📄 [VideoAIPanel] streamingContent 预览:', streamingContent.value.substring(0, 300))

              console.log('🔧 [VideoAIPanel] 开始解析为结构化数据')
              summaryData.value = parseSummaryToStructuredData(streamingContent.value)
              console.log('✅ [VideoAIPanel] 解析后的 summaryData:', summaryData.value)

              // 只有在 mindmapMarkdown 还没有被赋值的情况下才生成
              if (!mindmapMarkdown.value) {
                console.log('🎨 [VideoAIPanel] 开始生成思维导图 Markdown')
                mindmapMarkdown.value = generateMindmapFromSummary(summaryData.value)
                console.log('✅ [VideoAIPanel] mindmapMarkdown 已赋值')
              } else {
                console.log('ℹ️ [VideoAIPanel] mindmapMarkdown 已存在，跳过生成')
              }

              updateTabStatus('summary', 'done')
              return
            }
            else if (data.type === 'progress') {
              progressMessage.value = data.message || ''
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
        use_asr: true
      })
    })

    const result = await response.json()

    if (result.success) {
      subtitleFullText.value = result.full_text || ''
      subtitles.value = parseSubtitleText(result.full_text || '')
      updateTabStatus('subtitle', 'done')
    } else {
      updateTabStatus('subtitle', 'done')
    }
  } catch (err) {
    console.error('加载字幕失败:', err)
    updateTabStatus('subtitle', 'error')
  } finally {
    loading.value.subtitle = false
  }
}

// 将纯文本总结解析为结构化数据
const parseSummaryToStructuredData = (text) => {
  console.log('🔍 [VideoAIPanel] parseSummaryToStructuredData 开始执行')
  console.log('📥 [VideoAIPanel] 输入的 text 长度:', text?.length || 0)
  console.log('📄 [VideoAIPanel] 输入的 text 预览 (前500字符):', text?.substring(0, 500))

  if (!text) {
    console.error('❌ [VideoAIPanel] text 为空')
    return null
  }

  const result = {
    overview: '',
    outline: [],
    key_points: [],
    conclusion: ''
  }

  const lines = text.split('\n')
  let currentSection = 'overview'
  let currentContent = []

  console.log('📊 [VideoAIPanel] 开始逐行解析，总行数:', lines.length)

  for (let i = 0; i < lines.length; i++) {
    const trimmedLine = lines[i].trim()

    // 检测章节标题
    if (trimmedLine.match(/^【?(视频概述|内容大纲|核心要点|结论)?】?/i) ||
        trimmedLine.match(/^#{1,3}\s+/) ||
        trimmedLine.match(/^\d+\./)) {

      console.log('🔖 [VideoAIPanel] 检测到章节标题:', trimmedLine)

      // 保存上一个section的内容
      if (currentContent.length > 0) {
        const content = currentContent.join('\n').trim()
        if (currentSection === 'overview') {
          result.overview = content
          console.log('✅ [VideoAIPanel] 解析出 overview，长度:', content.length)
        } else if (currentSection === 'outline') {
          result.outline.push({ title: currentContent[0] || '', content: content })
          console.log('✅ [VideoAIPanel] 解析出 outline 项:', currentContent[0])
        } else if (currentSection === 'key_points') {
          result.key_points.push({ point: content })
          console.log('✅ [VideoAIPanel] 解析出 key_point:', content.substring(0, 50))
        } else if (currentSection === 'conclusion') {
          result.conclusion = content
          console.log('✅ [VideoAIPanel] 解析出 conclusion，长度:', content.length)
        }
        currentContent = []
      }

      // 确定新的section
      if (trimmedLine.includes('概述')) {
        currentSection = 'overview'
        console.log('📌 [VideoAIPanel] 切换到 overview section')
      } else if (trimmedLine.includes('大纲') || trimmedLine.includes('章节')) {
        currentSection = 'outline'
        console.log('📌 [VideoAIPanel] 切换到 outline section')
      } else if (trimmedLine.includes('要点') || trimmedLine.includes('重点')) {
        currentSection = 'key_points'
        console.log('📌 [VideoAIPanel] 切换到 key_points section')
      } else if (trimmedLine.includes('结论')) {
        currentSection = 'conclusion'
        console.log('📌 [VideoAIPanel] 切换到 conclusion section')
      } else if (trimmedLine.match(/^\d+\./)) {
        // 这是内容大纲的子项
        currentSection = 'outline'
        currentContent = [trimmedLine.replace(/^\d+\.\s*/, '')]
        console.log('📌 [VideoAIPanel] 检测到大纲子项:', trimmedLine)
      }
    } else {
      currentContent.push(trimmedLine)
    }
  }

  // 保存最后一个section
  if (currentContent.length > 0) {
    const content = currentContent.join('\n').trim()
    if (currentSection === 'overview') {
      result.overview = content
      console.log('✅ [VideoAIPanel] 最后保存 overview')
    } else if (currentSection === 'outline' && content) {
      result.outline.push({ title: content.split('\n')[0] || '', content: content })
      console.log('✅ [VideoAIPanel] 最后保存 outline 项')
    } else if (currentSection === 'key_points') {
      result.key_points.push({ point: content })
      console.log('✅ [VideoAIPanel] 最后保存 key_point')
    } else if (currentSection === 'conclusion') {
      result.conclusion = content
      console.log('✅ [VideoAIPanel] 最后保存 conclusion')
    }
  }

  // 如果没有解析出任何结构化内容，至少保留overview
  if (!result.overview && text.trim()) {
    result.overview = text.trim()
    console.log('⚠️ [VideoAIPanel] 没有解析出结构化内容，将全部文本作为 overview')
  }

  console.log('📊 [VideoAIPanel] 解析结果统计:')
  console.log('  - overview 长度:', result.overview?.length || 0)
  console.log('  - outline 数量:', result.outline?.length || 0)
  console.log('  - key_points 数量:', result.key_points?.length || 0)
  console.log('  - conclusion 长度:', result.conclusion?.length || 0)
  console.log('✅ [VideoAIPanel] parseSummaryToStructuredData 完成')

  return result
}

// 从总结数据生成思维导图 Markdown
const generateMindmapFromSummary = (data) => {
  console.log('🔍 [VideoAIPanel] generateMindmapFromSummary 开始执行')
  console.log('📥 [VideoAIPanel] 输入的 data:', data)

  if (!data) {
    console.error('❌ [VideoAIPanel] data 为空，无法生成思维导图')
    return ''
  }

  const lines = []
  const title = props.videoTitle || '视频主题'

  console.log('📝 [VideoAIPanel] 视频标题:', title)

  // 根节点 - markmap格式
  lines.push(`# ${title}`)

  // 视频概述
  if (data.overview) {
    console.log('✅ [VideoAIPanel] 有 overview:', data.overview)
    lines.push('')
    lines.push('## 视频概述')
    // 将概述文本分割为多个要点
    const overviewSentences = data.overview.split(/[。；；]/).filter(s => s.trim())
    overviewSentences.slice(0, 3).forEach(sentence => {
      if (sentence.trim()) {
        lines.push(`- ${sentence.trim()}`)
      }
    })
  } else {
    console.log('⚠️ [VideoAIPanel] 没有 overview')
  }

  // 内容大纲
  if (data.outline && Array.isArray(data.outline) && data.outline.length > 0) {
    console.log('✅ [VideoAIPanel] 有 outline，数量:', data.outline.length)
    lines.push('')
    lines.push('## 内容大纲')
    data.outline.forEach((item, index) => {
      lines.push(``)
      lines.push(`### ${item.title || `章节${index + 1}`}`)

      if (item.content) {
        // 分割内容为要点
        const sentences = item.content.split(/[。；；]/).filter(s => s.trim())
        sentences.slice(0, 5).forEach(sentence => {
          if (sentence.trim()) {
            lines.push(`- ${sentence.trim()}`)
          }
        })
      }
    })
  } else {
    console.log('⚠️ [VideoAIPanel] 没有 outline 或 outline 不是数组')
  }

  // 核心要点
  if (data.key_points && Array.isArray(data.key_points) && data.key_points.length > 0) {
    console.log('✅ [VideoAIPanel] 有 key_points，数量:', data.key_points.length)
    lines.push('')
    lines.push('## 核心要点')
    data.key_points.forEach(point => {
      const pointText = point.point || point
      if (pointText) {
        lines.push(`- ${pointText}`)
      }
    })
  } else {
    console.log('⚠️ [VideoAIPanel] 没有 key_points 或 key_points 不是数组')
  }

  // 结论
  if (data.conclusion) {
    console.log('✅ [VideoAIPanel] 有 conclusion:', data.conclusion)
    lines.push('')
    lines.push('## 结论')
    lines.push(`- ${data.conclusion}`)
  } else {
    console.log('⚠️ [VideoAIPanel] 没有 conclusion')
  }

  const result = lines.join('\n')
  console.log('📤 [VideoAIPanel] 生成的 Markdown 长度:', result.length)
  console.log('📄 [VideoAIPanel] 生成的 Markdown 预览 (前500字符):', result.substring(0, 500))

  return result
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

// 监听父组件传入的AI数据
watch(() => props.aiSummaryData, (newData) => {
  if (newData) {
    summaryData.value = newData
    updateTabStatus('summary', 'done')
    updateTabStatus('mindmap', 'done')
    updateTabStatus('chat', 'done')
  }
})

watch(() => props.aiSubtitles, (newData) => {
  if (newData && newData.length > 0) {
    subtitles.value = newData
    updateTabStatus('subtitle', 'done')
  }
})

// 组件挂载后自动开始分析
onMounted(() => {
  if (props.autoStart && props.videoUrl) {
    // 如果父组件传入了AI数据，直接使用
    if (props.aiSummaryData) {
      summaryData.value = props.aiSummaryData
      updateTabStatus('summary', 'done')
      updateTabStatus('mindmap', 'done')
      updateTabStatus('chat', 'done')
    }
    if (props.aiSubtitles && props.aiSubtitles.length > 0) {
      subtitles.value = props.aiSubtitles
      subtitleFullText.value = props.aiSubtitles.map(s => s.text).join('\n')
      updateTabStatus('subtitle', 'done')
    }
  }
})

// 暴露方法供父组件调用
defineExpose({
  loadAllFeatures,
  clearData
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

.tab-bar button:active {
  transform: translateY(0);
}

.tab-content {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
