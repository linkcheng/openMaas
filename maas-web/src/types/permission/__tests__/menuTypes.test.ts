/**
 * 菜单权限配置类型定义单元测试
 * Unit tests for menu permission configuration type definitions
 */

import { describe, it, expect } from 'vitest'
import type {
  MenuPermissionConfig,
  MenuType,
  MenuStatus,
  PermissionLogic,
  CreateMenuConfigRequest,
  UpdateMenuConfigRequest,
  MenuTreeNode,
  MenuPermissionResult,
  MenuConfigExport,
  MenuConfigImportRequest,
  MenuConfigImportResult,
  MenuPreviewConfig,
  MenuPreviewResult,
  MenuQueryParams,
  MenuDragOperation,
  BatchMenuOperationRequest,
} from '../menuTypes'

describe('Menu Types', () => {
  describe('MenuPermissionConfig interface', () => {
    it('should accept valid menu permission config', () => {
      const menuConfig: MenuPermissionConfig = {
        id: 'menu-123',
        menu_key: 'user_management',
        menu_name: '用户管理',
        menu_path: '/admin/users',
        menu_icon: 'user',
        menu_type: 'menu',
        required_permissions: ['user.view', 'user.manage'],
        permission_logic: 'AND',
        is_visible: true,
        status: 'visible',
        sort_order: 1,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        created_by: 'admin-123',
      }

      expect(menuConfig.id).toBe('menu-123')
      expect(menuConfig.menu_key).toBe('user_management')
      expect(menuConfig.menu_name).toBe('用户管理')
      expect(menuConfig.menu_path).toBe('/admin/users')
      expect(menuConfig.menu_type).toBe('menu')
      expect(menuConfig.required_permissions).toEqual(['user.view', 'user.manage'])
      expect(menuConfig.permission_logic).toBe('AND')
      expect(menuConfig.is_visible).toBe(true)
      expect(menuConfig.sort_order).toBe(1)
    })

    it('should accept menu config with children', () => {
      const parentMenu: MenuPermissionConfig = {
        id: 'menu-parent',
        menu_key: 'admin',
        menu_name: '系统管理',
        menu_path: '/admin',
        menu_type: 'menu',
        required_permissions: ['admin.access'],
        permission_logic: 'OR',
        is_visible: true,
        status: 'visible',
        sort_order: 1,
        level: 1,
        children: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      const childMenu: MenuPermissionConfig = {
        id: 'menu-child',
        menu_key: 'admin.users',
        menu_name: '用户管理',
        menu_path: '/admin/users',
        parent_key: 'admin',
        menu_type: 'menu',
        required_permissions: ['user.view'],
        permission_logic: 'AND',
        is_visible: true,
        status: 'visible',
        sort_order: 1,
        level: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      expect(parentMenu.children).toBeDefined()
      expect(childMenu.parent_key).toBe('admin')
      expect(childMenu.level).toBeGreaterThan(parentMenu.level)
    })
  })

  describe('Menu enums', () => {
    it('should accept valid menu types', () => {
      const menuType: MenuType = 'menu'
      const buttonType: MenuType = 'button'
      const tabType: MenuType = 'tab'
      const sectionType: MenuType = 'section'

      expect(menuType).toBe('menu')
      expect(buttonType).toBe('button')
      expect(tabType).toBe('tab')
      expect(sectionType).toBe('section')
    })

    it('should accept valid menu statuses', () => {
      const visibleStatus: MenuStatus = 'visible'
      const hiddenStatus: MenuStatus = 'hidden'
      const disabledStatus: MenuStatus = 'disabled'

      expect(visibleStatus).toBe('visible')
      expect(hiddenStatus).toBe('hidden')
      expect(disabledStatus).toBe('disabled')
    })

    it('should accept valid permission logic', () => {
      const andLogic: PermissionLogic = 'AND'
      const orLogic: PermissionLogic = 'OR'

      expect(andLogic).toBe('AND')
      expect(orLogic).toBe('OR')
    })
  })

  describe('CreateMenuConfigRequest interface', () => {
    it('should accept valid create menu config request', () => {
      const createRequest: CreateMenuConfigRequest = {
        menu_key: 'dashboard',
        menu_name: '仪表板',
        menu_path: '/dashboard',
        menu_icon: 'dashboard',
        menu_type: 'menu',
        required_permissions: ['dashboard.view'],
        permission_logic: 'AND',
        is_visible: true,
        sort_order: 0,
      }

      expect(createRequest.menu_key).toBe('dashboard')
      expect(createRequest.menu_name).toBe('仪表板')
      expect(createRequest.menu_path).toBe('/dashboard')
      expect(createRequest.menu_type).toBe('menu')
      expect(createRequest.required_permissions).toEqual(['dashboard.view'])
      expect(createRequest.permission_logic).toBe('AND')
    })

    it('should accept create request with parent', () => {
      const createRequest: CreateMenuConfigRequest = {
        menu_key: 'admin.roles',
        menu_name: '角色管理',
        menu_path: '/admin/roles',
        parent_key: 'admin',
        menu_type: 'menu',
        required_permissions: ['role.view'],
        permission_logic: 'AND',
        is_visible: true,
        sort_order: 2,
      }

      expect(createRequest.parent_key).toBe('admin')
    })
  })

  describe('MenuTreeNode interface', () => {
    it('should accept valid menu tree node', () => {
      const menuConfig: MenuPermissionConfig = {
        id: 'menu-1',
        menu_key: 'users',
        menu_name: '用户管理',
        menu_path: '/users',
        menu_type: 'menu',
        required_permissions: ['user.view'],
        permission_logic: 'AND',
        is_visible: true,
        status: 'visible',
        sort_order: 1,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      const treeNode: MenuTreeNode = {
        config: menuConfig,
        children: [],
        expanded: true,
        selected: false,
        draggable: true,
        level: 1,
        hasPermission: true,
      }

      expect(treeNode.config).toBe(menuConfig)
      expect(treeNode.children).toEqual([])
      expect(treeNode.expanded).toBe(true)
      expect(treeNode.hasPermission).toBe(true)
    })
  })

  describe('MenuPermissionResult interface', () => {
    it('should accept valid menu permission result', () => {
      const hasPermissionResult: MenuPermissionResult = {
        menu_key: 'users',
        hasPermission: true,
        isVisible: true,
        message: '权限验证通过',
      }

      const noPermissionResult: MenuPermissionResult = {
        menu_key: 'admin',
        hasPermission: false,
        isVisible: false,
        missingPermissions: ['admin.access'],
        message: '缺少管理员权限',
      }

      expect(hasPermissionResult.hasPermission).toBe(true)
      expect(hasPermissionResult.isVisible).toBe(true)
      expect(noPermissionResult.hasPermission).toBe(false)
      expect(noPermissionResult.missingPermissions).toEqual(['admin.access'])
    })
  })

  describe('MenuConfigExport interface', () => {
    it('should accept valid menu config export', () => {
      const exportData: MenuConfigExport = {
        version: '1.0.0',
        exported_at: '2024-01-01T00:00:00Z',
        configs: [],
        exported_by: 'admin-123',
        description: '菜单配置导出',
      }

      expect(exportData.version).toBe('1.0.0')
      expect(exportData.exported_at).toBe('2024-01-01T00:00:00Z')
      expect(Array.isArray(exportData.configs)).toBe(true)
      expect(exportData.exported_by).toBe('admin-123')
    })
  })

  describe('MenuConfigImportRequest interface', () => {
    it('should accept valid menu config import request', () => {
      const importRequest: MenuConfigImportRequest = {
        configs: [
          {
            menu_key: 'imported_menu',
            menu_name: '导入菜单',
            menu_path: '/imported',
            menu_type: 'menu',
            required_permissions: ['imported.view'],
            permission_logic: 'AND',
            is_visible: true,
            status: 'visible',
            sort_order: 1,
            level: 1,
          }
        ],
        import_mode: 'merge',
        overwrite_existing: false,
      }

      expect(importRequest.configs).toHaveLength(1)
      expect(importRequest.import_mode).toBe('merge')
      expect(importRequest.overwrite_existing).toBe(false)
    })

    it('should accept different import modes', () => {
      const mergeRequest: MenuConfigImportRequest = {
        configs: [],
        import_mode: 'merge',
      }

      const replaceRequest: MenuConfigImportRequest = {
        configs: [],
        import_mode: 'replace',
      }

      const appendRequest: MenuConfigImportRequest = {
        configs: [],
        import_mode: 'append',
      }

      expect(mergeRequest.import_mode).toBe('merge')
      expect(replaceRequest.import_mode).toBe('replace')
      expect(appendRequest.import_mode).toBe('append')
    })
  })

  describe('MenuConfigImportResult interface', () => {
    it('should accept valid menu config import result', () => {
      const importResult: MenuConfigImportResult = {
        success: true,
        imported_count: 5,
        skipped_count: 2,
        failed_count: 1,
        errors: ['菜单键重复: duplicate_key'],
        warnings: ['权限不存在: non_existent_permission'],
        imported_ids: ['menu-1', 'menu-2', 'menu-3', 'menu-4', 'menu-5'],
      }

      expect(importResult.success).toBe(true)
      expect(importResult.imported_count).toBe(5)
      expect(importResult.skipped_count).toBe(2)
      expect(importResult.failed_count).toBe(1)
      expect(importResult.errors).toHaveLength(1)
      expect(importResult.warnings).toHaveLength(1)
      expect(importResult.imported_ids).toHaveLength(5)
    })
  })

  describe('MenuPreviewConfig interface', () => {
    it('should accept valid menu preview config', () => {
      const previewConfig: MenuPreviewConfig = {
        role_id: 'role-123',
        user_id: 'user-456',
        preview_mode: 'combined',
        show_permission_info: true,
        show_hidden_menus: false,
      }

      expect(previewConfig.role_id).toBe('role-123')
      expect(previewConfig.user_id).toBe('user-456')
      expect(previewConfig.preview_mode).toBe('combined')
      expect(previewConfig.show_permission_info).toBe(true)
      expect(previewConfig.show_hidden_menus).toBe(false)
    })

    it('should accept different preview modes', () => {
      const rolePreview: MenuPreviewConfig = {
        role_id: 'role-123',
        preview_mode: 'role',
      }

      const userPreview: MenuPreviewConfig = {
        role_id: 'role-123',
        user_id: 'user-456',
        preview_mode: 'user',
      }

      const combinedPreview: MenuPreviewConfig = {
        role_id: 'role-123',
        user_id: 'user-456',
        preview_mode: 'combined',
      }

      expect(rolePreview.preview_mode).toBe('role')
      expect(userPreview.preview_mode).toBe('user')
      expect(combinedPreview.preview_mode).toBe('combined')
    })
  })

  describe('MenuDragOperation interface', () => {
    it('should accept valid menu drag operation', () => {
      const dragOperation: MenuDragOperation = {
        source_menu_key: 'menu_a',
        target_menu_key: 'menu_b',
        drop_type: 'after',
        new_sort_order: 3,
        new_parent_key: 'parent_menu',
      }

      expect(dragOperation.source_menu_key).toBe('menu_a')
      expect(dragOperation.target_menu_key).toBe('menu_b')
      expect(dragOperation.drop_type).toBe('after')
      expect(dragOperation.new_sort_order).toBe(3)
      expect(dragOperation.new_parent_key).toBe('parent_menu')
    })

    it('should accept different drop types', () => {
      const beforeDrop: MenuDragOperation = {
        source_menu_key: 'menu_a',
        target_menu_key: 'menu_b',
        drop_type: 'before',
        new_sort_order: 1,
      }

      const afterDrop: MenuDragOperation = {
        source_menu_key: 'menu_a',
        target_menu_key: 'menu_b',
        drop_type: 'after',
        new_sort_order: 2,
      }

      const innerDrop: MenuDragOperation = {
        source_menu_key: 'menu_a',
        target_menu_key: 'menu_b',
        drop_type: 'inner',
        new_sort_order: 1,
        new_parent_key: 'menu_b',
      }

      expect(beforeDrop.drop_type).toBe('before')
      expect(afterDrop.drop_type).toBe('after')
      expect(innerDrop.drop_type).toBe('inner')
    })
  })

  describe('BatchMenuOperationRequest interface', () => {
    it('should accept valid batch menu operation request', () => {
      const batchRequest: BatchMenuOperationRequest = {
        menu_keys: ['menu_1', 'menu_2', 'menu_3'],
        operation: 'hide',
        params: { reason: 'maintenance' },
      }

      expect(batchRequest.menu_keys).toEqual(['menu_1', 'menu_2', 'menu_3'])
      expect(batchRequest.operation).toBe('hide')
      expect(batchRequest.params).toEqual({ reason: 'maintenance' })
    })

    it('should accept different batch operations', () => {
      const operations = ['show', 'hide', 'enable', 'disable', 'delete']
      
      operations.forEach(operation => {
        const request: BatchMenuOperationRequest = {
          menu_keys: ['menu_1'],
          operation: operation as any,
        }
        
        expect(request.operation).toBe(operation)
      })
    })
  })

  describe('Menu key naming convention', () => {
    it('should follow hierarchical naming pattern', () => {
      const menuKeys = [
        'dashboard',
        'admin',
        'admin.users',
        'admin.users.create',
        'admin.roles',
        'admin.permissions',
        'system',
        'system.config',
        'system.logs',
      ]

      menuKeys.forEach(menuKey => {
        expect(menuKey).toMatch(/^[a-z_]+(\.[a-z_]+)*$/)
        
        if (menuKey.includes('.')) {
          const parts = menuKey.split('.')
          expect(parts.length).toBeGreaterThan(1)
          parts.forEach(part => {
            expect(part).toMatch(/^[a-z_]+$/)
          })
        }
      })
    })
  })
})