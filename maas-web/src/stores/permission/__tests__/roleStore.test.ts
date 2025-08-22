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

import { describe, it, expect, beforeEach, vi, type Mock } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRoleStore } from '../roleStore'

// Unmock Pinia for this test file
vi.unmock('pinia')
import { apiClient } from '@/utils/api'
import type { Role, CreateRoleRequest, UpdateRoleRequest } from '@/types/permission/roleTypes'
import type { ApiResponse, PaginatedResponse } from '@/types/permission/commonTypes'

// Mock API client
vi.mock('@/utils/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockApiClient = apiClient as {
  get: Mock
  post: Mock
  put: Mock
  delete: Mock
}

describe('useRoleStore', () => {
  let roleStore: ReturnType<typeof useRoleStore>

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
    user_count: 5,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 'admin',
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
    user_count: 2,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  }

  const mockPaginatedResponse: PaginatedResponse<Role> = {
    items: [mockRole, mockSystemRole],
    total: 2,
    page: 1,
    page_size: 10,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    roleStore = useRoleStore()
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      expect(roleStore.roles).toEqual([])
      expect(roleStore.loading).toBe(false)
      expect(roleStore.error).toBe(null)
      expect(roleStore.currentPage).toBe(1)
      expect(roleStore.pageSize).toBe(10)
      expect(roleStore.totalCount).toBe(0)
      expect(roleStore.searchQuery).toBe('')
      expect(roleStore.roleTypeFilter).toBe('')
      expect(roleStore.roleStatusFilter).toBe('')
      expect(roleStore.sortBy).toBe('created_at')
      expect(roleStore.sortOrder).toBe('desc')
    })

    it('计算属性应该返回正确的初始值', () => {
      expect(roleStore.totalPages).toBe(0)
      expect(roleStore.hasNextPage).toBe(false)
      expect(roleStore.hasPrevPage).toBe(false)
      expect(roleStore.filteredRoles).toEqual([])
      expect(roleStore.systemRoles).toEqual([])
      expect(roleStore.customRoles).toEqual([])
      expect(roleStore.activeRoles).toEqual([])
    })
  })

  describe('基础操作方法', () => {
    it('setLoading 应该设置加载状态', () => {
      roleStore.setLoading(true)
      expect(roleStore.loading).toBe(true)

      roleStore.setLoading(false)
      expect(roleStore.loading).toBe(false)
    })

    it('setError 应该设置错误信息', () => {
      const errorMessage = 'Test error'
      roleStore.setError(errorMessage)
      expect(roleStore.error).toBe(errorMessage)
    })

    it('clearError 应该清除错误信息', () => {
      roleStore.setError('Test error')
      roleStore.clearError()
      expect(roleStore.error).toBe(null)
    })

    it('resetFilters 应该重置所有筛选条件', () => {
      roleStore.setSearchQuery('test')
      roleStore.setRoleTypeFilter('system')
      roleStore.setRoleStatusFilter('active')
      roleStore.setPage(2)

      roleStore.resetFilters()

      expect(roleStore.searchQuery).toBe('')
      expect(roleStore.roleTypeFilter).toBe('')
      expect(roleStore.roleStatusFilter).toBe('')
      expect(roleStore.currentPage).toBe(1)
    })
  })

  describe('fetchRoles', () => {
    it('应该成功获取角色列表', async () => {
      const mockResponse: ApiResponse<PaginatedResponse<Role>> = {
        success: true,
        data: mockPaginatedResponse,
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      await roleStore.fetchRoles()

      expect(mockApiClient.get).toHaveBeenCalledWith('/roles', {
        page: 1,
        page_size: 10,
        search: undefined,
        role_type: undefined,
        status: undefined,
        sort_by: 'created_at',
        sort_order: 'desc',
      })

      expect(roleStore.roles).toEqual(mockPaginatedResponse.items)
      expect(roleStore.totalCount).toBe(mockPaginatedResponse.total)
      expect(roleStore.currentPage).toBe(mockPaginatedResponse.page)
      expect(roleStore.pageSize).toBe(mockPaginatedResponse.page_size)
      expect(roleStore.loading).toBe(false)
      expect(roleStore.error).toBe(null)
    })

    it('应该处理API错误', async () => {
      const errorMessage = 'API Error'
      mockApiClient.get.mockRejectedValue(new Error(errorMessage))

      await expect(roleStore.fetchRoles()).rejects.toThrow(errorMessage)

      expect(roleStore.loading).toBe(false)
      expect(roleStore.error).toBe(errorMessage)
    })

    it('应该处理API响应错误', async () => {
      const mockResponse: ApiResponse<PaginatedResponse<Role>> = {
        success: false,
        error: 'Server error',
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      await expect(roleStore.fetchRoles()).rejects.toThrow('Server error')

      expect(roleStore.error).toBe('Server error')
    })
  })

  describe('fetchRoleById', () => {
    it('应该成功获取角色详情', async () => {
      const mockResponse: ApiResponse<Role> = {
        success: true,
        data: mockRole,
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await roleStore.fetchRoleById('1')

      expect(mockApiClient.get).toHaveBeenCalledWith('/roles/1')
      expect(result).toEqual(mockRole)
      expect(roleStore.loading).toBe(false)
      expect(roleStore.error).toBe(null)
    })

    it('应该使用缓存的角色数据', async () => {
      // 先通过API调用设置缓存
      const mockResponse: ApiResponse<Role> = {
        success: true,
        data: mockRole,
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      // 第一次调用设置缓存
      await roleStore.fetchRoleById('1')
      
      // 清除mock调用记录
      vi.clearAllMocks()
      
      // 第二次调用应该使用缓存
      const result = await roleStore.fetchRoleById('1', true)

      expect(mockApiClient.get).not.toHaveBeenCalled()
      expect(result).toEqual(mockRole)
    })

    it('应该处理获取角色详情的错误', async () => {
      const errorMessage = 'Role not found'
      mockApiClient.get.mockRejectedValue(new Error(errorMessage))

      await expect(roleStore.fetchRoleById('1')).rejects.toThrow(errorMessage)

      expect(roleStore.error).toBe(errorMessage)
    })
  })

  describe('createRole', () => {
    it('应该成功创建角色', async () => {
      const createRequest: CreateRoleRequest = {
        name: 'new_role',
        display_name: 'New Role',
        description: 'New role description',
        role_type: 'custom',
      }

      const mockResponse: ApiResponse<Role> = {
        success: true,
        data: mockRole,
      }

      mockApiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await roleStore.createRole(createRequest)

      expect(mockApiClient.post).toHaveBeenCalledWith('/roles', createRequest)
      expect(result).toEqual(mockRole)
      expect(roleStore.roles[0]).toEqual(mockRole) // Check first item since unshift is used
      expect(roleStore.totalCount).toBe(1)
      expect(roleStore.loading).toBe(false)
      expect(roleStore.error).toBe(null)
    })

    it('应该处理创建角色的错误', async () => {
      const createRequest: CreateRoleRequest = {
        name: 'new_role',
        display_name: 'New Role',
        role_type: 'custom',
      }

      const errorMessage = 'Role name already exists'
      mockApiClient.post.mockRejectedValue(new Error(errorMessage))

      await expect(roleStore.createRole(createRequest)).rejects.toThrow(errorMessage)

      expect(roleStore.error).toBe(errorMessage)
    })
  })

  describe('updateRole', () => {
    beforeEach(() => {
      roleStore.roles = [mockRole]
    })

    it('应该成功更新角色', async () => {
      const updateRequest: UpdateRoleRequest = {
        display_name: 'Updated Role',
        description: 'Updated description',
      }

      const updatedRole = { ...mockRole, ...updateRequest }
      const mockResponse: ApiResponse<Role> = {
        success: true,
        data: updatedRole,
      }

      mockApiClient.put.mockResolvedValue({ data: mockResponse })

      const result = await roleStore.updateRole('1', updateRequest)

      expect(mockApiClient.put).toHaveBeenCalledWith('/roles/1', updateRequest)
      expect(result).toEqual(updatedRole)
      expect(roleStore.roles[0]).toEqual(updatedRole)
      expect(roleStore.loading).toBe(false)
      expect(roleStore.error).toBe(null)
    })

    it('应该处理更新角色的错误', async () => {
      const updateRequest: UpdateRoleRequest = {
        display_name: 'Updated Role',
      }

      const errorMessage = 'Update failed'
      mockApiClient.put.mockRejectedValue(new Error(errorMessage))

      await expect(roleStore.updateRole('1', updateRequest)).rejects.toThrow(errorMessage)

      expect(roleStore.error).toBe(errorMessage)
    })
  })

  describe('deleteRole', () => {
    beforeEach(() => {
      roleStore.roles = [mockRole]
      roleStore.totalCount = 1
    })

    it('应该成功删除角色', async () => {
      const mockResponse: ApiResponse<void> = {
        success: true,
      }

      mockApiClient.delete.mockResolvedValue({ data: mockResponse })

      await roleStore.deleteRole('1')

      expect(mockApiClient.delete).toHaveBeenCalledWith('/roles/1')
      expect(roleStore.roles).toEqual([])
      expect(roleStore.totalCount).toBe(0)
      expect(roleStore.loading).toBe(false)
      expect(roleStore.error).toBe(null)
    })

    it('应该处理删除角色的错误', async () => {
      const errorMessage = 'Delete failed'
      mockApiClient.delete.mockRejectedValue(new Error(errorMessage))

      await expect(roleStore.deleteRole('1')).rejects.toThrow(errorMessage)

      expect(roleStore.error).toBe(errorMessage)
      expect(roleStore.roles).toEqual([mockRole]) // 角色应该仍然存在
    })
  })

  describe('计算属性', () => {
    beforeEach(() => {
      roleStore.roles = [mockRole, mockSystemRole]
      roleStore.totalCount = 2
      roleStore.pageSize = 10
    })

    it('totalPages 应该计算正确的总页数', () => {
      expect(roleStore.totalPages).toBe(1)

      roleStore.totalCount = 25
      expect(roleStore.totalPages).toBe(3)
    })

    it('hasNextPage 应该正确判断是否有下一页', () => {
      roleStore.currentPage = 1
      roleStore.totalCount = 25
      roleStore.pageSize = 10
      expect(roleStore.hasNextPage).toBe(true)

      roleStore.currentPage = 3
      expect(roleStore.hasNextPage).toBe(false)
    })

    it('hasPrevPage 应该正确判断是否有上一页', () => {
      roleStore.currentPage = 1
      expect(roleStore.hasPrevPage).toBe(false)

      roleStore.currentPage = 2
      expect(roleStore.hasPrevPage).toBe(true)
    })

    it('systemRoles 应该返回系统角色', () => {
      expect(roleStore.systemRoles).toEqual([mockSystemRole])
    })

    it('customRoles 应该返回自定义角色', () => {
      expect(roleStore.customRoles).toEqual([mockRole])
    })

    it('activeRoles 应该返回活跃角色', () => {
      expect(roleStore.activeRoles).toEqual([mockRole, mockSystemRole])
    })

    it('filteredRoles 应该根据搜索条件筛选角色', () => {
      roleStore.setSearchQuery('test')
      expect(roleStore.filteredRoles).toEqual([mockRole])

      roleStore.setSearchQuery('admin')
      expect(roleStore.filteredRoles).toEqual([mockSystemRole])
    })

    it('filteredRoles 应该根据角色类型筛选角色', () => {
      roleStore.setRoleTypeFilter('system')
      expect(roleStore.filteredRoles).toEqual([mockSystemRole])

      roleStore.setRoleTypeFilter('custom')
      expect(roleStore.filteredRoles).toEqual([mockRole])
    })
  })

  describe('辅助方法', () => {
    beforeEach(() => {
      roleStore.roles = [mockRole, mockSystemRole]
    })

    it('findRoleById 应该根据ID查找角色', () => {
      const result = roleStore.findRoleById('1')
      expect(result).toEqual(mockRole)

      const notFound = roleStore.findRoleById('999')
      expect(notFound).toBeUndefined()
    })

    it('findRoleByName 应该根据名称查找角色', () => {
      const result = roleStore.findRoleByName('test_role')
      expect(result).toEqual(mockRole)

      const notFound = roleStore.findRoleByName('nonexistent')
      expect(notFound).toBeUndefined()
    })

    it('isRoleNameExists 应该检查角色名称是否存在', () => {
      expect(roleStore.isRoleNameExists('test_role')).toBe(true)
      expect(roleStore.isRoleNameExists('nonexistent')).toBe(false)
      expect(roleStore.isRoleNameExists('test_role', '1')).toBe(false) // 排除自身
    })
  })

  describe('分页和筛选方法', () => {
    it('setPage 应该设置页码', () => {
      roleStore.setPage(5)
      expect(roleStore.currentPage).toBe(5)
    })

    it('setPageSize 应该设置每页数量并重置页码', () => {
      roleStore.setPage(3)
      roleStore.setPageSize(20)
      expect(roleStore.pageSize).toBe(20)
      expect(roleStore.currentPage).toBe(1)
    })

    it('setSearchQuery 应该设置搜索关键词并重置页码', () => {
      roleStore.setPage(3)
      roleStore.setSearchQuery('test')
      expect(roleStore.searchQuery).toBe('test')
      expect(roleStore.currentPage).toBe(1)
    })

    it('setRoleTypeFilter 应该设置角色类型筛选并重置页码', () => {
      roleStore.setPage(3)
      roleStore.setRoleTypeFilter('system')
      expect(roleStore.roleTypeFilter).toBe('system')
      expect(roleStore.currentPage).toBe(1)
    })

    it('setRoleStatusFilter 应该设置角色状态筛选并重置页码', () => {
      roleStore.setPage(3)
      roleStore.setRoleStatusFilter('active')
      expect(roleStore.roleStatusFilter).toBe('active')
      expect(roleStore.currentPage).toBe(1)
    })

    it('setSorting 应该设置排序字段和方向', () => {
      roleStore.setSorting('name', 'asc')
      expect(roleStore.sortBy).toBe('name')
      expect(roleStore.sortOrder).toBe('asc')
    })
  })
})