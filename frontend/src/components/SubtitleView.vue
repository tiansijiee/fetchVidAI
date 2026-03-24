<template>
  <div class="subtitle-view">
    <!-- 搜索栏 -->
    <div class="mb-4 flex gap-2">
      <div class="flex-1 relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索字幕内容..."
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @input="onSearch"
        >
        <svg class="w-5 h-5 absolute right-3 top-2.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
      <button
        @click="toggleExpandAll"
        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
      >
        {{ allExpanded ? '收起全部' : '展开全部' }}
      </button>
    </div>

    <!-- 字幕统计 -->
    <div class="mb-4 p-3 bg-gray-50 rounded-lg flex items-center justify-between">
      <div class="flex items-center gap-4 text-sm text-gray-600">
        <span>共 {{ filteredSubtitles.length }} 条字幕</span>
        <span v-if="searchQuery">找到 {{ searchResults.length }} 条匹配</span>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600">显示:</label>
        <select
          v-model="displayMode"
          class="px-2 py-1 border border-gray-300 rounded text-sm"
        >
          <option value="all">全部</option>
          <option value="expanded">仅展开</option>
          <option value="collapsed">仅收起</option>
        </select>
      </div>
    </div>

    <!-- 字幕列表 -->
    <div class="subtitle-list space-y-2 max-h-[500px] overflow-y-auto">
      <div
        v-for="(subtitle, index) in displaySubtitles"
        :key="index"
        class="subtitle-item p-3 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
        :class="{
          'expanded': expandedIndexes.has(index),
          'highlight': isHighlighted(subtitle)
        }"
      >
        <div
          class="flex items-start justify-between cursor-pointer"
          @click="toggleExpand(index)"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs font-mono bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                {{ subtitle.time || subtitle.start_time }}
              </span>
              <span class="text-xs text-gray-500">#{{ index + 1 }}</span>
            </div>
            <p
              class="text-sm text-gray-700"
              :class="{
                'line-clamp-2': !expandedIndexes.has(index),
                'line-clamp-none': expandedIndexes.has(index)
              }"
            >
              {{ highlightText(subtitle.text) }}
            </p>
          </div>
          <button
            @click.stop="seekToTimestamp(subtitle.start_time || subtitle.time)"
            class="ml-2 p-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors flex-shrink-0"
            title="跳转到此时间"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="displaySubtitles.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <p>{{ searchQuery ? '未找到匹配的字幕' : '暂无字幕' }}</p>
      </div>
    </div>

    <!-- 操作提示 -->
    <div class="mt-4 p-4 bg-blue-50 rounded-lg">
      <h4 class="font-semibold text-gray-900 mb-2">操作提示</h4>
      <ul class="text-sm text-gray-600 space-y-1">
        <li>• 点击字幕内容展开/收起</li>
        <li>• 点击蓝色按钮跳转到对应时间点</li>
        <li>• 使用搜索框快速定位内容</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  videoUrl: {
    type: String,
    required: true
  },
  videoTitle: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['seek-timestamp'])

// 状态
const searchQuery = ref('')
const subtitles = ref([])
const expandedIndexes = ref(new Set())
const allExpanded = ref(false)
const displayMode = ref('all')

// 计算属性
const filteredSubtitles = computed(() => {
  return subtitles.value
})

const searchResults = computed(() => {
  if (!searchQuery.value.trim()) return []

  const query = searchQuery.value.toLowerCase()
  return subtitles.value.filter(subtitle =>
    subtitle.text.toLowerCase().includes(query)
  )
})

const displaySubtitles = computed(() => {
  let result = filteredSubtitles.value

  // 搜索过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(subtitle =>
      subtitle.text.toLowerCase().includes(query)
    )
  }

  // 显示模式过滤
  if (displayMode.value === 'expanded') {
    result = result.filter((_, index) => expandedIndexes.value.has(index))
  } else if (displayMode.value === 'collapsed') {
    result = result.filter((_, index) => !expandedIndexes.value.has(index))
  }

  return result
})

// 方法
const loadSubtitles = async () => {
  try {
    const response = await fetch('/api/ai/check-subtitle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: props.videoUrl })
    })

    const result = await response.json()

    if (result.success && result.has_subtitle) {
      // 如果有字幕，提取完整字幕数据
      const summaryResponse = await fetch('/api/ai/summarize/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: props.videoUrl,
          title: props.videoTitle,
          description: ''
        })
      })

      // 从总结结果中获取字幕
      // 这里需要根据实际API响应调整
      // 暂时使用空数组
      subtitles.value = []
    } else {
      // 使用模拟数据演示
      subtitles.value = generateMockSubtitles()
    }
  } catch (err) {
    console.error('加载字幕失败:', err)
    // 使用模拟数据演示
    subtitles.value = generateMockSubtitles()
  }
}

const generateMockSubtitles = () => {
  return [
    { time: '00:00', start_time: '00:00', end_time: '00:10', text: '大家好，欢迎来到我的频道' },
    { time: '00:10', start_time: '00:10', end_time: '00:20', text: '今天我们要讨论一个非常重要的话题' },
    { time: '00:20', start_time: '00:20', end_time: '00:30', text: '关于如何提高学习效率' },
    { time: '00:30', start_time: '00:30', end_time: '00:40', text: '首先，我们需要了解大脑的工作原理' },
    { time: '00:40', start_time: '00:40', end_time: '00:50', text: '研究表明，专注力是有限资源' },
    { time: '00:50', start_time: '00:50', end_time: '01:00', text: '合理安排休息时间非常重要' },
    { time: '01:00', start_time: '01:00', end_time: '01:10', text: '现在让我们看看具体的方法' },
    { time: '01:10', start_time: '01:10', end_time: '01:20', text: '第一，使用番茄工作法' },
    { time: '01:20', start_time: '01:20', end_time: '01:30', text: '第二，创造良好的学习环境' },
    { time: '01:30', start_time: '01:30', end_time: '01:40', text: '第三，保持充足的运动' }
  ]
}

const toggleExpand = (index) => {
  if (expandedIndexes.value.has(index)) {
    expandedIndexes.value.delete(index)
  } else {
    expandedIndexes.value.add(index)
  }
}

const toggleExpandAll = () => {
  if (allExpanded.value) {
    expandedIndexes.value.clear()
    allExpanded.value = false
  } else {
    subtitles.value.forEach((_, index) => {
      expandedIndexes.value.add(index)
    })
    allExpanded.value = true
  }
}

const onSearch = () => {
  // 搜索时自动展开匹配项
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    subtitles.value.forEach((subtitle, index) => {
      if (subtitle.text.toLowerCase().includes(query)) {
        expandedIndexes.value.add(index)
      }
    })
  }
}

const isHighlighted = (subtitle) => {
  if (!searchQuery.value.trim()) return false
  const query = searchQuery.value.toLowerCase()
  return subtitle.text.toLowerCase().includes(query)
}

const highlightText = (text) => {
  if (!searchQuery.value.trim()) return text

  const query = searchQuery.value
  const regex = new RegExp(`(${query})`, 'gi')
  return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>')
}

const seekToTimestamp = (timestamp) => {
  // 解析时间戳
  const match = timestamp.match(/(\d{1,2}:\d{2})/)
  if (match) {
    const timeStr = match[1]
    const [minutes, seconds] = timeStr.split(':').map(Number)
    const totalSeconds = minutes * 60 + seconds

    ElMessage.info(`跳转到时间: ${timeStr}`)

    // 发射事件给父组件
    emit('seek-timestamp', { time: timeStr, seconds: totalSeconds })
  }
}

onMounted(() => {
  loadSubtitles()
})
</script>

<style scoped>
.subtitle-view {
  width: 100%;
}

.subtitle-item {
  transition: all 0.2s ease;
}

.subtitle-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.subtitle-item.highlight {
  background-color: #fef3c7;
  border-color: #fbbf24;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-none {
  display: block;
}

:deep(mark) {
  padding: 0 2px;
  border-radius: 2px;
}
</style>
