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

import { ref, onMounted, onUnmounted, type Ref } from 'vue'

/**
 * 防抖函数
 * @param fn 要防抖的函数
 * @param delay 延迟时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

/**
 * 节流函数
 * @param fn 要节流的函数
 * @param delay 延迟时间（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let lastCall = 0

  return (...args: Parameters<T>) => {
    const now = Date.now()
    if (now - lastCall >= delay) {
      lastCall = now
      fn(...args)
    }
  }
}

/**
 * 图片懒加载 Composable
 * @param threshold 触发加载的阈值
 * @returns 懒加载相关的响应式数据和方法
 */
export function useLazyImage(threshold = 0.1) {
  const isLoaded = ref(false)
  const isError = ref(false)
  const imageRef = ref<HTMLImageElement>()

  let observer: IntersectionObserver | null = null

  const loadImage = (src: string) => {
    if (!imageRef.value) return

    const img = new Image()
    img.onload = () => {
      if (imageRef.value) {
        imageRef.value.src = src
        isLoaded.value = true
      }
    }
    img.onerror = () => {
      isError.value = true
    }
    img.src = src
  }

  const observe = (src: string) => {
    if (!imageRef.value || !('IntersectionObserver' in window)) {
      loadImage(src)
      return
    }

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage(src)
            observer?.unobserve(entry.target)
          }
        })
      },
      { threshold },
    )

    observer.observe(imageRef.value)
  }

  onUnmounted(() => {
    if (observer) {
      observer.disconnect()
    }
  })

  return {
    imageRef,
    isLoaded,
    isError,
    observe,
  }
}

/**
 * 虚拟滚动 Composable
 * @param items 数据项数组
 * @param itemHeight 每项的高度
 * @param containerHeight 容器高度
 * @param buffer 缓冲区大小
 * @returns 虚拟滚动相关的响应式数据和方法
 */
export function useVirtualScroll<T>(
  items: Ref<T[]>,
  itemHeight: number,
  containerHeight: number,
  buffer = 5,
) {
  const scrollTop = ref(0)
  const containerRef = ref<HTMLElement>()

  const visibleCount = Math.ceil(containerHeight / itemHeight)
  const totalHeight = ref(0)

  const startIndex = ref(0)
  const endIndex = ref(0)
  const visibleItems = ref<T[]>([])

  const updateVisibleItems = () => {
    const itemCount = items.value.length
    totalHeight.value = itemCount * itemHeight

    const start = Math.floor(scrollTop.value / itemHeight)
    const end = Math.min(start + visibleCount + buffer, itemCount)

    startIndex.value = Math.max(0, start - buffer)
    endIndex.value = end

    visibleItems.value = items.value.slice(startIndex.value, endIndex.value)
  }

  const handleScroll = throttle((event: Event) => {
    const target = event.target as HTMLElement
    scrollTop.value = target.scrollTop
    updateVisibleItems()
  }, 16) // 60fps

  const scrollToIndex = (index: number) => {
    if (containerRef.value) {
      const targetScrollTop = index * itemHeight
      containerRef.value.scrollTop = targetScrollTop
      scrollTop.value = targetScrollTop
      updateVisibleItems()
    }
  }

  const getItemStyle = (index: number) => ({
    position: 'absolute' as const,
    top: `${(startIndex.value + index) * itemHeight}px`,
    height: `${itemHeight}px`,
    width: '100%',
  })

  onMounted(() => {
    updateVisibleItems()
  })

  return {
    containerRef,
    visibleItems,
    totalHeight,
    startIndex,
    endIndex,
    handleScroll,
    scrollToIndex,
    getItemStyle,
    updateVisibleItems,
  }
}

/**
 * API 响应缓存
 */
class ApiCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>()

  set(key: string, data: any, ttl = 5 * 60 * 1000) {
    // 默认5分钟
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    })
  }

  get(key: string) {
    const item = this.cache.get(key)
    if (!item) return null

    const now = Date.now()
    if (now - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  has(key: string): boolean {
    const item = this.cache.get(key)
    if (!item) return false

    const now = Date.now()
    if (now - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return false
    }

    return true
  }

  delete(key: string) {
    this.cache.delete(key)
  }

  clear() {
    this.cache.clear()
  }

  // 清理过期缓存
  cleanup() {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key)
      }
    }
  }
}

export const apiCache = new ApiCache()

// 定期清理过期缓存
setInterval(() => {
  apiCache.cleanup()
}, 60 * 1000) // 每分钟清理一次

/**
 * 缓存装饰器
 * @param cacheKey 缓存键
 * @param ttl 缓存时间（毫秒）
 * @returns 装饰器函数
 */
export function cached(cacheKey: string, ttl?: number) {
  return function <T extends (...args: any[]) => Promise<any>>(
    target: any,
    propertyName: string,
    descriptor: TypedPropertyDescriptor<T>,
  ) {
    const method = descriptor.value!

    descriptor.value = async function (this: any, ...args: any[]) {
      const key = `${cacheKey}:${JSON.stringify(args)}`

      if (apiCache.has(key)) {
        return apiCache.get(key)
      }

      const result = await method.apply(this, args)
      apiCache.set(key, result, ttl)

      return result
    } as T
  }
}

/**
 * 性能监控
 */
export class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private metrics = new Map<string, number[]>()

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  // 测量函数执行时间
  measure<T>(name: string, fn: () => T): T {
    const start = performance.now()
    const result = fn()
    const end = performance.now()

    this.recordMetric(name, end - start)
    return result
  }

  // 测量异步函数执行时间
  async measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now()
    const result = await fn()
    const end = performance.now()

    this.recordMetric(name, end - start)
    return result
  }

  // 记录指标
  recordMetric(name: string, value: number) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, [])
    }

    const values = this.metrics.get(name)!
    values.push(value)

    // 只保留最近100个记录
    if (values.length > 100) {
      values.shift()
    }
  }

  // 获取指标统计
  getStats(name: string) {
    const values = this.metrics.get(name)
    if (!values || values.length === 0) {
      return null
    }

    const sorted = [...values].sort((a, b) => a - b)
    const sum = values.reduce((a, b) => a + b, 0)

    return {
      count: values.length,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      avg: sum / values.length,
      median: sorted[Math.floor(sorted.length / 2)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)],
    }
  }

  // 获取所有指标
  getAllStats() {
    const stats: Record<string, any> = {}
    for (const name of this.metrics.keys()) {
      stats[name] = this.getStats(name)
    }
    return stats
  }

  // 清除指标
  clearMetrics(name?: string) {
    if (name) {
      this.metrics.delete(name)
    } else {
      this.metrics.clear()
    }
  }
}

export const performanceMonitor = PerformanceMonitor.getInstance()

/**
 * 资源预加载
 * @param urls 要预加载的资源URL数组
 * @param type 资源类型
 */
export function preloadResources(urls: string[], type: 'image' | 'script' | 'style' = 'image') {
  urls.forEach((url) => {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = url

    switch (type) {
      case 'image':
        link.as = 'image'
        break
      case 'script':
        link.as = 'script'
        break
      case 'style':
        link.as = 'style'
        break
    }

    document.head.appendChild(link)
  })
}

/**
 * 检测设备性能
 */
export function getDevicePerformance() {
  // 检测设备内存
  const memory = (navigator as any).deviceMemory || 4 // 默认4GB

  // 检测CPU核心数
  const cores = navigator.hardwareConcurrency || 4 // 默认4核

  // 检测网络连接
  const connection = (navigator as any).connection
  const effectiveType = connection?.effectiveType || '4g'

  // 性能等级评估
  let performanceLevel: 'low' | 'medium' | 'high' = 'medium'

  if (memory >= 8 && cores >= 8 && ['4g', '5g'].includes(effectiveType)) {
    performanceLevel = 'high'
  } else if (memory <= 2 || cores <= 2 || effectiveType === 'slow-2g') {
    performanceLevel = 'low'
  }

  return {
    memory,
    cores,
    effectiveType,
    performanceLevel,
  }
}

/**
 * 根据设备性能调整配置
 */
export function getOptimalConfig() {
  const { performanceLevel } = getDevicePerformance()

  const configs = {
    low: {
      pageSize: 10,
      debounceDelay: 500,
      throttleDelay: 100,
      cacheSize: 50,
      enableVirtualScroll: true,
      enableImageLazyLoad: true,
      enablePreload: false,
    },
    medium: {
      pageSize: 20,
      debounceDelay: 300,
      throttleDelay: 50,
      cacheSize: 100,
      enableVirtualScroll: false,
      enableImageLazyLoad: true,
      enablePreload: true,
    },
    high: {
      pageSize: 50,
      debounceDelay: 200,
      throttleDelay: 16,
      cacheSize: 200,
      enableVirtualScroll: false,
      enableImageLazyLoad: false,
      enablePreload: true,
    },
  }

  return configs[performanceLevel]
}
