<template>
  <div class="mindmap-panel">
    <!-- 初始状态 -->
    <div v-if="!mindmapContent && !isLoading" class="text-center py-12">
      <div class="w-24 h-24 bg-gradient-to-br from-green-100 to-teal-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
        <svg class="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path>
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900 mb-3">思维导图</h3>
      <p class="text-gray-600 mb-8 max-w-md mx-auto">
        将视频总结转换为可视化思维导图，帮助快速理解内容结构
      </p>
      <p class="text-sm text-gray-500">请先生成视频总结</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="w-20 h-20 relative mx-auto mb-6">
        <div class="absolute inset-0 border-4 border-green-200 rounded-full"></div>
        <div class="absolute inset-0 border-4 border-green-500 rounded-full border-t-transparent animate-spin"></div>
        <div class="absolute inset-3 bg-gradient-to-br from-green-500 to-teal-500 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path>
          </svg>
        </div>
      </div>
      <h3 class="text-lg font-bold text-gray-900 mb-2">正在生成思维导图...</h3>
      <p class="text-sm text-gray-600">请稍候</p>
    </div>

    <!-- 思维导图内容 -->
    <div v-if="mindmapContent && !isLoading">
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
          <!-- 导出按钮容器 -->
          <div class="relative export-button-container">
            <button
              @click="showExportMenu = !showExportMenu"
              class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              导出
              <svg v-if="showExportMenu" class="w-3 h-3 ml-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>

              <!-- 导出格式菜单 -->
              <div
                v-if="showExportMenu"
                class="absolute top-full right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-50 min-w-[140px]"
                @click.stop
              >
                <button
                  @click="exportMarkdown"
                  class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  📄 Markdown (.md)
                </button>
                <button
                  @click="exportPNG"
                  class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  🖼️ PNG 图片
                </button>
                <button
                  @click="exportSVG"
                  class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  📊 SVG 矢量
                </button>
              </div>
            </button>
          </div>
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
        <svg
          v-if="viewMode === 'interactive'"
          ref="svgMindmap"
          class="mindmap-svg w-full h-full"
          :style="{ backgroundColor: '#ffffff' }"
        ></svg>

        <pre
          v-else
          class="mindmap-markdown p-6 overflow-auto"
          :style="{ height: '100%', maxWidth: '100%' }"
        >{{ mindmapContent }}</pre>
      </div>

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

        <!-- 调试按钮 -->
        <div class="mt-4 pt-4 border-t border-teal-200">
          <button
            @click="testWithMockData"
            class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm font-medium"
          >
            🧪 测试模拟数据
          </button>
          <span class="ml-3 text-xs text-orange-600">点击测试思维导图是否正常工作</span>
        </div>

        <!-- 调试信息显示 -->
        <div class="mt-4 pt-4 border-t border-teal-200">
          <h5 class="font-medium text-gray-900 mb-2">🔍 调试信息</h5>
          <div class="text-xs text-gray-600 space-y-1">
            <p>• Markdown长度: {{ mindmapContent?.length || 0 }} 字符</p>
            <p>• 视图模式: {{ viewMode }}</p>
            <p>• Markmap实例: {{ markmapInstance ? '已创建' : '未创建' }}</p>
            <p>• SVG元素: {{ svgMindmap ? '已挂载' : '未挂载' }}</p>
          </div>
        </div>
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
  isLoading: Boolean,
  markdown: String
})

const emit = defineEmits(['generate-mindmap'])

const svgMindmap = ref(null)
const scale = ref(1)
const isDragging = ref(false)
const viewMode = ref('interactive')
const markmapInstance = ref(null)
const showExportMenu = ref(false)

// ==============================================
// 【调试模式】模拟数据用于测试
// ==============================================
const MOCK_MINDMAP_DATA = `# AI视频分析技术

## 视频概述
- 本视频介绍了人工智能在视频分析领域的应用
- 涵盖了深度学习模型和计算机视觉技术
- 探讨了实际应用场景和未来发展趋势

## 内容大纲

### 1. 视频分析基础
- 视频帧提取与预处理
- 特征提取技术
- 时序信息建模

### 2. 深度学习模型
- CNN卷积神经网络
- RNN循环神经网络
- Transformer注意力机制

### 3. 应用场景
- 智能监控系统
- 视频内容推荐
- 动作识别与分类

## 核心要点
- 深度学习显著提升了视频分析准确率
- 实时处理需要优化模型架构
- 多模态融合是未来发展方向

## 结论
AI视频分析技术正在快速发展，将在更多领域发挥重要作用`

const mindmapContent = computed(() => {
  const content = props.markdown || ''
  console.log('🔍 [MindmapPanel] mindmapContent computed called')
  console.log('📥 [MindmapPanel] props.markdown:', props.markdown)
  console.log('📤 [MindmapPanel] 返回内容长度:', content.length)
  console.log('📝 [MindmapPanel] 返回内容预览:', content.substring(0, 200))
  return content
})

// ==============================================
// 【调试模式】使用模拟数据测试
// ==============================================

watch(() => props.markdown, (newVal) => {
  console.log('🔍 [MindmapPanel] props.markdown changed')
  console.log('📥 [MindmapPanel] 新值:', newVal ? newVal.substring(0, 100) + '...' : '空')
  console.log('📏 [MindmapPanel] 长度:', newVal?.length || 0)
})

const clearSVG = () => {
  if (svgMindmap.value) svgMindmap.value.innerHTML = ''
  if (markmapInstance.value) {
    try { markmapInstance.value.destroy() } catch {}
    markmapInstance.value = null
  }
}

watch(mindmapContent, async (newVal) => {
  console.log('🔍 [MindmapPanel] mindmapContent watch triggered')
  console.log('📥 [MindmapPanel] newVal:', newVal ? '有内容' : '空')
  console.log('📏 [MindmapPanel] newVal.length:', newVal?.length || 0)
  console.log('🎯 [MindmapPanel] viewMode:', viewMode.value)

  if (newVal && viewMode.value === 'interactive') {
    console.log('✅ [MindmapPanel] 准备渲染思维导图')
    clearSVG()
    await nextTick()
    renderMindmap()
  } else {
    console.log('⏸️ [MindmapPanel] 跳过渲染，原因:', !newVal ? '内容为空' : '不是交互模式')
  }
}, { immediate: true })

// ==============================================
// 【调试模式】渲染思维导图（带详细日志）
// ==============================================
const renderMindmap = async () => {
  console.log('🚀 [MindmapPanel] renderMindmap 开始执行')
  console.log('📦 [MindmapPanel] svgMindmap.value:', svgMindmap.value)
  console.log('📝 [MindmapPanel] mindmapContent.value 长度:', mindmapContent.value?.length || 0)

  if (!svgMindmap.value) {
    console.error('❌ [MindmapPanel] svgMindmap 为空，无法渲染')
    return
  }

  if (!mindmapContent.value) {
    console.error('❌ [MindmapPanel] mindmapContent 为空，无法渲染')
    return
  }

  try {
    console.log('📊 [MindmapPanel] 开始转换 Markdown')
    const transformer = new Transformer()

    console.log('🔧 [MindmapPanel] 调用 transformer.transform()')
    console.log('📄 [MindmapPanel] 输入的 Markdown:', mindmapContent.value)

    const { root } = transformer.transform(mindmapContent.value)

    console.log('✅ [MindmapPanel] transform 成功')
    console.log('🌳 [MindmapPanel] 生成的根节点:', root)
    console.log('🌳 [MindmapPanel] 根节点类型:', root?.type)
    console.log('🌳 [MindmapPanel] 根节点内容:', root?.content)

    if (!root) {
      console.error('❌ [MindmapPanel] transformer 返回的 root 为空')
      return
    }

    console.log('🎨 [MindmapPanel] 创建 Markmap 实例')
    markmapInstance.value = Markmap.create(svgMindmap.value, {
      autoFit: true,
      fitRatio: 0.95, // 增大到0.95，让导图占据更多空间
      duration: 300,
      zoom: true,
      pan: true,
      initialExpandLevel: -1, // 展开所有节点
      spacingHorizontal: 120, // 水平间距
      spacingVertical: 10, // 垂直间距
      paddingX: 80 // 水平内边距
    })

    console.log('💾 [MindmapPanel] 设置数据到 Markmap')
    markmapInstance.value.setData(root)

    console.log('📐 [MindmapPanel] 调用 fit() 适配视图并优化缩放')
    setTimeout(() => {
      console.log('✅ [MindmapPanel] fit() 执行完成')
      markmapInstance.value?.fit()
      // 优化：根据内容长度动态调整缩放
      const contentLength = mindmapContent.value?.length || 0
      const scaleMultiplier = contentLength > 3000 ? 1.5 : contentLength > 1500 ? 1.8 : 2.0
      markmapInstance.value?.rescale(scaleMultiplier)

      // 使用 center() 方法居中显示
      setTimeout(() => {
        if (markmapInstance.value) {
          markmapInstance.value?.center()
        }
      }, 100)
    }, 100)

    console.log('🎉 [MindmapPanel] 渲染完成')

  } catch (error) {
    console.error('❌ [MindmapPanel] 渲染失败:', error)
    console.error('❌ [MindmapPanel] 错误堆栈:', error.stack)
    // 即使出错，也强制显示
    viewMode.value = 'markdown'
  }
}

// ==============================================
// 【调试模式】使用模拟数据测试
// ==============================================
const testWithMockData = () => {
  console.log('🧪 [MindmapPanel] 使用模拟数据测试')
  console.log('📝 [MindmapPanel] 模拟数据:', MOCK_MINDMAP_DATA)

  // 直接设置 props.markdown 为模拟数据
  // 注意：这里我们修改的是计算属性返回值，所以需要通过其他方式
  // 暂时切换到 markdown 视图查看模拟数据
  viewMode.value = 'markdown'

  // 创建一个临时的 mock 内容用于测试
  const mockContent = MOCK_MINDMAP_DATA

  console.log('🔄 [MindmapPanel] 清空 SVG')
  clearSVG()

  console.log('🔄 [MindmapPanel] 切换到交互模式并渲染')
  nextTick(() => {
    viewMode.value = 'interactive'
    nextTick(() => {
      // 直接使用模拟数据渲染
      try {
        const transformer = new Transformer()
        const { root } = transformer.transform(mockContent)
        console.log('🌳 [Mock测试] 根节点:', root)

        markmapInstance.value = Markmap.create(svgMindmap.value, {
          autoFit: true,
          fitRatio: 0.95
        })
        markmapInstance.value.setData(root)
        setTimeout(() => markmapInstance.value?.fit(), 100)

        console.log('✅ [Mock测试] 渲染成功')
      } catch (error) {
        console.error('❌ [Mock测试] 渲染失败:', error)
      }
    })
  })
}

const zoomIn = () => scale.value = Math.min(scale.value * 1.2, 3)
const zoomOut = () => scale.value = Math.max(scale.value / 1.2, 0.3)
const resetZoom = () => scale.value = 1
const fitToScreen = () => markmapInstance.value?.fit()

const toggleView = async () => {
  viewMode.value = viewMode.value === 'interactive' ? 'markdown' : 'interactive'
  if (viewMode.value === 'interactive') {
    await nextTick()
    renderMindmap()
  }
}

const startDrag = () => isDragging.value = true
const stopDrag = () => isDragging.value = false
const onDrag = () => {}
const onWheel = (e) => e.preventDefault()

// 导出为 Markdown
const exportMarkdown = () => {
  try {
    const blob = new Blob([mindmapContent.value], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `思维导图_${Date.now()}.md`
    a.click()
    URL.revokeObjectURL(url)
    showExportMenu.value = false
    ElMessage.success('Markdown 导出成功')
  } catch (error) {
    console.error('Markdown 导出失败:', error)
    ElMessage.error('Markdown 导出失败')
  }
}

// 导出为 PNG（需要 markmap 实例）
const exportPNG = async () => {
  if (!svgMindmap.value) {
    ElMessage.error('思维导图未加载，无法导出 PNG')
    return
  }

  try {
    // 获取 SVG 元素
    const svgElement = svgMindmap.value.querySelector('svg')
    if (!svgElement) {
      ElMessage.error('无法找到 SVG 元素')
      return
    }

    console.log('🖼️ [MindmapPanel] 开始 PNG 导出...')

    // 获取 SVG 的实际内容尺寸（不是视口尺寸）
    const bbox = svgElement.viewBox.baseVal
    const width = bbox.width || svgElement.clientWidth || 1200
    const height = bbox.height || svgElement.clientHeight || 800

    console.log(`📐 [MindmapPanel] SVG 尺寸: ${width}x${height}`)

    // 创建高分辨率 Canvas
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const scale = 2  // 2倍分辨率以获得更清晰的图片

    canvas.width = width * scale
    canvas.height = height * scale

    // 序列化 SVG
    const svgData = new XMLSerializer().serializeToString(svgElement)

    // 添加必要的命名空间和样式
    const svgElementWithNS = svgData.replace(
      '<svg',
      '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
    )

    // 构建 Blob URL
    const svgBlob = new Blob([svgElementWithNS], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(svgBlob)

    console.log('🔄 [MindmapPanel] 创建 SVG Blob URL:', url)

    // 创建图片对象
    const img = new Image()

    img.onload = () => {
      console.log('✅ [MindmapPanel] 图片加载成功，开始绘制到 Canvas...')

      // 设置白色背景
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // 绘制 SVG
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

      // 清理 Blob URL
      URL.revokeObjectURL(url)

      console.log('💾 [MindmapPanel] 开始导出 PNG...')

      // 导出为 PNG
      canvas.toBlob((blob) => {
        if (!blob) {
          console.error('❌ [MindmapPanel] Canvas to Blob 失败')
          ElMessage.error('PNG 导出失败，Canvas 转换出错')
          showExportMenu.value = false
          return
        }

        console.log('✅ [MindmapPanel] PNG Blob 创建成功，大小:', blob.size)

        const pngUrl = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = pngUrl
        a.download = `思维导图_${Date.now()}.png`
        a.click()
        URL.revokeObjectURL(pngUrl)

        showExportMenu.value = false
        ElMessage.success('PNG 导出成功')
        console.log('🎉 [MindmapPanel] PNG 导出完成')
      }, 'image/png')
    }

    img.onerror = (error) => {
      console.error('❌ [MindmapPanel] 图片加载失败:', error)
      URL.revokeObjectURL(url)
      ElMessage.error('PNG 导出失败，SVG 加载出错')
      showExportMenu.value = false
    }

    // 设置图片源
    img.src = url

  } catch (error) {
    console.error('❌ [MindmapPanel] PNG 导出异常:', error)
    console.error('❌ [MindmapPanel] 错误堆栈:', error.stack)
    ElMessage.error(`PNG 导出失败: ${error.message}`)
    showExportMenu.value = false
  }
}

// 导出为 SVG
const exportSVG = () => {
  if (!svgMindmap.value) {
    ElMessage.error('思维导图未加载，无法导出 SVG')
    return
  }

  try {
    const svgElement = svgMindmap.value.querySelector('svg')
    if (!svgElement) {
      ElMessage.error('无法找到 SVG 元素')
      return
    }

    // 获取 SVG 数据
    const svgData = new XMLSerializer().serializeToString(svgElement)
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = `思维导图_${Date.now()}.svg`
    a.click()
    URL.revokeObjectURL(url)

    showExportMenu.value = false
    ElMessage.success('SVG 导出成功')
  } catch (error) {
    console.error('SVG 导出失败:', error)
    ElMessage.error('SVG 导出失败，请重试')
    showExportMenu.value = false
  }
}

// 点击外部关闭导出菜单的处理器
const handleClickOutside = (event) => {
  if (showExportMenu.value) {
    const exportButton = document.querySelector('.export-button-container')
    if (exportButton && !exportButton.contains(event.target)) {
      showExportMenu.value = false
    }
  }
}

onMounted(() => {
  renderMindmap()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  // 清理资源
  clearSVG()
})
</script>

<style scoped>
.mindmap-canvas { position: relative; }
.mindmap-svg { display: block; }
.mindmap-markdown {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  background: #f8f9fa;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>