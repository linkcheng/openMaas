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
  UserUpdateRequest,
  PasswordChangeRequest,
  UserStatsResponse,
  ActivityLogResponse,
} from '@/types/requests'

/**
 * 用户管理 API 接口
 */
export const userApi = {
  // 获取当前用户资料
  getProfile: () => apiClient.get<ApiResponse>('/users/me'),

  // 更新用户资料
  updateProfile: (data: UserUpdateRequest) => apiClient.put<ApiResponse>('/users/me', data),

  // 修改密码
  changePassword: (data: PasswordChangeRequest) =>
    apiClient.post<ApiResponse>('/users/me/change-password', data),

  // 获取用户统计信息
  getStats: () => apiClient.get<ApiResponse<UserStatsResponse>>('/users/me/stats'),

  // 获取用户活动日志
  getActivityLogs: (
    params: {
      page?: number
      limit?: number
      type?: string
    } = {},
  ) => apiClient.get<ApiResponse<ActivityLogResponse[]>>('/users/me/activity-logs', { params }),
}

// 便捷的API方法导出
export const { getProfile, updateProfile, changePassword, getStats, getUserActivityLogs } = userApi