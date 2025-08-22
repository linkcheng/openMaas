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
import type {
  Role,
  CreateRoleRequest,
  UpdateRoleRequest,
  RolePermissionAssignRequest,
  RoleType,
  RoleStatus,
  RoleStats,
} from '@/types/permission/roleTypes'
import type { BatchOperationResult } from '@/types/permission/commonTypes'

/**
 * 角色管理业务逻辑组合式函数
 * Role management business logic composable
 */
export const useRoleManagement = () => {
  const roleStore = useRoleStore()
  const { showSuccess, showError, showWarning, confirmDelete, confirmBatchDelete } = useNotification()

  // ==================== 对话框状态 ====================
  
  /** 角色编辑对话框可见性 */
  const roleDialogVisible = ref(false)
  
  /** 权限分配对话框可见性 */
  const permissionDialogVisible = ref(false)
  
  /** 当前选中的角色 */
  const selectedRole = ref<Role | null>(null)
  
  /** 对话框模式 */
  const dialogMode = ref<'create' | 'edit'>('create')
  
  /** 批量选中的角色ID */
  const selectedRoleIds = ref<string[]>([])

  // ==================== 表单状态 ====================
  
  /** 角色表单数据 */
  const roleFormData = ref<Partial<CreateRoleRequest>>({
    name: '',
    display_name: '',
    description: '',
    role_type: 'custom',
  })
  
  /** 表单验证状态 */
  const formValidation = ref({
    nameError: '',
    displayNameError: '',
  })

  // ==================== 计算属性 ====================
  
  /** 角色列表 */
  const roles = computed(() => roleStore.roles)
  
  /** 筛选后的角色列表 */
  const filteredRoles = computed(() => roleStore.filteredRoles)
  
  /** 系统角色列表 */
  const systemRoles = computed(() => roleStore.systemRoles)
  
  /** 自定义角色列表 */
  const customRoles = computed(() => roleStore.customRoles)
  
  /** 活跃角色列表 */
  const activeRoles = computed(() => roleStore.activeRoles)
  
  /** 加载状态 */
  const loading = computed(() => roleStore.loading)
  
  /** 批量操作加载状态 */
  const batchLoading = computed(() => roleStore.batchOperationLoading)
  
  /** 错误信息 */
  const error = computed(() => roleStore.error)
  
  /** 分页信息 */
  const pagination = computed(() => ({
    currentPage: roleStore.currentPage,
    pageSize: roleStore.pageSize,
    totalCount: roleStore.totalCount,
    totalPages: roleStore.totalPages,
    hasNextPage: roleStore.hasNextPage,
    hasPrevPage: roleStore.hasPrevPage,
  }))
  
  /** 筛选条件 */
  const filters = computed(() => ({
    searchQuery: roleStore.searchQuery,
    roleTypeFilter: roleStore.roleTypeFilter,
    roleStatusFilter: roleStore.roleStatusFilter,
  }))
  
  /** 排序信息 */
  const sorting = computed(() => ({
    sortBy: roleStore.sortBy,
    sortOrder: roleStore.sortOrder,
  }))
  
  /** 角色统计信息 */
  const stats = computed(() => roleStore.stats)
  
  /** 是否有选中的角色 */
  const hasSelectedRoles = computed(() => selectedRoleIds.value.length > 0)
  
  /** 选中角色数量 */
  const selectedRoleCount = computed(() => selectedRoleIds.value.length)
  
  /** 是否可以批量删除 */
  const canBatchDelete = computed(() => {
    if (!hasSelectedRoles.value) return false
    
    // 检查是否包含系统角色
    const selectedRoles = roles.value.filter(role => selectedRoleIds.value.includes(role.id))
    return !selectedRoles.some(role => role.is_system_role)
  })

  // ==================== 初始化和数据获取 ====================
  
  /**
   * 初始化角色管理
   */
  const initialize = async () => {
    try {
      await Promise.all([
        roleStore.fetchRoles(),
        roleStore.fetchRoleStats(),
      ])
    } catch (err) {
      console.error('初始化角色管理失败:', err)
      showError('初始化角色管理失败')
    }
  }
  
  /**
   * 刷新角色列表
   */
  const refresh = async () => {
    try {
      await roleStore.refresh()
      showSuccess('角色列表已刷新')
    } catch (err) {
      console.error('刷新角色列表失败:', err)
      showError('刷新角色列表失败')
    }
  }
  
  /**
   * 获取角色详情
   */
  const fetchRoleDetails = async (roleId: string, useCache = true): Promise<Role | null> => {
    try {
      return await roleStore.fetchRoleById(roleId, useCache)
    } catch (err) {
      console.error('获取角色详情失败:', err)
      showError('获取角色详情失败')
      return null
    }
  }

  // ==================== 角色CRUD操作 ====================
  
  /**
   * 打开创建角色对话框
   */
  const openCreateDialog = () => {
    selectedRole.value = null
    dialogMode.value = 'create'
    roleFormData.value = {
      name: '',
      display_name: '',
      description: '',
      role_type: 'custom',
    }
    clearFormValidation()
    roleDialogVisible.value = true
  }
  
  /**
   * 打开编辑角色对话框
   */
  const openEditDialog = (role: Role) => {
    selectedRole.value = role
    dialogMode.value = 'edit'
    roleFormData.value = {
      name: role.name,
      display_name: role.display_name,
      description: role.description,
      role_type: role.role_type,
    }
    clearFormValidation()
    roleDialogVisible.value = true
  }
  
  /**
   * 创建角色
   */
  const createRole = async (roleData: CreateRoleRequest): Promise<boolean> => {
    try {
      // 验证表单
      if (!validateRoleForm(roleData)) {
        return false
      }
      
      const newRole = await roleStore.createRole(roleData)
      showSuccess(`角色 "${newRole.display_name}" 创建成功`)
      roleDialogVisible.value = false
      return true
    } catch (err) {
      console.error('创建角色失败:', err)
      showError('创建角色失败')
      return false
    }
  }
  
  /**
   * 更新角色
   */
  const updateRole = async (roleId: string, roleData: UpdateRoleRequest): Promise<boolean> => {
    try {
      // 验证表单
      if (!validateRoleForm(roleData)) {
        return false
      }
      
      const updatedRole = await roleStore.updateRole(roleId, roleData)
      showSuccess(`角色 "${updatedRole.display_name}" 更新成功`)
      roleDialogVisible.value = false
      return true
    } catch (err) {
      console.error('更新角色失败:', err)
      showError('更新角色失败')
      return false
    }
  }
  
  /**
   * 删除角色
   */
  const deleteRole = async (role: Role): Promise<boolean> => {
    try {
      // 系统角色不能删除
      if (role.is_system_role) {
        showWarning('系统角色不能删除')
        return false
      }
      
      // 确认删除
      const confirmed = await confirmDelete(
        role.display_name,
        `确定要删除角色 "${role.display_name}" 吗？此操作不可撤销。`
      )
      
      if (!confirmed) return false
      
      await roleStore.deleteRole(role.id)
      showSuccess(`角色 "${role.display_name}" 删除成功`)
      return true
    } catch (err) {
      console.error('删除角色失败:', err)
      showError('删除角色失败')
      return false
    }
  }

  // ==================== 权限分配操作 ====================
  
  /**
   * 打开权限分配对话框
   */
  const openPermissionDialog = (role: Role) => {
    selectedRole.value = role
    permissionDialogVisible.value = true
  }
  
  /**
   * 分配角色权限
   */
  const assignRolePermissions = async (
    roleId: string,
    permissionData: RolePermissionAssignRequest
  ): Promise<boolean> => {
    try {
      const updatedRole = await roleStore.assignRolePermissions(roleId, permissionData)
      showSuccess(`角色 "${updatedRole.display_name}" 权限分配成功`)
      permissionDialogVisible.value = false
      return true
    } catch (err) {
      console.error('分配角色权限失败:', err)
      showError('分配角色权限失败')
      return false
    }
  }

  // ==================== 批量操作 ====================
  
  /**
   * 批量删除角色
   */
  const batchDeleteRoles = async (): Promise<boolean> => {
    try {
      if (!hasSelectedRoles.value) {
        showWarning('请选择要删除的角色')
        return false
      }
      
      if (!canBatchDelete.value) {
        showWarning('选中的角色包含系统角色，无法删除')
        return false
      }
      
      // 确认批量删除
      const confirmed = await confirmBatchDelete(selectedRoleCount.value)
      if (!confirmed) return false
      
      const result = await roleStore.batchDeleteRoles(selectedRoleIds.value)
      
      if (result.success_ids.length > 0) {
        showSuccess(`成功删除 ${result.success_ids.length} 个角色`)
      }
      
      if (result.failed_ids.length > 0) {
        showWarning(`${result.failed_ids.length} 个角色删除失败`)
      }
      
      // 清空选择
      selectedRoleIds.value = []
      return true
    } catch (err) {
      console.error('批量删除角色失败:', err)
      showError('批量删除角色失败')
      return false
    }
  }
  
  /**
   * 批量更新角色状态
   */
  const batchUpdateRoleStatus = async (status: RoleStatus): Promise<boolean> => {
    try {
      if (!hasSelectedRoles.value) {
        showWarning('请选择要更新的角色')
        return false
      }
      
      const result = await roleStore.batchUpdateRoleStatus(selectedRoleIds.value, status)
      
      if (result.success_ids.length > 0) {
        const statusText = status === 'active' ? '激活' : '停用'
        showSuccess(`成功${statusText} ${result.success_ids.length} 个角色`)
      }
      
      if (result.failed_ids.length > 0) {
        showWarning(`${result.failed_ids.length} 个角色状态更新失败`)
      }
      
      // 清空选择
      selectedRoleIds.value = []
      return true
    } catch (err) {
      console.error('批量更新角色状态失败:', err)
      showError('批量更新角色状态失败')
      return false
    }
  }

  // ==================== 搜索和筛选 ====================
  
  /**
   * 设置搜索关键词
   */
  const setSearchQuery = (query: string) => {
    roleStore.setSearchQuery(query)
  }
  
  /**
   * 设置角色类型筛选
   */
  const setRoleTypeFilter = (type: RoleType | '') => {
    roleStore.setRoleTypeFilter(type)
  }
  
  /**
   * 设置角色状态筛选
   */
  const setRoleStatusFilter = (status: RoleStatus | '') => {
    roleStore.setRoleStatusFilter(status)
  }
  
  /**
   * 重置筛选条件
   */
  const resetFilters = () => {
    roleStore.resetFilters()
  }

  // ==================== 分页操作 ====================
  
  /**
   * 设置页码
   */
  const setPage = (page: number) => {
    roleStore.setPage(page)
    roleStore.fetchRoles()
  }
  
  /**
   * 设置每页数量
   */
  const setPageSize = (size: number) => {
    roleStore.setPageSize(size)
    roleStore.fetchRoles()
  }
  
  /**
   * 上一页
   */
  const prevPage = () => {
    if (roleStore.hasPrevPage) {
      setPage(roleStore.currentPage - 1)
    }
  }
  
  /**
   * 下一页
   */
  const nextPage = () => {
    if (roleStore.hasNextPage) {
      setPage(roleStore.currentPage + 1)
    }
  }

  // ==================== 排序操作 ====================
  
  /**
   * 设置排序
   */
  const setSorting = (field: string, order: 'asc' | 'desc') => {
    roleStore.setSorting(field, order)
    roleStore.fetchRoles()
  }

  // ==================== 选择操作 ====================
  
  /**
   * 选择角色
   */
  const selectRole = (roleId: string) => {
    if (!selectedRoleIds.value.includes(roleId)) {
      selectedRoleIds.value.push(roleId)
    }
  }
  
  /**
   * 取消选择角色
   */
  const unselectRole = (roleId: string) => {
    const index = selectedRoleIds.value.indexOf(roleId)
    if (index > -1) {
      selectedRoleIds.value.splice(index, 1)
    }
  }
  
  /**
   * 切换角色选择状态
   */
  const toggleRoleSelection = (roleId: string) => {
    if (selectedRoleIds.value.includes(roleId)) {
      unselectRole(roleId)
    } else {
      selectRole(roleId)
    }
  }
  
  /**
   * 全选/取消全选
   */
  const toggleSelectAll = () => {
    if (selectedRoleIds.value.length === filteredRoles.value.length) {
      // 当前全选，取消全选
      selectedRoleIds.value = []
    } else {
      // 全选当前页面的角色（排除系统角色）
      selectedRoleIds.value = filteredRoles.value
        .filter(role => !role.is_system_role)
        .map(role => role.id)
    }
  }
  
  /**
   * 清空选择
   */
  const clearSelection = () => {
    selectedRoleIds.value = []
  }

  // ==================== 表单验证 ====================
  
  /**
   * 验证角色表单
   */
  const validateRoleForm = (roleData: Partial<CreateRoleRequest | UpdateRoleRequest>): boolean => {
    clearFormValidation()
    let isValid = true
    
    // 验证角色名称
    if (!roleData.name || roleData.name.trim() === '') {
      formValidation.value.nameError = '角色名称不能为空'
      isValid = false
    } else if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(roleData.name)) {
      formValidation.value.nameError = '角色名称只能包含字母、数字和下划线，且必须以字母开头'
      isValid = false
    } else if (roleStore.isRoleNameExists(roleData.name, selectedRole.value?.id)) {
      formValidation.value.nameError = '角色名称已存在'
      isValid = false
    }
    
    // 验证显示名称
    if (!roleData.display_name || roleData.display_name.trim() === '') {
      formValidation.value.displayNameError = '显示名称不能为空'
      isValid = false
    }
    
    return isValid
  }
  
  /**
   * 清除表单验证错误
   */
  const clearFormValidation = () => {
    formValidation.value = {
      nameError: '',
      displayNameError: '',
    }
  }

  // ==================== 辅助方法 ====================
  
  /**
   * 根据ID查找角色
   */
  const findRoleById = (roleId: string): Role | undefined => {
    return roleStore.findRoleById(roleId)
  }
  
  /**
   * 根据名称查找角色
   */
  const findRoleByName = (roleName: string): Role | undefined => {
    return roleStore.findRoleByName(roleName)
  }
  
  /**
   * 检查角色是否被选中
   */
  const isRoleSelected = (roleId: string): boolean => {
    return selectedRoleIds.value.includes(roleId)
  }
  
  /**
   * 获取角色类型显示文本
   */
  const getRoleTypeText = (roleType: RoleType): string => {
    const typeMap: Record<RoleType, string> = {
      system: '系统角色',
      custom: '自定义角色',
    }
    return typeMap[roleType] || roleType
  }
  
  /**
   * 获取角色状态显示文本
   */
  const getRoleStatusText = (status: RoleStatus): string => {
    const statusMap: Record<RoleStatus, string> = {
      active: '激活',
      inactive: '停用',
    }
    return statusMap[status] || status
  }

  // ==================== 监听器 ====================
  
  // 监听搜索关键词变化，自动触发搜索
  watch(
    () => roleStore.searchQuery,
    (newQuery) => {
      if (newQuery !== undefined) {
        // 延迟搜索，避免频繁请求
        setTimeout(() => {
          roleStore.fetchRoles()
        }, 300)
      }
    }
  )
  
  // 监听筛选条件变化，自动刷新列表
  watch(
    [() => roleStore.roleTypeFilter, () => roleStore.roleStatusFilter],
    () => {
      roleStore.fetchRoles()
    }
  )

  return {
    // ==================== 状态 ====================
    roleDialogVisible,
    permissionDialogVisible,
    selectedRole,
    dialogMode,
    selectedRoleIds,
    roleFormData,
    formValidation,

    // ==================== 计算属性 ====================
    roles,
    filteredRoles,
    systemRoles,
    customRoles,
    activeRoles,
    loading,
    batchLoading,
    error,
    pagination,
    filters,
    sorting,
    stats,
    hasSelectedRoles,
    selectedRoleCount,
    canBatchDelete,

    // ==================== 方法 ====================
    // 初始化和数据获取
    initialize,
    refresh,
    fetchRoleDetails,

    // 角色CRUD操作
    openCreateDialog,
    openEditDialog,
    createRole,
    updateRole,
    deleteRole,

    // 权限分配操作
    openPermissionDialog,
    assignRolePermissions,

    // 批量操作
    batchDeleteRoles,
    batchUpdateRoleStatus,

    // 搜索和筛选
    setSearchQuery,
    setRoleTypeFilter,
    setRoleStatusFilter,
    resetFilters,

    // 分页操作
    setPage,
    setPageSize,
    prevPage,
    nextPage,

    // 排序操作
    setSorting,

    // 选择操作
    selectRole,
    unselectRole,
    toggleRoleSelection,
    toggleSelectAll,
    clearSelection,

    // 表单验证
    validateRoleForm,
    clearFormValidation,

    // 辅助方法
    findRoleById,
    findRoleByName,
    isRoleSelected,
    getRoleTypeText,
    getRoleStatusText,
  }
}