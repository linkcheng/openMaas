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
  <div class="stat-card" :class="{ clickable: clickable }" @click="handleClick">
    <div class="stat-header">
      <div class="stat-icon" :style="{ backgroundColor: iconColor, color: iconTextColor }">
        <component :is="iconComponent" v-if="iconComponent" />
        <span v-else>{{ icon }}</span>
      </div>
      <div class="stat-trend" v-if="trend !== undefined" :class="trendClass">
        <el-icon class="trend-icon">
          <component :is="trend > 0 ? ArrowUp : ArrowDown" />
        </el-icon>
        <span class="trend-value">{{ Math.abs(trend) }}%</span>
      </div>
    </div>

    <div class="stat-content">
      <div class="stat-value" :style="{ color: valueColor }">
        {{ formattedValue }}
      </div>
      <div class="stat-label">{{ label }}</div>
      <div class="stat-subtitle" v-if="subtitle">{{ subtitle }}</div>
    </div>

    <div class="stat-footer" v-if="showFooter">
      <div class="stat-comparison" v-if="comparison">
        <span class="comparison-label">vs 上月</span>
        <span class="comparison-value" :class="comparisonClass">
          {{ comparison }}
        </span>
      </div>
      <div class="stat-action" v-if="actionText">
        <el-button type="primary" size="small" link>{{ actionText }}</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'

interface Props {
  // 基础数据
  value: number | string
  label: string
  subtitle?: string
  icon?: string
  iconComponent?: any // eslint-disable-line @typescript-eslint/no-explicit-any
  iconColor?: string
  iconTextColor?: string
  valueColor?: string

  // 趋势数据
  trend?: number
  comparison?: string

  // 格式化选项
  formatType?: 'number' | 'currency' | 'percentage' | 'bytes'
  precision?: number

  // 交互
  clickable?: boolean
  actionText?: string

  // 显示选项
  showFooter?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  formatType: 'number',
  precision: 0,
  iconColor: 'var(--el-fill-color-light)',
  iconTextColor: 'var(--el-text-color-primary)',
  valueColor: 'var(--el-color-primary)',
  clickable: false,
  showFooter: true,
})

const emit = defineEmits<{
  click: []
}>()

const formattedValue = computed(() => {
  const val = typeof props.value === 'string' ? parseFloat(props.value) || 0 : props.value

  switch (props.formatType) {
    case 'currency':
      return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: props.precision,
        maximumFractionDigits: props.precision,
      }).format(val)

    case 'percentage':
      return `${val.toFixed(props.precision)}%`

    case 'bytes':
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let size = val
      let unitIndex = 0
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
      }
      return `${size.toFixed(props.precision)}${units[unitIndex]}`

    default:
      return new Intl.NumberFormat('zh-CN', {
        minimumFractionDigits: props.precision,
        maximumFractionDigits: props.precision,
      }).format(val)
  }
})

const trendClass = computed(() => ({
  'trend-up': props.trend !== undefined && props.trend > 0,
  'trend-down': props.trend !== undefined && props.trend < 0,
  'trend-neutral': props.trend !== undefined && props.trend === 0,
}))

const comparisonClass = computed(() => {
  if (!props.comparison) return ''
  const isPositive = props.comparison.includes('+') || props.comparison.includes('增')
  return isPositive ? 'comparison-positive' : 'comparison-negative'
})

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.stat-card {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  box-shadow: var(--el-box-shadow);
  transform: translateY(-2px);
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  border-color: var(--el-color-primary);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  font-size: 1.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.25px;
  transition: all 0.3s ease;
}

.trend-icon {
  font-size: 0.875rem;
  transition: transform 0.3s ease;
}

.trend-value {
  font-size: 0.75rem;
  font-weight: 700;
}

.stat-trend.trend-up {
  background: linear-gradient(
    135deg,
    var(--el-color-success-light-9),
    var(--el-color-success-light-8)
  );
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success-light-7);
}

.stat-trend.trend-down {
  background: linear-gradient(
    135deg,
    var(--el-color-danger-light-9),
    var(--el-color-danger-light-8)
  );
  color: var(--el-color-danger);
  border: 1px solid var(--el-color-danger-light-7);
}

.stat-trend.trend-neutral {
  background: var(--el-color-info-light-9);
  color: var(--el-color-info);
  border: 1px solid var(--el-color-info-light-7);
}

.stat-card:hover .trend-icon {
  transform: translateY(-1px);
}

.stat-content {
  margin-bottom: 1rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 0.25rem;
  background: linear-gradient(135deg, currentColor, rgba(255, 255, 255, 0.8));
  -webkit-background-clip: text;
  background-clip: text;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--el-text-color-regular);
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.stat-subtitle {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.stat-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid var(--el-border-color-lighter);
}

.stat-comparison {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.comparison-label {
  color: var(--el-text-color-secondary);
}

.comparison-value {
  font-weight: 600;
}

.comparison-value.comparison-positive {
  color: var(--el-color-success);
}

.comparison-value.comparison-negative {
  color: var(--el-color-danger);
}

.stat-action {
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stat-card {
    padding: 1rem;
  }

  .stat-value {
    font-size: 1.75rem;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }

  .stat-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .stat-card {
    background: var(--el-bg-color-overlay);
    border-color: var(--el-border-color);
  }

  .stat-card:hover {
    background: var(--el-fill-color-extra-light);
  }
}
</style>
