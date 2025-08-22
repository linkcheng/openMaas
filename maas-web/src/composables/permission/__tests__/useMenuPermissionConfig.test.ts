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
import { useMenuPermissionConfig } from '../useMenuPermissionConfig'
import { useMenuConfigStore } from '@/stores/permission/menuConfigStore'
import { usePermissionStore } from '@/stores/permission/permissionStore'
import { useRoleStore } from '@/stores/permission/roleStore'
import { useNotification } from '@/composables/useNotification'
import type {
  MenuPermissionConfig,
  CreateMenuConfigRequest,
  UpdateMenuConfigRequest,
  MenuTreeNode,
  MenuConfigExport,
  MenuConfigImportRequest,
  MenuConfigImportResult,
  MenuPreviewConfig,
  MenuPreviewResult,
} from '@/types/permission/menuTypes'
import type { Role } from '@/types/permission/roleTypes'
import type { Permission } from '@/types/permission/permissionTypes'

// Mock dependencies
vi.mock('@/stores/permission/menuConfigStore')
vi.mock('@/stores/permission/permissionStore')
vi.mock('@/stores/permission/roleStore')
vi.mock('@/composables/useNotification')

// Mock data
const mockMenuConfig: MenuPermissionConfig = {
  id: '1',
  menu_key: 'user-management',
  menu_name: 'User Management',
  menu_path: '/admin/users',
  menu_type: 'menu',
  parent_key: undefined,
  required_permissions: ['user.view'],
  permission_logic: 'AND',
  is_visible: true,
  status: 'visible',
  sort_order: 0,
  level: 0,
  icon: 'user',
  description: 'User management menu',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockChildMenuConfig: MenuPermissionConfig = {
  id: '2',
  menu_key: 'user-list',
  menu_name: 'User List',
  menu_path: '/admin/users/list',
  menu_type: 'menu',
  parent_key: 'user-management',
  required_permissions: ['user.view'],
  permission_logic: 'AND',
  is_visible: true,
  status: 'visible',
  sort_order: 0,
  level: 1,
  icon: 'list',
  description: 'User list submenu',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const mockTreeNode: MenuTreeNode = {
  config: mockMenuConfig,
  children: [
    {
      config: mockChildMenuConfig,
      children: [],
      expanded: false,
      selected: false,
      draggable: true,
      level: 1,
    },
  ],
  expanded: true,
  selected: false,
  draggable: true,
  level: 0,
}

const mockRole: Role = {
  id: 'role1',
  name: 'admin',
  display_name: 'Administrator',
  description: 'Administrator role',
  role_type: 'system',
  is_system_role: true,
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

const mockCreateMenuConfigRequest: CreateMenuConfigRequest = {
  menu_key: 'new-menu',
  menu_name: 'New Menu',
  menu_path: '/new-menu',
  menu_type: 'menu',
  parent_key: undefined,
  required_permissions: ['user.view'],
  permission_logic: 'AND',
  is_visible: true,
  sort_order: 0,
  icon: 'menu',
  description: 'New menu description',
}

const mockExportData: MenuConfigExport = {
  version: '1.0',
  exported_at: '2024-01-01T00:00:00Z',
  configs: [mockMenuConfig],
  total_count: 1,
}

const mockImportResult: MenuConfigImportResult = {
  success: true,
  imported_count: 1,
  skipped_count: 0,
  error_count: 0,
  warnings: [],
  errors: [],
}

const mockPreviewResult: MenuPreviewResult = {
  role_id: 'role1',
  user_id: undefined,
  visible_menus: [mockMenuConfig],
  hidden_menus: [],
  permission_results: {
    'user-management': {
      menu_key: 'user-management',
      hasPermission: true,
      isVisible: true,
      message: 'Has permission',
    },
  },
}

describe('useMenuPermissionConfig', () => {
  let menuConfigStore: any
  let permissionStore: any
  let roleStore: any
  let notification: any

  beforeEach(() => {
    setActivePinia(createPinia())
    
    // Mock menu config store
    menuConfigStore = {
      menuConfigs: [mockMenuConfig, mockChildMenuConfig],
      filteredMenuConfigs: [mockMenuConfig, mockChildMenuConfig],
      menuTree: [mockTreeNode],
      rootMenuConfigs: [mockMenuConfig],
      menuConfigsByType: { menu: [mockMenuConfig, mockChildMenuConfig], button: [], tab: [], section: [] },
      visibleMenuConfigs: [mockMenuConfig, mockChildMenuConfig],
      hiddenMenuConfigs: [],
      availableParentMenus: [{ key: 'user-management', name: 'User Management', level: 0 }],
      usedPermissions: ['user.view'],
      loading: false,
      batchOperationLoading: false,
      importExportLoading: false,
      previewLoading: false,
      error: null,
      searchQuery: '',
      menuTypeFilter: '',
      statusFilter: '',
      parentFilter: '',
      rootOnlyFilter: false,
      permissionFilter: '',
      sortBy: 'sort_order',
      sortOrder: 'asc',
      selectedNodes: new Set(),
      previewResult: null,
      fetchMenuConfigs: vi.fn().mockResolvedValue(undefined),
      fetchMenuConfigByKey: vi.fn().mockResolvedValue(mockMenuConfig),
      createMenuConfig: vi.fn().mockResolvedValue(mockMenuConfig),
      updateMenuConfig: vi.fn().mockResolvedValue(mockMenuConfig),
      deleteMenuConfig: vi.fn().mockResolvedValue(undefined),
      batchOperateMenuConfigs: vi.fn().mockResolvedValue({ success_ids: ['1'], failed_ids: [] }),
      exportMenuConfigs: vi.fn().mockResolvedValue(mockExportData),
      importMenuConfigs: vi.fn().mockResolvedValue(mockImportResult),
      previewMenuPermissions: vi.fn().mockResolvedValue(mockPreviewResult),
      clearPreviewResult: vi.fn(),
      refresh: vi.fn().mockResolvedValue(undefined),
      setSearchQuery: vi.fn(),
      setMenuTypeFilter: vi.fn(),
      setStatusFilter: vi.fn(),
      setParentFilter: vi.fn(),
      setRootOnlyFilter: vi.fn(),
      setPermissionFilter: vi.fn(),
      resetFilters: vi.fn(),
      setSorting: vi.fn(),
      toggleNodeExpanded: vi.fn(),
      toggleNodeSelected: vi.fn(),
      expandAllNodes: vi.fn(),
      collapseAllNodes: vi.fn(),
      selectAllNodes: vi.fn(),
      deselectAllNodes: vi.fn(),
      startDrag: vi.fn(),
      endDrag: vi.fn(),
      setDropTarget: vi.fn(),
      performDragOperation: vi.fn().mockResolvedValue(undefined),
      findConfigByKey: vi.fn().mockReturnValue(mockMenuConfig),
      isMenuKeyExists: vi.fn().mockReturnValue(false),
      getChildConfigs: vi.fn().mockReturnValue([]),
      getParentConfig: vi.fn().mockReturnValue(undefined),
      validateMenuPermission: vi.fn().mockReturnValue({ hasPermission: true, isVisible: true }),
    }

    // Mock permission store
    permissionStore = {
      activePermissions: [mockPermission],
      fetchPermissions: vi.fn().mockResolvedValue(undefined),
    }

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
      confirmDelete: vi.fn().mockResolvedValue(true),
      confirmBatchDelete: vi.fn().mockResolvedValue(true),
    }

    vi.mocked(useMenuConfigStore).mockReturnValue(menuConfigStore)
    vi.mocked(usePermissionStore).mockReturnValue(permissionStore)
    vi.mocked(useRoleStore).mockReturnValue(roleStore)
    vi.mocked(useNotification).mockReturnValue(notification)
  })

  describe('初始化', () => {
    it('应该正确初始化', async () => {
      const { initialize } = useMenuPermissionConfig()
      
      await initialize()
      
      expect(menuConfigStore.fetchMenuConfigs).toHaveBeenCalled()
      expect(permissionStore.fetchPermissions).toHaveBeenCalled()
      expect(roleStore.fetchRoles).toHaveBeenCalled()
    })

    it('初始化失败时应该显示错误消息', async () => {
      menuConfigStore.fetchMenuConfigs.mockRejectedValue(new Error('Network error'))
      
      const { initialize } = useMenuPermissionConfig()
      
      await initialize()
      
      expect(notification.showError).toHaveBeenCalledWith('初始化菜单权限配置管理失败')
    })
  })

  describe('计算属性', () => {
    it('应该正确返回菜单配置列表', () => {
      const {
        menuConfigs,
        filteredMenuConfigs,
        menuTree,
        rootMenuConfigs,
        visibleMenuConfigs,
        availableParentMenus,
      } = useMenuPermissionConfig()
      
      expect(menuConfigs.value).toEqual([mockMenuConfig, mockChildMenuConfig])
      expect(filteredMenuConfigs.value).toEqual([mockMenuConfig, mockChildMenuConfig])
      expect(menuTree.value).toEqual([mockTreeNode])
      expect(rootMenuConfigs.value).toEqual([mockMenuConfig])
      expect(visibleMenuConfigs.value).toEqual([mockMenuConfig, mockChildMenuConfig])
      expect(availableParentMenus.value).toEqual([{ key: 'user-management', name: 'User Management', level: 0 }])
    })

    it('应该正确返回可用的权限和角色', () => {
      const { availablePermissions, availableRoles } = useMenuPermissionConfig()
      
      expect(availablePermissions.value).toEqual([mockPermission])
      expect(availableRoles.value).toEqual([mockRole])
    })
  })

  describe('对话框操作', () => {
    it('应该正确打开创建对话框', () => {
      const { openCreateDialog, configDialogVisible, dialogMode, configFormData } = useMenuPermissionConfig()
      
      openCreateDialog()
      
      expect(configDialogVisible.value).toBe(true)
      expect(dialogMode.value).toBe('create')
      expect(configFormData.value.menu_key).toBe('')
      expect(configFormData.value.menu_name).toBe('')
      expect(configFormData.value.menu_type).toBe('menu')
    })

    it('应该正确打开编辑对话框', () => {
      const { openEditDialog, configDialogVisible, dialogMode, configFormData, selectedConfig } = useMenuPermissionConfig()
      
      openEditDialog(mockMenuConfig)
      
      expect(configDialogVisible.value).toBe(true)
      expect(dialogMode.value).toBe('edit')
      expect(selectedConfig.value).toEqual(mockMenuConfig)
      expect(configFormData.value.menu_key).toBe(mockMenuConfig.menu_key)
      expect(configFormData.value.menu_name).toBe(mockMenuConfig.menu_name)
    })

    it('应该正确打开查看对话框', () => {
      const { openViewDialog, configDialogVisible, dialogMode, selectedConfig } = useMenuPermissionConfig()
      
      openViewDialog(mockMenuConfig)
      
      expect(configDialogVisible.value).toBe(true)
      expect(dialogMode.value).toBe('view')
      expect(selectedConfig.value).toEqual(mockMenuConfig)
    })
  })

  describe('菜单配置CRUD操作', () => {
    it('应该成功创建菜单配置', async () => {
      const { createMenuConfig, configDialogVisible } = useMenuPermissionConfig()
      
      const result = await createMenuConfig(mockCreateMenuConfigRequest)
      
      expect(result).toBe(true)
      expect(menuConfigStore.createMenuConfig).toHaveBeenCalledWith(mockCreateMenuConfigRequest)
      expect(notification.showSuccess).toHaveBeenCalledWith(`菜单配置 "${mockMenuConfig.menu_name}" 创建成功`)
      expect(configDialogVisible.value).toBe(false)
    })

    it('创建菜单配置时表单验证失败应该返回false', async () => {
      const { createMenuConfig } = useMenuPermissionConfig()
      
      const invalidRequest = { ...mockCreateMenuConfigRequest, menu_key: '' }
      const result = await createMenuConfig(invalidRequest)
      
      expect(result).toBe(false)
      expect(menuConfigStore.createMenuConfig).not.toHaveBeenCalled()
    })

    it('应该成功更新菜单配置', async () => {
      const { updateMenuConfig, configDialogVisible } = useMenuPermissionConfig()
      
      const updateRequest: UpdateMenuConfigRequest = {
        menu_name: 'Updated Menu',
        description: 'Updated description',
      }
      
      const result = await updateMenuConfig('user-management', updateRequest)
      
      expect(result).toBe(true)
      expect(menuConfigStore.updateMenuConfig).toHaveBeenCalledWith('user-management', updateRequest)
      expect(notification.showSuccess).toHaveBeenCalledWith(`菜单配置 "${mockMenuConfig.menu_name}" 更新成功`)
      expect(configDialogVisible.value).toBe(false)
    })

    it('应该成功删除菜单配置', async () => {
      const { deleteMenuConfig } = useMenuPermissionConfig()
      
      const result = await deleteMenuConfig(mockMenuConfig)
      
      expect(result).toBe(true)
      expect(notification.confirmDelete).toHaveBeenCalled()
      expect(menuConfigStore.deleteMenuConfig).toHaveBeenCalledWith(mockMenuConfig.menu_key)
      expect(notification.showSuccess).toHaveBeenCalledWith(`菜单配置 "${mockMenuConfig.menu_name}" 删除成功`)
    })

    it('有子菜单时不应该删除菜单配置', async () => {
      menuConfigStore.getChildConfigs.mockReturnValue([mockChildMenuConfig])
      
      const { deleteMenuConfig } = useMenuPermissionConfig()
      
      const result = await deleteMenuConfig(mockMenuConfig)
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith(`菜单 "${mockMenuConfig.menu_name}" 有 1 个子菜单，请先删除子菜单`)
      expect(menuConfigStore.deleteMenuConfig).not.toHaveBeenCalled()
    })

    it('用户取消删除时应该返回false', async () => {
      notification.confirmDelete.mockResolvedValue(false)
      
      const { deleteMenuConfig } = useMenuPermissionConfig()
      
      const result = await deleteMenuConfig(mockMenuConfig)
      
      expect(result).toBe(false)
      expect(menuConfigStore.deleteMenuConfig).not.toHaveBeenCalled()
    })
  })

  describe('批量操作', () => {
    it('应该成功批量删除菜单配置', async () => {
      const { batchDeleteMenuConfigs, selectedMenuKeys } = useMenuPermissionConfig()
      
      selectedMenuKeys.value = ['user-management']
      
      const result = await batchDeleteMenuConfigs()
      
      expect(result).toBe(true)
      expect(notification.confirmBatchDelete).toHaveBeenCalledWith(1)
      expect(menuConfigStore.batchOperateMenuConfigs).toHaveBeenCalledWith({
        menu_keys: ['user-management'],
        operation: 'delete',
      })
      expect(notification.showSuccess).toHaveBeenCalledWith('成功删除 1 个菜单配置')
    })

    it('没有选中菜单时不应该执行批量删除', async () => {
      const { batchDeleteMenuConfigs, selectedMenuKeys } = useMenuPermissionConfig()
      
      selectedMenuKeys.value = []
      
      const result = await batchDeleteMenuConfigs()
      
      expect(result).toBe(false)
      expect(notification.showWarning).toHaveBeenCalledWith('请选择要删除的菜单配置')
      expect(menuConfigStore.batchOperateMenuConfigs).not.toHaveBeenCalled()
    })

    it('应该成功批量显示菜单配置', async () => {
      const { batchShowMenuConfigs, selectedMenuKeys } = useMenuPermissionConfig()
      
      selectedMenuKeys.value = ['user-management']
      
      const result = await batchShowMenuConfigs()
      
      expect(result).toBe(true)
      expect(menuConfigStore.batchOperateMenuConfigs).toHaveBeenCalledWith({
        menu_keys: ['user-management'],
        operation: 'show',
      })
      expect(notification.showSuccess).toHaveBeenCalledWith('成功显示 1 个菜单配置')
    })

    it('应该成功批量隐藏菜单配置', async () => {
      const { batchHideMenuConfigs, selectedMenuKeys } = useMenuPermissionConfig()
      
      selectedMenuKeys.value = ['user-management']
      
      const result = await batchHideMenuConfigs()
      
      expect(result).toBe(true)
      expect(menuConfigStore.batchOperateMenuConfigs).toHaveBeenCalledWith({
        menu_keys: ['user-management'],
        operation: 'hide',
      })
      expect(notification.showSuccess).toHaveBeenCalledWith('成功隐藏 1 个菜单配置')
    })
  })

  describe('导入导出操作', () => {
    it('应该成功导出菜单配置', async () => {
      // Mock DOM methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      }
      const mockCreateElement = vi.fn().mockReturnValue(mockLink)
      const mockCreateObjectURL = vi.fn().mockReturnValue('blob:url')
      const mockRevokeObjectURL = vi.fn()
      const mockAppendChild = vi.fn()
      const mockRemoveChild = vi.fn()

      Object.defineProperty(document, 'createElement', { value: mockCreateElement })
      Object.defineProperty(document.body, 'appendChild', { value: mockAppendChild })
      Object.defineProperty(document.body, 'removeChild', { value: mockRemoveChild })
      Object.defineProperty(URL, 'createObjectURL', { value: mockCreateObjectURL })
      Object.defineProperty(URL, 'revokeObjectURL', { value: mockRevokeObjectURL })

      const { exportMenuConfigs } = useMenuPermissionConfig()
      
      const result = await exportMenuConfigs(['user-management'])
      
      expect(result).toBe(true)
      expect(menuConfigStore.exportMenuConfigs).toHaveBeenCalledWith(['user-management'])
      expect(notification.showSuccess).toHaveBeenCalledWith('菜单配置导出成功')
      expect(mockLink.click).toHaveBeenCalled()
    })

    it('应该正确打开导入对话框', () => {
      const { openImportDialog, importDialogVisible, importFormData } = useMenuPermissionConfig()
      
      openImportDialog()
      
      expect(importDialogVisible.value).toBe(true)
      expect(importFormData.value.merge_strategy).toBe('replace')
      expect(importFormData.value.validate_permissions).toBe(true)
    })

    it('应该成功导入菜单配置', async () => {
      const { importMenuConfigs, importDialogVisible } = useMenuPermissionConfig()
      
      const importRequest: MenuConfigImportRequest = {
        configs: [mockMenuConfig],
        merge_strategy: 'replace',
        validate_permissions: true,
        create_missing_parents: true,
      }
      
      const result = await importMenuConfigs(importRequest)
      
      expect(result).toBe(true)
      expect(menuConfigStore.importMenuConfigs).toHaveBeenCalledWith(importRequest)
      expect(notification.showSuccess).toHaveBeenCalledWith('成功导入 1 个菜单配置')
      expect(importDialogVisible.value).toBe(false)
    })

    it('导入失败时应该显示错误消息', async () => {
      const failedResult = { ...mockImportResult, success: false, error: 'Import failed' }
      menuConfigStore.importMenuConfigs.mockResolvedValue(failedResult)
      
      const { importMenuConfigs } = useMenuPermissionConfig()
      
      const importRequest: MenuConfigImportRequest = {
        configs: [mockMenuConfig],
        merge_strategy: 'replace',
        validate_permissions: true,
        create_missing_parents: true,
      }
      
      const result = await importMenuConfigs(importRequest)
      
      expect(result).toBe(false)
      expect(notification.showError).toHaveBeenCalledWith('导入失败: Import failed')
    })
  })

  describe('预览功能', () => {
    it('应该正确打开预览对话框', () => {
      const { openPreviewDialog, previewDialogVisible, previewConfig } = useMenuPermissionConfig()
      
      openPreviewDialog()
      
      expect(previewDialogVisible.value).toBe(true)
      expect(previewConfig.value.role_id).toBe('')
      expect(previewConfig.value.include_disabled).toBe(false)
    })

    it('应该成功预览菜单权限', async () => {
      const { previewMenuPermissions } = useMenuPermissionConfig()
      
      const config: MenuPreviewConfig = {
        role_id: 'role1',
        user_id: '',
        include_disabled: false,
      }
      
      const result = await previewMenuPermissions(config)
      
      expect(result).toBe(true)
      expect(menuConfigStore.previewMenuPermissions).toHaveBeenCalledWith(config)
      expect(notification.showSuccess).toHaveBeenCalledWith('菜单预览生成成功')
    })

    it('应该正确清除预览结果', () => {
      const { clearPreviewResult } = useMenuPermissionConfig()
      
      clearPreviewResult()
      
      expect(menuConfigStore.clearPreviewResult).toHaveBeenCalled()
    })
  })

  describe('搜索和筛选', () => {
    it('应该正确设置搜索关键词', () => {
      const { setSearchQuery } = useMenuPermissionConfig()
      
      setSearchQuery('test')
      
      expect(menuConfigStore.setSearchQuery).toHaveBeenCalledWith('test')
    })

    it('应该正确设置菜单类型筛选', () => {
      const { setMenuTypeFilter } = useMenuPermissionConfig()
      
      setMenuTypeFilter('button')
      
      expect(menuConfigStore.setMenuTypeFilter).toHaveBeenCalledWith('button')
    })

    it('应该正确重置筛选条件', () => {
      const { resetFilters } = useMenuPermissionConfig()
      
      resetFilters()
      
      expect(menuConfigStore.resetFilters).toHaveBeenCalled()
    })
  })

  describe('树形结构操作', () => {
    it('应该正确展开/折叠节点', () => {
      const { toggleNodeExpanded } = useMenuPermissionConfig()
      
      toggleNodeExpanded('user-management')
      
      expect(menuConfigStore.toggleNodeExpanded).toHaveBeenCalledWith('user-management')
    })

    it('应该正确选择/取消选择节点', () => {
      const { toggleNodeSelected, selectedMenuKeys } = useMenuPermissionConfig()
      
      menuConfigStore.selectedNodes.add('user-management')
      
      toggleNodeSelected('user-management')
      
      expect(menuConfigStore.toggleNodeSelected).toHaveBeenCalledWith('user-management')
      expect(selectedMenuKeys.value).toContain('user-management')
    })

    it('应该正确展开所有节点', () => {
      const { expandAllNodes, treeExpandAll } = useMenuPermissionConfig()
      
      expandAllNodes()
      
      expect(menuConfigStore.expandAllNodes).toHaveBeenCalled()
      expect(treeExpandAll.value).toBe(true)
    })

    it('应该正确折叠所有节点', () => {
      const { collapseAllNodes, treeExpandAll } = useMenuPermissionConfig()
      
      collapseAllNodes()
      
      expect(menuConfigStore.collapseAllNodes).toHaveBeenCalled()
      expect(treeExpandAll.value).toBe(false)
    })
  })

  describe('拖拽操作', () => {
    it('应该正确开始拖拽', () => {
      const { startDrag, isDragging } = useMenuPermissionConfig()
      
      startDrag('user-management')
      
      expect(menuConfigStore.startDrag).toHaveBeenCalledWith('user-management')
      expect(isDragging.value).toBe(true)
    })

    it('应该正确结束拖拽', () => {
      const { endDrag, isDragging } = useMenuPermissionConfig()
      
      endDrag()
      
      expect(menuConfigStore.endDrag).toHaveBeenCalled()
      expect(isDragging.value).toBe(false)
    })

    it('应该成功执行拖拽操作', async () => {
      const { performDragOperation } = useMenuPermissionConfig()
      
      const operation = {
        source_key: 'user-management',
        target_key: 'admin',
        position: 'inside' as const,
      }
      
      const result = await performDragOperation(operation)
      
      expect(result).toBe(true)
      expect(menuConfigStore.performDragOperation).toHaveBeenCalledWith(operation)
      expect(notification.showSuccess).toHaveBeenCalledWith('菜单排序更新成功')
    })
  })

  describe('选择操作', () => {
    it('应该正确选择菜单', () => {
      const { selectMenu, selectedMenuKeys, isMenuSelected } = useMenuPermissionConfig()
      
      selectMenu('user-management')
      
      expect(selectedMenuKeys.value).toContain('user-management')
      expect(isMenuSelected('user-management')).toBe(true)
    })

    it('应该正确取消选择菜单', () => {
      const { selectMenu, unselectMenu, selectedMenuKeys, isMenuSelected } = useMenuPermissionConfig()
      
      selectMenu('user-management')
      unselectMenu('user-management')
      
      expect(selectedMenuKeys.value).not.toContain('user-management')
      expect(isMenuSelected('user-management')).toBe(false)
    })

    it('应该正确切换菜单选择状态', () => {
      const { toggleMenuSelection, selectedMenuKeys } = useMenuPermissionConfig()
      
      toggleMenuSelection('user-management')
      expect(selectedMenuKeys.value).toContain('user-management')
      
      toggleMenuSelection('user-management')
      expect(selectedMenuKeys.value).not.toContain('user-management')
    })

    it('应该正确清空选择', () => {
      const { selectMenu, clearSelection, selectedMenuKeys } = useMenuPermissionConfig()
      
      selectMenu('user-management')
      selectMenu('user-list')
      clearSelection()
      
      expect(selectedMenuKeys.value).toEqual([])
    })
  })

  describe('表单验证', () => {
    it('应该验证菜单键不能为空', () => {
      const { validateConfigForm, formValidation } = useMenuPermissionConfig()
      
      const result = validateConfigForm({ menu_key: '', menu_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.menuKeyError).toBe('菜单键不能为空')
    })

    it('应该验证菜单键格式', () => {
      const { validateConfigForm, formValidation } = useMenuPermissionConfig()
      
      const result = validateConfigForm({ menu_key: '123invalid', menu_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.menuKeyError).toBe('菜单键只能包含字母、数字、下划线和连字符，且必须以字母开头')
    })

    it('应该验证菜单键唯一性', () => {
      menuConfigStore.isMenuKeyExists.mockReturnValue(true)
      
      const { validateConfigForm, formValidation } = useMenuPermissionConfig()
      
      const result = validateConfigForm({ menu_key: 'existing-menu', menu_name: 'Test' })
      
      expect(result).toBe(false)
      expect(formValidation.value.menuKeyError).toBe('菜单键已存在')
    })

    it('应该验证菜单名称不能为空', () => {
      const { validateConfigForm, formValidation } = useMenuPermissionConfig()
      
      const result = validateConfigForm({ menu_key: 'valid-key', menu_name: '' })
      
      expect(result).toBe(false)
      expect(formValidation.value.menuNameError).toBe('菜单名称不能为空')
    })

    it('菜单类型为菜单时应该验证菜单路径', () => {
      const { validateConfigForm, formValidation } = useMenuPermissionConfig()
      
      const result = validateConfigForm({ 
        menu_key: 'valid-key', 
        menu_name: 'Valid Name',
        menu_type: 'menu',
        menu_path: '',
      })
      
      expect(result).toBe(false)
      expect(formValidation.value.menuPathError).toBe('菜单类型为菜单时，菜单路径不能为空')
    })

    it('有效的表单数据应该通过验证', () => {
      const { validateConfigForm } = useMenuPermissionConfig()
      
      const result = validateConfigForm({
        menu_key: 'valid-key',
        menu_name: 'Valid Name',
        menu_type: 'menu',
        menu_path: '/valid-path',
      })
      
      expect(result).toBe(true)
    })
  })

  describe('辅助方法', () => {
    it('应该正确获取菜单类型显示文本', () => {
      const { getMenuTypeText } = useMenuPermissionConfig()
      
      expect(getMenuTypeText('menu')).toBe('菜单')
      expect(getMenuTypeText('button')).toBe('按钮')
      expect(getMenuTypeText('tab')).toBe('标签页')
      expect(getMenuTypeText('section')).toBe('区域')
    })

    it('应该正确获取菜单状态显示文本', () => {
      const { getMenuStatusText } = useMenuPermissionConfig()
      
      expect(getMenuStatusText('visible')).toBe('可见')
      expect(getMenuStatusText('hidden')).toBe('隐藏')
      expect(getMenuStatusText('disabled')).toBe('禁用')
    })

    it('应该正确获取权限逻辑显示文本', () => {
      const { getPermissionLogicText } = useMenuPermissionConfig()
      
      expect(getPermissionLogicText('AND')).toBe('需要所有权限')
      expect(getPermissionLogicText('OR')).toBe('需要任一权限')
    })

    it('应该正确查找菜单配置', () => {
      const { findConfigByKey } = useMenuPermissionConfig()
      
      expect(findConfigByKey('user-management')).toEqual(mockMenuConfig)
    })

    it('应该正确获取下一个排序顺序', () => {
      const { getNextSortOrder } = useMenuPermissionConfig()
      
      // Mock root configs with sort orders
      menuConfigStore.rootMenuConfigs = [
        { ...mockMenuConfig, sort_order: 0 },
        { ...mockMenuConfig, sort_order: 1 },
      ]
      
      expect(getNextSortOrder()).toBe(2)
    })
  })
})