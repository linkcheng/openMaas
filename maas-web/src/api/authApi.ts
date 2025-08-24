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

import { apiClient } from '@/utils/apiClient'
import type { ApiResponse } from '@/types/api'
import type {
  UserRegisterRequest,
  UserLoginRequest,
  AuthTokens,
  LoginResponse,
  PasswordResetRequest,
  PasswordResetConfirmRequest,
} from '@/types/requests'

/**
 * 认证相关 API 接口
 */
export const authApi = {
  // 用户注册
  register: (data: UserRegisterRequest) => apiClient.post<ApiResponse>('/auth/register', data),

  // 用户登录
  login: (data: UserLoginRequest) => apiClient.post<ApiResponse<LoginResponse>>('/auth/login', data),

  // 刷新 token
  refreshToken: () => apiClient.post<ApiResponse<AuthTokens>>('/auth/refresh'),

  // 用户登出
  logout: () => apiClient.post<ApiResponse>('/auth/logout'),

  // 忘记密码
  forgotPassword: (data: PasswordResetRequest) =>
    apiClient.post<ApiResponse>('/auth/forgot-password', data),

  // 重置密码
  resetPassword: (data: PasswordResetConfirmRequest) =>
    apiClient.post<ApiResponse>('/auth/reset-password', data),

  // 邮箱验证
  verifyEmail: (token: string) => apiClient.post<ApiResponse>('/auth/verify-email', { token }),

  // 获取公钥
  getPublicKey: () => apiClient.get<ApiResponse>('/auth/crypto/public-key'),
}

// 便捷的API方法导出
export const {
  register,
  login,
  refreshToken,
  logout,
  forgotPassword,
  resetPassword,
  verifyEmail,
  getPublicKey,
} = authApi