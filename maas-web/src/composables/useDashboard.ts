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

import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiClient, handleApiError } from '@/utils/api'
import { useAuth } from '@/composables/useAuth'
import type {
  UserStatsResponse,
  AdminStatsResponse,
  ActivityLogResponse,
  SystemHealthResponse,
} from '@/utils/api'

export function useDashboard() {
  const { isAdmin } = useAuth()

  // 状态管理
  const loading = ref(false)
  const refreshing = ref(false)
  const lastUpdated = ref<Date | null>(null)

  // 数据状态
  const userStats = reactive<Partial<UserStatsResponse>>({
    total_api_calls: 0,
    total_storage_used: 0,
    total_compute_hours: 0,
    models_created: 0,
    applications_created: 0,
    last_30_days_activity: {},
    api_keys_count: 0,
    requests_count: 0,
    usage_cost: 0,
  })

  const adminStats = reactive<Partial<AdminStatsResponse>>({
    total_users: 0,
    total_api_keys: 0,
    total_requests: 0,
    active_users: 0,
    active_users_30d: 0,
    total_models: 0,
    total_deployments: 0,
    storage_usage_total: 0,
    user_growth_trend: {},
    popular_models: [],
  })

  const recentActivities = ref<ActivityLogResponse[]>([])
  const systemHealth = reactive<Partial<SystemHealthResponse>>({
    status: 'healthy',
    database: true,
    redis: true,
    storage: true,
    uptime: 0,
    version: '1.0.0',
  })

  // 图表数据
  const chartData = reactive({
    // 用户增长趋势（最近30天）
    userGrowthTrend: {} as Record<string, number>,
    // API调用趋势
    apiCallsTrend: {} as Record<string, number>,
    // 模型使用分布
    modelUsageDistribution: [] as Array<{ name: string; value: number; color?: string }>,
    // 用户活跃度分布
    userActivityDistribution: [] as Array<{ name: string; value: number; color?: string }>,
  })

  // 自动刷新定时器
  let refreshInterval: ReturnType<typeof setInterval> | null = null

  // 错误状态
  const error = ref<string | null>(null)
  const apiError = ref<{
    userStats: boolean
    adminStats: boolean
    activities: boolean
    systemHealth: boolean
  }>({
    userStats: false,
    adminStats: false,
    activities: false,
    systemHealth: false,
  })

  // 加载用户统计数据
  const loadUserStats = async (): Promise<boolean> => {
    try {
      apiError.value.userStats = false
      const response = await apiClient.stats.getUserStats()
      if (response.data?.success && response.data.data) {
        Object.assign(userStats, response.data.data)
        return true
      }
      throw new Error('API响应格式错误')
    } catch (error) {
      console.error('加载用户统计失败:', handleApiError(error))
      apiError.value.userStats = true

      // 对于API不存在的情况，使用模拟数据
      Object.assign(userStats, {
        api_keys_count: 3,
        requests_count: 1240,
        usage_cost: 24.5,
        total_api_calls: 1240,
        models_created: 2,
        applications_created: 1,
      })
      return false
    }
  }

  // 加载管理员统计数据
  const loadAdminStats = async (): Promise<boolean> => {
    try {
      apiError.value.adminStats = false
      const response = await apiClient.stats.getAdminStats()
      if (response.data?.success && response.data.data) {
        Object.assign(adminStats, response.data.data)
        return true
      }
      throw new Error('API响应格式错误')
    } catch (error) {
      console.error('加载管理员统计失败:', handleApiError(error))
      apiError.value.adminStats = true

      // 对于API不存在的情况，使用模拟数据
      Object.assign(adminStats, {
        total_users: 245,
        total_api_keys: 89,
        total_requests: 15420,
        active_users: 67,
        active_users_30d: 156,
        total_models: 23,
        total_deployments: 12,
      })
      return false
    }
  }

  // 加载最近活动
  const loadRecentActivities = async (): Promise<boolean> => {
    try {
      apiError.value.activities = false
      const response = isAdmin.value
        ? await apiClient.stats.getAllActivityLogs({ limit: 10 })
        : await apiClient.stats.getUserActivityLogs({ limit: 10 })

      if (response.data?.success && response.data.data) {
        recentActivities.value = response.data.data
        return true
      }
      throw new Error('API响应格式错误')
    } catch (error) {
      console.error('加载最近活动失败:', handleApiError(error))
      apiError.value.activities = true

      // 对于API不存在的情况，使用模拟数据
      const mockActivities: ActivityLogResponse[] = [
        {
          id: '1',
          type: 'api_call',
          description: '成功调用API接口',
          timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
          status: 'success',
        },
        {
          id: '2',
          type: 'login',
          description: '用户登录成功',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          status: 'success',
        },
      ]

      if (isAdmin.value) {
        mockActivities.push(
          {
            id: '3',
            type: 'user_register',
            description: '新用户注册',
            timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
            status: 'success',
          },
          {
            id: '4',
            type: 'system_warning',
            description: '系统负载较高',
            timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
            status: 'warning',
          },
        )
      }

      recentActivities.value = mockActivities
      return false
    }
  }

  // 加载系统健康状态
  const loadSystemHealth = async (): Promise<boolean> => {
    try {
      apiError.value.systemHealth = false
      const response = await apiClient.system.getHealth()
      if (response.data?.success && response.data.data) {
        Object.assign(systemHealth, response.data.data)
        return true
      }
      throw new Error('API响应格式错误')
    } catch (error) {
      console.error('加载系统状态失败:', handleApiError(error))
      apiError.value.systemHealth = true
      // 使用默认值，不显示错误消息
      return false
    }
  }

  // 加载所有数据
  const loadAllData = async () => {
    loading.value = true
    error.value = null

    try {
      const promises: Promise<boolean>[] = [loadUserStats(), loadRecentActivities()]

      if (isAdmin.value) {
        promises.push(loadAdminStats(), loadSystemHealth())
      }

      const results = await Promise.all(promises)
      const successCount = results.filter((success) => success).length
      const totalCount = results.length

      // 如果部分API失败但不是全部失败，只在控制台记录
      if (successCount === 0) {
        error.value = '无法连接到服务器，正在使用演示数据'
        ElMessage.warning('当前显示的是演示数据，请检查网络连接')
      } else if (successCount < totalCount) {
        console.warn(`部分API加载失败: ${successCount}/${totalCount} 成功`)
      }

      lastUpdated.value = new Date()

      // 生成图表数据
      generateChartData()
    } catch (error) {
      ElMessage.error('加载仪表盘数据失败')
      console.error('加载数据时出现未预期错误:', error)
    } finally {
      loading.value = false
    }
  }

  // 刷新数据
  const refreshData = async () => {
    refreshing.value = true
    try {
      await loadAllData()

      // 根据API状态显示不同消息
      const hasAnyApiError = Object.values(apiError.value).some((hasError) => hasError)
      if (!hasAnyApiError) {
        ElMessage.success('数据已刷新')
      } else {
        ElMessage.info('数据已刷新（部分为演示数据）')
      }
    } catch (err) {
      ElMessage.error('刷新数据失败')
      console.error('刷新数据失败:', err)
    } finally {
      refreshing.value = false
    }
  }

  // 获取连接状态
  const getConnectionStatus = () => {
    const hasAnyApiError = Object.values(apiError.value).some((hasError) => hasError)

    if (!hasAnyApiError) {
      return { status: 'connected', message: '已连接到服务器' }
    }

    const errorCount = Object.values(apiError.value).filter((hasError) => hasError).length
    const totalApis = Object.keys(apiError.value).length

    if (errorCount === totalApis) {
      return { status: 'disconnected', message: '无法连接到服务器' }
    }

    return { status: 'partial', message: `部分服务不可用 (${totalApis - errorCount}/${totalApis})` }
  }

  // 生成模拟图表数据
  const generateChartData = () => {
    // 生成用户增长趋势数据（最近30天）
    const userTrend: Record<string, number> = {}
    const apiTrend: Record<string, number> = {}

    for (let i = 29; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      const dateKey = date.toISOString().split('T')[0]

      // 模拟用户增长数据
      userTrend[dateKey] = Math.floor(Math.random() * 10) + 5

      // 模拟API调用数据
      apiTrend[dateKey] = Math.floor(Math.random() * 500) + 200
    }

    chartData.userGrowthTrend = userTrend
    chartData.apiCallsTrend = apiTrend

    // 生成模型使用分布数据
    chartData.modelUsageDistribution = [
      { name: 'GPT-4', value: 45, color: '#6366f1' },
      { name: 'Claude-3', value: 30, color: '#8b5cf6' },
      { name: 'Llama-2', value: 15, color: '#06b6d4' },
      { name: '其他模型', value: 10, color: '#10b981' },
    ]

    // 生成用户活跃度分布
    chartData.userActivityDistribution = [
      { name: '高度活跃', value: 25, color: '#10b981' },
      { name: '中等活跃', value: 35, color: '#f59e0b' },
      { name: '低度活跃', value: 30, color: '#ef4444' },
      { name: '不活跃', value: 10, color: '#6b7280' },
    ]
  }

  // 处理时间周期变化
  const handlePeriodChange = (period: string) => {
    // 根据选择的时间周期重新生成数据
    let days = 30
    if (period === '7days') days = 7
    else if (period === '3months') days = 90

    const newUserTrend: Record<string, number> = {}
    const newApiTrend: Record<string, number> = {}

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      const dateKey = date.toISOString().split('T')[0]

      newUserTrend[dateKey] = Math.floor(Math.random() * 10) + 5
      newApiTrend[dateKey] = Math.floor(Math.random() * 500) + 200
    }

    chartData.userGrowthTrend = newUserTrend
    chartData.apiCallsTrend = newApiTrend
  }

  // 启动自动刷新
  const startAutoRefresh = (intervalMs: number = 5 * 60 * 1000) => {
    stopAutoRefresh()
    refreshInterval = setInterval(() => {
      loadAllData()
    }, intervalMs)
  }

  // 停止自动刷新
  const stopAutoRefresh = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }

  // 格式化时间
  const formatTime = (timestamp: string): string => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60))

    if (diffMinutes < 1) return '刚刚'
    if (diffMinutes < 60) return `${diffMinutes}分钟前`

    const diffHours = Math.floor(diffMinutes / 60)
    if (diffHours < 24) return `${diffHours}小时前`

    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}天前`
  }

  // 获取活动图标
  const getActivityIcon = (type: string): string => {
    const icons: Record<string, string> = {
      api_call: '🔗',
      login: '🔐',
      user_register: '👤',
      system_warning: '⚠️',
      api_key_created: '🔑',
      model_upload: '🤖',
      deployment: '🚀',
      default: '📋',
    }
    return icons[type] || icons.default
  }

  // 生命周期管理
  onMounted(() => {
    loadAllData()
    startAutoRefresh() // 每5分钟自动刷新
  })

  onUnmounted(() => {
    stopAutoRefresh()
  })

  return {
    // 状态
    loading,
    refreshing,
    lastUpdated,
    error,
    apiError,

    // 数据
    userStats,
    adminStats,
    recentActivities,
    systemHealth,
    chartData,

    // 方法
    loadAllData,
    refreshData,
    startAutoRefresh,
    stopAutoRefresh,
    formatTime,
    getActivityIcon,
    getConnectionStatus,
    handlePeriodChange,
  }
}
