/**
 * 自定义指令集合
 */

import lazyLoad from './lazyLoad'

export default {
  install(app) {
    // 注册懒加载指令
    app.directive('lazy', lazyLoad)
  }
}
