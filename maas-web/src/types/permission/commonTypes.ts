/**
 * 权限管理通用类型定义
 * Common type definitions for permission management
 */

/**
 * API响应基础接口
 */
export interface ApiResponse<T = any> {
  /** 请求是否成功 */
  success: boolean
  /** 响应数据 */
  data?: T
  /** 错误信息 */
  error?: string
  /** 响应消息 */
  message?: string
  /** 响应状态码 */
  code?: number
  /** 请求ID（用于追踪） */
  request_id?: string
  /** 响应时间戳 */
  timestamp?: string
}

/**
 * 分页响应接口
 */
export interface PaginatedResponse<T> {
  /** 数据项列表 */
  items: T[]
  /** 总记录数 */
  total: number
  /** 当前页码 */
  page: number
  /** 每页数量 */
  page_size: number
  /** 总页数 */
  total_pages: number
  /** 是否有下一页 */
  has_next: boolean
  /** 是否有上一页 */
  has_prev: boolean
  /** 下一页页码 */
  next_page?: number
  /** 上一页页码 */
  prev_page?: number
}

/**
 * 分页请求参数接口
 */
export interface PaginationParams {
  /** 页码（从1开始） */
  page?: number
  /** 每页数量 */
  page_size?: number
  /** 排序字段 */
  sort_by?: string
  /** 排序方向 */
  sort_order?: 'asc' | 'desc'
}

/**
 * 搜索参数接口
 */
export interface SearchParams {
  /** 搜索关键词 */
  search?: string
  /** 搜索字段 */
  search_fields?: string[]
  /** 是否精确匹配 */
  exact_match?: boolean
  /** 是否区分大小写 */
  case_sensitive?: boolean
}

/**
 * 筛选参数接口
 */
export interface FilterParams {
  /** 筛选条件 */
  filters?: Record<string, any>
  /** 日期范围筛选 */
  date_range?: {
    start_date?: string
    end_date?: string
    field?: string
  }
  /** 状态筛选 */
  status?: string[]
  /** 标签筛选 */
  tags?: string[]
}

/**
 * 查询参数基础接口
 */
export interface BaseQueryParams extends PaginationParams, SearchParams, FilterParams {
  /** 包含的关联数据 */
  include?: string[]
  /** 排除的字段 */
  exclude?: string[]
  /** 字段选择 */
  fields?: string[]
}

/**
 * 批量操作请求接口
 */
export interface BatchOperationRequest<T = any> {
  /** 操作的ID列表 */
  ids: string[]
  /** 操作类型 */
  operation: string
  /** 操作参数 */
  params?: T
  /** 是否强制执行 */
  force?: boolean
}

/**
 * 批量操作结果接口
 */
export interface BatchOperationResult {
  /** 操作是否成功 */
  success: boolean
  /** 成功处理的数量 */
  success_count: number
  /** 失败处理的数量 */
  failed_count: number
  /** 跳过处理的数量 */
  skipped_count: number
  /** 成功的ID列表 */
  success_ids: string[]
  /** 失败的ID列表 */
  failed_ids: string[]
  /** 错误信息列表 */
  errors?: Array<{
    id: string
    error: string
  }>
  /** 警告信息列表 */
  warnings?: Array<{
    id: string
    warning: string
  }>
}

/**
 * 操作日志接口
 */
export interface OperationLog {
  /** 日志ID */
  id: string
  /** 操作类型 */
  operation: string
  /** 操作对象类型 */
  target_type: string
  /** 操作对象ID */
  target_id: string
  /** 操作者ID */
  operator_id: string
  /** 操作者信息 */
  operator: {
    id: string
    username: string
    display_name: string
  }
  /** 操作描述 */
  description: string
  /** 操作前数据 */
  before_data?: Record<string, any>
  /** 操作后数据 */
  after_data?: Record<string, any>
  /** 操作结果 */
  result: 'success' | 'failed' | 'partial'
  /** 错误信息 */
  error_message?: string
  /** 操作时间 */
  created_at: string
  /** 客户端IP */
  client_ip?: string
  /** 用户代理 */
  user_agent?: string
}

/**
 * 用户基础信息接口
 */
export interface UserInfo {
  /** 用户ID */
  id: string
  /** 用户名 */
  username: string
  /** 邮箱 */
  email: string
  /** 用户资料 */
  profile: {
    /** 全名 */
    full_name: string
    /** 头像URL */
    avatar_url?: string
    /** 部门 */
    department?: string
    /** 职位 */
    position?: string
  }
  /** 用户状态 */
  status: 'active' | 'inactive' | 'locked' | 'deleted'
  /** 最后登录时间 */
  last_login_at?: string
  /** 创建时间 */
  created_at: string
}

/**
 * 用户角色关联接口
 */
export interface UserRole {
  /** 用户ID */
  user_id: string
  /** 用户信息 */
  user: UserInfo
  /** 角色列表 */
  roles: Role[]
  /** 分配时间 */
  assigned_at: string
  /** 分配者ID */
  assigned_by: string
  /** 分配者信息 */
  assigned_by_user?: UserInfo
  /** 过期时间 */
  expires_at?: string
  /** 是否活跃 */
  is_active: boolean
}

/**
 * 错误详情接口
 */
export interface ErrorDetail {
  /** 错误代码 */
  code: string
  /** 错误消息 */
  message: string
  /** 错误字段 */
  field?: string
  /** 错误详细信息 */
  details?: Record<string, any>
}

/**
 * 验证错误接口
 */
export interface ValidationError {
  /** 字段名 */
  field: string
  /** 错误消息 */
  message: string
  /** 错误代码 */
  code: string
  /** 拒绝的值 */
  rejected_value?: any
}

/**
 * 表单验证结果接口
 */
export interface FormValidationResult {
  /** 验证是否通过 */
  valid: boolean
  /** 验证错误列表 */
  errors: ValidationError[]
  /** 警告信息列表 */
  warnings?: ValidationError[]
}

/**
 * 导出配置接口
 */
export interface ExportConfig {
  /** 导出格式 */
  format: 'json' | 'csv' | 'excel'
  /** 导出字段 */
  fields?: string[]
  /** 筛选条件 */
  filters?: Record<string, any>
  /** 是否包含关联数据 */
  include_relations?: boolean
  /** 文件名 */
  filename?: string
}

/**
 * 导入配置接口
 */
export interface ImportConfig {
  /** 导入格式 */
  format: 'json' | 'csv' | 'excel'
  /** 字段映射 */
  field_mapping?: Record<string, string>
  /** 导入模式 */
  mode: 'create' | 'update' | 'upsert'
  /** 是否跳过错误 */
  skip_errors?: boolean
  /** 是否验证数据 */
  validate_data?: boolean
}

// 重新导出角色和权限类型以避免循环依赖
import type { Role } from './roleTypes'
import type { Permission } from './permissionTypes'

export type { Role, Permission }