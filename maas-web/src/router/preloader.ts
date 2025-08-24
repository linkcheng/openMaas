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

import { memoryCache } from '@/utils/cache'

/**
 * 简化的路由组件预加载
 */
export class RoutePreloader {
  private static instance: RoutePreloader
  private preloadedRoutes = new Set<string>()

  static getInstance(): RoutePreloader {
    if (!RoutePreloader.instance) {
      RoutePreloader.instance = new RoutePreloader()
    }
    return RoutePreloader.instance
  }

  /**
   * 预加载路由组件
   * @param routeName 路由名称
   */
  async preloadRoute(routeName: string): Promise<void> {
    if (this.preloadedRoutes.has(routeName)) {
      return
    }

    try {
      // 使用缓存检查是否已预加载
      const cacheKey = `route_preload_${routeName}`
      if (memoryCache.has(cacheKey)) {
        return
      }

      // 根据路由名称预加载对应组件
      await this.getRoutePreloader(routeName)?.()

      this.preloadedRoutes.add(routeName)
      memoryCache.set(cacheKey, true, 10 * 60 * 1000) // 缓存10分钟
    } catch (error) {
      console.warn(`预加载路由 ${routeName} 失败:`, error)
    }
  }

  /**
   * 获取路由对应的预加载器
   * @param routeName 路由名称
   */
  private getRoutePreloader(routeName: string): (() => Promise<any>) | null {
    const preloaders: Record<string, () => Promise<any>> = {
      'admin-providers': () => import('@/views/admin/ProviderManagementPage.vue'),
      'dashboard': () => import('@/views/DashboardView.vue'),
      'profile': () => import('@/views/user/ProfileView.vue'),
      'settings': () => import('@/views/user/SettingsView.vue'),
      // 可根据需要扩展更多路由
    }

    return preloaders[routeName] || null
  }

  /**
   * 批量预加载关键路由
   */
  async preloadCriticalRoutes(): Promise<void> {
    const criticalRoutes = ['dashboard', 'profile']
    
    await Promise.allSettled(
      criticalRoutes.map(route => this.preloadRoute(route))
    )
  }

  /**
   * 检查路由是否已预加载
   */
  isRoutePreloaded(routeName: string): boolean {
    return this.preloadedRoutes.has(routeName)
  }

  /**
   * 清除预加载缓存
   */
  clearPreloadCache(): void {
    this.preloadedRoutes.clear()
  }
}

export const routePreloader = RoutePreloader.getInstance()

/**
 * 简化的路由组件预加载函数
 */
export function preloadRouteComponents(routeName: string): void {
  // 异步预加载，不阻塞导航
  routePreloader.preloadRoute(routeName).catch(err => {
    console.warn('Route preload failed:', err)
  })
}