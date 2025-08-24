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
import { memoryCache } from './cache'

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

// 简化的API缓存（使用统一缓存工具）

/**
 * 缓存API响应
 * @param key 缓存键
 * @param fetchFn 获取数据的函数
 * @param ttlMs 缓存时间（毫秒），默认5分钟
 */
export async function cacheApiResponse<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttlMs = 5 * 60 * 1000
): Promise<T> {
  // 检查缓存
  const cached = memoryCache.get<T>(key)
  if (cached) {
    return cached
  }

  // 获取数据并缓存
  const result = await fetchFn()
  memoryCache.set(key, result, ttlMs)
  return result
}

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

// 重新导出性能监控相关功能
export {
  PerformanceMonitor,
  performanceMonitor,
  getDevicePerformance,
  getOptimalConfig,
} from './performanceMonitor'
