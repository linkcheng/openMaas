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
  AdminStatsResponse,
  ActivityLogResponse,
  SystemHealthResponse,
  AuditLogResponse,
  AuditStatsResponse,
  AuditLogsListResponse,
} from '@/types/requests'

/**
 * 管理员 API 接口
 */
export const adminApi = {
  // 用户管理
  users: {
    searchUsers: (params: {
      keyword?: string
      status?: string
      organization?: string
      page?: number
      limit?: number
    }) => apiClient.get<ApiResponse>('/users', { params }),

    getUserById: (userId: string) => apiClient.get<ApiResponse>(`/users/${userId}`),

    suspendUser: (userId: string, reason: string) =>
      apiClient.post<ApiResponse>(`/users/${userId}/suspend`, null, {
        params: { reason },
      }),

    activateUser: (userId: string) => apiClient.post<ApiResponse>(`/users/${userId}/activate`),
  },

  // 统计数据
  stats: {
    getAdminStats: () => apiClient.get<ApiResponse<AdminStatsResponse>>('/admin/stats'),

    getAllActivityLogs: (
      params: {
        page?: number
        limit?: number
        user_id?: string
        type?: string
      } = {},
    ) => apiClient.get<ApiResponse<ActivityLogResponse[]>>('/admin/activity-logs', { params }),
  },

  // 系统监控
  system: {
    getHealth: () => apiClient.get<ApiResponse<SystemHealthResponse>>('/system/health'),
    getMetrics: () => apiClient.get<ApiResponse>('/system/metrics'),
    getResources: () => apiClient.get<ApiResponse>('/system/resources'),
  },

  // 仪表盘
  dashboard: {
    getOverview: () => apiClient.get<ApiResponse>('/dashboard/overview'),
  },

  // 审计日志
  audit: {
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
    ) => apiClient.get<ApiResponse<AuditLogsListResponse>>('/audit/logs', { params }),

    getStats: () => apiClient.get<ApiResponse<AuditStatsResponse>>('/audit/stats'),

    exportLogs: (data: { log_ids: string[] }) =>
      apiClient.post<ApiResponse<AuditLogResponse[]>>('/audit/logs/export', data),
  },
}

// 便捷的API方法导出
export const {
  users: { searchUsers, getUserById, suspendUser, activateUser },
  stats: { getAdminStats, getAllActivityLogs },
  system: {
    getHealth: getSystemHealth,
    getMetrics: getSystemMetrics,
    getResources: getSystemResources,
  },
  dashboard: { getOverview: getDashboardOverview },
  audit: { getLogs: getAuditLogs, getStats: getAuditStats, exportLogs: exportAuditLogs },
} = adminApi