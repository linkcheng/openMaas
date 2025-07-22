<template>
  <div class="pie-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
    </div>
    <EChart :option="chartOption" :height="height" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import EChart from './EChart.vue'
import type { EChartsOption } from 'echarts'

interface PieDataItem {
  name: string
  value: number
  color?: string
}

interface Props {
  title: string
  data: PieDataItem[]
  height?: string
  showLegend?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: '350px',
  showLegend: true
})

// 默认颜色调色板
const defaultColors = [
  '#6366f1', '#8b5cf6', '#06b6d4', '#10b981', 
  '#f59e0b', '#ef4444', '#ec4899', '#84cc16'
]

// 计算图表配置
const chartOption = computed((): EChartsOption => {
  const processedData = props.data.map((item, index) => ({
    ...item,
    itemStyle: {
      color: item.color || defaultColors[index % defaultColors.length]
    }
  }))

  const option: EChartsOption = {
    title: {
      show: false
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params: any) {
        return `${params.seriesName}<br/>${params.name}: ${params.value} (${params.percent}%)`
      }
    },
    legend: {
      show: props.showLegend,
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: {
        color: 'var(--el-text-color-primary)'
      }
    },
    series: [
      {
        name: props.title,
        type: 'pie',
        radius: props.showLegend ? ['40%', '70%'] : ['30%', '60%'],
        center: props.showLegend ? ['40%', '50%'] : ['50%', '50%'],
        data: processedData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: !props.showLegend,
          position: 'outside',
          formatter: '{b}: {c} ({d}%)',
          color: 'var(--el-text-color-primary)'
        },
        labelLine: {
          show: !props.showLegend
        }
      }
    ]
  }

  return option
})
</script>

<style scoped>
.pie-chart {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 1rem;
}

.chart-header {
  margin-bottom: 1rem;
}

.chart-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 1.1rem;
  font-weight: 600;
}
</style>