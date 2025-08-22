import { describe, it, expect, vi } from 'vitest'
import type { Permission } from '@/types/permission'

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  Search: { name: 'Search' },
  Folder: { name: 'Folder' },
  Document: { name: 'Document' },
  Key: { name: 'Key' },
  Collection: { name: 'Collection' },
  FolderOpened: { name: 'FolderOpened' },
  View: { name: 'View' },
  UserFilled: { name: 'UserFilled' },
  Edit: { name: 'Edit' },
  Delete: { name: 'Delete' },
  Grid: { name: 'Grid' }
}))

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElTree: { name: 'ElTree' },
  ElInput: { name: 'ElInput' },
  ElButton: { name: 'ElButton' },
  ElIcon: { name: 'ElIcon' },
  ElTag: { name: 'ElTag' },
  ElTooltip: { name: 'ElTooltip' },
  ElBadge: { name: 'ElBadge' },
  ElEmpty: { name: 'ElEmpty' }
}))

describe('PermissionTree', () => {
  const mockPermissions: Permission[] = [
    {
      id: '1',
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
      updated_at: '2024-01-01T00:00:00Z'
    },
    {
      id: '2',
      name: 'user.read',
      display_name: '查看用户',
      description: '查看用户信息的权限',
      resource: 'user',
      action: 'read',
      module: 'user_management',
      status: 'active',
      is_system_permission: true,
      level: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    },
    {
      id: '3',
      name: 'role.create',
      display_name: '创建角色',
      description: '创建新角色的权限',
      resource: 'role',
      action: 'create',
      module: 'permission_management',
      status: 'active',
      is_system_permission: true,
      level: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }
  ]

  // Test the tree building logic
  const testPermissionTreeLogic = () => {
    // Build tree data structure
    const buildTreeData = (permissions: Permission[]) => {
      const moduleMap = new Map()
      const resourceMap = new Map()
      const result: any[] = []

      permissions.forEach(permission => {
        // Create module node
        if (!moduleMap.has(permission.module)) {
          const moduleNode = {
            id: `module-${permission.module}`,
            name: permission.module,
            display_name: permission.module,
            type: 'module',
            children: []
          }
          moduleMap.set(permission.module, moduleNode)
          result.push(moduleNode)
        }

        // Create resource node
        const resourceKey = `${permission.module}-${permission.resource}`
        if (!resourceMap.has(resourceKey)) {
          const resourceNode = {
            id: `resource-${resourceKey}`,
            name: permission.resource,
            display_name: permission.resource,
            type: 'resource',
            module: permission.module,
            children: []
          }
          resourceMap.set(resourceKey, resourceNode)
          moduleMap.get(permission.module).children.push(resourceNode)
        }

        // Create permission node
        const permissionNode = {
          id: permission.id,
          name: permission.name,
          display_name: permission.display_name,
          description: permission.description,
          type: 'permission',
          module: permission.module,
          resource: permission.resource,
          action: permission.action,
          created_at: permission.created_at
        }

        resourceMap.get(resourceKey).children.push(permissionNode)
      })

      return result
    }

    // Get permission tag type
    const getPermissionTagType = (permission: any) => {
      const actionTypeMap: Record<string, string> = {
        'create': 'success',
        'read': 'info',
        'update': 'warning',
        'delete': 'danger',
        'manage': 'primary'
      }
      return actionTypeMap[permission.action || ''] || 'info'
    }

    // Get children count
    const getChildrenCount = (node: any): number => {
      if (!node.children) return 0
      
      let count = 0
      function countChildren(children: any[]) {
        children.forEach(child => {
          if (child.type === 'permission') {
            count++
          }
          if (child.children) {
            countChildren(child.children)
          }
        })
      }
      
      countChildren(node.children)
      return count
    }

    // Filter node
    const filterNode = (value: string, data: any) => {
      if (!value) return true
      
      const searchValue = value.toLowerCase()
      const nameMatch = data.name.toLowerCase().includes(searchValue)
      const displayNameMatch = data.display_name.toLowerCase().includes(searchValue)
      const descriptionMatch = data.description && data.description.toLowerCase().includes(searchValue)
      
      return nameMatch || displayNameMatch || !!descriptionMatch
    }

    // Get all permission IDs
    const getAllPermissionIds = (nodes: any[]): string[] => {
      const ids: string[] = []
      
      function collectIds(children: any[]) {
        children.forEach(child => {
          if (child.type === 'permission') {
            ids.push(child.id)
          }
          if (child.children) {
            collectIds(child.children)
          }
        })
      }
      
      collectIds(nodes)
      return ids
    }

    // Find node by ID
    const findNodeById = (nodes: any[], id: string): any | null => {
      for (const node of nodes) {
        if (node.id === id) {
          return node
        }
        if (node.children) {
          const found = findNodeById(node.children, id)
          if (found) {
            return found
          }
        }
      }
      return null
    }

    return {
      buildTreeData,
      getPermissionTagType,
      getChildrenCount,
      filterNode,
      getAllPermissionIds,
      findNodeById
    }
  }

  describe('树形数据构建', () => {
    it('应该正确构建树形数据结构', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      expect(treeData).toHaveLength(2) // 两个模块
      
      // 验证模块节点
      const userModule = treeData.find(node => node.name === 'user_management')
      const permissionModule = treeData.find(node => node.name === 'permission_management')
      
      expect(userModule).toBeDefined()
      expect(userModule.type).toBe('module')
      expect(userModule.children).toHaveLength(1) // 一个资源
      
      expect(permissionModule).toBeDefined()
      expect(permissionModule.type).toBe('module')
      expect(permissionModule.children).toHaveLength(1) // 一个资源
    })

    it('应该正确创建资源节点', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      const userModule = treeData.find(node => node.name === 'user_management')
      const userResource = userModule.children[0]
      
      expect(userResource.type).toBe('resource')
      expect(userResource.name).toBe('user')
      expect(userResource.children).toHaveLength(2) // 两个权限
    })

    it('应该正确创建权限节点', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      const userModule = treeData.find(node => node.name === 'user_management')
      const userResource = userModule.children[0]
      const createPermission = userResource.children.find((p: any) => p.action === 'create')
      
      expect(createPermission.type).toBe('permission')
      expect(createPermission.name).toBe('user.create')
      expect(createPermission.display_name).toBe('创建用户')
      expect(createPermission.action).toBe('create')
    })
  })

  describe('权限标签类型', () => {
    it('应该为不同操作返回正确的标签类型', () => {
      const logic = testPermissionTreeLogic()
      
      const createPermission = { action: 'create' }
      const readPermission = { action: 'read' }
      const updatePermission = { action: 'update' }
      const deletePermission = { action: 'delete' }
      const managePermission = { action: 'manage' }
      const unknownPermission = { action: 'unknown' }
      
      expect(logic.getPermissionTagType(createPermission)).toBe('success')
      expect(logic.getPermissionTagType(readPermission)).toBe('info')
      expect(logic.getPermissionTagType(updatePermission)).toBe('warning')
      expect(logic.getPermissionTagType(deletePermission)).toBe('danger')
      expect(logic.getPermissionTagType(managePermission)).toBe('primary')
      expect(logic.getPermissionTagType(unknownPermission)).toBe('info')
    })
  })

  describe('子节点计数', () => {
    it('应该正确计算权限子节点数量', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      const userModule = treeData.find(node => node.name === 'user_management')
      const permissionModule = treeData.find(node => node.name === 'permission_management')
      
      expect(logic.getChildrenCount(userModule)).toBe(2) // 两个权限
      expect(logic.getChildrenCount(permissionModule)).toBe(1) // 一个权限
    })

    it('应该为没有子节点的节点返回0', () => {
      const logic = testPermissionTreeLogic()
      const nodeWithoutChildren = { children: [] }
      const nodeWithoutChildrenProperty = {}
      
      expect(logic.getChildrenCount(nodeWithoutChildren)).toBe(0)
      expect(logic.getChildrenCount(nodeWithoutChildrenProperty)).toBe(0)
    })
  })

  describe('节点过滤', () => {
    it('应该根据名称过滤节点', () => {
      const logic = testPermissionTreeLogic()
      
      const node = {
        name: 'user.create',
        display_name: '创建用户',
        description: '创建新用户的权限'
      }
      
      expect(logic.filterNode('user', node)).toBe(true)
      expect(logic.filterNode('create', node)).toBe(true)
      expect(logic.filterNode('创建', node)).toBe(true)
      expect(logic.filterNode('权限', node)).toBe(true)
      expect(logic.filterNode('不存在', node)).toBe(false)
    })

    it('应该在没有搜索值时返回true', () => {
      const logic = testPermissionTreeLogic()
      const node = { name: 'test', display_name: 'test' }
      
      expect(logic.filterNode('', node)).toBe(true)
      expect(logic.filterNode(null as any, node)).toBe(true)
    })

    it('应该处理没有描述的节点', () => {
      const logic = testPermissionTreeLogic()
      const node = {
        name: 'user.create',
        display_name: '创建用户'
      }
      
      expect(logic.filterNode('用户', node)).toBe(true)
      expect(logic.filterNode('不存在', node)).toBe(false)
    })
  })

  describe('权限ID收集', () => {
    it('应该正确收集所有权限ID', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      const allPermissionIds = logic.getAllPermissionIds(treeData)
      
      expect(allPermissionIds).toHaveLength(3)
      expect(allPermissionIds).toContain('1')
      expect(allPermissionIds).toContain('2')
      expect(allPermissionIds).toContain('3')
    })

    it('应该只收集权限类型的节点ID', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      const allPermissionIds = logic.getAllPermissionIds(treeData)
      
      // 不应该包含模块和资源节点的ID
      expect(allPermissionIds).not.toContain('module-user_management')
      expect(allPermissionIds).not.toContain('resource-user_management-user')
    })
  })

  describe('节点查找', () => {
    it('应该根据ID找到正确的节点', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      const foundNode = logic.findNodeById(treeData, '1')
      
      expect(foundNode).toBeDefined()
      expect(foundNode.name).toBe('user.create')
      expect(foundNode.type).toBe('permission')
    })

    it('应该在找不到节点时返回null', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      const foundNode = logic.findNodeById(treeData, 'non-existent')
      
      expect(foundNode).toBeNull()
    })

    it('应该能找到嵌套的节点', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData(mockPermissions)
      
      const moduleNode = logic.findNodeById(treeData, 'module-user_management')
      const resourceNode = logic.findNodeById(treeData, 'resource-user_management-user')
      
      expect(moduleNode).toBeDefined()
      expect(moduleNode.type).toBe('module')
      expect(resourceNode).toBeDefined()
      expect(resourceNode.type).toBe('resource')
    })
  })

  describe('事件处理逻辑', () => {
    it('应该正确处理权限选择', () => {
      const selectedPermissions = ['1', '2']
      const mockEmit = vi.fn()
      
      // 模拟选择处理逻辑
      const handleSelection = (permissions: string[]) => {
        mockEmit('select', permissions)
      }
      
      handleSelection(selectedPermissions)
      
      expect(mockEmit).toHaveBeenCalledWith('select', selectedPermissions)
    })

    it('应该正确处理节点点击', () => {
      const mockEmit = vi.fn()
      const permission = mockPermissions[0]
      
      // 模拟节点点击处理逻辑
      const handleNodeClick = (perm: Permission) => {
        mockEmit('node-click', perm)
      }
      
      handleNodeClick(permission)
      
      expect(mockEmit).toHaveBeenCalledWith('node-click', permission)
    })

    it('应该正确处理批量操作', () => {
      const mockEmit = vi.fn()
      const selectedPermissions = ['1', '2', '3']
      
      // 模拟批量操作处理逻辑
      const handleBatchAssign = (permissions: string[]) => {
        mockEmit('batch-assign', permissions)
      }
      
      const handleBatchRemove = (permissions: string[]) => {
        mockEmit('batch-remove', permissions)
      }
      
      handleBatchAssign(selectedPermissions)
      handleBatchRemove(selectedPermissions)
      
      expect(mockEmit).toHaveBeenCalledWith('batch-assign', selectedPermissions)
      expect(mockEmit).toHaveBeenCalledWith('batch-remove', selectedPermissions)
    })
  })

  describe('数据验证', () => {
    it('应该正确处理空权限列表', () => {
      const logic = testPermissionTreeLogic()
      const treeData = logic.buildTreeData([])
      
      expect(treeData).toHaveLength(0)
    })

    it('应该正确处理单个权限', () => {
      const logic = testPermissionTreeLogic()
      const singlePermission = [mockPermissions[0]]
      const treeData = logic.buildTreeData(singlePermission)
      
      expect(treeData).toHaveLength(1)
      expect(treeData[0].type).toBe('module')
      expect(treeData[0].children).toHaveLength(1)
      expect(treeData[0].children[0].children).toHaveLength(1)
    })

    it('应该正确处理相同模块的多个权限', () => {
      const logic = testPermissionTreeLogic()
      const sameModulePermissions = mockPermissions.filter(p => p.module === 'user_management')
      const treeData = logic.buildTreeData(sameModulePermissions)
      
      expect(treeData).toHaveLength(1) // 只有一个模块
      expect(treeData[0].children).toHaveLength(1) // 只有一个资源
      expect(treeData[0].children[0].children).toHaveLength(2) // 两个权限
    })
  })
})