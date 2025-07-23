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
  <div class="activity-log">
    <div class="activity-header">
      <h3>{{ title }}</h3>
      <div class="activity-controls">
        <el-select v-model="selectedFilter" @change="handleFilterChange" size="small">
          <el-option label="全部活动" value="all" />
          <el-option label="API调用" value="api_call" />
          <el-option label="用户登录" value="login" />
          <el-option label="系统事件" value="system" />
        </el-select>
        <el-button
          :icon="RefreshRight"
          :loading="loading"
          @click="refreshActivities"
          size="small"
          circle
        />
      </div>
    </div>

    <div class="activity-timeline" v-if="filteredActivities.length > 0">
      <div
        v-for="activity in filteredActivities"
        :key="activity.id"
        class="activity-item"
        :class="{ 'activity-error': activity.status === 'error' }"
      >
        <div class="activity-timeline-marker">
          <div class="activity-icon" :class="getActivityStatusClass(activity.status)">
            <component
              :is="getActivityIconComponent(activity.type)"
              v-if="getActivityIconComponent(activity.type)"
            />
            <span v-else>{{ getActivityIcon(activity.type) }}</span>
          </div>
          <div class="timeline-line" v-if="!isLastActivity(activity.id)"></div>
        </div>

        <div class="activity-content">
          <div class="activity-main">
            <div class="activity-info">
              <h4 class="activity-title">{{ activity.description }}</h4>
              <div class="activity-meta">
                <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
                <span class="activity-separator">•</span>
                <span class="activity-type">{{ getActivityTypeText(activity.type) }}</span>
                <el-tag v-if="activity.user" size="small" type="info" effect="plain">
                  {{ activity.user }}
                </el-tag>
              </div>
              <p v-if="activity.details" class="activity-details">{{ activity.details }}</p>
            </div>

            <div class="activity-status">
              <el-tag
                :type="getStatusTagType(activity.status)"
                size="small"
                :effect="activity.status === 'error' ? 'dark' : 'light'"
              >
                {{ getStatusText(activity.status) }}
              </el-tag>
            </div>
          </div>

          <div v-if="activity.metadata" class="activity-metadata">
            <div class="metadata-item" v-for="(value, key) in activity.metadata" :key="key">
              <span class="metadata-key">{{ key }}:</span>
              <span class="metadata-value">{{ value }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="loading" class="activity-loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else class="activity-empty">
      <el-empty :description="getEmptyDescription()">
        <template #image>
          <div class="empty-icon">📋</div>
        </template>
        <el-button type="primary" @click="refreshActivities">刷新活动</el-button>
      </el-empty>
    </div>

    <!-- 查看更多 -->
    <div v-if="hasMore && filteredActivities.length > 0" class="activity-footer">
      <el-button type="primary" text @click="loadMore" :loading="loadingMore">
        查看更多活动
      </el-button>
      <span class="activity-count"
        >显示 {{ filteredActivities.length }} / {{ totalCount }} 条记录</span
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  RefreshRight,
  Link,
  UserFilled,
  Key,
  Warning,
  Monitor,
  Upload,
  Position,
} from '@element-plus/icons-vue'

interface ActivityItem {
  id: string
  type: string
  description: string
  details?: string
  timestamp: string
  status: 'success' | 'warning' | 'error'
  user?: string
  metadata?: Record<string, any> // eslint-disable-line @typescript-eslint/no-explicit-any
}

interface Props {
  title?: string
  activities: ActivityItem[]
  loading?: boolean
  hasMore?: boolean
  totalCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '最近活动',
  loading: false,
  hasMore: false,
  totalCount: 0,
})

const emit = defineEmits<{
  refresh: []
  loadMore: []
  filterChange: [filter: string]
}>()

// 状态
const selectedFilter = ref('all')
const loadingMore = ref(false)

// 计算属性
const filteredActivities = computed(() => {
  if (selectedFilter.value === 'all') {
    return props.activities
  }
  return props.activities.filter((activity) => activity.type === selectedFilter.value)
})

// 方法
const handleFilterChange = (filter: string) => {
  emit('filterChange', filter)
}

const refreshActivities = () => {
  emit('refresh')
}

const loadMore = () => {
  loadingMore.value = true
  emit('loadMore')
  // 这里应该在父组件的响应中设置 loadingMore.value = false
}

const isLastActivity = (id: string): boolean => {
  const index = filteredActivities.value.findIndex((activity) => activity.id === id)
  return index === filteredActivities.value.length - 1
}

const getActivityIcon = (type: string): string => {
  const icons: Record<string, string> = {
    api_call: '🔗',
    login: '🔐',
    user_register: '👤',
    system_warning: '⚠️',
    api_key_created: '🔑',
    model_upload: '🤖',
    deployment: '🚀',
    system_event: '🖥️',
    default: '📋',
  }
  return icons[type] || icons.default
}

const getActivityIconComponent = (type: string) => {
  const componentMap: Record<string, any> = {
     
    api_call: Link,
    login: UserFilled,
    api_key_created: Key,
    system_warning: Warning,
    model_upload: Upload,
    deployment: Position,
    system_event: Monitor,
  }
  return componentMap[type]
}

const getActivityStatusClass = (status: string): string => {
  return `status-${status}`
}

const getActivityTypeText = (type: string): string => {
  const typeTexts: Record<string, string> = {
    api_call: 'API调用',
    login: '用户登录',
    user_register: '用户注册',
    system_warning: '系统警告',
    api_key_created: 'API密钥',
    model_upload: '模型上传',
    deployment: '部署应用',
    system_event: '系统事件',
  }
  return typeTexts[type] || '未知类型'
}

const getStatusTagType = (status: string): string => {
  const typeMap: Record<string, string> = {
    success: 'success',
    warning: 'warning',
    error: 'danger',
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string): string => {
  const statusTexts: Record<string, string> = {
    success: '成功',
    warning: '警告',
    error: '失败',
  }
  return statusTexts[status] || '未知'
}

const getEmptyDescription = (): string => {
  if (selectedFilter.value === 'all') {
    return '暂无活动记录'
  }
  return `暂无 ${getActivityTypeText(selectedFilter.value)} 记录`
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
  if (diffDays < 7) return `${diffDays}天前`

  return time.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 暴露方法给父组件
defineExpose({
  setLoadingMore: (loading: boolean) => {
    loadingMore.value = loading
  },
})
</script>

<style scoped>
.activity-log {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.activity-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.activity-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.activity-timeline {
  position: relative;
}

.activity-item {
  display: flex;
  gap: 1rem;
  position: relative;
  padding-bottom: 1.5rem;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: var(--el-fill-color-extra-light);
  margin: 0 -0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
}

.activity-item.activity-error {
  background: var(--el-color-danger-light-9);
  border-left: 3px solid var(--el-color-danger);
  padding-left: 1rem;
  margin-left: -1rem;
  border-radius: 0 8px 8px 0;
}

.activity-timeline-marker {
  position: relative;
  flex-shrink: 0;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  font-weight: 500;
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
}

.activity-icon.status-success {
  background: var(--el-color-success-light-9);
  color: var(--el-color-success);
  border: 2px solid var(--el-color-success-light-7);
}

.activity-icon.status-warning {
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning);
  border: 2px solid var(--el-color-warning-light-7);
}

.activity-icon.status-error {
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
  border: 2px solid var(--el-color-danger-light-7);
}

.timeline-line {
  position: absolute;
  left: 50%;
  top: 40px;
  width: 2px;
  height: calc(100% + 1.5rem);
  background: var(--el-border-color-light);
  transform: translateX(-50%);
  z-index: 1;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.activity-info {
  flex: 1;
  min-width: 0;
}

.activity-title {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.activity-time {
  font-weight: 500;
}

.activity-separator {
  color: var(--el-text-color-disabled);
}

.activity-type {
  background: var(--el-fill-color-light);
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-weight: 500;
}

.activity-details {
  margin: 0.5rem 0 0 0;
  font-size: 0.75rem;
  color: var(--el-text-color-regular);
  line-height: 1.4;
  background: var(--el-fill-color-extra-light);
  padding: 0.5rem;
  border-radius: 4px;
  border-left: 3px solid var(--el-color-primary-light-7);
}

.activity-status {
  flex-shrink: 0;
}

.activity-metadata {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: var(--el-fill-color-extra-light);
  border-radius: 6px;
  font-size: 0.75rem;
}

.metadata-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.metadata-item:last-child {
  margin-bottom: 0;
}

.metadata-key {
  color: var(--el-text-color-secondary);
  min-width: 80px;
  font-weight: 500;
}

.metadata-value {
  color: var(--el-text-color-primary);
  word-break: break-all;
}

.activity-loading {
  padding: 1rem 0;
}

.activity-empty {
  padding: 2rem 0;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.activity-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: 1rem;
}

.activity-count {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .activity-log {
    padding: 1rem;
  }

  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .activity-controls {
    width: 100%;
    justify-content: space-between;
  }

  .activity-item {
    gap: 0.75rem;
  }

  .activity-main {
    flex-direction: column;
    gap: 0.75rem;
  }

  .activity-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .activity-footer {
    flex-direction: column;
    gap: 0.75rem;
    text-align: center;
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .activity-item:hover {
    background: var(--el-fill-color);
  }

  .activity-metadata {
    background: var(--el-fill-color);
  }

  .activity-details {
    background: var(--el-fill-color);
  }
}
</style>
