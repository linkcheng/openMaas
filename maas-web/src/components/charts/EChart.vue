<template>
  <div ref="chartContainer" :style="{ width: '100%', height: height }" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'

interface Props {
  option: EChartsOption
  height?: string
  width?: string
  theme?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '300px',
  width: '100%',
  theme: 'default'
})

const chartContainer = ref<HTMLElement>()
let chart: ECharts | null = null
let resizeHandler: (() => void) | null = null

// 初始化图表
const initChart = async () => {
  if (!chartContainer.value) return

  await nextTick()
  
  // 销毁已存在的图表实例
  if (chart) {
    chart.dispose()
    chart = null
  }

  // 创建新的图表实例
  chart = echarts.init(chartContainer.value, props.theme)
  chart.setOption(props.option, true)

  // 监听窗口大小变化
  resizeHandler = () => {
    chart?.resize()
  }
  window.addEventListener('resize', resizeHandler)
}

// 更新图表配置
const updateChart = () => {
  if (chart && props.option) {
    chart.setOption(props.option, true)
  }
}

// 监听option变化
watch(
  () => props.option,
  () => {
    updateChart()
  },
  { deep: true }
)

// 监听主题变化
watch(
  () => props.theme,
  () => {
    initChart()
  }
)

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chart) {
    // 移除resize监听器
    if (resizeHandler) {
      window.removeEventListener('resize', resizeHandler)
    }
    chart.dispose()
    chart = null
  }
})

// 暴露图表实例给父组件
defineExpose({
  chart,
  updateChart,
  initChart
})
</script>

<style scoped>
/* 确保图表容器有足够的尺寸 */
div {
  min-height: 200px;
}
</style>