import axios, { type AxiosInstance, type AxiosResponse, AxiosError } from 'axios'
import { useUserStore } from '@/stores/userStore'

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

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器 - 添加认证头
    this.client.interceptors.request.use(
      async (config) => {
        const userStore = useUserStore()
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
        const userStore = useUserStore()

        if (error.response?.status === 401) {
          // 401 未授权，清除认证状态并重定向到登录页
          userStore.clearAuth()
          // 这里可以添加路由跳转到登录页
          // router.push('/login')
        }

        return Promise.reject(error)
      },
    )
  }

  // 认证相关API
  auth = {
    register: (data: UserRegisterRequest) => this.client.post<ApiResponse>('/auth/register', data),

    login: (data: UserLoginRequest) => this.client.post<ApiResponse>('/auth/login', data),

    refreshToken: () => this.client.post<ApiResponse>('/auth/refresh'),

    logout: () => this.client.post<ApiResponse>('/auth/logout'),

    forgotPassword: (data: PasswordResetRequest) =>
      this.client.post<ApiResponse>('/auth/forgot-password', data),

    resetPassword: (data: PasswordResetConfirmRequest) =>
      this.client.post<ApiResponse>('/auth/reset-password', data),

    verifyEmail: (token: string) => this.client.post<ApiResponse>('/auth/verify-email', { token }),

    getCurrentUser: () => this.client.get<ApiResponse>('/auth/me'),

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
    getUserActivityLogs: (params: {
      page?: number
      limit?: number
      type?: string
    } = {}) => this.client.get<ApiResponse<ActivityLogResponse[]>>('/users/me/activity-logs', { params }),

    // 获取所有用户活动日志（管理员）
    getAllActivityLogs: (params: {
      page?: number
      limit?: number
      user_id?: string
      type?: string
    } = {}) => this.client.get<ApiResponse<ActivityLogResponse[]>>('/admin/activity-logs', { params }),
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
