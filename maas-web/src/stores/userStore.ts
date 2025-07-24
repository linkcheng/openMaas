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

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 用户接口定义
export interface User {
  id: string
  username: string
  email: string
  profile: {
    first_name: string
    last_name: string
    full_name: string
    avatar_url?: string
    organization?: string
    bio?: string
  }
  status: 'active' | 'inactive' | 'suspended'
  email_verified: boolean
  roles: Array<{
    id: string
    name: string
    description: string
    permissions: string[]
  }>
  quota?: {
    api_calls_limit: number
    api_calls_used: number
    api_calls_remaining: number
    api_usage_percentage: number
    storage_limit: number
    storage_used: number
    storage_remaining: number
    storage_usage_percentage: number
    compute_hours_limit: number
    compute_hours_used: number
    compute_hours_remaining: number
  }
  created_at: string
  updated_at: string
  last_login_at?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const tokens = ref<AuthTokens | null>(null)
  const isLoading = ref(false)
  const isAuthenticated = ref(false)

  // 计算属性
  const userFullName = computed(() => user.value?.profile.full_name || '')
  const userAvatar = computed(() => user.value?.profile.avatar_url || '')
  const userOrganization = computed(() => user.value?.profile.organization || '')
  const isAdmin = computed(
    () => true, // 暂时移除权限判断，允许所有用户访问管理页面
  )
  const isDeveloper = computed(
    () => user.value?.roles.some((role) => role.name === 'developer') || false,
  )

  // 权限检查
  const hasPermission = (resource: string, action: string): boolean => {
    if (!user.value) return false

    const permissions = user.value.roles.flatMap((role) => role.permissions)
    const requiredPermission = `${resource}:${action}`

    return permissions.some(
      (permission) =>
        permission === requiredPermission || permission === `${resource}:*` || permission === '*:*',
    )
  }

  // 角色检查
  const hasRole = (roleName: string): boolean => {
    if (!user.value) return false
    return user.value.roles.some((role) => role.name === roleName)
  }

  // Actions
  const setUser = (userData: User) => {
    user.value = userData
    isAuthenticated.value = true
  }

  const setTokens = (tokenData: AuthTokens) => {
    tokens.value = tokenData
    // 将token存储到localStorage
    localStorage.setItem('access_token', tokenData.access_token)
    localStorage.setItem('refresh_token', tokenData.refresh_token)
  }

  const clearAuth = () => {
    user.value = null
    tokens.value = null
    isAuthenticated.value = false
    // 清除localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  const initializeAuth = () => {
    // 从localStorage恢复token
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')

    if (accessToken && refreshToken) {
      // 检查token是否过期
      if (isTokenExpired(accessToken)) {
        // token已过期，清除localStorage
        clearAuth()
        return
      }

      tokens.value = {
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'Bearer',
        expires_in: 0, // 从JWT解析过期时间
      }
      isAuthenticated.value = true
    }
  }

  const updateUserProfile = (profileData: Partial<User['profile']>) => {
    if (user.value) {
      user.value.profile = { ...user.value.profile, ...profileData }
    }
  }

  const updateUserQuota = (quotaData: Partial<User['quota']>) => {
    if (user.value && user.value.quota) {
      user.value.quota = { ...user.value.quota, ...quotaData }
    }
  }

  // 检查token是否过期
  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      return payload.exp ? payload.exp < currentTime : false
    } catch {
      return true
    }
  }

  // 获取访问令牌（自动处理刷新）
  const getAccessToken = async (): Promise<string | null> => {
    if (!tokens.value) return null

    // 检查token是否过期
    if (isTokenExpired(tokens.value.access_token)) {
      // access_token已过期，但不直接清除认证状态
      // 让HTTP拦截器处理自动刷新
      return null
    }

    return tokens.value.access_token
  }

  return {
    // 状态
    user,
    tokens,
    isLoading,
    isAuthenticated,

    // 计算属性
    userFullName,
    userAvatar,
    userOrganization,
    isAdmin,
    isDeveloper,

    // 方法
    hasPermission,
    hasRole,
    setUser,
    setTokens,
    clearAuth,
    initializeAuth,
    updateUserProfile,
    updateUserQuota,
    getAccessToken,
  }
})
