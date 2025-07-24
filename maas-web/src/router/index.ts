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

import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import HomeView from '../views/HomeView.vue'
import MainLayout from '@/components/layout/MainLayout.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    // 认证相关路由
    {
      path: '/auth/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/auth/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/auth/forgot-password',
      name: 'forgot-password',
      component: () => import('../views/auth/ForgotPasswordView.vue'),
      meta: { requiresGuest: true },
    },

    // 主应用路由（使用 MainLayout 包装）
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        // 仪表盘
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
          meta: { requiresAuth: true, title: '仪表盘' },
        },

        // AI MaaS 平台功能
        {
          path: 'data-management',
          name: 'data-management',
          component: () => import('../views/maas/DataManagementView.vue'),
          meta: { requiresAuth: true, title: '数据管理' },
        },
        {
          path: 'model-management',
          name: 'model-management',
          component: () => import('../views/maas/ModelManagementView.vue'),
          meta: { requiresAuth: true, title: '模型管理' },
        },
        {
          path: 'model-finetune',
          name: 'model-finetune',
          component: () => import('../views/maas/ModelFineTuneView.vue'),
          meta: { requiresAuth: true, title: '模型微调' },
        },
        {
          path: 'model-deployment',
          name: 'model-deployment',
          component: () => import('../views/maas/ModelDeploymentView.vue'),
          meta: { requiresAuth: true, title: '模型部署' },
        },
        {
          path: 'model-inference',
          name: 'model-inference',
          component: () => import('../views/maas/ModelInferenceView.vue'),
          meta: { requiresAuth: true, title: '模型推理' },
        },
        {
          path: 'knowledge-base',
          name: 'knowledge-base',
          component: () => import('../views/maas/KnowledgeBaseView.vue'),
          meta: { requiresAuth: true, title: '知识库管理' },
        },
        {
          path: 'application-management',
          name: 'application-management',
          component: () => import('../views/maas/ApplicationManagementView.vue'),
          meta: { requiresAuth: true, title: '应用管理' },
        },
        {
          path: 'application-scenarios',
          name: 'application-scenarios',
          component: () => import('../views/maas/ApplicationScenariosView.vue'),
          meta: { requiresAuth: true, title: '应用场景' },
        },

        // 用户管理路由
        {
          path: 'user/profile',
          name: 'profile',
          component: () => import('../views/user/ProfileView.vue'),
          meta: { requiresAuth: true, title: '个人资料' },
        },
        {
          path: 'user/settings',
          name: 'settings',
          component: () => import('../views/user/SettingsView.vue'),
          meta: { requiresAuth: true, title: '设置' },
        },

        // 管理员路由
        {
          path: 'admin/dashboard',
          name: 'admin',
          component: () => import('../views/admin/AdminDashboard.vue'),
          meta: { requiresAuth: true, requiresAdmin: true, title: '管理后台' },
        },
        {
          path: 'admin/users',
          name: 'admin-users',
          component: () => import('../views/admin/UserManagement.vue'),
          meta: { requiresAuth: true, requiresAdmin: true, title: '用户管理' },
        },
        {
          path: 'admin/audit-logs',
          name: 'admin-audit-logs',
          component: () => import('../views/admin/AuditLogsView.vue'),
          meta: { requiresAuth: true, requiresAdmin: true, title: '系统日志' },
        },
      ],
    },
  ],
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, isAdmin, initializeAuth } = useAuth()

  // 初始化认证状态
  if (!isAuthenticated.value) {
    await initializeAuth()
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    next('/auth/login')
    return
  }

  // 检查是否需要游客状态（未登录）
  if (to.meta.requiresGuest && isAuthenticated.value) {
    next('/')
    return
  }

  // 检查是否需要管理员权限 (暂时注释掉权限检查)
  // if (to.meta.requiresAdmin && !isAdmin.value) {
  //   next('/')
  //   return
  // }

  next()
})

export default router
