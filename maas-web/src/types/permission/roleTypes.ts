/**
 * 角色相关类型定义
 * Role-related type definitions for permission management
 */

/**
 * 角色类型枚举
 */
export type RoleType = 'system' | 'custom'

/**
 * 角色状态枚举
 */
export type RoleStatus = 'active' | 'inactive' | 'deleted'

/**
 * 角色基础信息接口
 */
export interface Role {
  /** 角色ID */
  id: string
  /** 角色名称（唯一标识） */
  name: string
  /** 角色显示名称 */
  display_name: string
  /** 角色描述 */
  description?: string
  /** 角色类型 */
  role_type: RoleType
  /** 是否为系统角色 */
  is_system_role: boolean
  /** 角色状态 */
  status: RoleStatus
  /** 关联的权限列表 */
  permissions: Permission[]
  /** 拥有此角色的用户数量 */
  user_count?: number
  /** 创建时间 */
  created_at: string
  /** 更新时间 */
  updated_at: string
  /** 创建者ID */
  created_by?: string
  /** 更新者ID */
  updated_by?: string
}

/**
 * 角色创建请求接口
 */
export interface CreateRoleRequest {
  /** 角色名称 */
  name: string
  /** 角色显示名称 */
  display_name: string
  /** 角色描述 */
  description?: string
  /** 角色类型 */
  role_type: RoleType
  /** 初始权限ID列表 */
  permission_ids?: string[]
}

/**
 * 角色更新请求接口
 */
export interface UpdateRoleRequest {
  /** 角色显示名称 */
  display_name?: string
  /** 角色描述 */
  description?: string
  /** 角色状态 */
  status?: RoleStatus
}

/**
 * 角色权限分配请求接口
 */
export interface RolePermissionAssignRequest {
  /** 权限ID列表 */
  permission_ids: string[]
}

/**
 * 角色查询参数接口
 */
export interface RoleQueryParams {
  /** 搜索关键词 */
  search?: string
  /** 角色类型筛选 */
  role_type?: RoleType
  /** 角色状态筛选 */
  status?: RoleStatus
  /** 页码 */
  page?: number
  /** 每页数量 */
  page_size?: number
  /** 排序字段 */
  sort_by?: string
  /** 排序方向 */
  sort_order?: 'asc' | 'desc'
}

/**
 * 角色统计信息接口
 */
export interface RoleStats {
  /** 总角色数 */
  total_roles: number
  /** 系统角色数 */
  system_roles: number
  /** 自定义角色数 */
  custom_roles: number
  /** 活跃角色数 */
  active_roles: number
  /** 最近创建的角色 */
  recent_roles: Role[]
}

// 导入权限类型（避免循环依赖，使用类型导入）
import type { Permission } from './permissionTypes'