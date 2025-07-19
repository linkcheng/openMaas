<template>
  <div class="admin-dashboard">
    <div class="container">
      <h1>管理员仪表板</h1>

      <!-- 概览统计 -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.total_users }}</span>
            <span class="stat-label">总用户数</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">🔑</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.total_api_keys }}</span>
            <span class="stat-label">API密钥数</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.total_requests }}</span>
            <span class="stat-label">总请求数</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">⚡</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.active_users }}</span>
            <span class="stat-label">活跃用户</span>
          </div>
        </div>
      </div>

      <!-- 系统状态 -->
      <div class="system-status">
        <h2>系统状态</h2>
        <div class="status-grid">
          <div class="status-item">
            <div class="status-indicator" :class="{ online: systemStatus.api_server }"></div>
            <span>API服务器</span>
            <span class="status-text">{{ systemStatus.api_server ? '正常' : '异常' }}</span>
          </div>

          <div class="status-item">
            <div class="status-indicator" :class="{ online: systemStatus.database }"></div>
            <span>数据库</span>
            <span class="status-text">{{ systemStatus.database ? '正常' : '异常' }}</span>
          </div>

          <div class="status-item">
            <div class="status-indicator" :class="{ online: systemStatus.redis }"></div>
            <span>Redis缓存</span>
            <span class="status-text">{{ systemStatus.redis ? '正常' : '异常' }}</span>
          </div>

          <div class="status-item">
            <div class="status-indicator" :class="{ online: systemStatus.storage }"></div>
            <span>存储服务</span>
            <span class="status-text">{{ systemStatus.storage ? '正常' : '异常' }}</span>
          </div>
        </div>
      </div>

      <!-- 最近活动 -->
      <div class="recent-activity">
        <h2>最近活动</h2>
        <div class="activity-list">
          <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon">{{ getActivityIcon(activity.type) }}</div>
            <div class="activity-content">
              <p class="activity-description">{{ activity.description }}</p>
              <p class="activity-time">{{ formatTime(activity.timestamp) }}</p>
            </div>
            <div class="activity-status" :class="activity.status">
              {{ activity.status }}
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="quick-actions">
        <h2>快速操作</h2>
        <div class="actions-grid">
          <router-link to="/admin/users" class="action-card">
            <div class="action-icon">👥</div>
            <h3>用户管理</h3>
            <p>管理系统用户和权限</p>
          </router-link>

          <div class="action-card" @click="refreshSystemStatus">
            <div class="action-icon">🔄</div>
            <h3>刷新状态</h3>
            <p>更新系统状态信息</p>
          </div>

          <div class="action-card" @click="exportUserData">
            <div class="action-icon">📋</div>
            <h3>导出数据</h3>
            <p>导出用户和使用数据</p>
          </div>

          <div class="action-card" @click="viewSystemLogs">
            <div class="action-icon">📝</div>
            <h3>系统日志</h3>
            <p>查看系统运行日志</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { apiClient, handleApiError } from '@/utils/api'

interface Stats {
  total_users: number
  total_api_keys: number
  total_requests: number
  active_users: number
}

interface SystemStatus {
  api_server: boolean
  database: boolean
  redis: boolean
  storage: boolean
}

interface Activity {
  id: string
  type: string
  description: string
  timestamp: string
  status: 'success' | 'warning' | 'error'
}

const stats = reactive<Stats>({
  total_users: 0,
  total_api_keys: 0,
  total_requests: 0,
  active_users: 0,
})

const systemStatus = reactive<SystemStatus>({
  api_server: true,
  database: true,
  redis: true,
  storage: false,
})

const recentActivities = ref<Activity[]>([
  {
    id: '1',
    type: 'user_register',
    description: '新用户 john@example.com 注册成功',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    status: 'success',
  },
  {
    id: '2',
    type: 'api_key_created',
    description: '用户 alice@example.com 创建了新的API密钥',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    status: 'success',
  },
  {
    id: '3',
    type: 'login_failed',
    description: '用户 bob@example.com 登录失败',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    status: 'warning',
  },
  {
    id: '4',
    type: 'system_error',
    description: '存储服务连接失败',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    status: 'error',
  },
])

const loadStats = async () => {
  try {
    // 模拟加载统计数据
    // 实际应该调用管理员API获取统计信息
    stats.total_users = 245
    stats.total_api_keys = 89
    stats.total_requests = 15420
    stats.active_users = 67
  } catch (error) {
    console.error('加载统计数据失败:', handleApiError(error))
  }
}

const loadSystemStatus = async () => {
  try {
    // 模拟检查系统状态
    // 实际应该调用健康检查API
    systemStatus.api_server = true
    systemStatus.database = true
    systemStatus.redis = true
    systemStatus.storage = Math.random() > 0.3 // 模拟不稳定的存储服务
  } catch (error) {
    console.error('检查系统状态失败:', handleApiError(error))
  }
}

const refreshSystemStatus = async () => {
  await loadSystemStatus()
  alert('系统状态已刷新')
}

const exportUserData = () => {
  // 模拟导出功能
  alert('用户数据导出功能开发中...')
}

const viewSystemLogs = () => {
  // 模拟查看日志功能
  alert('系统日志查看功能开发中...')
}

const getActivityIcon = (type: string): string => {
  const icons: Record<string, string> = {
    user_register: '👤',
    api_key_created: '🔑',
    login_failed: '⚠️',
    system_error: '❌',
    default: '📋',
  }
  return icons[type] || icons.default
}

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

onMounted(() => {
  loadStats()
  loadSystemStatus()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  font-size: 2rem;
  background: #f3f4f6;
  padding: 0.75rem;
  border-radius: 50%;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #6366f1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.system-status,
.recent-activity,
.quick-actions {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 4px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ef4444;
  transition: background-color 0.2s;
}

.status-indicator.online {
  background: #10b981;
}

.status-text {
  margin-left: auto;
  font-size: 0.875rem;
  font-weight: 500;
}

.activity-list {
  margin-top: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  font-size: 1.25rem;
  background: #f3f4f6;
  padding: 0.5rem;
  border-radius: 4px;
}

.activity-content {
  flex: 1;
}

.activity-description {
  margin: 0;
  font-size: 0.875rem;
  color: #374151;
}

.activity-time {
  margin: 0.25rem 0 0 0;
  font-size: 0.75rem;
  color: #6b7280;
}

.activity-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.activity-status.success {
  background: #d1fae5;
  color: #065f46;
}

.activity-status.warning {
  background: #fef3c7;
  color: #92400e;
}

.activity-status.error {
  background: #fee2e2;
  color: #991b1b;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.action-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.action-card:hover {
  background: #f3f4f6;
  border-color: #6366f1;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.action-card h3 {
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.action-card p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

h1,
h2 {
  color: #111827;
  margin-bottom: 1rem;
}
</style>
