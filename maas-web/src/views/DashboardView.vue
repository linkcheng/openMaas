<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="title-section">
      <h1>仪表盘</h1>
      <div class="real-time-indicator">
        <el-icon><DataAnalysis /></el-icon>
        <span>实时监控</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-cards">
      <el-col v-for="(stat, index) in stats" :key="index" :xs="24" :sm="12" :md="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">{{ stat.label }}</p>
              <p class="stat-value">{{ stat.value }}</p>
            </div>
            <el-icon class="stat-icon" :style="{ color: stat.iconColor }">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-change">
            <el-icon class="trend-icon"><TrendCharts /></el-icon>
            <span class="change-value">{{ stat.change }}</span>
            <span class="change-period">vs 上月</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="24" class="main-content">
      <!-- 模型性能图表 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span class="card-title">模型性能趋势</span>
          </template>
          <div class="chart-placeholder">
            <p>图表区域 - 集成实际图表库</p>
          </div>
        </el-card>
      </el-col>

      <!-- 最近活动 -->
      <el-col :xs="24" :lg="12">
        <el-card class="activity-card">
          <template #header>
            <span class="card-title">最近活动</span>
          </template>
          <div class="activity-list">
            <div v-for="(activity, index) in recentActivity" :key="index" class="activity-item">
              <div class="activity-avatar">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="activity-content">
                <p class="activity-text">
                  {{ activity.action }}
                  <span class="activity-name">{{ activity.name }}</span>
                </p>
                <p class="activity-time">{{ activity.time }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-card class="quick-actions-card">
      <template #header>
        <span class="card-title">快速操作</span>
      </template>
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8">
          <el-button type="primary" size="large" class="quick-action-btn"> 创建新模型 </el-button>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-button type="success" size="large" class="quick-action-btn"> 上传数据集 </el-button>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-button color="#8b5cf6" size="large" class="quick-action-btn"> 部署应用 </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { DataAnalysis, Coin, Cpu, Monitor, User, TrendCharts } from '@element-plus/icons-vue'

interface StatItem {
  icon: typeof DataAnalysis
  iconColor: string
  label: string
  value: string
  change: string
}

interface ActivityItem {
  type: string
  action: string
  name: string
  time: string
}

const stats = ref<StatItem[]>([
  {
    icon: Coin,
    iconColor: '#409eff',
    label: '数据集',
    value: '156',
    change: '+12%',
  },
  {
    icon: Cpu,
    iconColor: '#409eff',
    label: '模型',
    value: '89',
    change: '+5%',
  },
  {
    icon: Monitor,
    iconColor: '#409eff',
    label: '部署实例',
    value: '34',
    change: '+8%',
  },
  {
    icon: User,
    iconColor: '#409eff',
    label: '活跃用户',
    value: '1,234',
    change: '+15%',
  },
])

const recentActivity = ref<ActivityItem[]>([
  { type: 'model', action: '部署了模型', name: 'ChatGLM-6B', time: '2 分钟前' },
  { type: 'data', action: '上传了数据集', name: '对话数据集v2', time: '5 分钟前' },
  { type: 'finetune', action: '开始微调', name: 'BERT-Base', time: '10 分钟前' },
  { type: 'knowledge', action: '同步知识库', name: '产品文档', time: '15 分钟前' },
])
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.title-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.title-section h1 {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.real-time-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
}

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info .stat-label {
  color: #909399;
  font-size: 14px;
  margin: 0 0 4px 0;
}

.stat-info .stat-value {
  color: #303133;
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.stat-icon {
  font-size: 32px;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
}

.trend-icon {
  color: #67c23a;
}

.change-value {
  color: #67c23a;
  font-size: 14px;
  font-weight: 500;
}

.change-period {
  color: #909399;
  font-size: 14px;
}

.main-content {
  margin-bottom: 24px;
}

.chart-card,
.activity-card {
  height: 400px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-placeholder {
  height: 280px;
  background-color: #f5f7fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 280px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.activity-avatar {
  width: 32px;
  height: 32px;
  background-color: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #303133;
}

.activity-name {
  color: #409eff;
  font-weight: 500;
}

.activity-time {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.quick-actions-card .card-title {
  margin-bottom: 16px;
}

.quick-action-btn {
  width: 100%;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }

  .title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .chart-card,
  .activity-card {
    height: auto;
    margin-bottom: 16px;
  }

  .chart-placeholder {
    height: 200px;
  }

  .activity-list {
    height: auto;
    max-height: 300px;
  }
}
</style>
