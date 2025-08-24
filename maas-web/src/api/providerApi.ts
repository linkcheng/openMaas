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
  CreateProviderRequest,
  UpdateProviderRequest,
  ListProvidersParams,
  SearchProvidersParams,
  ProviderResponse,
  ProvidersListResponse,
  ProviderStatsResponse,
} from '@/types/providerTypes'

/**
 * 供应商管理 API 接口
 */
export const providerApi = {
  // 获取供应商列表
  listProviders: (params: ListProvidersParams = {}) =>
    apiClient.get<ProvidersListResponse>('/models/providers', { params }),

  // 创建供应商
  createProvider: (data: CreateProviderRequest) =>
    apiClient.post<ProviderResponse>('/models/providers', data),

  // 获取单个供应商详情
  getProvider: (providerId: number) =>
    apiClient.get<ProviderResponse>(`/models/providers/${providerId}`),

  // 更新供应商
  updateProvider: (providerId: number, data: UpdateProviderRequest) =>
    apiClient.put<ProviderResponse>(`/models/providers/${providerId}`, data),

  // 删除供应商
  deleteProvider: (providerId: number) =>
    apiClient.delete<ApiResponse>(`/models/providers/${providerId}`),

  // 激活供应商
  activateProvider: (providerId: number) =>
    apiClient.post<ProviderResponse>(`/models/providers/${providerId}/activate`),

  // 停用供应商
  deactivateProvider: (providerId: number) =>
    apiClient.post<ProviderResponse>(`/models/providers/${providerId}/deactivate`),

  // 搜索供应商
  searchProviders: (params: SearchProvidersParams) =>
    apiClient.get<ProvidersListResponse>('/models/providers/search', { params }),

  // 获取供应商统计信息
  getProviderStats: () => apiClient.get<ProviderStatsResponse>('/models/providers/stats'),

  // 测试供应商连接
  testProvider: (providerId: number) =>
    apiClient.post<ApiResponse>(`/models/providers/${providerId}/test`),

  // 批量操作供应商
  batchUpdateProviders: (data: {
    provider_ids: number[]
    action: 'activate' | 'deactivate' | 'delete'
  }) => apiClient.post<ApiResponse>('/models/providers/batch', data),

  // 获取供应商关联的模型配置
  getRelatedModels: (providerId: number) =>
    apiClient.get<ApiResponse<Array<{ id: number; name: string; is_active: boolean }>>>(
      `/models/providers/${providerId}/models`,
    ),

  // 获取供应商使用情况
  getProviderUsage: (providerId: number) =>
    apiClient.get<
      ApiResponse<{
        activeConnections: number
        recentRequests: number
        lastUsed?: string
      }>
    >(`/models/providers/${providerId}/usage`),
}

// 便捷的API方法导出
export const {
  listProviders,
  createProvider,
  getProvider,
  updateProvider,
  deleteProvider,
  activateProvider,
  deactivateProvider,
  searchProviders,
  getProviderStats,
  testProvider,
  batchUpdateProviders,
} = providerApi