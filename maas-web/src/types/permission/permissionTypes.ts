/**
 * 权限相关类型定义
 * Permission-related type definitions for permission management
 */

/**
 * 权限状态枚举
 */
export type PermissionStatus = 'active' | 'inactive' | 'deprecated'

/**
 * 权限操作类型枚举
 */
export type PermissionAction = 'create' | 'read' | 'update' | 'delete' | 'manage' | 'view' | 'execute'

/**
 * 权限资源类型枚举
 */
export type PermissionResource = 
  | 'user' 
  | 'role' 
  | 'permission' 
  | 'provider' 
  | 'model' 
  | 'chat' 
  | 'system' 
  | 'menu'
  | 'audit'
  | 'config'

/**
 * 权限模块枚举
 */
export type PermissionModule = 
  | 'user_management'
  | 'permission_management' 
  | 'provider_management'
  | 'model_management'
  | 'chat_management'
  | 'system_management'
  | 'audit_management'

/**
 * 权限基础信息接口
 */
export interface Permission {
  /** 权限ID */
  id: string
  /** 权限名称（唯一标识，格式：resource.action） */
  name: string
  /** 权限显示名称 */
  display_name: string
  /** 权限描述 */
  description?: string
  /** 资源类型 */
  resource: PermissionResource
  /** 操作类型 */
  action: PermissionAction
  /** 所属模块 */
  module: PermissionModule
  /** 权限状态 */
  status: PermissionStatus
  /** 是否为系统权限 */
  is_system_permission: boolean
  /** 父权限ID（用于权限层级） */
  parent_id?: string
  /** 子权限列表 */
  children?: Permission[]
  /** 权限级别（数字越大权限越高） */
  level: number
  /** 创建时间 */
  created_at: string
  /** 更新时间 */
  updated_at: string
  /** 创建者ID */
  created_by?: string
}

/**
 * 权限创建请求接口
 */
export interface CreatePermissionRequest {
  /** 权限名称 */
  name: string
  /** 权限显示名称 */
  display_name: string
  /** 权限描述 */
  description?: string
  /** 资源类型 */
  resource: PermissionResource
  /** 操作类型 */
  action: PermissionAction
  /** 所属模块 */
  module: PermissionModule
  /** 父权限ID */
  parent_id?: string
  /** 权限级别 */
  level?: number
}

/**
 * 权限更新请求接口
 */
export interface UpdatePermissionRequest {
  /** 权限显示名称 */
  display_name?: string
  /** 权限描述 */
  description?: string
  /** 权限状态 */
  status?: PermissionStatus
  /** 权限级别 */
  level?: number
}

/**
 * 权限查询参数接口
 */
export interface PermissionQueryParams {
  /** 搜索关键词 */
  search?: string
  /** 资源类型筛选 */
  resource?: PermissionResource
  /** 操作类型筛选 */
  action?: PermissionAction
  /** 模块筛选 */
  module?: PermissionModule
  /** 权限状态筛选 */
  status?: PermissionStatus
  /** 是否只显示系统权限 */
  system_only?: boolean
  /** 父权限ID筛选 */
  parent_id?: string
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
 * 权限树节点接口
 */
export interface PermissionTreeNode {
  /** 权限信息 */
  permission: Permission
  /** 子节点 */
  children: PermissionTreeNode[]
  /** 是否展开 */
  expanded?: boolean
  /** 是否选中 */
  selected?: boolean
  /** 是否禁用 */
  disabled?: boolean
  /** 节点层级 */
  level: number
}

/**
 * 权限树显示节点类型
 */
export type PermissionTreeDisplayNodeType = 'module' | 'resource' | 'permission'

/**
 * 权限树显示节点接口（用于组件显示）
 */
export interface PermissionTreeDisplayNode {
  id: string
  name: string
  display_name: string
  description?: string
  type: PermissionTreeDisplayNodeType
  module?: string
  resource?: string
  action?: string
  created_at?: string
  children?: PermissionTreeDisplayNode[]
  disabled?: boolean
}

/**
 * 权限验证结果接口
 */
export interface PermissionCheckResult {
  /** 是否有权限 */
  hasPermission: boolean
  /** 缺失的权限列表 */
  missingPermissions?: string[]
  /** 验证消息 */
  message?: string
}

/**
 * 权限统计信息接口
 */
export interface PermissionStats {
  /** 总权限数 */
  total_permissions: number
  /** 系统权限数 */
  system_permissions: number
  /** 自定义权限数 */
  custom_permissions: number
  /** 按模块分组的权限数 */
  permissions_by_module: Record<PermissionModule, number>
  /** 按资源分组的权限数 */
  permissions_by_resource: Record<PermissionResource, number>
  /** 最近创建的权限 */
  recent_permissions: Permission[]
}

/**
 * 批量权限操作请求接口
 */
export interface BatchPermissionRequest {
  /** 权限ID列表 */
  permission_ids: string[]
  /** 操作类型 */
  action: 'activate' | 'deactivate' | 'delete'
}

/**
 * 权限依赖关系接口
 */
export interface PermissionDependency {
  /** 权限ID */
  permission_id: string
  /** 依赖的权限ID列表 */
  depends_on: string[]
  /** 被依赖的权限ID列表 */
  required_by: string[]
}