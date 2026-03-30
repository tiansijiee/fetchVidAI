<template>
  <button
    @click="switchLanguage"
    class="language-switcher flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all text-sm font-medium shadow-sm hover:shadow-md"
    :title="currentLocale === 'zh' ? 'Switch to English' : '切换到简体中文'"
  >
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"></path>
    </svg>
    <span>{{ currentLocale === 'zh' ? 'EN' : '简中' }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { locale } = useI18n()
const router = useRouter()

const currentLocale = computed(() => locale.value)

const switchLanguage = () => {
  const newLocale = locale.value === 'zh' ? 'en' : 'zh'
  locale.value = newLocale
  localStorage.setItem('fetchvid_locale', newLocale)
  document.documentElement.lang = newLocale

  // 触发自定义事件，通知父组件更新 SEO
  window.dispatchEvent(new CustomEvent('language-changed', { detail: { locale: newLocale } }))
}
</script>

<style scoped>
.language-switcher {
  transition: all 0.2s ease;
}

.language-switcher:hover {
  transform: translateY(-1px);
}

.language-switcher:active {
  transform: translateY(0);
}
</style>
