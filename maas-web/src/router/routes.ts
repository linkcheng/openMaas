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
  {
    path: 'dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: {
      requiresAuth: true,
      title: '仪表盘'
    }
  },
  {
    path: 'data-management',
    name: 'data-management',
    component: () => import('../views/maas/DataManagementView.vue'),
    meta: {
      requiresAuth: true,
      title: '数据管理'
    }
  },
  {
    path: 'model-management',
    name: 'model-management',
    component: () => import('../views/maas/ModelManagementView.vue'),
    meta: {
      requiresAuth: true,
      title: '模型管理'
    }
  },
  {
    path: 'model-finetune',
    name: 'model-finetune',
    component: () => import('../views/maas/ModelFineTuneView.vue'),
    meta: {
      requiresAuth: true,
      title: '模型微调'
    }
  },
  {
    path: 'model-deployment',
    name: 'model-deployment',
    component: () => import('../views/maas/ModelDeploymentView.vue'),
    meta: {
      requiresAuth: true,
      title: '模型部署'
    }
  },
  {
    path: 'model-inference',
    name: 'model-inference',
    component: () => import('../views/maas/ModelInferenceView.vue'),
    meta: {
      requiresAuth: true,
      title: '模型推理'
    }
  },
  {
    path: 'knowledge-base',
    name: 'knowledge-base',
    component: () => import('../views/maas/KnowledgeBaseView.vue'),
    meta: {
      requiresAuth: true,
      title: '知识库管理'
    }
  },
  {
    path: 'application-management',
    name: 'application-management',
    component: () => import('../views/maas/ApplicationManagementView.vue'),
    meta: {
      requiresAuth: true,
      title: '应用管理'
    }
  },
  {
    path: 'application-scenarios',
    name: 'application-scenarios',
    component: () => import('../views/maas/ApplicationScenariosView.vue'),
    meta: {
      requiresAuth: true,
      title: '应用场景'
    }
  },
]

// 用户管理路由
export const userRoutes: RouteRecordRaw[] = [
  {
    path: 'user/profile',
    name: 'profile',
    component: () => import('../views/user/ProfileView.vue'),
    meta: {
      requiresAuth: true,
      title: '个人资料'
    }
  },
  {
    path: 'user/settings',
    name: 'settings',
    component: () => import('../views/user/SettingsView.vue'),
    meta: {
      requiresAuth: true,
      title: '设置'
    }
  },
]

// 管理员路由
export const adminRoutes: RouteRecordRaw[] = [
  {
    path: 'admin/dashboard',
    name: 'admin',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: '管理后台'
    }
  },
  {
    path: 'admin/users',
    name: 'admin-users',
    component: () => import('../views/admin/UserManagement.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: '用户管理'
    }
  },
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
  {
    path: 'admin/audit-logs',
    name: 'admin-audit-logs',
    component: () => import('../views/admin/AuditLogsView.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: '系统日志'
    }
  },
]

// 权限管理路由
export const permissionRoutes: RouteRecordRaw[] = [
  {
    path: 'admin/permission',
    component: () => import('../views/admin/permission/PermissionLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', redirect: 'roles' },
      {
        path: 'roles',
        name: 'permission-roles',
        component: () => import('../views/admin/permission/RoleManagement.vue'),
        meta: {
          requiresAuth: true,
          requiresAdmin: true,
          title: '角色管理',
          permissions: 'system:roles:view'
        }
      },
      {
        path: 'permissions',
        name: 'permission-permissions',
        component: () => import('../views/admin/permission/PermissionManagement.vue'),
        meta: {
          requiresAuth: true,
          requiresAdmin: true,
          title: '权限管理',
          permissions: 'system:permissions:view'
        }
      },
      {
        path: 'user-roles',
        name: 'permission-user-roles',
        component: () => import('../views/admin/permission/UserRoleManagement.vue'),
        meta: {
          requiresAuth: true,
          requiresAdmin: true,
          title: '用户权限',
          permissions: 'system:users:manage'
        }
      },
    ]
  },
]

// 通用路由
export const commonRoutes: RouteRecordRaw[] = [
  {
    path: 'permission-denied',
    name: 'permission-denied',
    component: () => import('../views/common/PermissionDeniedView.vue'),
    meta: {
      requiresAuth: true,
      title: '权限不足'
    }
  },
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
