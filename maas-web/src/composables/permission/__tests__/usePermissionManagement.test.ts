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

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePermissionManagement } from '../usePermissionManagement'
import { usePermissionStore } from '@/stores/permission/permissionStore'
import { useNotification } from '@/composables/useNotification'
import type {
  Permission,
  CreatePermissionRequest,
  UpdatePermissionRequest,
  PermissionTreeNode,
  PermissionDependency,
} from '@/types/permission/permissionTypes'

// Mock dependencies
vi.mock('@/stores/permission/permissionStore')
vi.mock('@/composables/useNotification')

// Mock data
const mockPermission: Permission = {
  id: '1',
  name: 'user.view',
  display_name: 'View Users',
  description: 'Permission to view users',
  resource: 'user',
  action: 'view',
  module: 'user',
  status: 'active',
  is_system_permission: false,
  parent_id: undefined,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockSystemPermission: Permission = {
  id: '2',
  name: 'system.admin',
  display_name: 'System Admin',
  description: 'System administrator permission',
  resource: 'system',
  action: 'manage',
  module: 'system',
  status: 'active',
  is_system_permission: true,
  parent_id: undefined,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockChildPermission: Permission = {
  id: '3',
  name: 'user.create',
  display_name: 'Create Users',
  description: 'Permission to create users',
  resource: 'user',
  action: 'create',
  module: 'user',
  status: 'active',
  is_system_permission: false,
  parent_id: '1',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockTreeNode: PermissionTreeNode = {
  permission: mockPermission,
  children: [
    {
      permission: mockChildPermission,
      children: [],
      expanded: false,
      selected: false,
      level: 1,
    },
  ],
  expanded: true,
  selected: false,
  level: 0,
}

const mockDependency: PermissionDependency = {
  permission_id: '1',
  depends_on: [],
  dependents: ['3'],
  roles_using: ['role1'],
  users_affected: 5,
}

const mockCreatePermissionRequest: CreatePermissionRequest = {
  name: 'user.edit',
  display_name: 'Edit Users',
  description: 'Permission to edit users',
  resource: 'user',
  action: 'update',
  module: 'user',
  parent_id: undefined,
}

describe('usePermissionManagement', () => {
  let permissionStore: any
  let notification: any

  beforeEach(() => {
    setActivePinia(createPinia())
    
    // Mock permission store
    permissionStore = {
      permissions: [mockPermission, mockSystemPermission, mockChildPermission],
      filteredPermissions: [mockPermission, mockSystemPermission, mockChildPermission],
      permissionTree: [mockTreeNode],
      permissionsByModule: { user: [mockPermission, mockChildPermission], system: [mockSystemPermission] },
      permissionsByResource: { user: [mockPermission, mockChildPermission], system: [mockSystemPermission] },
      systemPermissions: [mockSystemPermission],
      customPermissions: [mockPermission, mockChildPermission],
      activePermissions: [mockPermission, mockSystemPermission, mockChildPermission],
      rootPermissions: [mockPermission, mockSystemPermission],
      availableModules: ['user', 'system'],
      availableResources: ['user', 'system'],
      loading: false,
      batchOperationLoading: false,
      error: null,
      currentPage: 1,
      pageSize: 10,
      totalCount: 3,
      totalPages: 1,
      hasNextPage: false,
      hasPrevPage: false,
      searchQuery: '',
      resourceFilter: '',
      actionFilter: '',
      moduleFilter: '',
      statusFilter: '',
      systemOnlyFilter: false,
      sortBy: 'created_at',
      sortOrder: 'desc',
      stats: null,
      selectedNodes: new Set(),
      expandedNodes: new Set(),
      fetchPermissions: vi.fn().mockResolvedValue(undefined),
      fetchPermissionById: vi.fn().mockResolvedValue(mockPermission),
      createPermission: vi.fn().mockResolvedValue(mockPermission),
      updatePermission: vi.fn().mockResolvedValue(mockPermission),
      deletePermission: vi.fn().mockResolvedValue(undefined),
      fetchPermissionStats: vi.fn().mockResolvedValue({}),
      fetchPermissionDependencies: vi.fn().mockResolvedValue(mockDependency),
      batchOperatePermissions: vi.fn().mockResolvedValue({ success_ids: ['1'], failed_ids: [] }),
      refresh: vi.fn().mockResolvedValue(undefined),
      setSearchQuery: vi.fn(),
      setResourceFilter: vi.fn(),
      setActionFilter: vi.fn(),
      setModuleFilter: vi.fn(),
      setStatusFilter: vi.fn(),
      setSystemOnlyFilter: vi.fn(),
      resetFilters: vi.fn(),
      setPage: vi.fn(),
      setPageSize: vi.fn(),
      setSorting: vi.fn(),
      toggleNodeExpanded: vi.fn(),
      toggleNodeSelected: vi.fn(),
      expandAllNodes: vi.fn(),
      collapseAllNodes: vi.fn(),
      selectAllNodes: vi.fn(),
      deselectAllNodes: vi.fn(),
      checkPermission: vi.fn().mockReturnValue({ hasPermission: true }),
      checkPermissions: vi.fn().mockReturnValue({ hasPermission: true }),
      findPermissionById: vi.fn().mockReturnValue(mockPermission),
      findPermissionByName: vi.fn().mockReturnValue(mockPermission),
      isPermissionNameExists: vi.fn().mockReturnValue(false),
      getChildPermissions: vi.fn().mockReturnValue([]),
      getParentPermission: vi.fn().mockReturnValue(undefined),
    }

    // Mock notification
    notification = {
      showSuccess: vi.fn(),
      showError: vi.fn(),
      showWarning: vi.fn(),
      confirmDelete: vi.fn().mockResolvedValue(true),
      confirmBatchDelete: vi.fn().mockResolvedValue(true),
    }

    vi.mocked(usePermissionStore).mockReturnValue(permissionStore)
    vi.mocked(useNotification).mockReturnValue(notification)
  })

  describe('初始化', () => {
    it('应该正确初始化', async () => {
      const { initialize } = usePermissionManagement()
      
      await initialize()
      
      expect(permissionStore.fetchPermissions).toHaveBeenCalled()
      expect(permissionStore.fetchPermissionStats).toHaveBeenCalled()
    })

    it('初始化失败时应该显示错误消息', async () => {
      permissionStore.fetchPermissions.mockRejectedValue(new Error('Network error'))
      
      const { initialize } = usePermissionManagement()
      
      await initialize()
      
      expect(notification.showError).toHaveBeenCalledWith('初始化权限管理失败')
    })
  })

  describe('计算属性', () => {
    it('应该正确返回权限列表', () => {
      const {
        permissions,
        filteredPermissions,
        systemPermissions,
        customPermissions,
        activePermissions,
        rootPermissions,
      } = usePermissionManagement()
      
      expect(permissions.value).toEqual([mockPermission, mockSystemPermission, mockChildPermission])
      expect(filteredPermissions.value).toEqual([mockPermission, mockSystemPermission, mockChildPermission])
      expect(systemPermissions.value).toEqual([mockSystemPermission])
      expect(customPermissions.value).toEqual([mockPermission, mockChildPermission])
      expect(activePermissions.value).toEqual([mockPermission, mockSystemPermission, mockChildPermission])
      expect(rootPermissions.value).toEqual([mockPermission, mockSystemPermission])
    })

    it('应该正确返回权限树结构', () => {
      const { permissionTree } = usePermissionManagement()
      
      expect(permissionTree.value).toEqual([mockTreeNode])
    })

    it('应该正确返回分页信息', () => {
      const { pagination } = usePermissionManagement()
      
      expect(pagination.value).toEqual({
        currentPage: 1,
        pageSize: 10,
        totalCount: 3,
        totalPages: 1,
        hasNextPage: false,
        hasPrevPage: false,
      })
    })
  })

  describe('对话框操作', () => {
    it('应该正确打开创建对话框', () => {
      const { openCreateDialog, permissionDialogVisible, dialogMode, permissionFormData } = usePermissionManagement()
      
      openCreateDialog()
      
      expect(permissionDialogVisible.value).toBe(true)
      expect(dialogMode.value).toBe('create')
      expect(permissionFormData.value).toEqual({
        name: '',
        display_name: '',
        description: '',
        resource: 'user',
        action: 'view',
        module: 'user',
        parent_id: undefined,
      })
    })

    it('应该正确打开编辑对话框', () => {
      const { openEditDialog, permissionDialogVisible, dialogMode, permissionFormData, selectedPermission } = usePermissionManagement()
      
      openEditDialog(mockPermission)
      
      expect(permissionDialogVisible.value).toBe(true)
      expect(dialogMode.value).toBe('edit')
      expect(selectedPermission.value).toEqual(mockPermission)
      expect(permissionFormData.value).toEqual({
        name: mockPermission.name,
        display_name: mockPermission.display_name,
        description: mockPermission.description,
        resource: mockPermission.resource,
        action: mockPermission.action,
        module: mockPermission.module,
        parent_id: mockPermission.parent_id,
      })
    })

    it('应该正确打开查看对话框', () => {
      const { openViewDialog, permissionDialogVisible, dialogMode, selectedPermission } = usePermissionManagement()
      
      openViewDialog(mockPermission)
      
      expect(permissionDialogVisible.value).toBe(true)
      expect(dialogMode.value).toBe('view')
      expect(selectedPermission.value).toEqual(mockPermission)
    })
  })

  describe('权限CRUD操作', () => {
    it('应该成功创建权限', async () => {
      const { createPermission, permissionDialogVisible } = usePermissionManagement()
      
      const result = await createPermission(mockCreatePermissionRequest)
      
      expect(result).toBe(true)
      expect(permissionStore.createPermission).toHaveBeenCalledWith(mockCreatePermissionRequest)
      expect(notification.showSuccess).toHaveBeenCalledWith(`权限 "${mockPermission.display_name}" 创建成功`)
      expect(permissionDialogVisible.value).toBe(false)
    })

    it('创建权限时表单验证失败应该返回false', async () => {
      const { createPermission } = usePermissionManagement()
      
      const invalidRequest = { ...mockCreatePermissionRequest, name: '' }
      const result = await createPermission(invalidRequest)
      
      expect(result).toBe(false)
      expect(permissionStore.createPermission).not.toHaveBeenCalled()
    })

    it('应该成功更新权限', async () => {
      const { updatePermission, permissionDialogVisible } = usePermissionManagement()
      
      const updateRequest: UpdatePermissionRequest = {
        display_name: 'Updated Permission',
        description: 'Updated description',
      }
      
      const result = await updatePermission('1', updateRequest)
      
      expect(result).toBe(true)
      expect(permissionStore.updatePermission).toHaveBeenCalledWith('1', updateRequest)
      expect(notification.showSuccess).toHaveBeenCalledWith(`权限 "${mockPermission.display_name}" 更新成功`)
      expect(permissionDialogVisible.value).toBe(false)
    })

    it('应该成功删除权限', async () => {
      const { deletePermission } = usePermissionManagement()
      
      const result = await deletePermission(mockPermission)
      
      expect(result).toBe(true)
      expect(notification.confirmDelete).toHaveBeenCalled()
      expect(permissionStore.deletePermission).toHaveBeenCalledWith(mockPermission.id)
      expect(notification.showSuccess).toHaveBeenCalledWith(`权限 "${mockPermission.display_name}" 删除成功`)
    })

    it('不应该删除系统权限', async () => {
      const { deletePermission } = usePermissionManagement()
      
      const result = await deletePermission(mockSystemPermission)
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith('系统权限不能删除')
      expect(permissionStore.deletePermission).not.toHaveBeenCalled()
    })

    it('有子权限时不应该删除权限', async () => {
      permissionStore.getChildPermissions.mockReturnValue([mockChildPermission])
      
      const { deletePermission } = usePermissionManagement()
      
      const result = await deletePermission(mockPermission)
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith(`权限 "${mockPermission.display_name}" 有 1 个子权限，请先删除子权限`)
      expect(permissionStore.deletePermission).not.toHaveBeenCalled()
    })

    it('用户取消删除时应该返回false', async () => {
      notification.confirmDelete.mockResolvedValue(false)
      
      const { deletePermission } = usePermissionManagement()
      
      const result = await deletePermission(mockPermission)
      
      expect(result).toBe(false)
      expect(permissionStore.deletePermission).not.toHaveBeenCalled()
    })
  })

  describe('批量操作', () => {
    it('应该成功批量删除权限', async () => {
      const { batchDeletePermissions, selectedPermissionIds } = usePermissionManagement()
      
      selectedPermissionIds.value = ['1']
      
      const result = await batchDeletePermissions()
      
      expect(result).toBe(true)
      expect(notification.confirmBatchDelete).toHaveBeenCalledWith(1)
      expect(permissionStore.batchOperatePermissions).toHaveBeenCalledWith({
        permission_ids: ['1'],
        action: 'delete',
      })
      expect(notification.showSuccess).toHaveBeenCalledWith('成功删除 1 个权限')
    })

    it('没有选中权限时不应该执行批量删除', async () => {
      const { batchDeletePermissions, selectedPermissionIds } = usePermissionManagement()
      
      selectedPermissionIds.value = []
      
      const result = await batchDeletePermissions()
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith('请选择要删除的权限')
      expect(permissionStore.batchOperatePermissions).not.toHaveBeenCalled()
    })

    it('应该成功批量激活权限', async () => {
      const { batchActivatePermissions, selectedPermissionIds } = usePermissionManagement()
      
      selectedPermissionIds.value = ['1']
      
      const result = await batchActivatePermissions()
      
      expect(result).toBe(true)
      expect(permissionStore.batchOperatePermissions).toHaveBeenCalledWith({
        permission_ids: ['1'],
        action: 'activate',
      })
      expect(notification.showSuccess).toHaveBeenCalledWith('成功激活 1 个权限')
    })

    it('应该成功批量停用权限', async () => {
      const { batchDeactivatePermissions, selectedPermissionIds } = usePermissionManagement()
      
      selectedPermissionIds.value = ['1']
      
      const result = await batchDeactivatePermissions()
      
      expect(result).toBe(true)
      expect(permissionStore.batchOperatePermissions).toHaveBeenCalledWith({
        permission_ids: ['1'],
        action: 'deactivate',
      })
      expect(notification.showSuccess).toHaveBeenCalledWith('成功停用 1 个权限')
    })
  })

  describe('搜索和筛选', () => {
    it('应该正确设置搜索关键词', () => {
      const { setSearchQuery } = usePermissionManagement()
      
      setSearchQuery('test')
      
      expect(permissionStore.setSearchQuery).toHaveBeenCalledWith('test')
    })

    it('应该正确设置资源类型筛选', () => {
      const { setResourceFilter } = usePermissionManagement()
      
      setResourceFilter('user')
      
      expect(permissionStore.setResourceFilter).toHaveBeenCalledWith('user')
    })

    it('应该正确设置模块筛选', () => {
      const { setModuleFilter } = usePermissionManagement()
      
      setModuleFilter('user')
      
      expect(permissionStore.setModuleFilter).toHaveBeenCalledWith('user')
    })

    it('应该正确重置筛选条件', () => {
      const { resetFilters } = usePermissionManagement()
      
      resetFilters()
      
      expect(permissionStore.resetFilters).toHaveBeenCalled()
    })
  })

  describe('分页操作', () => {
    it('应该正确设置页码', () => {
      const { setPage } = usePermissionManagement()
      
      setPage(2)
      
      expect(permissionStore.setPage).toHaveBeenCalledWith(2)
      expect(permissionStore.fetchPermissions).toHaveBeenCalled()
    })

    it('应该正确设置每页数量', () => {
      const { setPageSize } = usePermissionManagement()
      
      setPageSize(20)
      
      expect(permissionStore.setPageSize).toHaveBeenCalledWith(20)
      expect(permissionStore.fetchPermissions).toHaveBeenCalled()
    })
  })

  describe('树形结构操作', () => {
    it('应该正确展开/折叠节点', () => {
      const { toggleNodeExpanded } = usePermissionManagement()
      
      toggleNodeExpanded('1')
      
      expect(permissionStore.toggleNodeExpanded).toHaveBeenCalledWith('1')
    })

    it('应该正确选择/取消选择节点', () => {
      const { toggleNodeSelected, selectedPermissionIds } = usePermissionManagement()
      
      permissionStore.selectedNodes.add('1')
      
      toggleNodeSelected('1')
      
      expect(permissionStore.toggleNodeSelected).toHaveBeenCalledWith('1')
      expect(selectedPermissionIds.value).toContain('1')
    })

    it('应该正确展开所有节点', () => {
      const { expandAllNodes, treeExpandAll } = usePermissionManagement()
      
      expandAllNodes()
      
      expect(permissionStore.expandAllNodes).toHaveBeenCalled()
      expect(treeExpandAll.value).toBe(true)
    })

    it('应该正确折叠所有节点', () => {
      const { collapseAllNodes, treeExpandAll } = usePermissionManagement()
      
      collapseAllNodes()
      
      expect(permissionStore.collapseAllNodes).toHaveBeenCalled()
      expect(treeExpandAll.value).toBe(false)
    })
  })

  describe('权限验证', () => {
    it('应该正确检查权限', () => {
      const { checkPermission } = usePermissionManagement()
      
      const result = checkPermission('user.view')
      
      expect(permissionStore.checkPermission).toHaveBeenCalledWith('user.view')
      expect(result).toEqual({ hasPermission: true })
    })

    it('应该正确批量检查权限', () => {
      const { checkPermissions } = usePermissionManagement()
      
      const result = checkPermissions(['user.view', 'user.create'])
      
      expect(permissionStore.checkPermissions).toHaveBeenCalledWith(['user.view', 'user.create'])
      expect(result).toEqual({ hasPermission: true })
    })
  })

  describe('选择操作', () => {
    it('应该正确选择权限', () => {
      const { selectPermission, selectedPermissionIds, isPermissionSelected } = usePermissionManagement()
      
      selectPermission('1')
      
      expect(selectedPermissionIds.value).toContain('1')
      expect(isPermissionSelected('1')).toBe(true)
    })

    it('应该正确取消选择权限', () => {
      const { selectPermission, unselectPermission, selectedPermissionIds, isPermissionSelected } = usePermissionManagement()
      
      selectPermission('1')
      unselectPermission('1')
      
      expect(selectedPermissionIds.value).not.toContain('1')
      expect(isPermissionSelected('1')).toBe(false)
    })

    it('应该正确切换权限选择状态', () => {
      const { togglePermissionSelection, selectedPermissionIds } = usePermissionManagement()
      
      togglePermissionSelection('1')
      expect(selectedPermissionIds.value).toContain('1')
      
      togglePermissionSelection('1')
      expect(selectedPermissionIds.value).not.toContain('1')
    })

    it('应该正确清空选择', () => {
      const { selectPermission, clearSelection, selectedPermissionIds } = usePermissionManagement()
      
      selectPermission('1')
      selectPermission('2')
      clearSelection()
      
      expect(selectedPermissionIds.value).toEqual([])
    })
  })

  describe('表单验证', () => {
    it('应该验证权限名称不能为空', () => {
      const { validatePermissionForm, formValidation } = usePermissionManagement()
      
      const result = validatePermissionForm({ name: '', display_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.nameError).toBe('权限名称不能为空')
    })

    it('应该验证权限名称格式', () => {
      const { validatePermissionForm, formValidation } = usePermissionManagement()
      
      const result = validatePermissionForm({ name: '123invalid', display_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.nameError).toBe('权限名称只能包含字母、数字、点号和下划线，且必须以字母开头')
    })

    it('应该验证权限名称唯一性', () => {
      permissionStore.isPermissionNameExists.mockReturnValue(true)
      
      const { validatePermissionForm, formValidation } = usePermissionManagement()
      
      const result = validatePermissionForm({ name: 'existing_permission', display_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.nameError).toBe('权限名称已存在')
    })

    it('应该验证显示名称不能为空', () => {
      const { validatePermissionForm, formValidation } = usePermissionManagement()
      
      const result = validatePermissionForm({ name: 'valid_name', display_name: '' })
      
      expect(result).toBe(false)
      expect(formValidation.value.displayNameError).toBe('显示名称不能为空')
    })

    it('应该验证资源类型不能为空', () => {
      const { validatePermissionForm, formValidation } = usePermissionManagement()
      
      const result = validatePermissionForm({ 
        name: 'valid_name', 
        display_name: 'Valid Name',
        resource: undefined as any,
      })
      
      expect(result).toBe(false)
      expect(formValidation.value.resourceError).toBe('资源类型不能为空')
    })

    it('有效的表单数据应该通过验证', () => {
      const { validatePermissionForm } = usePermissionManagement()
      
      const result = validatePermissionForm({
        name: 'valid_name',
        display_name: 'Valid Name',
        resource: 'user',
        action: 'view',
        module: 'user',
      })
      
      expect(result).toBe(true)
    })
  })

  describe('辅助方法', () => {
    it('应该正确获取资源类型显示文本', () => {
      const { getResourceText } = usePermissionManagement()
      
      expect(getResourceText('user')).toBe('用户')
      expect(getResourceText('role')).toBe('角色')
      expect(getResourceText('system')).toBe('系统')
    })

    it('应该正确获取操作类型显示文本', () => {
      const { getActionText } = usePermissionManagement()
      
      expect(getActionText('view')).toBe('查看')
      expect(getActionText('create')).toBe('创建')
      expect(getActionText('delete')).toBe('删除')
    })

    it('应该正确获取模块显示文本', () => {
      const { getModuleText } = usePermissionManagement()
      
      expect(getModuleText('user')).toBe('用户管理')
      expect(getModuleText('system')).toBe('系统管理')
    })

    it('应该正确获取权限状态显示文本', () => {
      const { getStatusText } = usePermissionManagement()
      
      expect(getStatusText('active')).toBe('激活')
      expect(getStatusText('inactive')).toBe('停用')
    })

    it('应该正确查找权限', () => {
      const { findPermissionById, findPermissionByName } = usePermissionManagement()
      
      expect(findPermissionById('1')).toEqual(mockPermission)
      expect(findPermissionByName('user.view')).toEqual(mockPermission)
    })

    it('应该正确获取权限依赖关系', async () => {
      const { fetchPermissionDependencies, permissionDependency } = usePermissionManagement()
      
      const result = await fetchPermissionDependencies('1')
      
      expect(result).toEqual(mockDependency)
      expect(permissionDependency.value).toEqual(mockDependency)
      expect(permissionStore.fetchPermissionDependencies).toHaveBeenCalledWith('1')
    })
  })
})