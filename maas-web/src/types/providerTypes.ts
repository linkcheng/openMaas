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

// 供应商基础接口
export interface Provider {
  provider_id: number
  provider_name: string
  provider_type: string
  display_name: string
  description?: string
  base_url: string
  additional_config?: Record<string, any>
  is_active: boolean
  created_by: string
  created_at: string
  updated_by: string
  updated_at: string
}

// 创建供应商请求
export interface CreateProviderRequest {
  provider_name: string
  provider_type: string
  display_name: string
  description?: string
  base_url: string
  api_key?: string
  additional_config?: Record<string, any>
  is_active: boolean
}

// 更新供应商请求
export interface UpdateProviderRequest {
  provider_name?: string
  provider_type?: string
  display_name?: string
  description?: string
  base_url?: string
  api_key?: string
  additional_config?: Record<string, any>
  is_active?: boolean
}

// 查询参数
export interface ListProvidersParams {
  page?: number
  size?: number
  provider_type?: string
  is_active?: boolean
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface SearchProvidersParams {
  page?: number
  size?: number
  keyword?: string
  provider_type?: string
  is_active?: boolean
}

// 分页信息
export interface PaginationInfo {
  page: number
  size: number
  total: number
  pages: number
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

// 表单数据
export interface ProviderFormData {
  provider_name: string
  provider_type: string
  display_name: string
  description: string
  base_url: string
  api_key: string
  additional_config: Record<string, any>
  is_active: boolean
}

// 供应商类型枚举
export enum ProviderType {
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
  AZURE = 'azure',
  BEDROCK = 'bedrock',
  COHERE = 'cohere',
  CUSTOM = 'custom',
}

// 供应商类型选项
export interface ProviderTypeOption {
  value: ProviderType
  label: string
  icon?: string
  description?: string
}

// 状态选项
export interface StatusOption {
  value: string
  label: string
  color?: string
}

// 表单验证规则
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  pattern?: RegExp
  message: string
}

export interface FieldValidationRules {
  [fieldName: string]: ValidationRule[]
}

// 表单错误类型
export interface FormErrors {
  [fieldName: string]: string
}

// 供应商操作类型
export enum ProviderAction {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  ACTIVATE = 'activate',
  DEACTIVATE = 'deactivate',
  VIEW = 'view',
}

// 供应商状态
export enum ProviderStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
}

// 排序选项
export interface SortOption {
  field: string
  order: 'asc' | 'desc'
  label: string
}

// 筛选选项
export interface FilterOptions {
  providerTypes: ProviderTypeOption[]
  statusOptions: StatusOption[]
  sortOptions: SortOption[]
}

// 供应商配置模板
export interface ProviderConfigTemplate {
  provider_type: ProviderType
  required_fields: string[]
  optional_fields: string[]
  default_config: Record<string, any>
  validation_schema: Record<string, ValidationRule[]>
}

// 供应商统计信息
export interface ProviderStats {
  total_providers: number
  active_providers: number
  inactive_providers: number
  providers_by_type: Record<ProviderType, number>
  recent_activity: Array<{
    provider_id: number
    action: ProviderAction
    timestamp: string
  }>
}

// API响应类型
export interface ProviderResponse {
  success: boolean
  data: Provider
  message?: string
}

export interface ProvidersListResponse {
  success: boolean
  data: PaginatedResponse<Provider>
  message?: string
}

export interface ProviderStatsResponse {
  success: boolean
  data: ProviderStats
  message?: string
}

// 错误响应类型
export interface ProviderErrorResponse {
  success: false
  error: string
  details?: Record<string, any>
}

// 供应商图标映射
export const PROVIDER_ICONS: Record<ProviderType, string> = {
  [ProviderType.OPENAI]: '/icons/openai.svg',
  [ProviderType.ANTHROPIC]: '/icons/anthropic.svg',
  [ProviderType.AZURE]: '/icons/azure.svg',
  [ProviderType.BEDROCK]: '/icons/bedrock.svg',
  [ProviderType.COHERE]: '/icons/cohere.svg',
  [ProviderType.CUSTOM]: '/icons/custom.svg',
}

// 供应商类型选项常量
export const PROVIDER_TYPE_OPTIONS: ProviderTypeOption[] = [
  {
    value: ProviderType.OPENAI,
    label: 'OpenAI',
    icon: PROVIDER_ICONS[ProviderType.OPENAI],
    description: 'OpenAI GPT models',
  },
  {
    value: ProviderType.ANTHROPIC,
    label: 'Anthropic',
    icon: PROVIDER_ICONS[ProviderType.ANTHROPIC],
    description: 'Anthropic Claude models',
  },
  {
    value: ProviderType.AZURE,
    label: 'Azure OpenAI',
    icon: PROVIDER_ICONS[ProviderType.AZURE],
    description: 'Microsoft Azure OpenAI Service',
  },
  {
    value: ProviderType.BEDROCK,
    label: 'Amazon Bedrock',
    icon: PROVIDER_ICONS[ProviderType.BEDROCK],
    description: 'Amazon Bedrock foundation models',
  },
  {
    value: ProviderType.COHERE,
    label: 'Cohere',
    icon: PROVIDER_ICONS[ProviderType.COHERE],
    description: 'Cohere language models',
  },
  {
    value: ProviderType.CUSTOM,
    label: '自定义',
    icon: PROVIDER_ICONS[ProviderType.CUSTOM],
    description: 'Custom provider implementation',
  },
]

// 状态选项常量
export const STATUS_OPTIONS: StatusOption[] = [
  {
    value: ProviderStatus.ACTIVE,
    label: '激活',
    color: 'green',
  },
  {
    value: ProviderStatus.INACTIVE,
    label: '停用',
    color: 'gray',
  },
]

// 排序选项常量
export const SORT_OPTIONS: SortOption[] = [
  {
    field: 'created_at',
    order: 'desc',
    label: '创建时间（最新）',
  },
  {
    field: 'created_at',
    order: 'asc',
    label: '创建时间（最早）',
  },
  {
    field: 'display_name',
    order: 'asc',
    label: '名称（A-Z）',
  },
  {
    field: 'display_name',
    order: 'desc',
    label: '名称（Z-A）',
  },
  {
    field: 'provider_type',
    order: 'asc',
    label: '类型',
  },
]

// 表单验证规则常量
export const PROVIDER_VALIDATION_RULES: FieldValidationRules = {
  provider_name: [
    { required: true, message: '供应商名称不能为空' },
    { min: 1, max: 64, message: '供应商名称长度应在1-64个字符之间' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '供应商名称只能包含字母、数字、下划线和连字符' },
  ],
  display_name: [
    { required: true, message: '显示名称不能为空' },
    { min: 1, max: 128, message: '显示名称长度应在1-128个字符之间' },
  ],
  provider_type: [{ required: true, message: '请选择供应商类型' }],
  base_url: [
    { required: true, message: 'API基础URL不能为空' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的URL地址' },
  ],
  description: [{ max: 1000, message: '描述长度不能超过1000个字符' }],
}

// 默认配置模板
export const PROVIDER_CONFIG_TEMPLATES: Record<ProviderType, ProviderConfigTemplate> = {
  [ProviderType.OPENAI]: {
    provider_type: ProviderType.OPENAI,
    required_fields: ['api_key'],
    optional_fields: ['organization', 'timeout', 'max_retries'],
    default_config: {
      timeout: 30,
      max_retries: 3,
    },
    validation_schema: {
      api_key: [{ required: true, message: 'API密钥不能为空' }],
      timeout: [{ min: 1, max: 300, message: '超时时间应在1-300秒之间' }],
      max_retries: [{ min: 0, max: 10, message: '重试次数应在0-10次之间' }],
    },
  },
  [ProviderType.ANTHROPIC]: {
    provider_type: ProviderType.ANTHROPIC,
    required_fields: ['api_key'],
    optional_fields: ['timeout', 'max_retries'],
    default_config: {
      timeout: 30,
      max_retries: 3,
    },
    validation_schema: {
      api_key: [{ required: true, message: 'API密钥不能为空' }],
      timeout: [{ min: 1, max: 300, message: '超时时间应在1-300秒之间' }],
      max_retries: [{ min: 0, max: 10, message: '重试次数应在0-10次之间' }],
    },
  },
  [ProviderType.AZURE]: {
    provider_type: ProviderType.AZURE,
    required_fields: ['api_key', 'api_version'],
    optional_fields: ['timeout', 'max_retries'],
    default_config: {
      api_version: '2023-12-01-preview',
      timeout: 30,
      max_retries: 3,
    },
    validation_schema: {
      api_key: [{ required: true, message: 'API密钥不能为空' }],
      api_version: [{ required: true, message: 'API版本不能为空' }],
      timeout: [{ min: 1, max: 300, message: '超时时间应在1-300秒之间' }],
      max_retries: [{ min: 0, max: 10, message: '重试次数应在0-10次之间' }],
    },
  },
  [ProviderType.BEDROCK]: {
    provider_type: ProviderType.BEDROCK,
    required_fields: ['aws_access_key_id', 'aws_secret_access_key', 'region'],
    optional_fields: ['timeout', 'max_retries'],
    default_config: {
      region: 'us-east-1',
      timeout: 30,
      max_retries: 3,
    },
    validation_schema: {
      aws_access_key_id: [{ required: true, message: 'AWS Access Key ID不能为空' }],
      aws_secret_access_key: [{ required: true, message: 'AWS Secret Access Key不能为空' }],
      region: [{ required: true, message: 'AWS区域不能为空' }],
      timeout: [{ min: 1, max: 300, message: '超时时间应在1-300秒之间' }],
      max_retries: [{ min: 0, max: 10, message: '重试次数应在0-10次之间' }],
    },
  },
  [ProviderType.COHERE]: {
    provider_type: ProviderType.COHERE,
    required_fields: ['api_key'],
    optional_fields: ['timeout', 'max_retries'],
    default_config: {
      timeout: 30,
      max_retries: 3,
    },
    validation_schema: {
      api_key: [{ required: true, message: 'API密钥不能为空' }],
      timeout: [{ min: 1, max: 300, message: '超时时间应在1-300秒之间' }],
      max_retries: [{ min: 0, max: 10, message: '重试次数应在0-10次之间' }],
    },
  },
  [ProviderType.CUSTOM]: {
    provider_type: ProviderType.CUSTOM,
    required_fields: [],
    optional_fields: ['timeout', 'max_retries'],
    default_config: {
      timeout: 30,
      max_retries: 3,
    },
    validation_schema: {
      timeout: [{ min: 1, max: 300, message: '超时时间应在1-300秒之间' }],
      max_retries: [{ min: 0, max: 10, message: '重试次数应在0-10次之间' }],
    },
  },
}
