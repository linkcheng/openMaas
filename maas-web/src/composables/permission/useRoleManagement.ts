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
import type { Role, CreateRoleRequest, UpdateRoleRequest } from '@/types/permission/roleTypes'
import type { PaginatedApiResponse } from '@/types/api'

export const useRoleManagement = () => {
  const { hasPermission } = useAuth()

  // 状态
  const roles = ref<Role[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  const searchQuery = ref('')

  // 权限检查
  const canView = computed(() => hasPermission('admin.role.view'))
  const canCreate = computed(() => hasPermission('admin.role.create'))
  const canEdit = computed(() => hasPermission('admin.role.edit'))
  const canDelete = computed(() => hasPermission('admin.role.delete'))

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  // 获取角色列表
  const fetchRoles = async () => {
    isLoading.value = true
    error.value = null

    try {
      // 调用后端API获取角色列表
      const params: any = {
        page: currentPage.value,
        limit: pageSize.value
      }
      
      if (searchQuery.value) {
        params.name = searchQuery.value
      }
      
      const response = await apiClient.get('/roles', params)
      
      if ((response.data as any)?.success) {
        const data = response.data.data
        roles.value = data.roles || []
        total.value = data.total || 0
        
        return { success: true, data: roles.value }
      } else {
        throw new Error((response.data as any)?.message || '获取角色列表失败')
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

  // 创建角色
  const createRole = async (data: CreateRoleRequest) => {
    if (!canCreate.value) {
      error.value = '没有创建角色的权限'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    }

    isLoading.value = true
    error.value = null

    try {
      // 调用后端API创建角色
      const response = await apiClient.post('/roles', data)
      
      if ((response.data as any)?.success) {
        const newRole = response.data.data
        roles.value.push(newRole)
        total.value = roles.value.length
        
        ElMessage.success('角色创建成功')
        return { success: true, data: newRole }
      } else {
        throw new Error((response.data as any)?.message || '创建角色失败')
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

  // 更新角色
  const updateRole = async (id: string, data: UpdateRoleRequest) => {
    if (!canEdit.value) {
      error.value = '没有编辑角色的权限'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    }

    isLoading.value = true
    error.value = null

    try {
      // 调用后端API更新角色
      const response = await apiClient.put(`/roles/${id}`, data)
      
      if ((response.data as any)?.success) {
        const updatedRole = response.data.data
        const roleIndex = roles.value.findIndex(role => role.id === id)
        
        if (roleIndex !== -1) {
          roles.value[roleIndex] = updatedRole
        }
        
        ElMessage.success('角色更新成功')
        return { success: true, data: updatedRole }
      } else {
        throw new Error((response.data as any)?.message || '更新角色失败')
      }
    } catch (err) {
      error.value = '更新角色失败'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 删除角色
  const deleteRole = async (id: string) => {
    if (!canDelete.value) {
      error.value = '没有删除角色的权限'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    }

    isLoading.value = true
    error.value = null

    try {
      // 调用后端API删除角色
      const response = await apiClient.delete(`/roles/${id}`)
      
      if ((response.data as any)?.success) {
        const roleIndex = roles.value.findIndex(role => role.id === id)
        if (roleIndex !== -1) {
          roles.value.splice(roleIndex, 1)
          total.value = roles.value.length
        }
        
        ElMessage.success('角色删除成功')
        return { success: true }
      } else {
        throw new Error((response.data as any)?.message || '删除角色失败')
      }
    } catch (err) {
      error.value = '删除角色失败'
      ElMessage.error(error.value)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 搜索角色
  const searchRoles = async () => {
    await fetchRoles()
  }

  // 重置搜索
  const resetSearch = () => {
    searchQuery.value = ''
    currentPage.value = 1
    fetchRoles()
  }

  // 分页改变
  const handlePageChange = (page: number) => {
    currentPage.value = page
    fetchRoles()
  }

  // 页面大小改变
  const handlePageSizeChange = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchRoles()
  }

  // 刷新列表
  const refreshRoles = () => {
    fetchRoles()
  }

  return {
    // 状态
    roles,
    isLoading,
    error,
    currentPage,
    pageSize,
    total,
    searchQuery,

    // 权限
    canView,
    canCreate,
    canEdit,
    canDelete,

    // 方法
    clearError,
    fetchRoles,
    createRole,
    updateRole,
    deleteRole,
    searchRoles,
    resetSearch,
    handlePageChange,
    handlePageSizeChange,
    refreshRoles
  }
}