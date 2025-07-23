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
  <div class="dashboard-charts">
    <div class="charts-header">
      <h3>{{ title }}</h3>
      <div class="charts-controls">
        <el-select v-model="selectedPeriod" @change="handlePeriodChange" size="small">
          <el-option label="最近7天" value="7days" />
          <el-option label="最近30天" value="30days" />
          <el-option label="最近3个月" value="3months" />
        </el-select>
        <el-button
          :icon="RefreshRight"
          :loading="loading"
          @click="refreshCharts"
          size="small"
          circle
        />
      </div>
    </div>

    <div class="charts-grid">
      <!-- 模型性能趋势图 -->
      <div class="chart-container">
        <div class="chart-header">
          <h4>模型性能趋势</h4>
          <el-tag size="small" type="success">实时监控</el-tag>
        </div>
        <div class="chart-placeholder" v-if="!hasModelData">
          <div class="placeholder-container">
            <div class="placeholder-chart-area">
              <div class="placeholder-bars">
                <div
                  class="bar"
                  v-for="i in 12"
                  :key="i"
                  :style="{ height: `${20 + Math.random() * 60}%` }"
                ></div>
              </div>
            </div>
            <div class="placeholder-text">
              <h4>模型性能图表</h4>
              <p>图表数据加载中 - 集成实际图表库后将显示详细性能趋势</p>
            </div>
          </div>
        </div>
        <component :is="chartComponent" v-else :data="modelPerformanceData" />
      </div>

      <!-- API调用统计 -->
      <div class="chart-container">
        <div class="chart-header">
          <h4>API调用统计</h4>
          <div class="chart-metrics">
            <span class="metric">
              <span class="metric-label">平均响应时间</span>
              <span class="metric-value">{{ averageResponseTime }}ms</span>
            </span>
          </div>
        </div>
        <div class="chart-content">
          <div class="mini-stats">
            <div class="mini-stat">
              <div class="mini-value">{{ formatNumber(totalCalls) }}</div>
              <div class="mini-label">总调用次数</div>
            </div>
            <div class="mini-stat">
              <div class="mini-value">{{ successRate }}%</div>
              <div class="mini-label">成功率</div>
            </div>
            <div class="mini-stat">
              <div class="mini-value">{{ formatNumber(errorCount) }}</div>
              <div class="mini-label">错误次数</div>
            </div>
          </div>
          <div class="trend-indicator">
            <el-progress
              :percentage="successRate"
              :color="getProgressColor(successRate)"
              :stroke-width="8"
              striped
              striped-flow
            />
          </div>
        </div>
      </div>

      <!-- 存储使用情况 -->
      <div class="chart-container">
        <div class="chart-header">
          <h4>存储使用情况</h4>
          <el-button type="primary" size="small" text>查看详情</el-button>
        </div>
        <div class="storage-overview">
          <div class="storage-stats">
            <div class="storage-item">
              <div class="storage-label">已使用</div>
              <div class="storage-value primary">{{ formatBytes(usedStorage) }}</div>
            </div>
            <div class="storage-item">
              <div class="storage-label">总容量</div>
              <div class="storage-value">{{ formatBytes(totalStorage) }}</div>
            </div>
            <div class="storage-item">
              <div class="storage-label">使用率</div>
              <div class="storage-value" :class="getUsageClass(storageUsagePercent)">
                {{ storageUsagePercent }}%
              </div>
            </div>
          </div>
          <div class="storage-progress">
            <el-progress
              :percentage="storageUsagePercent"
              :color="getStorageProgressColor(storageUsagePercent)"
              :stroke-width="12"
            />
          </div>
        </div>
      </div>

      <!-- 用户活跃度 -->
      <div class="chart-container">
        <div class="chart-header">
          <h4>用户活跃度</h4>
          <div class="activity-legend">
            <span class="legend-item active">
              <span class="legend-dot active"></span>
              活跃用户
            </span>
            <span class="legend-item">
              <span class="legend-dot"></span>
              总用户
            </span>
          </div>
        </div>
        <div class="activity-chart">
          <div class="activity-metrics">
            <div class="activity-metric">
              <div class="metric-number">{{ activeUsers }}</div>
              <div class="metric-label">今日活跃</div>
              <div class="metric-change positive">+{{ dailyGrowth }}%</div>
            </div>
            <div class="activity-metric">
              <div class="metric-number">{{ weeklyActiveUsers }}</div>
              <div class="metric-label">本周活跃</div>
              <div class="metric-change" :class="weeklyGrowth >= 0 ? 'positive' : 'negative'">
                {{ weeklyGrowth >= 0 ? '+' : '' }}{{ weeklyGrowth }}%
              </div>
            </div>
          </div>
          <div class="activity-bars">
            <div
              v-for="(day, index) in weeklyActivity"
              :key="index"
              class="activity-bar"
              :style="{ height: `${(day.active / day.total) * 100}%` }"
              :title="`${day.date}: ${day.active}/${day.total} 活跃`"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'

interface Props {
  title?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  // eslint-disable-line @typescript-eslint/no-unused-vars
  title: '数据分析',
  loading: false,
})

const emit = defineEmits<{
  periodChange: [period: string]
  refresh: []
}>()

// 数据状态
const selectedPeriod = ref('30days')
const hasModelData = ref(false)
const chartComponent = ref(null)

// 模拟数据
const totalCalls = ref(15420)
const successRate = ref(98.5)
const errorCount = ref(23)
const averageResponseTime = ref(245)

const usedStorage = ref(2.4 * 1024 * 1024 * 1024) // 2.4GB
const totalStorage = ref(10 * 1024 * 1024 * 1024) // 10GB
const storageUsagePercent = computed(() =>
  Math.round((usedStorage.value / totalStorage.value) * 100),
)

const activeUsers = ref(1234)
const weeklyActiveUsers = ref(5678)
const dailyGrowth = ref(15)
const weeklyGrowth = ref(8)

const weeklyActivity = ref([
  { date: '周一', active: 890, total: 1200 },
  { date: '周二', active: 950, total: 1250 },
  { date: '周三', active: 1020, total: 1300 },
  { date: '周四', active: 1100, total: 1350 },
  { date: '周五', active: 1250, total: 1400 },
  { date: '周六', active: 980, total: 1150 },
  { date: '周日', active: 850, total: 1100 },
])

const modelPerformanceData = ref({
  // 这里将来会连接实际的图表数据
})

// 方法
const handlePeriodChange = (period: string) => {
  emit('periodChange', period)
}

const refreshCharts = () => {
  emit('refresh')
}

const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('zh-CN').format(num)
}

const formatBytes = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)}${units[unitIndex]}`
}

const getProgressColor = (rate: number): string => {
  if (rate >= 95) return '#67c23a'
  if (rate >= 90) return '#e6a23c'
  return '#f56c6c'
}

const getStorageProgressColor = (percent: number): string => {
  if (percent < 70) return '#67c23a'
  if (percent < 85) return '#e6a23c'
  return '#f56c6c'
}

const getUsageClass = (percent: number): string => {
  if (percent < 70) return 'safe'
  if (percent < 85) return 'warning'
  return 'danger'
}

onMounted(() => {
  // 初始化图表数据
})
</script>

<style scoped>
.dashboard-charts {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.charts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.charts-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.charts-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.chart-container {
  background: var(--el-fill-color-extra-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 1.25rem;
  transition: all 0.3s ease;
}

.chart-container:hover {
  border-color: var(--el-color-primary-light-7);
  transform: translateY(-1px);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.chart-metrics {
  display: flex;
  gap: 1rem;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 0.75rem;
}

.metric-label {
  color: var(--el-text-color-secondary);
  margin-bottom: 0.25rem;
}

.metric-value {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* 图表占位符样式 */
.chart-placeholder {
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--el-fill-color-extra-light), var(--el-fill-color-light));
  border-radius: 8px;
  border: 1px dashed var(--el-border-color-light);
}

.placeholder-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 1.5rem;
  padding: 2rem;
}

.placeholder-chart-area {
  width: 100%;
  max-width: 300px;
  height: 120px;
  position: relative;
  background: var(--el-fill-color);
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  align-items: end;
  justify-content: center;
}

.placeholder-bars {
  display: flex;
  align-items: end;
  justify-content: space-between;
  height: 100%;
  width: 100%;
  gap: 0.25rem;
}

.bar {
  flex: 1;
  background: linear-gradient(180deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border-radius: 2px 2px 0 0;
  opacity: 0.7;
  animation: chart-pulse 2s infinite ease-in-out;
  min-height: 8px;
}

.bar:nth-child(even) {
  animation-delay: 0.5s;
}

.bar:nth-child(3n) {
  animation-delay: 1s;
}

.placeholder-text h4 {
  margin: 0 0 0.5rem 0;
  color: var(--el-text-color-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.placeholder-text p {
  margin: 0;
  color: var(--el-text-color-regular);
  font-size: 0.875rem;
  line-height: 1.5;
  max-width: 280px;
}

@keyframes chart-pulse {
  0%,
  100% {
    opacity: 0.7;
    transform: scaleY(1);
  }
  50% {
    opacity: 1;
    transform: scaleY(1.1);
  }
}

/* 迷你统计样式 */
.mini-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.mini-stat {
  text-align: center;
  flex: 1;
}

.mini-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--el-color-primary);
  margin-bottom: 0.25rem;
}

.mini-label {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.trend-indicator {
  margin-top: 1rem;
}

/* 存储概览样式 */
.storage-overview {
  padding: 0.5rem 0;
}

.storage-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.storage-item {
  text-align: center;
  flex: 1;
}

.storage-label {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.25rem;
}

.storage-value {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--el-text-color-primary);
}

.storage-value.primary {
  color: var(--el-color-primary);
  font-size: 1rem;
}

.storage-value.safe {
  color: var(--el-color-success);
}

.storage-value.warning {
  color: var(--el-color-warning);
}

.storage-value.danger {
  color: var(--el-color-danger);
}

.storage-progress {
  margin-top: 1rem;
}

/* 活跃度图表样式 */
.activity-legend {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--el-text-color-secondary);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--el-color-info-light-5);
}

.legend-dot.active {
  background: var(--el-color-primary);
}

.activity-chart {
  display: flex;
  justify-content: space-between;
  align-items: end;
  height: 140px;
}

.activity-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 60%;
}

.activity-metric {
  padding: 0.75rem;
  background: var(--el-fill-color-light);
  border-radius: 6px;
}

.metric-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--el-color-primary);
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.5rem;
}

.metric-change {
  font-size: 0.75rem;
  font-weight: 600;
}

.metric-change.positive {
  color: var(--el-color-success);
}

.metric-change.negative {
  color: var(--el-color-danger);
}

.activity-bars {
  display: flex;
  align-items: end;
  gap: 0.25rem;
  height: 100px;
  width: 35%;
}

.activity-bar {
  flex: 1;
  background: linear-gradient(180deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border-radius: 2px 2px 0 0;
  min-height: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.activity-bar:hover {
  opacity: 0.8;
  transform: scaleY(1.1);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .dashboard-charts {
    padding: 1rem;
  }

  .charts-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .chart-container {
    padding: 1rem;
  }

  .storage-stats {
    flex-direction: column;
    gap: 0.75rem;
  }

  .activity-chart {
    flex-direction: column;
    height: auto;
    gap: 1rem;
  }

  .activity-metrics {
    width: 100%;
    flex-direction: row;
  }

  .activity-bars {
    width: 100%;
    height: 60px;
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .chart-container {
    background: var(--el-fill-color);
  }

  .activity-metric {
    background: var(--el-fill-color-darker);
  }
}
</style>
