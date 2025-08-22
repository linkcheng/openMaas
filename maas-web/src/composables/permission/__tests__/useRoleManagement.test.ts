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
import { useRoleManagement } from '../useRoleManagement'
import { useRoleStore } from '@/stores/permission/roleStore'
import { useNotification } from '@/composables/useNotification'
import type { Role, CreateRoleRequest, UpdateRoleRequest } from '@/types/permission/roleTypes'

// Mock dependencies
vi.mock('@/stores/permission/roleStore')
vi.mock('@/composables/useNotification')

// Mock data
const mockRole: Role = {
  id: '1',
  name: 'test_role',
  display_name: 'Test Role',
  description: 'Test role description',
  role_type: 'custom',
  is_system_role: false,
  status: 'active',
  permissions: [],
  user_count: 0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockSystemRole: Role = {
  id: '2',
  name: 'admin',
  display_name: 'Administrator',
  description: 'System administrator role',
  role_type: 'system',
  is_system_role: true,
  status: 'active',
  permissions: [],
  user_count: 5,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockCreateRoleRequest: CreateRoleRequest = {
  name: 'new_role',
  display_name: 'New Role',
  description: 'New role description',
  role_type: 'custom',
}

describe('useRoleManagement', () => {
  let roleStore: any
  let notification: any

  beforeEach(() => {
    setActivePinia(createPinia())
    
    // Mock role store
    roleStore = {
      roles: [mockRole, mockSystemRole],
      filteredRoles: [mockRole, mockSystemRole],
      systemRoles: [mockSystemRole],
      customRoles: [mockRole],
      activeRoles: [mockRole, mockSystemRole],
      loading: false,
      batchOperationLoading: false,
      error: null,
      currentPage: 1,
      pageSize: 10,
      totalCount: 2,
      totalPages: 1,
      hasNextPage: false,
      hasPrevPage: false,
      searchQuery: '',
      roleTypeFilter: '',
      roleStatusFilter: '',
      sortBy: 'created_at',
      sortOrder: 'desc',
      stats: null,
      fetchRoles: vi.fn().mockResolvedValue(undefined),
      fetchRoleById: vi.fn().mockResolvedValue(mockRole),
      createRole: vi.fn().mockResolvedValue(mockRole),
      updateRole: vi.fn().mockResolvedValue(mockRole),
      deleteRole: vi.fn().mockResolvedValue(undefined),
      assignRolePermissions: vi.fn().mockResolvedValue(mockRole),
      fetchRoleStats: vi.fn().mockResolvedValue({}),
      batchDeleteRoles: vi.fn().mockResolvedValue({ success_ids: ['1'], failed_ids: [] }),
      batchUpdateRoleStatus: vi.fn().mockResolvedValue({ success_ids: ['1'], failed_ids: [] }),
      refresh: vi.fn().mockResolvedValue(undefined),
      setSearchQuery: vi.fn(),
      setRoleTypeFilter: vi.fn(),
      setRoleStatusFilter: vi.fn(),
      resetFilters: vi.fn(),
      setPage: vi.fn(),
      setPageSize: vi.fn(),
      setSorting: vi.fn(),
      findRoleById: vi.fn().mockReturnValue(mockRole),
      findRoleByName: vi.fn().mockReturnValue(mockRole),
      isRoleNameExists: vi.fn().mockReturnValue(false),
    }

    // Mock notification
    notification = {
      showSuccess: vi.fn(),
      showError: vi.fn(),
      showWarning: vi.fn(),
      confirmDelete: vi.fn().mockResolvedValue(true),
      confirmBatchDelete: vi.fn().mockResolvedValue(true),
    }

    vi.mocked(useRoleStore).mockReturnValue(roleStore)
    vi.mocked(useNotification).mockReturnValue(notification)
  })

  describe('初始化', () => {
    it('应该正确初始化', async () => {
      const { initialize } = useRoleManagement()
      
      await initialize()
      
      expect(roleStore.fetchRoles).toHaveBeenCalled()
      expect(roleStore.fetchRoleStats).toHaveBeenCalled()
    })

    it('初始化失败时应该显示错误消息', async () => {
      roleStore.fetchRoles.mockRejectedValue(new Error('Network error'))
      
      const { initialize } = useRoleManagement()
      
      await initialize()
      
      expect(notification.showError).toHaveBeenCalledWith('初始化角色管理失败')
    })
  })

  describe('计算属性', () => {
    it('应该正确返回角色列表', () => {
      const { roles, filteredRoles, systemRoles, customRoles, activeRoles } = useRoleManagement()
      
      expect(roles.value).toEqual([mockRole, mockSystemRole])
      expect(filteredRoles.value).toEqual([mockRole, mockSystemRole])
      expect(systemRoles.value).toEqual([mockSystemRole])
      expect(customRoles.value).toEqual([mockRole])
      expect(activeRoles.value).toEqual([mockRole, mockSystemRole])
    })

    it('应该正确返回分页信息', () => {
      const { pagination } = useRoleManagement()
      
      expect(pagination.value).toEqual({
        currentPage: 1,
        pageSize: 10,
        totalCount: 2,
        totalPages: 1,
        hasNextPage: false,
        hasPrevPage: false,
      })
    })

    it('应该正确返回筛选条件', () => {
      const { filters } = useRoleManagement()
      
      expect(filters.value).toEqual({
        searchQuery: '',
        roleTypeFilter: '',
        roleStatusFilter: '',
      })
    })
  })

  describe('对话框操作', () => {
    it('应该正确打开创建对话框', () => {
      const { openCreateDialog, roleDialogVisible, dialogMode, roleFormData } = useRoleManagement()
      
      openCreateDialog()
      
      expect(roleDialogVisible.value).toBe(true)
      expect(dialogMode.value).toBe('create')
      expect(roleFormData.value).toEqual({
        name: '',
        display_name: '',
        description: '',
        role_type: 'custom',
      })
    })

    it('应该正确打开编辑对话框', () => {
      const { openEditDialog, roleDialogVisible, dialogMode, roleFormData, selectedRole } = useRoleManagement()
      
      openEditDialog(mockRole)
      
      expect(roleDialogVisible.value).toBe(true)
      expect(dialogMode.value).toBe('edit')
      expect(selectedRole.value).toEqual(mockRole)
      expect(roleFormData.value).toEqual({
        name: mockRole.name,
        display_name: mockRole.display_name,
        description: mockRole.description,
        role_type: mockRole.role_type,
      })
    })

    it('应该正确打开权限分配对话框', () => {
      const { openPermissionDialog, permissionDialogVisible, selectedRole } = useRoleManagement()
      
      openPermissionDialog(mockRole)
      
      expect(permissionDialogVisible.value).toBe(true)
      expect(selectedRole.value).toEqual(mockRole)
    })
  })

  describe('角色CRUD操作', () => {
    it('应该成功创建角色', async () => {
      const { createRole, roleDialogVisible } = useRoleManagement()
      
      const result = await createRole(mockCreateRoleRequest)
      
      expect(result).toBe(true)
      expect(roleStore.createRole).toHaveBeenCalledWith(mockCreateRoleRequest)
      expect(notification.showSuccess).toHaveBeenCalledWith(`角色 "${mockRole.display_name}" 创建成功`)
      expect(roleDialogVisible.value).toBe(false)
    })

    it('创建角色时表单验证失败应该返回false', async () => {
      const { createRole } = useRoleManagement()
      
      const invalidRequest = { ...mockCreateRoleRequest, name: '' }
      const result = await createRole(invalidRequest)
      
      expect(result).toBe(false)
      expect(roleStore.createRole).not.toHaveBeenCalled()
    })

    it('应该成功更新角色', async () => {
      const { updateRole, roleDialogVisible } = useRoleManagement()
      
      const updateRequest: UpdateRoleRequest = {
        display_name: 'Updated Role',
        description: 'Updated description',
      }
      
      const result = await updateRole('1', updateRequest)
      
      expect(result).toBe(true)
      expect(roleStore.updateRole).toHaveBeenCalledWith('1', updateRequest)
      expect(notification.showSuccess).toHaveBeenCalledWith(`角色 "${mockRole.display_name}" 更新成功`)
      expect(roleDialogVisible.value).toBe(false)
    })

    it('应该成功删除角色', async () => {
      const { deleteRole } = useRoleManagement()
      
      const result = await deleteRole(mockRole)
      
      expect(result).toBe(true)
      expect(notification.confirmDelete).toHaveBeenCalled()
      expect(roleStore.deleteRole).toHaveBeenCalledWith(mockRole.id)
      expect(notification.showSuccess).toHaveBeenCalledWith(`角色 "${mockRole.display_name}" 删除成功`)
    })

    it('不应该删除系统角色', async () => {
      const { deleteRole } = useRoleManagement()
      
      const result = await deleteRole(mockSystemRole)
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith('系统角色不能删除')
      expect(roleStore.deleteRole).not.toHaveBeenCalled()
    })

    it('用户取消删除时应该返回false', async () => {
      notification.confirmDelete.mockResolvedValue(false)
      
      const { deleteRole } = useRoleManagement()
      
      const result = await deleteRole(mockRole)
      
      expect(result).toBe(false)
      expect(roleStore.deleteRole).not.toHaveBeenCalled()
    })
  })

  describe('权限分配操作', () => {
    it('应该成功分配角色权限', async () => {
      const { assignRolePermissions, permissionDialogVisible } = useRoleManagement()
      
      const permissionData = {
        permission_ids: ['perm1', 'perm2'],
        operation: 'assign' as const,
      }
      
      const result = await assignRolePermissions('1', permissionData)
      
      expect(result).toBe(true)
      expect(roleStore.assignRolePermissions).toHaveBeenCalledWith('1', permissionData)
      expect(notification.showSuccess).toHaveBeenCalledWith(`角色 "${mockRole.display_name}" 权限分配成功`)
      expect(permissionDialogVisible.value).toBe(false)
    })
  })

  describe('批量操作', () => {
    it('应该成功批量删除角色', async () => {
      const { batchDeleteRoles, selectedRoleIds, clearSelection } = useRoleManagement()
      
      selectedRoleIds.value = ['1']
      
      const result = await batchDeleteRoles()
      
      expect(result).toBe(true)
      expect(notification.confirmBatchDelete).toHaveBeenCalledWith(1)
      expect(roleStore.batchDeleteRoles).toHaveBeenCalledWith(['1'])
      expect(notification.showSuccess).toHaveBeenCalledWith('成功删除 1 个角色')
    })

    it('没有选中角色时不应该执行批量删除', async () => {
      const { batchDeleteRoles, selectedRoleIds } = useRoleManagement()
      
      selectedRoleIds.value = []
      
      const result = await batchDeleteRoles()
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith('请选择要删除的角色')
      expect(roleStore.batchDeleteRoles).not.toHaveBeenCalled()
    })

    it('应该成功批量更新角色状态', async () => {
      const { batchUpdateRoleStatus, selectedRoleIds } = useRoleManagement()
      
      selectedRoleIds.value = ['1']
      
      const result = await batchUpdateRoleStatus('inactive')
      
      expect(result).toBe(true)
      expect(roleStore.batchUpdateRoleStatus).toHaveBeenCalledWith(['1'], 'inactive')
      expect(notification.showSuccess).toHaveBeenCalledWith('成功停用 1 个角色')
    })
  })

  describe('搜索和筛选', () => {
    it('应该正确设置搜索关键词', () => {
      const { setSearchQuery } = useRoleManagement()
      
      setSearchQuery('test')
      
      expect(roleStore.setSearchQuery).toHaveBeenCalledWith('test')
    })

    it('应该正确设置角色类型筛选', () => {
      const { setRoleTypeFilter } = useRoleManagement()
      
      setRoleTypeFilter('system')
      
      expect(roleStore.setRoleTypeFilter).toHaveBeenCalledWith('system')
    })

    it('应该正确重置筛选条件', () => {
      const { resetFilters } = useRoleManagement()
      
      resetFilters()
      
      expect(roleStore.resetFilters).toHaveBeenCalled()
    })
  })

  describe('分页操作', () => {
    it('应该正确设置页码', () => {
      const { setPage } = useRoleManagement()
      
      setPage(2)
      
      expect(roleStore.setPage).toHaveBeenCalledWith(2)
      expect(roleStore.fetchRoles).toHaveBeenCalled()
    })

    it('应该正确设置每页数量', () => {
      const { setPageSize } = useRoleManagement()
      
      setPageSize(20)
      
      expect(roleStore.setPageSize).toHaveBeenCalledWith(20)
      expect(roleStore.fetchRoles).toHaveBeenCalled()
    })
  })

  describe('选择操作', () => {
    it('应该正确选择角色', () => {
      const { selectRole, selectedRoleIds, isRoleSelected } = useRoleManagement()
      
      selectRole('1')
      
      expect(selectedRoleIds.value).toContain('1')
      expect(isRoleSelected('1')).toBe(true)
    })

    it('应该正确取消选择角色', () => {
      const { selectRole, unselectRole, selectedRoleIds, isRoleSelected } = useRoleManagement()
      
      selectRole('1')
      unselectRole('1')
      
      expect(selectedRoleIds.value).not.toContain('1')
      expect(isRoleSelected('1')).toBe(false)
    })

    it('应该正确切换角色选择状态', () => {
      const { toggleRoleSelection, selectedRoleIds } = useRoleManagement()
      
      toggleRoleSelection('1')
      expect(selectedRoleIds.value).toContain('1')
      
      toggleRoleSelection('1')
      expect(selectedRoleIds.value).not.toContain('1')
    })

    it('应该正确清空选择', () => {
      const { selectRole, clearSelection, selectedRoleIds } = useRoleManagement()
      
      selectRole('1')
      selectRole('2')
      clearSelection()
      
      expect(selectedRoleIds.value).toEqual([])
    })
  })

  describe('表单验证', () => {
    it('应该验证角色名称不能为空', () => {
      const { validateRoleForm, formValidation } = useRoleManagement()
      
      const result = validateRoleForm({ name: '', display_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.nameError).toBe('角色名称不能为空')
    })

    it('应该验证角色名称格式', () => {
      const { validateRoleForm, formValidation } = useRoleManagement()
      
      const result = validateRoleForm({ name: '123invalid', display_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.nameError).toBe('角色名称只能包含字母、数字和下划线，且必须以字母开头')
    })

    it('应该验证角色名称唯一性', () => {
      roleStore.isRoleNameExists.mockReturnValue(true)
      
      const { validateRoleForm, formValidation } = useRoleManagement()
      
      const result = validateRoleForm({ name: 'existing_role', display_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.nameError).toBe('角色名称已存在')
    })

    it('应该验证显示名称不能为空', () => {
      const { validateRoleForm, formValidation } = useRoleManagement()
      
      const result = validateRoleForm({ name: 'valid_name', display_name: '' })
      
      expect(result).toBe(false)
      expect(formValidation.value.displayNameError).toBe('显示名称不能为空')
    })

    it('有效的表单数据应该通过验证', () => {
      const { validateRoleForm } = useRoleManagement()
      
      const result = validateRoleForm({ name: 'valid_name', display_name: 'Valid Name' })
      
      expect(result).toBe(true)
    })
  })

  describe('辅助方法', () => {
    it('应该正确获取角色类型显示文本', () => {
      const { getRoleTypeText } = useRoleManagement()
      
      expect(getRoleTypeText('system')).toBe('系统角色')
      expect(getRoleTypeText('custom')).toBe('自定义角色')
    })

    it('应该正确获取角色状态显示文本', () => {
      const { getRoleStatusText } = useRoleManagement()
      
      expect(getRoleStatusText('active')).toBe('激活')
      expect(getRoleStatusText('inactive')).toBe('停用')
    })

    it('应该正确查找角色', () => {
      const { findRoleById, findRoleByName } = useRoleManagement()
      
      expect(findRoleById('1')).toEqual(mockRole)
      expect(findRoleByName('test_role')).toEqual(mockRole)
    })
  })
})