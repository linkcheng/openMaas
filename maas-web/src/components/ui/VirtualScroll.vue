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
  <div
    ref="containerRef"
    class="virtual-scroll-container"
    :style="{ height: `${containerHeight}px` }"
    @scroll="handleScroll"
  >
    <!-- 虚拟滚动区域 -->
    <div
      class="virtual-scroll-content"
      :style="{ height: `${totalHeight}px`, position: 'relative' }"
    >
      <!-- 渲染可见项 -->
      <div
        v-for="(item, index) in visibleItems"
        :key="getItemKey(item, startIndex + index)"
        :style="getItemStyle(index)"
        class="virtual-scroll-item"
      >
        <slot :item="item" :index="startIndex + index" :isVisible="true" />
      </div>
    </div>

    <!-- 滚动指示器 -->
    <div
      v-if="showScrollIndicator && totalHeight > containerHeight"
      class="scroll-indicator"
      :style="scrollIndicatorStyle"
    />
  </div>
</template>

<script setup lang="ts" generic="T">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useVirtualScroll, throttle } from '@/utils/performance'

interface Props {
  items: T[]
  itemHeight: number
  containerHeight: number
  buffer?: number
  showScrollIndicator?: boolean
  getItemKey?: (item: T, index: number) => string | number
}

const props = withDefaults(defineProps<Props>(), {
  buffer: 5,
  showScrollIndicator: true,
  getItemKey: (item: T, index: number) => index,
})

const emit = defineEmits<{
  scroll: [{ scrollTop: number; scrollLeft: number }]
  'scroll-end': []
  'scroll-start': []
}>()

const itemsRef = computed(() => ref(props.items))

const {
  containerRef,
  visibleItems,
  totalHeight,
  startIndex,
  endIndex,
  handleScroll: virtualHandleScroll,
  scrollToIndex,
  getItemStyle,
  updateVisibleItems,
} = useVirtualScroll(itemsRef, props.itemHeight, props.containerHeight, props.buffer)

// 滚动指示器样式
const scrollIndicatorStyle = computed(() => {
  if (!containerRef.value) return {}

  const scrollTop = containerRef.value.scrollTop
  const scrollHeight = totalHeight.value
  const clientHeight = props.containerHeight

  const indicatorHeight = Math.max(20, (clientHeight / scrollHeight) * clientHeight)
  const indicatorTop = (scrollTop / scrollHeight) * clientHeight

  return {
    height: `${indicatorHeight}px`,
    top: `${indicatorTop}px`,
  }
})

// 节流的滚动处理
const throttledScrollHandler = throttle((event: Event) => {
  virtualHandleScroll(event)

  const target = event.target as HTMLElement
  emit('scroll', {
    scrollTop: target.scrollTop,
    scrollLeft: target.scrollLeft,
  })

  // 检测滚动到顶部或底部
  if (target.scrollTop === 0) {
    emit('scroll-start')
  } else if (target.scrollTop + target.clientHeight >= target.scrollHeight - 1) {
    emit('scroll-end')
  }
}, 16) // 60fps

const handleScroll = (event: Event) => {
  throttledScrollHandler(event)
}

// 监听items变化，更新虚拟滚动
watch(
  () => props.items,
  () => {
    updateVisibleItems()
  },
  { deep: true },
)

// 监听容器高度变化
watch(
  () => props.containerHeight,
  () => {
    updateVisibleItems()
  },
)

// 监听项目高度变化
watch(
  () => props.itemHeight,
  () => {
    updateVisibleItems()
  },
)

// 暴露方法给父组件
defineExpose({
  scrollToIndex,
  scrollToTop: () => scrollToIndex(0),
  scrollToBottom: () => scrollToIndex(props.items.length - 1),
  getVisibleRange: () => ({ start: startIndex.value, end: endIndex.value }),
  updateVisibleItems,
})
</script>

<style scoped>
.virtual-scroll-container {
  overflow: auto;
  position: relative;
  width: 100%;
}

.virtual-scroll-content {
  width: 100%;
}

.virtual-scroll-item {
  width: 100%;
}

.scroll-indicator {
  position: absolute;
  right: 2px;
  width: 4px;
  background-color: var(--maas-primary-500);
  border-radius: 2px;
  opacity: 0.6;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.virtual-scroll-container:hover .scroll-indicator {
  opacity: 0.8;
}

/* 自定义滚动条样式 */
.virtual-scroll-container::-webkit-scrollbar {
  width: 8px;
}

.virtual-scroll-container::-webkit-scrollbar-track {
  background: var(--color-background-soft);
  border-radius: 4px;
}

.virtual-scroll-container::-webkit-scrollbar-thumb {
  background: var(--color-border-hover);
  border-radius: 4px;
}

.virtual-scroll-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* Firefox 滚动条样式 */
.virtual-scroll-container {
  scrollbar-width: thin;
  scrollbar-color: var(--color-border-hover) var(--color-background-soft);
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .scroll-indicator {
    transition: none;
  }
}
</style>
