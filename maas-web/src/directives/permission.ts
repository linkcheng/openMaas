/**
 * 权限验证指令
 * Permission validation directive
 */

import type { Directive, DirectiveBinding } from 'vue'
import { useAuth } from '@/composables/useAuth'

export interface PermissionDirectiveValue {
  resource: string
  action: string
  logic?: 'AND' | 'OR'
  permissions?: string[]
}

/**
 * 权限验证指令
 * 用法:
 * v-permission="{ resource: 'user', action: 'create' }"
 * v-permission="{ permissions: ['user.create', 'user.update'], logic: 'OR' }"
 * v-permission="'user.create'"
 */
export const permission: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | PermissionDirectiveValue>) {
    updateElementVisibility(el, binding)
  },
  
  updated(el: HTMLElement, binding: DirectiveBinding<string | PermissionDirectiveValue>) {
    updateElementVisibility(el, binding)
  }
}

/**
 * 更新元素可见性
 */
function updateElementVisibility(
  el: HTMLElement, 
  binding: DirectiveBinding<string | PermissionDirectiveValue>
) {
  const { hasPermission, hasAnyPermission, hasAllPermissions } = useAuth()
  let hasRequiredPermission = false

  if (typeof binding.value === 'string') {
    // 简单权限字符串检查
    hasRequiredPermission = hasPermission(binding.value)
  } else if (binding.value && typeof binding.value === 'object') {
    const { resource, action, logic = 'AND', permissions } = binding.value

    if (permissions && Array.isArray(permissions)) {
      // 多权限检查
      if (logic === 'OR') {
        hasRequiredPermission = hasAnyPermission(permissions)
      } else {
        hasRequiredPermission = hasAllPermissions(permissions)
      }
    } else if (resource && action) {
      // 资源-操作权限检查
      hasRequiredPermission = hasPermission(`${resource}.${action}`)
    }
  }

  // 控制元素显示/隐藏
  if (hasRequiredPermission) {
    el.style.display = ''
    el.removeAttribute('aria-hidden')
  } else {
    el.style.display = 'none'
    el.setAttribute('aria-hidden', 'true')
  }
}

/**
 * 角色验证指令
 * 用法:
 * v-role="'admin'"
 * v-role="['admin', 'moderator']"
 */
export const role: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    updateElementVisibilityByRole(el, binding)
  },
  
  updated(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    updateElementVisibilityByRole(el, binding)
  }
}

/**
 * 根据角色更新元素可见性
 */
function updateElementVisibilityByRole(
  el: HTMLElement, 
  binding: DirectiveBinding<string | string[]>
) {
  const { hasRole, hasAnyRole } = useAuth()
  let hasRequiredRole = false

  if (typeof binding.value === 'string') {
    // 单角色检查
    hasRequiredRole = hasRole(binding.value)
  } else if (Array.isArray(binding.value)) {
    // 多角色检查（任一匹配即可）
    hasRequiredRole = hasAnyRole(binding.value)
  }

  // 控制元素显示/隐藏
  if (hasRequiredRole) {
    el.style.display = ''
    el.removeAttribute('aria-hidden')
  } else {
    el.style.display = 'none'
    el.setAttribute('aria-hidden', 'true')
  }
}

/**
 * 管理员权限指令
 * 用法:
 * v-admin
 */
export const admin: Directive = {
  mounted(el: HTMLElement) {
    updateElementVisibilityByAdmin(el)
  },
  
  updated(el: HTMLElement) {
    updateElementVisibilityByAdmin(el)
  }
}

/**
 * 根据管理员权限更新元素可见性
 */
function updateElementVisibilityByAdmin(el: HTMLElement) {
  const { isAdmin } = useAuth()

  // 控制元素显示/隐藏
  if (isAdmin.value) {
    el.style.display = ''
    el.removeAttribute('aria-hidden')
  } else {
    el.style.display = 'none'
    el.setAttribute('aria-hidden', 'true')
  }
}

/**
 * 认证状态指令
 * 用法:
 * v-auth - 需要登录
 * v-guest - 需要未登录
 */
export const auth: Directive = {
  mounted(el: HTMLElement) {
    updateElementVisibilityByAuth(el, true)
  },
  
  updated(el: HTMLElement) {
    updateElementVisibilityByAuth(el, true)
  }
}

export const guest: Directive = {
  mounted(el: HTMLElement) {
    updateElementVisibilityByAuth(el, false)
  },
  
  updated(el: HTMLElement) {
    updateElementVisibilityByAuth(el, false)
  }
}

/**
 * 根据认证状态更新元素可见性
 */
function updateElementVisibilityByAuth(el: HTMLElement, requireAuth: boolean) {
  const { isAuthenticated } = useAuth()
  const shouldShow = requireAuth ? isAuthenticated.value : !isAuthenticated.value

  // 控制元素显示/隐藏
  if (shouldShow) {
    el.style.display = ''
    el.removeAttribute('aria-hidden')
  } else {
    el.style.display = 'none'
    el.setAttribute('aria-hidden', 'true')
  }
}

/**
 * 权限指令集合
 */
export default {
  permission,
  role,
  admin,
  auth,
  guest,
}