import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
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

// 将认证模块挂载到全局
app.config.globalProperties.$auth = auth

app.mount('#app')
