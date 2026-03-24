<template>
  <router-view />
</template>

<script setup>
// 主应用组件 - 使用路由系统
</script>

<style>
/* 全局样式 */
:root {
  --primary-500: #8b5cf6;
  --accent-500: #ec4899;
}

.gradient-text {
  @apply bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent;
}

.glass-card {
  @apply bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-sm;
}

.btn-primary {
  @apply bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-gradient {
  @apply bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed;
}

.input-field {
  @apply w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all;
}

.platform-badge {
  @apply px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:border-purple-300 transition-colors;
}

.nav-link {
  @apply text-gray-600 hover:text-purple-600 font-medium transition-colors cursor-pointer;
}

.progress-bar {
  @apply bg-gradient-to-r from-purple-500 to-pink-500;
}

.format-card {
  @apply relative p-4 border-2 border-gray-200 rounded-xl cursor-pointer hover:border-purple-300 transition-all;
}

.format-card.selected {
  @apply border-purple-500 bg-purple-50;
}
</style>