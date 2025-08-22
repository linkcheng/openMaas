/**
 * 权限管理工具函数
 * Permission management utility functions
 */

import type {
  Permission,
  PermissionTreeNode,
  PermissionCheckResult,
  Role,
  MenuPermissionConfig,
  MenuTreeNode,
  MenuPermissionResult,
  MenuConfigExport,
  MenuConfigImportRequest,
  PermissionLogic,
} from '../types/permission'

/**
 * 权限名称验证正则表达式
 * 格式: resource.action 或 resource.subresource.action
 */
const PERMISSION_NAME_REGEX = /^[a-z_]+(\.[a-z_]+)*\.[a-z_]+$/

/**
 * 菜单键名验证正则表达式
 * 格式: menu_key 或 parent.child
 */
const MENU_KEY_REGEX = /^[a-z_]+(\.[a-z_]+)*$/

/**
 * 验证权限名称格式
 * @param permissionName 权限名称
 * @returns 是否符合格式要求
 */
export function validatePermissionName(permissionName: string): boolean {
  if (!permissionName || typeof permissionName !== 'string') {
    return false
  }
  
  return PERMISSION_NAME_REGEX.test(permissionName)
}

/**
 * 格式化权限名称
 * @param resource 资源类型
 * @param action 操作类型
 * @param subResource 子资源（可选）
 * @returns 格式化后的权限名称
 */
export function formatPermissionName(
  resource: string,
  action: string,
  subResource?: string
): string {
  const parts = [resource]
  if (subResource) {
    parts.push(subResource)
  }
  parts.push(action)
  
  return parts.join('.')
}

/**
 * 解析权限名称
 * @param permissionName 权限名称
 * @returns 解析后的权限组件
 */
export function parsePermissionName(permissionName: string): {
  resource: string
  action: string
  subResource?: string
} | null {
  if (!validatePermissionName(permissionName)) {
    return null
  }
  
  const parts = permissionName.split('.')
  const action = parts.pop()!
  const resource = parts.shift()!
  const subResource = parts.length > 0 ? parts.join('.') : undefined
  
  return {
    resource,
    action,
    subResource,
  }
}

/**
 * 检查用户是否拥有指定权限
 * @param userPermissions 用户权限列表
 * @param requiredPermission 需要的权限
 * @returns 权限检查结果
 */
export function checkPermission(
  userPermissions: string[],
  requiredPermission: string
): PermissionCheckResult {
  const hasPermission = userPermissions.includes(requiredPermission)
  
  return {
    hasPermission,
    missingPermissions: hasPermission ? undefined : [requiredPermission],
    message: hasPermission ? '权限验证通过' : `缺少权限: ${requiredPermission}`,
  }
}

/**
 * 检查用户是否拥有多个权限（支持AND/OR逻辑）
 * @param userPermissions 用户权限列表
 * @param requiredPermissions 需要的权限列表
 * @param logic 权限逻辑（AND/OR）
 * @returns 权限检查结果
 */
export function checkMultiplePermissions(
  userPermissions: string[],
  requiredPermissions: string[],
  logic: PermissionLogic = 'AND'
): PermissionCheckResult {
  if (requiredPermissions.length === 0) {
    return {
      hasPermission: true,
      message: '无需权限验证',
    }
  }
  
  const missingPermissions = requiredPermissions.filter(
    permission => !userPermissions.includes(permission)
  )
  
  let hasPermission: boolean
  let message: string
  
  if (logic === 'AND') {
    hasPermission = missingPermissions.length === 0
    message = hasPermission 
      ? '权限验证通过' 
      : `缺少权限: ${missingPermissions.join(', ')}`
  } else {
    hasPermission = missingPermissions.length < requiredPermissions.length
    message = hasPermission 
      ? '权限验证通过' 
      : `需要以下任一权限: ${requiredPermissions.join(', ')}`
  }
  
  return {
    hasPermission,
    missingPermissions: hasPermission ? undefined : missingPermissions,
    message,
  }
}

/**
 * 将权限列表转换为树形结构
 * @param permissions 权限列表
 * @returns 权限树节点列表
 */
export function buildPermissionTree(permissions: Permission[]): PermissionTreeNode[] {
  const permissionMap = new Map<string, Permission>()
  const rootNodes: PermissionTreeNode[] = []
  const nodeMap = new Map<string, PermissionTreeNode>()
  
  // 创建权限映射
  permissions.forEach(permission => {
    permissionMap.set(permission.id, permission)
  })
  
  // 创建树节点
  permissions.forEach(permission => {
    const node: PermissionTreeNode = {
      permission,
      children: [],
      expanded: false,
      selected: false,
      disabled: false,
      level: permission.level || 1,
    }
    
    nodeMap.set(permission.id, node)
    
    if (permission.parent_id && nodeMap.has(permission.parent_id)) {
      // 添加到父节点
      const parentNode = nodeMap.get(permission.parent_id)!
      parentNode.children.push(node)
    } else {
      // 根节点
      rootNodes.push(node)
    }
  })
  
  // 按模块和名称排序
  const sortNodes = (nodes: PermissionTreeNode[]) => {
    nodes.sort((a, b) => {
      // 先按模块排序
      if (a.permission.module !== b.permission.module) {
        return a.permission.module.localeCompare(b.permission.module)
      }
      // 再按名称排序
      return a.permission.name.localeCompare(b.permission.name)
    })
    
    // 递归排序子节点
    nodes.forEach(node => {
      if (node.children.length > 0) {
        sortNodes(node.children)
      }
    })
  }
  
  sortNodes(rootNodes)
  return rootNodes
}

/**
 * 在权限树中搜索权限
 * @param nodes 权限树节点
 * @param searchQuery 搜索关键词
 * @returns 匹配的权限节点
 */
export function searchPermissionTree(
  nodes: PermissionTreeNode[],
  searchQuery: string
): PermissionTreeNode[] {
  if (!searchQuery.trim()) {
    return nodes
  }
  
  const query = searchQuery.toLowerCase()
  const matchedNodes: PermissionTreeNode[] = []
  
  const searchNode = (node: PermissionTreeNode): boolean => {
    const permission = node.permission
    const matches = 
      permission.name.toLowerCase().includes(query) ||
      permission.display_name.toLowerCase().includes(query) ||
      (permission.description && permission.description.toLowerCase().includes(query))
    
    // 搜索子节点
    const matchedChildren = node.children.filter(searchNode)
    
    if (matches || matchedChildren.length > 0) {
      const matchedNode: PermissionTreeNode = {
        ...node,
        children: matchedChildren,
        expanded: matchedChildren.length > 0, // 如果有匹配的子节点，展开节点
      }
      matchedNodes.push(matchedNode)
      return true
    }
    
    return false
  }
  
  nodes.forEach(searchNode)
  return matchedNodes
}

/**
 * 获取权限的所有父权限
 * @param permission 权限对象
 * @param allPermissions 所有权限列表
 * @returns 父权限列表
 */
export function getPermissionAncestors(
  permission: Permission,
  allPermissions: Permission[]
): Permission[] {
  const ancestors: Permission[] = []
  const permissionMap = new Map(allPermissions.map(p => [p.id, p]))
  
  let currentPermission = permission
  while (currentPermission.parent_id) {
    const parent = permissionMap.get(currentPermission.parent_id)
    if (parent) {
      ancestors.unshift(parent)
      currentPermission = parent
    } else {
      break
    }
  }
  
  return ancestors
}

/**
 * 获取权限的所有子权限
 * @param permission 权限对象
 * @param allPermissions 所有权限列表
 * @returns 子权限列表
 */
export function getPermissionDescendants(
  permission: Permission,
  allPermissions: Permission[]
): Permission[] {
  const descendants: Permission[] = []
  const children = allPermissions.filter(p => p.parent_id === permission.id)
  
  children.forEach(child => {
    descendants.push(child)
    descendants.push(...getPermissionDescendants(child, allPermissions))
  })
  
  return descendants
}

/**
 * 验证菜单键名格式
 * @param menuKey 菜单键名
 * @returns 是否符合格式要求
 */
export function validateMenuKey(menuKey: string): boolean {
  if (!menuKey || typeof menuKey !== 'string') {
    return false
  }
  
  return MENU_KEY_REGEX.test(menuKey)
}

/**
 * 将菜单配置列表转换为树形结构
 * @param configs 菜单配置列表
 * @returns 菜单树节点列表
 */
export function buildMenuTree(configs: MenuPermissionConfig[]): MenuTreeNode[] {
  const configMap = new Map<string, MenuPermissionConfig>()
  const rootNodes: MenuTreeNode[] = []
  const nodeMap = new Map<string, MenuTreeNode>()
  
  // 创建配置映射
  configs.forEach(config => {
    configMap.set(config.menu_key, config)
  })
  
  // 创建树节点
  configs.forEach(config => {
    const node: MenuTreeNode = {
      config,
      children: [],
      expanded: false,
      selected: false,
      draggable: true,
      level: config.level || 1,
      hasPermission: true, // 默认有权限，实际使用时需要根据用户权限计算
    }
    
    nodeMap.set(config.menu_key, node)
    
    if (config.parent_key && nodeMap.has(config.parent_key)) {
      // 添加到父节点
      const parentNode = nodeMap.get(config.parent_key)!
      parentNode.children.push(node)
    } else {
      // 根节点
      rootNodes.push(node)
    }
  })
  
  // 按排序顺序排序
  const sortNodes = (nodes: MenuTreeNode[]) => {
    nodes.sort((a, b) => a.config.sort_order - b.config.sort_order)
    
    // 递归排序子节点
    nodes.forEach(node => {
      if (node.children.length > 0) {
        sortNodes(node.children)
      }
    })
  }
  
  sortNodes(rootNodes)
  return rootNodes
}

/**
 * 验证菜单权限
 * @param menuConfig 菜单配置
 * @param userPermissions 用户权限列表
 * @returns 菜单权限验证结果
 */
export function validateMenuPermission(
  menuConfig: MenuPermissionConfig,
  userPermissions: string[]
): MenuPermissionResult {
  if (menuConfig.required_permissions.length === 0) {
    return {
      menu_key: menuConfig.menu_key,
      hasPermission: true,
      isVisible: menuConfig.is_visible,
      message: '无需权限验证',
    }
  }
  
  const permissionResult = checkMultiplePermissions(
    userPermissions,
    menuConfig.required_permissions,
    menuConfig.permission_logic
  )
  
  return {
    menu_key: menuConfig.menu_key,
    hasPermission: permissionResult.hasPermission,
    isVisible: menuConfig.is_visible && permissionResult.hasPermission,
    missingPermissions: permissionResult.missingPermissions,
    message: permissionResult.message,
  }
}

/**
 * 导出菜单权限配置
 * @param configs 菜单配置列表
 * @param exportedBy 导出者ID
 * @param description 导出描述
 * @returns 导出数据
 */
export function exportMenuConfig(
  configs: MenuPermissionConfig[],
  exportedBy?: string,
  description?: string
): MenuConfigExport {
  return {
    version: '1.0.0',
    exported_at: new Date().toISOString(),
    configs,
    exported_by: exportedBy,
    description,
  }
}

/**
 * 验证菜单配置导入数据
 * @param importData 导入数据
 * @returns 验证结果
 */
export function validateMenuConfigImport(importData: any): {
  valid: boolean
  errors: string[]
} {
  const errors: string[] = []
  
  if (!importData || typeof importData !== 'object') {
    errors.push('导入数据格式不正确')
    return { valid: false, errors }
  }
  
  if (!importData.configs || !Array.isArray(importData.configs)) {
    errors.push('缺少配置数据或格式不正确')
    return { valid: false, errors }
  }
  
  // 验证每个配置项
  importData.configs.forEach((config: any, index: number) => {
    if (!config.menu_key || typeof config.menu_key !== 'string') {
      errors.push(`配置项 ${index + 1}: 缺少或无效的菜单键名`)
    } else if (!validateMenuKey(config.menu_key)) {
      errors.push(`配置项 ${index + 1}: 菜单键名格式不正确`)
    }
    
    if (!config.menu_name || typeof config.menu_name !== 'string') {
      errors.push(`配置项 ${index + 1}: 缺少或无效的菜单名称`)
    }
    
    if (!config.menu_path || typeof config.menu_path !== 'string') {
      errors.push(`配置项 ${index + 1}: 缺少或无效的菜单路径`)
    }
    
    if (!config.required_permissions || !Array.isArray(config.required_permissions)) {
      errors.push(`配置项 ${index + 1}: 缺少或无效的权限配置`)
    } else {
      config.required_permissions.forEach((permission: unknown, permIndex: number) => {
        if (typeof permission !== 'string' || !validatePermissionName(permission)) {
          errors.push(`配置项 ${index + 1}, 权限 ${permIndex + 1}: 权限名称格式不正确`)
        }
      })
    }
    
    if (config.permission_logic && !['AND', 'OR'].includes(config.permission_logic)) {
      errors.push(`配置项 ${index + 1}: 权限逻辑必须是 AND 或 OR`)
    }
  })
  
  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * 处理菜单配置导入
 * @param importRequest 导入请求
 * @param existingConfigs 现有配置
 * @returns 处理后的配置列表
 */
export function processMenuConfigImport(
  importRequest: MenuConfigImportRequest,
  existingConfigs: MenuPermissionConfig[]
): MenuPermissionConfig[] {
  const existingMap = new Map(existingConfigs.map(config => [config.menu_key, config]))
  const processedConfigs: MenuPermissionConfig[] = []
  
  importRequest.configs.forEach(importConfig => {
    const existingConfig = existingMap.get(importConfig.menu_key)
    
    if (importRequest.import_mode === 'replace' || 
        (importRequest.import_mode === 'merge' && importRequest.overwrite_existing) ||
        !existingConfig) {
      
      // 创建新配置或替换现有配置
      const newConfig: MenuPermissionConfig = {
        id: existingConfig?.id || `menu-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        ...importConfig,
        created_at: existingConfig?.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      
      processedConfigs.push(newConfig)
    } else if (existingConfig) {
      // 保留现有配置
      processedConfigs.push(existingConfig)
    }
  })
  
  // 如果是追加模式，添加现有配置
  if (importRequest.import_mode === 'append') {
    const importKeys = new Set(importRequest.configs.map(config => config.menu_key))
    existingConfigs.forEach(config => {
      if (!importKeys.has(config.menu_key)) {
        processedConfigs.push(config)
      }
    })
  }
  
  return processedConfigs
}

/**
 * 计算权限级别
 * @param permissionName 权限名称
 * @returns 权限级别
 */
export function calculatePermissionLevel(permissionName: string): number {
  const parsed = parsePermissionName(permissionName)
  if (!parsed) return 1
  
  // 基础级别
  let level = 1
  
  // 根据操作类型调整级别
  const actionLevels: Record<string, number> = {
    'view': 1,
    'read': 1,
    'create': 2,
    'update': 2,
    'delete': 3,
    'manage': 4,
    'execute': 3,
  }
  
  level = actionLevels[parsed.action] || 1
  
  // 如果有子资源，增加级别
  if (parsed.subResource) {
    level += 1
  }
  
  return level
}

/**
 * 生成权限显示名称
 * @param permissionName 权限名称
 * @returns 显示名称
 */
export function generatePermissionDisplayName(permissionName: string): string {
  const parsed = parsePermissionName(permissionName)
  if (!parsed) return permissionName
  
  const resourceNames: Record<string, string> = {
    'user': '用户',
    'role': '角色',
    'permission': '权限',
    'provider': '提供商',
    'model': '模型',
    'chat': '对话',
    'system': '系统',
    'menu': '菜单',
    'audit': '审计',
    'config': '配置',
  }
  
  const actionNames: Record<string, string> = {
    'view': '查看',
    'read': '读取',
    'create': '创建',
    'update': '更新',
    'delete': '删除',
    'manage': '管理',
    'execute': '执行',
  }
  
  const resourceName = resourceNames[parsed.resource] || parsed.resource
  const actionName = actionNames[parsed.action] || parsed.action
  
  if (parsed.subResource) {
    return `${actionName}${resourceName}${parsed.subResource}`
  }
  
  return `${actionName}${resourceName}`
}