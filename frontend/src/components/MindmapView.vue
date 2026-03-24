<template>
  <div class="mindmap-container">
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-600">缩放:</span>
        <button
          @click="zoomIn"
          class="p-2 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
          title="放大"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"></path>
          </svg>
        </button>
        <button
          @click="zoomOut"
          class="p-2 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
          title="缩小"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"></path>
          </svg>
        </button>
        <button
          @click="resetZoom"
          class="p-2 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
          title="重置"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>
      <span class="text-sm text-gray-500">{{ Math.round(scale * 100) }}%</span>
    </div>

    <div
      ref="mindmapContainer"
      class="mindmap-canvas border border-gray-200 rounded-xl overflow-hidden"
      :style="{ height: '600px', cursor: isDragging ? 'grabbing' : 'grab' }"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="stopDrag"
      @mouseleave="stopDrag"
      @wheel="onWheel"
    >
      <svg
        ref="mindmapSvg"
        :style="svgStyle"
        class="mindmap-svg"
      >
        <!-- 这里将使用markmap渲染思维导图 -->
        <g ref="mindmapGroup">
          <foreignObject
            :x="0"
            :y="0"
            :width="800"
            :height="600"
          >
            <div
              ref="markmapContent"
              class="markmap-content"
              xmlns="http://www.w3.org/1999/xhtml"
            >
              <pre>{{ mindmapMarkdown }}</pre>
            </div>
          </foreignObject>
        </g>
      </svg>
    </div>

    <div class="mt-4 p-4 bg-blue-50 rounded-lg">
      <h4 class="font-semibold text-gray-900 mb-2">操作提示</h4>
      <ul class="text-sm text-gray-600 space-y-1">
        <li>• 鼠标拖拽移动思维导图</li>
        <li>• 鼠标滚轮缩放</li>
        <li>• 点击时间戳可跳转到对应位置</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  summaryData: {
    type: Object,
    required: true
  },
  videoTitle: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['seek-timestamp'])

// Refs
const mindmapContainer = ref(null)
const mindmapSvg = ref(null)
const markmapContent = ref(null)

// 状态
const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)

// 计算属性
const svgStyle = computed(() => ({
  transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value})`,
  transformOrigin: '0 0',
  transition: isDragging.value ? 'none' : 'transform 0.1s ease-out'
}))

const mindmapMarkdown = computed(() => {
  if (!props.summaryData) return ''

  let markdown = `# ${props.videoTitle || '视频主题'}\n\n`

  // 从outline生成主要分支
  if (props.summaryData.outline?.length) {
    props.summaryData.outline.forEach(outline => {
      markdown += `## ${outline.title}\n`
      // 提取关键点作为子节点
      if (outline.content) {
        const sentences = outline.content.split('。').filter(s => s.trim().length > 5)
        sentences.slice(0, 3).forEach(sentence => {
          markdown += `- ${sentence.trim()}。\n`
        })
      }
    })
  }

  // 从key_points生成额外分支
  if (props.summaryData.key_points?.length) {
    markdown += `\n## 核心要点\n`
    props.summaryData.key_points.forEach(point => {
      markdown += `- ${point.point}\n`
    })
  }

  // 从conclusion生成总结分支
  if (props.summaryData.conclusion?.takeaways?.length) {
    markdown += `\n## 主要收获\n`
    props.summaryData.conclusion.takeaways.forEach(takeaway => {
      markdown += `- ${takeaway}\n`
    })
  }

  return markdown
})

// 方法
const zoomIn = () => {
  scale.value = Math.min(scale.value * 1.2, 3)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value / 1.2, 0.3)
}

const resetZoom = () => {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
}

const startDrag = (e) => {
  isDragging.value = true
  dragStartX.value = e.clientX - translateX.value
  dragStartY.value = e.clientY - translateY.value
}

const onDrag = (e) => {
  if (!isDragging.value) return
  translateX.value = e.clientX - dragStartX.value
  translateY.value = e.clientY - dragStartY.value
}

const stopDrag = () => {
  isDragging.value = false
}

const onWheel = (e) => {
  e.preventDefault()
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  scale.value = Math.max(0.3, Math.min(3, scale.value * delta))
}

// 初始化markmap
const initMarkmap = async () => {
  await nextTick()

  try {
    // 检查markmap是否已安装
    const markmapInstalled = !!window.markmap

    if (!markmapInstalled) {
      // markmap未安装，显示简单版本
      console.warn('markmap未安装，显示简化版本')
      // 简化版本已通过模板渲染
      return
    }

    if (markmapContent.value && window.markmap && window.MarkmapTransformer) {
      const transformer = new window.MarkmapTransformer()
      const { root } = transformer.transform(mindmapMarkdown.value)

      // 清空现有内容
      markmapContent.value.innerHTML = ''

      // 创建markmap实例
      window.markmapInstance = window.markmap.Markmap.create(markmapContent.value, null, root)

      ElMessage.success('思维导图生成成功')
    }
  } catch (err) {
    console.error('markmap加载失败:', err)
    ElMessage.warning('思维导图加载失败，显示简化版本')
  }
}

// 监听数据变化
watch(() => props.summaryData, () => {
  initMarkmap()
}, { deep: true })

onMounted(() => {
  initMarkmap()
})
</script>

<style scoped>
.mindmap-container {
  width: 100%;
}

.mindmap-canvas {
  background: white;
  position: relative;
}

.mindmap-svg {
  width: 100%;
  height: 100%;
}

.markmap-content {
  width: 100%;
  height: 100%;
  overflow: auto;
}

.markmap-content pre {
  margin: 0;
  padding: 20px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  background: #f8f9fa;
  border-radius: 8px;
}
</style>
