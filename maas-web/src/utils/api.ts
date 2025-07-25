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

import axios, { type AxiosInstance, type AxiosResponse, type AxiosRequestConfig, AxiosError } from 'axios'
import { useUserStore } from '@/stores/userStore'
import { tokenNotification } from '@/utils/notification'
import { logTokenEvent, logTokenError, MonitoringEvent } from '@/utils/tokenMonitor'

// 开发环境下加载调试工具
if (import.meta.env.DEV) {
  import('@/utils/tokenDebugTools')
}

// API响应接口
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 用户相关请求接口
export interface UserRegisterRequest {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  organization?: string
}

export interface UserLoginRequest {
  login_id: string
  password: string
}

export interface UserUpdateRequest {
  first_name?: string
  last_name?: string
  avatar_url?: string
  organization?: string
  bio?: string
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

export interface ApiKeyCreateRequest {
  name: string
  permissions: string[]
  expires_at?: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirmRequest {
  token: string
  new_password: string
}

// 认证响应接口
export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
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
}

// 统计数据相关接口
export interface UserStatsResponse {
  total_api_calls: number
  total_storage_used: number
  total_compute_hours: number
  models_created: number
  applications_created: number
  last_30_days_activity: Record<string, number>
  api_keys_count: number
  requests_count: number
  usage_cost: number
}

export interface AdminStatsResponse {
  total_users: number
  total_api_keys: number
  total_requests: number
  active_users: number
  active_users_30d: number
  total_models: number
  total_deployments: number
  storage_usage_total: number
  user_growth_trend: Record<string, number>
  popular_models: Array<{
    id: string
    name: string
    usage_count: number
  }>
}

export interface ActivityLogResponse {
  id: string
  type: string
  description: string
  timestamp: string
  status: 'success' | 'warning' | 'error'
  user_id?: string
  metadata?: Record<string, unknown>
}

export interface SystemHealthResponse {
  status: 'healthy' | 'warning' | 'error'
  database: boolean
  redis: boolean
  storage: boolean
  uptime: number
  version: string
}

// 审计日志相关接口
export interface AuditLogResponse {
  audit_log_id: string
  user_id?: string
  username?: string
  action: string
  resource_type?: string
  resource_id?: string
  description: string
  ip_address?: string
  user_agent?: string
  request_id?: string
  result: 'success' | 'failure'
  error_message?: string
  metadata: Record<string, unknown>
  created_at: string
}

export interface AuditStatsResponse {
  total_operations: number
  successful_operations: number
  failed_operations: number
  unique_users: number
  recent_logins: number
  top_actions: Array<{
    action: string
    count: number
  }>
}

export interface AuditLogsListResponse {
  items: AuditLogResponse[]
  total: number
  page: number
  size: number
}

class ApiClient {
  private client: AxiosInstance
  private isRefreshing = false
  private isPreventiveRefreshing = false
  private refreshRetryCount = 0
  private readonly maxRefreshRetries = 3
  private refreshRetryDelay = 1000 // ms
  private readonly preventiveRefreshThreshold = 5 // 分钟
  private readonly queueTimeout = 30000 // 队列超时时间：30秒
  private failedQueue: Array<{
    resolve: (value: string | null) => void
    reject: (error: AxiosError) => void
    timestamp: number
  }> = []

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
    
    // 定期清理过期的队列项（每10秒清理一次）
    setInterval(() => {
      if (this.failedQueue.length > 0) {
        this.cleanExpiredQueueItems()
      }
    }, 10000)
  }

  private processQueue(error: AxiosError | null, token: string | null = null) {
    const currentTime = Date.now()
    
    // 处理队列中的所有请求
    this.failedQueue.forEach(({ resolve, reject, timestamp }) => {
      // 检查请求是否超时
      if (currentTime - timestamp > this.queueTimeout) {
        console.warn('队列中的请求已超时')
        reject(new AxiosError('Request timeout in queue', 'QUEUE_TIMEOUT'))
        return
      }
      
      if (error) {
        reject(error)
      } else {
        resolve(token)
      }
    })
    
    this.failedQueue = []
  }

  private cleanExpiredQueueItems() {
    const currentTime = Date.now()
    const originalLength = this.failedQueue.length
    
    this.failedQueue = this.failedQueue.filter(({ timestamp, reject }) => {
      const isExpired = currentTime - timestamp > this.queueTimeout
      if (isExpired) {
        console.warn('清理过期的队列请求')
        reject(new AxiosError('Request timeout in queue', 'QUEUE_TIMEOUT'))
        
        // 记录队列超时
        logTokenEvent(MonitoringEvent.QUEUE_TIMEOUT, {
          queueSize: originalLength,
          metadata: { timeoutMs: this.queueTimeout }
        })
      }
      return !isExpired
    })
    
    if (originalLength !== this.failedQueue.length) {
      const cleanedCount = originalLength - this.failedQueue.length
      console.log(`清理了 ${cleanedCount} 个过期请求`)
      
      // 记录队列清理
      logTokenEvent(MonitoringEvent.QUEUE_CLEANUP, {
        queueSize: originalLength,
        metadata: { 
          cleanedCount,
          remainingCount: this.failedQueue.length
        }
      })
    }
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  private isTokenExpiringSoon(token: string, thresholdMinutes: number = this.preventiveRefreshThreshold): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      const thresholdTime = currentTime + (thresholdMinutes * 60)
      return payload.exp ? payload.exp < thresholdTime : true
    } catch {
      return true
    }
  }

  private async preventiveRefresh(): Promise<void> {
    if (this.isPreventiveRefreshing || this.isRefreshing) {
      return // 避免重复刷新
    }

    const userStore = useUserStore()
    const tokens = userStore.tokens
    
    if (!tokens?.access_token || !tokens?.refresh_token) {
      return
    }

    if (this.isTokenExpiringSoon(tokens.access_token)) {
      // 记录预防性刷新开始
      logTokenEvent(MonitoringEvent.PREVENTIVE_REFRESH_START)
      
      console.log('Token即将过期，开始预防性刷新')
      this.isPreventiveRefreshing = true
      
      try {
        const newTokens = await this.refreshTokenWithRetry()
        userStore.setTokens({
          access_token: newTokens.access_token,
          refresh_token: newTokens.refresh_token,
          token_type: newTokens.token_type,
          expires_in: newTokens.expires_in,
        })
        
        // 记录预防性刷新成功
        logTokenEvent(MonitoringEvent.PREVENTIVE_REFRESH_SUCCESS)
        tokenNotification.preventiveRefreshSuccess()
      } catch (error) {
        // 记录预防性刷新失败
        logTokenError(MonitoringEvent.PREVENTIVE_REFRESH_FAILED, error as AxiosError)
        tokenNotification.preventiveRefreshFailed(error as AxiosError)
        // 预防性刷新失败不应该中断当前请求，让正常的401处理机制处理
      } finally {
        this.isPreventiveRefreshing = false
      }
    }
  }

  private async refreshTokenWithRetry(): Promise<AuthTokens> {
    const userStore = useUserStore()
    const tokens = userStore.tokens
    
    if (!tokens?.refresh_token) {
      logTokenError(MonitoringEvent.TOKEN_REFRESH_FAILED, 
        new AxiosError('No refresh token available', 'NO_REFRESH_TOKEN'))
      throw new Error('No refresh token available')
    }

    for (let attempt = 1; attempt <= this.maxRefreshRetries; attempt++) {
      const startTime = Date.now()
      
      try {
        // 记录刷新尝试
        logTokenEvent(MonitoringEvent.TOKEN_REFRESH_ATTEMPT, {
          attempt,
          maxAttempts: this.maxRefreshRetries
        })
        
        console.log(`Token刷新尝试 ${attempt}/${this.maxRefreshRetries}`)
        
        const response = await this.client.post<ApiResponse<AuthTokens>>('/auth/refresh', {}, {
          headers: {
            'Authorization': `Bearer ${tokens.refresh_token}`
          }
        })

        if (response.data.success && response.data.data) {
          const duration = Date.now() - startTime
          
          // 记录成功
          logTokenEvent(MonitoringEvent.TOKEN_REFRESH_SUCCESS, {
            attempt,
            duration,
            metadata: { responseTime: duration }
          })
          
          this.refreshRetryCount = 0 // 重置重试计数
          return response.data.data
        } else {
          throw new Error('Token refresh response invalid')
        }
      } catch (error) {
        const duration = Date.now() - startTime
        
        console.warn(`Token刷新失败，尝试 ${attempt}/${this.maxRefreshRetries}:`, error)
        
        // 记录失败
        logTokenError(MonitoringEvent.TOKEN_REFRESH_FAILED, error as AxiosError, {
          attempt,
          maxAttempts: this.maxRefreshRetries,
          duration
        })
        
        // 显示用户友好的提示
        tokenNotification.refreshFailed(error as AxiosError, attempt, this.maxRefreshRetries)
        
        if (attempt === this.maxRefreshRetries) {
          // 记录所有重试失败
          logTokenError(MonitoringEvent.TOKEN_REFRESH_ALL_FAILED, error as AxiosError, {
            totalAttempts: this.maxRefreshRetries,
            totalDuration: Date.now() - (startTime - duration)
          })
          throw error
        }
        
        // 记录重试
        logTokenEvent(MonitoringEvent.TOKEN_REFRESH_RETRY, {
          attempt: attempt + 1,
          maxAttempts: this.maxRefreshRetries,
          retryDelay: this.refreshRetryDelay * Math.pow(2, attempt)
        })
        
        // 等待一段时间后重试，使用指数退避
        const delayTime = this.refreshRetryDelay * Math.pow(2, attempt - 1)
        await this.delay(delayTime)
      }
    }
    
    throw new Error('Token refresh failed after all retries')
  }

  private setupInterceptors() {
    // 请求拦截器 - 添加认证头
    this.client.interceptors.request.use(
      async (config) => {
        const userStore = useUserStore()
        
        // 尝试预防性刷新token（如果即将过期）
        await this.preventiveRefresh()
        
        const token = await userStore.getAccessToken()

        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        return config
      },
      (error) => {
        return Promise.reject(error)
      },
    )

    // 响应拦截器 - 处理错误和token刷新
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
        const userStore = useUserStore()

        // 区分错误类型
        const isNetworkError = !error.response
        const isTimeoutError = error.code === 'ECONNABORTED' || error.message.includes('timeout')
        const isAuthError = error.response?.status === 401
        const isServerError = error.response && error.response.status >= 500

        // 处理网络错误和超时错误
        if (isNetworkError || isTimeoutError) {
          console.warn('网络或超时错误:', error.message)
          // 网络错误不尝试token刷新，直接返回错误
          return Promise.reject(error)
        }

        // 处理服务器错误
        if (isServerError) {
          console.warn('服务器错误:', error.response?.status, error.message)
          // 服务器错误不尝试token刷新，直接返回错误
          return Promise.reject(error)
        }

        // 处理401未授权错误
        if (isAuthError && !originalRequest._retry) {
          // 如果是刷新token接口本身失败，直接登出
          if (originalRequest.url?.includes('/auth/refresh')) {
            console.error('刷新token接口本身失败')
            userStore.clearAuth()
            if (typeof window !== 'undefined') {
              window.location.href = '/#/auth/login'
            }
            return Promise.reject(error)
          }

          // 如果正在刷新token，将请求加入队列
          if (this.isRefreshing) {
            // 清理过期的队列项
            this.cleanExpiredQueueItems()
            
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ 
                resolve, 
                reject, 
                timestamp: Date.now() 
              })
            }).then(token => {
              if (token && originalRequest.headers) {
                originalRequest.headers['Authorization'] = `Bearer ${token}`
              }
              return this.client(originalRequest)
            }).catch(err => {
              return Promise.reject(err)
            })
          }

          originalRequest._retry = true
          this.isRefreshing = true

          try {
            // 使用带重试机制的token刷新方法
            const newTokens = await this.refreshTokenWithRetry()
            
            // 更新token
            userStore.setTokens({
              access_token: newTokens.access_token,
              refresh_token: newTokens.refresh_token,
              token_type: newTokens.token_type,
              expires_in: newTokens.expires_in,
            })

            // 处理队列中的请求
            this.processQueue(null, newTokens.access_token)

            // 重新发送原请求
            if (originalRequest.headers) {
              originalRequest.headers['Authorization'] = `Bearer ${newTokens.access_token}`
            }
            return this.client(originalRequest)
          } catch (refreshError) {
            // 刷新失败，清除认证状态
            console.error('Token刷新重试全部失败:', refreshError)
            this.processQueue(refreshError as AxiosError, null)
            
            // 显示最终失败通知
            tokenNotification.allRetriesFailed(refreshError as AxiosError)
            
            userStore.clearAuth()
            
            // 延迟跳转，给用户时间看到通知
            if (typeof window !== 'undefined') {
              setTimeout(() => {
                window.location.href = '/#/auth/login'
              }, 3000)
            }
            
            return Promise.reject(refreshError)
          } finally {
            this.isRefreshing = false
          }
        }

        // 处理403禁止访问错误
        if (error.response?.status === 403) {
          // 403通常表示权限不足，不需要刷新token
          console.warn('权限不足:', error.response.status)
          return Promise.reject(error)
        }

        // 其他错误直接返回
        return Promise.reject(error)
      },
    )
  }

  // 认证相关API
  auth = {
    register: (data: UserRegisterRequest) => this.client.post<ApiResponse>('/auth/register', data),

    login: (data: UserLoginRequest) => this.client.post<ApiResponse<LoginResponse>>('/auth/login', data),

    refreshToken: () => this.client.post<ApiResponse<AuthTokens>>('/auth/refresh'),

    logout: () => this.client.post<ApiResponse>('/auth/logout'),

    forgotPassword: (data: PasswordResetRequest) =>
      this.client.post<ApiResponse>('/auth/forgot-password', data),

    resetPassword: (data: PasswordResetConfirmRequest) =>
      this.client.post<ApiResponse>('/auth/reset-password', data),

    verifyEmail: (token: string) => this.client.post<ApiResponse>('/auth/verify-email', { token }),


    getPublicKey: () => this.client.get<ApiResponse>('/auth/crypto/public-key'),
  }

  // 用户管理API
  users = {
    getProfile: () => this.client.get<ApiResponse>('/users/me'),

    updateProfile: (data: UserUpdateRequest) => this.client.put<ApiResponse>('/users/me', data),

    changePassword: (data: PasswordChangeRequest) =>
      this.client.post<ApiResponse>('/users/me/change-password', data),

    getStats: () => this.client.get<ApiResponse>('/users/me/stats'),

    getApiKeys: () => this.client.get<ApiResponse>('/users/me/api-keys'),

    createApiKey: (data: ApiKeyCreateRequest) =>
      this.client.post<ApiResponse>('/users/me/api-keys', data),

    revokeApiKey: (keyId: string) => this.client.delete<ApiResponse>(`/users/me/api-keys/${keyId}`),

    // 管理员API
    searchUsers: (params: {
      keyword?: string
      status?: string
      organization?: string
      page?: number
      limit?: number
    }) => this.client.get<ApiResponse>('/users', { params }),

    getUserById: (userId: string) => this.client.get<ApiResponse>(`/users/${userId}`),

    suspendUser: (userId: string, reason: string) =>
      this.client.post<ApiResponse>(`/users/${userId}/suspend`, null, {
        params: { reason },
      }),

    activateUser: (userId: string) => this.client.post<ApiResponse>(`/users/${userId}/activate`),
  }

  // 统计数据API
  stats = {
    // 用户统计
    getUserStats: () => this.client.get<ApiResponse<UserStatsResponse>>('/users/me/stats'),

    // 管理员统计
    getAdminStats: () => this.client.get<ApiResponse<AdminStatsResponse>>('/admin/stats'),

    // 获取用户活动日志
    getUserActivityLogs: (
      params: {
        page?: number
        limit?: number
        type?: string
      } = {},
    ) => this.client.get<ApiResponse<ActivityLogResponse[]>>('/users/me/activity-logs', { params }),

    // 获取所有用户活动日志（管理员）
    getAllActivityLogs: (
      params: {
        page?: number
        limit?: number
        user_id?: string
        type?: string
      } = {},
    ) => this.client.get<ApiResponse<ActivityLogResponse[]>>('/admin/activity-logs', { params }),
  }

  // 系统监控API
  system = {
    // 系统健康检查
    getHealth: () => this.client.get<ApiResponse<SystemHealthResponse>>('/system/health'),

    // 系统指标
    getMetrics: () => this.client.get<ApiResponse>('/system/metrics'),

    // 资源使用情况
    getResources: () => this.client.get<ApiResponse>('/system/resources'),
  }

  // 仪表盘API
  dashboard = {
    // 获取仪表盘概览数据
    getOverview: () => this.client.get<ApiResponse>('/dashboard/overview'),
  }

  // 审计日志API
  audit = {
    // 获取审计日志列表
    getLogs: (
      params: {
        page?: number
        size?: number
        username?: string
        action?: string
        result?: string
        start_time?: string
        end_time?: string
      } = {},
    ) => this.client.get<ApiResponse<AuditLogsListResponse>>('/audit/logs', { params }),

    // 获取审计日志统计
    getStats: () => this.client.get<ApiResponse<AuditStatsResponse>>('/audit/stats'),

    // 导出审计日志
    exportLogs: (data: { log_ids: string[] }) =>
      this.client.post<ApiResponse<AuditLogResponse[]>>('/audit/logs/export', data),
  }

  // 通用请求方法
  get<T = unknown>(url: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> {
    return this.client.get(url, { params })
  }

  post<T = unknown>(url: string, data?: unknown): Promise<AxiosResponse<T>> {
    return this.client.post(url, data)
  }

  put<T = unknown>(url: string, data?: unknown): Promise<AxiosResponse<T>> {
    return this.client.put(url, data)
  }

  delete<T = unknown>(url: string): Promise<AxiosResponse<T>> {
    return this.client.delete(url)
  }
}

// 创建单例实例
export const apiClient = new ApiClient()

// 便捷的API方法导出
export const {
  auth: { register, login, refreshToken, logout, forgotPassword, resetPassword, verifyEmail, getPublicKey },
  users: { getProfile, updateProfile, changePassword, getStats, getApiKeys, createApiKey, revokeApiKey, searchUsers, getUserById, suspendUser, activateUser },
  stats: { getUserStats, getAdminStats, getUserActivityLogs, getAllActivityLogs },
  system: { getHealth: getSystemHealth, getMetrics: getSystemMetrics, getResources: getSystemResources },
  dashboard: { getOverview: getDashboardOverview },
  audit: { getLogs: getAuditLogs, getStats: getAuditStats, exportLogs: exportAuditLogs },
} = apiClient

// 错误处理工具函数
export const handleApiError = (error: unknown): string => {
  if (error instanceof AxiosError) {
    if (error.response?.data?.detail) {
      return error.response.data.detail
    }
    if (error.response?.data?.message) {
      return error.response.data.message
    }
    if (error.message) {
      return error.message
    }
  }
  if (error instanceof Error) {
    return error.message
  }
  return '请求失败，请稍后重试'
}
