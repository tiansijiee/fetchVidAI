<template>
  <div class="chat-view">
    <!-- 聊天消息区域 -->
    <div
      ref="messagesContainer"
      class="messages-container flex-1 overflow-y-auto p-4 space-y-4"
      style="min-height: 400px; max-height: 600px;"
    >
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message text-center py-12">
        <div class="w-20 h-20 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-10 h-10 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">AI视频助手</h3>
        <p class="text-gray-600 max-w-md mx-auto mb-6">
          基于视频内容的智能问答，您可以询问关于视频的任何问题
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
          <button
            v-for="(suggestion, index) in suggestedQuestions"
            :key="index"
            @click="askQuestion(suggestion)"
            class="p-3 bg-gray-100 rounded-lg text-left hover:bg-gray-200 transition-colors"
          >
            <p class="text-sm text-gray-700">{{ suggestion }}</p>
          </button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="message"
        :class="message.role === 'user' ? 'user-message' : 'assistant-message'"
      >
        <div class="flex items-start gap-3">
          <!-- 头像 -->
          <div class="flex-shrink-0">
            <div v-if="message.role === 'user'" class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </div>
            <div v-else class="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
            </div>
          </div>

          <!-- 消息内容 -->
          <div class="flex-1 min-w-0">
            <div
              class="inline-block px-4 py-2 rounded-2xl"
              :class="message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'"
            >
              <!-- 用户消息 -->
              <p v-if="message.role === 'user'" class="text-sm whitespace-pre-wrap">{{ message.content }}</p>

              <!-- AI回复 - 支持Markdown和时间戳 -->
              <div v-else class="assistant-content">
                <div v-if="message.streaming" class="flex items-center gap-2">
                  <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <div
                  v-else
                  class="prose prose-sm max-w-none"
                  v-html="formatMessage(message.content)"
                ></div>

                <!-- 时间戳引用 -->
                <div v-if="message.citations && message.citations.length" class="mt-2 pt-2 border-t border-gray-200">
                  <p class="text-xs text-gray-500 mb-1">引用时间点:</p>
                  <div class="flex flex-wrap gap-1">
                    <button
                      v-for="(citation, idx) in message.citations"
                      :key="idx"
                      @click="seekToTimestamp(citation.time)"
                      class="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded hover:bg-purple-200 transition-colors"
                    >
                      {{ citation.time }}
                    </button>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div v-if="!message.streaming && message.role === 'assistant'" class="mt-2 flex gap-2">
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
            </div>

            <!-- 时间戳 -->
            <p class="text-xs text-gray-500 mt-1">{{ formatTime(message.timestamp) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container p-4 border-t border-gray-200">
      <div class="flex gap-2">
        <div class="flex-1 relative">
          <textarea
            v-model="currentQuestion"
            placeholder="询问关于视频的问题..."
            class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-2xl resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            rows="1"
            @keydown.enter.exact.prevent="sendMessage"
            @input="adjustTextareaHeight"
            ref="textareaRef"
          ></textarea>
        </div>
        <button
          @click="sendMessage"
          :disabled="!currentQuestion.trim() || isSending"
          class="p-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
        >
          <svg v-if="!isSending" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
          </svg>
          <div v-else class="w-5 h-5 flex items-center justify-center">
            <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </button>
      </div>
      <p class="text-xs text-gray-500 mt-2 text-center">按 Enter 发送，Shift + Enter 换行</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  videoUrl: {
    type: String,
    required: true
  },
  videoTitle: {
    type: String,
    default: ''
  },
  subtitleText: {
    type: String,
    default: ''
  },
  summaryData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['seek-timestamp'])

// Refs
const messagesContainer = ref(null)
const textareaRef = ref(null)

// 状态
const messages = ref([])
const currentQuestion = ref('')
const isSending = ref(false)
const sessionId = ref(null)

// 计算属性
const suggestedQuestions = computed(() => {
  if (props.summaryData?.suggested_questions) {
    return props.summaryData.suggested_questions
  }

  // 默认建议问题
  return [
    '这个视频主要讲了什么？',
    '视频中有哪些核心要点？',
    '你能详细解释一下视频内容吗？'
  ]
})

// 方法
const sendMessage = async () => {
  const question = currentQuestion.value.trim()
  if (!question || isSending.value) return

  // 添加用户消息
  const userMessage = {
    role: 'user',
    content: question,
    timestamp: Date.now()
  }
  messages.value.push(userMessage)

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
    // 调用流式问答API
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

                // 提取时间戳引用
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
    console.error('问答失败:', err)
    aiMessage.content = '抱歉，回答生成失败。请稍后重试。'
    aiMessage.streaming = false
    ElMessage.error(err.message || '问答失败')
  } finally {
    isSending.value = false
  }
}

const askQuestion = (question) => {
  currentQuestion.value = question
  sendMessage()
}

const extractCitations = (message) => {
  // 从消息中提取时间戳引用
  // 匹配格式如: (00:30) 或 [00:30-01:00]
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
  formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-gray-800 text-white p-3 rounded-lg overflow-x-auto"><code>$2</code></pre>')

  // 时间戳高亮
  formatted = formatted.replace(/\(?(\d{1,2}:\d{2})\)?/g, '<button class="text-purple-600 hover:text-purple-800 underline" onclick="window.dispatchEvent(new CustomEvent(\'seek-timestamp\', {detail: \'$1\'}))">$1</button>')

  // 段落
  formatted = formatted.split('\n\n').map(p => `<p class="mb-2">${p}</p>`).join('')

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

const seekToTimestamp = (timestamp) => {
  const match = timestamp.match(/(\d{1,2}:\d{2})/)
  if (match) {
    const timeStr = match[1]
    const [minutes, seconds] = timeStr.split(':').map(Number)
    const totalSeconds = minutes * 60 + seconds

    ElMessage.info(`跳转到时间: ${timeStr}`)
    emit('seek-timestamp', { time: timeStr, seconds: totalSeconds })
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const adjustTextareaHeight = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 120) + 'px'
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  // 监听时间戳点击事件
  window.addEventListener('seek-timestamp', (e) => {
    seekToTimestamp(e.detail)
  })
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.messages-container {
  background: #f9fafb;
}

.message {
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

.user-message {
  justify-content: flex-end;
}

.assistant-message {
  justify-content: flex-start;
}

.assistant-content {
  max-width: 500px;
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
</style>
