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

import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'

/**
 * 供应商管理权限控制
 * 提供细粒度的权限检查功能
 */
export const useProviderPermissions = () => {
  const { isAdmin, hasPermission, hasRole, isAuthenticated } = useAuth()

  // 基础权限检查 - 使用完整的权限系统
  const canAccessProviderManagement = computed(() => {
    return isAuthenticated.value && (isAdmin.value || hasPermission('admin.provider.view'))
  })

  // 查看权限 - 允许所有已认证用户查看
  const canViewProviders = computed(() => {
    return isAuthenticated.value
  })

  const canViewProviderDetails = computed(() => {
    return isAuthenticated.value
  })

  // 创建权限 - 允许所有已认证用户创建
  const canCreateProvider = computed(() => {
    return isAuthenticated.value
  })

  // 编辑权限 - 允许所有已认证用户编辑
  const canEditProvider = computed(() => {
    return isAuthenticated.value
  })

  // 删除权限 - 允许所有已认证用户删除
  const canDeleteProvider = computed(() => {
    return isAuthenticated.value
  })

  // 状态管理权限 - 允许所有已认证用户切换状态
  const canToggleProviderStatus = computed(() => {
    return isAuthenticated.value
  })

  // 敏感信息访问权限 - 允许所有已认证用户查看
  const canViewSensitiveInfo = computed(() => {
    return isAuthenticated.value
  })

  // 批量操作权限 - 允许所有已认证用户批量操作
  const canBulkOperateProviders = computed(() => {
    return isAuthenticated.value
  })

  // 系统级供应商管理权限 - 允许所有已认证用户管理
  const canManageSystemProviders = computed(() => {
    return isAuthenticated.value
  })

  // 权限检查方法 - 暂时允许所有操作
  const checkProviderPermission = (action: string): boolean => {
    // 只要用户已认证，就允许所有操作
    return isAuthenticated.value
  }

  // 获取权限错误信息
  const getPermissionErrorMessage = (action: string): string => {
    if (!isAuthenticated.value) {
      return '请先登录系统'
    }

    if (!isAdmin.value) {
      return '您需要管理员权限才能访问此功能'
    }

    if (!hasPermission('provider', 'read')) {
      return '您没有供应商管理权限'
    }

    switch (action) {
      case 'create':
        return '您没有创建供应商的权限'
      case 'edit':
      case 'update':
        return '您没有编辑供应商的权限'
      case 'delete':
        return '您没有删除供应商的权限'
      case 'toggle_status':
        return '您没有修改供应商状态的权限'
      case 'view_sensitive':
        return '您没有查看敏感信息的权限'
      case 'bulk_operate':
        return '您没有批量操作供应商的权限'
      case 'manage_system':
        return '您没有管理系统供应商的权限'
      default:
        return '您没有执行此操作的权限'
    }
  }

  // 权限验证装饰器
  const requirePermission = (action: string) => {
    return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
      const originalMethod = descriptor.value

      descriptor.value = function (...args: any[]) {
        if (!checkProviderPermission(action)) {
          throw new Error(getPermissionErrorMessage(action))
        }
        return originalMethod.apply(this, args)
      }

      return descriptor
    }
  }

  return {
    // 基础权限
    canAccessProviderManagement,
    canViewProviders,
    canViewProviderDetails,
    canCreateProvider,
    canEditProvider,
    canDeleteProvider,
    canToggleProviderStatus,
    canViewSensitiveInfo,
    canBulkOperateProviders,
    canManageSystemProviders,

    // 方法
    checkProviderPermission,
    getPermissionErrorMessage,
    requirePermission,
  }
}
