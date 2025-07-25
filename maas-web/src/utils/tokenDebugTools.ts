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

import { tokenMonitor } from './tokenMonitor'

// 开发环境下的调试工具
class TokenDebugTools {
  // 在控制台打印当前统计信息
  printStats() {
    console.group('🔑 Token监控统计')
    console.log(tokenMonitor.generateReport())
    console.groupEnd()
  }

  // 在控制台打印健康状态
  printHealth() {
    const health = tokenMonitor.getHealthStatus()
    const errorRate = tokenMonitor.getErrorRate()
    const successRate = tokenMonitor.getSuccessRate()
    const stats = tokenMonitor.getStats()
    
    const healthEmoji = {
      healthy: '✅',
      warning: '⚠️',
      critical: '❌'
    }
    
    console.log(`${healthEmoji[health]} Token健康状态: ${health.toUpperCase()}`)
    console.log(`📊 成功率: ${successRate.toFixed(1)}% | 错误率: ${errorRate.toFixed(1)}%`)
    console.log(`⚡ 平均响应时间: ${stats.averageResponseTime.toFixed(0)}ms`)
    console.log(`🔄 总刷新次数: ${stats.totalAttempts} | 预防性刷新: ${stats.preventiveRefreshCount}`)
  }

  // 在控制台打印最近事件
  printRecentEvents(count: number = 10) {
    const events = tokenMonitor.getRecentEvents(count)
    console.group(`📋 最近${count}个Token事件`)
    events.forEach(event => {
      const time = new Date(event.timestamp).toLocaleTimeString()
      const eventName = event.event.replace(/_/g, ' ')
      let icon = '🔵'
      
      if (event.event.includes('SUCCESS')) icon = '✅'
      else if (event.event.includes('FAILED')) icon = '❌'
      else if (event.event.includes('RETRY')) icon = '🔄'
      else if (event.event.includes('PREVENTIVE')) icon = '⚡'
      
      console.log(`${icon} ${time} - ${eventName}${event.error ? ` (${event.error})` : ''}`)
    })
    console.groupEnd()
  }

  // 重置所有统计数据
  resetStats() {
    tokenMonitor.resetStats()
    console.log('🔄 Token监控统计已重置')
  }

  // 模拟监控告警
  checkAlerts() {
    const health = tokenMonitor.getHealthStatus()
    const errorRate = tokenMonitor.getErrorRate()
    const stats = tokenMonitor.getStats()
    
    const alerts = []
    
    if (health === 'critical') {
      alerts.push('🚨 CRITICAL: Token刷新系统状态异常')
    } else if (health === 'warning') {
      alerts.push('⚠️ WARNING: Token刷新系统性能下降')
    }
    
    if (errorRate > 30) {
      alerts.push(`🚨 高错误率: ${errorRate.toFixed(1)}%`)
    }
    
    if (stats.averageResponseTime > 5000) {
      alerts.push(`⚠️ 响应时间过长: ${stats.averageResponseTime.toFixed(0)}ms`)
    }
    
    if (stats.totalAttempts > 0 && stats.failureCount === stats.totalAttempts) {
      alerts.push('🚨 所有Token刷新尝试都失败了')
    }
    
    if (alerts.length > 0) {
      console.group('🚨 Token监控告警')
      alerts.forEach(alert => console.warn(alert))
      console.groupEnd()
    } else {
      console.log('✅ 没有Token监控告警')
    }
    
    return alerts
  }

  // 导出监控数据
  exportData() {
    const data = {
      stats: tokenMonitor.getStats(),
      recentEvents: tokenMonitor.getRecentEvents(50),
      health: tokenMonitor.getHealthStatus(),
      errorRate: tokenMonitor.getErrorRate(),
      successRate: tokenMonitor.getSuccessRate(),
      exportTime: new Date().toISOString()
    }
    
    console.log('📤 Token监控数据导出:')
    console.log(JSON.stringify(data, null, 2))
    
    return data
  }

  // 监控数据概览
  overview() {
    console.group('🔍 Token监控概览')
    this.printHealth()
    console.log('')
    this.printRecentEvents(5)
    console.log('')
    const alerts = this.checkAlerts()
    if (alerts.length === 0) {
      console.log('✅ 系统运行正常')
    }
    console.groupEnd()
  }

  // 启动定期报告
  startPeriodicReport(intervalMinutes: number = 5) {
    console.log(`📊 启动Token监控定期报告，间隔: ${intervalMinutes}分钟`)
    
    const interval = setInterval(() => {
      const stats = tokenMonitor.getStats()
      if (stats.totalAttempts > 0) {
        this.overview()
      }
    }, intervalMinutes * 60 * 1000)
    
    return interval
  }
}

// 创建全局调试工具实例
export const tokenDebugTools = new TokenDebugTools()

// 开发环境下将调试工具挂载到window对象
if (import.meta.env.DEV && typeof window !== 'undefined') {
  ;(window as any).tokenDebug = tokenDebugTools
  ;(window as any).tokenMonitor = tokenMonitor
  
  console.log('🔧 Token调试工具已挂载到 window.tokenDebug')
  console.log('📊 Token监控器已挂载到 window.tokenMonitor')
  console.log('使用 tokenDebug.overview() 查看监控概览')
}