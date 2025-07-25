/*
 * Copyright 2025 MaaS Team
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/userStore'
import { apiClient, handleApiError } from '@/utils/api'
import { SM2CryptoUtil } from '@/utils/crypto'
import type {
  UserRegisterRequest,
  UserLoginRequest,
  PasswordResetRequest,
  PasswordResetConfirmRequest,
  LoginResponse,
  AuthTokens,
} from '@/utils/api'

export const useAuth = () => {
  const userStore = useUserStore()

  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => userStore.isAuthenticated)
  const currentUser = computed(() => userStore.user)
  const isAdmin = computed(() => userStore.isAdmin)
  const isDeveloper = computed(() => userStore.isDeveloper)

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  // 用户注册
  const register = async (data: UserRegisterRequest) => {
    isLoading.value = true
    error.value = null

    try {
      // 加密密码
      const encryptedPassword = await SM2CryptoUtil.encryptPassword(data.password)

      const encryptedData = {
        ...data,
        password: encryptedPassword,
      }

      const response = await apiClient.auth.register(encryptedData)

      if (response.data.success) {
        return { success: true, message: response.data.message }
      } else {
        error.value = response.data.error || '注册失败'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = handleApiError(err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 用户登录
  const login = async (data: UserLoginRequest) => {
    isLoading.value = true
    error.value = null

    try {
      // 加密密码
      const encryptedPassword = await SM2CryptoUtil.encryptPassword(data.password)
      const encryptedData = {
        ...data,
        password: encryptedPassword,
      }

      const response = await apiClient.auth.login(encryptedData)

      if (response.data.success && response.data.data) {
        const tokenData: LoginResponse = response.data.data

        // 存储token和用户信息
        userStore.setTokens({
          access_token: tokenData.access_token,
          refresh_token: tokenData.refresh_token,
          token_type: tokenData.token_type,
          expires_in: tokenData.expires_in,
        })

        userStore.setUser(tokenData.user)

        return { success: true, message: response.data.message }
      } else {
        error.value = response.data.error || '登录失败'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = handleApiError(err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 用户登出
  const logout = async () => {
    isLoading.value = true
    error.value = null

    try {
      await apiClient.auth.logout()
    } catch (err) {
      // 即使登出API调用失败，也要清除本地状态
      console.error('登出API调用失败:', err)
    } finally {
      // 清除本地认证状态
      userStore.clearAuth()
      isLoading.value = false
    }
  }

  // 刷新token
  const refreshToken = async () => {
    try {
      const response = await apiClient.auth.refreshToken()

      if (response.data.success && response.data.data) {
        const tokenData: AuthTokens = response.data.data

        userStore.setTokens({
          access_token: tokenData.access_token,
          refresh_token: tokenData.refresh_token,
          token_type: tokenData.token_type,
          expires_in: tokenData.expires_in,
        })

        return true
      }
      return false
    } catch (err) {
      console.error('刷新token失败:', err)
      userStore.clearAuth()
      return false
    }
  }

  // 获取当前用户信息
  const getCurrentUser = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.users.getProfile()

      if (response.data.success && response.data.data) {
        const userData: LoginResponse['user'] = response.data.data
        userStore.setUser(userData)
        return { success: true, data: userData }
      } else {
        error.value = response.data.error || '获取用户信息失败'
        // 如果获取用户信息失败，清除认证状态
        userStore.clearAuth()
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = handleApiError(err)
      // 认证失败，清除状态
      userStore.clearAuth()
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 忘记密码
  const forgotPassword = async (data: PasswordResetRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.auth.forgotPassword(data)

      if (response.data.success) {
        return { success: true, message: response.data.message }
      } else {
        error.value = response.data.error || '发送重置邮件失败'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = handleApiError(err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 重置密码
  const resetPassword = async (data: PasswordResetConfirmRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.auth.resetPassword(data)

      if (response.data.success) {
        return { success: true, message: response.data.message }
      } else {
        error.value = response.data.error || '重置密码失败'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = handleApiError(err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 验证邮箱
  const verifyEmail = async (token: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.auth.verifyEmail(token)

      if (response.data.success) {
        return { success: true, message: response.data.message }
      } else {
        error.value = response.data.error || '邮箱验证失败'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = handleApiError(err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 权限检查
  const hasPermission = (resource: string, action: string) => {
    return userStore.hasPermission(resource, action)
  }

  // 角色检查
  const hasRole = (roleName: string) => {
    return userStore.hasRole(roleName)
  }

  // 初始化认证状态
  const initializeAuth = async () => {
    userStore.initializeAuth()

    // 如果有token，尝试获取用户信息验证token有效性
    if (userStore.tokens && userStore.isAuthenticated) {
      const result = await getCurrentUser()
      if (!result.success) {
        // 获取用户信息失败，说明token无效，已在getCurrentUser中清除了认证状态
        console.warn('Token validation failed, user logged out')
      }
    }
  }

  return {
    // 状态
    isLoading,
    error,

    // 计算属性
    isAuthenticated,
    currentUser,
    isAdmin,
    isDeveloper,

    // 方法
    clearError,
    register,
    login,
    logout,
    refreshToken,
    getCurrentUser,
    forgotPassword,
    resetPassword,
    verifyEmail,
    hasPermission,
    hasRole,
    initializeAuth,
  }
}
