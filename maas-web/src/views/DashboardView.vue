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
        <h1>仪表板</h1>
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
            <div class="stat-card">
              <div class="stat-icon">👥</div>
              <div class="stat-content">
                <span class="stat-value">{{ adminStats.total_users || 0 }}</span>
                <span class="stat-label">总用户数</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon">🔑</div>
              <div class="stat-content">
                <span class="stat-value">{{ adminStats.total_api_keys || 0 }}</span>
                <span class="stat-label">API密钥数</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon">📊</div>
              <div class="stat-content">
                <span class="stat-value">{{ adminStats.total_requests || 0 }}</span>
                <span class="stat-label">总请求数</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon">⚡</div>
              <div class="stat-content">
                <span class="stat-value">{{ adminStats.active_users || 0 }}</span>
                <span class="stat-label">活跃用户</span>
              </div>
            </div>
          </div>

          <!-- 管理员图表区域 -->
          <div class="charts-section">
            <div class="charts-grid">
              <TrendChart
                title="用户增长趋势"
                :data="chartData.userGrowthTrend"
                color="#6366f1"
                type="line"
                height="300px"
                @period-change="handlePeriodChange"
              />
              <TrendChart
                title="API调用趋势"
                :data="chartData.apiCallsTrend"
                color="#10b981"
                type="bar"
                height="300px"
                @period-change="handlePeriodChange"
              />
            </div>
            <div class="charts-grid">
              <PieChart
                title="模型使用分布"
                :data="chartData.modelUsageDistribution"
                height="300px"
              />
              <PieChart
                title="用户活跃度分布"
                :data="chartData.userActivityDistribution"
                height="300px"
              />
            </div>
          </div>

          <!-- 管理员快速操作 -->
          <div class="quick-actions">
            <h2>管理员操作</h2>
            <div class="actions-grid">
              <router-link to="/admin/dashboard" class="action-card">
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
                <span class="stat-value">{{ userStats.api_keys_count || 0 }}</span>
                <span class="stat-label">API密钥</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon">📊</div>
              <div class="stat-content">
                <span class="stat-value">{{ userStats.requests_count || 0 }}</span>
                <span class="stat-label">本月请求</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon">💰</div>
              <div class="stat-content">
                <span class="stat-value">${{ userStats.usage_cost || 0 }}</span>
                <span class="stat-label">本月费用</span>
              </div>
            </div>
          </div>

          <!-- 普通用户快速操作 -->
          <div class="quick-actions">
            <h2>快速操作</h2>
            <div class="actions-grid">
              <router-link to="/user/profile" class="action-card">
                <div class="action-icon">👤</div>
                <h3>个人资料</h3>
                <p>查看和编辑个人信息</p>
              </router-link>

              <router-link to="/user/settings" class="action-card">
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
            <div v-if="recentActivities.length === 0" class="empty-activities">
              <el-empty description="暂无活动记录" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RefreshRight, WarnTriangleFilled } from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'
import { useDashboard } from '@/composables/useDashboard'
import TrendChart from '@/components/charts/TrendChart.vue'
import PieChart from '@/components/charts/PieChart.vue'

const { isAdmin, currentUser } = useAuth()

const {
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
  chartData,
  
  // 方法
  refreshData,
  formatTime,
  getActivityIcon,
  getConnectionStatus,
  handlePeriodChange,
} = useDashboard()
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

.dashboard-header h1 {
  margin: 0;
  color: var(--el-text-color-primary);
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
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

/* 图表区域样式 */
.charts-section {
  margin-bottom: 2rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

/* 确保图表在小屏幕上也能正常显示 */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

.stat-card {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: var(--el-box-shadow);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2rem;
  background: var(--el-fill-color-light);
  padding: 0.75rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 60px;
  min-height: 60px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--el-color-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--el-text-color-regular);
  margin-top: 0.25rem;
}

.quick-actions,
.recent-activity {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.quick-actions h2,
.recent-activity h2 {
  color: var(--el-text-color-primary);
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.action-card {
  background: var(--el-fill-color-extra-light);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 1.5rem;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: all 0.2s;
  display: block;
}

.action-card:hover {
  background: var(--el-fill-color-light);
  border-color: var(--el-color-primary);
  transform: translateY(-2px);
  box-shadow: var(--el-box-shadow-light);
  text-decoration: none;
  color: inherit;
}

.action-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: block;
}

.action-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--el-text-color-primary);
  font-size: 1.1rem;
}

.action-card p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--el-text-color-regular);
  line-height: 1.4;
}

.activity-list {
  margin-top: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: background-color 0.2s;
}

.activity-item:hover {
  background: var(--el-fill-color-extra-light);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  font-size: 1.25rem;
  background: var(--el-fill-color-light);
  padding: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  min-height: 40px;
}

.activity-content {
  flex: 1;
}

.activity-description {
  margin: 0;
  font-size: 0.875rem;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.activity-time {
  margin: 0.25rem 0 0 0;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.activity-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.activity-status.success {
  background: var(--el-color-success-light-9);
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success-light-7);
}

.activity-status.warning {
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning);
  border: 1px solid var(--el-color-warning-light-7);
}

.activity-status.error {
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
  border: 1px solid var(--el-color-danger-light-7);
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
