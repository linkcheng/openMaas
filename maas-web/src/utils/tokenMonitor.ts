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

import { AxiosError } from 'axios'

// 监控事件类型
export enum MonitoringEvent {
  TOKEN_REFRESH_ATTEMPT = 'token_refresh_attempt',
  TOKEN_REFRESH_SUCCESS = 'token_refresh_success',
  TOKEN_REFRESH_FAILED = 'token_refresh_failed',
  TOKEN_REFRESH_RETRY = 'token_refresh_retry',
  TOKEN_REFRESH_ALL_FAILED = 'token_refresh_all_failed',
  PREVENTIVE_REFRESH_START = 'preventive_refresh_start',
  PREVENTIVE_REFRESH_SUCCESS = 'preventive_refresh_success',
  PREVENTIVE_REFRESH_FAILED = 'preventive_refresh_failed',
  QUEUE_TIMEOUT = 'queue_timeout',
  QUEUE_CLEANUP = 'queue_cleanup',
}

// 监控数据接口
export interface MonitoringData {
  event: MonitoringEvent
  timestamp: number
  attempt?: number
  maxAttempts?: number
  totalAttempts?: number
  retryDelay?: number
  error?: string
  errorType?: string
  duration?: number
  totalDuration?: number
  queueSize?: number
  metadata?: Record<string, unknown>
}

// Token刷新统计
interface TokenRefreshStats {
  totalAttempts: number
  successCount: number
  failureCount: number
  preventiveRefreshCount: number
  averageResponseTime: number
  lastRefreshTime: number
  errorsByType: Record<string, number>
}

class TokenMonitor {
  private stats: TokenRefreshStats = {
    totalAttempts: 0,
    successCount: 0,
    failureCount: 0,
    preventiveRefreshCount: 0,
    averageResponseTime: 0,
    lastRefreshTime: 0,
    errorsByType: {},
  }

  private recentEvents: MonitoringData[] = []
  private readonly maxRecentEvents = 100
  private responseTimes: number[] = []
  private readonly maxResponseTimes = 50

  // 记录监控事件
  logEvent(data: MonitoringData) {
    // 添加到最近事件列表
    this.recentEvents.unshift(data)
    if (this.recentEvents.length > this.maxRecentEvents) {
      this.recentEvents = this.recentEvents.slice(0, this.maxRecentEvents)
    }

    // 更新统计信息
    this.updateStats(data)

    // 控制台日志记录
    this.logToConsole(data)

    // 开发环境下可以发送到外部监控系统
    if (import.meta.env.DEV) {
      this.logToExternalMonitoring(data)
    }
  }

  private updateStats(data: MonitoringData) {
    switch (data.event) {
      case MonitoringEvent.TOKEN_REFRESH_ATTEMPT:
        this.stats.totalAttempts++
        break

      case MonitoringEvent.TOKEN_REFRESH_SUCCESS:
        this.stats.successCount++
        this.stats.lastRefreshTime = data.timestamp
        if (data.duration) {
          this.responseTimes.push(data.duration)
          if (this.responseTimes.length > this.maxResponseTimes) {
            this.responseTimes = this.responseTimes.slice(-this.maxResponseTimes)
          }
          this.stats.averageResponseTime =
            this.responseTimes.reduce((a, b) => a + b, 0) / this.responseTimes.length
        }
        break

      case MonitoringEvent.TOKEN_REFRESH_FAILED:
      case MonitoringEvent.TOKEN_REFRESH_ALL_FAILED:
        this.stats.failureCount++
        if (data.errorType) {
          this.stats.errorsByType[data.errorType] =
            (this.stats.errorsByType[data.errorType] || 0) + 1
        }
        break

      case MonitoringEvent.PREVENTIVE_REFRESH_SUCCESS:
        this.stats.preventiveRefreshCount++
        break
    }
  }

  private logToConsole(data: MonitoringData) {
    const timestamp = new Date(data.timestamp).toISOString()
    const eventName = data.event.replace(/_/g, ' ').toUpperCase()

    let logLevel: 'log' | 'warn' | 'error' = 'log'
    let message = `[TOKEN MONITOR] ${eventName}`

    switch (data.event) {
      case MonitoringEvent.TOKEN_REFRESH_ATTEMPT:
        message += ` - 尝试 ${data.attempt}/${data.maxAttempts}`
        break

      case MonitoringEvent.TOKEN_REFRESH_SUCCESS:
        message += data.duration ? ` - 耗时 ${data.duration}ms` : ''
        break

      case MonitoringEvent.TOKEN_REFRESH_FAILED:
      case MonitoringEvent.TOKEN_REFRESH_ALL_FAILED:
        logLevel = 'error'
        message += data.error ? ` - 错误: ${data.error}` : ''
        break

      case MonitoringEvent.PREVENTIVE_REFRESH_START:
        message += ' - 开始预防性刷新'
        break

      case MonitoringEvent.QUEUE_TIMEOUT:
        logLevel = 'warn'
        message += ` - 队列大小: ${data.queueSize || 0}`
        break
    }

    console[logLevel](`${timestamp} ${message}`, data.metadata || '')
  }

  private logToExternalMonitoring(data: MonitoringData) {
    // 这里可以集成外部监控系统，如Sentry、DataDog等
    // 示例：发送到自定义监控端点
    try {
      // 模拟发送到监控系统
      if (typeof window !== 'undefined' && window.navigator && 'sendBeacon' in window.navigator) {
        const _payload = JSON.stringify({
          source: 'maas-web-token-monitor',
          ...data,
        })
        // window.navigator.sendBeacon('/api/monitoring/token-events', _payload)
      }
    } catch (error) {
      console.warn('发送监控数据失败:', error)
    }
  }

  // 获取统计信息
  getStats(): TokenRefreshStats {
    return { ...this.stats }
  }

  // 获取最近事件
  getRecentEvents(count: number = 20): MonitoringData[] {
    return this.recentEvents.slice(0, count)
  }

  // 获取错误率
  getErrorRate(): number {
    if (this.stats.totalAttempts === 0) return 0
    return (this.stats.failureCount / this.stats.totalAttempts) * 100
  }

  // 获取成功率
  getSuccessRate(): number {
    if (this.stats.totalAttempts === 0) return 0
    return (this.stats.successCount / this.stats.totalAttempts) * 100
  }

  // 检查健康状态
  getHealthStatus(): 'healthy' | 'warning' | 'critical' {
    const errorRate = this.getErrorRate()
    const avgResponseTime = this.stats.averageResponseTime

    if (errorRate > 50 || avgResponseTime > 10000) {
      return 'critical'
    } else if (errorRate > 20 || avgResponseTime > 5000) {
      return 'warning'
    }

    return 'healthy'
  }

  // 重置统计
  resetStats() {
    this.stats = {
      totalAttempts: 0,
      successCount: 0,
      failureCount: 0,
      preventiveRefreshCount: 0,
      averageResponseTime: 0,
      lastRefreshTime: 0,
      errorsByType: {},
    }
    this.recentEvents = []
    this.responseTimes = []
  }

  // 生成监控报告
  generateReport(): string {
    const stats = this.getStats()
    const health = this.getHealthStatus()
    const errorRate = this.getErrorRate()
    const successRate = this.getSuccessRate()

    return `
Token刷新监控报告
==================
健康状态: ${health.toUpperCase()}
总尝试次数: ${stats.totalAttempts}
成功次数: ${stats.successCount}
失败次数: ${stats.failureCount}
预防性刷新次数: ${stats.preventiveRefreshCount}
成功率: ${successRate.toFixed(2)}%
错误率: ${errorRate.toFixed(2)}%
平均响应时间: ${stats.averageResponseTime.toFixed(2)}ms
最后刷新时间: ${stats.lastRefreshTime ? new Date(stats.lastRefreshTime).toLocaleString() : '无'}

错误类型统计:
${Object.entries(stats.errorsByType)
  .map(([type, count]) => `  ${type}: ${count}`)
  .join('\n')}

最近5个事件:
${this.getRecentEvents(5)
  .map(
    (event) =>
      `  ${new Date(event.timestamp).toLocaleTimeString()} - ${event.event} ${event.error ? '(' + event.error + ')' : ''}`,
  )
  .join('\n')}
    `.trim()
  }
}

// 创建全局监控实例
export const tokenMonitor = new TokenMonitor()

// 工具函数：记录token刷新事件
export const logTokenEvent = (
  event: MonitoringEvent,
  additionalData: Partial<MonitoringData> = {},
) => {
  tokenMonitor.logEvent({
    event,
    timestamp: Date.now(),
    ...additionalData,
  })
}

// 工具函数：记录错误
export const logTokenError = (
  event: MonitoringEvent,
  error: AxiosError,
  additionalData: Partial<MonitoringData> = {},
) => {
  let errorType = 'unknown'

  if (!error.response) {
    errorType = error.code === 'ECONNABORTED' ? 'timeout' : 'network'
  } else {
    const status = error.response.status
    if (status === 401) errorType = 'auth'
    else if (status >= 500) errorType = 'server'
    else errorType = 'client'
  }

  tokenMonitor.logEvent({
    event,
    timestamp: Date.now(),
    error: error.message,
    errorType,
    ...additionalData,
  })
}
