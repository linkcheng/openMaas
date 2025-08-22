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
import { useUserRoleAssign } from '../useUserRoleAssign'
import { useRoleStore } from '@/stores/permission/roleStore'
import { useNotification } from '@/composables/useNotification'
import { apiClient } from '@/utils/api'
import type {
  User,
  UserRoleAssignment,
  UserRoleAssignRequest,
  UserPermissions,
  BatchUserRoleRequest,
} from '../useUserRoleAssign'
import type { Role } from '@/types/permission/roleTypes'
import type { Permission } from '@/types/permission/permissionTypes'

// Mock dependencies
vi.mock('@/stores/permission/roleStore')
vi.mock('@/composables/useNotification')
vi.mock('@/utils/api')

// Mock data
const mockUser: User = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  profile: {
    full_name: 'Test User',
    avatar_url: 'https://example.com/avatar.jpg',
  },
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockRole: Role = {
  id: 'role1',
  name: 'test_role',
  display_name: 'Test Role',
  description: 'Test role description',
  role_type: 'custom',
  is_system_role: false,
  status: 'active',
  permissions: [],
  user_count: 1,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockPermission: Permission = {
  id: 'perm1',
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

const mockUserRoleAssignment: UserRoleAssignment = {
  user_id: '1',
  user: mockUser,
  roles: [mockRole],
  assigned_at: '2024-01-01T00:00:00Z',
  assigned_by: 'admin',
}

const mockUserPermissions: UserPermissions = {
  user_id: '1',
  permissions: [mockPermission],
  role_permissions: {
    role1: [mockPermission],
  },
  effective_permissions: [mockPermission],
}

describe('useUserRoleAssign', () => {
  let roleStore: any
  let notification: any
  let mockApiClient: any

  beforeEach(() => {
    setActivePinia(createPinia())
    
    // Mock role store
    roleStore = {
      activeRoles: [mockRole],
      fetchRoles: vi.fn().mockResolvedValue(undefined),
    }

    // Mock notification
    notification = {
      showSuccess: vi.fn(),
      showError: vi.fn(),
      showWarning: vi.fn(),
      confirm: vi.fn().mockResolvedValue(true),
    }

    // Mock API client
    mockApiClient = {
      get: vi.fn(),
      put: vi.fn(),
      post: vi.fn(),
    }

    vi.mocked(useRoleStore).mockReturnValue(roleStore)
    vi.mocked(useNotification).mockReturnValue(notification)
    vi.mocked(apiClient).mockReturnValue(mockApiClient)
  })

  describe('初始化', () => {
    it('应该正确初始化', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: {
            items: [mockUser],
            total: 1,
            page: 1,
            page_size: 10,
          },
        },
      })

      const { initialize } = useUserRoleAssign()
      
      await initialize()
      
      expect(mockApiClient.get).toHaveBeenCalledWith('/users', expect.any(Object))
      expect(roleStore.fetchRoles).toHaveBeenCalled()
    })

    it('初始化失败时应该显示错误消息', async () => {
      mockApiClient.get.mockRejectedValue(new Error('Network error'))
      
      const { initialize } = useUserRoleAssign()
      
      await initialize()
      
      expect(notification.showError).toHaveBeenCalledWith('初始化用户角色分配管理失败')
    })
  })

  describe('用户列表管理', () => {
    it('应该成功获取用户列表', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: {
            items: [mockUser],
            total: 1,
            page: 1,
            page_size: 10,
          },
        },
      })

      const { fetchUsers, users, pagination } = useUserRoleAssign()
      
      await fetchUsers()
      
      expect(users.value).toEqual([mockUser])
      expect(pagination.value.totalCount).toBe(1)
      expect(mockApiClient.get).toHaveBeenCalledWith('/users', expect.any(Object))
    })

    it('获取用户列表失败时应该抛出错误', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: false,
          error: 'Failed to fetch users',
        },
      })

      const { fetchUsers } = useUserRoleAssign()
      
      await expect(fetchUsers()).rejects.toThrow('Failed to fetch users')
    })
  })

  describe('用户角色分配', () => {
    it('应该成功获取用户角色分配信息', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: mockUserRoleAssignment,
        },
      })

      const { fetchUserRoleAssignment } = useUserRoleAssign()
      
      const result = await fetchUserRoleAssignment('1')
      
      expect(result).toEqual(mockUserRoleAssignment)
      expect(mockApiClient.get).toHaveBeenCalledWith('/users/1/roles')
    })

    it('应该成功获取用户权限信息', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: mockUserPermissions,
        },
      })

      const { fetchUserPermissions } = useUserRoleAssign()
      
      const result = await fetchUserPermissions('1')
      
      expect(result).toEqual(mockUserPermissions)
      expect(mockApiClient.get).toHaveBeenCalledWith('/users/1/permissions')
    })

    it('应该成功分配用户角色', async () => {
      mockApiClient.put.mockResolvedValue({
        data: {
          success: true,
          data: mockUserRoleAssignment,
        },
      })

      const { assignUserRoles } = useUserRoleAssign()
      
      const request: UserRoleAssignRequest = {
        user_id: '1',
        role_ids: ['role1'],
        operation: 'assign',
      }
      
      const result = await assignUserRoles(request)
      
      expect(result).toEqual(mockUserRoleAssignment)
      expect(mockApiClient.put).toHaveBeenCalledWith('/users/1/roles', {
        role_ids: ['role1'],
        operation: 'assign',
      })
    })
  })

  describe('对话框操作', () => {
    it('应该正确打开角色分配对话框', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: mockUserRoleAssignment,
        },
      })

      const {
        openAssignDialog,
        assignDialogVisible,
        selectedUser,
        currentUserAssignment,
        assignFormData,
      } = useUserRoleAssign()
      
      await openAssignDialog(mockUser)
      
      expect(assignDialogVisible.value).toBe(true)
      expect(selectedUser.value).toEqual(mockUser)
      expect(currentUserAssignment.value).toEqual(mockUserRoleAssignment)
      expect(assignFormData.value.selectedRoleIds).toEqual(['role1'])
    })

    it('应该正确打开权限查看对话框', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: mockUserPermissions,
        },
      })

      const {
        openPermissionDialog,
        permissionDialogVisible,
        selectedUser,
        currentUserPermissions,
      } = useUserRoleAssign()
      
      await openPermissionDialog(mockUser)
      
      expect(permissionDialogVisible.value).toBe(true)
      expect(selectedUser.value).toEqual(mockUser)
      expect(currentUserPermissions.value).toEqual(mockUserPermissions)
    })
  })

  describe('保存用户角色分配', () => {
    it('应该成功保存用户角色分配', async () => {
      mockApiClient.get
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: {
              items: [mockUser],
              total: 1,
              page: 1,
              page_size: 10,
            },
          },
        })
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: mockUserRoleAssignment,
          },
        })

      mockApiClient.put.mockResolvedValue({
        data: {
          success: true,
          data: mockUserRoleAssignment,
        },
      })

      const {
        openAssignDialog,
        saveUserRoleAssignment,
        assignFormData,
        assignDialogVisible,
      } = useUserRoleAssign()
      
      await openAssignDialog(mockUser)
      
      // 修改角色分配
      assignFormData.value.selectedRoleIds = ['role1', 'role2']
      
      const result = await saveUserRoleAssignment()
      
      expect(result).toBe(true)
      expect(notification.confirm).toHaveBeenCalled()
      expect(mockApiClient.put).toHaveBeenCalled()
      expect(notification.showSuccess).toHaveBeenCalledWith(`用户 "${mockUser.profile.full_name}" 角色分配成功`)
      expect(assignDialogVisible.value).toBe(false)
    })

    it('未选择用户时应该返回false', async () => {
      const { saveUserRoleAssignment } = useUserRoleAssign()
      
      const result = await saveUserRoleAssignment()
      
      expect(result).toBe(false)
      expect(notification.showError).toHaveBeenCalledWith('未选择用户')
    })

    it('角色分配没有变更时应该显示警告', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: mockUserRoleAssignment,
        },
      })

      const {
        openAssignDialog,
        saveUserRoleAssignment,
      } = useUserRoleAssign()
      
      await openAssignDialog(mockUser)
      
      const result = await saveUserRoleAssignment()
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith('角色分配没有变更')
    })

    it('用户取消确认时应该返回false', async () => {
      notification.confirm.mockResolvedValue(false)
      
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: mockUserRoleAssignment,
        },
      })

      const {
        openAssignDialog,
        saveUserRoleAssignment,
        assignFormData,
      } = useUserRoleAssign()
      
      await openAssignDialog(mockUser)
      assignFormData.value.selectedRoleIds = ['role1', 'role2']
      
      const result = await saveUserRoleAssignment()
      
      expect(result).toBe(false)
      expect(mockApiClient.put).not.toHaveBeenCalled()
    })
  })

  describe('批量操作', () => {
    it('应该成功批量分配角色', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: {
            items: [mockUser],
            total: 1,
            page: 1,
            page_size: 10,
          },
        },
      })

      mockApiClient.post.mockResolvedValue({
        data: {
          success: true,
          data: {},
        },
      })

      const { batchAssignRoles, selectedUserIds } = useUserRoleAssign()
      
      selectedUserIds.value = ['1']
      
      const result = await batchAssignRoles(['role1'])
      
      expect(result).toBe(true)
      expect(notification.confirm).toHaveBeenCalled()
      expect(mockApiClient.post).toHaveBeenCalledWith('/users/batch/roles', {
        user_ids: ['1'],
        role_ids: ['role1'],
        operation: 'assign',
      })
      expect(notification.showSuccess).toHaveBeenCalledWith('成功为 1 个用户分配角色')
    })

    it('没有选中用户时不应该执行批量分配', async () => {
      const { batchAssignRoles, selectedUserIds } = useUserRoleAssign()
      
      selectedUserIds.value = []
      
      const result = await batchAssignRoles(['role1'])
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith('请选择要分配角色的用户')
      expect(mockApiClient.post).not.toHaveBeenCalled()
    })

    it('没有选择角色时不应该执行批量分配', async () => {
      const { batchAssignRoles, selectedUserIds } = useUserRoleAssign()
      
      selectedUserIds.value = ['1']
      
      const result = await batchAssignRoles([])
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith('请选择要分配的角色')
      expect(mockApiClient.post).not.toHaveBeenCalled()
    })

    it('应该成功批量移除角色', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: {
            items: [mockUser],
            total: 1,
            page: 1,
            page_size: 10,
          },
        },
      })

      mockApiClient.post.mockResolvedValue({
        data: {
          success: true,
          data: {},
        },
      })

      const { batchUnassignRoles, selectedUserIds } = useUserRoleAssign()
      
      selectedUserIds.value = ['1']
      
      const result = await batchUnassignRoles(['role1'])
      
      expect(result).toBe(true)
      expect(notification.confirm).toHaveBeenCalled()
      expect(mockApiClient.post).toHaveBeenCalledWith('/users/batch/roles', {
        user_ids: ['1'],
        role_ids: ['role1'],
        operation: 'unassign',
      })
      expect(notification.showSuccess).toHaveBeenCalledWith('成功为 1 个用户移除角色')
    })
  })

  describe('搜索和筛选', () => {
    it('应该正确设置搜索关键词', () => {
      const { setSearchQuery, filters } = useUserRoleAssign()
      
      setSearchQuery('test')
      
      expect(filters.value.searchQuery).toBe('test')
    })

    it('应该正确设置活跃状态筛选', () => {
      const { setActiveFilter, filters } = useUserRoleAssign()
      
      setActiveFilter(true)
      
      expect(filters.value.activeFilter).toBe(true)
    })

    it('应该正确重置筛选条件', () => {
      const { resetFilters, filters } = useUserRoleAssign()
      
      resetFilters()
      
      expect(filters.value.searchQuery).toBe('')
      expect(filters.value.activeFilter).toBe('')
      expect(filters.value.hasRolesFilter).toBe('')
    })
  })

  describe('分页操作', () => {
    it('应该正确设置页码', () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: {
            items: [mockUser],
            total: 1,
            page: 2,
            page_size: 10,
          },
        },
      })

      const { setPage, pagination } = useUserRoleAssign()
      
      setPage(2)
      
      expect(mockApiClient.get).toHaveBeenCalled()
    })

    it('应该正确设置每页数量', () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          success: true,
          data: {
            items: [mockUser],
            total: 1,
            page: 1,
            page_size: 20,
          },
        },
      })

      const { setPageSize } = useUserRoleAssign()
      
      setPageSize(20)
      
      expect(mockApiClient.get).toHaveBeenCalled()
    })
  })

  describe('选择操作', () => {
    it('应该正确选择用户', () => {
      const { selectUser, selectedUserIds, isUserSelected } = useUserRoleAssign()
      
      selectUser('1')
      
      expect(selectedUserIds.value).toContain('1')
      expect(isUserSelected('1')).toBe(true)
    })

    it('应该正确取消选择用户', () => {
      const { selectUser, unselectUser, selectedUserIds, isUserSelected } = useUserRoleAssign()
      
      selectUser('1')
      unselectUser('1')
      
      expect(selectedUserIds.value).not.toContain('1')
      expect(isUserSelected('1')).toBe(false)
    })

    it('应该正确切换用户选择状态', () => {
      const { toggleUserSelection, selectedUserIds } = useUserRoleAssign()
      
      toggleUserSelection('1')
      expect(selectedUserIds.value).toContain('1')
      
      toggleUserSelection('1')
      expect(selectedUserIds.value).not.toContain('1')
    })

    it('应该正确清空选择', () => {
      const { selectUser, clearSelection, selectedUserIds } = useUserRoleAssign()
      
      selectUser('1')
      selectUser('2')
      clearSelection()
      
      expect(selectedUserIds.value).toEqual([])
    })
  })

  describe('辅助方法', () => {
    it('应该正确查找用户', () => {
      const { users, findUserById } = useUserRoleAssign()
      
      users.value = [mockUser]
      
      expect(findUserById('1')).toEqual(mockUser)
      expect(findUserById('nonexistent')).toBeUndefined()
    })

    it('应该正确获取用户状态显示文本', () => {
      const { getUserStatusText } = useUserRoleAssign()
      
      expect(getUserStatusText(true)).toBe('激活')
      expect(getUserStatusText(false)).toBe('停用')
    })

    it('应该正确获取用户角色显示文本', () => {
      const { getUserRolesText } = useUserRoleAssign()
      
      expect(getUserRolesText([])).toBe('无角色')
      expect(getUserRolesText([mockRole])).toBe('Test Role')
    })

    it('应该正确获取权限来源角色', () => {
      const { getPermissionSourceRoles, currentUserPermissions, availableRoles } = useUserRoleAssign()
      
      currentUserPermissions.value = mockUserPermissions
      availableRoles.value = [mockRole]
      
      const sourceRoles = getPermissionSourceRoles('perm1')
      
      expect(sourceRoles).toEqual([mockRole])
    })
  })
})