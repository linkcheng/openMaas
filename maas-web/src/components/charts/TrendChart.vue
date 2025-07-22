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
  <div class="trend-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-actions">
        <el-select
          v-model="selectedPeriod"
          size="small"
          @change="handlePeriodChange"
        >
          <el-option label="最近7天" value="7days" />
          <el-option label="最近30天" value="30days" />
          <el-option label="最近3个月" value="3months" />
        </el-select>
      </div>
    </div>
    <EChart :option="chartOption" :height="height" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import EChart from './EChart.vue'
import type { EChartsOption } from 'echarts'

interface Props {
  title: string
  data: Record<string, number>
  height?: string
  color?: string
  type?: 'line' | 'bar'
}

const props = withDefaults(defineProps<Props>(), {
  height: '350px',
  color: '#6366f1',
  type: 'line'
})

const emit = defineEmits<{
  periodChange: [period: string]
}>()

const selectedPeriod = ref('30days')

// 处理时间周期变化
const handlePeriodChange = (period: string) => {
  emit('periodChange', period)
}

// 计算图表配置
const chartOption = computed((): EChartsOption => {
  const dataEntries = Object.entries(props.data)
  const dates = dataEntries.map(([date]) => date)
  const values = dataEntries.map(([, value]) => value)

  const option: EChartsOption = {
    title: {
      show: false
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: props.color
        }
      },
      formatter: function(params: any) {
        if (Array.isArray(params) && params.length > 0) {
          const param = params[0]
          return `${param.axisValueLabel}<br/>${param.seriesName}: ${param.value}`
        }
        return ''
      }
    },
    legend: {
      show: false
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: props.type === 'bar',
      data: dates,
      axisLabel: {
        formatter: function(value: string) {
          // 格式化日期显示
          const date = new Date(value)
          return `${date.getMonth() + 1}/${date.getDate()}`
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: function(value: number) {
          if (value >= 1000) {
            return `${(value / 1000).toFixed(1)}k`
          }
          return value.toString()
        }
      }
    },
    series: [
      {
        name: props.title,
        type: props.type,
        smooth: props.type === 'line',
        data: values,
        itemStyle: {
          color: props.color
        },
        lineStyle: props.type === 'line' ? {
          color: props.color,
          width: 2
        } : undefined,
        areaStyle: props.type === 'line' ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: props.color + '40'
              },
              {
                offset: 1,
                color: props.color + '00'
              }
            ]
          }
        } : undefined
      }
    ]
  }

  return option
})

// 监听数据变化
watch(
  () => props.data,
  () => {
    // 数据更新时可以添加动画效果
  },
  { deep: true }
)
</script>

<style scoped>
.trend-chart {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 1rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.chart-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .chart-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>