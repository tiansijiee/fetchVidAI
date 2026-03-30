/**
 * SEO 工具类
 * 动态管理页面的 TDK（Title、Description、Keywords）
 */
import { useI18n } from 'vue-i18n'

/**
 * SEO 路由配置
 * 为每个路由定义独立的 TDK
 */
export const SEO_ROUTES = {
  // 首页/视频下载页
  '/': {
    zh: {
      titleKey: 'home.title',
      descKey: 'home.description',
      keywordsKey: 'home.keywords'
    },
    en: {
      titleKey: 'home.title',
      descKey: 'home.description',
      keywordsKey: 'home.keywords'
    }
  },
  '/download': {
    zh: {
      titleKey: 'home.title',
      descKey: 'home.description',
      keywordsKey: 'home.keywords'
    },
    en: {
      titleKey: 'home.title',
      descKey: 'home.description',
      keywordsKey: 'home.keywords'
    }
  },
  // AI总结页
  '/summarize': {
    zh: {
      titleKey: 'aiSummary.title',
      descKey: 'aiSummary.description',
      keywordsKey: 'aiSummary.keywords'
    },
    en: {
      titleKey: 'aiSummary.title',
      descKey: 'aiSummary.description',
      keywordsKey: 'aiSummary.keywords'
    }
  },
  // 价格页
  '/pricing': {
    zh: {
      titleKey: 'pricing.title',
      descKey: 'pricing.description',
      keywordsKey: 'pricing.keywords'
    },
    en: {
      titleKey: 'pricing.title',
      descKey: 'pricing.description',
      keywordsKey: 'pricing.keywords'
    }
  },
  // 功能页
  '/features': {
    zh: {
      titleKey: 'features.title',
      descKey: 'features.description',
      keywordsKey: 'features.keywords'
    },
    en: {
      titleKey: 'features.title',
      descKey: 'features.description',
      keywordsKey: 'features.keywords'
    }
  },
  // 教程页
  '/tutorial': {
    zh: {
      titleKey: 'tutorial.title',
      descKey: 'tutorial.description',
      keywordsKey: 'tutorial.keywords'
    },
    en: {
      titleKey: 'tutorial.title',
      descKey: 'tutorial.description',
      keywordsKey: 'tutorial.keywords'
    }
  },
  // 平台落地页 - B站
  '/bilibili': {
    zh: {
      titleKey: 'platformBilibili.title',
      descKey: 'platformBilibili.description',
      keywordsKey: 'platformBilibili.keywords'
    },
    en: {
      titleKey: 'platformBilibili.title',
      descKey: 'platformBilibili.description',
      keywordsKey: 'platformBilibili.keywords'
    }
  },
  // 平台落地页 - YouTube
  '/youtube': {
    zh: {
      titleKey: 'platformYoutube.title',
      descKey: 'platformYoutube.description',
      keywordsKey: 'platformYoutube.keywords'
    },
    en: {
      titleKey: 'platformYoutube.title',
      descKey: 'platformYoutube.description',
      keywordsKey: 'platformYoutube.keywords'
    }
  },
  // 平台落地页 - 抖音
  '/douyin': {
    zh: {
      titleKey: 'platformDouyin.title',
      descKey: 'platformDouyin.description',
      keywordsKey: 'platformDouyin.keywords'
    },
    en: {
      titleKey: 'platformDouyin.title',
      descKey: 'platformDouyin.description',
      keywordsKey: 'platformDouyin.keywords'
    }
  }
}

/**
 * 根据语言键获取嵌套的翻译值
 * 例如：'home.title' => t('home.title')
 */
const getNestedTranslation = (t, key) => {
  if (!key) return ''
  return t(key)
}

/**
 * 更新页面 SEO 信息
 * @param {string} path - 路由路径
 * @param {string} locale - 语言（zh/en）
 */
export const updateSEO = (path, locale = 'zh') => {
  const routeConfig = SEO_ROUTES[path] || SEO_ROUTES['/']
  const localeConfig = routeConfig[locale] || routeConfig['zh']

  // 创建临时的 t 函数来获取翻译
  // 注意：这里需要从 i18n 实例获取翻译，但由于是工具函数，我们需要传入 t 函数
  // 所以这个函数会在组件内调用，传入 t 函数

  return localeConfig
}

/**
 * 在组件内更新 SEO 的 Composable
 * 使用方式：在组件 setup 中调用 useSEO()
 */
export const useSEO = () => {
  const { t, locale } = useI18n()
  const route = window.location.pathname

  const updatePageSEO = (path = route) => {
    const routeConfig = SEO_ROUTES[path] || SEO_ROUTES['/']
    const localeConfig = routeConfig[locale.value] || routeConfig['zh']

    // 获取翻译内容
    const title = getNestedTranslation(t, localeConfig.titleKey)
    const description = getNestedTranslation(t, localeConfig.descKey)
    const keywords = getNestedTranslation(t, localeConfig.keywordsKey)

    // 更新 document.title
    document.title = title

    // 更新 meta 标签
    updateMetaTag('description', description)
    updateMetaTag('keywords', keywords)

    // 更新 Open Graph 标签（社交媒体分享）
    updateMetaTag('og:title', title, 'property')
    updateMetaTag('og:description', description, 'property')
    updateMetaTag('og:type', 'website', 'property')

    // 更新 Twitter Card 标签
    updateMetaTag('twitter:card', 'summary_large_image')
    updateMetaTag('twitter:title', title)
    updateMetaTag('twitter:description', description)
  }

  return {
    updatePageSEO
  }
}

/**
 * 更新或创建 meta 标签
 * @param {string} name - meta 标签的 name 或 property 属性
 * @param {string} content - meta 标签的内容
 * @param {string} attrType - 使用 name 还是 property 属性
 */
const updateMetaTag = (name, content, attrType = 'name') => {
  let meta = document.querySelector(`meta[${attrType}="${name}"]`)

  if (!meta) {
    meta = document.createElement('meta')
    meta.setAttribute(attrType, name)
    document.head.appendChild(meta)
  }

  meta.setAttribute('content', content)
}

/**
 * 添加结构化数据（JSON-LD）
 * @param {Object} data - 结构化数据对象
 */
export const addStructuredData = (data) => {
  // 移除旧的结构化数据
  const oldScript = document.getElementById('structured-data')
  if (oldScript) {
    oldScript.remove()
  }

  // 创建新的结构化数据
  const script = document.createElement('script')
  script.id = 'structured-data'
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(data)
  document.head.appendChild(script)
}

/**
 * 生成软件应用的结构化数据
 */
export const generateSoftwareSchema = (locale = 'zh') => {
  const isZh = locale === 'zh'
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    'name': isZh ? 'FetchVid 万能视频下载器' : 'FetchVid Universal Video Downloader',
    'operatingSystem': 'Web',
    'applicationCategory': 'MultimediaApplication',
    'offers': {
      '@type': 'Offer',
      'price': isZh ? '¥29' : '$4.29',
      'priceCurrency': isZh ? 'CNY' : 'USD'
    },
    'aggregateRating': {
      '@type': 'AggregateRating',
      'ratingValue': '4.8',
      'ratingCount': '1000+'
    },
    'description': isZh
      ? 'FetchVid是专业的万能视频下载器，支持100+视频平台，一键下载高清视频，AI智能提取字幕、生成总结和思维导图。'
      : 'FetchVid is a professional universal video downloader supporting 100+ platforms. One-click HD video download, AI subtitle extraction, summary generation, and mind maps.'
  }
}

/**
 * 生成网站组织的结构化数据
 */
export const generateOrganizationSchema = (locale = 'zh') => {
  const isZh = locale === 'zh'
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    'name': 'FetchVid',
    'url': 'https://fetchvid.com',
    'logo': 'https://fetchvid.com/logo.png',
    'description': isZh
      ? 'FetchVid是专业的万能视频下载器，支持100+视频平台'
      : 'FetchVid is a professional universal video downloader supporting 100+ platforms',
    'contactPoint': {
      '@type': 'ContactPoint',
      'contactType': 'customer service',
      'email': 'support@fetchvid.com'
    }
  }
}

/**
 * 生成面包屑导航的结构化数据
 */
export const generateBreadcrumbSchema = (breadcrumbs) => {
  const itemList = breadcrumbs.map((item, index) => ({
    '@type': 'ListItem',
    'position': index + 1,
    'name': item.name,
    'item': `https://fetchvid.com${item.path}`
  }))

  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    'itemListElement': itemList
  }
}

/**
 * 设置规范链接（Canonical URL）
 * 用于告诉搜索引擎这是页面的规范版本，避免重复内容
 * @param {string} url - 规范 URL
 */
export const setCanonicalUrl = (url) => {
  let link = document.querySelector('link[rel="canonical"]')

  if (!link) {
    link = document.createElement('link')
    link.rel = 'canonical'
    document.head.appendChild(link)
  }

  link.href = url
}

/**
 * 设置 hreflang 标签
 * 用于告诉搜索引擎不同语言版本的页面
 * @param {string} locale - 语言代码
 * @param {string} url - 页面 URL
 */
export const setHrefLang = (locale, url) => {
  let link = document.querySelector(`link[rel="alternate"][hreflang="${locale}"]`)

  if (!link) {
    link = document.createElement('link')
    link.rel = 'alternate'
    link.hreflang = locale
    document.head.appendChild(link)
  }

  link.href = url

  // 设置 x-default（指向默认语言版本）
  if (locale === 'zh') {
    let defaultLink = document.querySelector('link[rel="alternate"][hreflang="x-default"]')
    if (!defaultLink) {
      defaultLink = document.createElement('link')
      defaultLink.rel = 'alternate'
      defaultLink.hreflang = 'x-default'
      document.head.appendChild(defaultLink)
    }
    defaultLink.href = url
  }
}
