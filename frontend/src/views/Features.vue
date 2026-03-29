<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white font-sans">
    <!-- 导航栏 -->
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

          <!-- 导航入口 -->
          <nav class="hidden lg:flex items-center gap-8">
            <router-link to="/download" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">视频下载</router-link>
            <router-link to="/pricing" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">套餐价格</router-link>
            <router-link to="/features" class="nav-link text-base font-semibold text-blue-600">功能特性</router-link>
            <router-link to="/tutorial" class="nav-link text-base font-medium text-gray-600 hover:text-blue-600 transition-colors">使用教程</router-link>
          </nav>

          <!-- VIP入口 & 用户菜单 -->
          <div class="flex items-center gap-3">
            <button
              @click="handleUpgrade"
              class="hidden sm:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-xl font-medium transition-all duration-200 shadow-md shadow-purple-500/30 hover:shadow-lg hover:shadow-purple-500/40 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
              </svg>
              <span>开通VIP</span>
            </button>
            <UserMenu />
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
      <!-- 标题区域 -->
      <div class="text-center mb-12 lg:mb-16">
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
          <span class="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 bg-clip-text text-transparent">强大功能</span>
        </h1>
        <p class="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
          全方位满足您的视频处理需求
        </p>
      </div>

      <!-- 核心功能 -->
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8 mb-16">
        <!-- 视频下载 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-5 shadow-lg shadow-blue-500/30">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">视频下载</h3>
          <p class="text-gray-600 mb-4">支持100+视频平台，一键下载高清视频，支持多种格式选择</p>
          <ul class="space-y-2">
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              支持B站、YouTube、抖音等
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              最高8K高清下载
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              批量下载支持
            </li>
          </ul>
        </div>

        <!-- AI智能总结 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-5 shadow-lg shadow-purple-500/30">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">AI智能总结</h3>
          <p class="text-gray-600 mb-4">自动提取视频核心内容，生成结构化摘要，快速了解视频要点</p>
          <ul class="space-y-2">
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-purple-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              智能提取关键信息
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-purple-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              多语言视频支持
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-purple-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              支持长视频总结
            </li>
          </ul>
        </div>

        <!-- AI问答 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="w-14 h-14 bg-gradient-to-br from-pink-500 to-pink-600 rounded-2xl flex items-center justify-center mb-5 shadow-lg shadow-pink-500/30">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">AI智能问答</h3>
          <p class="text-gray-600 mb-4">基于视频内容的智能问答系统，快速获取视频中任何信息</p>
          <ul class="space-y-2">
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-pink-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              实时对话式问答
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-pink-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              精准定位视频内容
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-pink-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              多轮对话支持
            </li>
          </ul>
        </div>

        <!-- 思维导图 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-5 shadow-lg shadow-green-500/30">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">思维导图</h3>
          <p class="text-gray-600 mb-4">自动生成视频内容思维导图，可视化展示知识结构</p>
          <ul class="space-y-2">
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              自动生成导图
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              多种格式导出
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              可编辑可分享
            </li>
          </ul>
        </div>

        <!-- 字幕提取 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="w-14 h-14 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-2xl flex items-center justify-center mb-5 shadow-lg shadow-yellow-500/30">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">字幕提取</h3>
          <p class="text-gray-600 mb-4">一键提取视频字幕，支持多种字幕格式，便于学习和编辑</p>
          <ul class="space-y-2">
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-yellow-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              自动识别字幕
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-yellow-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              SRT/TXT格式导出
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-yellow-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              多语言字幕支持
            </li>
          </ul>
        </div>

        <!-- 弹幕下载 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 lg:p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="w-14 h-14 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl flex items-center justify-center mb-5 shadow-lg shadow-red-500/30">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">弹幕下载</h3>
          <p class="text-gray-600 mb-4">保存视频弹幕内容，了解观众互动和热门观点</p>
          <ul class="space-y-2">
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              完整弹幕保存
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              弹幕数据分析
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              支持B站弹幕
            </li>
          </ul>
        </div>
      </div>

      <!-- 平台支持 -->
      <div class="bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 rounded-3xl p-8 lg:p-12 shadow-2xl shadow-blue-500/30 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-purple-400/20 animate-pulse"></div>
        <div class="absolute -top-20 -right-20 w-40 h-40 bg-blue-400/30 rounded-full blur-3xl"></div>
        <div class="absolute -bottom-20 -left-20 w-40 h-40 bg-purple-400/30 rounded-full blur-3xl"></div>

        <div class="relative z-10">
          <h2 class="text-3xl font-bold text-white text-center mb-8">支持100+视频平台</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div class="flex flex-col items-center justify-center p-4 bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20 transition-colors">
              <span class="text-2xl mb-2">📺</span>
              <span class="text-white text-sm font-medium">Bilibili</span>
            </div>
            <div class="flex flex-col items-center justify-center p-4 bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20 transition-colors">
              <span class="text-2xl mb-2">▶️</span>
              <span class="text-white text-sm font-medium">YouTube</span>
            </div>
            <div class="flex flex-col items-center justify-center p-4 bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20 transition-colors">
              <span class="text-2xl mb-2">🎵</span>
              <span class="text-white text-sm font-medium">抖音</span>
            </div>
            <div class="flex flex-col items-center justify-center p-4 bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20 transition-colors">
              <span class="text-2xl mb-2">🎬</span>
              <span class="text-white text-sm font-medium">快手</span>
            </div>
            <div class="flex flex-col items-center justify-center p-4 bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20 transition-colors">
              <span class="text-2xl mb-2">🐦</span>
              <span class="text-white text-sm font-medium">Twitter</span>
            </div>
            <div class="flex flex-col items-center justify-center p-4 bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20 transition-colors">
              <span class="text-2xl mb-2">🌭</span>
              <span class="text-white text-sm font-medium">微博</span>
            </div>
          </div>
          <p class="text-center text-blue-100 mt-6 text-sm">以及更多平台...</p>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-200 mt-16 lg:mt-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center text-gray-500 text-sm">
          <p>&copy; 2024 FetchVid. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import UserMenu from '../components/UserMenu.vue'

const router = useRouter()

const handleUpgrade = () => {
  router.push('/upgrade')
}
</script>

<style scoped>
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
</style>
