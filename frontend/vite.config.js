import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
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
  }
})
