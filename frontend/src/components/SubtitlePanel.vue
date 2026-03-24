<template>
  <div class="subtitle-panel">
    <!-- 初始状态 -->
    <div v-if="subtitles.length === 0 && !isLoading" class="text-center py-12">
      <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      </div>
      <h3 class="text-xl font-bold text-gray-900 mb-2">视频字幕</h3>
      <p class="text-gray-600 mb-6 max-w-md mx-auto">
        查看完整视频字幕，支持时间跳转和关键词搜索
      </p>
      <button
        @click="$emit('load-subtitles')"
        class="px-6 py-3 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 transition-colors flex items-center justify-center gap-2 mx-auto"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
        </svg>
        加载字幕
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p class="text-gray-600">正在加载字幕...</p>
    </div>

    <!-- 字幕内容 -->
    <div v-if="subtitles.length > 0">
      <!-- 工具栏 -->
      <div class="flex flex-col sm:flex-row gap-4 mb-6 p-4 bg-gray-50 rounded-xl">
        <!-- 搜索框 -->
        <div class="flex-1 relative">
          <svg class="w-5 h-5 absolute left-3 top-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索字幕内容..."
            class="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
        </div>

        <!-- 统计和操作 -->
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-600">
            共 <span class="font-semibold text-blue-600">{{ filteredSubtitles.length }}</span> 条字幕
          </span>
          <button
            @click="toggleExpandAll"
            class="px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
          >
            {{ allExpanded ? '收起全部' : '展开全部' }}
          </button>
        </div>
      </div>

      <!-- 字幕列表 -->
      <div class="space-y-2 max-h-[500px] overflow-y-auto pr-2">
        <div
          v-for="(subtitle, index) in filteredSubtitles"
          :key="index"
          class="subtitle-item p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-300 transition-colors"
          :class="{ 'bg-blue-50 border-blue-300': isHighlighted(subtitle) }"
        >
          <div class="flex items-start gap-3">
            <!-- 时间戳 -->
            <button
              @click="$emit('seek-timestamp', { time: subtitle.time, seconds: parseTime(subtitle.time) })"
              class="flex-shrink-0 px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg text-sm font-mono hover:bg-blue-200 transition-colors"
            >
              {{ subtitle.time }}
            </button>

            <!-- 内容 -->
            <div class="flex-1 min-w-0">
              <p
                class="text-gray-700 cursor-pointer"
                :class="{
                  'line-clamp-2': !expandedIndexes.has(index),
                  'line-clamp-none': expandedIndexes.has(index)
                }"
                @click="toggleExpand(index)"
                v-html="highlightText(subtitle.text)"
              ></p>
            </div>

            <!-- 展开/收起按钮 -->
            <button
              @click="toggleExpand(index)"
              class="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg v-if="!expandedIndexes.has(index)" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
              </svg>
            </button>
          </div>
        </div>

      </div>

      <!-- 空状态 -->
      <div v-if="filteredSubtitles.length === 0 && searchQuery" class="text-center py-12">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <p class="text-gray-500">未找到匹配的字幕</p>
        <button
          @click="searchQuery = ''"
          class="mt-4 text-blue-600 hover:text-blue-700 font-medium"
        >
          清除搜索
        </button>
      </div>

      <!-- 操作提示 -->
      <div class="mt-6 p-4 bg-blue-50 rounded-xl">
        <h4 class="font-semibold text-gray-900 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          操作提示
        </h4>
        <ul class="text-sm text-gray-600 space-y-1">
          <li>• 点击时间戳跳转到视频对应位置</li>
          <li>• 点击字幕内容展开/收起</li>
          <li>• 使用搜索框快速定位关键词</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  videoUrl: String,
  videoTitle: String,
  isLoading: Boolean,
  subtitles: Array
})

const emit = defineEmits(['load-subtitles', 'seek-timestamp'])

// 状态
const searchQuery = ref('')
const expandedIndexes = ref(new Set())
const allExpanded = ref(false)

// 计算属性
const filteredSubtitles = computed(() => {
  if (!props.subtitles || props.subtitles.length === 0) return []

  if (!searchQuery.value.trim()) {
    return props.subtitles
  }

  const query = searchQuery.value.toLowerCase()
  return props.subtitles.filter(subtitle =>
    subtitle.text.toLowerCase().includes(query)
  )
})

// 方法
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
    props.subtitles.forEach((_, index) => {
      expandedIndexes.value.add(index)
    })
    allExpanded.value = true
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
  return text.replace(regex, '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>')
}

const parseTime = (timeStr) => {
  const match = timeStr.match(/(\d{1,2}):(\d{2})/)
  if (match) {
    const [, minutes, seconds] = match
    return parseInt(minutes) * 60 + parseInt(seconds)
  }
  return 0
}
</script>

<style scoped>
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
  background-color: #fef08a;
  padding: 0 2px;
  border-radius: 2px;
}
</style>
