<template>
  <div class="min-h-screen bg-gray-50">

    <div class="relative z-10">
      <!-- 顶部导航 -->
      <header class="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
              </div>
              <span class="text-xl font-bold gradient-text">FetchVid</span>
            </div>
            <nav class="flex items-center gap-3">
              <span class="hidden sm:inline-flex platform-badge">
                <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                支持8大平台
              </span>
              <!-- 用户等级 -->
              <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg">
                <span class="text-amber-600">👑</span>
                <span class="text-sm font-medium text-amber-700">免费版</span>
              </div>
              <button class="sm:hidden px-3 py-1.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-sm font-medium rounded-lg">
                升级
              </button>
            </nav>
          </div>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <!-- 标题区 -->
        <div class="text-center mb-10">
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4">
            <span class="gradient-text">万能视频下载</span>
          </h1>
          <p class="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
            支持B站、微博、知乎等8大平台，多分辨率选择
          </p>

          <!-- 使用量显示 -->
          <div class="mt-6 inline-flex items-center gap-3 px-4 py-2 bg-white border border-gray-200 rounded-xl">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
              </svg>
              <span class="text-sm text-gray-600">今日已用 <span class="font-semibold text-gray-900">2/5</span> 次</span>
            </div>
            <div class="w-px h-4 bg-gray-200"></div>
            <button class="text-sm font-medium text-primary-600 hover:text-primary-700">升级会员 →</button>
          </div>
        </div>

        <!-- 输入卡片 -->
        <div class="glass-card p-6 sm:p-8 mb-8">
          <div class="space-y-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              <span class="flex items-center gap-2">
                <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                </svg>
                粘贴视频链接
              </span>
            </label>
            <div class="flex flex-col sm:flex-row gap-3">
              <input
                v-model="videoUrl"
                type="text"
                placeholder="支持 B站/微博/知乎/YouTube 等平台链接"
                class="input-field flex-1"
                @keyup.enter="parseVideo"
                :disabled="loading"
              >
              <button
                @click="parseVideo"
                :disabled="!videoUrl.trim() || loading"
                class="btn-primary whitespace-nowrap flex items-center justify-center gap-2"
                :class="{ 'opacity-50 cursor-not-allowed': !videoUrl.trim() || loading }"
              >
                <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
                <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ loading ? '解析中...' : '解析视频' }}</span>
              </button>
            </div>

            <!-- 错误提示 -->
            <div v-if="error" class="p-4 rounded-2xl bg-red-50 border border-red-200 flex items-start gap-3">
              <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span class="text-red-700 text-sm">{{ error }}</span>
            </div>

            <!-- 支持的平台 -->
            <div class="flex flex-wrap items-center gap-2 pt-2">
              <span class="text-sm text-gray-500">支持：</span>
              <span
                v-for="platform in platforms"
                :key="platform.id"
                @click="fillExample(platform.example)"
                class="platform-badge text-xs"
                :class="{ 'opacity-50 cursor-not-allowed': platform.disabled }"
                :style="!platform.disabled ? 'cursor: pointer' : ''"
              >
                <span v-if="platform.icon" v-html="platform.icon"></span>
                {{ platform.name }}
                <span v-if="platform.disabled" class="text-xs text-gray-400 ml-1">(即将支持)</span>
              </span>
            </div>
          </div>
        </div>

        <!-- 视频信息卡片 -->
        <div v-if="videoData" class="glass-card p-6 sm:p-8 mb-8">
          <!-- 视频信息 -->
          <div class="flex flex-col sm:flex-row gap-6 mb-8">
            <div class="relative flex-shrink-0 mx-auto sm:mx-0">
              <div class="relative group">
                <img
                  :src="getThumbnailUrl(videoData.thumbnail)"
                  :alt="videoData.title"
                  class="w-full sm:w-64 h-40 object-cover rounded-xl"
                  @error="$event.target.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22256%22 height=%22160%22%3E%3Crect fill=%22%23f3f4f6%22 width=%22256%22 height=%22160%22/%3E%3Ctext fill=%22%239ca3af%22 font-size=%2214%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22%3E无封面%3C/text%3E%3C/svg%3E'"
                >
                <div class="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded-lg">
                  {{ videoData.duration }}
                </div>
              </div>
            </div>

            <div class="flex-1 min-w-0">
              <h3 class="text-xl sm:text-2xl font-bold text-gray-900 mb-3 line-clamp-2">{{ videoData.title }}</h3>
              <div class="space-y-2 text-sm text-gray-600">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                  <span>{{ videoData.uploader || '未知UP主' }}</span>
                </div>
                <div v-if="videoData.view_count" class="flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                  <span>{{ formatViewCount(videoData.view_count) }} 次观看</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 分辨率选择 -->
          <div class="mb-8">
            <h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              选择画质
              <span class="ml-2 text-xs font-normal text-gray-500">1080P及以上需要会员</span>
            </h4>

            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              <div
                v-for="format in videoData.formats"
                :key="format.format_id"
                @click="selectedFormat = format.format_id"
                class="format-card"
                :class="{ 'selected': selectedFormat === format.format_id, 'recommended': format.recommended }"
              >
                <div v-if="format.recommended" class="absolute -top-2 -right-2 bg-accent-500 text-white text-xs px-2 py-1 rounded-full">
                  推荐
                </div>
                <div class="text-center">
                  <div class="text-lg font-bold text-gray-900 mb-1">
                    {{ format.quality }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ format.ext?.toUpperCase() || 'MP4' }}
                  </div>
                  <div v-if="format.size_formatted" class="text-xs text-gray-400 mt-1">
                    {{ format.size_formatted }}
                  </div>
                  <div v-if="format.recommended" class="text-xs text-primary-600 font-medium mt-2">
                    含音频
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 下载按钮 -->
          <div class="flex flex-col sm:flex-row gap-3">
            <button
              @click="downloadVideo"
              :disabled="downloading || !selectedFormat"
              class="btn-primary flex-1 flex items-center justify-center gap-2 text-base"
              :class="{ 'opacity-50 cursor-not-allowed': downloading || !selectedFormat }"
            >
              <svg v-if="!downloading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
              <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ downloading ? `下载中 ${downloadProgress}%` : '开始下载' }}</span>
            </button>
          </div>

          <!-- 下载进度 -->
          <div v-if="downloading && downloadProgress > 0" class="mt-6">
            <div class="relative h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="absolute inset-y-0 left-0 progress-bar rounded-full transition-all duration-300"
                :style="{ width: downloadProgress + '%' }"
              ></div>
            </div>
            <p class="text-center text-sm text-gray-600 mt-2">
              下载进度: {{ downloadProgress }}%
            </p>
          </div>
        </div>

        <!-- 功能特点 -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div class="glass-card p-6 text-center">
            <div class="w-14 h-14 bg-primary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <h3 class="font-bold text-gray-900 mb-2">极速解析</h3>
            <p class="text-sm text-gray-600">秒级响应，即时获取视频信息</p>
          </div>
          <div class="glass-card p-6 text-center">
            <div class="w-14 h-14 bg-accent-500 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
            </div>
            <h3 class="font-bold text-gray-900 mb-2">多画质选择</h3>
            <p class="text-sm text-gray-600">支持360P-1080P多种分辨率</p>
          </div>
          <div class="glass-card p-6 text-center">
            <div class="w-14 h-14 bg-accent-500 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <h3 class="font-bold text-gray-900 mb-2">安全可靠</h3>
            <p class="text-sm text-gray-600">本地下载，保护隐私安全</p>
          </div>
        </div>

        <!-- 价格方案 -->
        <div class="mb-8">
          <h2 class="text-2xl sm:text-3xl font-bold text-center text-gray-900 mb-8">
            选择适合您的方案
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <!-- 免费版 -->
            <div class="glass-card p-6">
              <div class="text-center">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">免费版</h3>
                <div class="mb-4">
                  <span class="text-4xl font-bold text-gray-900">¥0</span>
                  <span class="text-gray-500">/永久</span>
                </div>
                <p class="text-sm text-gray-500 mb-6">适合轻度使用</p>
              </div>
              <ul class="space-y-3 mb-6">
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  每日5次下载
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  最高720P画质
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  基础下载速度
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-400">
                  <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  无批量下载
                </li>
              </ul>
              <button class="w-full py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors">
                当前方案
              </button>
            </div>

            <!-- 月度会员 -->
            <div class="glass-card p-6 relative border-2 border-primary-500">
              <div class="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-medium rounded-full">
                最受欢迎
              </div>
              <div class="text-center">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">月度会员</h3>
                <div class="mb-4">
                  <span class="text-4xl font-bold text-gray-900">¥19.9</span>
                  <span class="text-gray-500">/月</span>
                </div>
                <p class="text-sm text-gray-500 mb-6">适合频繁下载</p>
              </div>
              <ul class="space-y-3 mb-6">
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  每日100次下载
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  最高1080P画质
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  加速下载
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  批量下载(10个)
                </li>
              </ul>
              <button class="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-medium hover:opacity-90 transition-opacity">
                立即开通
              </button>
            </div>

            <!-- 年度会员 -->
            <div class="glass-card p-6">
              <div class="text-center">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">年度会员</h3>
                <div class="mb-4">
                  <span class="text-4xl font-bold text-gray-900">¥99</span>
                  <span class="text-gray-500">/年</span>
                  <span class="ml-2 text-xs text-green-600 font-medium">省58%</span>
                </div>
                <p class="text-sm text-gray-500 mb-6">超值首选</p>
              </div>
              <ul class="space-y-3 mb-6">
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  无限次下载
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  最高4K超清
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  极速下载
                </li>
                <li class="flex items-center gap-2 text-sm text-gray-600">
                  <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  无限批量下载
                </li>
              </ul>
              <button class="w-full py-3 bg-primary-500 text-white rounded-xl font-medium hover:bg-primary-600 transition-colors">
                立即开通
              </button>
            </div>
          </div>
        </div>
      </main>

      <!-- 底部 -->
      <footer class="border-t border-gray-200 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p class="text-center text-sm text-gray-600">
            © 2024 FetchVid · 仅供学习交流使用
          </p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const videoUrl = ref('')
const loading = ref(false)
const error = ref('')
const videoData = ref(null)
const selectedFormat = ref('')
const downloading = ref(false)
const downloadProgress = ref(0)
const originalUrl = ref('')
const downloadTaskId = ref(null)

// 平台配置
const platforms = [
  {
    id: 'bilibili',
    name: 'B站',
    icon: '📺',
    example: 'https://www.bilibili.com/video/BV1xx411c7mu',
    disabled: false
  },
  {
    id: 'weibo',
    name: '微博',
    icon: '🌭',
    example: 'https://weibo.com/tv/show/123456',
    disabled: false
  },
  {
    id: 'zhihu',
    name: '知乎',
    icon: '🧠',
    example: 'https://www.zhihu.com/question/123456',
    disabled: false
  },
  {
    id: 'youtube',
    name: 'YouTube',
    icon: '▶️',
    example: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    disabled: false
  },
  {
    id: 'twitter',
    name: 'Twitter',
    icon: '🐦',
    example: 'https://twitter.com/user/status/123456',
    disabled: false
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: '🎵',
    example: 'https://www.tiktok.com/@user/video/123456',
    disabled: false
  },
  {
    id: 'instagram',
    name: 'Instagram',
    icon: '📷',
    example: 'https://instagram.com/p/ABC123/',
    disabled: false
  },
  {
    id: 'vimeo',
    name: 'Vimeo',
    icon: '🎬',
    example: 'https://vimeo.com/123456',
    disabled: false
  }
]

// 获取缩略图URL
const getThumbnailUrl = (url) => {
  if (!url) return ''
  return `/api/proxy/thumbnail?url=${encodeURIComponent(url)}`
}

// 格式化观看次数
const formatViewCount = (count) => {
  if (!count) return '0'
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toLocaleString()
}

// 填充示例链接
const fillExample = (url) => {
  videoUrl.value = url
  error.value = ''
}

// 解析视频
const parseVideo = async () => {
  const url = videoUrl.value.trim()
  if (!url) {
    error.value = '请输入视频链接'
    return
  }

  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    error.value = '请输入有效的链接（需以 http:// 或 https:// 开头）'
    return
  }

  loading.value = true
  error.value = ''
  videoData.value = null

  try {
    const response = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })

    const result = await response.json()

    if (result.success) {
      videoData.value = result.data
      originalUrl.value = url
      // 默认选择推荐格式或最高画质
      if (result.data.formats && result.data.formats.length > 0) {
        const recommended = result.data.formats.find(f => f.recommended)
        selectedFormat.value = recommended ? recommended.format_id : result.data.formats[0].format_id
      }
      ElMessage.success('解析成功！')
    } else {
      error.value = result.message || '解析失败，请检查链接是否正确'
      ElMessage.error(result.message)
    }
  } catch (err) {
    console.error('解析错误:', err)
    error.value = '网络错误，请确保后端服务已启动'
    ElMessage.error('网络错误，请确保后端服务已启动')
  } finally {
    loading.value = false
  }
}

// 下载视频
const downloadVideo = async () => {
  if (!selectedFormat.value) {
    ElMessage.warning('请先选择画质')
    return
  }

  downloading.value = true
  downloadProgress.value = 0

  try {
    ElMessage.info('开始下载，请稍候...')

    // 启动下载任务（传递选择的格式ID）
    const startResponse = await fetch('/api/proxy/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video_url: originalUrl.value,
        filename: videoData.value.title,
        format_id: selectedFormat.value
      })
    })

    if (!startResponse.ok) {
      throw new Error('启动下载失败')
    }

    const startData = await startResponse.json()
    if (!startData.success) {
      throw new Error(startData.message || '启动下载失败')
    }

    downloadTaskId.value = startData.task_id

    // 轮询下载状态
    const pollStatus = async () => {
      try {
        const statusResponse = await fetch(`/api/proxy/download/status/${downloadTaskId.value}`)
        if (!statusResponse.ok) {
          throw new Error('获取下载状态失败')
        }

        const status = await statusResponse.json()

        if (status.status === 'completed') {
          downloadProgress.value = 100
          ElMessage.success('下载完成，正在保存文件...')

          // 下载文件
          const fileResponse = await fetch(`/api/proxy/download/file/${downloadTaskId.value}`)
          if (!fileResponse.ok) {
            throw new Error('获取文件失败')
          }

          const blob = await fileResponse.blob()
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = status.filename
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)

          ElMessage.success('下载完成！')
          downloading.value = false
          downloadTaskId.value = null

        } else if (status.status === 'error') {
          throw new Error(status.error || '下载失败')
        } else {
          downloadProgress.value = status.progress || 0
          setTimeout(pollStatus, 2000)
        }
      } catch (err) {
        throw err
      }
    }

    pollStatus()

  } catch (err) {
    console.error('下载错误:', err)
    ElMessage.error(err.message || '下载失败，请重试')
    downloading.value = false
    downloadTaskId.value = null
    downloadProgress.value = 0
  }
}
</script>
