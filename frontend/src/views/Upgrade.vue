<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-blue-100 p-4 py-8">
    <div class="max-w-6xl mx-auto">
      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">升级会员</h1>
        <p class="text-gray-600 mt-2">解锁无限使用权限和更多高级功能</p>
      </div>

      <!-- 套餐卡片 -->
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <!-- 月度会员 -->
        <div
          @click="selectPlan('monthly')"
          :class="[
            'bg-white rounded-2xl shadow-lg p-6 cursor-pointer transition-all border-2',
            selectedPlan === 'monthly' ? 'border-blue-500 shadow-xl' : 'border-transparent hover:shadow-lg'
          ]"
        >
          <div class="text-center">
            <h3 class="text-xl font-bold text-gray-800 mb-2">月度会员</h3>
            <div class="text-4xl font-bold text-blue-600 mb-4">¥29</div>
            <p class="text-gray-500 text-sm mb-6">30天有效期</p>

            <ul class="text-left space-y-3 mb-6">
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限视频下载
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限 AI 总结
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限 AI 问答
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                全格式思维导图导出
              </li>
            </ul>

            <button
              @click.stop="handleSubscribe('monthly')"
              :disabled="loading || selectedPlan !== 'monthly'"
              class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 font-medium"
            >
              {{ loading && selectedPlan === 'monthly' ? '处理中...' : '立即订阅' }}
            </button>
          </div>
        </div>

        <!-- 季度会员 - 推荐 -->
        <div
          @click="selectPlan('quarterly')"
          :class="[
            'bg-white rounded-2xl shadow-lg p-6 cursor-pointer transition-all border-2 relative',
            selectedPlan === 'quarterly' ? 'border-purple-500 shadow-xl' : 'border-transparent hover:shadow-lg'
          ]"
        >
          <div class="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <span class="bg-purple-500 text-white text-xs px-3 py-1 rounded-full font-medium">推荐</span>
          </div>

          <div class="text-center">
            <h3 class="text-xl font-bold text-gray-800 mb-2">季度会员</h3>
            <div class="text-4xl font-bold text-purple-600 mb-4">¥79</div>
            <p class="text-gray-500 text-sm mb-6">90天有效期 · 省¥8</p>

            <ul class="text-left space-y-3 mb-6">
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限视频下载
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限 AI 总结
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限 AI 问答
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                全格式 + 高清导出
              </li>
              <li class="flex items-center text-purple-600 font-medium">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                优先技术支持
              </li>
            </ul>

            <button
              @click.stop="handleSubscribe('quarterly')"
              :disabled="loading || selectedPlan !== 'quarterly'"
              class="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition disabled:opacity-50 font-medium"
            >
              {{ loading && selectedPlan === 'quarterly' ? '处理中...' : '立即订阅' }}
            </button>
          </div>
        </div>

        <!-- 年度会员 -->
        <div
          @click="selectPlan('yearly')"
          :class="[
            'bg-white rounded-2xl shadow-lg p-6 cursor-pointer transition-all border-2 relative',
            selectedPlan === 'yearly' ? 'border-yellow-500 shadow-xl' : 'border-transparent hover:shadow-lg'
          ]"
        >
          <div class="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <span class="bg-yellow-500 text-white text-xs px-3 py-1 rounded-full font-medium">超值</span>
          </div>

          <div class="text-center">
            <h3 class="text-xl font-bold text-gray-800 mb-2">年度会员</h3>
            <div class="text-4xl font-bold text-yellow-600 mb-4">¥288</div>
            <p class="text-gray-500 text-sm mb-6">365天有效期 · 省¥60</p>

            <ul class="text-left space-y-3 mb-6">
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限视频下载
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限 AI 总结
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                无限 AI 问答
              </li>
              <li class="flex items-center text-gray-700">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                全格式 + 高清导出
              </li>
              <li class="flex items-center text-yellow-600 font-medium">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                优先技术支持
              </li>
            </ul>

            <button
              @click.stop="handleSubscribe('yearly')"
              :disabled="loading || selectedPlan !== 'yearly'"
              class="w-full bg-yellow-600 text-white py-2 px-4 rounded-lg hover:bg-yellow-700 transition disabled:opacity-50 font-medium"
            >
              {{ loading && selectedPlan === 'yearly' ? '处理中...' : '立即订阅' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 支付说明 -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h3 class="text-lg font-bold text-gray-800 mb-4">支付说明</h3>
        <div class="grid md:grid-cols-3 gap-4 text-sm">
          <div class="flex items-start">
            <svg class="w-6 h-6 text-green-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            <div>
              <p class="font-medium text-gray-800">安全支付</p>
              <p class="text-gray-600">采用 Stripe 加密支付，保护您的交易安全</p>
            </div>
          </div>
          <div class="flex items-start">
            <svg class="w-6 h-6 text-blue-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            <div>
              <p class="font-medium text-gray-800">即时生效</p>
              <p class="text-gray-600">支付成功后会员权限立即生效</p>
            </div>
          </div>
          <div class="flex items-start">
            <svg class="w-6 h-6 text-purple-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
            </svg>
            <div>
              <p class="font-medium text-gray-800">多种支付方式</p>
              <p class="text-gray-600">支持支付宝、微信支付、银行卡等多种方式</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 返回按钮 -->
      <div class="text-center">
        <router-link
          to="/"
          class="inline-flex items-center text-gray-600 hover:text-gray-800 font-medium"
        >
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          返回首页
        </router-link>
      </div>
    </div>

    <!-- Stripe 支付弹窗 -->
    <el-dialog
      v-model="showPaymentDialog"
      title="完成支付"
      width="90%"
      :close-on-click-modal="false"
    >
      <div id="stripe-card-element" class="mb-4"></div>
      <div v-if="paymentError" class="text-red-500 text-sm mb-4">{{ paymentError }}</div>

      <template #footer>
        <button
          @click="closePaymentDialog"
          class="px-4 py-2 text-gray-600 hover:text-gray-800 mr-2"
        >
          取消
        </button>
        <button
          @click="confirmPayment"
          :disabled="processingPayment"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {{ processingPayment ? '支付中...' : `支付 ¥${currentAmount}` }}
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import auth from '../auth/auth'
import { loadStripe } from '@stripe/stripe-js'

const router = useRouter()
const selectedPlan = ref('quarterly')
const loading = ref(false)
const showPaymentDialog = ref(false)
const processingPayment = ref(false)
const paymentError = ref('')
const stripe = ref(null)
const cardElement = ref(null)
const paymentIntent = ref(null)

const plans = {
  monthly: { price: 29, name: '月度会员' },
  quarterly: { price: 79, name: '季度会员' },
  yearly: { price: 288, name: '年度会员' }
}

const currentAmount = computed(() => {
  return plans[selectedPlan.value]?.price || 0
})

const selectPlan = (plan) => {
  selectedPlan.value = plan
}

const handleSubscribe = async (plan) => {
  // 检查是否已登录
  if (!auth.isAuthenticated()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  loading.value = true

  try {
    // 创建支付意图
    const response = await fetch('/api/payment/create-intent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${auth.getToken()}`
      },
      body: JSON.stringify({ plan_type: plan })
    })

    const data = await response.json()

    if (response.ok) {
      paymentIntent.value = data.payment

      // 加载 Stripe
      if (!stripe.value) {
        stripe.value = await loadStripe(data.payment.publishable_key)
      }

      // 显示支付弹窗
      showPaymentDialog.value = true

      // 延迟创建卡片元素，确保DOM已渲染
      setTimeout(() => {
        createCardElement()
      }, 100)
    } else {
      ElMessage.error(data.error || '创建支付失败')
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

const createCardElement = async () => {
  if (!stripe.value || !paymentIntent.value) return

  const elements = stripe.value.elements()

  cardElement.value = elements.create('card', {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4'
        }
      }
    }
  })

  cardElement.value.mount('#stripe-card-element')
}

const confirmPayment = async () => {
  if (!stripe.value || !cardElement.value || !paymentIntent.value) return

  processingPayment.value = true
  paymentError.value = ''

  try {
    const { error, paymentIntent: confirmedIntent } = await stripe.value.confirmCardPayment(
      paymentIntent.value.client_secret,
      {
        payment_method: {
          card: cardElement.value
        }
      }
    )

    if (error) {
      paymentError.value = error.message
    } else if (confirmedIntent.status === 'succeeded') {
      // 支付成功，刷新用户信息
      await auth.refreshUserInfo()

      ElMessage.success('支付成功！会员已开通')
      showPaymentDialog.value = false
      router.push('/')
    }
  } catch (error) {
    paymentError.value = '支付处理失败，请稍后重试'
  } finally {
    processingPayment.value = false
  }
}

const closePaymentDialog = () => {
  showPaymentDialog.value = false
  paymentError.value = ''
  if (cardElement.value) {
    cardElement.value.destroy()
    cardElement.value = null
  }
}
</script>
