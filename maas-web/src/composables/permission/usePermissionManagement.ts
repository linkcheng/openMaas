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

import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuth } from '@/composables/useAuth'
import { apiClient, handleApiError } from '@/utils/api'
import type { Permission, CreatePermissionRequest, UpdatePermissionRequest } from '@/types/permission/permissionTypes'

export const usePermissionManagement = () => {
  const { hasPermission } = useAuth()

  // 状态
  const permissions = ref<Permission[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  const searchQuery = ref('')
  const selectedModule = ref('')

  // 权限检查
  const canView = computed(() => hasPermission('system:permissions:view'))
  const canCreate = computed(() => hasPermission('system:permissions:create'))
  const canEdit = computed(() => hasPermission('system:permissions:edit'))
  const canDelete = computed(() => hasPermission('system:permissions:delete'))

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  // 获取权限列表
  const fetchPermissions = async () => {
    isLoading.value = true
    error.value = null

    try {
      // 调用后端API获取权限列表
      const params: any = {
        page: currentPage.value,
        limit: pageSize.value
      }

      if (searchQuery.value) {
        params.name = searchQuery.value
      }

      if (selectedModule.value) {
        params.module = selectedModule.value
      }

      const response = await apiClient.get('/permissions', params)

      if ((response.data as any)?.success) {
        const data = response.data.data
        permissions.value = data.permissions || []
        total.value = data.total || 0

        return { success: true, data: permissions.value }
      } else {
        throw new Error((response.data as any)?.message || '获取权限列表失败')
      }
    } catch (err) {
      const errorMessage = handleApiError(err)
      error.value = errorMessage
      ElMessage.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // 创建权限
  const createPermission = async (data: CreatePermissionRequest) => {
    if (!canCreate.value) {
      error.value = '没有创建权限的权限'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    }

    isLoading.value = true
    error.value = null

    try {
      // 调用后端API创建权限
      const response = await apiClient.post('/permissions', data)

      if ((response.data as any)?.success) {
        const newPermission = response.data.data
        permissions.value.push(newPermission)
        total.value = permissions.value.length

        ElMessage.success('权限创建成功')
        return { success: true, data: newPermission }
      } else {
        throw new Error((response.data as any)?.message || '创建权限失败')
      }
    } catch (err) {
      const errorMessage = handleApiError(err)
      error.value = errorMessage
      ElMessage.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // 更新权限
  const updatePermission = async (id: string, data: UpdatePermissionRequest) => {
    if (!canEdit.value) {
      error.value = '没有编辑权限的权限'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    }

    isLoading.value = true
    error.value = null

    try {
      // 调用后端API更新权限
      const response = await apiClient.put(`/permissions/${id}`, data)

      if ((response.data as any)?.success) {
        const updatedPermission = response.data.data
        const permissionIndex = permissions.value.findIndex(permission => permission.id === id)

        if (permissionIndex !== -1) {
          permissions.value[permissionIndex] = updatedPermission
        }

        ElMessage.success('权限更新成功')
        return { success: true, data: updatedPermission }
      } else {
        throw new Error((response.data as any)?.message || '更新权限失败')
      }
    } catch (err) {
      error.value = '更新权限失败'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 删除权限
  const deletePermission = async (id: string) => {
    if (!canDelete.value) {
      error.value = '没有删除权限的权限'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    }

    isLoading.value = true
    error.value = null

    try {
      // 调用后端API删除权限
      const response = await apiClient.delete(`/permissions/${id}`)

      if ((response.data as any)?.success) {
        const permissionIndex = permissions.value.findIndex(permission => permission.id === id)
        if (permissionIndex !== -1) {
          permissions.value.splice(permissionIndex, 1)
          total.value = permissions.value.length
        }

        ElMessage.success('权限删除成功')
        return { success: true }
      } else {
        throw new Error((response.data as any)?.message || '删除权限失败')
      }
    } catch (err) {
      error.value = '删除权限失败'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 获取模块列表
  const getModules = computed(() => {
    const modules = new Set(permissions.value.map(p => p.module))
    return Array.from(modules).sort()
  })

  // 获取资源列表
  const getResources = computed(() => {
    const resources = new Set(permissions.value.map(p => p.resource))
    return Array.from(resources).sort()
  })

  // 获取动作列表
  const getActions = computed(() => {
    const actions = new Set(permissions.value.map(p => p.action))
    return Array.from(actions).sort()
  })

  // 搜索权限
  const searchPermissions = async () => {
    await fetchPermissions()
  }

  // 重置搜索
  const resetSearch = () => {
    searchQuery.value = ''
    selectedModule.value = ''
    currentPage.value = 1
    fetchPermissions()
  }

  // 分页改变
  const handlePageChange = (page: number) => {
    currentPage.value = page
    fetchPermissions()
  }

  // 页面大小改变
  const handlePageSizeChange = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchPermissions()
  }

  // 刷新列表
  const refreshPermissions = () => {
    fetchPermissions()
  }

  return {
    // 状态
    permissions,
    isLoading,
    error,
    currentPage,
    pageSize,
    total,
    searchQuery,
    selectedModule,

    // 权限
    canView,
    canCreate,
    canEdit,
    canDelete,

    // 计算属性
    getModules,
    getResources,
    getActions,

    // 方法
    clearError,
    fetchPermissions,
    createPermission,
    updatePermission,
    deletePermission,
    searchPermissions,
    resetSearch,
    handlePageChange,
    handlePageSizeChange,
    refreshPermissions
  }
}
