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

/**
 * API 模块统一导出
 * 提供模块化和向后兼容的 API 接口
 */

// 导出所有 API 模块
export { authApi } from './authApi'
export { userApi } from './userApi'
export { adminApi } from './adminApi'
export { providerApi } from './providerApi'

// 导出 API 客户端和工具函数
export { apiClient, handleApiError } from '@/utils/apiClient'

// 便捷的API方法导出（向后兼容）
export {
  register,
  login,
  refreshToken,
  logout,
  forgotPassword,
  resetPassword,
  verifyEmail,
  getPublicKey,
} from './authApi'

export { getProfile, updateProfile, changePassword, getUserActivityLogs } from './userApi'

export {
  searchUsers,
  getUserById,
  suspendUser,
  activateUser,
  getAdminStats,
  getAllActivityLogs,
  getSystemHealth,
  getSystemMetrics,
  getSystemResources,
  getDashboardOverview,
  getAuditLogs,
  getAuditStats,
  exportAuditLogs,
} from './adminApi'

export {
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
} from './providerApi'

// 导出类型定义
export type * from '@/types/requests'