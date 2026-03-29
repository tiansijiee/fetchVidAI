<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white font-sans">
    <!-- 顶部导航栏 - 浅蓝渐变 + 毛玻璃效果 -->
    <header class="bg-gradient-to-r from-blue-50/90 via-white/95 to-blue-50/90 backdrop-blur-xl border-b border-blue-100/50 sticky top-0 z-50 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo区域 -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div class="flex flex-col">
              <span class="text-lg font-bold text-gray-900 leading-tight">FetchVid</span>
              <span class="text-xs text-gray-500 leading-tight">智能视频下载</span>
            </div>
          </div>

          <!-- 导航入口 - 添加更多导航项 -->
          <nav class="hidden lg:flex items-center gap-8">
            <router-link to="/download" class="nav-link text-base font-semibold text-blue-600 hover:text-blue-700 transition-colors relative">
              视频下载
              <span class="absolute -bottom-6 left-0 right-0 h-0.5 bg-blue-600 rounded-full"></span>
            </router-link>
            <router-link to="/pricing" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">套餐价格</router-link>
            <router-link to="/features" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">功能特性</router-link>
            <router-link to="/tutorial" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">使用教程</router-link>
          </nav>

          <!-- VIP入口 & 用户菜单 -->
          <div class="flex items-center gap-3">
            <!-- VIP按钮 -->
            <button
              @click="handleUpgrade"
              class="hidden sm:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-xl font-medium transition-all duration-200 shadow-md shadow-purple-500/30 hover:shadow-lg hover:shadow-purple-500/40 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
              </svg>
              <span>开通VIP</span>
            </button>

            <!-- 用户菜单组件 -->
            <UserMenu />

            <!-- 移动端菜单按钮 -->
            <button class="lg:hidden p-2 text-gray-600 hover:text-blue-600 transition-colors" @click="mobileMenuOpen = !mobileMenuOpen">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- 移动端菜单 -->
        <div v-if="mobileMenuOpen" class="lg:hidden py-4 border-t border-blue-100/50">
          <nav class="flex flex-col gap-3">
            <router-link to="/download" class="text-base font-semibold text-blue-600 py-2 px-4 rounded-lg hover:bg-blue-50 transition-colors">视频下载</router-link>
            <router-link to="/pricing" class="text-base font-medium text-gray-600 py-2 px-4 rounded-lg hover:bg-blue-50 transition-colors">套餐价格</router-link>
            <router-link to="/features" class="text-base font-medium text-gray-600 py-2 px-4 rounded-lg hover:bg-blue-50 transition-colors">功能特性</router-link>
            <router-link to="/tutorial" class="text-base font-medium text-gray-600 py-2 px-4 rounded-lg hover:bg-blue-50 transition-colors">使用教程</router-link>
            <button @click="handleUpgrade" class="btn-gradient-vip w-full">开通VIP</button>
          </nav>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">

      <!-- Hero区域 - 蓝紫渐变标题 -->
      <div class="text-center mb-12 lg:mb-16 animate-slideUp">
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-blue-50/80 border border-blue-200/50 rounded-full mb-6 backdrop-blur-sm">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          <span class="text-sm font-medium text-blue-700">支持100+视频平台</span>
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
          <span class="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 bg-clip-text text-transparent">万能视频下载器</span>
          <span class="block mt-2 text-3xl sm:text-4xl lg:text-5xl text-gray-800">一键下载任意视频</span>
        </h1>

        <p class="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          粘贴链接，一键下载 + AI 智能总结
        </p>

        <!-- 核心价值标签 - 圆角胶囊 + 浅蓝背景 -->
        <div class="flex flex-wrap justify-center gap-3 mb-8">
          <span class="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            高速下载
          </span>
          <span class="inline-flex items-center px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            AI 智能总结
          </span>
          <span class="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-full text-sm font-medium">
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            多清晰度
          </span>
        </div>
      </div>

      <!-- 核心输入区 - 优化后的样式 -->
      <div class="max-w-4xl mx-auto mb-12 lg:mb-16 animate-slideUp" style="animation-delay: 0.1s">
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg shadow-blue-100/50 border border-blue-100 p-6 sm:p-8 lg:p-10">
          <!-- 输入引导文案 -->
          <div class="flex items-center justify-between mb-4">
            <label class="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
              粘贴视频链接开始下载
            </label>
            <span class="text-xs text-gray-500">支持 HTTPS 链接</span>
          </div>

          <!-- 输入区域 - 圆角 + 轻微阴影 + 聚焦高亮 -->
          <div class="flex flex-col lg:flex-row gap-4">
            <div class="flex-1 relative">
              <div class="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                </svg>
              </div>
              <input
                v-model="videoUrl"
                type="text"
                placeholder="粘贴视频链接，如 https://www.bilibili.com/video/..."
                class="w-full pl-14 pr-6 py-4 rounded-xl border-2 border-gray-200 bg-white text-gray-900 placeholder-gray-400 transition-all duration-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 focus:outline-none shadow-sm hover:shadow-md"
                @keyup.enter="parseVideo"
                :disabled="loading"
              >
            </div>
            <!-- 蓝紫渐变按钮 + 悬停放大效果 -->
            <button
              @click="parseVideo"
              :disabled="!videoUrl.trim() || loading"
              class="text-lg px-10 py-4 min-w-[180px] flex items-center justify-center gap-3 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg shadow-blue-500/30 transition-all duration-200 hover:from-blue-700 hover:to-purple-700 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105 active:scale-100 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              <svg v-if="!loading" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              <svg v-else class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ loading ? '解析中...' : '立即解析' }}</span>
            </button>
          </div>

          <!-- 快速尝试标签 -->
          <div class="flex flex-wrap items-center gap-2 mt-4">
            <span class="text-sm text-gray-500 font-medium">快速尝试：</span>
            <button
              v-for="platform in quickPlatforms"
              :key="platform.id"
              @click="fillExample(platform.example)"
              class="platform-badge"
            >
              <span class="text-lg">{{ platform.icon }}</span>
              <span>{{ platform.name }}</span>
            </button>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="mt-4 p-4 bg-red-50 border-2 border-red-200 rounded-xl">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span class="text-red-700 text-sm font-medium">{{ error }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 使用步骤说明 - 优化后的样式 -->
      <div class="max-w-5xl 不要mx-auto mb-12 lg:mb-16 animate-slideUp" style="animation-delay: 0.2s">
        <div class="text-center mb-10">
          <h2 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">简单三步，轻松下载</h2>
          <p class="text-gray-500 text-sm">无需安装软件，浏览器内直接完成</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
          <!-- 步骤1 - 蓝色渐变圆形 + 白色图标 -->
          <div class="group p-6 text-center bg-white/50 rounded-2xl hover:bg-white/80 transition-all duration-200">
            <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/30 group-hover:shadow-xl group-hover:shadow-blue-500/40 transition-all">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
            </div>
            <div class="flex items-center justify-center gap-2 mb-3">
              <span class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">1</span>
              <h3 class="text-lg font-bold text-gray-900">粘贴链接</h3>
            </div>
            <p class="text-sm text-gray-500">从任意视频平台复制链接</p>
          </div>

          <!-- 步骤2 - 紫色渐变圆形 + 白色图标 -->
          <div class="group p-6 text-center bg-white/50 rounded-2xl hover:bg-white/80 transition-all duration-200">
            <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-purple-500/30 group-hover:shadow-xl group-hover:shadow-purple-500/40 transition-all">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </div>
            <div class="flex items-center justify-center gap-2 mb-3">
              <span class="w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
              <h3 class="text-lg font-bold text-gray-900">解析视频</h3>
            </div>
            <p class="text-sm text-gray-500">点击解析，AI 自动分析</p>
          </div>

          <!-- 步骤3 - 蓝紫渐变圆形 + 白色图标 -->
          <div class="group p-6 text-center bg-white/50 rounded-2xl hover:bg-white/80 transition-all duration-200">
            <div class="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/30 group-hover:shadow-xl group-hover:shadow-blue-500/40 transition-all">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
            </div>
            <div class="flex items-center justify-center gap-2 mb-3">
              <span class="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
              <h3 class="text-lg font-bold text-gray-900">下载视频</h3>
            </div>
            <p class="text-sm text-gray-500">选择清晰度，立即下载</p>
          </div>
        </div>
      </div>

      <!-- 解析结果区 - 双栏布局 -->
      <div v-if="videoData" class="max-w-7xl mx-auto animate-slideUp" style="animation-delay: 0.3s">
        <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">

          <!-- 左侧栏：视频信息 (40%宽度) -->
          <div class="lg:col-span-2">
            <div class="bg-white rounded-lg border border-gray-200 p-5 sticky top-24 shadow-sm">
              <!-- 视频封面 -->
              <div class="relative aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4">
                <img
                  :src="getThumbnailUrl(videoData.thumbnail)"
                  class="w-full h-full object-cover"
                >
                <!-- 时长标签 -->
                <div class="absolute bottom-3 right-3 bg-black/80 backdrop-blur-sm text-white text-xs px-3 py-1.5 rounded-lg font-medium">
                  {{ videoData.duration }}
                </div>
              </div>

              <!-- 视频信息 -->
              <h3 class="font-semibold text-gray-900 mb-2 line-clamp-2 text-sm leading-relaxed">
                {{ videoData.title }}
              </h3>
              <div class="flex items-center gap-3 text-xs text-gray-500 mb-4">
                <div class="flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                  <span>{{ videoData.uploader || '未知UP主' }}</span>
                </div>
                <div class="flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>{{ formatViewCount(videoData.view_count) }}</span>
                </div>
              </div>

              <!-- 清晰度选择 -->
              <div class="space-y-2 mb-4">
                <p class="text-xs font-medium text-gray-600 mb-2">选择质量</p>
                <div class="grid grid-cols-3 gap-2">
                  <button
                    v-for="format in displayFormats"
                    :key="format.format_id"
                    @click="selectedFormat = format.format_id"
                    class="quality-card px-3 py-2 rounded-md text-xs font-medium transition-all"
                    :class="selectedFormat === format.format_id ? 'quality-card-selected' : 'quality-card-default'"
                  >
                    {{ format.quality }}
                  </button>
                </div>
                <!-- 音频选项 -->
                <button
                  v-if="videoData.audio_only"
                  @click="selectedFormat = videoData.audio_only.format_id"
                  class="quality-card px-3 py-2 rounded-md text-xs font-medium transition-all w-full"
                  :class="selectedFormat === videoData.audio_only.format_id ? 'quality-card-selected' : 'quality-card-default'"
                >
                  🎵 音频
                </button>
              </div>

              <!-- 选中的格式信息 -->
              <div v-if="selectedFormatData" class="mb-4 text-xs text-gray-500">
                {{ selectedFormatData.ext?.toUpperCase() }} · {{ selectedFormatData.size_formatted || '未知大小' }}
              </div>

              <!-- 下载按钮 -->
              <button
                @click="downloadVideo"
                :disabled="downloading || !selectedFormat"
                class="w-full bg-[#1890ff] hover:bg-[#1677d9] text-white font-medium py-2.5 px-4 rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
              >
                <svg v-if="!downloading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ downloading ? `下载中 ${downloadProgress}%` : '下载视频' }}</span>
              </button>

              <!-- 下载进度条 -->
              <div v-if="downloading && downloadProgress > 0" class="mt-4">
                <div class="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-[#1890ff] transition-all duration-300" :style="{ width: downloadProgress + '%' }"></div>
                </div>
                <p class="text-center text-xs text-gray-600 mt-2">{{ downloadProgress }}%</p>
              </div>
            </div>
          </div>

          <!-- 右侧栏：AI总结 (60%宽度) -->
          <div class="lg:col-span-3">
            <!-- Tab切换栏 -->
            <div class="bg-white rounded-lg border border-gray-200 p-1.5 flex gap-1.5 mb-4">
              <button
                v-for="tab in aiTabs"
                :key="tab.key"
                @click="activeAITab = tab.key"
                class="flex-1 px-3 py-2 rounded-md font-medium text-xs transition-all duration-200 flex items-center justify-center gap-1.5"
                :class="activeAITab === tab.key
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
            <div class="bg-white rounded-lg border border-gray-200 p-5 h-[600px] overflow-y-auto shadow-sm">

              <!-- 视频总结 Tab - SSE逐字打字机效果 -->
              <div v-if="activeAITab === 'summary'" class="space-y-4">
                <!-- 初始加载状态 -->
                <div v-if="aiInitialLoading && !aiSummaryText" class="flex flex-col items-center justify-center py-16">
                  <div class="relative w-16 h-16 mb-4">
                    <div class="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
                    <div class="absolute inset-0 border-4 border-[#1677ff] rounded-full border-t-transparent animate-spin"></div>
                  </div>
                  <h3 class="text-sm font-semibold text-gray-900 mb-1">AI正在分析视频...</h3>
                  <p class="text-xs text-gray-500">提取字幕内容并生成总结</p>
                </div>

                <!-- 格式化总结内容 -->
                <div v-if="parsedSummary && parsedSummary.sections.length > 0" class="space-y-6">
                  <div v-for="(section, index) in parsedSummary.sections" :key="index" class="space-y-3">
                    <!-- 【核心知识要点】特殊样式 - 顶部间距 -->
                    <div v-if="section.title === '核心知识要点'" class="pt-3">
                      <!-- 标题 -->
                      <h3 class="text-base font-bold text-gray-900">{{ section.title }}</h3>

                      <!-- 列表项 -->
                      <div v-if="section.listItems && section.listItems.length > 0" class="space-y-2 mt-3">
                        <div
                          v-for="(item, itemIndex) in section.listItems"
                          :key="itemIndex"
                          class="flex items-start gap-2 text-sm text-gray-700"
                        >
                          <span class="text-[#1677ff] flex-shrink-0 mt-0.5">•</span>
                          <span>{{ item }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- 【内容大纲】特殊样式 - 支持章节标题 -->
                    <div v-else-if="section.title === '内容大纲'">
                      <!-- 标题 -->
                      <h3 class="text-base font-bold text-gray-900">{{ section.title }}</h3>

                      <!-- 章节标题和列表 -->
                      <div v-if="section.subsections && section.subsections.length > 0" class="space-y-4 mt-3">
                        <div v-for="(subsection, subIndex) in section.subsections" :key="subIndex" class="space-y-2">
                          <!-- 章节标题 (1. xxx) - 蓝色、16px、加粗、无缩进 -->
                          <h4 class="text-[16px] font-bold text-[#1677ff]">
                            {{ subsection.number }}{{ subsection.number ? '. ' : '' }}{{ subsection.title }}
                          </h4>

                          <!-- 章节列表内容 - 黑色、14px、左边缩进16px、圆点符号 -->
                          <div v-if="subsection.listItems && subsection.listItems.length > 0" class="space-y-2 ml-4">
                            <div
                              v-for="(item, itemIndex) in subsection.listItems"
                              :key="itemIndex"
                              class="flex items-start gap-2 text-[14px] text-gray-700"
                            >
                              <span class="text-[#1E40AF] flex-shrink-0 mt-0.5">•</span>
                              <span>{{ item }}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- 如果没有subsections但有listItems，显示原有列表（向后兼容） -->
                      <div v-else-if="section.listItems && section.listItems.length > 0" class="space-y-2 mt-3">
                        <div
                          v-for="(item, itemIndex) in section.listItems"
                          :key="itemIndex"
                          class="flex items-start gap-2 text-sm text-gray-700"
                        >
                          <span class="text-[#1677ff] flex-shrink-0 mt-0.5">•</span>
                          <span>{{ item }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- 【视频概述】和其他模块 - 保持原有样式 -->
                    <div v-else>
                      <!-- 标题 -->
                      <h3 class="text-base font-bold text-gray-900">{{ section.title }}</h3>

                      <!-- 章节内容 -->
                      <div v-if="section.content" class="text-sm text-gray-700 leading-relaxed pl-4">
                        {{ section.content }}
                      </div>

                      <!-- 列表项 -->
                      <div v-if="section.listItems && section.listItems.length > 0" class="space-y-2">
                        <div
                          v-for="(item, itemIndex) in section.listItems"
                          :key="itemIndex"
                          class="flex items-start gap-2 text-sm text-gray-700"
                        >
                          <span class="text-[#1677ff] flex-shrink-0 mt-0.5">•</span>
                          <span>{{ item }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 如果解析失败，显示原始文本 -->
                <div v-else-if="aiSummaryText" class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {{ aiSummaryText }}
                </div>

                <!-- AI生成中状态 - 在内容下方显示 -->
                <div v-if="aiStreaming && aiSummaryText" class="flex items-center justify-center gap-2 py-3 border-t border-gray-100 mt-4">
                  <div class="flex gap-1">
                    <span class="w-1.5 h-1.5 bg-[#1677ff] rounded-full animate-bounce" style="animation-delay: 0s"></span>
                    <span class="w-1.5 h-1.5 bg-[#1677ff] rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                    <span class="w-1.5 h-1.5 bg-[#1677ff] rounded-full animate-bounce" style="animation-delay: 0.4s"></span>
                  </div>
                  <span class="text-xs text-gray-500">AI正在生成中...</span>
                </div>

                <!-- 空状态 -->
                <div v-if="!aiInitialLoading && !aiSummaryText" class="text-center py-12">
                  <div class="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                    </svg>
                  </div>
                  <h3 class="text-sm font-semibold text-gray-900 mb-1">等待AI分析</h3>
                  <p class="text-xs text-gray-500">视频解析完成后自动开始</p>
                </div>
              </div>

              <!-- 字幕文本 Tab -->
              <div v-else-if="activeAITab === 'subtitle'" class="space-y-3">
                <!-- 字幕功能按钮 -->
                <div v-if="aiSubtitles.length > 0" class="flex items-center justify-between mb-3">
                  <div class="text-xs text-gray-500">
                    共 {{ aiSubtitles.length }} 条字幕
                  </div>
                  <div class="flex gap-2">
                    <button
                      @click="toggleSubtitleExpanded"
                      class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors flex items-center gap-1"
                      :class="subtitleExpanded ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' : 'bg-[#1677ff] text-white hover:bg-[#1455cc]'"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path v-if="!subtitleExpanded" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                      </svg>
                      {{ subtitleExpanded ? '收起全部' : '展开全部' }}
                    </button>
                    <button
                      @click="downloadSubtitle('srt')"
                      class="px-3 py-1.5 text-xs font-medium rounded-lg bg-[#1677ff] text-white hover:bg-[#1455cc] transition-colors flex items-center gap-1"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                      </svg>
                      下载SRT
                    </button>
                    <button
                      @click="downloadSubtitle('txt')"
                      class="px-3 py-1.5 text-xs font-medium rounded-lg bg-[#1677ff] text-white hover:bg-[#1455cc] transition-colors flex items-center gap-1"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                      </svg>
                      下载TXT
                    </button>
                  </div>
                </div>

                <div v-if="aiSubtitles.length > 0" class="space-y-3 max-h-[450px] overflow-y-auto">
                  <div
                    v-for="(sub, index) in (subtitleExpanded ? aiSubtitles : aiSubtitles.slice(0, 10))"
                    :key="index"
                    class="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div class="text-xs text-gray-400 mb-1 font-mono">{{ sub.time }}</div>
                    <div class="text-sm text-gray-700">{{ sub.text }}</div>
                  </div>
                  <!-- 收起时显示提示 -->
                  <div v-if="!subtitleExpanded && aiSubtitles.length > 10" class="text-center py-3">
                    <span class="text-xs text-gray-500">还有 {{ aiSubtitles.length - 10 }} 条字幕，点击"展开全部"查看</span>
                  </div>
                </div>
                <div v-else class="text-center py-12">
                  <div class="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                  <h3 class="text-sm font-semibold text-gray-900 mb-1">字幕文本</h3>
                  <p class="text-xs text-gray-500">AI分析完成后自动显示</p>
                </div>
              </div>

              <!-- 思维导图 Tab -->
              <div v-else-if="activeAITab === 'mindmap'" class="space-y-3">
                <!-- 思维导图功能按钮 -->
                <div v-if="aiMindmap" class="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <div class="text-xs text-gray-500">
                    交互式思维导图
                  </div>
                  <div class="flex gap-2">
                    <button
                      @click="mindmapViewMode = mindmapViewMode === 'interactive' ? 'markdown' : 'interactive'"
                      class="px-3 py-1.5 text-xs font-medium rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors flex items-center gap-1"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                      </svg>
                      {{ mindmapViewMode === 'interactive' ? 'Markdown视图' : '交互视图' }}
                    </button>
                    <button
                      @click="toggleMindmapFullscreen"
                      class="px-3 py-1.5 text-xs font-medium rounded-lg bg-[#1677ff] text-white hover:bg-[#1455cc] transition-colors flex items-center gap-1"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
                      </svg>
                      全屏查看
                    </button>
                    <!-- 下载格式切换按钮 -->
                    <button
                      @click="toggleMindmapDownloadFormat"
                      class="px-3 py-1.5 text-xs font-medium rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors flex items-center gap-1"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                      </svg>
                      {{ mindmapDownloadFormat === 'svg' ? 'SVG' : 'MD' }}
                    </button>
                    <button
                      @click="downloadMindmap(mindmapDownloadFormat)"
                      class="px-3 py-1.5 text-xs font-medium rounded-lg bg-[#1677ff] text-white hover:bg-[#1455cc] transition-colors flex items-center gap-1"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                      </svg>
                      下载{{ mindmapDownloadFormat === 'svg' ? 'SVG' : 'MD' }}
                    </button>
                  </div>
                </div>

                <!-- 思维导图内容 -->
                <div v-if="aiMindmap" class="relative">
                  <div
                    :class="mindmapFullscreen ? 'fixed inset-0 z-50 bg-white p-8 overflow-auto' : 'bg-gray-50 rounded-lg p-4'"
                  >
                    <div v-if="mindmapFullscreen" class="flex justify-end mb-4">
                      <button
                        @click="toggleMindmapFullscreen"
                        class="px-3 py-1.5 text-xs font-medium rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors flex items-center gap-1"
                      >
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                        关闭全屏
                      </button>
                    </div>

                    <!-- 交互式思维导图 -->
                    <svg
                      v-if="mindmapViewMode === 'interactive'"
                      ref="mindmapSvg"
                      class="mindmap-svg w-full"
                      :style="mindmapFullscreen ? 'height: calc(100vh - 100px)' : 'height: 600px'"
                    ></svg>

                    <!-- Markdown 文本视图 -->
                    <pre
                      v-else
                      class="mindmap-markdown text-sm text-gray-700 leading-relaxed whitespace-pre-wrap font-mono bg-white p-4 rounded-lg overflow-auto"
                      :style="mindmapFullscreen ? 'max-height: calc(100vh - 100px)' : 'max-height: 450px'"
                    >{{ aiMindmap }}</pre>
                  </div>
                </div>
                <div v-else class="text-center py-12">
                  <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7"></path>
                  </svg>
                  <p class="text-xs">思维导图正在生成中...</p>
                </div>
              </div>

              <!-- AI问答 Tab -->
              <div v-else-if="activeAITab === 'chat'" class="flex flex-col h-full">
                <div class="flex-1 space-y-3 max-h-[350px] overflow-y-auto mb-3" id="aiChatContainer">
                  <div v-if="aiChatMessages.length === 0" class="text-center py-10">
                    <div class="w-14 h-14 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                      <svg class="w-7 h-7 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                      </svg>
                    </div>
                    <h3 class="text-sm font-semibold text-gray-900 mb-1">AI问答助手</h3>
                    <p class="text-xs text-gray-500">AI分析完成后可提问</p>
                  </div>
                  <div
                    v-for="(msg, index) in aiChatMessages"
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
                <div class="flex gap-2">
                  <input
                    v-model="aiChatQuestion"
                    type="text"
                    placeholder="向AI提问关于视频内容的问题..."
                    class="flex-1 px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1890ff] focus:border-transparent"
                    @keyup.enter="sendAIChat"
                    :disabled="aiChatLoading"
                  >
                  <button
                    @click="sendAIChat"
                    :disabled="!aiChatQuestion.trim() || aiChatLoading"
                    class="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg text-xs transition-all flex items-center justify-center"
                  >
                    发送
                  </button>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>

      <!-- VIP转化引导区 - 蓝紫渐变 + 发光效果 -->
      <div class="max-w-5xl mx-auto mt-16 lg:mt-20 animate-slideUp" style="animation-delay: 0.4s">
        <div class="bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 rounded-3xl p-8 lg:p-10 shadow-2xl shadow-blue-500/30 relative overflow-hidden">
          <!-- 背景发光效果 -->
          <div class="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-purple-400/20 animate-pulse"></div>
          <div class="absolute -top-20 -right-20 w-40 h-40 bg-blue-400/30 rounded-full blur-3xl"></div>
          <div class="absolute -bottom-20 -left-20 w-40 h-40 bg-purple-400/30 rounded-full blur-3xl"></div>

          <div class="relative flex flex-col lg:flex-row items-center gap-8">
            <div class="flex-1 text-center lg:text-left">
              <h3 class="text-2xl lg:text-3xl font-bold text-white mb-6">
                解锁全部功能，享受VIP特权
              </h3>
              <div class="grid grid-cols-2 gap-4 text-left">
                <!-- 无限下载 -->
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                  </div>
                  <div>
                    <div class="font-semibold text-white">无限下载</div>
                    <div class="text-xs text-blue-200">不限次数，畅快使用</div>
                  </div>
                </div>
                <!-- AI 总结 -->
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                    </svg>
                  </div>
                  <div>
                    <div class="font-semibold text-white">AI 总结</div>
                    <div class="text-xs text-blue-200">智能提取视频要点</div>
                  </div>
                </div>
                <!-- 超清画质 -->
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                    </svg>
                  </div>
                  <div>
                    <div class="font-semibold text-white">超清画质</div>
                    <div class="text-xs text-blue-200">支持4K/8K下载</div>
                  </div>
                </div>
                <!-- 隐私保护 -->
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                    </svg>
                  </div>
                  <div>
                    <div class="font-semibold text-white">隐私保护</div>
                    <div class="text-xs text-blue-200">下载记录不留痕</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex-shrink-0 text-center">
              <div class="mb-4">
                <span class="text-5xl lg:text-6xl font-bold text-white">¥29</span>
                <span class="text-xl text-blue-200">/月</span>
              </div>
              <!-- 紫色渐变按钮 + 悬停上浮效果 -->
              <button @click="handleUpgrade" class="w-full text-lg px-10 py-4 rounded-xl font-bold text-white bg-gradient-to-r from-purple-500 to-pink-500 shadow-xl shadow-purple-500/30 transition-all duration-300 hover:from-purple-600 hover:to-pink-600 hover:shadow-2xl hover:shadow-purple-500/40 hover:-translate-y-1 active:translate-y-0">
                立即开通VIP
              </button>
              <p class="text-xs text-blue-200 mt-3">随时取消，无隐藏费用</p>
            </div>
          </div>
        </div>
      </div>

    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-200 mt-16 lg:mt-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <!-- 品牌信息 -->
          <div>
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
              </div>
              <div>
                <div class="font-bold text-gray-900">FetchVid</div>
                <div class="text-xs text-gray-500">万能视频下载器</div>
              </div>
            </div>
            <p class="text-sm text-gray-600">支持100+视频平台，一键下载高清视频，AI智能总结视频内容。</p>
          </div>

          <!-- 快速链接 -->
          <div>
            <h4 class="font-semibold text-gray-900 mb-4">快速链接</h4>
            <ul class="space-y-2">
              <li><router-link to="/download" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">视频下载</router-link></li>
              <li><router-link to="/summarize" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">AI总结</router-link></li>
              <li><a href="#" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">使用教程</a></li>
              <li><a href="#" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">常见问题</a></li>
            </ul>
          </div>

          <!-- 联系方式 -->
          <div>
            <h4 class="font-semibold text-gray-900 mb-4">联系我们</h4>
            <ul class="space-y-2">
              <li class="text-sm text-gray-600">客服邮箱: support@fetchvid.com</li>
              <li class="text-sm text-gray-600">工作时间: 9:00-21:00</li>
              <li class="text-sm text-gray-600">响应时间: <1小时</li>
            </ul>
          </div>
        </div>

        <div class="pt-8 border-t border-gray-200">
          <div class="text-center text-sm text-gray-500">
            <p>© 2024 FetchVid · 万能视频下载器 · 支持B站/YouTube/微博/抖音等平台</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'
import UserMenu from '../components/UserMenu.vue'
import auth from '../auth/auth'
import { getFingerprint } from '../utils/fingerprint'

// 🔥 加在这里：强制刷新次数显示
const triggerUpdate = ref(0)
let removeAuthListener = null
const videoUrl = ref('')
const loading = ref(false)
const error = ref('')
const videoData = ref(null)
const originalUrl = ref('')
const selectedFormat = ref('')
const downloading = ref(false)
const downloadProgress = ref(0)
const downloadTaskId = ref(null)
const mobileMenuOpen = ref(false)

// AI分析相关状态
const aiProgress = ref(0)
const aiSubtitles = ref([])
const aiAnalysisComplete = ref(false)
const aiInitialLoading = ref(true) // 初始加载状态

// AI Tabs相关状态
const aiTabs = ref([
  { key: 'summary', label: '视频总结', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { key: 'subtitle', label: '字幕文本', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { key: 'mindmap', label: '思维导图', icon: 'M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7' },
  { key: 'chat', label: 'AI问答', icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z' }
])
const activeAITab = ref('summary')
const aiStreaming = ref(false)
const aiSummaryText = ref('')  // 改为纯文本，不再解析为sections
const aiMindmap = ref(null)
const aiChatMessages = ref([])
const aiChatQuestion = ref('')
const aiChatLoading = ref(false)
const aiRemainingQuota = ref(999)

// 字幕相关状态
const subtitleExpanded = ref(false)
const subtitleFormat = ref('srt') // srt 或 txt

// 思维导图相关状态
const mindmapFullscreen = ref(false)
const mindmapViewMode = ref('interactive') // 'interactive' 或 'markdown'
const mindmapDownloadFormat = ref('svg') // 'png' 或 'md'，默认PNG
const mindmapSvg = ref(null)
const markmapInstance = ref(null)

// 快速尝试平台
const quickPlatforms = [
  { id: 'youtube', name: 'YouTube', icon: '▶️', example: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' },
  { id: 'bilibili', name: 'Bilibili', icon: '📺', example: 'https://www.bilibili.com/video/BV1xx411c7mu' },
  { id: 'twitter', name: 'Twitter', icon: '🐦', example: 'https://twitter.com/user/status/123456' },
  { id: 'weibo', name: '微博', icon: '🌭', example: 'https://weibo.com/tv/show/123456' }
]

// 计算属性 - 解析后的总结内容
const parsedSummary = computed(() => {
  if (!aiSummaryText.value) return null
  return parseSummaryText(aiSummaryText.value)
})
const displayFormats = computed(() => {
  if (!videoData.value?.formats) return []
  return videoData.value.formats.map(f => ({
    ...f,
    recommended: f.quality === '1080p' || f.format_id === videoData.value.formats[0]?.format_id
  }))
})

const selectedFormatData = computed(() => {
  if (!videoData.value?.formats) return null
  return videoData.value.formats.find(f => f.format_id === selectedFormat.value)
})

onMounted(() => {
  // 🔥 加这一段：auth 变化自动刷新次数
  removeAuthListener = auth.addListener(() => {
    triggerUpdate.value++
  })
})

// 方法
// Handle upgrade navigation
const handleUpgrade = () => {
  // Navigate to upgrade page
  window.location.href = '/upgrade'
}

const getThumbnailUrl = (url) => {
  if (!url) return ''
  return `/api/proxy/thumbnail?url=${encodeURIComponent(url)}`
}

const formatViewCount = (count) => {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万'
  return count.toLocaleString()
}

const fillExample = (url) => {
  videoUrl.value = url
  error.value = ''
}

// 格式化时间（秒转为 HH:MM:SS 或 MM:SS）
const formatTime = (seconds) => {
  if (!seconds || seconds < 0) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  if (mins >= 60) {
    const hours = Math.floor(mins / 60)
    const remainingMins = mins % 60
    return `${String(hours).padStart(2, '0')}:${String(remainingMins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

// 解析总结文本为结构化数据（扩展版，支持章节标题和核心知识要点）
const parseSummaryText = (text) => {
  if (!text) return { sections: [] }

  const sections = []
  const lines = text.split('\n')
  let currentSection = null
  let currentContent = []
  let currentListItems = []
  let currentSubsections = []  // 新增：用于存储【内容大纲】的章节标题
  let inContentOutline = false  // 标记是否在【内容大纲】模块内

  for (let line of lines) {
    line = line.trim()

    // 检测主标题（【xxx】或 # xxx）
    if (line.match(/^【(.+)】$/) || line.match(/^#+\s+(.+)$/)) {
      // 保存上一个section
      if (currentSection) {
        sections.push({
          title: currentSection,
          content: currentContent.join('\n').trim(),
          listItems: currentListItems,
          subsections: currentSubsections  // 新增：章节标题列表
        })
      }

      // 开始新section
      const titleMatch = line.match(/^【(.+)】$/)
      const headingMatch = line.match(/^#+\s+(.+)$/)
      currentSection = titleMatch ? titleMatch[1] : headingMatch[1]
      currentContent = []
      currentListItems = []
      currentSubsections = []

      // 检测是否是【内容大纲】模块
      inContentOutline = currentSection === '内容大纲'
    }
    // 在【内容大纲】模块内，检测章节标题（1. xxx、2. xxx 等）
    else if (inContentOutline && line.match(/^\d+\.\s+(.+)$/)) {
      const titleMatch = line.match(/^\d+\.\s+(.+)$/)
      const numberMatch = line.match(/^(\d+)\.\s+(.+)$/)
      const chapterNumber = numberMatch ? numberMatch[1] : ''
      const chapterTitle = titleMatch[1].trim()
      if (chapterTitle) {
        // 保存上一个章节（如果有列表项）
        if (currentSubsections.length > 0 && currentSubsections[currentSubsections.length - 1].listItems.length === 0) {
          // 上一个章节没有列表项，直接替换标题
          currentSubsections[currentSubsections.length - 1].title = chapterTitle
          currentSubsections[currentSubsections.length - 1].number = chapterNumber
        } else {
          // 创建新章节
          currentSubsections.push({
            number: chapterNumber,  // 保存编号
            title: chapterTitle,
            listItems: []
          })
        }
      }
    }
    // 检测列表项（- 或 •）- 注意：不再匹配 1. 开头（那是章节标题）
    else if (line.match(/^[-•]\s*/)) {
      const listItem = line.replace(/^[-•]\s*/, '').trim()
      if (listItem) {
        if (inContentOutline && currentSubsections.length > 0) {
          // 在【内容大纲】内，添加到当前章节的列表
          currentSubsections[currentSubsections.length - 1].listItems.push(listItem)
        } else {
          // 在其他模块内，添加到主列表
          currentListItems.push(listItem)
        }
      }
    }
    // 普通内容
    else if (line) {
      currentContent.push(line)
    }
  }

  // 保存最后一个section
  if (currentSection) {
    sections.push({
      title: currentSection,
      content: currentContent.join('\n').trim(),
      listItems: currentListItems,
      subsections: currentSubsections
    })
  }

  return { sections }
}

// 格式化总结文本（将横线改为圆点）
const formatSummaryText = (text) => {
  if (!text) return ''
  return text
    .replace(/^[-\u2014\u2013]\s*/gm, '\u2022 ')  // 将横线改为圆点
    .replace(/^\d+\.\s*/gm, (match) => '\u2022 ')  // 将数字序号改为圆点
}

// 下载字幕
const downloadSubtitle = (format = 'srt') => {
  if (aiSubtitles.value.length === 0) {
    ElMessage.warning('暂无字幕可下载')
    return
  }

  let content = ''
  const filename = `${videoData.value?.title || 'subtitle'}.${format}`

  if (format === 'st') {
    // SRT格式
    aiSubtitles.value.forEach((sub, index) => {
      content += `${index + 1}\n`
      content += `${sub.time} --> ${formatTime(sub.end)}\n`
      content += `${sub.text}\n\n`
    })
  } else {
    // TXT格式
    content = aiSubtitles.value.map(sub => `[${sub.time}] ${sub.text}`).join('\n')
  }

  // 创建下载
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success(`字幕已下载为 ${format.toUpperCase()} 格式`)
}

// 切换字幕展开/收起
const toggleSubtitleExpanded = () => {
  subtitleExpanded.value = !subtitleExpanded.value
}

// 下载思维导图
const downloadMindmap = async (format = 'md') => {
  if (!aiMindmap.value) {
    ElMessage.warning('暂无思维导图可下载')
    return
  }

  const filename = `${videoData.value?.title || 'mindmap'}.${format}`

  if (format === 'md') {
    // MD 下载（保持不变）
    const blob = new Blob([aiMindmap.value], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('思维导图已下载为 MD 格式')
  } 
  else if (format === 'svg') {
    if (!mindmapSvg.value) {
      ElMessage.warning('思维导图未渲染完成，请稍后再试')
      return
    }

    try {
      // ✅ 方案：直接导出 SVG，让用户手动转 PNG（最稳妥，无跨域报错）
      const svgData = new XMLSerializer().serializeToString(mindmapSvg.value)
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
      const svgUrl = URL.createObjectURL(svgBlob)
      
      const link = document.createElement('a')
      link.href = svgUrl
      link.download = filename.replace('.png', '.svg')
      link.click()
      URL.revokeObjectURL(svgUrl)
      
      ElMessage.success('已导出 SVG 格式，如需可在浏览器打开后右键「另存为 PNG」')
    } catch (error) {
      console.error('导出错误:', error)
      ElMessage.error('导出失败，请使用 MD 格式')
    }
  }
}

// 切换思维导图全屏
const toggleMindmapFullscreen = () => {
  mindmapFullscreen.value = !mindmapFullscreen.value
  // 全屏切换后重新渲染思维导图
  if (mindmapFullscreen.value && mindmapViewMode.value === 'interactive') {
    nextTick(() => renderMindmap())
  }
}

// 切换思维导图下载格式
const toggleMindmapDownloadFormat = () => {
  mindmapDownloadFormat.value = mindmapDownloadFormat.value === 'svg' ? 'md' : 'svg'
}

// ==============================================
// 【交互式思维导图】使用 markmap 渲染
// ==============================================
const renderMindmap = async () => {
  if (!mindmapSvg.value || !aiMindmap.value) return

  try {
    console.log('🚀 开始渲染交互式思维导图')
    const transformer = new Transformer()
    const { root } = transformer.transform(aiMindmap.value)

    if (markmapInstance.value) {
      try { markmapInstance.value.destroy() } catch (e) {}
    }

    // Markmap配置说明：
    // - fitRatio: 适配比例，值越大导图越大（0-1）
    // - spacingHorizontal: 水平节点间距
    // - spacingVertical: 垂直节点间距
    // - initialExpandLevel: 初始展开层级（-1表示全部展开）
    markmapInstance.value = Markmap.create(mindmapSvg.value, {
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

    markmapInstance.value.setData(root)

    // 优化缩放和居中逻辑
    setTimeout(() => {
      if (markmapInstance.value) {
        // 先适配容器
        markmapInstance.value.fit()

        // 根据内容复杂度动态调整缩放
        const contentLength = aiMindmap.value.length
        const scaleMultiplier = contentLength > 3000 ? 1.5 : contentLength > 1500 ? 1.8 : 2.0
        markmapInstance.value.rescale(scaleMultiplier)

        // 使用 center() 方法居中显示
        setTimeout(() => {
          if (markmapInstance.value) {
            markmapInstance.value.center()
          }
        }, 100)
      }
    }, 300)

    console.log('🎉 思维导图渲染完成')
  } catch (error) {
    console.error('❌ 思维导图渲染失败:', error)
    mindmapViewMode.value = 'markdown'
  }
}
// 监听思维导图数据变化
watch(aiMindmap, (newVal) => {
  console.log('🔍 [VideoDownload] aiMindmap 变化')
  console.log('📝 [VideoDownload] 新值长度:', newVal?.length || 0)

  if (newVal && mindmapViewMode.value === 'interactive') {
    nextTick(() => {
      renderMindmap()
    })
  }
})

// 监听视图模式切换
watch(mindmapViewMode, (newMode) => {
  console.log('🔄 [VideoDownload] 思维导图视图模式切换:', newMode)

  if (newMode === 'interactive' && aiMindmap.value) {
    nextTick(() => {
      renderMindmap()
    })
  }
})

// 监听 Tab 切换
watch(activeAITab, (newTab) => {
  console.log('🔄 [VideoDownload] AI Tab 切换:', newTab)

  if (newTab === 'mindmap' && aiMindmap.value && mindmapViewMode.value === 'interactive') {
    nextTick(() => {
      renderMindmap()
    })
  }
})

// 组件卸载时清理
onUnmounted(() => {
   if (removeAuthListener) removeAuthListener()
  if (markmapInstance.value) {
    try {
      markmapInstance.value.destroy()
    } catch (e) {
      console.error('清理思维导图实例失败:', e)
    }
  }
})

// 解析视频 - 同时触发AI分析
const parseVideo = async () => {
  downloading.value = false
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

  loading.value = true
  error.value = ''
  videoData.value = null

  // 重置AI状态
  aiProgress.value = 0
  aiSubtitles.value = []
  aiAnalysisComplete.value = false
  aiStreaming.value = false
  aiSummaryText.value = ''
  aiMindmap.value = null

  try {
    const response = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })

    const result = await response.json()

    // 检查是否是次数不足错误
    if (result.code === 'QUOTA_EXCEEDED') {
      loading.value = false
      error.value = result.message || '今日解析次数已用完'
      if (result.require_login) {
        window.dispatchEvent(new CustomEvent('auth:login-required'))
      } else {
        window.dispatchEvent(new CustomEvent('auth:upgrade-required'))
      }
      return
    }

    if (result.success) {
      videoData.value = result.data
      originalUrl.value = url

      // 动态获取所有清晰度格式，包括音频
      if (result.data.formats && result.data.formats.length > 0) {
        const format1080p = result.data.formats.find(f => f.quality === '1080p')
        selectedFormat.value = format1080p?.format_id || result.data.formats[0].format_id
      }

      ElMessage.success('解析成功！')

      // 解析成功后自动开始AI分析
      startAIAnalysis()
    } else {
      error.value = result.message
      ElMessage.error(result.message)
    }
  } catch (err) {
    error.value = '网络错误，请确保后端服务已启动'
    ElMessage.error('网络错误')
  } finally {
    loading.value = false
  }
}

// 开始AI分析 - SSE逐字流式加载
const startAIAnalysis = async () => {
  if (!originalUrl.value) return

  aiInitialLoading.value = true
  aiStreaming.value = false
  aiSummaryText.value = ''
  aiMindmap.value = null
  aiSubtitles.value = []
  aiChatMessages.value = []
  activeAITab.value = 'summary'

  // 设置超时控制（5分钟超时，ASR可能需要较长时间）
  const AI_TIMEOUT = 300000 // 5分钟
  let timeoutTimer = null
  let lastDataTime = Date.now()
  let hasReceivedData = false // 标记是否已收到数据

  // 超时检查定时器：如果60秒内没有收到任何数据，提示用户
  const NO_DATA_TIMEOUT = 60000 // 60秒无数据超时
  let noDataTimer = setInterval(() => {
    const timeSinceLastData = Date.now() - lastDataTime
    if (timeSinceLastData > NO_DATA_TIMEOUT && aiInitialLoading.value && !hasReceivedData) {
      clearInterval(noDataTimer)
      aiInitialLoading.value = false
      ElMessage.warning('AI分析响应较慢，请稍候或刷新重试')
    }
  }, 5000)

  // 清理总超时定时器的函数
  const clearTimeoutTimer = () => {
    if (timeoutTimer) {
      clearTimeout(timeoutTimer)
      timeoutTimer = null
    }
    if (noDataTimer) {
      clearInterval(noDataTimer)
      noDataTimer = null
    }
  }

  try {
    // 如果已有字幕文本，直接传递给后端，避免重复提取
    const subtitleText = aiSubtitles.value.length > 0
      ? aiSubtitles.value.map(sub => sub.text).join('\n')
      : null

    // 设置总超时
    timeoutTimer = setTimeout(() => {
      clearTimeoutTimer()
      aiInitialLoading.value = false
      aiStreaming.value = false
      ElMessage.error('AI分析超时，请稍后重试或尝试其他视频')
    }, AI_TIMEOUT)

    // 获取fingerprint和token
    const fingerprint = getFingerprint()
    const token = auth.getToken()

    // 构建请求头
    const headers = {
      'Content-Type': 'application/json'
    }
    if (fingerprint) {
      headers['X-Fingerprint'] = fingerprint
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch('/api/ai/summarize/char-stream', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        url: originalUrl.value,
        title: videoData.value?.title || '',
        description: videoData.value?.description || '',
        subtitle_text: subtitleText
      })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    // 读取SSE流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentEventType = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      // 更新最后收到数据的时间
      lastDataTime = Date.now()

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        // 解析SSE事件: event: xxx\ndata: xxx\n\n
        if (line.startsWith('event: ')) {
          currentEventType = line.slice(7).trim()
          continue
        }

        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            // 使用从event:行捕获的事件类型
            if (currentEventType === 'subtitle') {
              // 收到第一个数据事件，清理总超时定时器
              if (!hasReceivedData) {
                hasReceivedData = true
                clearTimeoutTimer()
              }

              // 字幕事件 - 兼容多种格式
              console.log('🎬 [VideoDownload] 收到字幕事件')
              console.log('📦 [VideoDownload] data:', data)

              // 优先使用 subtitles (已格式化的)
              let subtitlesData = data.subtitles || data.segments || []

              console.log('📊 [VideoDownload] subtitlesData 长度:', subtitlesData.length)

              // 如果有 text 字段但没有 subtitles，解析 text
              if (!subtitlesData.length && data.text) {
                const text = data.text || ''
                subtitlesData = text.split('\n').map((line, idx) => ({
                  time: `00:${String(Math.floor(idx * 3 / 60)).padStart(2, '0')}:${String((idx * 3) % 60).padStart(2, '0')}`,
                  text: line.trim()
                }))
              }

              // 确保每条字幕都有 time 和 text 字段
              if (subtitlesData.length > 0) {
                const firstSub = subtitlesData[0]

                // 如果没有 time 字段但有 start 字段，生成 time
                if (!firstSub.time && firstSub.start !== undefined) {
                  subtitlesData = subtitlesData.map(sub => {
                    const start = sub.start || 0
                    const minutes = Math.floor(start / 60)
                    const seconds = Math.floor(start % 60)
                    return {
                      ...sub,
                      time: `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
                    }
                  })
                }
              }

              // 确保 subtitlesData 包含必要的字段
              aiSubtitles.value = subtitlesData.map(seg => {
                if (seg.time) {
                  return {
                    time: seg.time,
                    start: seg.start || 0,
                    end: seg.end || 0,
                    text: seg.text || ''
                  }
                }
                const start = seg.start || seg.start_time || 0
                const end = seg.end || seg.end_time || (start + 3)
                return {
                  time: formatTime(start),
                  start: start,
                  end: end,
                  text: seg.text || ''
                }
              }).filter(s => s.text)
            }
            else if (currentEventType === 'summary' && data.token) {
              // 收到第一个数据事件，清理总超时定时器
              if (!hasReceivedData) {
                hasReceivedData = true
                clearTimeoutTimer()
              }

              // 隐藏初始加载，开始流式输出
              if (aiInitialLoading.value) {
                aiInitialLoading.value = false
                aiStreaming.value = true
              }

              // 逐token打字机效果 - 直接追加纯文本
              aiSummaryText.value += data.token

              // 更新进度
              if (aiProgress.value < 90) {
                aiProgress.value = Math.min(aiProgress.value + 1, 90)
              }
            }
            else if (currentEventType === 'mindmap') {
              // 收到第一个数据事件，清理总超时定时器
              if (!hasReceivedData) {
                hasReceivedData = true
                clearTimeoutTimer()
              }

              // 思维导图事件 - 纯文本格式
              const mindmapText = data.text || data.content || ''
              if (mindmapText) {
                aiMindmap.value = mindmapText
              }
            }
            else if (currentEventType === 'quota') {
              // 配额信息
              aiRemainingQuota.value = data.remaining
            }
            else if (currentEventType === 'done') {
              // 完成
              aiProgress.value = 100
              aiStreaming.value = false
              aiInitialLoading.value = false
              aiAnalysisComplete.value = true
              ElMessage.success('AI分析完成！')

              // 刷新剩余次数
              auth.refreshQuota()
            }
            else if (currentEventType === 'error') {
              throw new Error(data.message || '生成失败')
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e, line)
          }
        }
      }
    }

  } catch (err) {
    console.error('AI分析失败:', err)
    aiStreaming.value = false
    aiInitialLoading.value = false
    ElMessage.error(err.message || 'AI分析失败')
  } finally {
    // 清理定时器
    clearTimeoutTimer()
  }
}

const downloadVideo = async () => {
  if (!selectedFormat.value) {
    ElMessage.warning('请先选择清晰度')
    return
  }

  // 检查剩余次数（前端预检查）
  const quota = auth.quota
  if (quota && typeof quota.download_remaining === 'number' && quota.download_remaining <= 0) {
    const role = auth.getRole()
    if (role === 'guest') {
      ElMessage.warning('今日下载次数已用完，注册后每日3次')
      window.dispatchEvent(new CustomEvent('auth:login-required'))
    } else {
      ElMessage.warning('今日下载次数已用完，开通VIP无限使用')
      window.dispatchEvent(new CustomEvent('auth:upgrade-required'))
    }
    return
  }

  downloading.value = true
  downloadProgress.value = 0
  let shouldContinuePolling = true  // 轮询控制标志

  try {
    ElMessage.info('开始下载，请稍候...')

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

    const startResponse = await fetch('/api/proxy/download', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        video_url: originalUrl.value,
        filename: videoData.value.title,
        format_id: selectedFormat.value
      })
    })

    const startData = await startResponse.json()
    console.log('[DOWNLOAD] 开始下载响应:', startData)

    // 检查是否是次数不足错误
    if (startData.code === 'QUOTA_EXCEEDED') {
      downloading.value = false
      if (startData.require_login) {
        ElMessage.warning(startData.message || '今日下载次数已用完')
        window.dispatchEvent(new CustomEvent('auth:login-required'))
      } else {
        ElMessage.warning(startData.message || '今日下载次数已用完')
        window.dispatchEvent(new CustomEvent('auth:upgrade-required'))
      }
      return
    }

    // 增强错误处理：检查 success 字段和 status 字段
    if (startData.success === false || startData.status === 'error') {
      const errorMsg = startData.message || startData.error || '下载失败，请稍后重试'
      throw new Error(errorMsg)
    }

    // 如果没有task_id，说明可能出错了
    if (!startData.task_id) {
      throw new Error(startData.message || '无法创建下载任务')
    }

    downloadTaskId.value = startData.task_id

    const pollStatus = async () => {
  if (!shouldContinuePolling) {
    console.log('[DOWNLOAD] 轮询已停止')
    return
  }

  try {
    const statusResponse = await fetch(`/api/proxy/download/status/${downloadTaskId.value}`)

    if (!statusResponse.ok) {
      throw new Error(`服务器错误: ${statusResponse.status}`)
    }

    let status
    try {
      status = await statusResponse.json()
      console.log('[DOWNLOAD] 状态响应:', status)
    } catch (jsonErr) {
      throw new Error('服务器响应格式错误')
    }

    if (status.status === 'error') {
      const errorMsg = status.error || '下载失败，请稍后重试'
      console.log('[DOWNLOAD] 检测到错误状态:', errorMsg)
      downloading.value = false
      shouldContinuePolling = false
      // 直接提示，不抛出！
      ElMessage.error(errorMsg)
      return
    }

    if (status.status === 'completed') {
      shouldContinuePolling = false

      const fileResponse = await fetch(`/api/proxy/download/file/${downloadTaskId.value}`)
      const blob = await fileResponse.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = status.filename
      link.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('下载完成！')
      downloading.value = false
      downloadProgress.value = 100

      auth.refreshQuota()
    } else {
      const newProgress = status.progress || 0
      if (newProgress > 0) {
        downloadProgress.value = newProgress
      }
      if (shouldContinuePolling) {
        setTimeout(pollStatus, 1000)
      }
    }
  } catch (err) {
    console.error('[DOWNLOAD] 下载状态轮询错误:', err)
    shouldContinuePolling = false
    downloading.value = false
    // 直接提示，不抛出！
    ElMessage.error(err.message || '下载异常，请稍后重试')
  }
}

    pollStatus()
  } catch (err) {
    // 友好的错误提示
    const errorMsg = err.message || '下载失败，请稍后重试'
    ElMessage.error({
      message: errorMsg,
      duration: 5000,
      showClose: true
    })

    // 重置所有状态
    downloading.value = false
    downloadProgress.value = 0
    downloadTaskId.value = null
  }
}

// AI问答功能 - 使用流式接口
const sendAIChat = async () => {
  if (!aiChatQuestion.value.trim() || aiChatLoading.value) return

  const question = aiChatQuestion.value.trim()
  aiChatMessages.value.push({ role: 'user', content: question })
  aiChatQuestion.value = ''
  aiChatLoading.value = true

  // 添加一个临时的助手消息用于流式输出
  const assistantMessageIndex = aiChatMessages.value.length
  aiChatMessages.value.push({ role: 'assistant', content: '' })

  try {
    // 如果已有字幕文本，直接传递给后端
    const subtitleText = aiSubtitles.value.length > 0
      ? aiSubtitles.value.map(sub => sub.text).join('\n')
      : null

    const response = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: originalUrl.value,
        question,
        subtitle_text: subtitleText,  // 新增：传递已有字幕
        video_info: {
          title: videoData.value?.title || '',
          description: videoData.value?.description || ''
        },
        chat_history: aiChatMessages.value.slice(0, -2).map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    // 读取SSE流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentEventType = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEventType = line.slice(7).trim()
          continue
        }

        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (currentEventType === 'content' && data.content) {
              // 流式追加内容
              aiChatMessages.value[assistantMessageIndex].content += data.content
            }
            else if (currentEventType === 'complete') {
              // 完成
              aiChatLoading.value = false
            }
            else if (currentEventType === 'error') {
              throw new Error(data.message || 'AI回答失败')
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e, line)
          }
        }
      }
    }

  } catch (err) {
    console.error('AI问答失败:', err)
    ElMessage.error(err.message || 'AI回答失败')
    // 秠除失败的回答
    if (aiChatMessages.value[assistantMessageIndex].content === '') {
      aiChatMessages.value.splice(assistantMessageIndex, 1)
    }
  } finally {
    aiChatLoading.value = false
  }
}
</script>

<style scoped>
/* 导航链接样式 */
.nav-link {
  position: relative;
  padding-bottom: 6px;
  transition: all 0.2s ease;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(to right, #3b82f6, #8b5cf6);
  transition: width 0.2s ease;
}

.nav-link:hover::after {
  width: 100%;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.btn-gradient-ai {
  @apply bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium px-6 py-3 rounded-xl hover:from-purple-600 hover:to-pink-600 active:from-purple-700 active:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg;
}

.btn-gradient-vip {
  @apply bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium px-6 py-3 rounded-xl hover:from-purple-600 hover:to-pink-600 active:from-purple-700 active:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg;
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

/* 质量卡片样式 */
.quality-card {
  border: 1px solid #e5e7eb;
  background: white;
  transition: all 0.2s ease;
}

.quality-card-default {
  @apply quality-card;
  color: #4b5563;
}

.quality-card-default:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
}

.quality-card-selected {
  @apply quality-card;
  background-color: #eff6ff;
  border-color: #1890ff;
  color: #1890ff;
  box-shadow: 0 0 0 1px #1890ff;
}

.quality-card-selected:hover {
  background-color: #dbeafe;
}

/* 格式化总结样式 */
.formatted-summary {
  line-height: 1.8;
}

.formatted-summary ::v-deep([class*="【"]) {
  font-weight: bold;
  color: #111827;
  font-size: 1rem;
  display: block;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

/* 思维导图样式 */
.mindmap-content {
  font-family: 'Courier New', monospace;
  line-height: 1.6;
}

.mindmap-content h1 {
  font-size: 1.25rem;
  font-weight: bold;
  color: #111827;
  margin-bottom: 1rem;
}

.mindmap-content h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.mindmap-content ul {
  list-style: disc;
  padding-left: 1.5rem;
  margin: 0.5rem 0;
}

.mindmap-content li {
  margin: 0.25rem 0;
}

.mindmap-content p {
  margin: 0.5rem 0;
}

/* 交互式思维导图样式 */
.mindmap-canvas {
  position: relative;
  width: 100%;
  display: block;
}

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
