/**
 * 权限管理工具函数单元测试
 * Unit tests for permission management utility functions
 */

import { describe, it, expect } from 'vitest'
import {
  validatePermissionName,
  formatPermissionName,
  parsePermissionName,
  checkPermission,
  checkMultiplePermissions,
  buildPermissionTree,
  searchPermissionTree,
  getPermissionAncestors,
  getPermissionDescendants,
  validateMenuKey,
  buildMenuTree,
  validateMenuPermission,
  exportMenuConfig,
  validateMenuConfigImport,
  processMenuConfigImport,
  calculatePermissionLevel,
  generatePermissionDisplayName,
} from '../permission'

import type {
  Permission,
  MenuPermissionConfig,
  MenuConfigImportRequest,
} from '@/types/permission'

describe('Permission Utility Functions', () => {
  describe('validatePermissionName', () => {
    it('should validate correct permission names', () => {
      expect(validatePermissionName('user.create')).toBe(true)
      expect(validatePermissionName('user.profile.update')).toBe(true)
      expect(validatePermissionName('system.config.manage')).toBe(true)
      expect(validatePermissionName('role_management.view')).toBe(true)
    })

    it('should reject invalid permission names', () => {
      expect(validatePermissionName('')).toBe(false)
      expect(validatePermissionName('user')).toBe(false)
      expect(validatePermissionName('user.')).toBe(false)
      expect(validatePermissionName('.create')).toBe(false)
      expect(validatePermissionName('user.create.')).toBe(false)
      expect(validatePermissionName('user-create')).toBe(false)
      expect(validatePermissionName('User.Create')).toBe(false)
      expect(validatePermissionName('user create')).toBe(false)
    })

    it('should handle non-string inputs', () => {
      expect(validatePermissionName(null as any)).toBe(false)
      expect(validatePermissionName(undefined as any)).toBe(false)
      expect(validatePermissionName(123 as any)).toBe(false)
      expect(validatePermissionName({} as any)).toBe(false)
    })
  })

  describe('formatPermissionName', () => {
    it('should format permission names correctly', () => {
      expect(formatPermissionName('user', 'create')).toBe('user.create')
      expect(formatPermissionName('user', 'update', 'profile')).toBe('user.profile.update')
      expect(formatPermissionName('system', 'manage', 'config')).toBe('system.config.manage')
    })

    it('should handle empty subResource', () => {
      expect(formatPermissionName('role', 'delete', '')).toBe('role.delete')
      expect(formatPermissionName('role', 'delete', undefined)).toBe('role.delete')
    })
  })

  describe('parsePermissionName', () => {
    it('should parse valid permission names', () => {
      expect(parsePermissionName('user.create')).toEqual({
        resource: 'user',
        action: 'create',
        subResource: undefined,
      })

      expect(parsePermissionName('user.profile.update')).toEqual({
        resource: 'user',
        action: 'update',
        subResource: 'profile',
      })

      expect(parsePermissionName('system.config.manage')).toEqual({
        resource: 'system',
        action: 'manage',
        subResource: 'config',
      })
    })

    it('should return null for invalid permission names', () => {
      expect(parsePermissionName('invalid')).toBeNull()
      expect(parsePermissionName('user.')).toBeNull()
      expect(parsePermissionName('.create')).toBeNull()
      expect(parsePermissionName('')).toBeNull()
    })
  })

  describe('checkPermission', () => {
    const userPermissions = ['user.view', 'user.create', 'role.view']

    it('should return true for existing permissions', () => {
      const result = checkPermission(userPermissions, 'user.view')
      expect(result.hasPermission).toBe(true)
      expect(result.missingPermissions).toBeUndefined()
      expect(result.message).toBe('权限验证通过')
    })

    it('should return false for missing permissions', () => {
      const result = checkPermission(userPermissions, 'user.delete')
      expect(result.hasPermission).toBe(false)
      expect(result.missingPermissions).toEqual(['user.delete'])
      expect(result.message).toBe('缺少权限: user.delete')
    })
  })

  describe('checkMultiplePermissions', () => {
    const userPermissions = ['user.view', 'user.create', 'role.view']

    it('should handle AND logic correctly', () => {
      const result1 = checkMultiplePermissions(
        userPermissions,
        ['user.view', 'user.create'],
        'AND'
      )
      expect(result1.hasPermission).toBe(true)

      const result2 = checkMultiplePermissions(
        userPermissions,
        ['user.view', 'user.delete'],
        'AND'
      )
      expect(result2.hasPermission).toBe(false)
      expect(result2.missingPermissions).toEqual(['user.delete'])
    })

    it('should handle OR logic correctly', () => {
      const result1 = checkMultiplePermissions(
        userPermissions,
        ['user.view', 'user.delete'],
        'OR'
      )
      expect(result1.hasPermission).toBe(true)

      const result2 = checkMultiplePermissions(
        userPermissions,
        ['user.delete', 'user.manage'],
        'OR'
      )
      expect(result2.hasPermission).toBe(false)
    })

    it('should handle empty permission list', () => {
      const result = checkMultiplePermissions(userPermissions, [], 'AND')
      expect(result.hasPermission).toBe(true)
      expect(result.message).toBe('无需权限验证')
    })
  })

  describe('buildPermissionTree', () => {
    const permissions: Permission[] = [
      {
        id: 'perm-1',
        name: 'user.manage',
        display_name: '用户管理',
        resource: 'user',
        action: 'manage',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'perm-2',
        name: 'user.create',
        display_name: '创建用户',
        resource: 'user',
        action: 'create',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        parent_id: 'perm-1',
        level: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'perm-3',
        name: 'role.view',
        display_name: '查看角色',
        resource: 'role',
        action: 'view',
        module: 'permission_management',
        status: 'active',
        is_system_permission: true,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]

    it('should build permission tree correctly', () => {
      const tree = buildPermissionTree(permissions)
      
      expect(tree).toHaveLength(2) // 两个根节点
      
      const userManageNode = tree.find(node => node.permission.id === 'perm-1')
      expect(userManageNode).toBeDefined()
      expect(userManageNode!.children).toHaveLength(1)
      expect(userManageNode!.children[0].permission.id).toBe('perm-2')
      
      const roleViewNode = tree.find(node => node.permission.id === 'perm-3')
      expect(roleViewNode).toBeDefined()
      expect(roleViewNode!.children).toHaveLength(0)
    })

    it('should sort nodes by module and name', () => {
      const tree = buildPermissionTree(permissions)
      
      // 应该按模块排序：permission_management 在前，user_management 在后
      expect(tree[0].permission.module).toBe('permission_management')
      expect(tree[1].permission.module).toBe('user_management')
    })
  })

  describe('searchPermissionTree', () => {
    const permissions: Permission[] = [
      {
        id: 'perm-1',
        name: 'user.manage',
        display_name: '用户管理',
        description: '管理系统用户',
        resource: 'user',
        action: 'manage',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'perm-2',
        name: 'role.view',
        display_name: '查看角色',
        description: '查看系统角色',
        resource: 'role',
        action: 'view',
        module: 'permission_management',
        status: 'active',
        is_system_permission: true,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]

    it('should search by permission name', () => {
      const tree = buildPermissionTree(permissions)
      const results = searchPermissionTree(tree, 'user')
      
      expect(results).toHaveLength(1)
      expect(results[0].permission.name).toBe('user.manage')
    })

    it('should search by display name', () => {
      const tree = buildPermissionTree(permissions)
      const results = searchPermissionTree(tree, '角色')
      
      expect(results).toHaveLength(1)
      expect(results[0].permission.display_name).toBe('查看角色')
    })

    it('should search by description', () => {
      const tree = buildPermissionTree(permissions)
      const results = searchPermissionTree(tree, '管理系统')
      
      expect(results).toHaveLength(1)
      expect(results[0].permission.description).toBe('管理系统用户')
    })

    it('should return all nodes for empty search', () => {
      const tree = buildPermissionTree(permissions)
      const results = searchPermissionTree(tree, '')
      
      expect(results).toHaveLength(2)
    })
  })

  describe('getPermissionAncestors', () => {
    const permissions: Permission[] = [
      {
        id: 'perm-1',
        name: 'user.manage',
        display_name: '用户管理',
        resource: 'user',
        action: 'manage',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'perm-2',
        name: 'user.profile.manage',
        display_name: '用户资料管理',
        resource: 'user',
        action: 'manage',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        parent_id: 'perm-1',
        level: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'perm-3',
        name: 'user.profile.update',
        display_name: '更新用户资料',
        resource: 'user',
        action: 'update',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        parent_id: 'perm-2',
        level: 3,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]

    it('should get all ancestors correctly', () => {
      const ancestors = getPermissionAncestors(permissions[2], permissions)
      
      expect(ancestors).toHaveLength(2)
      expect(ancestors[0].id).toBe('perm-1')
      expect(ancestors[1].id).toBe('perm-2')
    })

    it('should return empty array for root permission', () => {
      const ancestors = getPermissionAncestors(permissions[0], permissions)
      expect(ancestors).toHaveLength(0)
    })
  })

  describe('getPermissionDescendants', () => {
    const permissions: Permission[] = [
      {
        id: 'perm-1',
        name: 'user.manage',
        display_name: '用户管理',
        resource: 'user',
        action: 'manage',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'perm-2',
        name: 'user.create',
        display_name: '创建用户',
        resource: 'user',
        action: 'create',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        parent_id: 'perm-1',
        level: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'perm-3',
        name: 'user.update',
        display_name: '更新用户',
        resource: 'user',
        action: 'update',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        parent_id: 'perm-1',
        level: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]

    it('should get all descendants correctly', () => {
      const descendants = getPermissionDescendants(permissions[0], permissions)
      
      expect(descendants).toHaveLength(2)
      expect(descendants.map(d => d.id)).toContain('perm-2')
      expect(descendants.map(d => d.id)).toContain('perm-3')
    })

    it('should return empty array for leaf permission', () => {
      const descendants = getPermissionDescendants(permissions[1], permissions)
      expect(descendants).toHaveLength(0)
    })
  })

  describe('validateMenuKey', () => {
    it('should validate correct menu keys', () => {
      expect(validateMenuKey('dashboard')).toBe(true)
      expect(validateMenuKey('admin')).toBe(true)
      expect(validateMenuKey('admin.users')).toBe(true)
      expect(validateMenuKey('admin.users.create')).toBe(true)
      expect(validateMenuKey('user_management')).toBe(true)
    })

    it('should reject invalid menu keys', () => {
      expect(validateMenuKey('')).toBe(false)
      expect(validateMenuKey('admin.')).toBe(false)
      expect(validateMenuKey('.users')).toBe(false)
      expect(validateMenuKey('admin..users')).toBe(false)
      expect(validateMenuKey('Admin.Users')).toBe(false)
      expect(validateMenuKey('admin-users')).toBe(false)
      expect(validateMenuKey('admin users')).toBe(false)
    })
  })

  describe('buildMenuTree', () => {
    const menuConfigs: MenuPermissionConfig[] = [
      {
        id: 'menu-1',
        menu_key: 'admin',
        menu_name: '系统管理',
        menu_path: '/admin',
        menu_type: 'menu',
        required_permissions: ['admin.access'],
        permission_logic: 'AND',
        is_visible: true,
        status: 'visible',
        sort_order: 1,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'menu-2',
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
      },
      {
        id: 'menu-3',
        menu_key: 'dashboard',
        menu_name: '仪表板',
        menu_path: '/dashboard',
        menu_type: 'menu',
        required_permissions: [],
        permission_logic: 'AND',
        is_visible: true,
        status: 'visible',
        sort_order: 0,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]

    it('should build menu tree correctly', () => {
      const tree = buildMenuTree(menuConfigs)
      
      expect(tree).toHaveLength(2) // 两个根节点
      
      // 应该按 sort_order 排序
      expect(tree[0].config.menu_key).toBe('dashboard')
      expect(tree[1].config.menu_key).toBe('admin')
      
      // 检查子节点
      const adminNode = tree[1]
      expect(adminNode.children).toHaveLength(1)
      expect(adminNode.children[0].config.menu_key).toBe('admin.users')
    })
  })

  describe('validateMenuPermission', () => {
    const menuConfig: MenuPermissionConfig = {
      id: 'menu-1',
      menu_key: 'admin.users',
      menu_name: '用户管理',
      menu_path: '/admin/users',
      menu_type: 'menu',
      required_permissions: ['user.view', 'user.manage'],
      permission_logic: 'AND',
      is_visible: true,
      status: 'visible',
      sort_order: 1,
      level: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    it('should validate menu permission with AND logic', () => {
      const userPermissions = ['user.view', 'user.manage']
      const result = validateMenuPermission(menuConfig, userPermissions)
      
      expect(result.hasPermission).toBe(true)
      expect(result.isVisible).toBe(true)
      expect(result.menu_key).toBe('admin.users')
    })

    it('should reject menu permission when missing required permissions', () => {
      const userPermissions = ['user.view']
      const result = validateMenuPermission(menuConfig, userPermissions)
      
      expect(result.hasPermission).toBe(false)
      expect(result.isVisible).toBe(false)
      expect(result.missingPermissions).toEqual(['user.manage'])
    })

    it('should handle menu with no required permissions', () => {
      const noPermissionMenu: MenuPermissionConfig = {
        ...menuConfig,
        required_permissions: [],
      }
      
      const result = validateMenuPermission(noPermissionMenu, [])
      
      expect(result.hasPermission).toBe(true)
      expect(result.isVisible).toBe(true)
      expect(result.message).toBe('无需权限验证')
    })
  })

  describe('exportMenuConfig', () => {
    const configs: MenuPermissionConfig[] = [
      {
        id: 'menu-1',
        menu_key: 'dashboard',
        menu_name: '仪表板',
        menu_path: '/dashboard',
        menu_type: 'menu',
        required_permissions: [],
        permission_logic: 'AND',
        is_visible: true,
        status: 'visible',
        sort_order: 0,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]

    it('should export menu config correctly', () => {
      const exportData = exportMenuConfig(configs, 'admin-123', '测试导出')
      
      expect(exportData.version).toBe('1.0.0')
      expect(exportData.configs).toEqual(configs)
      expect(exportData.exported_by).toBe('admin-123')
      expect(exportData.description).toBe('测试导出')
      expect(exportData.exported_at).toBeDefined()
    })
  })

  describe('validateMenuConfigImport', () => {
    it('should validate correct import data', () => {
      const importData = {
        version: '1.0.0',
        configs: [
          {
            menu_key: 'test_menu',
            menu_name: '测试菜单',
            menu_path: '/test',
            menu_type: 'menu',
            required_permissions: ['test.view'],
            permission_logic: 'AND',
            is_visible: true,
            status: 'visible',
            sort_order: 1,
            level: 1,
          },
        ],
      }
      
      const result = validateMenuConfigImport(importData)
      expect(result.valid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should reject invalid import data', () => {
      const invalidData = {
        configs: [
          {
            menu_key: 'Invalid Key',
            menu_name: '',
            required_permissions: 'not-an-array',
            permission_logic: 'INVALID',
          },
        ],
      }
      
      const result = validateMenuConfigImport(invalidData)
      expect(result.valid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })
  })

  describe('calculatePermissionLevel', () => {
    it('should calculate permission levels correctly', () => {
      expect(calculatePermissionLevel('user.view')).toBe(1)
      expect(calculatePermissionLevel('user.create')).toBe(2)
      expect(calculatePermissionLevel('user.delete')).toBe(3)
      expect(calculatePermissionLevel('user.manage')).toBe(4)
      expect(calculatePermissionLevel('user.profile.update')).toBe(3) // 2 + 1 for subresource
    })

    it('should handle invalid permission names', () => {
      expect(calculatePermissionLevel('invalid')).toBe(1)
      expect(calculatePermissionLevel('')).toBe(1)
    })
  })

  describe('generatePermissionDisplayName', () => {
    it('should generate display names correctly', () => {
      expect(generatePermissionDisplayName('user.create')).toBe('创建用户')
      expect(generatePermissionDisplayName('role.delete')).toBe('删除角色')
      expect(generatePermissionDisplayName('system.manage')).toBe('管理系统')
      expect(generatePermissionDisplayName('user.profile.update')).toBe('更新用户profile')
    })

    it('should handle unknown resources and actions', () => {
      expect(generatePermissionDisplayName('unknown.action')).toBe('actionunknown')
      expect(generatePermissionDisplayName('resource.unknown')).toBe('unknownresource')
    })

    it('should handle invalid permission names', () => {
      expect(generatePermissionDisplayName('invalid')).toBe('invalid')
      expect(generatePermissionDisplayName('')).toBe('')
    })
  })
})