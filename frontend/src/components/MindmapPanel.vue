<template>
  <div class="mindmap-panel">
    <!-- 初始状态 -->
    <div v-if="!summaryData && !isLoading" class="text-center py-12">
      <div class="w-24 h-24 bg-gradient-to-r from-green-100 to-teal-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path>
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900 mb-3">思维导图</h3>
      <p class="text-gray-600 mb-8 max-w-md mx-auto">
        将视频总结转换为可视化思维导图，帮助快速理解内容结构
      </p>
      <p class="text-sm text-gray-500 mb-4">请先生成视频总结</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p class="text-gray-600">正在生成思维导图...</p>
    </div>

    <!-- 思维导图内容 -->
    <div v-if="summaryData && !isLoading">
      <!-- 工具栏 -->
      <div class="flex flex-wrap items-center justify-between gap-4 mb-6 p-4 bg-gray-50 rounded-xl">
        <div class="flex items-center gap-2">
          <button
            @click="zoomIn"
            class="p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
            title="放大"
          >
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0 0h3m-3 0H7"></path>
            </svg>
          </button>
          <button
            @click="zoomOut"
            class="p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
            title="缩小"
          >
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"></path>
            </svg>
          </button>
          <button
            @click="resetZoom"
            class="p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
            title="重置"
          >
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
          <button
            @click="fitToScreen"
            class="p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
            title="适应屏幕"
          >
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
            </svg>
          </button>
          <span class="text-sm text-gray-600 ml-2">{{ Math.round(scale * 100) }}%</span>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="toggleView"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {{ viewMode === 'interactive' ? 'Markdown视图' : '交互视图' }}
          </button>
          <button
            @click="exportMindmap"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            导出
          </button>
        </div>
      </div>

      <!-- 思维导图画布 -->
      <div
        ref="canvasContainer"
        class="mindmap-canvas border border-gray-200 rounded-xl overflow-hidden"
        :style="{ height: '550px', cursor: viewMode === 'interactive' ? (isDragging ? 'grabbing' : 'grab') : 'default' }"
        @mousedown="viewMode === 'interactive' ? startDrag : null"
        @mousemove="viewMode === 'interactive' ? onDrag : null"
        @mouseup="viewMode === 'interactive' ? stopDrag : null"
        @mouseleave="viewMode === 'interactive' ? stopDrag : null"
        @wheel="viewMode === 'interactive' ? onWheel : null"
      >
        <!-- SVG交互式思维导图 -->
        <svg
          v-if="viewMode === 'interactive'"
          ref="svgMindmap"
          class="mindmap-svg w-full h-full"
          :style="{ backgroundColor: '#ffffff' }"
        ></svg>

        <!-- Markdown文本视图 -->
        <pre
          v-else
          class="mindmap-markdown p-6 overflow-auto"
          :style="{ height: '100%', maxWidth: '100%' }"
        >{{ mindmapMarkdown }}</pre>
      </div>

      <!-- 操作提示 -->
      <div class="mt-6 p-4 bg-teal-50 rounded-xl">
        <h4 class="font-semibold text-gray-900 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          操作提示
        </h4>
        <ul class="text-sm text-gray-600 space-y-1">
          <li v-if="viewMode === 'interactive'">• 鼠标滚轮缩放，拖拽移动导图</li>
          <li>• 点击节点可展开/收起子内容</li>
          <li>• 切换视图模式查看不同展示方式</li>
          <li>• 导出为Markdown格式可用于其他工具</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'

const props = defineProps({
  videoUrl: String,
  videoTitle: String,
  isLoading: Boolean,
  summaryData: Object
})

const emit = defineEmits(['generate-mindmap', 'seek-timestamp'])

// Refs
const canvasContainer = ref(null)
const svgMindmap = ref(null)

// 状态
const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const viewMode = ref('interactive') // 'interactive' 或 'markdown'
const markmapInstance = ref(null)

// 计算属性
const mindmapMarkdown = computed(() => {
  if (!props.summaryData) return ''

  let md = `# ${props.summaryData.overview?.substring(0, 50) || '视频主题'}...\n\n`

  // 从outline生成主要分支
  if (props.summaryData.outline?.length) {
    props.summaryData.outline.forEach((outline, index) => {
      md += `## ${index + 1}. ${outline.title}\n`
      // 提取关键点作为子节点
      const content = outline.content || ''
      const sentences = content.split('。').filter(s => s.trim().length > 5)
      sentences.slice(0, 3).forEach(sentence => {
        md += `- ${sentence.trim()}。\n`
      })
      md += '\n'
    })
  }

  // 从key_points生成额外分支
  if (props.summaryData.key_points?.length) {
    md += `## 核心要点\n`
    props.summaryData.key_points.forEach(point => {
      md += `- ${point.point}\n`
    })
    md += '\n'
  }

  // 从conclusion生成总结分支
  if (props.summaryData.conclusion?.takeaways?.length) {
    md += `## 主要收获\n`
    props.summaryData.conclusion.takeaways.forEach(takeaway => {
      md += `- ${takeaway}\n`
    })
  }

  return md
})

// 监听summaryData变化，重新渲染思维导图
watch(() => props.summaryData, async (newData) => {
  if (newData && viewMode.value === 'interactive') {
    await nextTick()
    renderMindmap()
  }
}, { immediate: true })

// 渲染交互式思维导图
const renderMindmap = async () => {
  if (!svgMindmap.value || !mindmapMarkdown.value) return

  try {
    // 创建Transformer
    const transformer = new Transformer()

    // 转换markdown为思维导图数据
    const { root, features } = transformer.transform(mindmapMarkdown.value)

    // 如果已有实例，先销毁
    if (markmapInstance.value) {
      markmapInstance.value = null
    }

    // 创建markmap实例
    markmapInstance.value = Markmap.create(svgMindmap.value, {
      autoFit: true,
      fitRatio: 0.95,
      duration: 500
    })

    // 设置数据
    markmapInstance.value.setData(root)
    markmapInstance.value.fit()

  } catch (error) {
    console.error('思维导图渲染失败:', error)
    // 降级到markdown视图
    viewMode.value = 'markdown'
  }
}

// 方法
const zoomIn = () => {
  if (viewMode.value === 'interactive' && markmapInstance.value) {
    markmapInstance.value.fit()
  } else {
    scale.value = Math.min(scale.value * 1.2, 3)
  }
}

const zoomOut = () => {
  if (viewMode.value === 'interactive' && markmapInstance.value) {
    markmapInstance.value.fit()
  } else {
    scale.value = Math.max(scale.value / 1.2, 0.3)
  }
}

const resetZoom = () => {
  if (viewMode.value === 'interactive' && markmapInstance.value) {
    markmapInstance.value.fit()
  } else {
    scale.value = 1
  }
}

const fitToScreen = () => {
  if (viewMode.value === 'interactive' && markmapInstance.value) {
    markmapInstance.value.fit()
  }
}

const toggleView = async () => {
  viewMode.value = viewMode.value === 'interactive' ? 'markdown' : 'interactive'

  if (viewMode.value === 'interactive') {
    await nextTick()
    renderMindmap()
  }
}

const startDrag = (e) => {
  isDragging.value = true
  dragStartX.value = e.clientX - translateX.value
  dragStartY.value = e.clientY - translateY.value
}

const onDrag = (e) => {
  if (!isDragging.value || !markmapInstance.value) return

  // markmap有自己的拖拽处理，这里不需要额外处理
}

const stopDrag = () => {
  isDragging.value = false
}

const onWheel = (e) => {
  if (viewMode.value === 'interactive' && markmapInstance.value) {
    // markmap有自己的滚轮处理
    return
  }
  e.preventDefault()
}

const exportMindmap = () => {
  const blob = new Blob([mindmapMarkdown.value], { type: 'text/markdown' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.videoTitle || '思维导图'}_${Date.now()}.md`
  link.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('导出成功！')
}

// 组件挂载后初始化
onMounted(async () => {
  if (props.summaryData && viewMode.value === 'interactive') {
    await nextTick()
    renderMindmap()
  }
})

// 组件卸载时清理
onUnmounted(() => {
  if (markmapInstance.value) {
    markmapInstance.value = null
  }
})
</script>

<style scoped>
.mindmap-canvas {
  position: relative;
}

.mindmap-svg {
  display: block;
}

.mindmap-markdown {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  background: #f8f9fa;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* markmap样式覆盖 */
:deep(.markmap) {
  width: 100%;
  height: 100%;
}

:deep(.markmap svg) {
  width: 100%;
  height: 100%;
}
</style>
