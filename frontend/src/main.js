import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import i18n, { initLocale } from './i18n'
import directives from './directives'
import './style.css'

// 导入认证模块（必须在 axios 之前导入）
import auth from './auth/auth'

// 导入 Axios 配置（依赖 auth 模块）
import './auth/axios'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.use(i18n)
app.use(directives) // 注册自定义指令（图片懒加载等）

// 将认证模块挂载到全局
app.config.globalProperties.$auth = auth

// 初始化语言设置
initLocale()

app.mount('#app')
