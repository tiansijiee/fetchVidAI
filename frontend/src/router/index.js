/**
 * Vue Router 配置
 * 新增路由系统，支持多页面
 */
import { createRouter, createWebHistory } from 'vue-router'

// 页面组件（懒加载）
const VideoDownload = () => import('../views/VideoDownload.vue')
const VideoSummarize = () => import('../views/VideoSummarize.vue')
const TestView = () => import('../views/TestView.vue')
const Login = () => import('../views/Login.vue')
const Upgrade = () => import('../views/Upgrade.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: VideoDownload
  },
  {
    path: '/download',
    name: 'download',
    component: VideoDownload
  },
  {
    path: '/summarize',
    name: 'summarize',
    component: VideoSummarize
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
  routes
})

export default router
