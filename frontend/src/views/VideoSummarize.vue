<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white font-sans">
    <div class="relative z-10">
      <!-- 顶部导航 -->
      <header class="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <!-- Logo区域 -->
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/20">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
              </div>
              <div class="flex flex-col">
                <span class="text-lg font-bold text-gray-900 leading-tight">FetchVid</span>
                <span class="text-xs text-gray-500 leading-tight">万能视频下载器</span>
              </div>
            </div>
            <nav class="flex items-center gap-8">
              <router-link to="/download" class="nav-link">视频下载</router-link>
              <router-link to="/summarize" class="nav-link-active">AI总结</router-link>
            </nav>
            <!-- 用户菜单 -->
            <UserMenu />
          </div>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">

        <!-- 标题区 -->
        <div class="text-center mb-10 animate-slideUp">
          <div class="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 border border-purple-200 rounded-full mb-6">
            <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            <span class="text-sm font-medium text-purple-700">AI智能分析</span>
          </div>
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-4">
            <span class="gradient-text-ai">AI视频总结</span>
          </h1>
          <p class="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
            智能提取视频核心内容，生成摘要、思维导图和知识点
          </p>
        </div>

        <!-- 输入卡片 -->
        <div class="max-w-4xl mx-auto mb-10 animate-slideUp" style="animation-delay: 0.1s">
          <div class="glass-card p-6 sm:p-8">
            <div class="space-y-6">
              <!-- 输入引导文案 -->
              <div class="flex items-center justify-between mb-2">
                <label class="flex items-center gap-2 text-sm font-semibold text-gray-700">
                  <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                  </svg>
                  粘贴视频链接
                </label>
                <span class="text-xs text-gray-500">需要有字幕的视频</span>
              </div>

              <!-- 输入区域 -->
              <div class="flex flex-col sm:flex-row gap-4">
                <input
                  v-model="videoUrl"
                  type="text"
                  placeholder="支持 B站/YouTube 等有字幕的视频链接"
                  class="input-field flex-1"
                  @keyup.enter="checkAndSummarize"
                  :disabled="processing"
                >
                <button
                  @click="checkAndSummarize"
                  :disabled="!videoUrl.trim() || processing"
                  class="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 px-6 rounded-lg text-sm transition-all whitespace-nowrap flex items-center justify-center gap-2 shadow-md hover:shadow-lg transform hover:scale-[1.02] active:scale-[0.98]"
                >
                  <svg v-if="!processing" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                  <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{{ processing ? 'AI分析中...' : '开始AI分析' }}</span>
                </button>
              </div>

              <!-- 平台支持标签 -->
              <div class="flex flex-wrap items-center gap-2">
                <span class="text-sm text-gray-500">支持平台：</span>
                <span class="platform-badge text-xs px-3 py-1.5">📺 B站</span>
                <span class="platform-badge text-xs px-3 py-1.5">▶️ YouTube</span>
                <span class="text-xs text-gray-400">*需要有字幕的视频</span>
              </div>

              <!-- 错误提示 -->
              <div v-if="error" class="p-4 bg-red-50 border-2 border-red-200 rounded-xl">
                <span class="text-red-700 text-sm">{{ error }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 处理进度 -->
        <div v-if="processing" class="max-w-4xl mx-auto mb-10 animate-slideUp" style="animation-delay: 0.2s">
          <div class="ai-card p-8 text-center">
            <div class="max-w-md mx-auto">
              <div class="w-20 h-20 mx-auto mb-6 relative">
                <div class="absolute inset-0 border-4 border-purple-200 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-purple-500 rounded-full border-t-transparent animate-spin"></div>
                <div class="absolute inset-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                  </svg>
                </div>
              </div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">{{ processingStatus.title }}</h3>
              <p class="text-sm text-gray-600 mb-6">{{ processingStatus.desc }}</p>
              <div class="progress-bar">
                <div class="progress-bar-ai" :style="{ width: processingProgress + '%' }"></div>
              </div>
              <p class="text-xs text-gray-500 mt-3">{{ processingProgress }}%</p>
            </div>
          </div>
        </div>

        <!-- 双栏布局：左侧视频信息 + 右侧AI总结 -->
        <div v-if="videoInfo.title || summaryResult" class="grid grid-cols-1 lg:grid-cols-5 gap-6 animate-slideUp" style="animation-delay: 0.3s">

          <!-- 左侧栏：视频信息 (40%宽度) -->
          <div class="lg:col-span-2">
            <div class="bg-white rounded-lg border border-gray-200 p-5 sticky top-24 shadow-sm">
              <!-- 视频封面 -->
              <div class="relative aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4">
                <img
                  v-if="videoInfo.thumbnail"
                  :src="getThumbnailUrl(videoInfo.thumbnail)"
                  class="w-full h-full object-cover"
                >
                <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
                  <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                </div>
              </div>

              <!-- 视频信息 -->
              <h3 class="font-semibold text-gray-900 mb-2 line-clamp-2 text-sm leading-relaxed">
                {{ videoInfo.title }}
              </h3>
              <div class="flex items-center gap-3 text-xs text-gray-500 mb-4">
                <div class="flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                  <span>{{ videoInfo.uploader || '未知UP主' }}</span>
                </div>
                <div class="flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>{{ videoInfo.views || '0' }}</span>
                </div>
              </div>

              <!-- 质量选择卡片 -->
              <div class="space-y-2 mb-4">
                <p class="text-xs font-medium text-gray-600 mb-2">选择质量</p>
                <div class="grid grid-cols-3 gap-2">
                  <button
                    v-for="quality in qualityOptions"
                    :key="quality.value"
                    @click="selectedQuality = quality.value"
                    class="quality-card px-3 py-2 rounded-md text-xs font-medium transition-all"
                    :class="selectedQuality === quality.value ? 'quality-card-selected' : 'quality-card-default'"
                  >
                    {{ quality.label }}
                  </button>
                </div>
              </div>

              <!-- 下载按钮 -->
              <button
                @click="downloadVideo"
                class="w-full bg-[#1890ff] hover:bg-[#1677d9] text-white font-medium py-2.5 px-4 rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                下载视频
              </button>

              <!-- 进度条 -->
              <div v-if="processing" class="mt-4">
                <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                  <span>处理进度</span>
                  <span>{{ formatTime(elapsedTime) }}/{{ formatTime(estimatedTime) }}</span>
                </div>
                <div class="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-[#1890ff] transition-all duration-300" :style="{ width: processingProgress + '%' }"></div>
                </div>
                <div class="text-center mt-2 text-xs text-gray-600">{{ processingStatus.desc }}</div>
              </div>
            </div>
          </div>

          <!-- 右侧栏：AI总结 (60%宽度) -->
          <div class="lg:col-span-3">
            <!-- Tab切换栏 -->
            <div class="bg-white rounded-lg border border-gray-200 p-1.5 flex gap-1.5 mb-4">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                @click="activeTab = tab.key"
                class="flex-1 px-3 py-2 rounded-md font-medium text-xs transition-all duration-200 flex items-center justify-center gap-1.5"
                :class="activeTab === tab.key
                  ? 'bg-[#1890ff] text-white'
                  : 'text-gray-600 hover:bg-gray-50'"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.icon"></path>
                </svg>
                <span>{{ tab.label }}</span>
              </button>
            </div>

            <!-- Tab内容区 -->
            <div class="bg-white rounded-lg border border-gray-200 p-5 min-h-[500px] shadow-sm">

              <!-- 视频总结 Tab - 流式显示 -->
              <div v-if="activeTab === 'summary'" class="space-y-4">
                <!-- 如果正在流式输出，显示逐字动画 -->
                <div v-if="streamingContent || summaryResult" class="space-y-4">
                  <!-- 编号章节列表 -->
                  <div v-for="(section, index) in displayedSections" :key="index" class="border-b border-gray-100 pb-4 last:border-0">
                    <div class="flex items-start gap-3">
                      <!-- 章节编号 -->
                      <div class="flex-shrink-0 w-6 h-6 bg-[#1890ff] text-white rounded-full flex items-center justify-center text-xs font-semibold">
                        {{ index + 1 }}
                      </div>
                      <!-- 章节内容 -->
                      <div class="flex-1 min-w-0">
                        <h4 class="font-semibold text-gray-900 text-sm mb-1.5">{{ section.title }}</h4>
                        <p class="text-sm text-gray-600 leading-relaxed">{{ section.content }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 空状态 -->
                <div v-else class="text-center py-12">
                  <div class="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                    </svg>
                  </div>
                  <h3 class="text-sm font-semibold text-gray-900 mb-1">等待分析</h3>
                  <p class="text-xs text-gray-500">点击"开始AI分析"按钮开始</p>
                </div>

                <!-- AI正在生成状态 -->
                <div v-if="isStreaming" class="flex items-center justify-center gap-2 py-4">
                  <div class="flex gap-1">
                    <span class="w-2 h-2 bg-[#1890ff] rounded-full animate-bounce" style="animation-delay: 0s"></span>
                    <span class="w-2 h-2 bg-[#1890ff] rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                    <span class="w-2 h-2 bg-[#1890ff] rounded-full animate-bounce" style="animation-delay: 0.4s"></span>
                  </div>
                  <span class="text-xs text-gray-600">AI正在生成中...</span>
                </div>
              </div>

              <!-- 字幕文本 Tab -->
              <div v-else-if="activeTab === 'subtitle'" class="space-y-3">
                <div v-if="subtitles.length > 0" class="space-y-3 max-h-[450px] overflow-y-auto">
                  <div
                    v-for="(sub, index) in subtitles"
                    :key="index"
                    class="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div class="text-xs text-gray-400 mb-1">{{ sub.time }}</div>
                    <div class="text-sm text-gray-700">{{ sub.text }}</div>
                  </div>
                </div>
                <div v-else class="text-center py-12">
                  <div class="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                  <h3 class="text-sm font-semibold text-gray-900 mb-1">字幕文本</h3>
                  <p class="text-xs text-gray-500 mb-4">点击下方按钮查看完整字幕内容</p>
                  <button @click="checkSubtitle" class="bg-[#1890ff] hover:bg-[#1677d9] text-white font-medium py-2 px-4 rounded-lg text-xs transition-colors">查看完整字幕</button>
                </div>
              </div>

              <!-- 思维导图 Tab -->
              <div v-else-if="activeTab === 'mindmap'" class="space-y-3">
                <div v-if="summaryResult && summaryResult.mindmap && summaryResult.mindmap.branches && summaryResult.mindmap.branches.length > 0" class="space-y-3">
                  <div class="text-center font-semibold text-gray-900 text-sm mb-4 py-3 bg-gray-50 rounded-lg">
                    {{ typeof summaryResult.mindmap.root === 'object' ? summaryResult.mindmap.root.text || summaryResult.mindmap.root.content || '主题' : summaryResult.mindmap.root || '主题' }}
                  </div>
                  <div class="space-y-2">
                    <div
                      v-for="(branch, index) in summaryResult.mindmap.branches"
                      :key="index"
                      class="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow"
                    >
                      <h4 class="font-semibold text-gray-900 text-xs mb-2 flex items-center gap-2">
                        <span class="w-5 h-5 bg-[#1890ff] text-white rounded-md flex items-center justify-center text-[10px]">{{ index + 1 }}</span>
                        {{ typeof branch === 'object' ? (branch.text || branch.name || branch.content || '') : branch }}
                      </h4>
                      <ul v-if="typeof branch === 'object' && branch.children && branch.children.length > 0" class="space-y-1.5">
                        <li v-for="(child, i) in branch.children" :key="i" class="text-xs text-gray-600 flex items-center gap-2">
                          <span class="w-1 h-1 bg-gray-300 rounded-full flex-shrink-0"></span>
                          {{ typeof child === 'object' ? (child.text || child.content || child.name || '') : child }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-12 text-gray-500">
                  <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7"></path>
                  </svg>
                  <p class="text-xs">思维导图正在生成中...</p>
                  <p v-if="summaryResult && summaryResult.mindmap" class="text-xs text-gray-400 mt-2">
                    调试信息: {{ JSON.stringify(summaryResult.mindmap) }}
                  </p>
                </div>
              </div>

              <!-- AI问答 Tab -->
              <div v-else-if="activeTab === 'chat'" class="flex flex-col h-full">
                <!-- 聊天消息区 -->
                <div class="flex-1 space-y-3 max-h-[350px] overflow-y-auto mb-3" id="chatContainer">
                  <div v-if="chatMessages.length === 0" class="text-center py-10">
                    <div class="w-14 h-14 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                      <svg class="w-7 h-7 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                      </svg>
                    </div>
                    <h3 class="text-sm font-semibold text-gray-900 mb-1">AI问答助手</h3>
                    <p class="text-xs text-gray-500">向AI提问关于视频内容的任何问题</p>
                  </div>
                  <div
                    v-for="(msg, index) in chatMessages"
                    :key="index"
                    class="flex gap-2"
                    :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
                  >
                    <div
                      class="max-w-[85%] rounded-xl px-3 py-2 text-xs"
                      :class="msg.role === 'user' ? 'bg-[#1890ff] text-white' : 'bg-gray-100 text-gray-800'"
                    >
                      {{ msg.content }}
                    </div>
                  </div>
                </div>
                <!-- 输入区 -->
                <div class="flex gap-2">
                  <input
                    v-model="chatQuestion"
                    type="text"
                    placeholder="向AI提问关于视频内容的问题..."
                    class="flex-1 px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1890ff] focus:border-transparent"
                    @keyup.enter="sendChat"
                    :disabled="chatLoading"
                  >
                  <button
                    @click="sendChat"
                    :disabled="!chatQuestion.trim() || chatLoading"
                    class="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg text-xs transition-all flex items-center justify-center"
                  >
                    发送
                  </button>
                </div>
              </div>

            </div>
          </div>

        </div>
      </main>
    </div>

    <!-- 字幕查看对话框 -->
    <el-dialog v-model="subtitleDialogVisible" title="完整字幕" width="80%" top="5vh">
      <div class="max-h-[60vh] overflow-y-auto">
        <div
          v-for="(sub, index) in subtitles"
          :key="index"
          class="mb-3 pb-3 border-b border-gray-100"
        >
          <div class="text-xs text-gray-400 mb-1">{{ sub.time }}</div>
          <div class="text-sm text-gray-700">{{ sub.text }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import UserMenu from '../components/UserMenu.vue'
import auth from '../auth/auth'
import { getFingerprint } from '../utils/fingerprint'

const videoUrl = ref('')
const processing = ref(false)
const processingProgress = ref(0)
const error = ref('')
const summaryResult = ref(null)
const videoInfo = reactive({ title: '', uploader: '', thumbnail: '', views: '0' })
const chatMessages = ref([])
const chatQuestion = ref('')
const chatLoading = ref(false)
const subtitleDialogVisible = ref(false)
const subtitles = ref([])
const activeTab = ref('summary')

// 新增：质量选择
const qualityOptions = [
  { label: '1080P', value: '1080p' },
  { label: '720P', value: '720p' },
  { label: '480P', value: '480p' }
]
const selectedQuality = ref('1080p')

// 新增：流式显示状态
const streamingContent = ref('')
const isStreaming = ref(false)
const displayedSections = ref([])

// 新增：时间跟踪
const elapsedTime = ref(0)
const estimatedTime = ref(82) // 预估时间（秒）
const timerInterval = ref(null)

// Tab配置
const tabs = [
  {
    key: 'summary',
    label: '视频总结',
    icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
    color: 'from-purple-500 to-pink-500'
  },
  {
    key: 'subtitle',
    label: '字幕文本',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'from-primary-500 to-cyan-500'
  },
  {
    key: 'mindmap',
    label: '思维导图',
    icon: 'M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2',
    color: 'from-green-500 to-teal-500'
  },
  {
    key: 'chat',
    label: 'AI问答',
    icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z',
    color: 'from-indigo-500 to-purple-500'
  }
]

const processingStatus = computed(() => {
  const statusMap = {
    checking: { title: '检查字幕', desc: '正在检查视频是否有字幕...' },
    extracting: { title: '提取字幕', desc: '正在提取视频字幕内容...' },
    summarizing: { title: 'AI总结中', desc: 'AI正在分析视频内容并生成总结...' },
    creating_chat: { title: '创建会话', desc: '正在创建AI问答会话...' },
    completed: { title: '完成', desc: '总结已完成！' }
  }
  const progress = processingProgress.value
  if (progress < 20) return statusMap.checking
  if (progress < 40) return statusMap.extracting
  if (progress < 80) return statusMap.summarizing
  if (progress < 100) return statusMap.creating_chat
  return statusMap.completed
})

const getThumbnailUrl = (url) => {
  if (!url) return ''
  return `/api/proxy/thumbnail?url=${encodeURIComponent(url)}`
}

// 格式化时间显示（秒 -> MM:SS）
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 下载视频
const downloadVideo = () => {
  if (!videoUrl.value) {
    ElMessage.warning('请先输入视频链接')
    return
  }
  // TODO: 实现下载功能
  ElMessage.info('下载功能开发中...')
}

const checkAndSummarize = async () => {
  const url = videoUrl.value.trim()
  if (!url) {
    error.value = '请输入视频链接'
    return
  }

  // 检查剩余次数（前端预检查）
  const quota = auth.quota
  if (quota && typeof quota.parse_remaining === 'number' && quota.parse_remaining <= 0) {
    const role = auth.getRole()
    if (role === 'guest') {
      ElMessage.warning('今日解析次数已用完，注册后每日3次')
      window.dispatchEvent(new CustomEvent('auth:login-required'))
    } else {
      ElMessage.warning('今日解析次数已用完，开通VIP无限使用')
      window.dispatchEvent(new CustomEvent('auth:upgrade-required'))
    }
    return
  }

  processing.value = true
  processingProgress.value = 0
  error.value = ''
  summaryResult.value = null
  streamingContent.value = ''
  displayedSections.value = []
  isStreaming.value = true
  elapsedTime.value = 0

  // 启动计时器
  if (timerInterval.value) clearInterval(timerInterval.value)
  timerInterval.value = setInterval(() => {
    elapsedTime.value++
  }, 1000)

  try {
    // 构建请求头（包含fingerprint和token）
    const headers = {
      'Content-Type': 'application/json'
    }
    const fingerprint = getFingerprint()
    if (fingerprint) {
      headers['X-Fingerprint'] = fingerprint
    }
    const token = auth.getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    // 先解析视频获取基本信息
    const parseResponse = await fetch('/api/parse', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ url })
    })

    const parseResult = await parseResponse.json()
    if (!parseResult.success) {
      throw new Error(parseResult.message)
    }

    videoInfo.title = parseResult.data.title
    videoInfo.uploader = parseResult.data.uploader
    videoInfo.thumbnail = parseResult.data.thumbnail
    videoInfo.views = parseResult.data.views || '0'

    processingProgress.value = 20

    // 使用流式API直接获取总结结果
    const streamResponse = await fetch('/api/ai/summarize/stream', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        url,
        title: videoInfo.title,
        description: parseResult.data.description || ''
      })
    })

    if (!streamResponse.ok) {
      throw new Error('请求失败')
    }

    // 读取SSE流
    const reader = streamResponse.body.getReader()
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

            if (data.type === 'progress') {
              // 更新进度消息
              if (data.message.includes('分析')) processingProgress.value = 30
              else if (data.message.includes('字幕')) processingProgress.value = 50
              else if (data.message.includes('ASR') || data.message.includes('转写')) processingProgress.value = 60
              else if (data.message.includes('思考') || data.message.includes('AI')) processingProgress.value = 80
            } else if (data.type === 'result') {
              // 最终结果 - 转换为编号章节格式并流式显示
              summaryResult.value = data.data
              await streamDisplaySections(data.data)
              processingProgress.value = 100
              processing.value = false
              isStreaming.value = false
              if (timerInterval.value) clearInterval(timerInterval.value)
              ElMessage.success('AI总结完成！')

              // 刷新剩余次数
              auth.refreshQuota()
              return
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
    error.value = err.message || '处理失败'
    processing.value = false
    isStreaming.value = false
    if (timerInterval.value) clearInterval(timerInterval.value)
    ElMessage.error(err.message)
  }
}

// 将AI总结结果转换为编号章节格式
const convertToSections = (data) => {
  const sections = []

  // 1. 视频概述
  if (data.overview) {
    sections.push({
      title: '视频概述',
      content: data.overview
    })
  }

  // 2. 内容大纲
  if (data.outline && data.outline.length > 0) {
    data.outline.forEach((item, index) => {
      sections.push({
        title: `${index + 1}. ${item.title}`,
        content: item.content
      })
    })
  }

  // 3. 核心要点
  if (data.key_points && data.key_points.length > 0) {
    const keyPointsText = data.key_points.map(p => `• ${p.point}`).join('\n')
    sections.push({
      title: '核心要点',
      content: keyPointsText
    })
  }

  // 4. 总结结论
  if (data.conclusion) {
    const conclusionText = data.conclusion.summary || ''
    const takeaways = data.conclusion.takeaways ? data.conclusion.takeaways.map(t => `• ${t}`).join('\n') : ''
    sections.push({
      title: '总结结论',
      content: conclusionText + (takeaways ? '\n\n' + takeaways : '')
    })
  }

  return sections
}

// 流式显示章节内容（逐字显示效果）
const streamDisplaySections = async (data) => {
  const sections = convertToSections(data)

  for (const section of sections) {
    const displayedSection = {
      title: section.title,
      content: ''
    }
    displayedSections.value.push(displayedSection)

    // 逐字显示内容
    const fullContent = section.content
    for (let i = 0; i < fullContent.length; i++) {
      displayedSection.content += fullContent[i]
      // 添加小延迟以实现打字机效果
      await new Promise(resolve => setTimeout(resolve, 20))
    }
  }
}

const sendChat = async () => {
  if (!chatQuestion.value.trim() || !videoUrl.value) return

  const question = chatQuestion.value
  chatQuestion.value = ''
  chatMessages.value.push({ role: 'user', content: question })
  chatLoading.value = true

  try {
    // 构建请求头
    const headers = {
      'Content-Type': 'application/json'
    }
    const fingerprint = getFingerprint()
    if (fingerprint) {
      headers['X-Fingerprint'] = fingerprint
    }
    const token = auth.getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        question,
        url: videoUrl.value,
        video_info: {
          title: videoInfo.title
        }
      })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    // 读取SSE流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let assistantMessage = ''

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

            if (data.type === 'content') {
              assistantMessage += data.content
              // 更新最后一条消息
              const lastMsg = chatMessages.value[chatMessages.value.length - 1]
              if (lastMsg && lastMsg.role === 'assistant') {
                lastMsg.content = assistantMessage
              } else {
                chatMessages.value.push({ role: 'assistant', content: assistantMessage })
              }
              scrollToBottom()
            } else if (data.type === 'complete') {
              scrollToBottom()
            } else if (data.type === 'error') {
              throw new Error(data.message || '问答失败')
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e)
          }
        }
      }
    }

  } catch (err) {
    ElMessage.error(err.message || '网络错误')
  } finally {
    chatLoading.value = false
  }
}

const scrollToBottom = async () => {
  await nextTick()
  const container = document.getElementById('chatContainer')
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

const copyText = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}

const exportSummary = (format) => {
  if (!summaryResult.value) return

  let md = `# ${videoInfo.title || '视频总结'}\n\n`

  // 视频概述
  if (summaryResult.value.overview) {
    md += `## 🎯 视频概述\n\n${summaryResult.value.overview}\n\n`
  }

  // 内容大纲
  if (summaryResult.value.outline && summaryResult.value.outline.length) {
    md += `## 📚 内容大纲\n\n`
    summaryResult.value.outline.forEach((outline, index) => {
      md += `### ${index + 1}. ${outline.title}\n\n${outline.content}\n\n`
    })
  }

  // 核心要点
  if (summaryResult.value.key_points && summaryResult.value.key_points.length) {
    md += `## 💡 核心要点\n\n`
    summaryResult.value.key_points.forEach(point => {
      md += `- ${point.point}\n`
    })
    md += '\n'
  }

  // 总结结论
  if (summaryResult.value.conclusion) {
    md += `## 📝 总结结论\n\n`
    if (summaryResult.value.conclusion.summary) {
      md += `**总结**: ${summaryResult.value.conclusion.summary}\n\n`
    }
    if (summaryResult.value.conclusion.takeaways) {
      md += `**主要收获**:\n\n`
      summaryResult.value.conclusion.takeaways.forEach(takeaway => {
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
  link.download = `${videoInfo.title || '视频总结'}_${Date.now()}.md`
  link.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('导出成功！')
}

const checkSubtitle = async () => {
  if (!videoUrl.value || !subtitles.value.length) {
    // 如果没有字幕，尝试获取
    try {
      // 构建请求头
      const headers = {
        'Content-Type': 'application/json'
      }
      const fingerprint = getFingerprint()
      if (fingerprint) {
        headers['X-Fingerprint'] = fingerprint
      }
      const token = auth.getToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch('/api/ai/subtitle/raw', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          url: videoUrl.value,
          use_asr: true
        })
      })

      const result = await response.json()
      if (result.success && result.full_text) {
        // 解析字幕文本为字幕数组
        const lines = result.full_text.split('\n').filter(line => line.trim())
        subtitles.value = lines.map((line, index) => ({
          time: `${Math.floor(index * 5 / 60).toString().padStart(2, '0')}:${((index * 5) % 60).toString().padStart(2, '0')}`,
          text: line.trim()
        }))
      }
    } catch (err) {
      ElMessage.error('获取字幕失败')
    }
  }
  subtitleDialogVisible.value = true
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 质量选择卡片样式 */
.quality-card {
  transition: all 0.2s ease;
  cursor: pointer;
  border: 1px solid #e5e7eb;
}

.quality-card-default {
  background-color: #f9fafb;
  color: #6b7280;
}

.quality-card-default:hover {
  background-color: #f3f4f6;
  border-color: #d1d5db;
}

.quality-card-selected {
  background-color: #1890ff;
  color: white;
  border-color: #1890ff;
}

.quality-card-selected:hover {
  background-color: #1677d9;
  border-color: #1677d9;
}
</style>
