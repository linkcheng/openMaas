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
  Role,
  CreateRoleRequest,
  UpdateRoleRequest,
  RolePermissionAssignRequest,
  RoleQueryParams,
  RoleStats,
  RoleType,
  RoleStatus,
} from '@/types/permission/roleTypes'
import type {
  ApiResponse,
  PaginatedResponse,
  BatchOperationRequest,
  BatchOperationResult,
} from '@/types/permission/commonTypes'

/**
 * 角色状态管理 Store
 * Role state management store
 */
export const useRoleStore = defineStore('role', () => {
  // ==================== 状态定义 ====================
  
  /** 角色列表 */
  const roles = ref<Role[]>([])
  
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
  
  /** 角色类型筛选 */
  const roleTypeFilter = ref<RoleType | ''>('')
  
  /** 角色状态筛选 */
  const roleStatusFilter = ref<RoleStatus | ''>('')
  
  /** 排序字段 */
  const sortBy = ref('created_at')
  
  /** 排序方向 */
  const sortOrder = ref<'asc' | 'desc'>('desc')
  
  /** 角色统计信息 */
  const stats = ref<RoleStats | null>(null)
  
  /** 缓存的角色详情 */
  const roleDetailsCache = ref<Map<string, Role>>(new Map())
  
  /** 批量操作状态 */
  const batchOperationLoading = ref(false)

  // ==================== 计算属性 ====================
  
  /** 总页数 */
  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
  
  /** 是否有下一页 */
  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  
  /** 是否有上一页 */
  const hasPrevPage = computed(() => currentPage.value > 1)
  
  /** 筛选后的角色列表 */
  const filteredRoles = computed(() => {
    let filtered = roles.value

    // 搜索筛选
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(role =>
        role.name.toLowerCase().includes(query) ||
        role.display_name.toLowerCase().includes(query) ||
        (role.description && role.description.toLowerCase().includes(query))
      )
    }

    // 角色类型筛选
    if (roleTypeFilter.value) {
      filtered = filtered.filter(role => role.role_type === roleTypeFilter.value)
    }

    // 角色状态筛选
    if (roleStatusFilter.value) {
      filtered = filtered.filter(role => role.status === roleStatusFilter.value)
    }

    return filtered
  })
  
  /** 系统角色列表 */
  const systemRoles = computed(() => 
    roles.value.filter(role => role.is_system_role)
  )
  
  /** 自定义角色列表 */
  const customRoles = computed(() => 
    roles.value.filter(role => !role.is_system_role)
  )
  
  /** 活跃角色列表 */
  const activeRoles = computed(() => 
    roles.value.filter(role => role.status === 'active')
  )

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
    roleTypeFilter.value = ''
    roleStatusFilter.value = ''
    currentPage.value = 1
  }

  // ==================== API 调用方法 ====================
  
  /**
   * 获取角色列表
   */
  const fetchRoles = async (params?: Partial<RoleQueryParams>) => {
    setLoading(true)
    clearError()

    try {
      const queryParams: RoleQueryParams = {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value || undefined,
        role_type: roleTypeFilter.value || undefined,
        status: roleStatusFilter.value || undefined,
        sort_by: sortBy.value,
        sort_order: sortOrder.value,
        ...params,
      }

      const response = await apiClient.get<ApiResponse<PaginatedResponse<Role>>>(
        '/roles',
        queryParams
      )

      if (response.data.success && response.data.data) {
        const { items, total, page, page_size } = response.data.data
        roles.value = items
        totalCount.value = total
        currentPage.value = page
        pageSize.value = page_size
        
        // 更新缓存
        items.forEach(role => {
          roleDetailsCache.value.set(role.id, role)
        })
      } else {
        throw new Error(response.data.error || '获取角色列表失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取角色列表失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 获取角色详情
   */
  const fetchRoleById = async (roleId: string, useCache = true): Promise<Role> => {
    // 检查缓存
    if (useCache && roleDetailsCache.value.has(roleId)) {
      return roleDetailsCache.value.get(roleId)!
    }

    setLoading(true)
    clearError()

    try {
      const response = await apiClient.get<ApiResponse<Role>>(`/roles/${roleId}`)

      if (response.data.success && response.data.data) {
        const role = response.data.data
        
        // 更新缓存
        roleDetailsCache.value.set(roleId, role)
        
        // 更新列表中的角色
        const index = roles.value.findIndex(r => r.id === roleId)
        if (index !== -1) {
          roles.value[index] = role
        }
        
        return role
      } else {
        throw new Error(response.data.error || '获取角色详情失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取角色详情失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 创建角色
   */
  const createRole = async (roleData: CreateRoleRequest): Promise<Role> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<Role>>('/roles', roleData)

      if (response.data.success && response.data.data) {
        const newRole = response.data.data
        
        // 添加到列表开头
        roles.value.unshift(newRole)
        totalCount.value += 1
        
        // 更新缓存
        roleDetailsCache.value.set(newRole.id, newRole)
        
        return newRole
      } else {
        throw new Error(response.data.error || '创建角色失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '创建角色失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 更新角色
   */
  const updateRole = async (roleId: string, roleData: UpdateRoleRequest): Promise<Role> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.put<ApiResponse<Role>>(`/roles/${roleId}`, roleData)

      if (response.data.success && response.data.data) {
        const updatedRole = response.data.data
        
        // 更新列表中的角色
        const index = roles.value.findIndex(role => role.id === roleId)
        if (index !== -1) {
          roles.value[index] = updatedRole
        }
        
        // 更新缓存
        roleDetailsCache.value.set(roleId, updatedRole)
        
        return updatedRole
      } else {
        throw new Error(response.data.error || '更新角色失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '更新角色失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 删除角色
   */
  const deleteRole = async (roleId: string): Promise<void> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.delete<ApiResponse<void>>(`/roles/${roleId}`)

      if (response.data.success) {
        // 从列表中移除
        roles.value = roles.value.filter(role => role.id !== roleId)
        totalCount.value -= 1
        
        // 从缓存中移除
        roleDetailsCache.value.delete(roleId)
      } else {
        throw new Error(response.data.error || '删除角色失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '删除角色失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 分配角色权限
   */
  const assignRolePermissions = async (
    roleId: string, 
    permissionData: RolePermissionAssignRequest
  ): Promise<Role> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.put<ApiResponse<Role>>(
        `/roles/${roleId}/permissions`,
        permissionData
      )

      if (response.data.success && response.data.data) {
        const updatedRole = response.data.data
        
        // 更新列表中的角色
        const index = roles.value.findIndex(role => role.id === roleId)
        if (index !== -1) {
          roles.value[index] = updatedRole
        }
        
        // 更新缓存
        roleDetailsCache.value.set(roleId, updatedRole)
        
        return updatedRole
      } else {
        throw new Error(response.data.error || '分配角色权限失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '分配角色权限失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 获取角色统计信息
   */
  const fetchRoleStats = async (): Promise<RoleStats> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.get<ApiResponse<RoleStats>>('/roles/stats')

      if (response.data.success && response.data.data) {
        stats.value = response.data.data
        return response.data.data
      } else {
        throw new Error(response.data.error || '获取角色统计失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取角色统计失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // ==================== 批量操作方法 ====================
  
  /**
   * 批量删除角色
   */
  const batchDeleteRoles = async (roleIds: string[]): Promise<BatchOperationResult> => {
    batchOperationLoading.value = true
    clearError()

    try {
      const request: BatchOperationRequest = {
        ids: roleIds,
        operation: 'delete',
      }

      const response = await apiClient.post<ApiResponse<BatchOperationResult>>(
        '/roles/batch',
        request
      )

      if (response.data.success && response.data.data) {
        const result = response.data.data
        
        // 从列表中移除成功删除的角色
        if (result.success_ids.length > 0) {
          roles.value = roles.value.filter(role => !result.success_ids.includes(role.id))
          totalCount.value -= result.success_ids.length
          
          // 从缓存中移除
          result.success_ids.forEach(id => {
            roleDetailsCache.value.delete(id)
          })
        }
        
        return result
      } else {
        throw new Error(response.data.error || '批量删除角色失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '批量删除角色失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      batchOperationLoading.value = false
    }
  }
  
  /**
   * 批量更新角色状态
   */
  const batchUpdateRoleStatus = async (
    roleIds: string[], 
    status: RoleStatus
  ): Promise<BatchOperationResult> => {
    batchOperationLoading.value = true
    clearError()

    try {
      const request: BatchOperationRequest<{ status: RoleStatus }> = {
        ids: roleIds,
        operation: 'update_status',
        params: { status },
      }

      const response = await apiClient.post<ApiResponse<BatchOperationResult>>(
        '/roles/batch',
        request
      )

      if (response.data.success && response.data.data) {
        const result = response.data.data
        
        // 更新成功的角色状态
        if (result.success_ids.length > 0) {
          roles.value.forEach(role => {
            if (result.success_ids.includes(role.id)) {
              role.status = status
              role.updated_at = new Date().toISOString()
            }
          })
          
          // 更新缓存
          result.success_ids.forEach(id => {
            const cachedRole = roleDetailsCache.value.get(id)
            if (cachedRole) {
              cachedRole.status = status
              cachedRole.updated_at = new Date().toISOString()
            }
          })
        }
        
        return result
      } else {
        throw new Error(response.data.error || '批量更新角色状态失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '批量更新角色状态失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      batchOperationLoading.value = false
    }
  }

  // ==================== 辅助方法 ====================
  
  /**
   * 根据ID查找角色
   */
  const findRoleById = (roleId: string): Role | undefined => {
    return roles.value.find(role => role.id === roleId)
  }
  
  /**
   * 根据名称查找角色
   */
  const findRoleByName = (roleName: string): Role | undefined => {
    return roles.value.find(role => role.name === roleName)
  }
  
  /**
   * 检查角色名称是否已存在
   */
  const isRoleNameExists = (roleName: string, excludeId?: string): boolean => {
    return roles.value.some(role => 
      role.name === roleName && role.id !== excludeId
    )
  }
  
  /**
   * 清除缓存
   */
  const clearCache = () => {
    roleDetailsCache.value.clear()
  }
  
  /**
   * 刷新当前页数据
   */
  const refresh = async () => {
    await fetchRoles()
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
   * 设置角色类型筛选
   */
  const setRoleTypeFilter = (type: RoleType | '') => {
    roleTypeFilter.value = type
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置角色状态筛选
   */
  const setRoleStatusFilter = (status: RoleStatus | '') => {
    roleStatusFilter.value = status
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
    roles,
    loading,
    error,
    currentPage,
    pageSize,
    totalCount,
    searchQuery,
    roleTypeFilter,
    roleStatusFilter,
    sortBy,
    sortOrder,
    stats,
    batchOperationLoading,

    // ==================== 计算属性 ====================
    totalPages,
    hasNextPage,
    hasPrevPage,
    filteredRoles,
    systemRoles,
    customRoles,
    activeRoles,

    // ==================== 方法 ====================
    // 基础操作
    setLoading,
    setError,
    clearError,
    resetFilters,
    
    // API 调用
    fetchRoles,
    fetchRoleById,
    createRole,
    updateRole,
    deleteRole,
    assignRolePermissions,
    fetchRoleStats,
    
    // 批量操作
    batchDeleteRoles,
    batchUpdateRoleStatus,
    
    // 辅助方法
    findRoleById,
    findRoleByName,
    isRoleNameExists,
    clearCache,
    refresh,
    
    // 分页和筛选
    setPage,
    setPageSize,
    setSearchQuery,
    setRoleTypeFilter,
    setRoleStatusFilter,
    setSorting,
  }
})