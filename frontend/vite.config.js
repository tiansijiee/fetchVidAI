import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('[Proxy]', req.method, req.url, '->', proxyReq.path)
          })
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('[Proxy Response]', proxyRes.statusCode, req.url)
          })
          proxy.on('error', (err, _req, _res) => {
            console.log('[Proxy Error]', err)
          })
          return proxy
        }
      }
    }
  },
  build: {
    // 生产环境优化
    minify: 'terser',
    terserOptions: {
      compress: {
        // 移除console.log
        drop_console: true,
        // 移除debugger
        drop_debugger: true
      }
    },
    // 分包优化
    rollupOptions: {
      output: {
        manualChunks: {
          // Vue核心
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          // UI组件库
          'ui-vendor': ['element-plus'],
          // 工具库
          'utils': ['axios', 'dayjs']
        }
      }
    },
    // 代码分割阈值
    chunkSizeWarningLimit: 1000
  }
})
