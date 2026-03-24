<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- 顶部导航 -->
      <header class="bg-white rounded-2xl shadow-sm p-6 mb-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">系统测试模式</h1>
              <p class="text-sm text-gray-600">验证系统完整性 - 不消耗API配额</p>
            </div>
          </div>
          <router-link to="/summarize" class="btn-gradient px-4 py-2 rounded-lg text-sm">
            返回AI总结
          </router-link>
        </div>
      </header>

      <!-- 测试状态卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-gray-900">系统测试</h3>
            <span v-if="testStatus" :class="testStatus === 'running' ? 'animate-spin' : ''" class="text-2xl">
              {{ testStatus === 'running' ? '⏳' : testStatus === 'passed' ? '✅' : '❌' }}
            </span>
          </div>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">总测试数</span>
              <span class="font-semibold">{{ testSummary.total }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">通过</span>
              <span class="font-semibold text-green-600">{{ testSummary.passed }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">失败</span>
              <span class="font-semibold text-red-600">{{ testSummary.failed }}</span>
            </div>
          </div>
          <button @click="runSystemTest" class="w-full mt-4 btn-gradient py-2 rounded-lg text-sm" :disabled="testStatus === 'running'">
            {{ testStatus === 'running' ? '测试中...' : '运行系统测试' }}
          </button>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h3 class="font-semibold text-gray-900 mb-4">API连接测试</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">后端服务</span>
              <span :class="apiStatus.backend ? 'text-green-600' : 'text-red-600'">
                {{ apiStatus.backend ? '✓' : '✗' }}
              </span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">测试模式</span>
              <span :class="apiStatus.testMode ? 'text-green-600' : 'text-red-600'">
                {{ apiStatus.testMode ? '✓' : '✗' }}
              </span>
            </div>
          </div>
          <button @click="checkApiStatus" class="w-full mt-4 px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50">
            检查状态
          </button>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h3 class="font-semibold text-gray-900 mb-4">功能测试</h3>
          <div class="space-y-2">
            <button @click="testSummarize" class="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 text-left">
              📝 测试AI总结
            </button>
            <button @click="testChat" class="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 text-left">
              💬 测试AI问答
            </button>
            <button @click="testSubtitle" class="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 text-left">
              📄 测试字幕提取
            </button>
          </div>
        </div>
      </div>

      <!-- 测试结果展示 -->
      <div v-if="testResults.length > 0" class="bg-white rounded-2xl shadow-sm p-6 mb-8">
        <h3 class="text-xl font-bold text-gray-900 mb-4">测试结果</h3>
        <div class="space-y-3">
          <div
            v-for="(result, index) in testResults"
            :key="index"
            class="flex items-center justify-between p-4 rounded-lg"
            :class="result.status === 'passed' ? 'bg-green-50' : 'bg-red-50'"
          >
            <div class="flex items-center gap-3">
              <span class="text-xl">{{ result.status === 'passed' ? '✅' : '❌' }}</span>
              <span class="font-medium text-gray-900">{{ result.name }}</span>
            </div>
            <span class="text-sm text-gray-600">{{ result.message }}</span>
          </div>
        </div>
      </div>

      <!-- 功能演示区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- AI总结演示 -->
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">AI总结演示</h3>
          <div v-if="demoSummary" class="space-y-4">
            <div class="p-4 bg-purple-50 rounded-lg">
              <h4 class="font-semibold text-gray-900 mb-2">核心总结</h4>
              <p class="text-sm text-gray-700">{{ demoSummary.summary }}</p>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <h4 class="font-semibold text-gray-900 mb-2">核心知识点 ({{ demoSummary.key_points?.length || 0 }})</h4>
              <div class="space-y-2">
                <div v-for="(point, index) in demoSummary.key_points?.slice(0, 4)" :key="index" class="flex items-start gap-2 text-sm">
                  <span class="text-yellow-500">{{ '⭐'.repeat(point.importance) }}</span>
                  <span class="text-gray-700">{{ point.point }}</span>
                </div>
              </div>
            </div>
          </div>
          <button @click="loadDemoSummary" class="w-full mt-4 btn-gradient py-2 rounded-lg text-sm">
            加载演示数据
          </button>
        </div>

        <!-- AI问答演示 -->
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">AI问答演示</h3>
          <div class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg max-h-64 overflow-y-auto">
              <div
                v-for="(msg, index) in demoChat"
                :key="index"
                class="mb-3"
                :class="msg.role === 'user' ? 'text-right' : 'text-left'"
              >
                <span
                  class="inline-block px-3 py-2 rounded-lg text-sm"
                  :class="msg.role === 'user' ? 'bg-purple-500 text-white' : 'bg-gray-200 text-gray-800'"
                >
                  {{ msg.content }}
                </span>
              </div>
            </div>
            <div class="flex gap-2">
              <input
                v-model="chatQuestion"
                type="text"
                placeholder="输入测试问题..."
                class="input-field flex-1 text-sm"
                @keyup.enter="sendDemoChat"
              >
              <button @click="sendDemoChat" class="btn-gradient px-4 rounded-lg text-sm">发送</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 测试说明 -->
      <div class="mt-8 bg-blue-50 border border-blue-200 rounded-2xl p-6">
        <h3 class="text-lg font-semibold text-blue-900 mb-3">测试模式说明</h3>
        <ul class="space-y-2 text-sm text-blue-800">
          <li>• 测试模式使用模拟数据，不会消耗真实的API配额</li>
          <li>• 可以验证系统的各个组件是否正常工作</li>
          <li>• 测试通过后，可以配置真实的API密钥进行实际使用</li>
          <li>• 所有的返回数据都是预设的示例，用于演示功能</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 测试状态
const testStatus = ref(null)
const testSummary = ref({ total: 0, passed: 0, failed: 0 })
const testResults = ref([])
const apiStatus = ref({ backend: false, testMode: false })

// 演示数据
const demoSummary = ref(null)
const demoChat = ref([])
const chatQuestion = ref('')

// 检查API状态
const checkApiStatus = async () => {
  try {
    const backendResponse = await fetch('http://localhost:5000/api/health')
    apiStatus.value.backend = backendResponse.ok

    const testResponse = await fetch('http://localhost:5000/api/ai/test/health')
    const testResult = await testResponse.json()
    apiStatus.value.testMode = testResult.success

    ElMessage.success('状态检查完成')
  } catch (err) {
    ElMessage.error('状态检查失败')
  }
}

// 运行系统测试
const runSystemTest = async () => {
  testStatus.value = 'running'
  testResults.value = []

  try {
    const response = await fetch('http://localhost:5000/api/ai/test/system')
    const result = await response.json()

    if (result.results) {
      testResults.value = result.results.tests
      testSummary.value = result.results.summary
    }

    testStatus.value = result.summary?.failed === 0 ? 'passed' : 'failed'

    if (result.success) {
      ElMessage.success(`测试完成：${testSummary.value.passed}/${testSummary.value.total} 通过`)
    } else {
      ElMessage.error(`测试完成：${testSummary.value.failed} 个失败`)
    }
  } catch (err) {
    testStatus.value = 'failed'
    ElMessage.error('系统测试失败')
  }
}

// 测试AI总结
const testSummarize = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/ai/test/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: '测试视频' })
    })
    const result = await response.json()
    if (result.success) {
      demoSummary.value = result.result
      ElMessage.success('AI总结测试成功')
    }
  } catch (err) {
    ElMessage.error('测试失败')
  }
}

// 测试AI问答
const testChat = async () => {
  demoChat.value = [
    { role: 'user', content: '这个视频主要讲了什么？' },
    { role: 'assistant', content: '这个视频主要讲解了核心技术概念和实践方法，非常适合初学者入门学习。' }
  ]
  ElMessage.success('AI问答测试数据已加载')
}

// 测试字幕提取
const testSubtitle = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/ai/test/subtitle')
    const result = await response.json()
    if (result.success) {
      ElMessage.success(`字幕测试成功：${result.data.subtitle_count} 条字幕`)
    }
  } catch (err) {
    ElMessage.error('测试失败')
  }
}

// 加载演示数据
const loadDemoSummary = async () => {
  await testSummarize()
}

// 发送演示聊天
const sendDemoChat = async () => {
  if (!chatQuestion.value.trim()) return

  demoChat.value.push({ role: 'user', content: chatQuestion.value })
  const question = chatQuestion.value
  chatQuestion.value = ''

  try {
    const response = await fetch('http://localhost:5000/api/ai/test/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    })
    const result = await response.json()
    if (result.success) {
      demoChat.value.push({ role: 'assistant', content: result.answer })
    }
  } catch (err) {
    ElMessage.error('发送失败')
  }
}

// 初始化检查状态
checkApiStatus()
</script>
