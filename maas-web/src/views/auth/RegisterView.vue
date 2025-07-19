<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-600 via-blue-500 to-blue-400 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8"
  >
    <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
      <div class="text-center mb-8">
        <div class="flex justify-center mb-6">
          <div
            class="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg"
          >
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
              />
            </svg>
          </div>
        </div>
        <h2 class="text-3xl font-bold text-gray-800 mb-2">注册 MaaS 账户</h2>
        <p class="text-gray-600">创建您的账户，开始使用智能模型服务</p>
      </div>

      <form class="space-y-6" @submit.prevent="handleRegister">
        <div class="space-y-4">
          <!-- 用户名 -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              用户名
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              minlength="3"
              maxlength="50"
              class="block w-full px-3 py-3 border border-gray-300 bg-white text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              placeholder="请输入用户名（3-50字符）"
            />
          </div>

          <!-- 邮箱 -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              邮箱地址
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="block w-full px-3 py-3 border border-gray-300 bg-white text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              placeholder="请输入邮箱地址"
            />
          </div>

          <!-- 姓名 -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
                名字
              </label>
              <input
                id="first_name"
                v-model="form.first_name"
                type="text"
                required
                maxlength="50"
                class="block w-full px-3 py-3 border border-gray-300 bg-white text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="名字"
              />
            </div>
            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
                姓氏
              </label>
              <input
                id="last_name"
                v-model="form.last_name"
                type="text"
                required
                maxlength="50"
                class="block w-full px-3 py-3 border border-gray-300 bg-white text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="姓氏"
              />
            </div>
          </div>

          <!-- 组织（可选） -->
          <div>
            <label for="organization" class="block text-sm font-medium text-gray-700 mb-2">
              组织 <span class="text-gray-500">(可选)</span>
            </label>
            <input
              id="organization"
              v-model="form.organization"
              type="text"
              maxlength="255"
              class="block w-full px-3 py-3 border border-gray-300 bg-white text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              placeholder="请输入组织名称"
            />
          </div>

          <!-- 密码 -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                minlength="8"
                maxlength="100"
                class="block w-full pr-10 px-3 py-3 border border-gray-300 bg-white text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="至少8位，包含大小写字母和数字"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-gray-600 transition-colors"
              >
                <svg
                  v-if="showPassword"
                  class="h-5 w-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
                  />
                </svg>
                <svg
                  v-else
                  class="h-5 w-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </button>
            </div>
            <!-- 密码强度提示 -->
            <div class="mt-2 space-y-1">
              <div class="flex items-center text-xs">
                <span :class="passwordChecks.length ? 'text-green-600' : 'text-gray-500'">
                  ✓ 至少8个字符
                </span>
              </div>
              <div class="flex items-center text-xs">
                <span :class="passwordChecks.uppercase ? 'text-green-600' : 'text-gray-500'">
                  ✓ 包含大写字母
                </span>
              </div>
              <div class="flex items-center text-xs">
                <span :class="passwordChecks.lowercase ? 'text-green-600' : 'text-gray-500'">
                  ✓ 包含小写字母
                </span>
              </div>
              <div class="flex items-center text-xs">
                <span :class="passwordChecks.number ? 'text-green-600' : 'text-gray-500'">
                  ✓ 包含数字
                </span>
              </div>
            </div>
          </div>

          <!-- 确认密码 -->
          <div>
            <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-2">
              确认密码
            </label>
            <input
              id="confirm_password"
              v-model="form.confirm_password"
              type="password"
              required
              class="block w-full px-3 py-3 border border-gray-300 bg-white text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              placeholder="请再次输入密码"
            />
            <div
              v-if="form.confirm_password && form.password !== form.confirm_password"
              class="mt-1 text-red-600 text-xs"
            >
              密码不匹配
            </div>
          </div>
        </div>

        <!-- 服务条款 -->
        <div class="flex items-center">
          <input
            id="agree-terms"
            v-model="form.agreeTerms"
            type="checkbox"
            required
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="agree-terms" class="ml-2 block text-sm text-gray-700">
            我已阅读并同意
            <a href="#" class="text-blue-600 hover:text-blue-500 transition-colors">服务条款</a>
            和
            <a href="#" class="text-blue-600 hover:text-blue-500 transition-colors">隐私政策</a>
          </label>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <div class="flex items-center">
            <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{{ error }}</span>
          </div>
        </div>

        <!-- 注册按钮 -->
        <div>
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <div v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            </div>
            {{ isLoading ? '注册中...' : '创建账户' }}
          </button>
        </div>

        <!-- 登录链接 -->
        <div class="text-center">
          <p class="text-gray-600">
            已有账户？
            <router-link
              to="/login"
              class="font-medium text-blue-600 hover:text-blue-500 transition-colors"
            >
              立即登录
            </router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { register, isLoading, error, clearError } = useAuth()

// 表单数据
const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  organization: '',
  password: '',
  confirm_password: '',
  agreeTerms: false,
})

const showPassword = ref(false)

// 密码强度检查
const passwordChecks = computed(() => ({
  length: form.value.password.length >= 8,
  uppercase: /[A-Z]/.test(form.value.password),
  lowercase: /[a-z]/.test(form.value.password),
  number: /\d/.test(form.value.password),
}))

// 表单验证
const isFormValid = computed(() => {
  return (
    form.value.username.length >= 3 &&
    form.value.email.includes('@') &&
    form.value.first_name.trim() &&
    form.value.last_name.trim() &&
    passwordChecks.value.length &&
    passwordChecks.value.uppercase &&
    passwordChecks.value.lowercase &&
    passwordChecks.value.number &&
    form.value.password === form.value.confirm_password &&
    form.value.agreeTerms
  )
})

// 处理注册
const handleRegister = async () => {
  clearError()

  if (!isFormValid.value) {
    return
  }

  const result = await register({
    username: form.value.username,
    email: form.value.email,
    password: form.value.password,
    first_name: form.value.first_name,
    last_name: form.value.last_name,
    organization: form.value.organization || undefined,
  })

  if (result.success) {
    // 注册成功，跳转到登录页面并显示提示
    router.push({
      path: '/login',
      query: { message: '注册成功，请检查邮箱完成验证后登录' },
    })
  }
}
</script>
