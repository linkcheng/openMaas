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
import { usePermissionStore } from '@/stores/permission/permissionStore'
import { useNotification } from '@/composables/useNotification'
import type {
  Permission,
  CreatePermissionRequest,
  UpdatePermissionRequest,
  PermissionTreeNode,
  PermissionStats,
  PermissionDependency,
  BatchPermissionRequest,
  PermissionResource,
  PermissionAction,
  PermissionModule,
  PermissionStatus,
  PermissionCheckResult,
} from '@/types/permission/permissionTypes'
import type { BatchOperationResult } from '@/types/permission/commonTypes'

/**
 * 权限管理业务逻辑组合式函数
 * Permission management business logic composable
 */
export const usePermissionManagement = () => {
  const permissionStore = usePermissionStore()
  const { showSuccess, showError, showWarning, confirmDelete, confirmBatchDelete } = useNotification()

  // ==================== 对话框状态 ====================
  
  /** 权限编辑对话框可见性 */
  const permissionDialogVisible = ref(false)
  
  /** 权限依赖对话框可见性 */
  const dependencyDialogVisible = ref(false)
  
  /** 当前选中的权限 */
  const selectedPermission = ref<Permission | null>(null)
  
  /** 对话框模式 */
  const dialogMode = ref<'create' | 'edit' | 'view'>('create')
  
  /** 批量选中的权限ID */
  const selectedPermissionIds = ref<string[]>([])
  
  /** 权限依赖信息 */
  const permissionDependency = ref<PermissionDependency | null>(null)

  // ==================== 表单状态 ====================
  
  /** 权限表单数据 */
  const permissionFormData = ref<Partial<CreatePermissionRequest>>({
    name: '',
    display_name: '',
    description: '',
    resource: 'user',
    action: 'view',
    module: 'user',
    parent_id: undefined,
  })
  
  /** 表单验证状态 */
  const formValidation = ref({
    nameError: '',
    displayNameError: '',
    resourceError: '',
    actionError: '',
    moduleError: '',
  })

  // ==================== 树形结构状态 ====================
  
  /** 树形结构搜索关键词 */
  const treeSearchQuery = ref('')
  
  /** 树形结构展开状态 */
  const treeExpandAll = ref(false)
  
  /** 树形结构选择模式 */
  const treeSelectionMode = ref<'single' | 'multiple'>('single')

  // ==================== 计算属性 ====================
  
  /** 权限列表 */
  const permissions = computed(() => permissionStore.permissions)
  
  /** 筛选后的权限列表 */
  const filteredPermissions = computed(() => permissionStore.filteredPermissions)
  
  /** 权限树结构 */
  const permissionTree = computed(() => permissionStore.permissionTree)
  
  /** 按模块分组的权限 */
  const permissionsByModule = computed(() => permissionStore.permissionsByModule)
  
  /** 按资源分组的权限 */
  const permissionsByResource = computed(() => permissionStore.permissionsByResource)
  
  /** 系统权限列表 */
  const systemPermissions = computed(() => permissionStore.systemPermissions)
  
  /** 自定义权限列表 */
  const customPermissions = computed(() => permissionStore.customPermissions)
  
  /** 活跃权限列表 */
  const activePermissions = computed(() => permissionStore.activePermissions)
  
  /** 根权限列表 */
  const rootPermissions = computed(() => permissionStore.rootPermissions)
  
  /** 可用的模块列表 */
  const availableModules = computed(() => permissionStore.availableModules)
  
  /** 可用的资源列表 */
  const availableResources = computed(() => permissionStore.availableResources)
  
  /** 加载状态 */
  const loading = computed(() => permissionStore.loading)
  
  /** 批量操作加载状态 */
  const batchLoading = computed(() => permissionStore.batchOperationLoading)
  
  /** 错误信息 */
  const error = computed(() => permissionStore.error)
  
  /** 分页信息 */
  const pagination = computed(() => ({
    currentPage: permissionStore.currentPage,
    pageSize: permissionStore.pageSize,
    totalCount: permissionStore.totalCount,
    totalPages: permissionStore.totalPages,
    hasNextPage: permissionStore.hasNextPage,
    hasPrevPage: permissionStore.hasPrevPage,
  }))
  
  /** 筛选条件 */
  const filters = computed(() => ({
    searchQuery: permissionStore.searchQuery,
    resourceFilter: permissionStore.resourceFilter,
    actionFilter: permissionStore.actionFilter,
    moduleFilter: permissionStore.moduleFilter,
    statusFilter: permissionStore.statusFilter,
    systemOnlyFilter: permissionStore.systemOnlyFilter,
  }))
  
  /** 排序信息 */
  const sorting = computed(() => ({
    sortBy: permissionStore.sortBy,
    sortOrder: permissionStore.sortOrder,
  }))
  
  /** 权限统计信息 */
  const stats = computed(() => permissionStore.stats)
  
  /** 是否有选中的权限 */
  const hasSelectedPermissions = computed(() => selectedPermissionIds.value.length > 0)
  
  /** 选中权限数量 */
  const selectedPermissionCount = computed(() => selectedPermissionIds.value.length)
  
  /** 是否可以批量删除 */
  const canBatchDelete = computed(() => {
    if (!hasSelectedPermissions.value) return false
    
    // 检查是否包含系统权限
    const selectedPerms = permissions.value.filter(perm => selectedPermissionIds.value.includes(perm.id))
    return !selectedPerms.some(perm => perm.is_system_permission)
  })
  
  /** 筛选后的权限树 */
  const filteredPermissionTree = computed(() => {
    if (!treeSearchQuery.value) return permissionTree.value
    
    const query = treeSearchQuery.value.toLowerCase()
    return filterTreeNodes(permissionTree.value, query)
  })

  // ==================== 初始化和数据获取 ====================
  
  /**
   * 初始化权限管理
   */
  const initialize = async () => {
    try {
      await Promise.all([
        permissionStore.fetchPermissions(),
        permissionStore.fetchPermissionStats(),
      ])
    } catch (err) {
      console.error('初始化权限管理失败:', err)
      showError('初始化权限管理失败')
    }
  }
  
  /**
   * 刷新权限列表
   */
  const refresh = async () => {
    try {
      await permissionStore.refresh()
      showSuccess('权限列表已刷新')
    } catch (err) {
      console.error('刷新权限列表失败:', err)
      showError('刷新权限列表失败')
    }
  }
  
  /**
   * 获取权限详情
   */
  const fetchPermissionDetails = async (permissionId: string, useCache = true): Promise<Permission | null> => {
    try {
      return await permissionStore.fetchPermissionById(permissionId, useCache)
    } catch (err) {
      console.error('获取权限详情失败:', err)
      showError('获取权限详情失败')
      return null
    }
  }
  
  /**
   * 获取权限依赖关系
   */
  const fetchPermissionDependencies = async (permissionId: string): Promise<PermissionDependency | null> => {
    try {
      const dependency = await permissionStore.fetchPermissionDependencies(permissionId)
      permissionDependency.value = dependency
      return dependency
    } catch (err) {
      console.error('获取权限依赖关系失败:', err)
      showError('获取权限依赖关系失败')
      return null
    }
  }

  // ==================== 权限CRUD操作 ====================
  
  /**
   * 打开创建权限对话框
   */
  const openCreateDialog = (parentPermission?: Permission) => {
    selectedPermission.value = null
    dialogMode.value = 'create'
    permissionFormData.value = {
      name: '',
      display_name: '',
      description: '',
      resource: 'user',
      action: 'view',
      module: 'user',
      parent_id: parentPermission?.id,
    }
    clearFormValidation()
    permissionDialogVisible.value = true
  }
  
  /**
   * 打开编辑权限对话框
   */
  const openEditDialog = (permission: Permission) => {
    selectedPermission.value = permission
    dialogMode.value = 'edit'
    permissionFormData.value = {
      name: permission.name,
      display_name: permission.display_name,
      description: permission.description,
      resource: permission.resource,
      action: permission.action,
      module: permission.module,
      parent_id: permission.parent_id,
    }
    clearFormValidation()
    permissionDialogVisible.value = true
  }
  
  /**
   * 打开查看权限对话框
   */
  const openViewDialog = (permission: Permission) => {
    selectedPermission.value = permission
    dialogMode.value = 'view'
    permissionDialogVisible.value = true
  }
  
  /**
   * 创建权限
   */
  const createPermission = async (permissionData: CreatePermissionRequest): Promise<boolean> => {
    try {
      // 验证表单
      if (!validatePermissionForm(permissionData)) {
        return false
      }
      
      const newPermission = await permissionStore.createPermission(permissionData)
      showSuccess(`权限 "${newPermission.display_name}" 创建成功`)
      permissionDialogVisible.value = false
      return true
    } catch (err) {
      console.error('创建权限失败:', err)
      showError('创建权限失败')
      return false
    }
  }
  
  /**
   * 更新权限
   */
  const updatePermission = async (permissionId: string, permissionData: UpdatePermissionRequest): Promise<boolean> => {
    try {
      // 验证表单
      if (!validatePermissionForm(permissionData)) {
        return false
      }
      
      const updatedPermission = await permissionStore.updatePermission(permissionId, permissionData)
      showSuccess(`权限 "${updatedPermission.display_name}" 更新成功`)
      permissionDialogVisible.value = false
      return true
    } catch (err) {
      console.error('更新权限失败:', err)
      showError('更新权限失败')
      return false
    }
  }
  
  /**
   * 删除权限
   */
  const deletePermission = async (permission: Permission): Promise<boolean> => {
    try {
      // 系统权限不能删除
      if (permission.is_system_permission) {
        showWarning('系统权限不能删除')
        return false
      }
      
      // 检查是否有子权限
      const childPermissions = permissionStore.getChildPermissions(permission.id)
      if (childPermissions.length > 0) {
        showWarning(`权限 "${permission.display_name}" 有 ${childPermissions.length} 个子权限，请先删除子权限`)
        return false
      }
      
      // 确认删除
      const confirmed = await confirmDelete(
        permission.display_name,
        `确定要删除权限 "${permission.display_name}" 吗？此操作不可撤销。`
      )
      
      if (!confirmed) return false
      
      await permissionStore.deletePermission(permission.id)
      showSuccess(`权限 "${permission.display_name}" 删除成功`)
      return true
    } catch (err) {
      console.error('删除权限失败:', err)
      showError('删除权限失败')
      return false
    }
  }

  // ==================== 批量操作 ====================
  
  /**
   * 批量删除权限
   */
  const batchDeletePermissions = async (): Promise<boolean> => {
    try {
      if (!hasSelectedPermissions.value) {
        showWarning('请选择要删除的权限')
        return false
      }
      
      if (!canBatchDelete.value) {
        showWarning('选中的权限包含系统权限，无法删除')
        return false
      }
      
      // 确认批量删除
      const confirmed = await confirmBatchDelete(selectedPermissionCount.value)
      if (!confirmed) return false
      
      const request: BatchPermissionRequest = {
        permission_ids: selectedPermissionIds.value,
        action: 'delete',
      }
      
      const result = await permissionStore.batchOperatePermissions(request)
      
      if (result.success_ids.length > 0) {
        showSuccess(`成功删除 ${result.success_ids.length} 个权限`)
      }
      
      if (result.failed_ids.length > 0) {
        showWarning(`${result.failed_ids.length} 个权限删除失败`)
      }
      
      // 清空选择
      selectedPermissionIds.value = []
      return true
    } catch (err) {
      console.error('批量删除权限失败:', err)
      showError('批量删除权限失败')
      return false
    }
  }
  
  /**
   * 批量激活权限
   */
  const batchActivatePermissions = async (): Promise<boolean> => {
    try {
      if (!hasSelectedPermissions.value) {
        showWarning('请选择要激活的权限')
        return false
      }
      
      const request: BatchPermissionRequest = {
        permission_ids: selectedPermissionIds.value,
        action: 'activate',
      }
      
      const result = await permissionStore.batchOperatePermissions(request)
      
      if (result.success_ids.length > 0) {
        showSuccess(`成功激活 ${result.success_ids.length} 个权限`)
      }
      
      if (result.failed_ids.length > 0) {
        showWarning(`${result.failed_ids.length} 个权限激活失败`)
      }
      
      // 清空选择
      selectedPermissionIds.value = []
      return true
    } catch (err) {
      console.error('批量激活权限失败:', err)
      showError('批量激活权限失败')
      return false
    }
  }
  
  /**
   * 批量停用权限
   */
  const batchDeactivatePermissions = async (): Promise<boolean> => {
    try {
      if (!hasSelectedPermissions.value) {
        showWarning('请选择要停用的权限')
        return false
      }
      
      const request: BatchPermissionRequest = {
        permission_ids: selectedPermissionIds.value,
        action: 'deactivate',
      }
      
      const result = await permissionStore.batchOperatePermissions(request)
      
      if (result.success_ids.length > 0) {
        showSuccess(`成功停用 ${result.success_ids.length} 个权限`)
      }
      
      if (result.failed_ids.length > 0) {
        showWarning(`${result.failed_ids.length} 个权限停用失败`)
      }
      
      // 清空选择
      selectedPermissionIds.value = []
      return true
    } catch (err) {
      console.error('批量停用权限失败:', err)
      showError('批量停用权限失败')
      return false
    }
  }

  // ==================== 搜索和筛选 ====================
  
  /**
   * 设置搜索关键词
   */
  const setSearchQuery = (query: string) => {
    permissionStore.setSearchQuery(query)
  }
  
  /**
   * 设置资源类型筛选
   */
  const setResourceFilter = (resource: PermissionResource | '') => {
    permissionStore.setResourceFilter(resource)
  }
  
  /**
   * 设置操作类型筛选
   */
  const setActionFilter = (action: PermissionAction | '') => {
    permissionStore.setActionFilter(action)
  }
  
  /**
   * 设置模块筛选
   */
  const setModuleFilter = (module: PermissionModule | '') => {
    permissionStore.setModuleFilter(module)
  }
  
  /**
   * 设置权限状态筛选
   */
  const setStatusFilter = (status: PermissionStatus | '') => {
    permissionStore.setStatusFilter(status)
  }
  
  /**
   * 设置系统权限筛选
   */
  const setSystemOnlyFilter = (systemOnly: boolean) => {
    permissionStore.setSystemOnlyFilter(systemOnly)
  }
  
  /**
   * 重置筛选条件
   */
  const resetFilters = () => {
    permissionStore.resetFilters()
  }

  // ==================== 分页操作 ====================
  
  /**
   * 设置页码
   */
  const setPage = (page: number) => {
    permissionStore.setPage(page)
    permissionStore.fetchPermissions()
  }
  
  /**
   * 设置每页数量
   */
  const setPageSize = (size: number) => {
    permissionStore.setPageSize(size)
    permissionStore.fetchPermissions()
  }
  
  /**
   * 上一页
   */
  const prevPage = () => {
    if (permissionStore.hasPrevPage) {
      setPage(permissionStore.currentPage - 1)
    }
  }
  
  /**
   * 下一页
   */
  const nextPage = () => {
    if (permissionStore.hasNextPage) {
      setPage(permissionStore.currentPage + 1)
    }
  }

  // ==================== 排序操作 ====================
  
  /**
   * 设置排序
   */
  const setSorting = (field: string, order: 'asc' | 'desc') => {
    permissionStore.setSorting(field, order)
    permissionStore.fetchPermissions()
  }

  // ==================== 树形结构操作 ====================
  
  /**
   * 展开/折叠节点
   */
  const toggleNodeExpanded = (permissionId: string) => {
    permissionStore.toggleNodeExpanded(permissionId)
  }
  
  /**
   * 选择/取消选择节点
   */
  const toggleNodeSelected = (permissionId: string) => {
    permissionStore.toggleNodeSelected(permissionId)
    
    // 同步到批量选择
    if (permissionStore.selectedNodes.has(permissionId)) {
      if (!selectedPermissionIds.value.includes(permissionId)) {
        selectedPermissionIds.value.push(permissionId)
      }
    } else {
      const index = selectedPermissionIds.value.indexOf(permissionId)
      if (index > -1) {
        selectedPermissionIds.value.splice(index, 1)
      }
    }
  }
  
  /**
   * 展开所有节点
   */
  const expandAllNodes = () => {
    permissionStore.expandAllNodes()
    treeExpandAll.value = true
  }
  
  /**
   * 折叠所有节点
   */
  const collapseAllNodes = () => {
    permissionStore.collapseAllNodes()
    treeExpandAll.value = false
  }
  
  /**
   * 选择所有节点
   */
  const selectAllNodes = () => {
    permissionStore.selectAllNodes()
    selectedPermissionIds.value = permissions.value
      .filter(perm => !perm.is_system_permission)
      .map(perm => perm.id)
  }
  
  /**
   * 取消选择所有节点
   */
  const deselectAllNodes = () => {
    permissionStore.deselectAllNodes()
    selectedPermissionIds.value = []
  }
  
  /**
   * 设置树形搜索关键词
   */
  const setTreeSearchQuery = (query: string) => {
    treeSearchQuery.value = query
  }

  // ==================== 权限验证 ====================
  
  /**
   * 检查权限
   */
  const checkPermission = (permissionName: string): PermissionCheckResult => {
    return permissionStore.checkPermission(permissionName)
  }
  
  /**
   * 批量检查权限
   */
  const checkPermissions = (permissionNames: string[]): PermissionCheckResult => {
    return permissionStore.checkPermissions(permissionNames)
  }

  // ==================== 选择操作 ====================
  
  /**
   * 选择权限
   */
  const selectPermission = (permissionId: string) => {
    if (!selectedPermissionIds.value.includes(permissionId)) {
      selectedPermissionIds.value.push(permissionId)
    }
  }
  
  /**
   * 取消选择权限
   */
  const unselectPermission = (permissionId: string) => {
    const index = selectedPermissionIds.value.indexOf(permissionId)
    if (index > -1) {
      selectedPermissionIds.value.splice(index, 1)
    }
  }
  
  /**
   * 切换权限选择状态
   */
  const togglePermissionSelection = (permissionId: string) => {
    if (selectedPermissionIds.value.includes(permissionId)) {
      unselectPermission(permissionId)
    } else {
      selectPermission(permissionId)
    }
  }
  
  /**
   * 全选/取消全选
   */
  const toggleSelectAll = () => {
    if (selectedPermissionIds.value.length === filteredPermissions.value.length) {
      // 当前全选，取消全选
      selectedPermissionIds.value = []
    } else {
      // 全选当前页面的权限（排除系统权限）
      selectedPermissionIds.value = filteredPermissions.value
        .filter(perm => !perm.is_system_permission)
        .map(perm => perm.id)
    }
  }
  
  /**
   * 清空选择
   */
  const clearSelection = () => {
    selectedPermissionIds.value = []
  }

  // ==================== 表单验证 ====================
  
  /**
   * 验证权限表单
   */
  const validatePermissionForm = (permissionData: Partial<CreatePermissionRequest | UpdatePermissionRequest>): boolean => {
    clearFormValidation()
    let isValid = true
    
    // 验证权限名称
    if (!permissionData.name || permissionData.name.trim() === '') {
      formValidation.value.nameError = '权限名称不能为空'
      isValid = false
    } else if (!/^[a-zA-Z][a-zA-Z0-9_.]*$/.test(permissionData.name)) {
      formValidation.value.nameError = '权限名称只能包含字母、数字、点号和下划线，且必须以字母开头'
      isValid = false
    } else if (permissionStore.isPermissionNameExists(permissionData.name, selectedPermission.value?.id)) {
      formValidation.value.nameError = '权限名称已存在'
      isValid = false
    }
    
    // 验证显示名称
    if (!permissionData.display_name || permissionData.display_name.trim() === '') {
      formValidation.value.displayNameError = '显示名称不能为空'
      isValid = false
    }
    
    // 验证资源类型
    if (!permissionData.resource) {
      formValidation.value.resourceError = '资源类型不能为空'
      isValid = false
    }
    
    // 验证操作类型
    if (!permissionData.action) {
      formValidation.value.actionError = '操作类型不能为空'
      isValid = false
    }
    
    // 验证模块
    if (!permissionData.module) {
      formValidation.value.moduleError = '模块不能为空'
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
      resourceError: '',
      actionError: '',
      moduleError: '',
    }
  }

  // ==================== 辅助方法 ====================
  
  /**
   * 根据ID查找权限
   */
  const findPermissionById = (permissionId: string): Permission | undefined => {
    return permissionStore.findPermissionById(permissionId)
  }
  
  /**
   * 根据名称查找权限
   */
  const findPermissionByName = (permissionName: string): Permission | undefined => {
    return permissionStore.findPermissionByName(permissionName)
  }
  
  /**
   * 检查权限是否被选中
   */
  const isPermissionSelected = (permissionId: string): boolean => {
    return selectedPermissionIds.value.includes(permissionId)
  }
  
  /**
   * 获取权限的子权限
   */
  const getChildPermissions = (permissionId: string): Permission[] => {
    return permissionStore.getChildPermissions(permissionId)
  }
  
  /**
   * 获取权限的父权限
   */
  const getParentPermission = (permissionId: string): Permission | undefined => {
    return permissionStore.getParentPermission(permissionId)
  }
  
  /**
   * 获取资源类型显示文本
   */
  const getResourceText = (resource: PermissionResource): string => {
    const resourceMap: Record<PermissionResource, string> = {
      user: '用户',
      role: '角色',
      permission: '权限',
      provider: '供应商',
      model: '模型',
      chat: '对话',
      system: '系统',
    }
    return resourceMap[resource] || resource
  }
  
  /**
   * 获取操作类型显示文本
   */
  const getActionText = (action: PermissionAction): string => {
    const actionMap: Record<PermissionAction, string> = {
      view: '查看',
      create: '创建',
      update: '更新',
      delete: '删除',
      manage: '管理',
      assign: '分配',
      execute: '执行',
    }
    return actionMap[action] || action
  }
  
  /**
   * 获取模块显示文本
   */
  const getModuleText = (module: PermissionModule): string => {
    const moduleMap: Record<PermissionModule, string> = {
      user: '用户管理',
      provider: '供应商管理',
      model: '模型管理',
      chat: '对话管理',
      system: '系统管理',
    }
    return moduleMap[module] || module
  }
  
  /**
   * 获取权限状态显示文本
   */
  const getStatusText = (status: PermissionStatus): string => {
    const statusMap: Record<PermissionStatus, string> = {
      active: '激活',
      inactive: '停用',
    }
    return statusMap[status] || status
  }
  
  /**
   * 筛选树形节点
   */
  const filterTreeNodes = (nodes: PermissionTreeNode[], query: string): PermissionTreeNode[] => {
    return nodes.filter(node => {
      const matchesQuery = 
        node.permission.name.toLowerCase().includes(query) ||
        node.permission.display_name.toLowerCase().includes(query) ||
        (node.permission.description && node.permission.description.toLowerCase().includes(query))
      
      const hasMatchingChildren = node.children && filterTreeNodes(node.children, query).length > 0
      
      if (matchesQuery || hasMatchingChildren) {
        return {
          ...node,
          children: hasMatchingChildren ? filterTreeNodes(node.children!, query) : node.children,
        }
      }
      
      return false
    }).filter(Boolean) as PermissionTreeNode[]
  }
  
  /**
   * 打开权限依赖对话框
   */
  const openDependencyDialog = async (permission: Permission) => {
    selectedPermission.value = permission
    await fetchPermissionDependencies(permission.id)
    dependencyDialogVisible.value = true
  }

  // ==================== 监听器 ====================
  
  // 监听搜索关键词变化，自动触发搜索
  watch(
    () => permissionStore.searchQuery,
    (newQuery) => {
      if (newQuery !== undefined) {
        // 延迟搜索，避免频繁请求
        setTimeout(() => {
          permissionStore.fetchPermissions()
        }, 300)
      }
    }
  )
  
  // 监听筛选条件变化，自动刷新列表
  watch(
    [
      () => permissionStore.resourceFilter,
      () => permissionStore.actionFilter,
      () => permissionStore.moduleFilter,
      () => permissionStore.statusFilter,
      () => permissionStore.systemOnlyFilter,
    ],
    () => {
      permissionStore.fetchPermissions()
    }
  )

  return {
    // ==================== 状态 ====================
    permissionDialogVisible,
    dependencyDialogVisible,
    selectedPermission,
    dialogMode,
    selectedPermissionIds,
    permissionDependency,
    permissionFormData,
    formValidation,
    treeSearchQuery,
    treeExpandAll,
    treeSelectionMode,

    // ==================== 计算属性 ====================
    permissions,
    filteredPermissions,
    permissionTree,
    filteredPermissionTree,
    permissionsByModule,
    permissionsByResource,
    systemPermissions,
    customPermissions,
    activePermissions,
    rootPermissions,
    availableModules,
    availableResources,
    loading,
    batchLoading,
    error,
    pagination,
    filters,
    sorting,
    stats,
    hasSelectedPermissions,
    selectedPermissionCount,
    canBatchDelete,

    // ==================== 方法 ====================
    // 初始化和数据获取
    initialize,
    refresh,
    fetchPermissionDetails,
    fetchPermissionDependencies,

    // 权限CRUD操作
    openCreateDialog,
    openEditDialog,
    openViewDialog,
    createPermission,
    updatePermission,
    deletePermission,

    // 批量操作
    batchDeletePermissions,
    batchActivatePermissions,
    batchDeactivatePermissions,

    // 搜索和筛选
    setSearchQuery,
    setResourceFilter,
    setActionFilter,
    setModuleFilter,
    setStatusFilter,
    setSystemOnlyFilter,
    resetFilters,

    // 分页操作
    setPage,
    setPageSize,
    prevPage,
    nextPage,

    // 排序操作
    setSorting,

    // 树形结构操作
    toggleNodeExpanded,
    toggleNodeSelected,
    expandAllNodes,
    collapseAllNodes,
    selectAllNodes,
    deselectAllNodes,
    setTreeSearchQuery,

    // 权限验证
    checkPermission,
    checkPermissions,

    // 选择操作
    selectPermission,
    unselectPermission,
    togglePermissionSelection,
    toggleSelectAll,
    clearSelection,

    // 表单验证
    validatePermissionForm,
    clearFormValidation,

    // 辅助方法
    findPermissionById,
    findPermissionByName,
    isPermissionSelected,
    getChildPermissions,
    getParentPermission,
    getResourceText,
    getActionText,
    getModuleText,
    getStatusText,
    openDependencyDialog,
  }
}