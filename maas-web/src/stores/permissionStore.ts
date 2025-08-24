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

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { adminApi } from '@/api'
import { handleApiError } from '@/utils/apiClient'
import { createListState } from './baseStore'

// 简化的权限类型定义
interface Permission {
  id: string
  name: string
  description: string
  module: string
  resource: string
  action: string
  is_active: boolean
  created_at: string
  updated_at: string
}

interface Role {
  id: string
  name: string
  description: string
  permissions: Permission[]
  is_system: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

interface MenuConfig {
  id: string
  name: string
  path: string
  icon?: string
  parent_id?: string
  required_permissions: string[]
  is_active: boolean
  sort_order: number
}

/**
 * 统一的权限管理 Store
 * 合并了原来分离的 permissionStore、roleStore、menuConfigStore
 */
export const usePermissionStore = defineStore('permission', () => {
  // 权限管理状态
  const {
    items: permissions,
    loading: permissionsLoading,
    error: permissionsError,
    pagination: permissionsPagination,
    setItems: setPermissions,
    setLoading: setPermissionsLoading,
    setError: setPermissionsError,
    clearError: clearPermissionsError,
    setPagination: setPermissionsPagination,
  } = createListState<Permission>()

  // 角色管理状态
  const {
    items: roles,
    loading: rolesLoading,
    error: rolesError,
    pagination: rolesPagination,
    setItems: setRoles,
    setLoading: setRolesLoading,
    setError: setRolesError,
    clearError: clearRolesError,
    setPagination: setRolesPagination,
    updateItem: updateRole,
    removeItem: removeRole,
    addItem: addRole,
  } = createListState<Role>()

  // 菜单配置状态
  const {
    items: menuConfigs,
    loading: menuLoading,
    error: menuError,
    setItems: setMenuConfigs,
    setLoading: setMenuLoading,
    setError: setMenuError,
    clearError: clearMenuError,
    updateItem: updateMenuConfig,
    removeItem: removeMenuConfig,
    addItem: addMenuConfig,
  } = createListState<MenuConfig>()

  // 计算属性
  const activeRoles = computed(() => roles.value.filter((role) => role.is_active))
  const systemRoles = computed(() => roles.value.filter((role) => role.is_system))
  const customRoles = computed(() => roles.value.filter((role) => !role.is_system))

  const activeMenus = computed(() => menuConfigs.value.filter((menu) => menu.is_active))
  const menuTree = computed(() => {
    const rootMenus = menuConfigs.value.filter((menu) => !menu.parent_id)
    const buildTree = (parentId?: string): MenuConfig[] => {
      return menuConfigs.value
        .filter((menu) => menu.parent_id === parentId)
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((menu) => ({
          ...menu,
          children: buildTree(menu.id),
        }))
    }
    return buildTree()
  })

  const permissionsByModule = computed(() => {
    const grouped: Record<string, Permission[]> = {}
    permissions.value.forEach((permission) => {
      if (!grouped[permission.module]) {
        grouped[permission.module] = []
      }
      grouped[permission.module].push(permission)
    })
    return grouped
  })

  // 权限相关方法
  const fetchPermissions = async (params: any = {}) => {
    try {
      setPermissionsLoading(true)
      clearPermissionsError()

      // 这里应该调用实际的权限 API
      // const response = await adminApi.permissions.list(params)
      // 模拟调用
      const response = { data: { success: true, data: { items: [], page: 1, size: 20, total: 0 } } }

      if (response.data.success && response.data.data) {
        setPermissions(response.data.data.items)
        setPermissionsPagination(
          response.data.data.page,
          response.data.data.size,
          response.data.data.total
        )
      }
    } catch (err) {
      setPermissionsError(handleApiError(err))
      throw err
    } finally {
      setPermissionsLoading(false)
    }
  }

  // 角色相关方法
  const fetchRoles = async (params: any = {}) => {
    try {
      setRolesLoading(true)
      clearRolesError()

      // 这里应该调用实际的角色 API
      // const response = await adminApi.roles.list(params)
      // 模拟调用
      const response = { data: { success: true, data: { items: [], page: 1, size: 20, total: 0 } } }

      if (response.data.success && response.data.data) {
        setRoles(response.data.data.items)
        setRolesPagination(response.data.data.page, response.data.data.size, response.data.data.total)
      }
    } catch (err) {
      setRolesError(handleApiError(err))
      throw err
    } finally {
      setRolesLoading(false)
    }
  }

  const createRole = async (roleData: Omit<Role, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      setRolesLoading(true)
      clearRolesError()

      // const response = await adminApi.roles.create(roleData)
      // 模拟创建
      const newRole: Role = {
        ...roleData,
        id: Date.now().toString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      addRole(newRole)
      return newRole
    } catch (err) {
      setRolesError(handleApiError(err))
      throw err
    } finally {
      setRolesLoading(false)
    }
  }

  const updateRoleData = async (roleId: string, roleData: Partial<Role>) => {
    try {
      setRolesLoading(true)
      clearRolesError()

      // const response = await adminApi.roles.update(roleId, roleData)
      // 模拟更新
      updateRole((role) => role.id === roleId, { ...roleData, updated_at: new Date().toISOString() })
    } catch (err) {
      setRolesError(handleApiError(err))
      throw err
    } finally {
      setRolesLoading(false)
    }
  }

  const deleteRole = async (roleId: string) => {
    try {
      setRolesLoading(true)
      clearRolesError()

      // const response = await adminApi.roles.delete(roleId)
      // 模拟删除
      removeRole((role) => role.id === roleId)
    } catch (err) {
      setRolesError(handleApiError(err))
      throw err
    } finally {
      setRolesLoading(false)
    }
  }

  // 菜单配置相关方法
  const fetchMenuConfigs = async () => {
    try {
      setMenuLoading(true)
      clearMenuError()

      // const response = await adminApi.menus.list()
      // 模拟调用
      const response = { data: { success: true, data: [] } }

      if (response.data.success) {
        setMenuConfigs(response.data.data)
      }
    } catch (err) {
      setMenuError(handleApiError(err))
      throw err
    } finally {
      setMenuLoading(false)
    }
  }

  const createMenuConfig = async (menuData: Omit<MenuConfig, 'id'>) => {
    try {
      setMenuLoading(true)
      clearMenuError()

      // const response = await adminApi.menus.create(menuData)
      // 模拟创建
      const newMenu: MenuConfig = {
        ...menuData,
        id: Date.now().toString(),
      }

      addMenuConfig(newMenu)
      return newMenu
    } catch (err) {
      setMenuError(handleApiError(err))
      throw err
    } finally {
      setMenuLoading(false)
    }
  }

  const updateMenuConfigData = async (menuId: string, menuData: Partial<MenuConfig>) => {
    try {
      setMenuLoading(true)
      clearMenuError()

      // const response = await adminApi.menus.update(menuId, menuData)
      // 模拟更新
      updateMenuConfig((menu) => menu.id === menuId, menuData)
    } catch (err) {
      setMenuError(handleApiError(err))
      throw err
    } finally {
      setMenuLoading(false)
    }
  }

  const deleteMenuConfig = async (menuId: string) => {
    try {
      setMenuLoading(true)
      clearMenuError()

      // const response = await adminApi.menus.delete(menuId)
      // 模拟删除
      removeMenuConfig((menu) => menu.id === menuId)
    } catch (err) {
      setMenuError(handleApiError(err))
      throw err
    } finally {
      setMenuLoading(false)
    }
  }

  // 权限检查方法
  const checkUserPermission = (userPermissions: string[], requiredPermission: string): boolean => {
    const parts = requiredPermission.split('.')
    if (parts.length !== 3) {
      return false
    }

    const [module, resource, action] = parts

    return userPermissions.some(permission => 
      permission === requiredPermission ||                    // 精确匹配
      permission === `${module}.${resource}.*` ||             // 资源通配符
      permission === `${module}.*.*` ||                       // 模块通配符
      permission === '*.*.*'                                  // 全局通配符
    )
  }

  return {
    // 权限状态
    permissions,
    permissionsLoading,
    permissionsError,
    permissionsPagination,
    permissionsByModule,

    // 角色状态
    roles,
    rolesLoading,
    rolesError,
    rolesPagination,
    activeRoles,
    systemRoles,
    customRoles,

    // 菜单状态
    menuConfigs,
    menuLoading,
    menuError,
    activeMenus,
    menuTree,

    // 权限方法
    fetchPermissions,

    // 角色方法
    fetchRoles,
    createRole,
    updateRoleData,
    deleteRole,

    // 菜单方法
    fetchMenuConfigs,
    createMenuConfig,
    updateMenuConfigData,
    deleteMenuConfig,

    // 工具方法
    checkUserPermission,
  }
})