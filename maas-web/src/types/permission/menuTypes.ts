/**
 * 菜单权限配置相关类型定义
 * Menu permission configuration type definitions
 */

import type { Permission } from './permissionTypes'

/**
 * 权限逻辑类型枚举
 */
export type PermissionLogic = 'AND' | 'OR'

/**
 * 菜单类型枚举
 */
export type MenuType = 'menu' | 'button' | 'tab' | 'section'

/**
 * 菜单状态枚举
 */
export type MenuStatus = 'visible' | 'hidden' | 'disabled'

/**
 * 菜单权限配置接口
 */
export interface MenuPermissionConfig {
  /** 配置ID */
  id: string
  /** 菜单唯一标识 */
  menu_key: string
  /** 菜单名称 */
  menu_name: string
  /** 菜单路径 */
  menu_path: string
  /** 菜单图标 */
  menu_icon?: string
  /** 父菜单标识 */
  parent_key?: string
  /** 菜单类型 */
  menu_type: MenuType
  /** 所需权限名称列表 */
  required_permissions: string[]
  /** 权限逻辑（AND/OR） */
  permission_logic: PermissionLogic
  /** 是否可见 */
  is_visible: boolean
  /** 菜单状态 */
  status: MenuStatus
  /** 排序顺序 */
  sort_order: number
  /** 子菜单配置 */
  children?: MenuPermissionConfig[]
  /** 菜单层级 */
  level: number
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
 * 菜单权限配置创建请求接口
 */
export interface CreateMenuConfigRequest {
  /** 菜单唯一标识 */
  menu_key: string
  /** 菜单名称 */
  menu_name: string
  /** 菜单路径 */
  menu_path: string
  /** 菜单图标 */
  menu_icon?: string
  /** 父菜单标识 */
  parent_key?: string
  /** 菜单类型 */
  menu_type: MenuType
  /** 所需权限名称列表 */
  required_permissions: string[]
  /** 权限逻辑 */
  permission_logic: PermissionLogic
  /** 是否可见 */
  is_visible: boolean
  /** 排序顺序 */
  sort_order: number
}

/**
 * 菜单权限配置更新请求接口
 */
export interface UpdateMenuConfigRequest {
  /** 菜单名称 */
  menu_name?: string
  /** 菜单路径 */
  menu_path?: string
  /** 菜单图标 */
  menu_icon?: string
  /** 所需权限名称列表 */
  required_permissions?: string[]
  /** 权限逻辑 */
  permission_logic?: PermissionLogic
  /** 是否可见 */
  is_visible?: boolean
  /** 菜单状态 */
  status?: MenuStatus
  /** 排序顺序 */
  sort_order?: number
}

/**
 * 菜单树节点接口
 */
export interface MenuTreeNode {
  /** 菜单配置 */
  config: MenuPermissionConfig
  /** 子节点 */
  children: MenuTreeNode[]
  /** 是否展开 */
  expanded?: boolean
  /** 是否选中 */
  selected?: boolean
  /** 是否可拖拽 */
  draggable?: boolean
  /** 节点层级 */
  level: number
  /** 是否有权限访问 */
  hasPermission?: boolean
}

/**
 * 菜单权限验证结果接口
 */
export interface MenuPermissionResult {
  /** 菜单标识 */
  menu_key: string
  /** 是否有权限 */
  hasPermission: boolean
  /** 是否可见 */
  isVisible: boolean
  /** 缺失的权限 */
  missingPermissions?: string[]
  /** 验证消息 */
  message?: string
}

/**
 * 菜单配置导入导出接口
 */
export interface MenuConfigExport {
  /** 导出版本 */
  version: string
  /** 导出时间 */
  exported_at: string
  /** 菜单配置列表 */
  configs: MenuPermissionConfig[]
  /** 导出者信息 */
  exported_by?: string
  /** 导出描述 */
  description?: string
}

/**
 * 菜单配置导入请求接口
 */
export interface MenuConfigImportRequest {
  /** 配置数据 */
  configs: Omit<MenuPermissionConfig, 'id' | 'created_at' | 'updated_at'>[]
  /** 导入模式 */
  import_mode: 'merge' | 'replace' | 'append'
  /** 是否覆盖现有配置 */
  overwrite_existing?: boolean
}

/**
 * 菜单配置导入结果接口
 */
export interface MenuConfigImportResult {
  /** 导入是否成功 */
  success: boolean
  /** 导入的配置数量 */
  imported_count: number
  /** 跳过的配置数量 */
  skipped_count: number
  /** 失败的配置数量 */
  failed_count: number
  /** 错误信息列表 */
  errors?: string[]
  /** 警告信息列表 */
  warnings?: string[]
  /** 导入的配置ID列表 */
  imported_ids?: string[]
}

/**
 * 菜单预览配置接口
 */
export interface MenuPreviewConfig {
  /** 角色ID */
  role_id: string
  /** 用户ID（可选，用于用户特定预览） */
  user_id?: string
  /** 预览模式 */
  preview_mode: 'role' | 'user' | 'combined'
  /** 是否显示权限信息 */
  show_permission_info?: boolean
  /** 是否显示隐藏菜单 */
  show_hidden_menus?: boolean
}

/**
 * 菜单预览结果接口
 */
export interface MenuPreviewResult {
  /** 可见的菜单列表 */
  visible_menus: MenuTreeNode[]
  /** 隐藏的菜单列表 */
  hidden_menus: MenuTreeNode[]
  /** 权限验证结果 */
  permission_results: MenuPermissionResult[]
  /** 预览统计 */
  stats: {
    total_menus: number
    visible_count: number
    hidden_count: number
    permission_denied_count: number
  }
}

/**
 * 菜单查询参数接口
 */
export interface MenuQueryParams {
  /** 搜索关键词 */
  search?: string
  /** 菜单类型筛选 */
  menu_type?: MenuType
  /** 菜单状态筛选 */
  status?: MenuStatus
  /** 父菜单筛选 */
  parent_key?: string
  /** 是否只显示根菜单 */
  root_only?: boolean
  /** 权限筛选 */
  permission?: string
  /** 排序字段 */
  sort_by?: string
  /** 排序方向 */
  sort_order?: 'asc' | 'desc'
}

/**
 * 菜单拖拽操作接口
 */
export interface MenuDragOperation {
  /** 被拖拽的菜单标识 */
  source_menu_key: string
  /** 目标菜单标识 */
  target_menu_key: string
  /** 拖拽类型 */
  drop_type: 'before' | 'after' | 'inner'
  /** 新的排序顺序 */
  new_sort_order: number
  /** 新的父菜单标识 */
  new_parent_key?: string
}

/**
 * 菜单批量操作请求接口
 */
export interface BatchMenuOperationRequest {
  /** 菜单标识列表 */
  menu_keys: string[]
  /** 操作类型 */
  operation: 'show' | 'hide' | 'enable' | 'disable' | 'delete'
  /** 操作参数 */
  params?: Record<string, any>
}