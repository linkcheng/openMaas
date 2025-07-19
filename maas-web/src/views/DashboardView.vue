<template>
  <div class="dashboard">
    <div class="container">
      <h1>仪表板</h1>

      <!-- 管理员仪表板 -->
      <div v-if="isAdmin" class="admin-section">
        <div class="stats-overview">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <span class="stat-value">{{ adminStats.total_users }}</span>
              <span class="stat-label">总用户数</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🔑</div>
            <div class="stat-content">
              <span class="stat-value">{{ adminStats.total_api_keys }}</span>
              <span class="stat-label">API密钥数</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <span class="stat-value">{{ adminStats.total_requests }}</span>
              <span class="stat-label">总请求数</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-content">
              <span class="stat-value">{{ adminStats.active_users }}</span>
              <span class="stat-label">活跃用户</span>
            </div>
          </div>
        </div>

        <!-- 管理员快速操作 -->
        <div class="quick-actions">
          <h2>管理员操作</h2>
          <div class="actions-grid">
            <router-link to="/admin" class="action-card">
              <div class="action-icon">🏠</div>
              <h3>管理后台</h3>
              <p>进入完整的管理员后台</p>
            </router-link>

            <router-link to="/admin/users" class="action-card">
              <div class="action-icon">👥</div>
              <h3>用户管理</h3>
              <p>管理系统用户和权限</p>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 普通用户仪表板 -->
      <div v-else class="user-section">
        <div class="welcome-card">
          <h2>欢迎回来, {{ currentUser?.username || '用户' }}!</h2>
          <p>这是您的个人仪表板，您可以在这里管理您的设置和查看使用情况。</p>
        </div>

        <div class="user-stats">
          <div class="stat-card">
            <div class="stat-icon">🔑</div>
            <div class="stat-content">
              <span class="stat-value">{{ userStats.api_keys_count }}</span>
              <span class="stat-label">API密钥</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <span class="stat-value">{{ userStats.requests_count }}</span>
              <span class="stat-label">本月请求</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-content">
              <span class="stat-value">${{ userStats.usage_cost }}</span>
              <span class="stat-label">本月费用</span>
            </div>
          </div>
        </div>

        <!-- 普通用户快速操作 -->
        <div class="quick-actions">
          <h2>快速操作</h2>
          <div class="actions-grid">
            <router-link to="/profile" class="action-card">
              <div class="action-icon">👤</div>
              <h3>个人资料</h3>
              <p>查看和编辑个人信息</p>
            </router-link>

            <router-link to="/settings" class="action-card">
              <div class="action-icon">⚙️</div>
              <h3>设置</h3>
              <p>管理账户设置和偏好</p>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 最近活动（所有用户） -->
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { handleApiError } from '@/utils/api'

interface AdminStats {
  total_users: number
  total_api_keys: number
  total_requests: number
  active_users: number
}

interface UserStats {
  api_keys_count: number
  requests_count: number
  usage_cost: number
}

interface Activity {
  id: string
  type: string
  description: string
  timestamp: string
  status: 'success' | 'warning' | 'error'
}

const { isAdmin, currentUser } = useAuth()

const adminStats = reactive<AdminStats>({
  total_users: 0,
  total_api_keys: 0,
  total_requests: 0,
  active_users: 0,
})

const userStats = reactive<UserStats>({
  api_keys_count: 0,
  requests_count: 0,
  usage_cost: 0,
})

const recentActivities = ref<Activity[]>([])

const loadAdminStats = async () => {
  try {
    adminStats.total_users = 245
    adminStats.total_api_keys = 89
    adminStats.total_requests = 15420
    adminStats.active_users = 67
  } catch (error) {
    console.error('加载管理员统计失败:', handleApiError(error))
  }
}

const loadUserStats = async () => {
  try {
    userStats.api_keys_count = 3
    userStats.requests_count = 1240
    userStats.usage_cost = 24.5
  } catch (error) {
    console.error('加载用户统计失败:', handleApiError(error))
  }
}

const loadRecentActivities = async () => {
  try {
    const activities: Activity[] = [
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
      activities.push(
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

    recentActivities.value = activities
  } catch (error) {
    console.error('加载最近活动失败:', handleApiError(error))
  }
}

const getActivityIcon = (type: string): string => {
  const icons: Record<string, string> = {
    api_call: '🔗',
    login: '🔐',
    user_register: '👤',
    system_warning: '⚠️',
    api_key_created: '🔑',
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
  if (isAdmin.value) {
    loadAdminStats()
  }
  loadUserStats()
  loadRecentActivities()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  text-align: center;
}

.welcome-card h2 {
  color: #6366f1;
  margin-bottom: 0.5rem;
}

.stats-overview,
.user-stats {
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

.quick-actions,
.recent-activity {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
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

h1,
h2 {
  color: #111827;
  margin-bottom: 1rem;
}
</style>
