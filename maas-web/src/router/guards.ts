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

import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

/**
 * 认证检查守卫
 */
export async function authGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
): Promise<void> {
  const { isAuthenticated, initializeAuth } = useAuth()

  // 初始化认证状态（如果需要）
  if (!isAuthenticated.value) {
    await initializeAuth()
  }

  // 需要认证但未认证
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    next('/auth/login')
    return
  }

  // 需要访客状态但已认证
  if (to.meta.requiresGuest && isAuthenticated.value) {
    next('/')
    return
  }

  next()
}

/**
 * 权限检查守卫
 */
export function permissionGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const { isAuthenticated, isAdmin, hasPermission, currentUser } = useAuth()

  // 只对已认证用户进行权限检查
  if (!isAuthenticated.value) {
    next()
    return
  }

  // 如果已认证但缺少用户信息，需要重新初始化
  if (!currentUser.value) {
    next()
    return
  }

  // 管理员权限检查
  if (to.meta.requiresAdmin && !isAdmin.value) {
    next({
      name: 'permission-denied',
      query: {
        reason: 'admin_required',
        from: to.path,
      },
    })
    return
  }

  // 具体权限检查
  if (to.meta.permissions) {
    const permission = to.meta.permissions as string
    if (!hasPermission(permission)) {
      next({
        name: 'permission-denied',
        query: {
          reason: 'insufficient_permissions',
          permission,
          from: to.path,
        },
      })
      return
    }
  }

  next()
}

/**
 * 组合所有守卫
 */
export async function routeGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): Promise<void> {
  try {
    // 1. 认证检查
    let authCheckPassed = false
    await authGuard(to, from, (result?: any) => {
      if (result) {
        next(result)
      } else {
        authCheckPassed = true
      }
    })
    
    // 2. 权限检查（仅在认证检查通过后执行）
    if (authCheckPassed) {
      permissionGuard(to, from, next)
    }
  } catch (error) {
    console.error('路由守卫错误:', error)
    next('/auth/login')
  }
}