<!--
Copyright 2025 MaaS Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

<template>
  <div class="dashboard">
    <div class="container">
      <!-- 页面头部 -->
      <div class="dashboard-header">
        <div class="header-left">
          <h1>仪表板</h1>
          <div class="real-time-indicator">
            <div class="indicator-dot" :class="{ active: !error }"></div>
            <span class="indicator-text">
              {{ error ? '连接异常' : '实时监控' }}
            </span>
          </div>
        </div>
        <div class="header-actions">
          <div v-if="error" class="connection-status error">
            <el-icon><WarnTriangleFilled /></el-icon>
            {{ error }}
          </div>
          <el-text v-else-if="lastUpdated" type="info" size="small">
            最后更新: {{ formatTime(lastUpdated.toISOString()) }}
          </el-text>
          <el-button
            :icon="RefreshRight"
            :loading="refreshing"
            @click="refreshData"
            circle
            title="刷新数据"
          />
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 主要内容 -->
      <div v-else>
        <!-- 管理员仪表板 -->
        <div v-if="isAdmin" class="admin-section">
          <!-- 统计卡片 -->
          <div class="stats-overview">
            <StatCard
              :value="adminStats.total_users || 0"
              label="总用户数"
              subtitle="系统注册用户总数"
              :icon-component="User"
              icon-color="#6366f1"
              icon-text-color="white"
              :trend="calculateTrend('users')"
              comparison="+12% vs 上月"
              format-type="number"
              clickable
              action-text="查看详情"
              @click="navigateToUserManagement"
            />

            <StatCard
              :value="adminStats.total_api_keys || 0"
              label="API密钥数"
              subtitle="已创建的API密钥总数"
              :icon-component="Key"
              icon-color="#10b981"
              icon-text-color="white"
              :trend="calculateTrend('api_keys')"
              comparison="+5% vs 上月"
              format-type="number"
              clickable
              @click="navigateToApiKeys"
            />

            <StatCard
              :value="adminStats.total_requests || 0"
              label="总请求数"
              subtitle="累计API调用次数"
              :icon-component="TrendCharts"
              icon-color="#f59e0b"
              icon-text-color="white"
              :trend="calculateTrend('requests')"
              comparison="+8% vs 上月"
              format-type="number"
              clickable
              @click="navigateToAnalytics"
            />

            <StatCard
              :value="adminStats.active_users || 0"
              label="活跃用户"
              subtitle="过去30天内活跃用户"
              :icon-component="User"
              icon-color="#8b5cf6"
              icon-text-color="white"
              :trend="calculateTrend('active_users')"
              comparison="+15% vs 上月"
              format-type="number"
              clickable
              @click="navigateToUserActivity"
            />
          </div>

          <!-- 管理员图表区域 -->
          <DashboardCharts
            title="数据分析"
            :loading="loading"
            @period-change="handlePeriodChange"
            @refresh="refreshData"
          />

          <!-- 管理员快速操作 -->
          <QuickActions
            title="管理员操作"
            :actions="adminQuickActions"
            :show-recent-actions="true"
            :recent-actions="recentAdminActions"
            @action-click="handleQuickActionClick"
          />
        </div>

        <!-- 普通用户仪表板 -->
        <div v-else class="user-section">
          <div class="welcome-card">
            <h2>欢迎回来, {{ currentUser?.username || '用户' }}!</h2>
            <p>这是您的个人仪表板，您可以在这里管理您的设置和查看使用情况。</p>
          </div>

          <div class="user-stats">
            <StatCard
              :value="userStats.api_keys_count || 0"
              label="API密钥"
              subtitle="您创建的API密钥数量"
              :icon-component="Key"
              icon-color="#6366f1"
              icon-text-color="white"
              format-type="number"
              clickable
              action-text="管理密钥"
              @click="navigateToUserApiKeys"
            />

            <StatCard
              :value="userStats.requests_count || 0"
              label="本月请求"
              subtitle="当月API调用次数"
              :icon-component="TrendCharts"
              icon-color="#10b981"
              icon-text-color="white"
              :trend="calculateUserTrend('requests')"
              comparison="+12% vs 上月"
              format-type="number"
              clickable
              @click="navigateToUserAnalytics"
            />

            <StatCard
              :value="userStats.usage_cost || 0"
              label="本月费用"
              subtitle="当月使用费用统计"
              :icon-component="Monitor"
              icon-color="#f59e0b"
              icon-text-color="white"
              :trend="calculateUserTrend('cost')"
              comparison="-5% vs 上月"
              format-type="currency"
              :precision="2"
              clickable
              action-text="查看账单"
              @click="navigateToUserBilling"
            />
          </div>

          <!-- 普通用户快速操作 -->
          <QuickActions
            title="快速操作"
            :actions="userQuickActions"
            :show-recent-actions="true"
            :recent-actions="recentUserActions"
            @action-click="handleQuickActionClick"
          />
        </div>

        <!-- 最近活动（所有用户） -->
        <ActivityLog
          title="最近活动"
          :activities="enrichedActivities"
          :loading="loading"
          :has-more="hasMoreActivities"
          :total-count="totalActivitiesCount"
          @refresh="refreshData"
          @load-more="loadMoreActivities"
          @filter-change="handleActivityFilterChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { RefreshRight, WarnTriangleFilled } from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'
import { useDashboard } from '@/composables/useDashboard'
import StatCard from '@/components/dashboard/StatCard.vue'
import DashboardCharts from '@/components/dashboard/DashboardCharts.vue'
import ActivityLog from '@/components/dashboard/ActivityLog.vue'
import QuickActions from '@/components/dashboard/QuickActions.vue'
import {
  Monitor,
  Key,
  TrendCharts,
  User,
  Setting,
  UserFilled,
  House,
} from '@element-plus/icons-vue'

interface ActivityMetadata {
  [key: string]: string | number
}

interface QuickActionType {
  id: string
  title: string
  description: string
  iconComponent?: any // eslint-disable-line @typescript-eslint/no-explicit-any
  color: string
  lastUsed?: string
  route: string
  badge?: string
  badgeType?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  shortcut?: string
  stats?: { label: string; value: string | number }[]
  showFooter?: boolean
}

const { isAdmin, currentUser } = useAuth()

const {
  // 状态
  loading,
  refreshing,
  lastUpdated,
  error,

  // 数据
  userStats,
  adminStats,
  recentActivities,

  // 方法
  refreshData,
  formatTime,
  handlePeriodChange,
} = useDashboard()

// 增强的活动数据
const enrichedActivities = computed(() => {
  return recentActivities.value.map((activity) => ({
    ...activity,
    user: isAdmin.value ? 'admin' : currentUser.value?.username,
    details: getActivityDetails(activity),
    metadata: getActivityMetadata(activity),
  }))
})

// 活动分页状态
const hasMoreActivities = ref(false)
const totalActivitiesCount = ref(0)

// 快速操作数据
const adminQuickActions = computed(() => [
  {
    id: 'admin-dashboard',
    title: '管理后台',
    description: '进入完整的管理员后台系统',
    iconComponent: House,
    color: '#6366f1',
    badge: '管理',
    badgeType: 'primary' as const,
    stats: [
      { label: '在线用户', value: '67' },
      { label: '系统负载', value: '32%' },
    ],
    route: '/admin/dashboard',
  },
  {
    id: 'user-management',
    title: '用户管理',
    description: '管理系统用户和权限设置',
    iconComponent: UserFilled,
    color: '#10b981',
    stats: [
      { label: '总用户', value: adminStats.total_users || 0 },
      { label: '今日新增', value: '5' },
    ],
    route: '/admin/users',
  },
  {
    id: 'system-settings',
    title: '系统设置',
    description: '配置系统参数和安全策略',
    iconComponent: Setting,
    color: '#f59e0b',
    badge: '重要',
    badgeType: 'warning' as const,
    shortcut: 'Ctrl+S',
    route: '/admin/settings',
  },
])

const userQuickActions = computed(() => [
  {
    id: 'user-profile',
    title: '个人资料',
    description: '查看和编辑个人信息设置',
    iconComponent: UserFilled,
    color: '#6366f1',
    stats: [{ label: '完整度', value: '85%' }],
    route: '/user/profile',
  },
  {
    id: 'user-settings',
    title: '账户设置',
    description: '管理账户设置和安全偏好',
    iconComponent: Setting,
    color: '#10b981',
    shortcut: 'Ctrl+,',
    route: '/user/settings',
  },
])

const recentAdminActions = ref<QuickActionType[]>([
  {
    id: 'recent-1',
    title: '用户管理',
    description: '管理系统用户和权限设置',
    iconComponent: UserFilled,
    color: '#10b981',
    lastUsed: '2分钟前',
    route: '/admin/users',
  },
])

const recentUserActions = ref<QuickActionType[]>([
  {
    id: 'recent-user-1',
    title: '个人资料',
    description: '查看和编辑个人信息设置',
    iconComponent: UserFilled,
    color: '#6366f1',
    lastUsed: '5分钟前',
    route: '/user/profile',
  },
])

// 计算趋势百分比
const calculateTrend = (type: string): number => {
  // 这里应该基于历史数据计算实际趋势
  const trendMap: Record<string, number> = {
    users: 12,
    api_keys: 5,
    requests: 8,
    active_users: 15,
  }
  return trendMap[type] || 0
}

const calculateUserTrend = (type: string): number => {
  const trendMap: Record<string, number> = {
    requests: 12,
    cost: -5,
  }
  return trendMap[type] || 0
}

// 获取活动详情
const getActivityDetails = (activity: { type: string }): string | undefined => {
  if (activity.type === 'api_call') {
    return '成功处理API请求，响应时间245ms'
  }
  if (activity.type === 'system_warning') {
    return '系统负载达到80%，建议关注资源使用情况'
  }
  return undefined
}

// 获取活动元数据
const getActivityMetadata = (activity: { type: string }): ActivityMetadata | undefined => {
  if (activity.type === 'api_call') {
    return {
      端点: '/api/v1/models/predict',
      方法: 'POST',
      状态码: '200',
      IP地址: '192.168.1.100',
    }
  }
  return undefined
}

// 导航方法
const navigateToUserManagement = () => {
  console.log('导航到用户管理')
}

const navigateToApiKeys = () => {
  console.log('导航到API密钥管理')
}

const navigateToAnalytics = () => {
  console.log('导航到分析页面')
}

const navigateToUserActivity = () => {
  console.log('导航到用户活动')
}

const navigateToUserApiKeys = () => {
  console.log('导航到用户API密钥')
}

const navigateToUserAnalytics = () => {
  console.log('导航到用户分析')
}

const navigateToUserBilling = () => {
  console.log('导航到用户账单')
}

// 活动相关方法
const loadMoreActivities = () => {
  console.log('加载更多活动')
}

const handleActivityFilterChange = (filter: string) => {
  console.log('活动过滤变更:', filter)
}

// 快速操作点击处理
const handleQuickActionClick = (action: QuickActionType) => {
  console.log('快速操作点击:', action)
  if (action.route) {
    // 这里应该使用路由导航
    console.log('导航到:', action.route)
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* 页面头部样式 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--el-border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.dashboard-header h1 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 2rem;
  font-weight: 700;
}

/* 实时监控指示器 */
.real-time-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--el-fill-color-extra-light);
  border-radius: 20px;
  border: 1px solid var(--el-border-color-light);
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--el-color-danger);
  animation: pulse-inactive 2s infinite ease-in-out;
}

.indicator-dot.active {
  background: var(--el-color-success);
  animation: pulse-active 2s infinite ease-in-out;
}

.indicator-text {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--el-text-color-regular);
}

@keyframes pulse-active {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

@keyframes pulse-inactive {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* 连接状态样式 */
.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.connection-status.error {
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning);
  border: 1px solid var(--el-color-warning-light-7);
}

.connection-status.partial {
  background: var(--el-color-info-light-9);
  color: var(--el-color-info);
  border: 1px solid var(--el-color-info-light-7);
}

.connection-status.connected {
  background: var(--el-color-success-light-9);
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success-light-7);
}

/* 加载状态 */
.loading-container {
  padding: 2rem;
}

/* 空状态样式 */
.empty-activities {
  padding: 2rem;
  text-align: center;
}

.welcome-card {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.welcome-card h2 {
  color: var(--el-color-primary);
  margin-bottom: 0.5rem;
}

.stats-overview,
.user-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* 快速操作样式优化 */
.quick-actions {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.quick-actions h2 {
  color: var(--el-text-color-primary);
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: var(--el-fill-color-extra-light);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 1.5rem;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  display: block;
}

.action-card:hover {
  background: var(--el-fill-color-light);
  border-color: var(--el-color-primary);
  transform: translateY(-3px);
  box-shadow: var(--el-box-shadow);
  text-decoration: none;
  color: inherit;
}

.action-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  display: block;
}

.action-card h3 {
  margin: 0 0 0.75rem 0;
  color: var(--el-text-color-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.action-card p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-left {
    width: 100%;
    justify-content: space-between;
  }

  .dashboard-header h1 {
    font-size: 1.5rem;
  }

  .real-time-indicator {
    padding: 0.375rem 0.625rem;
  }

  .indicator-text {
    font-size: 0.6875rem;
  }

  .header-actions {
    justify-content: flex-end;
    width: 100%;
  }

  .stats-overview,
  .user-stats {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .activity-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .activity-status {
    align-self: flex-start;
  }
}

@media (max-width: 480px) {
  .stat-card {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }

  .action-card {
    text-align: center;
  }

  .activity-item {
    padding: 1rem 0.5rem;
  }
}

/* 主题适配 */
@media (prefers-color-scheme: dark) {
  .welcome-card {
    background: var(--el-bg-color-overlay);
  }

  .stat-card {
    background: var(--el-bg-color-overlay);
  }

  .action-card {
    background: var(--el-fill-color);
  }

  .action-card:hover {
    background: var(--el-fill-color-light);
  }
}
</style>
