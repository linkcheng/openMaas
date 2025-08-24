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