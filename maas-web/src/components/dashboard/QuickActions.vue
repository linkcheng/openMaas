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
  <div class="quick-actions">
    <div class="actions-header">
      <h3>{{ title }}</h3>
      <el-button v-if="showViewAll" type="primary" text size="small" @click="handleViewAll">
        查看全部
      </el-button>
    </div>

    <div class="actions-grid">
      <div
        v-for="action in actions"
        :key="action.id"
        class="action-card"
        :class="{ 'action-disabled': action.disabled }"
        @click="handleActionClick(action)"
      >
        <div class="action-header">
          <div class="action-icon" :style="{ backgroundColor: action.color, color: 'white' }">
            <component :is="action.iconComponent" v-if="action.iconComponent" />
            <span v-else>{{ action.icon }}</span>
          </div>
          <el-tag
            v-if="action.badge"
            :type="action.badgeType || 'primary'"
            size="small"
            effect="dark"
          >
            {{ action.badge }}
          </el-tag>
        </div>

        <div class="action-content">
          <h4 class="action-title">{{ action.title }}</h4>
          <p class="action-description">{{ action.description }}</p>

          <div v-if="action.stats" class="action-stats">
            <div v-for="stat in action.stats" :key="stat.label" class="action-stat">
              <span class="stat-value">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>

        <div class="action-footer" v-if="action.showFooter !== false">
          <span class="action-shortcut" v-if="action.shortcut">{{ action.shortcut }}</span>
          <el-icon class="action-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 最近使用的操作 -->
    <div v-if="showRecentActions && recentActions.length > 0" class="recent-actions">
      <h4>最近使用</h4>
      <div class="recent-actions-list">
        <div
          v-for="action in recentActions"
          :key="action.id"
          class="recent-action-item"
          @click="handleActionClick(action)"
        >
          <div class="recent-icon" :style="{ backgroundColor: action.color }">
            <component :is="action.iconComponent" v-if="action.iconComponent" />
            <span v-else>{{ action.icon }}</span>
          </div>
          <div class="recent-content">
            <span class="recent-title">{{ action.title }}</span>
            <span class="recent-time">{{ action.lastUsed }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'

interface ActionStat {
  label: string
  value: string | number
}

interface QuickAction {
  id: string
  title: string
  description: string
  icon?: string
  iconComponent?: any // eslint-disable-line @typescript-eslint/no-explicit-any
  color: string
  disabled?: boolean
  badge?: string
  badgeType?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  shortcut?: string
  stats?: ActionStat[]
  showFooter?: boolean
  lastUsed?: string
  route?: string
  onClick?: () => void
}

interface Props {
  title?: string
  actions: QuickAction[]
  showViewAll?: boolean
  showRecentActions?: boolean
  recentActions?: QuickAction[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '快速操作',
  showViewAll: false,
  showRecentActions: false,
  recentActions: () => [],
})

const emit = defineEmits<{
  actionClick: [action: QuickAction]
  viewAll: []
}>()

const handleActionClick = (action: QuickAction) => {
  if (action.disabled) return

  if (action.onClick) {
    action.onClick()
  }

  emit('actionClick', action)
}

const handleViewAll = () => {
  emit('viewAll')
}
</script>

<style scoped>
.quick-actions {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.actions-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.action-card {
  background: var(--el-fill-color-extra-light);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.action-card:hover {
  background: var(--el-fill-color-light);
  border-color: var(--el-color-primary);
  transform: translateY(-3px);
  box-shadow: var(--el-box-shadow);
}

.action-card.action-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-card.action-disabled:hover {
  transform: none;
  box-shadow: none;
  border-color: var(--el-border-color-light);
}

.action-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 500;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
  margin-bottom: 1rem;
}

.action-title {
  margin: 0 0 0.5rem 0;
  color: var(--el-text-color-primary);
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.3;
}

.action-description {
  margin: 0 0 1rem 0;
  color: var(--el-text-color-regular);
  font-size: 0.875rem;
  line-height: 1.5;
}

.action-stats {
  display: flex;
  gap: 1.5rem;
}

.action-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  background: var(--el-fill-color);
  border-radius: 6px;
  flex: 1;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--el-color-primary);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
  text-align: center;
}

.action-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid var(--el-border-color-lighter);
}

.action-shortcut {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: monospace;
}

.action-arrow {
  color: var(--el-text-color-secondary);
  transition: all 0.3s ease;
}

.action-card:hover .action-arrow {
  color: var(--el-color-primary);
  transform: translateX(2px);
}

/* 最近使用的操作 */
.recent-actions {
  border-top: 1px solid var(--el-border-color-lighter);
  padding-top: 1.5rem;
}

.recent-actions h4 {
  margin: 0 0 1rem 0;
  color: var(--el-text-color-primary);
  font-size: 1rem;
  font-weight: 600;
}

.recent-actions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.recent-action-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--el-fill-color-extra-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.recent-action-item:hover {
  background: var(--el-fill-color-light);
  transform: translateX(4px);
}

.recent-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: white;
  flex-shrink: 0;
}

.recent-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.recent-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 0.125rem;
}

.recent-time {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quick-actions {
    padding: 1rem;
  }

  .actions-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .action-card {
    padding: 1.25rem;
  }

  .action-stats {
    flex-direction: column;
    gap: 0.75rem;
  }

  .action-stat {
    flex-direction: row;
    justify-content: space-between;
    padding: 0.75rem;
  }

  .recent-actions-list {
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .actions-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .action-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .action-footer {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .action-card {
    background: var(--el-fill-color);
  }

  .action-card:hover {
    background: var(--el-fill-color-light);
  }

  .action-stat {
    background: var(--el-fill-color-darker);
  }

  .recent-action-item {
    background: var(--el-fill-color);
  }

  .recent-action-item:hover {
    background: var(--el-fill-color-light);
  }
}
</style>
