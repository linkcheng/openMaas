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

import { defineAsyncComponent, type AsyncComponentLoader, type Component } from 'vue'
import { performanceMonitor, getDevicePerformance } from './performance'

// 组件加载状态
interface ComponentLoadState {
  loading: boolean
  loaded: boolean
  error: Error | null
  component: Component | null
}

// 组件预加载器
class ComponentPreloader {
  private static instance: ComponentPreloader
  private loadStates = new Map<string, ComponentLoadState>()
  private preloadQueue: string[] = []
  private isPreloading = false

  static getInstance(): ComponentPreloader {
    if (!ComponentPreloader.instance) {
      ComponentPreloader.instance = new ComponentPreloader()
    }
    return ComponentPreloader.instance
  }

  // 创建懒加载组件
  createLazyComponent(
    loader: AsyncComponentLoader,
    name: string,
    options: {
      loadingComponent?: Component
      errorComponent?: Component
      delay?: number
      timeout?: number
      suspensible?: boolean
      preload?: boolean
    } = {},
  ) {
    const {
      loadingComponent,
      errorComponent,
      delay = 200,
      timeout = 30000,
      suspensible = false,
      preload = false,
    } = options

    // 如果需要预加载，添加到预加载队列
    if (preload) {
      this.addToPreloadQueue(name, loader)
    }

    return defineAsyncComponent({
      loader: () => {
        return performanceMonitor.measureAsync(`component-load:${name}`, async () => {
          this.setLoadState(name, { loading: true, loaded: false, error: null, component: null })

          try {
            const component = await loader()
            this.setLoadState(name, { loading: false, loaded: true, error: null, component })
            return component
          } catch (error) {
            const err = error as Error
            this.setLoadState(name, { loading: false, loaded: false, error: err, component: null })
            throw err
          }
        })
      },
      loadingComponent,
      errorComponent,
      delay,
      timeout,
      suspensible,
    })
  }

  // 预加载组件
  async preloadComponent(name: string, loader: AsyncComponentLoader): Promise<Component | null> {
    const existingState = this.loadStates.get(name)

    // 如果已经加载或正在加载，直接返回
    if (existingState?.loaded) {
      return existingState.component
    }

    if (existingState?.loading) {
      // 等待加载完成
      return new Promise((resolve) => {
        const checkLoaded = () => {
          const state = this.loadStates.get(name)
          if (state?.loaded) {
            resolve(state.component)
          } else if (state?.error) {
            resolve(null)
          } else {
            setTimeout(checkLoaded, 100)
          }
        }
        checkLoaded()
      })
    }

    try {
      this.setLoadState(name, { loading: true, loaded: false, error: null, component: null })

      const component = await performanceMonitor.measureAsync(`preload:${name}`, async () => {
        return await loader()
      })

      this.setLoadState(name, { loading: false, loaded: true, error: null, component })
      return component
    } catch (error) {
      const err = error as Error
      this.setLoadState(name, { loading: false, loaded: false, error: err, component: null })
      console.warn(`预加载组件 ${name} 失败:`, err)
      return null
    }
  }

  // 添加到预加载队列
  private addToPreloadQueue(name: string, _loader: AsyncComponentLoader) {
    if (!this.preloadQueue.includes(name)) {
      this.preloadQueue.push(name)

      // 存储loader以便后续使用
      if (!this.loadStates.has(name)) {
        this.setLoadState(name, { loading: false, loaded: false, error: null, component: null })
      }

      // 开始预加载处理
      this.processPreloadQueue()
    }
  }

  // 处理预加载队列
  private async processPreloadQueue() {
    if (this.isPreloading || this.preloadQueue.length === 0) {
      return
    }

    this.isPreloading = true
    const { performanceLevel } = getDevicePerformance()

    // 根据设备性能决定并发数
    const concurrency = performanceLevel === 'high' ? 3 : performanceLevel === 'medium' ? 2 : 1

    while (this.preloadQueue.length > 0) {
      const batch = this.preloadQueue.splice(0, concurrency)

      await Promise.allSettled(
        batch.map(async (name) => {
          // 这里需要获取对应的loader，实际实现中可能需要调整存储方式
          // 暂时跳过实际预加载，只是演示结构
          console.debug(`预加载组件: ${name}`)
        }),
      )

      // 在低性能设备上添加延迟，避免阻塞主线程
      if (performanceLevel === 'low') {
        await new Promise((resolve) => setTimeout(resolve, 100))
      }
    }

    this.isPreloading = false
  }

  // 设置加载状态
  private setLoadState(name: string, state: ComponentLoadState) {
    this.loadStates.set(name, state)
  }

  // 获取加载状态
  getLoadState(name: string): ComponentLoadState | null {
    return this.loadStates.get(name) || null
  }

  // 获取所有加载状态
  getAllLoadStates(): Record<string, ComponentLoadState> {
    const states: Record<string, ComponentLoadState> = {}
    for (const [name, state] of this.loadStates.entries()) {
      states[name] = state
    }
    return states
  }

  // 清除加载状态
  clearLoadState(name: string) {
    this.loadStates.delete(name)
  }

  // 清除所有加载状态
  clearAllLoadStates() {
    this.loadStates.clear()
  }
}

export const componentPreloader = ComponentPreloader.getInstance()

// 常用组件的懒加载创建函数
export function createProviderComponents() {
  return {
    // 供应商管理相关组件
    ProviderCard: componentPreloader.createLazyComponent(
      () => import('@/components/provider/ProviderCard.vue'),
      'ProviderCard',
      { preload: true },
    ),

    ProviderDialogForm: componentPreloader.createLazyComponent(
      () => import('@/components/provider/ProviderDialogForm.vue'),
      'ProviderDialogForm',
      { preload: false }, // 按需加载
    ),

    ProviderDetailDialog: componentPreloader.createLazyComponent(
      () => import('@/components/provider/ProviderDetailDialog.vue'),
      'ProviderDetailDialog',
      { preload: false },
    ),

    ConfirmDeleteDialog: componentPreloader.createLazyComponent(
      () => import('@/components/provider/ConfirmDeleteDialog.vue'),
      'ConfirmDeleteDialog',
      { preload: false },
    ),

    // UI组件
    VirtualScroll: componentPreloader.createLazyComponent(
      () => import('@/components/ui/VirtualScroll.vue'),
      'VirtualScroll',
      { preload: false },
    ),

    LazyImage: componentPreloader.createLazyComponent(
      () => import('@/components/ui/LazyImage.vue'),
      'LazyImage',
      { preload: true },
    ),
  }
}

// 预加载关键组件
export async function preloadCriticalComponents() {
  const { performanceLevel } = getDevicePerformance()

  // 只在高性能设备上预加载
  if (performanceLevel === 'high') {
    const components = ['ProviderCard', 'LazyImage']

    await Promise.allSettled(
      components.map((name) =>
        componentPreloader.preloadComponent(
          name,
          () => import(`@/components/provider/${name}.vue`),
        ),
      ),
    )
  }
}

// 路由级别的组件预加载
export function preloadRouteComponents(routeName: string) {
  const routeComponentMap: Record<string, string[]> = {
    'admin-providers': ['ProviderCard', 'SearchInput', 'SelectFilter', 'Pagination'],
    'provider-detail': ['ProviderDetailDialog', 'ProviderDialogForm'],
  }

  const components = routeComponentMap[routeName] || []
  components.forEach((componentName) => {
    // 添加到预加载队列
    componentPreloader.addToPreloadQueue(
      componentName,
      () => import(`@/components/ui/${componentName}.vue`),
    )
  })
}
