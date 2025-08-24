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