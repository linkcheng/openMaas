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
import { useMenuConfigStore } from '../menuConfigStore'

// Unmock Pinia for this test file
vi.unmock('pinia')
import { apiClient } from '@/utils/api'
import type { 
  MenuPermissionConfig, 
  CreateMenuConfigRequest, 
  UpdateMenuConfigRequest,
  MenuConfigExport,
  MenuConfigImportRequest,
  MenuConfigImportResult,
  MenuPreviewConfig,
  MenuPreviewResult,
} from '@/types/permission/menuTypes'
import type { ApiResponse } from '@/types/permission/commonTypes'

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

describe('useMenuConfigStore', () => {
  let menuConfigStore: ReturnType<typeof useMenuConfigStore>

  // Mock data
  const mockMenuConfig: MenuPermissionConfig = {
    id: '1',
    menu_key: 'user_management',
    menu_name: 'User Management',
    menu_path: '/users',
    menu_icon: 'users',
    menu_type: 'menu',
    required_permissions: ['user.read', 'user.create'],
    permission_logic: 'OR',
    is_visible: true,
    status: 'visible',
    sort_order: 1,
    level: 0,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 'admin',
  }

  const mockChildMenuConfig: MenuPermissionConfig = {
    id: '2',
    menu_key: 'user_list',
    menu_name: 'User List',
    menu_path: '/users/list',
    parent_key: 'user_management',
    menu_type: 'menu',
    required_permissions: ['user.read'],
    permission_logic: 'AND',
    is_visible: true,
    status: 'visible',
    sort_order: 1,
    level: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 'admin',
  }

  const mockButtonConfig: MenuPermissionConfig = {
    id: '3',
    menu_key: 'create_user_btn',
    menu_name: 'Create User Button',
    menu_path: '',
    parent_key: 'user_list',
    menu_type: 'button',
    required_permissions: ['user.create'],
    permission_logic: 'AND',
    is_visible: true,
    status: 'visible',
    sort_order: 1,
    level: 2,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 'admin',
  }

  const mockExportData: MenuConfigExport = {
    version: '1.0.0',
    exported_at: '2024-01-01T00:00:00Z',
    configs: [mockMenuConfig, mockChildMenuConfig, mockButtonConfig],
    exported_by: 'admin',
    description: 'Test export',
  }

  const mockImportResult: MenuConfigImportResult = {
    success: true,
    imported_count: 3,
    skipped_count: 0,
    failed_count: 0,
    imported_ids: ['user_management', 'user_list', 'create_user_btn'],
  }

  const mockPreviewResult: MenuPreviewResult = {
    visible_menus: [],
    hidden_menus: [],
    permission_results: [],
    stats: {
      total_menus: 3,
      visible_count: 3,
      hidden_count: 0,
      permission_denied_count: 0,
    },
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    menuConfigStore = useMenuConfigStore()
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      expect(menuConfigStore.menuConfigs).toEqual([])
      expect(menuConfigStore.menuTree).toEqual([])
      expect(menuConfigStore.loading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
      expect(menuConfigStore.searchQuery).toBe('')
      expect(menuConfigStore.menuTypeFilter).toBe('')
      expect(menuConfigStore.statusFilter).toBe('')
      expect(menuConfigStore.parentFilter).toBe('')
      expect(menuConfigStore.rootOnlyFilter).toBe(false)
      expect(menuConfigStore.permissionFilter).toBe('')
      expect(menuConfigStore.sortBy).toBe('sort_order')
      expect(menuConfigStore.sortOrder).toBe('asc')
      expect(menuConfigStore.batchOperationLoading).toBe(false)
      expect(menuConfigStore.importExportLoading).toBe(false)
      expect(menuConfigStore.previewLoading).toBe(false)
      expect(menuConfigStore.previewResult).toBe(null)
    })

    it('计算属性应该返回正确的初始值', () => {
      expect(menuConfigStore.filteredMenuConfigs).toEqual([])
      expect(menuConfigStore.rootMenuConfigs).toEqual([])
      expect(menuConfigStore.visibleMenuConfigs).toEqual([])
      expect(menuConfigStore.hiddenMenuConfigs).toEqual([])
      expect(menuConfigStore.availableParentMenus).toEqual([])
      expect(menuConfigStore.usedPermissions).toEqual([])
    })
  })

  describe('基础操作方法', () => {
    it('setLoading 应该设置加载状态', () => {
      menuConfigStore.setLoading(true)
      expect(menuConfigStore.loading).toBe(true)

      menuConfigStore.setLoading(false)
      expect(menuConfigStore.loading).toBe(false)
    })

    it('setError 应该设置错误信息', () => {
      const errorMessage = 'Test error'
      menuConfigStore.setError(errorMessage)
      expect(menuConfigStore.error).toBe(errorMessage)
    })

    it('clearError 应该清除错误信息', () => {
      menuConfigStore.setError('Test error')
      menuConfigStore.clearError()
      expect(menuConfigStore.error).toBe(null)
    })

    it('resetFilters 应该重置所有筛选条件', () => {
      menuConfigStore.setSearchQuery('test')
      menuConfigStore.setMenuTypeFilter('menu')
      menuConfigStore.setStatusFilter('visible')
      menuConfigStore.setParentFilter('parent')
      menuConfigStore.setRootOnlyFilter(true)
      menuConfigStore.setPermissionFilter('user.read')

      menuConfigStore.resetFilters()

      expect(menuConfigStore.searchQuery).toBe('')
      expect(menuConfigStore.menuTypeFilter).toBe('')
      expect(menuConfigStore.statusFilter).toBe('')
      expect(menuConfigStore.parentFilter).toBe('')
      expect(menuConfigStore.rootOnlyFilter).toBe(false)
      expect(menuConfigStore.permissionFilter).toBe('')
    })
  })

  describe('fetchMenuConfigs', () => {
    it('应该成功获取菜单配置列表', async () => {
      const mockResponse: ApiResponse<MenuPermissionConfig[]> = {
        success: true,
        data: [mockMenuConfig, mockChildMenuConfig, mockButtonConfig],
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      await menuConfigStore.fetchMenuConfigs()

      expect(mockApiClient.get).toHaveBeenCalledWith('/menu-configs', {
        search: undefined,
        menu_type: undefined,
        status: undefined,
        parent_key: undefined,
        root_only: undefined,
        permission: undefined,
        sort_by: 'sort_order',
        sort_order: 'asc',
      })

      expect(menuConfigStore.menuConfigs).toEqual(mockResponse.data)
      expect(menuConfigStore.loading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
    })

    it('应该处理API错误', async () => {
      const errorMessage = 'API Error'
      mockApiClient.get.mockRejectedValue(new Error(errorMessage))

      await expect(menuConfigStore.fetchMenuConfigs()).rejects.toThrow(errorMessage)

      expect(menuConfigStore.loading).toBe(false)
      expect(menuConfigStore.error).toBe(errorMessage)
    })

    it('应该处理API响应错误', async () => {
      const mockResponse: ApiResponse<MenuPermissionConfig[]> = {
        success: false,
        error: 'Server error',
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      await expect(menuConfigStore.fetchMenuConfigs()).rejects.toThrow('Server error')

      expect(menuConfigStore.error).toBe('Server error')
    })
  })

  describe('fetchMenuConfigByKey', () => {
    it('应该成功获取菜单配置详情', async () => {
      const mockResponse: ApiResponse<MenuPermissionConfig> = {
        success: true,
        data: mockMenuConfig,
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await menuConfigStore.fetchMenuConfigByKey('user_management')

      expect(mockApiClient.get).toHaveBeenCalledWith('/menu-configs/user_management')
      expect(result).toEqual(mockMenuConfig)
      expect(menuConfigStore.loading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
    })

    it('应该使用缓存的配置数据', async () => {
      // 先设置缓存
      menuConfigStore.menuConfigs = [mockMenuConfig]
      
      const result = await menuConfigStore.fetchMenuConfigByKey('user_management', true)

      expect(mockApiClient.get).not.toHaveBeenCalled()
      expect(result).toEqual(mockMenuConfig)
    })

    it('应该处理获取配置详情的错误', async () => {
      const errorMessage = 'Config not found'
      mockApiClient.get.mockRejectedValue(new Error(errorMessage))

      await expect(menuConfigStore.fetchMenuConfigByKey('user_management')).rejects.toThrow(errorMessage)

      expect(menuConfigStore.error).toBe(errorMessage)
    })
  })

  describe('createMenuConfig', () => {
    it('应该成功创建菜单配置', async () => {
      const createRequest: CreateMenuConfigRequest = {
        menu_key: 'new_menu',
        menu_name: 'New Menu',
        menu_path: '/new',
        menu_type: 'menu',
        required_permissions: ['new.read'],
        permission_logic: 'AND',
        is_visible: true,
        sort_order: 1,
      }

      const mockResponse: ApiResponse<MenuPermissionConfig> = {
        success: true,
        data: mockMenuConfig,
      }

      mockApiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await menuConfigStore.createMenuConfig(createRequest)

      expect(mockApiClient.post).toHaveBeenCalledWith('/menu-configs', createRequest)
      expect(result).toEqual(mockMenuConfig)
      expect(menuConfigStore.menuConfigs).toContain(mockMenuConfig)
      expect(menuConfigStore.loading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
    })

    it('应该处理创建配置的错误', async () => {
      const createRequest: CreateMenuConfigRequest = {
        menu_key: 'new_menu',
        menu_name: 'New Menu',
        menu_path: '/new',
        menu_type: 'menu',
        required_permissions: [],
        permission_logic: 'AND',
        is_visible: true,
        sort_order: 1,
      }

      const errorMessage = 'Menu key already exists'
      mockApiClient.post.mockRejectedValue(new Error(errorMessage))

      await expect(menuConfigStore.createMenuConfig(createRequest)).rejects.toThrow(errorMessage)

      expect(menuConfigStore.error).toBe(errorMessage)
    })
  })

  describe('updateMenuConfig', () => {
    beforeEach(() => {
      menuConfigStore.menuConfigs = [mockMenuConfig]
    })

    it('应该成功更新菜单配置', async () => {
      const updateRequest: UpdateMenuConfigRequest = {
        menu_name: 'Updated Menu',
        is_visible: false,
      }

      const updatedConfig = { ...mockMenuConfig, ...updateRequest }
      const mockResponse: ApiResponse<MenuPermissionConfig> = {
        success: true,
        data: updatedConfig,
      }

      mockApiClient.put.mockResolvedValue({ data: mockResponse })

      const result = await menuConfigStore.updateMenuConfig('user_management', updateRequest)

      expect(mockApiClient.put).toHaveBeenCalledWith('/menu-configs/user_management', updateRequest)
      expect(result).toEqual(updatedConfig)
      expect(menuConfigStore.menuConfigs[0]).toEqual(updatedConfig)
      expect(menuConfigStore.loading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
    })

    it('应该处理更新配置的错误', async () => {
      const updateRequest: UpdateMenuConfigRequest = {
        menu_name: 'Updated Menu',
      }

      const errorMessage = 'Update failed'
      mockApiClient.put.mockRejectedValue(new Error(errorMessage))

      await expect(menuConfigStore.updateMenuConfig('user_management', updateRequest)).rejects.toThrow(errorMessage)

      expect(menuConfigStore.error).toBe(errorMessage)
    })
  })

  describe('deleteMenuConfig', () => {
    beforeEach(() => {
      menuConfigStore.menuConfigs = [mockMenuConfig]
    })

    it('应该成功删除菜单配置', async () => {
      const mockResponse: ApiResponse<void> = {
        success: true,
      }

      mockApiClient.delete.mockResolvedValue({ data: mockResponse })

      await menuConfigStore.deleteMenuConfig('user_management')

      expect(mockApiClient.delete).toHaveBeenCalledWith('/menu-configs/user_management')
      expect(menuConfigStore.menuConfigs).toEqual([])
      expect(menuConfigStore.loading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
    })

    it('应该处理删除配置的错误', async () => {
      const errorMessage = 'Delete failed'
      mockApiClient.delete.mockRejectedValue(new Error(errorMessage))

      await expect(menuConfigStore.deleteMenuConfig('user_management')).rejects.toThrow(errorMessage)

      expect(menuConfigStore.error).toBe(errorMessage)
      expect(menuConfigStore.menuConfigs).toEqual([mockMenuConfig]) // 配置应该仍然存在
    })
  })

  describe('导入导出功能', () => {
    it('exportMenuConfigs 应该成功导出菜单配置', async () => {
      const mockResponse: ApiResponse<MenuConfigExport> = {
        success: true,
        data: mockExportData,
      }

      mockApiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await menuConfigStore.exportMenuConfigs(['user_management'])

      expect(mockApiClient.get).toHaveBeenCalledWith('/menu-configs/export', {
        menu_keys: 'user_management',
      })
      expect(result).toEqual(mockExportData)
      expect(menuConfigStore.importExportLoading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
    })

    it('importMenuConfigs 应该成功导入菜单配置', async () => {
      const importRequest: MenuConfigImportRequest = {
        configs: [mockMenuConfig, mockChildMenuConfig],
        import_mode: 'merge',
        overwrite_existing: true,
      }

      const mockResponse: ApiResponse<MenuConfigImportResult> = {
        success: true,
        data: mockImportResult,
      }

      // Mock fetchMenuConfigs for refresh after import
      const mockFetchResponse: ApiResponse<MenuPermissionConfig[]> = {
        success: true,
        data: [mockMenuConfig, mockChildMenuConfig],
      }

      mockApiClient.post.mockResolvedValue({ data: mockResponse })
      mockApiClient.get.mockResolvedValue({ data: mockFetchResponse })

      const result = await menuConfigStore.importMenuConfigs(importRequest)

      expect(mockApiClient.post).toHaveBeenCalledWith('/menu-configs/import', importRequest)
      expect(result).toEqual(mockImportResult)
      expect(menuConfigStore.importExportLoading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
    })
  })

  describe('预览功能', () => {
    it('previewMenuPermissions 应该成功预览菜单权限', async () => {
      const previewConfig: MenuPreviewConfig = {
        role_id: 'admin',
        preview_mode: 'role',
        show_permission_info: true,
      }

      const mockResponse: ApiResponse<MenuPreviewResult> = {
        success: true,
        data: mockPreviewResult,
      }

      mockApiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await menuConfigStore.previewMenuPermissions(previewConfig)

      expect(mockApiClient.post).toHaveBeenCalledWith('/menu-configs/preview', previewConfig)
      expect(result).toEqual(mockPreviewResult)
      expect(menuConfigStore.previewResult).toEqual(mockPreviewResult)
      expect(menuConfigStore.previewLoading).toBe(false)
      expect(menuConfigStore.error).toBe(null)
    })

    it('clearPreviewResult 应该清除预览结果', () => {
      menuConfigStore.previewResult = mockPreviewResult
      menuConfigStore.clearPreviewResult()
      expect(menuConfigStore.previewResult).toBe(null)
    })
  })

  describe('计算属性', () => {
    beforeEach(() => {
      menuConfigStore.menuConfigs = [mockMenuConfig, mockChildMenuConfig, mockButtonConfig]
    })

    it('rootMenuConfigs 应该返回根菜单配置', () => {
      expect(menuConfigStore.rootMenuConfigs).toEqual([mockMenuConfig])
    })

    it('menuConfigsByType 应该按类型分组菜单配置', () => {
      const grouped = menuConfigStore.menuConfigsByType
      expect(grouped.menu).toEqual([mockMenuConfig, mockChildMenuConfig])
      expect(grouped.button).toEqual([mockButtonConfig])
      expect(grouped.tab).toEqual([])
      expect(grouped.section).toEqual([])
    })

    it('visibleMenuConfigs 应该返回可见的菜单配置', () => {
      expect(menuConfigStore.visibleMenuConfigs).toEqual([mockMenuConfig, mockChildMenuConfig, mockButtonConfig])
    })

    it('availableParentMenus 应该返回可用的父菜单选项', () => {
      const parents = menuConfigStore.availableParentMenus
      expect(parents).toHaveLength(2) // mockMenuConfig and mockChildMenuConfig are menu type
      expect(parents[0].key).toBe('user_management')
      expect(parents[1].key).toBe('user_list')
    })

    it('usedPermissions 应该返回所有使用的权限列表', () => {
      const permissions = menuConfigStore.usedPermissions
      expect(permissions).toEqual(['user.create', 'user.read'])
    })

    it('filteredMenuConfigs 应该根据搜索条件筛选配置', () => {
      menuConfigStore.setSearchQuery('User Management')
      expect(menuConfigStore.filteredMenuConfigs).toEqual([mockMenuConfig])

      menuConfigStore.setSearchQuery('user')
      expect(menuConfigStore.filteredMenuConfigs).toHaveLength(3) // 所有配置都包含 'user'
    })

    it('filteredMenuConfigs 应该根据菜单类型筛选配置', () => {
      menuConfigStore.setMenuTypeFilter('button')
      expect(menuConfigStore.filteredMenuConfigs).toEqual([mockButtonConfig])

      menuConfigStore.setMenuTypeFilter('menu')
      expect(menuConfigStore.filteredMenuConfigs).toEqual([mockMenuConfig, mockChildMenuConfig])
    })

    it('filteredMenuConfigs 应该根据根菜单筛选', () => {
      menuConfigStore.setRootOnlyFilter(true)
      expect(menuConfigStore.filteredMenuConfigs).toEqual([mockMenuConfig])
    })
  })

  describe('菜单树操作', () => {
    beforeEach(() => {
      menuConfigStore.menuConfigs = [mockMenuConfig, mockChildMenuConfig, mockButtonConfig]
      menuConfigStore.buildMenuTree()
    })

    it('buildMenuTree 应该构建正确的树结构', () => {
      expect(menuConfigStore.menuTree).toHaveLength(1)
      expect(menuConfigStore.menuTree[0].config).toEqual(mockMenuConfig)
      expect(menuConfigStore.menuTree[0].children).toHaveLength(1)
      expect(menuConfigStore.menuTree[0].children[0].config).toEqual(mockChildMenuConfig)
      expect(menuConfigStore.menuTree[0].children[0].children).toHaveLength(1)
      expect(menuConfigStore.menuTree[0].children[0].children[0].config).toEqual(mockButtonConfig)
    })

    it('toggleNodeExpanded 应该切换节点展开状态', () => {
      expect(menuConfigStore.expandedNodes.has('user_management')).toBe(false)
      
      menuConfigStore.toggleNodeExpanded('user_management')
      expect(menuConfigStore.expandedNodes.has('user_management')).toBe(true)
      
      menuConfigStore.toggleNodeExpanded('user_management')
      expect(menuConfigStore.expandedNodes.has('user_management')).toBe(false)
    })

    it('toggleNodeSelected 应该切换节点选中状态', () => {
      expect(menuConfigStore.selectedNodes.has('user_management')).toBe(false)
      
      menuConfigStore.toggleNodeSelected('user_management')
      expect(menuConfigStore.selectedNodes.has('user_management')).toBe(true)
      
      menuConfigStore.toggleNodeSelected('user_management')
      expect(menuConfigStore.selectedNodes.has('user_management')).toBe(false)
    })

    it('expandAllNodes 应该展开所有节点', () => {
      menuConfigStore.expandAllNodes()
      expect(menuConfigStore.expandedNodes.has('user_management')).toBe(true)
      expect(menuConfigStore.expandedNodes.has('user_list')).toBe(true)
      expect(menuConfigStore.expandedNodes.has('create_user_btn')).toBe(true)
    })

    it('collapseAllNodes 应该折叠所有节点', () => {
      menuConfigStore.expandAllNodes()
      menuConfigStore.collapseAllNodes()
      expect(menuConfigStore.expandedNodes.size).toBe(0)
    })

    it('selectAllNodes 应该选中所有节点', () => {
      menuConfigStore.selectAllNodes()
      expect(menuConfigStore.selectedNodes.has('user_management')).toBe(true)
      expect(menuConfigStore.selectedNodes.has('user_list')).toBe(true)
      expect(menuConfigStore.selectedNodes.has('create_user_btn')).toBe(true)
    })

    it('deselectAllNodes 应该取消选中所有节点', () => {
      menuConfigStore.selectAllNodes()
      menuConfigStore.deselectAllNodes()
      expect(menuConfigStore.selectedNodes.size).toBe(0)
    })
  })

  describe('辅助方法', () => {
    beforeEach(() => {
      menuConfigStore.menuConfigs = [mockMenuConfig, mockChildMenuConfig, mockButtonConfig]
    })

    it('findConfigByKey 应该根据菜单键查找配置', () => {
      const result = menuConfigStore.findConfigByKey('user_management')
      expect(result).toEqual(mockMenuConfig)

      const notFound = menuConfigStore.findConfigByKey('nonexistent')
      expect(notFound).toBeUndefined()
    })

    it('isMenuKeyExists 应该检查菜单键是否存在', () => {
      expect(menuConfigStore.isMenuKeyExists('user_management')).toBe(true)
      expect(menuConfigStore.isMenuKeyExists('nonexistent')).toBe(false)
      expect(menuConfigStore.isMenuKeyExists('user_management', 'user_management')).toBe(false) // 排除自身
    })

    it('getChildConfigs 应该获取子配置', () => {
      const children = menuConfigStore.getChildConfigs('user_management')
      expect(children).toEqual([mockChildMenuConfig])

      const grandChildren = menuConfigStore.getChildConfigs('user_list')
      expect(grandChildren).toEqual([mockButtonConfig])
    })

    it('getParentConfig 应该获取父配置', () => {
      const parent = menuConfigStore.getParentConfig('user_list')
      expect(parent).toEqual(mockMenuConfig)

      const noParent = menuConfigStore.getParentConfig('user_management')
      expect(noParent).toBeUndefined()
    })

    it('validateMenuPermission 应该验证菜单权限', () => {
      const userPermissions = ['user.read', 'user.create']
      
      // 测试 OR 逻辑
      const result1 = menuConfigStore.validateMenuPermission('user_management', userPermissions)
      expect(result1.hasPermission).toBe(true)
      expect(result1.isVisible).toBe(true)

      // 测试 AND 逻辑
      const result2 = menuConfigStore.validateMenuPermission('user_list', userPermissions)
      expect(result2.hasPermission).toBe(true)
      expect(result2.isVisible).toBe(true)

      // 测试权限不足
      const result3 = menuConfigStore.validateMenuPermission('user_list', ['other.permission'])
      expect(result3.hasPermission).toBe(false)
      expect(result3.isVisible).toBe(false)
      expect(result3.missingPermissions).toEqual(['user.read'])

      // 测试不存在的菜单
      const result4 = menuConfigStore.validateMenuPermission('nonexistent', userPermissions)
      expect(result4.hasPermission).toBe(false)
      expect(result4.isVisible).toBe(false)
    })
  })

  describe('拖拽操作', () => {
    it('startDrag 应该开始拖拽', () => {
      menuConfigStore.startDrag('user_management')
      expect(menuConfigStore.dragState.isDragging).toBe(true)
      expect(menuConfigStore.dragState.draggedNode).toBe('user_management')
    })

    it('endDrag 应该结束拖拽', () => {
      menuConfigStore.startDrag('user_management')
      menuConfigStore.setDropTarget('user_list')
      
      menuConfigStore.endDrag()
      expect(menuConfigStore.dragState.isDragging).toBe(false)
      expect(menuConfigStore.dragState.draggedNode).toBe(null)
      expect(menuConfigStore.dragState.dropTarget).toBe(null)
    })

    it('setDropTarget 应该设置拖拽目标', () => {
      menuConfigStore.setDropTarget('user_list')
      expect(menuConfigStore.dragState.dropTarget).toBe('user_list')
    })
  })

  describe('筛选方法', () => {
    it('setSearchQuery 应该设置搜索关键词', () => {
      menuConfigStore.setSearchQuery('test')
      expect(menuConfigStore.searchQuery).toBe('test')
    })

    it('setMenuTypeFilter 应该设置菜单类型筛选', () => {
      menuConfigStore.setMenuTypeFilter('menu')
      expect(menuConfigStore.menuTypeFilter).toBe('menu')
    })

    it('setStatusFilter 应该设置状态筛选', () => {
      menuConfigStore.setStatusFilter('visible')
      expect(menuConfigStore.statusFilter).toBe('visible')
    })

    it('setParentFilter 应该设置父菜单筛选', () => {
      menuConfigStore.setParentFilter('parent')
      expect(menuConfigStore.parentFilter).toBe('parent')
    })

    it('setRootOnlyFilter 应该设置根菜单筛选', () => {
      menuConfigStore.setRootOnlyFilter(true)
      expect(menuConfigStore.rootOnlyFilter).toBe(true)
    })

    it('setPermissionFilter 应该设置权限筛选', () => {
      menuConfigStore.setPermissionFilter('user.read')
      expect(menuConfigStore.permissionFilter).toBe('user.read')
    })

    it('setSorting 应该设置排序字段和方向', () => {
      menuConfigStore.setSorting('menu_name', 'desc')
      expect(menuConfigStore.sortBy).toBe('menu_name')
      expect(menuConfigStore.sortOrder).toBe('desc')
    })
  })
})