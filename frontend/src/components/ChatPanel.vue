<template>
  <div class="chat-panel">
    <!-- 欢迎界面 -->
    <div v-if="messages.length === 0" class="text-center py-8">
      <div class="w-20 h-20 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-10 h-10 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
        </svg>
      </div>
      <h3 class="text-xl font-bold text-gray-900 mb-2">AI视频助手</h3>
      <p class="text-gray-600 mb-6 max-w-md mx-auto">
        基于视频内容的智能问答，您可以询问任何关于视频的问题
      </p>

      <!-- 建议问题 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto mb-6">
        <button
          v-for="(suggestion, index) in suggestedQuestions"
          :key="index"
          @click="askQuestion(suggestion)"
          class="p-4 bg-gray-100 rounded-xl text-left hover:bg-gray-200 transition-colors"
        >
          <p class="text-sm text-gray-700">{{ suggestion }}</p>
        </button>
      </div>

      <!-- 输入框 -->
      <div class="max-w-2xl mx-auto">
        <div class="relative">
          <textarea
            v-model="currentQuestion"
            placeholder="询问关于视频的问题..."
            class="w-full px-4 py-3 pr-12 border-2 border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            rows="2"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
          <button
            @click="sendMessage"
            :disabled="!currentQuestion.trim() || isSending"
            class="absolute right-2 bottom-2 p-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="!isSending" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18 9 18 9-2zm0 0v-8"></path>
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </button>
        </div>
        <p class="text-xs text-gray-500 mt-2 text-center">按 Enter 发送</p>
      </div>
    </div>

    <!-- 对话历史 -->
    <div v-else class="flex flex-col" style="height: 600px;">
      <!-- 消息列表 -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="flex"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div class="max-w-[80%]">
            <!-- 用户消息 -->
            <div v-if="message.role === 'user'" class="bg-indigo-500 text-white px-4 py-2.5 rounded-2xl rounded-br-sm">
              <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
            </div>

            <!-- AI回复 -->
            <div v-else class="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm">
              <!-- 流式输出状态 -->
              <div v-if="message.streaming" class="flex items-center gap-2">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span class="text-sm text-gray-500">AI正在思考...</span>
              </div>

              <!-- 完整回复 -->
              <div v-else>
                <div
                  class="prose prose-sm max-w-none text-gray-700"
                  v-html="formatMessage(message.content)"
                ></div>

                <!-- 时间戳引用 -->
                <div v-if="message.citations && message.citations.length" class="mt-3 pt-3 border-t border-gray-200">
                  <p class="text-xs text-gray-500 mb-2">引用时间点:</p>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="(citation, idx) in message.citations"
                      :key="idx"
                      @click="$emit('seek-timestamp', { time: citation.time, seconds: parseTime(citation.time) })"
                      class="text-xs bg-indigo-100 text-indigo-700 px-2.5 py-1 rounded-lg hover:bg-indigo-200 transition-colors"
                    >
                      {{ citation.time }}
                    </button>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="mt-3 flex gap-2">
                  <button
                    @click="copyMessage(message.content)"
                    class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                  >
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                    复制
                  </button>
                  <button
                    @click="regenerateResponse(index)"
                    class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                  >
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                    重新生成
                  </button>
                </div>
              </div>

              <!-- 时间戳 -->
              <p class="text-xs text-gray-400 mt-2">{{ formatTime(message.timestamp) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="border-t border-gray-200 pt-4">
        <div class="relative">
          <textarea
            v-model="currentQuestion"
            placeholder="继续询问关于视频的问题..."
            class="w-full px-4 py-3 pr-12 border-2 border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            rows="2"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
          <button
            @click="sendMessage"
            :disabled="!currentQuestion.trim() || isSending"
            class="absolute right-2 bottom-2 p-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="!isSending" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18 9 18 9-2zm0 0v-8"></path>
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  videoUrl: String,
  videoTitle: String,
  subtitleText: {
    type: String,
    default: ''
  },
  isLoading: Boolean
})

const emit = defineEmits(['seek-timestamp'])

// Refs
const messagesContainer = ref(null)

// 状态
const messages = ref([])
const currentQuestion = ref('')
const isSending = ref(false)

// 计算属性
const suggestedQuestions = computed(() => [
  '这个视频主要讲了什么？',
  '视频中有哪些核心要点？',
  '你能详细解释一下视频内容吗？',
  '视频的结论是什么？'
])

// 方法
const askQuestion = (question) => {
  currentQuestion.value = question
  sendMessage()
}

const sendMessage = async () => {
  const question = currentQuestion.value.trim()
  if (!question || isSending.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: question,
    timestamp: Date.now()
  })

  currentQuestion.value = ''
  isSending.value = true

  // 添加AI回复占位符
  const aiMessage = {
    role: 'assistant',
    content: '',
    streaming: true,
    timestamp: Date.now(),
    citations: []
  }
  messages.value.push(aiMessage)

  try {
    const response = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        subtitle_text: props.subtitleText,
        chat_history: messages.value.slice(0, -1).map(m => ({
          role: m.role,
          content: m.content
        })),
        video_info: {
          title: props.videoTitle,
          url: props.videoUrl
        }
      })
    })

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

            switch (data.type) {
              case 'start':
                console.log('开始生成回答:', data.message)
                break
              case 'content':
                // 追加内容（打字机效果）
                aiMessage.content += data.content
                await scrollToBottom()
                break
              case 'complete':
                aiMessage.streaming = false
                extractCitations(aiMessage)
                ElMessage.success('回答完成')
                break
              case 'error':
                throw new Error(data.message || '生成失败')
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e)
          }
        }
      }
    }
  } catch (err) {
    aiMessage.content = '抱歉，回答生成失败。请稍后重试。'
    aiMessage.streaming = false
    ElMessage.error(err.message || '问答失败')
  } finally {
    isSending.value = false
  }
}

const extractCitations = (message) => {
  // 从消息中提取时间戳引用
  const timeRegex = /\(?(\d{1,2}:\d{2})\)?/g
  const citations = []

  let match
  while ((match = timeRegex.exec(message.content)) !== null) {
    citations.push({
      time: match[1],
      context: '' // 可以根据需要添加上下文
    })
  }

  if (citations.length > 0) {
    message.citations = citations
  }
}

const formatMessage = (content) => {
  // 简单的Markdown格式化
  let formatted = content

  // 代码块
  formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-gray-800 text-white p-3 rounded-lg overflow-x-auto my-2"><code>$2</code></pre>')

  // 时间戳高亮
  formatted = formatted.replace(/\(?(\d{1,2}:\d{2})\)?/g, '<button class="text-indigo-600 hover:text-indigo-800 underline mx-0.5" onclick="window.dispatchEvent(new CustomEvent(\'seek-timestamp\', {detail: \'$1\'}))">$1</button>')

  // 段落
  formatted = formatted.split('\n\n').map(p => `<p class="mb-2 last:mb-0">${p}</p>`).join('')

  return formatted
}

const copyMessage = (content) => {
  navigator.clipboard.writeText(content).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

const regenerateResponse = async (index) => {
  // 找到对应的用户问题
  const userMessage = messages.value[index - 1]
  if (userMessage && userMessage.role === 'user') {
    // 移除当前的AI回复
    messages.value.splice(index, 1)
    // 重新发送问题
    currentQuestion.value = userMessage.content
    await sendMessage()
  }
}

const parseTime = (timeStr) => {
  const match = timeStr.match(/(\d{1,2}):(\d{2})/)
  if (match) {
    const [, minutes, seconds] = match
    return parseInt(minutes) * 60 + parseInt(seconds)
  }
  return 0
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 监听时间戳点击事件
if (typeof window !== 'undefined') {
  window.addEventListener('seek-timestamp', (e) => {
    emit('seek-timestamp', { time: e.detail, seconds: parseTime(e.detail) })
  })
}
</script>

<style scoped>
.prose {
  color: #374151;
  line-height: 1.6;
}

.prose p {
  margin-bottom: 0.5em;
}

.prose pre {
  margin: 0.5em 0;
}

.prose code {
  background: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #9ca3af;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.mx-0\.5 {
  margin-left: 0.125rem;
  margin-right: 0.125rem;
}
</style>
