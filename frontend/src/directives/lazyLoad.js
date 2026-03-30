/**
 * 图片懒加载指令
 * 使用 Intersection Observer API 实现图片懒加载
 *
 * 使用方法：
 * <img v-lazy="imageUrl" :alt="description">
 * <img v-lazy="{ src: imageUrl, placeholder: placeholderUrl }" :alt="description">
 */

const lazyLoad = {
  mounted(el, binding) {
    // 初始化加载状态
    el.classList.add('lazy-loading')

    // 处理绑定的值
    const loadImage = () => {
      const imageUrl = typeof binding.value === 'string'
        ? binding.value
        : binding.value.src

      const placeholder = typeof binding.value === 'object' && binding.value.placeholder
        ? binding.value.placeholder
        : 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3C/svg%3E'

      // 先设置占位图
      el.src = placeholder

      // 创建 Intersection Observer
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // 图片进入视口，开始加载
            const img = new Image()

            img.onload = () => {
              el.src = imageUrl
              el.classList.remove('lazy-loading')
              el.classList.add('lazy-loaded')
              observer.unobserve(el)
            }

            img.onerror = () => {
              el.classList.remove('lazy-loading')
              el.classList.add('lazy-error')
              observer.unobserve(el)
            }

            img.src = imageUrl

            // 添加淡入动画
            el.style.transition = 'opacity 0.3s ease-in-out'
            el.style.opacity = '0'
            setTimeout(() => {
              el.style.opacity = '1'
            }, 50)
          }
        })
      }, {
        rootMargin: '50px 0px', // 提前50px开始加载
        threshold: 0.01
      })

      observer.observe(el)

      // 保存 observer 引用以便后续清理
      el._lazyObserver = observer
    }

    // 如果浏览器支持 Intersection Observer，使用懒加载
    if ('IntersectionObserver' in window) {
      loadImage()
    } else {
      // 不支持则直接加载
      el.src = typeof binding.value === 'string'
        ? binding.value
        : binding.value.src
    }
  },

  unmounted(el) {
    // 清理 observer
    if (el._lazyObserver) {
      el._lazyObserver.disconnect()
    }
  }
}

export default lazyLoad
