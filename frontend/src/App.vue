<template>
  <router-view />
</template>

<script setup>
// 主应用组件 - 使用路由系统
</script>

<style>
/* ==========================================
   全局样式覆盖
   保持与设计系统一致
   ========================================== */

/* 全局链接样式 */
a {
  @apply transition-colors duration-150;
}

/* 全局焦点样式 */
*:focus-visible {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
}

/* 全局禁用状态 */
button:disabled,
[disabled] {
  @apply cursor-not-allowed opacity-50;
}

/* Element Plus 组件样式微调 */
.el-button {
  @apply font-medium rounded-xl;
}

.el-button--large {
  @apply px-6 py-4 text-base;
}

.el-button--default {
  @apply border-gray-200 text-gray-700 hover:border-gray-300 hover:text-gray-900;
}

/* 输入框样式 */
.el-input__wrapper {
  @apply rounded-xl border-gray-200 shadow-sm;
}

.el-input__wrapper:hover {
  @apply border-gray-300;
}

.el-input__wrapper.is-focus {
  @apply border-primary-500 ring-4 ring-primary-500/10 shadow-sm;
}

/* 单选按钮组样式 */
.el-radio-button__inner {
  @apply rounded-lg border-gray-200;
}

.el-radio-button__original-radio:checked + .el-radio-button__inner {
  @apply bg-primary-500 border-primary-500 text-white;
}

/* 卡片样式 */
.el-card {
  @apply rounded-2xl border-gray-200 shadow-sm;
}

.el-card__header {
  @apply border-gray-100;
}

/* 对话框样式 */
.el-dialog {
  @apply rounded-2xl;
}

.el-dialog__header {
  @apply border-gray-100;
}

/* 消息提示样式优化 */
.el-message {
  @apply rounded-xl shadow-lg;
}

/* 标签页样式 */
.el-tabs__item {
  @apply font-medium text-gray-600;
}

.el-tabs__item.is-active {
  @apply text-primary-600;
}

.el-tabs__active-bar {
  @apply bg-primary-500;
}
</style>
