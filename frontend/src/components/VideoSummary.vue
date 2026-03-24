<template>
  <div class="video-summary">
    <!-- 初始状态 -->
    <div v-if="!summaryData && !isLoading" class="text-center py-12">
      <div class="w-24 h-24 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-12 h-12 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900 mb-3">AI智能总结</h3>
      <p class="text-gray-600 mb-8 max-w-md mx-auto">
        基于视频内容生成结构化总结，包含概述、大纲、要点和结论
      </p>
      <button
        @click="$emit('start-analysis')"
        class="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-medium hover:from-purple-600 hover:to-pink-600 transition-all flex items-center justify-center gap-2 mx-auto shadow-lg shadow-purple-500/30"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
        </svg>
        开始AI分析
      </button>
    </div>

    <!-- 加载状态 + 打字机效果 -->
    <div v-if="isLoading && !summaryData" class="text-center py-12">
      <!-- 有流式内容时显示打字机效果 -->
      <div v-if="displayContent" class="space-y-6">
        <section class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 text-left">
          <div class="flex items-center gap-2 mb-4">
            <div class="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900">AI正在思考...</h3>
          </div>
          <div class="flex items-start gap-2 text-gray-700">
            <span class="typing-cursor flex-shrink-0 mt-1"></span>
            <p class="flex-1 whitespace-pre-wrap">{{ displayContent }}</p>
          </div>
        </section>
      </div>

      <!-- 没有流式内容时显示加载动画 -->
      <div v-else>
        <div class="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">{{ streamingContent || 'AI正在分析视频内容...' }}</p>
        <p class="text-sm text-gray-500 mt-2">这可能需要30-60秒</p>
      </div>
    </div>

    <!-- 总结结果 - 4板块结构 -->
    <div v-if="summaryData" class="space-y-6">
      <!-- Section 1: 视频概述 -->
      <section class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">视频概述</h3>
        </div>
        <p class="text-gray-700 leading-relaxed">{{ summaryData.overview }}</p>
      </section>

      <!-- Section 2: 内容大纲 -->
      <section class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">内容大纲</h3>
        </div>
        <div class="space-y-4">
          <div
            v-for="(outline, index) in summaryData.outline"
            :key="index"
            class="border-l-4 border-blue-200 pl-4 hover:border-blue-400 transition-colors"
          >
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-semibold text-gray-900">{{ outline.title }}</h4>
              <button
                v-if="outline.timestamp"
                @click="$emit('seek-timestamp', { time: outline.timestamp.split('-')[0], seconds: parseTime(outline.timestamp.split('-')[0]) })"
                class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 transition-colors flex-shrink-0"
              >
                {{ outline.timestamp }}
              </button>
            </div>
            <p class="text-sm text-gray-600">{{ outline.content }}</p>
          </div>
        </div>
      </section>

      <!-- Section 3: 核心要点 -->
      <section class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-10 h-10 bg-yellow-500 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 01-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 01-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">核心要点</h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="(point, index) in summaryData.key_points"
            :key="index"
            class="p-4 bg-yellow-50 rounded-xl hover:bg-yellow-100 transition-colors"
          >
            <div class="flex items-start gap-2">
              <span class="text-yellow-500 text-lg">{{ '⭐'.repeat(Math.min(point.importance || 3, 5)) }}</span>
              <p class="text-sm text-gray-700 flex-1">{{ point.point }}</p>
            </div>
            <div v-if="point.timestamp" class="mt-2">
              <button
                @click="$emit('seek-timestamp', { time: point.timestamp, seconds: parseTime(point.timestamp) })"
                class="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded hover:bg-yellow-300 transition-colors"
              >
                {{ point.timestamp }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 4: 总结结论 -->
      <section v-if="summaryData.conclusion" class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">总结结论</h3>
        </div>
        <div class="space-y-4">
          <div v-if="summaryData.conclusion.summary" class="p-4 bg-green-50 rounded-xl">
            <p class="text-gray-700">{{ summaryData.conclusion.summary }}</p>
          </div>

          <div v-if="summaryData.conclusion.takeaways && summaryData.conclusion.takeaways.length" class="space-y-2">
            <h4 class="font-semibold text-gray-900 flex items-center gap-2">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              主要收获
            </h4>
            <ul class="space-y-2">
              <li v-for="(takeaway, index) in summaryData.conclusion.takeaways" :key="index" class="text-sm text-gray-600 flex items-start gap-2">
                <svg class="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                {{ takeaway }}
              </li>
            </ul>
          </div>

          <div v-if="summaryData.conclusion.recommendations && summaryData.conclusion.recommendations.length" class="space-y-2">
            <h4 class="font-semibold text-gray-900 flex items-center gap-2">
              <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              建议
            </h4>
            <ul class="space-y-2">
              <li v-for="(rec, index) in summaryData.conclusion.recommendations" :key="index" class="text-sm text-gray-600 flex items-start gap-2">
                <svg class="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                {{ rec }}
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 操作按钮 -->
      <div class="flex flex-wrap gap-3 justify-center">
        <button
          @click="exportSummary"
          class="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          导出总结
        </button>
        <button
          @click="$emit('seek-timestamp', { time: '00:00', seconds: 0 })"
          class="px-6 py-3 bg-purple-100 text-purple-700 rounded-xl hover:bg-purple-200 transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          重新观看视频
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  videoUrl: String,
  videoTitle: String,
  videoDescription: String,
  videoThumbnail: String,
  isLoading: Boolean,
  summaryData: Object,
  streamingContent: String
})

const emit = defineEmits(['start-analysis', 'seek-timestamp'])

// 打字机效果相关
const displayContent = ref('')
let typewriterInterval = null

// 监听streamingContent变化，实现打字机效果
watch(() => props.streamingContent, (newContent) => {
  if (newContent && !props.summaryData) {
    // 清除之前的定时器
    if (typewriterInterval) {
      clearInterval(typewriterInterval)
    }

    // 计算需要新增的字符
    const currentLength = displayContent.value.length
    const targetLength = newContent.length

    // 如果新内容更长，逐步显示
    if (targetLength > currentLength) {
      typewriterInterval = setInterval(() => {
        if (displayContent.value.length < targetLength) {
          displayContent.value = newContent.substring(0, displayContent.value.length + 3)
        } else {
          clearInterval(typewriterInterval)
        }
      }, 20) // 每20ms显示3个字符，加快速度
    } else {
      displayContent.value = newContent
    }
  } else if (!newContent && !props.summaryData) {
    // 清空内容
    displayContent.value = ''
  }
}, { immediate: true })

// 组件卸载时清除定时器
onUnmounted(() => {
  if (typewriterInterval) {
    clearInterval(typewriterInterval)
  }
})

const parseTime = (timeStr) => {
  const match = timeStr.match(/(\d{1,2}):(\d{2})/)
  if (match) {
    const [, minutes, seconds] = match
    return parseInt(minutes) * 60 + parseInt(seconds)
  }
  return 0
}

const exportSummary = () => {
  if (!props.summaryData) return

  let md = `# ${props.videoTitle || '视频总结'}\n\n`

  // Section 1: 视频概述
  if (props.summaryData.overview) {
    md += `## 🎯 视频概述\n\n${props.summaryData.overview}\n\n`
  }

  // Section 2: 内容大纲
  if (props.summaryData.outline?.length) {
    md += `## 📚 内容大纲\n\n`
    props.summaryData.outline.forEach((outline, index) => {
      md += `### ${index + 1}. ${outline.title}\n\n`
      md += `${outline.content}\n\n`
      if (outline.timestamp) {
        md += `⏱️ 时间: ${outline.timestamp}\n\n`
      }
    })
  }

  // Section 3: 核心要点
  if (props.summaryData.key_points?.length) {
    md += `## 💡 核心要点\n\n`
    props.summaryData.key_points.forEach(point => {
      const stars = '⭐'.repeat(Math.min(point.importance || 3, 5))
      md += `- ${stars} ${point.point}\n`
    })
    md += '\n'
  }

  // Section 4: 总结结论
  if (props.summaryData.conclusion) {
    md += `## 📝 总结结论\n\n`
    if (props.summaryData.conclusion.summary) {
      md += `**总结**: ${props.summaryData.conclusion.summary}\n\n`
    }
    if (props.summaryData.conclusion.takeaways?.length) {
      md += `**主要收获**:\n\n`
      props.summaryData.conclusion.takeaways.forEach(takeaway => {
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
  link.download = `${props.videoTitle || '视频总结'}_${Date.now()}.md`
  link.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('导出成功！')
}
</script>

<style scoped>
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

.animate-fadeIn {
  animation: fadeIn 0.5s ease-out forwards;
  opacity: 0;
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background-color: #8b5cf6;
  animation: blink 1s infinite;
  margin-right: 2px;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

section {
  animation: fadeIn 0.5s ease-out forwards;
}

section:nth-child(1) { animation-delay: 0s; }
section:nth-child(2) { animation-delay: 0.1s; }
section:nth-child(3) { animation-delay: 0.2s; }
section:nth-child(4) { animation-delay: 0.3s; }
</style>
