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
 * 统一的API响应类型定义
 * 确保前后端类型一致性
 */

// 基础API响应接口
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
  error_code?: string // 支持后端异常代码
}

// 分页响应接口
export interface PaginatedApiResponse<T = any> extends ApiResponse<{
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}> {}

// Token相关错误类型
export interface TokenError extends Error {
  code: 'TOKEN_VERSION_MISMATCH' | 'TOKEN_EXPIRED' | 'TOKEN_INVALID' | 'TOKEN_REFRESH_FAILED'
  context?: string
}

// 验证错误类型
export interface ValidationError extends Error {
  field?: string
  code: string
  details?: Record<string, any>
}

// 业务错误类型
export interface BusinessError extends Error {
  code: string
  status?: number
  details?: Record<string, any>
}

// 网络错误类型
export interface NetworkError extends Error {
  code: 'NETWORK_ERROR' | 'TIMEOUT_ERROR' | 'CONNECTION_ERROR'
  status?: number
}

// 统一错误响应接口
export interface ErrorResponse {
  success: false
  error: string
  error_code: string
  message?: string
  details?: Record<string, any>
  timestamp?: string
  request_id?: string
}

// HTTP状态码映射
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const

// 错误代码映射
export const ERROR_CODES = {
  // Token相关错误
  TOKEN_VERSION_MISMATCH: 'TOKEN_VERSION_MISMATCH',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_INVALID: 'TOKEN_INVALID',
  TOKEN_REFRESH_FAILED: 'TOKEN_REFRESH_FAILED',
  
  // 权限相关错误
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',
  ROLE_NOT_FOUND: 'ROLE_NOT_FOUND',
  
  // 用户相关错误
  USER_NOT_FOUND: 'USER_NOT_FOUND',
  USER_ALREADY_EXISTS: 'USER_ALREADY_EXISTS',
  USER_INACTIVE: 'USER_INACTIVE',
  USER_SUSPENDED: 'USER_SUSPENDED',
  
  // 验证相关错误
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',
  MISSING_REQUIRED_FIELD: 'MISSING_REQUIRED_FIELD',
  
  // 业务相关错误
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
  RESOURCE_ALREADY_EXISTS: 'RESOURCE_ALREADY_EXISTS',
  OPERATION_NOT_ALLOWED: 'OPERATION_NOT_ALLOWED',
  
  // 网络相关错误
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  CONNECTION_ERROR: 'CONNECTION_ERROR',
} as const

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES]
export type HttpStatus = typeof HTTP_STATUS[keyof typeof HTTP_STATUS]