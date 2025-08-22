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

import { ref, computed, watch } from 'vue'
import { useRoleStore } from '@/stores/permission/roleStore'
import { useNotification } from '@/composables/useNotification'
import { apiClient } from '@/utils/api'
import type { Role } from '@/types/permission/roleTypes'
import type { Permission } from '@/types/permission/permissionTypes'
import type { ApiResponse, PaginatedResponse } from '@/types/permission/commonTypes'

/**
 * 用户信息类型
 */
export interface User {
  id: string
  username: string
  email: string
  profile: {
    full_name: string
    avatar_url?: string
  }
  is_active: boolean
  created_at: string
  updated_at: string
}

/**
 * 用户角色分配信息类型
 */
export interface UserRoleAssignment {
  user_id: string
  user: User
  roles: Role[]
  assigned_at: string
  assigned_by: string
}

/**
 * 用户角色分配请求类型
 */
export interface UserRoleAssignRequest {
  user_id: string
  role_ids: string[]
  operation: 'assign' | 'unassign' | 'replace'
}

/**
 * 用户权限查询结果类型
 */
export interface UserPermissions {
  user_id: string
  permissions: Permission[]
  role_permissions: Record<string, Permission[]>
  effective_permissions: Permission[]
}

/**
 * 用户查询参数类型
 */
export interface UserQueryParams {
  page?: number
  page_size?: number
  search?: string
  is_active?: boolean
  has_roles?: boolean
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

/**
 * 批量用户角色操作请求类型
 */
export interface BatchUserRoleRequest {
  user_ids: string[]
  role_ids: string[]
  operation: 'assign' | 'unassign' | 'replace'
}

/**
 * 用户角色分配业务逻辑组合式函数
 * User role assignment business logic composable
 */
export const useUserRoleAssign = () => {
  const roleStore = useRoleStore()
  const { showSuccess, showError, showWarning, confirm } = useNotification()

  // ==================== 状态定义 ====================
  
  /** 用户列表 */
  const users = ref<User[]>([])
  
  /** 用户角色分配列表 */
  const userRoleAssignments = ref<UserRoleAssignment[]>([])
  
  /** 加载状态 */
  const loading = ref(false)
  
  /** 批量操作加载状态 */
  const batchLoading = ref(false)
  
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
  
  /** 活跃状态筛选 */
  const activeFilter = ref<boolean | ''>('')
  
  /** 是否有角色筛选 */
  const hasRolesFilter = ref<boolean | ''>('')
  
  /** 排序字段 */
  const sortBy = ref('created_at')
  
  /** 排序方向 */
  const sortOrder = ref<'asc' | 'desc'>('desc')

  // ==================== 对话框状态 ====================
  
  /** 用户角色分配对话框可见性 */
  const assignDialogVisible = ref(false)
  
  /** 用户权限查看对话框可见性 */
  const permissionDialogVisible = ref(false)
  
  /** 当前选中的用户 */
  const selectedUser = ref<User | null>(null)
  
  /** 当前用户的角色分配信息 */
  const currentUserAssignment = ref<UserRoleAssignment | null>(null)
  
  /** 当前用户的权限信息 */
  const currentUserPermissions = ref<UserPermissions | null>(null)
  
  /** 批量选中的用户ID */
  const selectedUserIds = ref<string[]>([])
  
  /** 角色分配表单数据 */
  const assignFormData = ref<{
    selectedRoleIds: string[]
    operation: 'assign' | 'unassign' | 'replace'
  }>({
    selectedRoleIds: [],
    operation: 'replace',
  })

  // ==================== 计算属性 ====================
  
  /** 总页数 */
  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
  
  /** 是否有下一页 */
  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  
  /** 是否有上一页 */
  const hasPrevPage = computed(() => currentPage.value > 1)
  
  /** 筛选后的用户列表 */
  const filteredUsers = computed(() => {
    let filtered = users.value

    // 搜索筛选
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(user =>
        user.username.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        user.profile.full_name.toLowerCase().includes(query)
      )
    }

    // 活跃状态筛选
    if (activeFilter.value !== '') {
      filtered = filtered.filter(user => user.is_active === activeFilter.value)
    }

    return filtered
  })
  
  /** 分页信息 */
  const pagination = computed(() => ({
    currentPage: currentPage.value,
    pageSize: pageSize.value,
    totalCount: totalCount.value,
    totalPages: totalPages.value,
    hasNextPage: hasNextPage.value,
    hasPrevPage: hasPrevPage.value,
  }))
  
  /** 筛选条件 */
  const filters = computed(() => ({
    searchQuery: searchQuery.value,
    activeFilter: activeFilter.value,
    hasRolesFilter: hasRolesFilter.value,
  }))
  
  /** 排序信息 */
  const sorting = computed(() => ({
    sortBy: sortBy.value,
    sortOrder: sortOrder.value,
  }))
  
  /** 是否有选中的用户 */
  const hasSelectedUsers = computed(() => selectedUserIds.value.length > 0)
  
  /** 选中用户数量 */
  const selectedUserCount = computed(() => selectedUserIds.value.length)
  
  /** 可用的角色列表 */
  const availableRoles = computed(() => roleStore.activeRoles)
  
  /** 当前用户已分配的角色ID列表 */
  const currentUserRoleIds = computed(() => {
    return currentUserAssignment.value?.roles.map(role => role.id) || []
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
    activeFilter.value = ''
    hasRolesFilter.value = ''
    currentPage.value = 1
  }

  // ==================== API 调用方法 ====================
  
  /**
   * 获取用户列表
   */
  const fetchUsers = async (params?: Partial<UserQueryParams>) => {
    setLoading(true)
    clearError()

    try {
      const queryParams: UserQueryParams = {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value || undefined,
        is_active: activeFilter.value !== '' ? activeFilter.value : undefined,
        has_roles: hasRolesFilter.value !== '' ? hasRolesFilter.value : undefined,
        sort_by: sortBy.value,
        sort_order: sortOrder.value,
        ...params,
      }

      const response = await apiClient.get<ApiResponse<PaginatedResponse<User>>>(
        '/users',
        queryParams
      )

      if (response.data.success && response.data.data) {
        const { items, total, page, page_size } = response.data.data
        users.value = items
        totalCount.value = total
        currentPage.value = page
        pageSize.value = page_size
      } else {
        throw new Error(response.data.error || '获取用户列表失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取用户列表失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 获取用户角色分配信息
   */
  const fetchUserRoleAssignment = async (userId: string): Promise<UserRoleAssignment> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.get<ApiResponse<UserRoleAssignment>>(
        `/users/${userId}/roles`
      )

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.error || '获取用户角色分配信息失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取用户角色分配信息失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 获取用户权限信息
   */
  const fetchUserPermissions = async (userId: string): Promise<UserPermissions> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.get<ApiResponse<UserPermissions>>(
        `/users/${userId}/permissions`
      )

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.error || '获取用户权限信息失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取用户权限信息失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 分配用户角色
   */
  const assignUserRoles = async (request: UserRoleAssignRequest): Promise<UserRoleAssignment> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.put<ApiResponse<UserRoleAssignment>>(
        `/users/${request.user_id}/roles`,
        {
          role_ids: request.role_ids,
          operation: request.operation,
        }
      )

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.error || '分配用户角色失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '分配用户角色失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 批量分配用户角色
   */
  const batchAssignUserRoles = async (request: BatchUserRoleRequest) => {
    batchLoading.value = true
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<any>>(
        '/users/batch/roles',
        request
      )

      if (response.data.success) {
        return response.data.data
      } else {
        throw new Error(response.data.error || '批量分配用户角色失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '批量分配用户角色失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      batchLoading.value = false
    }
  }

  // ==================== 初始化和数据获取 ====================
  
  /**
   * 初始化用户角色分配管理
   */
  const initialize = async () => {
    try {
      await Promise.all([
        fetchUsers(),
        roleStore.fetchRoles(),
      ])
    } catch (err) {
      console.error('初始化用户角色分配管理失败:', err)
      showError('初始化用户角色分配管理失败')
    }
  }
  
  /**
   * 刷新用户列表
   */
  const refresh = async () => {
    try {
      await fetchUsers()
      showSuccess('用户列表已刷新')
    } catch (err) {
      console.error('刷新用户列表失败:', err)
      showError('刷新用户列表失败')
    }
  }

  // ==================== 用户角色分配操作 ====================
  
  /**
   * 打开用户角色分配对话框
   */
  const openAssignDialog = async (user: User) => {
    try {
      selectedUser.value = user
      
      // 获取用户当前的角色分配信息
      const assignment = await fetchUserRoleAssignment(user.id)
      currentUserAssignment.value = assignment
      
      // 初始化表单数据
      assignFormData.value = {
        selectedRoleIds: assignment.roles.map(role => role.id),
        operation: 'replace',
      }
      
      assignDialogVisible.value = true
    } catch (err) {
      console.error('获取用户角色分配信息失败:', err)
      showError('获取用户角色分配信息失败')
    }
  }
  
  /**
   * 打开用户权限查看对话框
   */
  const openPermissionDialog = async (user: User) => {
    try {
      selectedUser.value = user
      
      // 获取用户权限信息
      const permissions = await fetchUserPermissions(user.id)
      currentUserPermissions.value = permissions
      
      permissionDialogVisible.value = true
    } catch (err) {
      console.error('获取用户权限信息失败:', err)
      showError('获取用户权限信息失败')
    }
  }
  
  /**
   * 保存用户角色分配
   */
  const saveUserRoleAssignment = async (): Promise<boolean> => {
    try {
      if (!selectedUser.value) {
        showError('未选择用户')
        return false
      }
      
      const request: UserRoleAssignRequest = {
        user_id: selectedUser.value.id,
        role_ids: assignFormData.value.selectedRoleIds,
        operation: assignFormData.value.operation,
      }
      
      // 检查是否有变更
      const currentRoleIds = currentUserRoleIds.value.sort()
      const newRoleIds = request.role_ids.sort()
      
      if (request.operation === 'replace' && 
          JSON.stringify(currentRoleIds) === JSON.stringify(newRoleIds)) {
        showWarning('角色分配没有变更')
        return false
      }
      
      // 确认角色变更
      const confirmed = await confirmRoleChange(selectedUser.value, request)
      if (!confirmed) return false
      
      const updatedAssignment = await assignUserRoles(request)
      currentUserAssignment.value = updatedAssignment
      
      showSuccess(`用户 "${selectedUser.value.profile.full_name}" 角色分配成功`)
      assignDialogVisible.value = false
      
      // 刷新用户列表
      await refresh()
      
      return true
    } catch (err) {
      console.error('保存用户角色分配失败:', err)
      showError('保存用户角色分配失败')
      return false
    }
  }
  
  /**
   * 确认角色变更
   */
  const confirmRoleChange = async (user: User, request: UserRoleAssignRequest): Promise<boolean> => {
    const currentRoles = currentUserAssignment.value?.roles || []
    const newRoles = availableRoles.value.filter(role => request.role_ids.includes(role.id))
    
    let message = `确定要为用户 "${user.profile.full_name}" `
    
    if (request.operation === 'assign') {
      message += `分配 ${newRoles.length} 个角色吗？`
    } else if (request.operation === 'unassign') {
      message += `移除 ${newRoles.length} 个角色吗？`
    } else {
      const addedRoles = newRoles.filter(role => !currentRoles.some(cr => cr.id === role.id))
      const removedRoles = currentRoles.filter(role => !newRoles.some(nr => nr.id === role.id))
      
      if (addedRoles.length > 0 && removedRoles.length > 0) {
        message += `添加 ${addedRoles.length} 个角色，移除 ${removedRoles.length} 个角色吗？`
      } else if (addedRoles.length > 0) {
        message += `添加 ${addedRoles.length} 个角色吗？`
      } else if (removedRoles.length > 0) {
        message += `移除 ${removedRoles.length} 个角色吗？`
      }
    }
    
    message += '\n\n角色变更将立即生效，用户可能需要重新登录。'
    
    return await confirm(message, '确认角色变更')
  }

  // ==================== 批量操作 ====================
  
  /**
   * 批量分配角色
   */
  const batchAssignRoles = async (roleIds: string[]): Promise<boolean> => {
    try {
      if (!hasSelectedUsers.value) {
        showWarning('请选择要分配角色的用户')
        return false
      }
      
      if (roleIds.length === 0) {
        showWarning('请选择要分配的角色')
        return false
      }
      
      const confirmed = await confirm(
        `确定要为选中的 ${selectedUserCount.value} 个用户分配 ${roleIds.length} 个角色吗？`,
        '批量分配角色'
      )
      
      if (!confirmed) return false
      
      const request: BatchUserRoleRequest = {
        user_ids: selectedUserIds.value,
        role_ids: roleIds,
        operation: 'assign',
      }
      
      await batchAssignUserRoles(request)
      
      showSuccess(`成功为 ${selectedUserCount.value} 个用户分配角色`)
      
      // 清空选择并刷新列表
      selectedUserIds.value = []
      await refresh()
      
      return true
    } catch (err) {
      console.error('批量分配角色失败:', err)
      showError('批量分配角色失败')
      return false
    }
  }
  
  /**
   * 批量移除角色
   */
  const batchUnassignRoles = async (roleIds: string[]): Promise<boolean> => {
    try {
      if (!hasSelectedUsers.value) {
        showWarning('请选择要移除角色的用户')
        return false
      }
      
      if (roleIds.length === 0) {
        showWarning('请选择要移除的角色')
        return false
      }
      
      const confirmed = await confirm(
        `确定要为选中的 ${selectedUserCount.value} 个用户移除 ${roleIds.length} 个角色吗？`,
        '批量移除角色'
      )
      
      if (!confirmed) return false
      
      const request: BatchUserRoleRequest = {
        user_ids: selectedUserIds.value,
        role_ids: roleIds,
        operation: 'unassign',
      }
      
      await batchAssignUserRoles(request)
      
      showSuccess(`成功为 ${selectedUserCount.value} 个用户移除角色`)
      
      // 清空选择并刷新列表
      selectedUserIds.value = []
      await refresh()
      
      return true
    } catch (err) {
      console.error('批量移除角色失败:', err)
      showError('批量移除角色失败')
      return false
    }
  }

  // ==================== 搜索和筛选 ====================
  
  /**
   * 设置搜索关键词
   */
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置活跃状态筛选
   */
  const setActiveFilter = (active: boolean | '') => {
    activeFilter.value = active
    currentPage.value = 1 // 重置到第一页
  }
  
  /**
   * 设置是否有角色筛选
   */
  const setHasRolesFilter = (hasRoles: boolean | '') => {
    hasRolesFilter.value = hasRoles
    currentPage.value = 1 // 重置到第一页
  }

  // ==================== 分页操作 ====================
  
  /**
   * 设置页码
   */
  const setPage = (page: number) => {
    currentPage.value = page
    fetchUsers()
  }
  
  /**
   * 设置每页数量
   */
  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1 // 重置到第一页
    fetchUsers()
  }
  
  /**
   * 上一页
   */
  const prevPage = () => {
    if (hasPrevPage.value) {
      setPage(currentPage.value - 1)
    }
  }
  
  /**
   * 下一页
   */
  const nextPage = () => {
    if (hasNextPage.value) {
      setPage(currentPage.value + 1)
    }
  }

  // ==================== 排序操作 ====================
  
  /**
   * 设置排序
   */
  const setSorting = (field: string, order: 'asc' | 'desc') => {
    sortBy.value = field
    sortOrder.value = order
    fetchUsers()
  }

  // ==================== 选择操作 ====================
  
  /**
   * 选择用户
   */
  const selectUser = (userId: string) => {
    if (!selectedUserIds.value.includes(userId)) {
      selectedUserIds.value.push(userId)
    }
  }
  
  /**
   * 取消选择用户
   */
  const unselectUser = (userId: string) => {
    const index = selectedUserIds.value.indexOf(userId)
    if (index > -1) {
      selectedUserIds.value.splice(index, 1)
    }
  }
  
  /**
   * 切换用户选择状态
   */
  const toggleUserSelection = (userId: string) => {
    if (selectedUserIds.value.includes(userId)) {
      unselectUser(userId)
    } else {
      selectUser(userId)
    }
  }
  
  /**
   * 全选/取消全选
   */
  const toggleSelectAll = () => {
    if (selectedUserIds.value.length === filteredUsers.value.length) {
      // 当前全选，取消全选
      selectedUserIds.value = []
    } else {
      // 全选当前页面的用户
      selectedUserIds.value = filteredUsers.value.map(user => user.id)
    }
  }
  
  /**
   * 清空选择
   */
  const clearSelection = () => {
    selectedUserIds.value = []
  }

  // ==================== 辅助方法 ====================
  
  /**
   * 根据ID查找用户
   */
  const findUserById = (userId: string): User | undefined => {
    return users.value.find(user => user.id === userId)
  }
  
  /**
   * 检查用户是否被选中
   */
  const isUserSelected = (userId: string): boolean => {
    return selectedUserIds.value.includes(userId)
  }
  
  /**
   * 获取用户状态显示文本
   */
  const getUserStatusText = (isActive: boolean): string => {
    return isActive ? '激活' : '停用'
  }
  
  /**
   * 获取用户角色显示文本
   */
  const getUserRolesText = (roles: Role[]): string => {
    if (roles.length === 0) return '无角色'
    return roles.map(role => role.display_name).join(', ')
  }
  
  /**
   * 获取权限来源角色
   */
  const getPermissionSourceRoles = (permissionId: string): Role[] => {
    if (!currentUserPermissions.value) return []
    
    const sourceRoles: Role[] = []
    
    Object.entries(currentUserPermissions.value.role_permissions).forEach(([roleId, permissions]) => {
      if (permissions.some(p => p.id === permissionId)) {
        const role = availableRoles.value.find(r => r.id === roleId)
        if (role) {
          sourceRoles.push(role)
        }
      }
    })
    
    return sourceRoles
  }

  // ==================== 监听器 ====================
  
  // 监听搜索关键词变化，自动触发搜索
  watch(
    () => searchQuery.value,
    (newQuery) => {
      if (newQuery !== undefined) {
        // 延迟搜索，避免频繁请求
        setTimeout(() => {
          fetchUsers()
        }, 300)
      }
    }
  )
  
  // 监听筛选条件变化，自动刷新列表
  watch(
    [() => activeFilter.value, () => hasRolesFilter.value],
    () => {
      fetchUsers()
    }
  )

  return {
    // ==================== 状态 ====================
    users,
    userRoleAssignments,
    loading,
    batchLoading,
    error,
    assignDialogVisible,
    permissionDialogVisible,
    selectedUser,
    currentUserAssignment,
    currentUserPermissions,
    selectedUserIds,
    assignFormData,

    // ==================== 计算属性 ====================
    filteredUsers,
    pagination,
    filters,
    sorting,
    hasSelectedUsers,
    selectedUserCount,
    availableRoles,
    currentUserRoleIds,

    // ==================== 方法 ====================
    // 初始化和数据获取
    initialize,
    refresh,
    fetchUsers,
    fetchUserRoleAssignment,
    fetchUserPermissions,

    // 用户角色分配操作
    openAssignDialog,
    openPermissionDialog,
    saveUserRoleAssignment,
    assignUserRoles,

    // 批量操作
    batchAssignRoles,
    batchUnassignRoles,

    // 搜索和筛选
    setSearchQuery,
    setActiveFilter,
    setHasRolesFilter,
    resetFilters,

    // 分页操作
    setPage,
    setPageSize,
    prevPage,
    nextPage,

    // 排序操作
    setSorting,

    // 选择操作
    selectUser,
    unselectUser,
    toggleUserSelection,
    toggleSelectAll,
    clearSelection,

    // 辅助方法
    findUserById,
    isUserSelected,
    getUserStatusText,
    getUserRolesText,
    getPermissionSourceRoles,
  }
}