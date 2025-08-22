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
import { usePermissionStore } from '../permissionStore'

// Unmock Pinia for this test file
vi.unmock('pinia')
import { apiClient } from '@/utils/api'
import type { 
  Permission, 
  CreatePermissionRequest, 
  UpdatePermissionRequest,
  PermissionStats,
} from '@/types/permission/permissionTypes'
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

describe('usePermissionStore', () => {
  let permissionStore: ReturnType<typeof usePermissionStore>

  // Mock data
  const mockPermission: Permission = {
    id: '1',
    name: 'user.create',
    display_name: 'Create User',
    description: 'Permission to create users',
    resource: 'user',
    action: 'create',
    module: 'user_management',
    status: 'active',
    is_system_permission: true,
    level: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 'admin',
  }

  const mockChildPermission: Permission = {
    id: '2',
    name: 'user.profile.update',
    display_name: 'Update User Profile',
    description: 'Permission to update user profiles',
    resource: 'user',
    action: 'update',
    module: 'user_management',
    status: 'active',
    is_system_permission: false,
    parent_id: '1',
    level: 2,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 'admin',
  }

  const mockPaginatedResponse: PaginatedResponse<Permission> = {
    items: [mockPermission, mockChildPermission],
    total: 2,
    page: 1,
    page_size: 10,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  }

  const mockStats: PermissionStats = {
    total_permissions: 2,
    system_permissions: 1,
    custom_permissions: 1,
    permissions_by_module: {
      user_management: 2,
      permission_management: 0,
      provider_management: 0,
      model_management: 0,
      chat_management: 0,
      system_management: 0,
      audit_management: 0,
    },
    permissions_by_resource: {
      user: 2,
      role: 0,
      permission: 0,
      provider: 0,
      model: 0,
      chat: 0,
      system: 0,
      menu: 0,
      audit: 0,
      config: 0,
    },
    recent_permissions: [mockPermission, mockChildPermission],
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    permissionStore = usePermissionStore()
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      expect(permissionStore.permissions).toEqual([])
      expect(permissionStore.permissionTree).toEqual([])
      expect(permissionStore.loading).toBe(false)
      expect(permissionStore.error).toBe(null)
      expect(permissionStore.currentPage).toBe(1)
      expect(permissionStore.pageSize).toBe(10)
      expect(permissionStore.totalCount).toBe(0)
      expect(permissionStore.searchQuery).toBe('')
      expect(permissionStore.resourceFilter).toBe('')
      expect(permissionStore.actionFilter).toBe('')
      expect(permissionStore.moduleFilter).toBe('')
      expect(permissionStore.statusFilter).toBe('')
      expect(permissionStore.systemOnlyFilter).toBe(false)
      expect(permissionStore.sortBy).toBe('created_at')
      expect(permissionStore.sortOrder).toBe('desc')
    })

    it('计算属性应该返回正确的初始值', () => {
      expect(permissionStore.totalPages).toBe(0)
      expect(permissionStore.hasNextPage).toBe(false)
      expect(permissionStore.hasPrevPage).toBe(false)
      expect(permissionStore.filteredPermissions).toEqual([])
      expect(permissionStore.systemPermissions).toEqual([])
      expect(permissionStore.customPermissions).toEqual([])
      expect(permissionStore.activePermissions).toEqual([])
      expect(permissionStore.rootPermissions).toEqual([])
      expect(permissionStore.availableModules).toEqual([])
      expect(permissionStore.availableResources).toEqual([])
    })
  })

  describe('基础操作方法', () => {
    it('setLoading 应该设置加载状态', () => {
      permissionStore.setLoading(true)
      expect(permissionStore.loading).toBe(true)

      permissionStore.setLoading(false)
      expect(permissionStore.loading).toBe(false)
    })

    it('setError 应该设置错误信息', () => {
      const errorMessage = 'Test error'
      permissionStore.setError(errorMessage)
      expect(permissionStore.error).toBe(errorMessage)
    })

    it('clearError 应该清除错误信息', () => {
      permissionStore.setError('Test error')
      permissionStore.clearError()
      expect(permissionStore.error).toBe(null)
    })

    it('resetFilters 应该重置所有筛选条件', () => {
      permissionStore.setSearchQuery('test')
      permissionStore.setResourceFilter('user')
      permissionStore.setActionFilter('create')
      permissionStore.setModuleFilter('user_management')
      permissionStore.setStatusFilter('active')
      permissionStore.setSystemOnlyFilter(true)
      permissionStore.setPage(2)

      permissionStore.resetFilters()

      expect(permissionStore.searchQuery).toBe('')
      expect(permissionStore.resourceFilter).toBe('')
      expect(permissionStore.actionFilter).toBe('')
      expect(permissionStore.moduleFilter).toBe('')
      expect(permissionStore.statusFilter).toBe('')
      expect(permissionStore.systemOnlyFilter).toBe(false)
      expect(permissionStore.currentPage).toBe(1)
    })
  })

  describe('fetchPermissions', () => {
    it('应该成功获取权限列表', async () => {
      const mockResponse: ApiResponse<PaginatedResponse<Permission>> = {
        success: true,
        data: mockPaginatedResponse,
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      await permissionStore.fetchPermissions()

      expect(mockApiClient.get).toHaveBeenCalledWith('/permissions', {
        page: 1,
        page_size: 10,
        search: undefined,
        resource: undefined,
        action: undefined,
        module: undefined,
        status: undefined,
        system_only: undefined,
        sort_by: 'created_at',
        sort_order: 'desc',
      })

      expect(permissionStore.permissions).toEqual(mockPaginatedResponse.items)
      expect(permissionStore.totalCount).toBe(mockPaginatedResponse.total)
      expect(permissionStore.currentPage).toBe(mockPaginatedResponse.page)
      expect(permissionStore.pageSize).toBe(mockPaginatedResponse.page_size)
      expect(permissionStore.loading).toBe(false)
      expect(permissionStore.error).toBe(null)
    })

    it('应该处理API错误', async () => {
      const errorMessage = 'API Error'
      mockApiClient.get.mockRejectedValue(new Error(errorMessage))

      await expect(permissionStore.fetchPermissions()).rejects.toThrow(errorMessage)

      expect(permissionStore.loading).toBe(false)
      expect(permissionStore.error).toBe(errorMessage)
    })

    it('应该处理API响应错误', async () => {
      const mockResponse: ApiResponse<PaginatedResponse<Permission>> = {
        success: false,
        error: 'Server error',
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      await expect(permissionStore.fetchPermissions()).rejects.toThrow('Server error')

      expect(permissionStore.error).toBe('Server error')
    })
  })

  describe('fetchPermissionById', () => {
    it('应该成功获取权限详情', async () => {
      const mockResponse: ApiResponse<Permission> = {
        success: true,
        data: mockPermission,
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await permissionStore.fetchPermissionById('1')

      expect(mockApiClient.get).toHaveBeenCalledWith('/permissions/1')
      expect(result).toEqual(mockPermission)
      expect(permissionStore.loading).toBe(false)
      expect(permissionStore.error).toBe(null)
    })

    it('应该使用缓存的权限数据', async () => {
      // 先设置缓存
      permissionStore.permissions = [mockPermission]
      
      const result = await permissionStore.fetchPermissionById('1', true)

      expect(mockApiClient.get).not.toHaveBeenCalled()
      expect(result).toEqual(mockPermission)
    })

    it('应该处理获取权限详情的错误', async () => {
      const errorMessage = 'Permission not found'
      mockApiClient.get.mockRejectedValue(new Error(errorMessage))

      await expect(permissionStore.fetchPermissionById('1')).rejects.toThrow(errorMessage)

      expect(permissionStore.error).toBe(errorMessage)
    })
  })

  describe('createPermission', () => {
    it('应该成功创建权限', async () => {
      const createRequest: CreatePermissionRequest = {
        name: 'user.delete',
        display_name: 'Delete User',
        description: 'Permission to delete users',
        resource: 'user',
        action: 'delete',
        module: 'user_management',
      }

      const mockResponse: ApiResponse<Permission> = {
        success: true,
        data: mockPermission,
      }

      mockApiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await permissionStore.createPermission(createRequest)

      expect(mockApiClient.post).toHaveBeenCalledWith('/permissions', createRequest)
      expect(result).toEqual(mockPermission)
      expect(permissionStore.permissions).toContain(mockPermission)
      expect(permissionStore.totalCount).toBe(1)
      expect(permissionStore.loading).toBe(false)
      expect(permissionStore.error).toBe(null)
    })

    it('应该处理创建权限的错误', async () => {
      const createRequest: CreatePermissionRequest = {
        name: 'user.delete',
        display_name: 'Delete User',
        resource: 'user',
        action: 'delete',
        module: 'user_management',
      }

      const errorMessage = 'Permission name already exists'
      mockApiClient.post.mockRejectedValue(new Error(errorMessage))

      await expect(permissionStore.createPermission(createRequest)).rejects.toThrow(errorMessage)

      expect(permissionStore.error).toBe(errorMessage)
    })
  })

  describe('updatePermission', () => {
    beforeEach(() => {
      permissionStore.permissions = [mockPermission]
    })

    it('应该成功更新权限', async () => {
      const updateRequest: UpdatePermissionRequest = {
        display_name: 'Updated Permission',
        description: 'Updated description',
      }

      const updatedPermission = { ...mockPermission, ...updateRequest }
      const mockResponse: ApiResponse<Permission> = {
        success: true,
        data: updatedPermission,
      }

      mockApiClient.put.mockResolvedValue({ data: mockResponse })

      const result = await permissionStore.updatePermission('1', updateRequest)

      expect(mockApiClient.put).toHaveBeenCalledWith('/permissions/1', updateRequest)
      expect(result).toEqual(updatedPermission)
      expect(permissionStore.permissions[0]).toEqual(updatedPermission)
      expect(permissionStore.loading).toBe(false)
      expect(permissionStore.error).toBe(null)
    })

    it('应该处理更新权限的错误', async () => {
      const updateRequest: UpdatePermissionRequest = {
        display_name: 'Updated Permission',
      }

      const errorMessage = 'Update failed'
      mockApiClient.put.mockRejectedValue(new Error(errorMessage))

      await expect(permissionStore.updatePermission('1', updateRequest)).rejects.toThrow(errorMessage)

      expect(permissionStore.error).toBe(errorMessage)
    })
  })

  describe('deletePermission', () => {
    beforeEach(() => {
      permissionStore.permissions = [mockPermission]
      permissionStore.totalCount = 1
    })

    it('应该成功删除权限', async () => {
      const mockResponse: ApiResponse<void> = {
        success: true,
      }

      mockApiClient.delete.mockResolvedValue({ data: mockResponse })

      await permissionStore.deletePermission('1')

      expect(mockApiClient.delete).toHaveBeenCalledWith('/permissions/1')
      expect(permissionStore.permissions).toEqual([])
      expect(permissionStore.totalCount).toBe(0)
      expect(permissionStore.loading).toBe(false)
      expect(permissionStore.error).toBe(null)
    })

    it('应该处理删除权限的错误', async () => {
      const errorMessage = 'Delete failed'
      mockApiClient.delete.mockRejectedValue(new Error(errorMessage))

      await expect(permissionStore.deletePermission('1')).rejects.toThrow(errorMessage)

      expect(permissionStore.error).toBe(errorMessage)
      expect(permissionStore.permissions).toEqual([mockPermission]) // 权限应该仍然存在
    })
  })

  describe('fetchPermissionStats', () => {
    it('应该成功获取权限统计信息', async () => {
      const mockResponse: ApiResponse<PermissionStats> = {
        success: true,
        data: mockStats,
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await permissionStore.fetchPermissionStats()

      expect(mockApiClient.get).toHaveBeenCalledWith('/permissions/stats')
      expect(result).toEqual(mockStats)
      expect(permissionStore.stats).toEqual(mockStats)
      expect(permissionStore.loading).toBe(false)
      expect(permissionStore.error).toBe(null)
    })

    it('应该处理获取统计信息的错误', async () => {
      const errorMessage = 'Stats fetch failed'
      mockApiClient.get.mockRejectedValue(new Error(errorMessage))

      await expect(permissionStore.fetchPermissionStats()).rejects.toThrow(errorMessage)

      expect(permissionStore.error).toBe(errorMessage)
    })
  })

  describe('计算属性', () => {
    beforeEach(() => {
      permissionStore.permissions = [mockPermission, mockChildPermission]
      permissionStore.totalCount = 2
      permissionStore.pageSize = 10
    })

    it('totalPages 应该计算正确的总页数', () => {
      expect(permissionStore.totalPages).toBe(1)

      permissionStore.totalCount = 25
      expect(permissionStore.totalPages).toBe(3)
    })

    it('hasNextPage 应该正确判断是否有下一页', () => {
      permissionStore.currentPage = 1
      permissionStore.totalCount = 25
      permissionStore.pageSize = 10
      expect(permissionStore.hasNextPage).toBe(true)

      permissionStore.currentPage = 3
      expect(permissionStore.hasNextPage).toBe(false)
    })

    it('hasPrevPage 应该正确判断是否有上一页', () => {
      permissionStore.currentPage = 1
      expect(permissionStore.hasPrevPage).toBe(false)

      permissionStore.currentPage = 2
      expect(permissionStore.hasPrevPage).toBe(true)
    })

    it('systemPermissions 应该返回系统权限', () => {
      expect(permissionStore.systemPermissions).toEqual([mockPermission])
    })

    it('customPermissions 应该返回自定义权限', () => {
      expect(permissionStore.customPermissions).toEqual([mockChildPermission])
    })

    it('activePermissions 应该返回活跃权限', () => {
      expect(permissionStore.activePermissions).toEqual([mockPermission, mockChildPermission])
    })

    it('rootPermissions 应该返回根权限', () => {
      expect(permissionStore.rootPermissions).toEqual([mockPermission])
    })

    it('availableModules 应该返回可用模块列表', () => {
      expect(permissionStore.availableModules).toEqual(['user_management'])
    })

    it('availableResources 应该返回可用资源列表', () => {
      expect(permissionStore.availableResources).toEqual(['user'])
    })

    it('filteredPermissions 应该根据搜索条件筛选权限', () => {
      permissionStore.setSearchQuery('create')
      expect(permissionStore.filteredPermissions).toEqual([mockPermission])

      permissionStore.setSearchQuery('profile')
      expect(permissionStore.filteredPermissions).toEqual([mockChildPermission])
    })

    it('filteredPermissions 应该根据资源类型筛选权限', () => {
      permissionStore.setResourceFilter('user')
      expect(permissionStore.filteredPermissions).toEqual([mockPermission, mockChildPermission])
    })

    it('filteredPermissions 应该根据系统权限筛选', () => {
      permissionStore.setSystemOnlyFilter(true)
      expect(permissionStore.filteredPermissions).toEqual([mockPermission])
    })
  })

  describe('权限验证方法', () => {
    beforeEach(() => {
      permissionStore.permissions = [mockPermission, mockChildPermission]
    })

    it('checkPermission 应该正确验证权限', () => {
      const result = permissionStore.checkPermission('user.create')
      expect(result.hasPermission).toBe(true)
      expect(result.message).toBe('拥有权限 user.create')

      const notFoundResult = permissionStore.checkPermission('nonexistent.permission')
      expect(notFoundResult.hasPermission).toBe(false)
      expect(notFoundResult.missingPermissions).toEqual(['nonexistent.permission'])
    })

    it('checkPermissions 应该批量验证权限', () => {
      const result = permissionStore.checkPermissions(['user.create', 'user.profile.update'])
      expect(result.hasPermission).toBe(true)
      expect(result.message).toBe('拥有所有权限')

      const missingResult = permissionStore.checkPermissions(['user.create', 'nonexistent.permission'])
      expect(missingResult.hasPermission).toBe(false)
      expect(missingResult.missingPermissions).toEqual(['nonexistent.permission'])
    })
  })

  describe('辅助方法', () => {
    beforeEach(() => {
      permissionStore.permissions = [mockPermission, mockChildPermission]
    })

    it('findPermissionById 应该根据ID查找权限', () => {
      const result = permissionStore.findPermissionById('1')
      expect(result).toEqual(mockPermission)

      const notFound = permissionStore.findPermissionById('999')
      expect(notFound).toBeUndefined()
    })

    it('findPermissionByName 应该根据名称查找权限', () => {
      const result = permissionStore.findPermissionByName('user.create')
      expect(result).toEqual(mockPermission)

      const notFound = permissionStore.findPermissionByName('nonexistent')
      expect(notFound).toBeUndefined()
    })

    it('isPermissionNameExists 应该检查权限名称是否存在', () => {
      expect(permissionStore.isPermissionNameExists('user.create')).toBe(true)
      expect(permissionStore.isPermissionNameExists('nonexistent')).toBe(false)
      expect(permissionStore.isPermissionNameExists('user.create', '1')).toBe(false) // 排除自身
    })

    it('getChildPermissions 应该获取子权限', () => {
      const children = permissionStore.getChildPermissions('1')
      expect(children).toEqual([mockChildPermission])
    })

    it('getParentPermission 应该获取父权限', () => {
      const parent = permissionStore.getParentPermission('2')
      expect(parent).toEqual(mockPermission)

      const noParent = permissionStore.getParentPermission('1')
      expect(noParent).toBeUndefined()
    })
  })

  describe('权限树操作', () => {
    beforeEach(() => {
      permissionStore.permissions = [mockPermission, mockChildPermission]
      permissionStore.buildPermissionTree()
    })

    it('buildPermissionTree 应该构建正确的树结构', () => {
      expect(permissionStore.permissionTree).toHaveLength(1)
      expect(permissionStore.permissionTree[0].permission).toEqual(mockPermission)
      expect(permissionStore.permissionTree[0].children).toHaveLength(1)
      expect(permissionStore.permissionTree[0].children[0].permission).toEqual(mockChildPermission)
    })

    it('toggleNodeExpanded 应该切换节点展开状态', () => {
      expect(permissionStore.expandedNodes.has('1')).toBe(false)
      
      permissionStore.toggleNodeExpanded('1')
      expect(permissionStore.expandedNodes.has('1')).toBe(true)
      
      permissionStore.toggleNodeExpanded('1')
      expect(permissionStore.expandedNodes.has('1')).toBe(false)
    })

    it('toggleNodeSelected 应该切换节点选中状态', () => {
      expect(permissionStore.selectedNodes.has('1')).toBe(false)
      
      permissionStore.toggleNodeSelected('1')
      expect(permissionStore.selectedNodes.has('1')).toBe(true)
      
      permissionStore.toggleNodeSelected('1')
      expect(permissionStore.selectedNodes.has('1')).toBe(false)
    })

    it('expandAllNodes 应该展开所有节点', () => {
      permissionStore.expandAllNodes()
      expect(permissionStore.expandedNodes.has('1')).toBe(true)
      expect(permissionStore.expandedNodes.has('2')).toBe(true)
    })

    it('collapseAllNodes 应该折叠所有节点', () => {
      permissionStore.expandAllNodes()
      permissionStore.collapseAllNodes()
      expect(permissionStore.expandedNodes.size).toBe(0)
    })

    it('selectAllNodes 应该选中所有节点', () => {
      permissionStore.selectAllNodes()
      expect(permissionStore.selectedNodes.has('1')).toBe(true)
      expect(permissionStore.selectedNodes.has('2')).toBe(true)
    })

    it('deselectAllNodes 应该取消选中所有节点', () => {
      permissionStore.selectAllNodes()
      permissionStore.deselectAllNodes()
      expect(permissionStore.selectedNodes.size).toBe(0)
    })
  })

  describe('分页和筛选方法', () => {
    it('setPage 应该设置页码', () => {
      permissionStore.setPage(5)
      expect(permissionStore.currentPage).toBe(5)
    })

    it('setPageSize 应该设置每页数量并重置页码', () => {
      permissionStore.setPage(3)
      permissionStore.setPageSize(20)
      expect(permissionStore.pageSize).toBe(20)
      expect(permissionStore.currentPage).toBe(1)
    })

    it('setSearchQuery 应该设置搜索关键词并重置页码', () => {
      permissionStore.setPage(3)
      permissionStore.setSearchQuery('test')
      expect(permissionStore.searchQuery).toBe('test')
      expect(permissionStore.currentPage).toBe(1)
    })

    it('setResourceFilter 应该设置资源筛选并重置页码', () => {
      permissionStore.setPage(3)
      permissionStore.setResourceFilter('user')
      expect(permissionStore.resourceFilter).toBe('user')
      expect(permissionStore.currentPage).toBe(1)
    })

    it('setActionFilter 应该设置操作筛选并重置页码', () => {
      permissionStore.setPage(3)
      permissionStore.setActionFilter('create')
      expect(permissionStore.actionFilter).toBe('create')
      expect(permissionStore.currentPage).toBe(1)
    })

    it('setModuleFilter 应该设置模块筛选并重置页码', () => {
      permissionStore.setPage(3)
      permissionStore.setModuleFilter('user_management')
      expect(permissionStore.moduleFilter).toBe('user_management')
      expect(permissionStore.currentPage).toBe(1)
    })

    it('setStatusFilter 应该设置状态筛选并重置页码', () => {
      permissionStore.setPage(3)
      permissionStore.setStatusFilter('active')
      expect(permissionStore.statusFilter).toBe('active')
      expect(permissionStore.currentPage).toBe(1)
    })

    it('setSystemOnlyFilter 应该设置系统权限筛选并重置页码', () => {
      permissionStore.setPage(3)
      permissionStore.setSystemOnlyFilter(true)
      expect(permissionStore.systemOnlyFilter).toBe(true)
      expect(permissionStore.currentPage).toBe(1)
    })

    it('setSorting 应该设置排序字段和方向', () => {
      permissionStore.setSorting('name', 'asc')
      expect(permissionStore.sortBy).toBe('name')
      expect(permissionStore.sortOrder).toBe('asc')
    })
  })
})