import axios, { type AxiosInstance, type AxiosResponse, AxiosError } from 'axios'
import { useUserStore } from '@/stores/userStore'

// API响应接口
export interface ApiResponse<T = any> {
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
  email: string
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

  // 通用请求方法
  get<T = any>(url: string, params?: any): Promise<AxiosResponse<T>> {
    return this.client.get(url, { params })
  }

  post<T = any>(url: string, data?: any): Promise<AxiosResponse<T>> {
    return this.client.post(url, data)
  }

  put<T = any>(url: string, data?: any): Promise<AxiosResponse<T>> {
    return this.client.put(url, data)
  }

  delete<T = any>(url: string): Promise<AxiosResponse<T>> {
    return this.client.delete(url)
  }
}

// 创建单例实例
export const apiClient = new ApiClient()

// 错误处理工具函数
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  if (error.message) {
    return error.message
  }
  return '请求失败，请稍后重试'
}
