/**
 * Vue I18n Configuration
 * 多语言配置文件
 */
import { createI18n } from 'vue-i18n'
import zh from './locales/zh'
import en from './locales/en'

// 默认语言：根据浏览器语言自动检测
const getDefaultLocale = () => {
  const browserLang = navigator.language || navigator.userLanguage
  // 如果是中文环境，使用简体中文，否则使用英文
  return browserLang.startsWith('zh') ? 'zh' : 'en'
}

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: getDefaultLocale(),
  fallbackLocale: 'en', // 回退语言
  messages: {
    zh,
    en
  },
  // SEO 优化：确保搜索引擎能识别不同语言版本
  seo: true
})

export default i18n

// 导出切换语言的函数
export const setLocale = (locale) => {
  i18n.global.locale.value = locale
  // 保存到 localStorage
  localStorage.setItem('fetchvid_locale', locale)
  // 更新 HTML lang 属性（SEO 优化）
  document.documentElement.lang = locale
}

// 导出获取当前语言的函数
export const getLocale = () => {
  return i18n.global.locale.value
}

// 初始化语言设置（从 localStorage 读取）
export const initLocale = () => {
  const savedLocale = localStorage.getItem('fetchvid_locale')
  if (savedLocale && (savedLocale === 'zh' || savedLocale === 'en')) {
    setLocale(savedLocale)
  } else {
    // 使用浏览器默认语言
    const defaultLocale = getDefaultLocale()
    setLocale(defaultLocale)
  }
}
