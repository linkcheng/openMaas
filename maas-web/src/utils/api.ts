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
 * @deprecated 此文件已被重构为模块化架构，请使用新的 API 模块
 * 
 * 新的使用方式:
 * import { authApi, userApi, adminApi, providerApi } from '@/api'
 * 或者
 * import { login, getProfile } from '@/api'
 * 
 * 此文件保留用于向后兼容，但建议逐步迁移到新的模块化 API
 */

// 重新导出新的 API 模块以保持向后兼容
export * from '@/api'

// 重新导出 API 客户端
export { apiClient, handleApiError } from '@/utils/apiClient'

// 重新导出类型定义
export type * from '@/types/requests'
export type * from '@/types/api'
