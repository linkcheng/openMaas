/**
 * 角色类型定义单元测试
 * Unit tests for role type definitions
 */

import { describe, it, expect } from 'vitest'
import type {
  Role,
  RoleType,
  RoleStatus,
  CreateRoleRequest,
  UpdateRoleRequest,
  RolePermissionAssignRequest,
  RoleQueryParams,
  RoleStats,
} from '../roleTypes'

describe('Role Types', () => {
  describe('Role interface', () => {
    it('should accept valid role data', () => {
      const validRole: Role = {
        id: 'role-123',
        name: 'admin',
        display_name: '系统管理员',
        description: '系统管理员角色',
        role_type: 'system',
        is_system_role: true,
        status: 'active',
        permissions: [],
        user_count: 5,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        created_by: 'user-123',
        updated_by: 'user-123',
      }

      expect(validRole.id).toBe('role-123')
      expect(validRole.name).toBe('admin')
      expect(validRole.display_name).toBe('系统管理员')
      expect(validRole.role_type).toBe('system')
      expect(validRole.is_system_role).toBe(true)
      expect(validRole.status).toBe('active')
    })

    it('should accept role with minimal required fields', () => {
      const minimalRole: Role = {
        id: 'role-456',
        name: 'user',
        display_name: '普通用户',
        role_type: 'custom',
        is_system_role: false,
        status: 'active',
        permissions: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      expect(minimalRole.description).toBeUndefined()
      expect(minimalRole.user_count).toBeUndefined()
      expect(minimalRole.created_by).toBeUndefined()
    })
  })

  describe('RoleType enum', () => {
    it('should accept valid role types', () => {
      const systemType: RoleType = 'system'
      const customType: RoleType = 'custom'

      expect(systemType).toBe('system')
      expect(customType).toBe('custom')
    })
  })

  describe('RoleStatus enum', () => {
    it('should accept valid role statuses', () => {
      const activeStatus: RoleStatus = 'active'
      const inactiveStatus: RoleStatus = 'inactive'
      const deletedStatus: RoleStatus = 'deleted'

      expect(activeStatus).toBe('active')
      expect(inactiveStatus).toBe('inactive')
      expect(deletedStatus).toBe('deleted')
    })
  })

  describe('CreateRoleRequest interface', () => {
    it('should accept valid create role request', () => {
      const createRequest: CreateRoleRequest = {
        name: 'editor',
        display_name: '编辑者',
        description: '内容编辑者角色',
        role_type: 'custom',
        permission_ids: ['perm-1', 'perm-2'],
      }

      expect(createRequest.name).toBe('editor')
      expect(createRequest.display_name).toBe('编辑者')
      expect(createRequest.role_type).toBe('custom')
      expect(createRequest.permission_ids).toEqual(['perm-1', 'perm-2'])
    })

    it('should accept create request with minimal fields', () => {
      const minimalRequest: CreateRoleRequest = {
        name: 'viewer',
        display_name: '查看者',
        role_type: 'custom',
      }

      expect(minimalRequest.description).toBeUndefined()
      expect(minimalRequest.permission_ids).toBeUndefined()
    })
  })

  describe('UpdateRoleRequest interface', () => {
    it('should accept valid update role request', () => {
      const updateRequest: UpdateRoleRequest = {
        display_name: '高级编辑者',
        description: '高级内容编辑者角色',
        status: 'active',
      }

      expect(updateRequest.display_name).toBe('高级编辑者')
      expect(updateRequest.description).toBe('高级内容编辑者角色')
      expect(updateRequest.status).toBe('active')
    })

    it('should accept partial update request', () => {
      const partialRequest: UpdateRoleRequest = {
        status: 'inactive',
      }

      expect(partialRequest.status).toBe('inactive')
      expect(partialRequest.display_name).toBeUndefined()
    })
  })

  describe('RolePermissionAssignRequest interface', () => {
    it('should accept valid permission assign request', () => {
      const assignRequest: RolePermissionAssignRequest = {
        permission_ids: ['perm-1', 'perm-2', 'perm-3'],
      }

      expect(assignRequest.permission_ids).toEqual(['perm-1', 'perm-2', 'perm-3'])
      expect(assignRequest.permission_ids.length).toBe(3)
    })

    it('should accept empty permission list', () => {
      const emptyRequest: RolePermissionAssignRequest = {
        permission_ids: [],
      }

      expect(emptyRequest.permission_ids).toEqual([])
    })
  })

  describe('RoleQueryParams interface', () => {
    it('should accept valid query parameters', () => {
      const queryParams: RoleQueryParams = {
        search: 'admin',
        role_type: 'system',
        status: 'active',
        page: 1,
        page_size: 10,
        sort_by: 'created_at',
        sort_order: 'desc',
      }

      expect(queryParams.search).toBe('admin')
      expect(queryParams.role_type).toBe('system')
      expect(queryParams.status).toBe('active')
      expect(queryParams.page).toBe(1)
      expect(queryParams.page_size).toBe(10)
      expect(queryParams.sort_by).toBe('created_at')
      expect(queryParams.sort_order).toBe('desc')
    })

    it('should accept empty query parameters', () => {
      const emptyParams: RoleQueryParams = {}

      expect(Object.keys(emptyParams)).toHaveLength(0)
    })
  })

  describe('RoleStats interface', () => {
    it('should accept valid role statistics', () => {
      const stats: RoleStats = {
        total_roles: 10,
        system_roles: 3,
        custom_roles: 7,
        active_roles: 8,
        recent_roles: [],
      }

      expect(stats.total_roles).toBe(10)
      expect(stats.system_roles).toBe(3)
      expect(stats.custom_roles).toBe(7)
      expect(stats.active_roles).toBe(8)
      expect(Array.isArray(stats.recent_roles)).toBe(true)
    })
  })

  describe('Type compatibility', () => {
    it('should ensure role type and is_system_role consistency', () => {
      const systemRole: Role = {
        id: 'role-1',
        name: 'admin',
        display_name: '管理员',
        role_type: 'system',
        is_system_role: true,
        status: 'active',
        permissions: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      const customRole: Role = {
        id: 'role-2',
        name: 'editor',
        display_name: '编辑者',
        role_type: 'custom',
        is_system_role: false,
        status: 'active',
        permissions: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      expect(systemRole.role_type === 'system' && systemRole.is_system_role).toBe(true)
      expect(customRole.role_type === 'custom' && !customRole.is_system_role).toBe(true)
    })
  })
})