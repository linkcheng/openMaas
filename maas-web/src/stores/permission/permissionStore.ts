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

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/utils/api'
import type {
  Permission,
  CreatePermissionRequest,
  UpdatePermissionRequest,
  PermissionQueryParams,
  PermissionTreeNode,
  PermissionStats,
  PermissionCheckResult,
  PermissionDependency,
  BatchPermissionRequest,
  PermissionResource,
  PermissionAction,
  PermissionModule,
  PermissionStatus,
} from '@/types/permission/permissionTypes'
import type {
  ApiResponse,
  PaginatedResponse,
  BatchOperationResult,
} from '@/types/permission/commonTypes'

/**
 * 权限状态管理 Store
 * Permission state management store
 */
export const usePermissionStore = defineStore('permission', () => {
  // ==================== 状态定义 ====================
  
  /** 权限列表 */
  const permissions = ref<Permission[]>([])
  
  /** 权限树结构 */
  const permissionTree = ref<PermissionTreeNode[]>([])
  
  /** 加载状态 */
  const loading = ref(false)
  
  /** 错误信息 */
  const error = ref<string | null>(null)
  
  /** 当前页码 */
  const currentPage = ref(1)
  
  /** 每页数量 */
  const pageSize = ref(10)
  
  /** 总记录数 */
  const totalCount = ref(0)
  
  /** 搜索关键词 */
  const searchQuery = ref('')
  
  /** 资源类型筛选 */
  const resourceFilter = ref<PermissionResource | ''>('')
  
  /** 操作类型筛选 */
  const actionFilter = ref<PermissionAction | ''>('')
  
  /** 模块筛选 */
  const moduleFilter = ref<PermissionModule | ''>('')
  
  /** 权限状态筛选 */
  const statusFilter = ref<PermissionStatus | ''>('')
  
  /** 是否只显示系统权限 */
  const systemOnlyFilter = ref(false)
  
  /** 排序字段 */
  const sortBy = ref('created_at')
  
  /** 排序方向 */
  const sortOrder = ref<'asc' | 'desc'>('desc')
  
  /** 权限统计信息 */
  const stats = ref<PermissionStats | null>(null)
  
  /** 缓存的权限详情 */
  const permissionDetailsCache = ref<Map<string, Permission>>(new Map())
  
  /** 权限依赖关系缓存 */
  const dependencyCache = ref<Map<string, PermissionDependency>>(new Map())
  
  /** 批量操作状态 */
  const batchOperationLoading = ref(false)
  
  /** 树形结构展开状态 */
  const expandedNodes = ref<Set<string>>(new Set())
  
  /** 树形结构选中状态 */
  const selectedNodes = ref<Set<string>>(new Set())

  // ==================== 计算属性 ====================
  
  /** 总页数 */
  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
  
  /** 是否有下一页 */
  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  
  /** 是否有上一页 */
  const hasPrevPage = computed(() => currentPage.value > 1)
  
  /** 筛选后的权限列表 */
  const filteredPermissions = computed(() => {
    let filtered = permissions.value

    // 搜索筛选
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(permission =>
        permission.name.toLowerCase().includes(query) ||
        permission.display_name.toLowerCase().includes(query) ||
        (permission.description && permission.description.toLowerCase().includes(query))
      )
    }

    // 资源类型筛选
    if (resourceFilter.value) {
      filtered = filtered.filter(permission => permission.resource === resourceFilter.value)
    }

    // 操作类型筛选
    if (actionFilter.value) {
      filtered = filtered.filter(permission => permission.action === actionFilter.value)
    }

    // 模块筛选
    if (moduleFilter.value) {
      filtered = filtered.filter(permission => permission.module === moduleFilter.value)
    }

    // 权限状态筛选
    if (statusFilter.value) {
      filtered = filtered.filter(permission => permission.status === statusFilter.value)
    }

    // 系统权限筛选
    if (systemOnlyFilter.value) {
      filtered = filtered.filter(permission => permission.is_system_permission)
    }

    return filtered
  })
  
  /** 按模块分组的权限 */
  const permissionsByModule = computed(() => {
    const grouped: Record<PermissionModule, Permission[]> = {} as Record<PermissionModule, Permission[]>
    
    permissions.value.forEach(permission => {
      if (!grouped[permission.module]) {
        grouped[permission.module] = []
      }
      grouped[permission.module].push(permission)
    })
    
    return grouped
  })
  
  /** 按资源分组的权限 */
  const permissionsByResource = computed(() => {
    const grouped: Record<PermissionResource, Permission[]> = {} as Record<PermissionResource, Permission[]>
    
    permissions.value.forEach(permission => {
      if (!grouped[permission.resource]) {
        grouped[permission.resource] = []
      }
      grouped[permission.resource].push(permission)
    })
    
    return grouped
  })
  
  /** 系统权限列表 */
  const systemPermissions = computed(() => 
    permissions.value.filter(permission => permission.is_system_permission)
  )
  
  /** 自定义权限列表 */
  const customPermissions = computed(() => 
    permissions.value.filter(permission => !permission.is_system_permission)
  )
  
  /** 活跃权限列表 */
  const activePermissions = computed(() => 
    permissions.value.filter(permission => permission.status === 'active')
  )
  
  /** 根权限列表（没有父权限的权限） */
  const rootPermissions = computed(() => 
    permissions.value.filter(permission => !permission.parent_id)
  )
  
  /** 可用的模块列表 */
  const availableModules = computed(() => {
    const modules = new Set<PermissionModule>()
    permissions.value.forEach(permission => modules.add(permission.module))
    return Array.from(modules).sort()
  })
  
  /** 可用的资源列表 */
  const availableResources = computed(() => {
    const resources = new Set<PermissionResource>()
    permissions.value.forEach(permission => resources.add(permission.resource))
    return Array.from(resources).sort()
  })

  // ==================== 基础操作方法 ====================
  
  /**
   * 设置加载状态
   */
  const setLoading = (value: boolean) => {
    loading.value = value
  }
  
  /**
   * 设置错误信息
   */
  const setError = (message: string | null) => {
    error.value = message
  }
  
  /**
   * 清除错误信息
   */
  const clearError = () => {
    error.value = null
  }
  
  /**
   * 重置筛选条件
   */
  const resetFilters = () => {
    searchQuery.value = ''
    resourceFilter.value = ''
    actionFilter.value = ''
    moduleFilter.value = ''
    statusFilter.value = ''
    systemOnlyFilter.value = false
    currentPage.value = 1
  }

  // ==================== API 调用方法 ====================
  
  /**
   * 获取权限列表
   */
  const fetchPermissions = async (params?: Partial<PermissionQueryParams>) => {
    setLoading(true)
    clearError()

    try {
      const queryParams: PermissionQueryParams = {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value || undefined,
        resource: resourceFilter.value || undefined,
        action: actionFilter.value || undefined,
        module: moduleFilter.value || undefined,
        status: statusFilter.value || undefined,
        system_only: systemOnlyFilter.value || undefined,
        sort_by: sortBy.value,
        sort_order: sortOrder.value,
        ...params,
      }

      const response = await apiClient.get<ApiResponse<PaginatedResponse<Permission>>>(
        '/permissions',
        queryParams
      )

      if (response.data.success && response.data.data) {
        const { items, total, page, page_size } = response.data.data
        permissions.value = items
        totalCount.value = total
        currentPage.value = page
        pageSize.value = page_size
        
        // 更新缓存
        items.forEach(permission => {
          permissionDetailsCache.value.set(permission.id, permission)
        })
        
        // 构建权限树
        buildPermissionTree()
      } else {
        throw new Error(response.data.error || '获取权限列表失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取权限列表失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 获取权限详情
   */
  const fetchPermissionById = async (permissionId: string, useCache = true): Promise<Permission> => {
    // 检查缓存
    if (useCache && permissionDetailsCache.value.has(permissionId)) {
      return permissionDetailsCache.value.get(permissionId)!
    }

    setLoading(true)
    clearError()

    try {
      const response = await apiClient.get<ApiResponse<Permission>>(`/permissions/${permissionId}`)

      if (response.data.success && response.data.data) {
        const permission = response.data.data
        
        // 更新缓存
        permissionDetailsCache.value.set(permissionId, permission)
        
        // 更新列表中的权限
        const index = permissions.value.findIndex(p => p.id === permissionId)
        if (index !== -1) {
          permissions.value[index] = permission
        }
        
        return permission
      } else {
        throw new Error(response.data.error || '获取权限详情失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取权限详情失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 创建权限
   */
  const createPermission = async (permissionData: CreatePermissionRequest): Promise<Permission> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<Permission>>('/permissions', permissionData)

      if (response.data.success && response.data.data) {
        const newPermission = response.data.data
        
        // 添加到列表开头
        permissions.value.unshift(newPermission)
        totalCount.value += 1
        
        // 更新缓存
        permissionDetailsCache.value.set(newPermission.id, newPermission)
        
        // 重新构建权限树
        buildPermissionTree()
        
        return newPermission
      } else {
        throw new Error(response.data.error || '创建权限失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '创建权限失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 更新权限
   */
  const updatePermission = async (
    permissionId: string, 
    permissionData: UpdatePermissionRequest
  ): Promise<Permission> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.put<ApiResponse<Permission>>(
        `/permissions/${permissionId}`,
        permissionData
      )

      if (response.data.success && response.data.data) {
        const updatedPermission = response.data.data
        
        // 更新列表中的权限
        const index = permissions.value.findIndex(permission => permission.id === permissionId)
        if (index !== -1) {
          permissions.value[index] = updatedPermission
        }
        
        // 更新缓存
        permissionDetailsCache.value.set(permissionId, updatedPermission)
        
        // 重新构建权限树
        buildPermissionTree()
        
        return updatedPermission
      } else {
        throw new Error(response.data.error || '更新权限失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '更新权限失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 删除权限
   */
  const deletePermission = async (permissionId: string): Promise<void> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.delete<ApiResponse<void>>(`/permissions/${permissionId}`)

      if (response.data.success) {
        // 从列表中移除
        permissions.value = permissions.value.filter(permission => permission.id !== permissionId)
        totalCount.value -= 1
        
        // 从缓存中移除
        permissionDetailsCache.value.delete(permissionId)
        dependencyCache.value.delete(permissionId)
        
        // 重新构建权限树
        buildPermissionTree()
      } else {
        throw new Error(response.data.error || '删除权限失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '删除权限失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 获取权限统计信息
   */
  const fetchPermissionStats = async (): Promise<PermissionStats> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.get<ApiResponse<PermissionStats>>('/permissions/stats')

      if (response.data.success && response.data.data) {
        stats.value = response.data.data
        return response.data.data
      } else {
        throw new Error(response.data.error || '获取权限统计失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取权限统计失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 获取权限依赖关系
   */
  const fetchPermissionDependencies = async (permissionId: string): Promise<PermissionDependency> => {
    // 检查缓存
    if (dependencyCache.value.has(permissionId)) {
      return dependencyCache.value.get(permissionId)!
    }

    setLoading(true)
    clearError()

    try {
      const response = await apiClient.get<ApiResponse<PermissionDependency>>(
        `/permissions/${permissionId}/dependencies`
      )

      if (response.data.success && response.data.data) {
        const dependency = response.data.data
        
        // 更新缓存
        dependencyCache.value.set(permissionId, dependency)
        
        return dependency
      } else {
        throw new Error(response.data.error || '获取权限依赖关系失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取权限依赖关系失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // ==================== 批量操作方法 ====================
  
  /**
   * 批量操作权限
   */
  const batchOperatePermissions = async (request: BatchPermissionRequest): Promise<BatchOperationResult> => {
    batchOperationLoading.value = true
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<BatchOperationResult>>(
        '/permissions/batch',
        request
      )

      if (response.data.success && response.data.data) {
        const result = response.data.data
        
        // 根据操作类型更新本地状态
        if (request.action === 'delete' && result.success_ids.length > 0) {
          // 删除操作：从列表中移除成功删除的权限
          permissions.value = permissions.value.filter(
            permission => !result.success_ids.includes(permission.id)
          )
          totalCount.value -= result.success_ids.length
          
          // 从缓存中移除
          result.success_ids.forEach(id => {
            permissionDetailsCache.value.delete(id)
            dependencyCache.value.delete(id)
          })
          
          // 重新构建权限树
          buildPermissionTree()
        } else if ((request.action === 'activate' || request.action === 'deactivate') && result.success_ids.length > 0) {
          // 激活/停用操作：更新权限状态
          const newStatus: PermissionStatus = request.action === 'activate' ? 'active' : 'inactive'
          
          permissions.value.forEach(permission => {
            if (result.success_ids.includes(permission.id)) {
              permission.status = newStatus
              permission.updated_at = new Date().toISOString()
            }
          })
          
          // 更新缓存
          result.success_ids.forEach(id => {
            const cachedPermission = permissionDetailsCache.value.get(id)
            if (cachedPermission) {
              cachedPermission.status = newStatus
              cachedPermission.updated_at = new Date().toISOString()
            }
          })
        }
        
        return result
      } else {
        throw new Error(response.data.error || '批量操作权限失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '批量操作权限失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      batchOperationLoading.value = false
    }
  }

  // ==================== 权限树操作方法 ====================
  
  /**
   * 构建权限树结构
   */
  const buildPermissionTree = () => {
    const permissionMap = new Map<string, Permission>()
    const rootNodes: PermissionTreeNode[] = []
    
    // 创建权限映射
    permissions.value.forEach(permission => {
      permissionMap.set(permission.id, permission)
    })
    
    // 构建树结构
    permissions.value.forEach(permission => {
      if (!permission.parent_id) {
        // 根节点
        const node = createTreeNode(permission, permissionMap, 0)
        rootNodes.push(node)
      }
    })
    
    // 按名称排序
    rootNodes.sort((a, b) => a.permission.name.localeCompare(b.permission.name))
    
    permissionTree.value = rootNodes
  }
  
  /**
   * 创建权限树节点
   */
  const createTreeNode = (
    permission: Permission,
    permissionMap: Map<string, Permission>,
    level: number
  ): PermissionTreeNode => {
    const children: PermissionTreeNode[] = []
    
    // 查找子权限
    permissions.value
      .filter(p => p.parent_id === permission.id)
      .forEach(childPermission => {
        const childNode = createTreeNode(childPermission, permissionMap, level + 1)
        children.push(childNode)
      })
    
    // 按名称排序子节点
    children.sort((a, b) => a.permission.name.localeCompare(b.permission.name))
    
    return {
      permission,
      children,
      expanded: expandedNodes.value.has(permission.id),
      selected: selectedNodes.value.has(permission.id),
      level,
    }
  }
  
  /**
   * 展开/折叠节点
   */
  const toggleNodeExpanded = (permissionId: string) => {
    if (expandedNodes.value.has(permissionId)) {
      expandedNodes.value.delete(permissionId)
    } else {
      expandedNodes.value.add(permissionId)
    }
    
    // 重新构建树结构以更新展开状态
    buildPermissionTree()
  }
  
  /**
   * 选择/取消选择节点
   */
  const toggleNodeSelected = (permissionId: string) => {
    if (selectedNodes.value.has(permissionId)) {
      selectedNodes.value.delete(permissionId)
    } else {
      selectedNodes.value.add(permissionId)
    }
    
    // 重新构建树结构以更新选中状态
    buildPermissionTree()
  }
  
  /**
   * 展开所有节点
   */
  const expandAllNodes = () => {
    permissions.value.forEach(permission => {
      expandedNodes.value.add(permission.id)
    })
    buildPermissionTree()
  }
  
  /**
   * 折叠所有节点
   */
  const collapseAllNodes = () => {
    expandedNodes.value.clear()
    buildPermissionTree()
  }
  
  /**
   * 选择所有节点
   */
  const selectAllNodes = () => {
    permissions.value.forEach(permission => {
      selectedNodes.value.add(permission.id)
    })
    buildPermissionTree()
  }
  
  /**
   * 取消选择所有节点
   */
  const deselectAllNodes = () => {
    selectedNodes.value.clear()
    buildPermissionTree()
  }

  // ==================== 权限验证方法 ====================
  
  /**
   * 检查权限
   */
  const checkPermission = (permissionName: string): PermissionCheckResult => {
    const permission = permissions.value.find(p => p.name === permissionName)
    
    if (!permission) {
      return {
        hasPermission: false,
        missingPermissions: [permissionName],
        message: `权限 ${permissionName} 不存在`,
      }
    }
    
    if (permission.status !== 'active') {
      return {
        hasPermission: false,
        missingPermissions: [permissionName],
        message: `权限 ${permissionName} 未激活`,
      }
    }
    
    return {
      hasPermission: true,
      message: `拥有权限 ${permissionName}`,
    }
  }
  
  /**
   * 批量检查权限
   */
  const checkPermissions = (permissionNames: string[]): PermissionCheckResult => {
    const missingPermissions: string[] = []
    
    permissionNames.forEach(name => {
      const result = checkPermission(name)
      if (!result.hasPermission) {
        missingPermissions.push(name)
      }
    })
    
    return {
      hasPermission: missingPermissions.length === 0,
      missingPermissions: missingPermissions.length > 0 ? missingPermissions : undefined,
      message: missingPermissions.length === 0 
        ? '拥有所有权限' 
        : `缺少权限: ${missingPermissions.join(', ')}`,
    }
  }

  // ==================== 辅助方法 ====================
  
  /**
   * 根据ID查找权限
   */
  const findPermissionById = (permissionId: string): Permission | undefined => {
    return permissions.value.find(permission => permission.id === permissionId)
  }
  
  /**
   * 根据名称查找权限
   */
  const findPermissionByName = (permissionName: string): Permission | undefined => {
    return permissions.value.find(permission => permission.name === permissionName)
  }
  
  /**
   * 检查权限名称是否已存在
   */
  const isPermissionNameExists = (permissionName: string, excludeId?: string): boolean => {
    return permissions.value.some(permission => 
      permission.name === permissionName && permission.id !== excludeId
    )
  }
  
  /**
   * 获取权限的子权限
   */
  const getChildPermissions = (permissionId: string): Permission[] => {
    return permissions.value.filter(permission => permission.parent_id === permissionId)
  }
  
  /**
   * 获取权限的父权限
   */
  const getParentPermission = (permissionId: string): Permission | undefined => {
    const permission = findPermissionById(permissionId)
    if (!permission?.parent_id) return undefined
    return findPermissionById(permission.parent_id)
  }
  
  /**
   * 清除缓存
   */
  const clearCache = () => {
    permissionDetailsCache.value.clear()
    dependencyCache.value.clear()
  }
  
  /**
   * 刷新当前页数据
   */
  const refresh = async () => {
    await fetchPermissions()
  }

  // ==================== 分页和筛选方法 ====================
  
  /**
   * 设置页码
   */
  const setPage = (page: number) => {
    currentPage.value = page
  }
  
  /**
   * 设置每页数量
   */
  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置搜索关键词
   */
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置资源类型筛选
   */
  const setResourceFilter = (resource: PermissionResource | '') => {
    resourceFilter.value = resource
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置操作类型筛选
   */
  const setActionFilter = (action: PermissionAction | '') => {
    actionFilter.value = action
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置模块筛选
   */
  const setModuleFilter = (module: PermissionModule | '') => {
    moduleFilter.value = module
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置权限状态筛选
   */
  const setStatusFilter = (status: PermissionStatus | '') => {
    statusFilter.value = status
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置系统权限筛选
   */
  const setSystemOnlyFilter = (systemOnly: boolean) => {
    systemOnlyFilter.value = systemOnly
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置排序
   */
  const setSorting = (field: string, order: 'asc' | 'desc') => {
    sortBy.value = field
    sortOrder.value = order
  }

  return {
    // ==================== 状态 ====================
    permissions,
    permissionTree,
    loading,
    error,
    currentPage,
    pageSize,
    totalCount,
    searchQuery,
    resourceFilter,
    actionFilter,
    moduleFilter,
    statusFilter,
    systemOnlyFilter,
    sortBy,
    sortOrder,
    stats,
    batchOperationLoading,
    expandedNodes,
    selectedNodes,

    // ==================== 计算属性 ====================
    totalPages,
    hasNextPage,
    hasPrevPage,
    filteredPermissions,
    permissionsByModule,
    permissionsByResource,
    systemPermissions,
    customPermissions,
    activePermissions,
    rootPermissions,
    availableModules,
    availableResources,

    // ==================== 方法 ====================
    // 基础操作
    setLoading,
    setError,
    clearError,
    resetFilters,
    
    // API 调用
    fetchPermissions,
    fetchPermissionById,
    createPermission,
    updatePermission,
    deletePermission,
    fetchPermissionStats,
    fetchPermissionDependencies,
    
    // 批量操作
    batchOperatePermissions,
    
    // 权限树操作
    buildPermissionTree,
    toggleNodeExpanded,
    toggleNodeSelected,
    expandAllNodes,
    collapseAllNodes,
    selectAllNodes,
    deselectAllNodes,
    
    // 权限验证
    checkPermission,
    checkPermissions,
    
    // 辅助方法
    findPermissionById,
    findPermissionByName,
    isPermissionNameExists,
    getChildPermissions,
    getParentPermission,
    clearCache,
    refresh,
    
    // 分页和筛选
    setPage,
    setPageSize,
    setSearchQuery,
    setResourceFilter,
    setActionFilter,
    setModuleFilter,
    setStatusFilter,
    setSystemOnlyFilter,
    setSorting,
  }
})