/**
 * 权限类型定义单元测试
 * Unit tests for permission type definitions
 */

import { describe, it, expect } from 'vitest'
import type {
  Permission,
  PermissionStatus,
  PermissionAction,
  PermissionResource,
  PermissionModule,
  CreatePermissionRequest,
  PermissionTreeNode,
  PermissionCheckResult,
  PermissionStats,
  BatchPermissionRequest,
  PermissionDependency,
} from '../permissionTypes'

describe('Permission Types', () => {
  describe('Permission interface', () => {
    it('should accept valid permission data', () => {
      const validPermission: Permission = {
        id: 'perm-123',
        name: 'user.create',
        display_name: '创建用户',
        description: '创建新用户的权限',
        resource: 'user',
        action: 'create',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        level: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        created_by: 'admin-123',
      }

      expect(validPermission.id).toBe('perm-123')
      expect(validPermission.name).toBe('user.create')
      expect(validPermission.display_name).toBe('创建用户')
      expect(validPermission.resource).toBe('user')
      expect(validPermission.action).toBe('create')
      expect(validPermission.module).toBe('user_management')
      expect(validPermission.status).toBe('active')
      expect(validPermission.level).toBe(1)
    })

    it('should accept permission with hierarchical structure', () => {
      const parentPermission: Permission = {
        id: 'perm-parent',
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
        children: [],
      }

      const childPermission: Permission = {
        id: 'perm-child',
        name: 'user.create',
        display_name: '创建用户',
        resource: 'user',
        action: 'create',
        module: 'user_management',
        status: 'active',
        is_system_permission: true,
        parent_id: 'perm-parent',
        level: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      expect(parentPermission.children).toBeDefined()
      expect(childPermission.parent_id).toBe('perm-parent')
      expect(childPermission.level).toBeGreaterThan(parentPermission.level)
    })
  })

  describe('Permission enums', () => {
    it('should accept valid permission statuses', () => {
      const activeStatus: PermissionStatus = 'active'
      const inactiveStatus: PermissionStatus = 'inactive'
      const deprecatedStatus: PermissionStatus = 'deprecated'

      expect(activeStatus).toBe('active')
      expect(inactiveStatus).toBe('inactive')
      expect(deprecatedStatus).toBe('deprecated')
    })

    it('should accept valid permission actions', () => {
      const actions: PermissionAction[] = ['create', 'read', 'update', 'delete', 'manage', 'view', 'execute']

      actions.forEach(action => {
        expect(typeof action).toBe('string')
        expect(['create', 'read', 'update', 'delete', 'manage', 'view', 'execute']).toContain(action)
      })
    })

    it('should accept valid permission resources', () => {
      const resources: PermissionResource[] = [
        'user', 'role', 'permission', 'provider', 'model', 'chat', 'system', 'menu', 'audit', 'config'
      ]

      resources.forEach(resource => {
        expect(typeof resource).toBe('string')
      })
    })

    it('should accept valid permission modules', () => {
      const modules: PermissionModule[] = [
        'user_management',
        'permission_management',
        'provider_management',
        'model_management',
        'chat_management',
        'system_management',
        'audit_management'
      ]

      modules.forEach(module => {
        expect(typeof module).toBe('string')
      })
    })
  })

  describe('CreatePermissionRequest interface', () => {
    it('should accept valid create permission request', () => {
      const createRequest: CreatePermissionRequest = {
        name: 'role.delete',
        display_name: '删除角色',
        description: '删除角色的权限',
        resource: 'role',
        action: 'delete',
        module: 'permission_management',
        level: 3,
      }

      expect(createRequest.name).toBe('role.delete')
      expect(createRequest.display_name).toBe('删除角色')
      expect(createRequest.resource).toBe('role')
      expect(createRequest.action).toBe('delete')
      expect(createRequest.module).toBe('permission_management')
      expect(createRequest.level).toBe(3)
    })

    it('should accept create request with parent permission', () => {
      const createRequest: CreatePermissionRequest = {
        name: 'user:profile:update',
        display_name: '更新用户资料',
        resource: 'user',
        action: 'update',
        module: 'user_management',
        parent_id: 'user.manage',
        level: 2,
      }

      expect(createRequest.parent_id).toBe('user.manage')
    })
  })

  describe('PermissionTreeNode interface', () => {
    it('should accept valid permission tree node', () => {
      const permission: Permission = {
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
      }

      const treeNode: PermissionTreeNode = {
        permission,
        children: [],
        expanded: true,
        selected: false,
        disabled: false,
        level: 1,
      }

      expect(treeNode.permission).toBe(permission)
      expect(treeNode.children).toEqual([])
      expect(treeNode.expanded).toBe(true)
      expect(treeNode.selected).toBe(false)
      expect(treeNode.level).toBe(1)
    })
  })

  describe('PermissionCheckResult interface', () => {
    it('should accept valid permission check result', () => {
      const hasPermissionResult: PermissionCheckResult = {
        hasPermission: true,
        message: '权限验证通过',
      }

      const noPermissionResult: PermissionCheckResult = {
        hasPermission: false,
        missingPermissions: ['user.create', 'user.update'],
        message: '缺少必要权限',
      }

      expect(hasPermissionResult.hasPermission).toBe(true)
      expect(hasPermissionResult.missingPermissions).toBeUndefined()

      expect(noPermissionResult.hasPermission).toBe(false)
      expect(noPermissionResult.missingPermissions).toEqual(['user.create', 'user.update'])
    })
  })

  describe('PermissionStats interface', () => {
    it('should accept valid permission statistics', () => {
      const stats: PermissionStats = {
        total_permissions: 50,
        system_permissions: 30,
        custom_permissions: 20,
        permissions_by_module: {
          user_management: 15,
          permission_management: 10,
          provider_management: 8,
          model_management: 7,
          chat_management: 5,
          system_management: 3,
          audit_management: 2,
        },
        permissions_by_resource: {
          user: 15,
          role: 8,
          permission: 7,
          provider: 6,
          model: 5,
          chat: 4,
          system: 3,
          menu: 1,
          audit: 1,
          config: 0,
        },
        recent_permissions: [],
      }

      expect(stats.total_permissions).toBe(50)
      expect(stats.system_permissions).toBe(30)
      expect(stats.custom_permissions).toBe(20)
      expect(typeof stats.permissions_by_module).toBe('object')
      expect(typeof stats.permissions_by_resource).toBe('object')
      expect(Array.isArray(stats.recent_permissions)).toBe(true)
    })
  })

  describe('BatchPermissionRequest interface', () => {
    it('should accept valid batch permission request', () => {
      const batchRequest: BatchPermissionRequest = {
        permission_ids: ['perm-1', 'perm-2', 'perm-3'],
        action: 'activate',
      }

      expect(batchRequest.permission_ids).toEqual(['perm-1', 'perm-2', 'perm-3'])
      expect(batchRequest.action).toBe('activate')
    })

    it('should accept different batch actions', () => {
      const activateRequest: BatchPermissionRequest = {
        permission_ids: ['perm-1'],
        action: 'activate',
      }

      const deactivateRequest: BatchPermissionRequest = {
        permission_ids: ['perm-2'],
        action: 'deactivate',
      }

      const deleteRequest: BatchPermissionRequest = {
        permission_ids: ['perm-3'],
        action: 'delete',
      }

      expect(activateRequest.action).toBe('activate')
      expect(deactivateRequest.action).toBe('deactivate')
      expect(deleteRequest.action).toBe('delete')
    })
  })

  describe('PermissionDependency interface', () => {
    it('should accept valid permission dependency', () => {
      const dependency: PermissionDependency = {
        permission_id: 'user.delete',
        depends_on: ['user.view', 'user.manage'],
        required_by: ['admin.full_access'],
      }

      expect(dependency.permission_id).toBe('user.delete')
      expect(dependency.depends_on).toEqual(['user.view', 'user.manage'])
      expect(dependency.required_by).toEqual(['admin.full_access'])
    })
  })

  describe('Permission naming convention', () => {
    it('should follow resource.action naming pattern', () => {
      const permissions = [
        'user.create',
        'user.read',
        'user.update',
        'user.delete',
        'role.manage',
        'permission.view',
        'system.config',
      ]

      permissions.forEach(permissionName => {
        expect(permissionName).toMatch(/^[a-z_]+\.[a-z_]+$/)
        const [resource, action] = permissionName.split('.')
        expect(resource).toBeTruthy()
        expect(action).toBeTruthy()
      })
    })
  })
})
