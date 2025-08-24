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

import type { RouteRecordRaw } from 'vue-router'

/**
 * 创建认证路由的辅助函数
 */
const createAuthRoute = (path: string, name: string, component: string, title: string): RouteRecordRaw => ({
  path: `/auth/${path}`,
  name,
  component: () => import(`../views/auth/${component}.vue`),
  meta: { requiresGuest: true, title }
})

/**
 * 创建需要认证的路由的辅助函数
 */
const createProtectedRoute = (
  path: string, 
  name: string, 
  component: string, 
  title: string,
  permissions?: string
): RouteRecordRaw => ({
  path,
  name,
  component: () => import(`../views/${component}.vue`),
  meta: { 
    requiresAuth: true, 
    title,
    ...(permissions && { permissions })
  }
})

/**
 * 创建管理员路由的辅助函数
 */
const createAdminRoute = (
  path: string, 
  name: string, 
  component: string, 
  title: string,
  permissions?: string
): RouteRecordRaw => ({
  path: `admin/${path}`,
  name,
  component: () => import(`../views/admin/${component}.vue`),
  meta: { 
    requiresAuth: true, 
    requiresAdmin: true, 
    title,
    ...(permissions && { permissions })
  }
})

// 基础路由
export const basicRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
  },
]

// 认证相关路由
export const authRoutes: RouteRecordRaw[] = [
  createAuthRoute('login', 'login', 'LoginView', '用户登录'),
  createAuthRoute('register', 'register', 'RegisterView', '用户注册'),
  createAuthRoute('forgot-password', 'forgot-password', 'ForgotPasswordView', '找回密码'),
]

// MaaS 平台功能路由
export const maasRoutes: RouteRecordRaw[] = [
  createProtectedRoute('dashboard', 'dashboard', 'DashboardView', '仪表盘'),
  createProtectedRoute('data-management', 'data-management', 'maas/DataManagementView', '数据管理'),
  createProtectedRoute('model-management', 'model-management', 'maas/ModelManagementView', '模型管理'),
  createProtectedRoute('model-finetune', 'model-finetune', 'maas/ModelFineTuneView', '模型微调'),
  createProtectedRoute('model-deployment', 'model-deployment', 'maas/ModelDeploymentView', '模型部署'),
  createProtectedRoute('model-inference', 'model-inference', 'maas/ModelInferenceView', '模型推理'),
  createProtectedRoute('knowledge-base', 'knowledge-base', 'maas/KnowledgeBaseView', '知识库管理'),
  createProtectedRoute('application-management', 'application-management', 'maas/ApplicationManagementView', '应用管理'),
  createProtectedRoute('application-scenarios', 'application-scenarios', 'maas/ApplicationScenariosView', '应用场景'),
]

// 用户管理路由
export const userRoutes: RouteRecordRaw[] = [
  createProtectedRoute('user/profile', 'profile', 'user/ProfileView', '个人资料'),
  createProtectedRoute('user/settings', 'settings', 'user/SettingsView', '设置'),
]

// 管理员路由
export const adminRoutes: RouteRecordRaw[] = [
  createAdminRoute('dashboard', 'admin', 'AdminDashboard', '管理后台'),
  createAdminRoute('users', 'admin-users', 'UserManagement', '用户管理'),
  {
    path: 'admin/providers',
    name: 'admin-providers',
    component: () => import('../views/admin/ProviderManagementPage.vue'),
    meta: {
      requiresAuth: true,
      title: '供应商管理',
      breadcrumb: [
        { name: '管理后台', path: '/admin/dashboard' },
        { name: '供应商管理', path: '/admin/providers' },
      ],
    },
  },
  createAdminRoute('audit-logs', 'admin-audit-logs', 'AuditLogsView', '系统日志'),
]

// 权限管理路由
export const permissionRoutes: RouteRecordRaw[] = [
  {
    path: 'admin/permission',
    component: () => import('../views/admin/permission/PermissionLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', redirect: 'roles' },
      createProtectedRoute('roles', 'permission-roles', 'admin/permission/RoleManagement', '角色管理', 'admin.role.view'),
      createProtectedRoute('permissions', 'permission-permissions', 'admin/permission/PermissionManagement', '权限管理', 'admin.permission.view'),
      createProtectedRoute('user-roles', 'permission-user-roles', 'admin/permission/UserRoleManagement', '用户权限', 'admin.user.manage'),
    ].map(route => ({
      ...route,
      meta: {
        ...route.meta,
        requiresAdmin: true
      }
    }))
  },
]

// 通用路由
export const commonRoutes: RouteRecordRaw[] = [
  createProtectedRoute('permission-denied', 'permission-denied', 'common/PermissionDeniedView', '权限不足'),
]

// 主应用路由（使用 MainLayout 包装）
export const mainRoutes: RouteRecordRaw = {
  path: '/',
  component: () => import('@/components/layout/MainLayout.vue'),
  meta: { requiresAuth: true },
  children: [
    ...maasRoutes,
    ...userRoutes,
    ...adminRoutes,
    ...permissionRoutes,
    ...commonRoutes,
  ],
}

// 所有路由
export const routes: RouteRecordRaw[] = [
  ...basicRoutes,
  ...authRoutes,
  mainRoutes,
]