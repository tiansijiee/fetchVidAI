/**
 * Vue Router 配置
 * 新增路由系统，支持多页面 + SEO 优化
 */
import { createRouter, createWebHistory } from 'vue-router'

// 页面组件（懒加载）
const VideoDownload = () => import('../views/VideoDownload.vue')
const VideoSummarize = () => import('../views/VideoSummarize.vue')
const TestView = () => import('../views/TestView.vue')
const Login = () => import('../views/Login.vue')
const Upgrade = () => import('../views/Upgrade.vue')
const Pricing = () => import('../views/Pricing.vue')
const Features = () => import('../views/Features.vue')
const Tutorial = () => import('../views/Tutorial.vue')

// 平台落地页组件（SEO 优化）
const PlatformBilibili = () => import('../views/PlatformBilibili.vue')
const PlatformYoutube = () => import('../views/PlatformYoutube.vue')
const PlatformDouyin = () => import('../views/PlatformDouyin.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: VideoDownload,
    meta: {
      title: '万能视频下载器 - 一键下载任意视频 + AI智能总结',
      description: 'FetchVid是专业的万能视频下载器，支持100+视频平台。一键下载高清视频，AI智能提取字幕、生成总结和思维导图。无水印、多格式、高速下载。'
    }
  },
  {
    path: '/download',
    name: 'download',
    component: VideoDownload,
    meta: {
      title: '万能视频下载器 - 一键下载任意视频 + AI智能总结',
      description: 'FetchVid是专业的万能视频下载器，支持100+视频平台。一键下载高清视频，AI智能提取字幕、生成总结和思维导图。无水印、多格式、高速下载。'
    }
  },
  {
    path: '/pricing',
    name: 'pricing',
    component: Pricing,
    meta: {
      title: '套餐价格 - 解锁无限视频下载和AI功能 | FetchVid',
      description: 'FetchVid会员套餐，解锁无限视频下载、AI智能总结、字幕提取等全部功能。月度会员¥29/月，年度会员¥288/年，超值划算。'
    }
  },
  {
    path: '/features',
    name: 'features',
    component: Features,
    meta: {
      title: '功能特性 - 全方位满足您的视频处理需求 | FetchVid',
      description: 'FetchVid提供视频下载、AI智能总结、AI问答、思维导图、字幕提取、弹幕下载等全方位视频处理功能。'
    }
  },
  {
    path: '/tutorial',
    name: 'tutorial',
    component: Tutorial,
    meta: {
      title: '使用教程 - 如何下载视频和AI总结 | FetchVid',
      description: 'FetchVid使用教程，详细介绍如何下载B站、YouTube、抖音等平台视频，以及如何使用AI总结、字幕提取等功能。'
    }
  },
  {
    path: '/summarize',
    name: 'summarize',
    component: VideoSummarize,
    meta: {
      title: 'AI视频总结 - 智能提取视频要点生成思维导图 | FetchVid',
      description: 'FetchVid AI视频总结功能，自动提取视频核心内容，生成结构化摘要和思维导图。支持长视频总结，多语言视频智能分析。'
    }
  },
  // 平台落地页（SEO 优化 - 针对长尾关键词）
  {
    path: '/bilibili',
    name: 'bilibili',
    component: PlatformBilibili,
    meta: {
      title: 'B站视频下载器 - 无水印下载B站高清视频 | FetchVid',
      description: '专业的B站视频下载工具，支持无水印下载B站1080P/4K高清视频。一键提取B站字幕、弹幕，AI智能生成视频总结和思维导图。免费试用，高速稳定。'
    }
  },
  {
    path: '/youtube',
    name: 'youtube',
    component: PlatformYoutube,
    meta: {
      title: 'YouTube视频下载器 - 一键下载YouTube高清视频 | FetchVid',
      description: '专业的YouTube视频下载工具，支持下载YouTube 4K/8K高清视频。一键提取字幕，AI智能生成视频总结。免费试用，无地域限制。'
    }
  },
  {
    path: '/douyin',
    name: 'douyin',
    component: PlatformDouyin,
    meta: {
      title: '抖音视频下载器 - 无水印下载抖音短视频 | FetchVid',
      description: '专业的抖音视频下载工具，支持无水印下载抖音短视频。一键保存高清视频，AI智能提取字幕和总结。免费试用，批量下载。'
    }
  },
  {
    path: '/test',
    name: 'test',
    component: TestView
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/upgrade',
    name: 'upgrade',
    component: Upgrade
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // SEO 优化：滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

export default router
