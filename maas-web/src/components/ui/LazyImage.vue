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
  <div class="lazy-image" :class="{ loading: !isLoaded && !isError, error: isError }">
    <!-- 占位符 -->
    <div v-if="!isLoaded && !isError" class="placeholder">
      <div class="placeholder-content">
        <svg
          v-if="showPlaceholderIcon"
          class="placeholder-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
        >
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21,15 16,10 5,21" />
        </svg>
        <div v-if="showLoadingSpinner" class="loading-spinner">
          <div class="spinner"></div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="isError" class="error-state">
      <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span class="error-text">{{ errorText }}</span>
    </div>

    <!-- 实际图片 -->
    <img
      v-show="isLoaded"
      ref="imageRef"
      :alt="alt"
      :class="imageClass"
      @load="handleLoad"
      @error="handleError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useLazyImage } from '@/utils/performance'

interface Props {
  src: string
  alt: string
  placeholder?: string
  errorText?: string
  threshold?: number
  imageClass?: string
  showPlaceholderIcon?: boolean
  showLoadingSpinner?: boolean
  eager?: boolean // 是否立即加载，不使用懒加载
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '',
  errorText: '图片加载失败',
  threshold: 0.1,
  imageClass: '',
  showPlaceholderIcon: true,
  showLoadingSpinner: false,
  eager: false,
})

const emit = defineEmits<{
  load: [event: Event]
  error: [event: Event]
}>()

const { imageRef, isLoaded, isError, observe } = useLazyImage(props.threshold)

const handleLoad = (event: Event) => {
  emit('load', event)
}

const handleError = (event: Event) => {
  emit('error', event)
}

const startLoading = () => {
  if (props.eager) {
    // 立即加载
    if (imageRef.value) {
      imageRef.value.src = props.src
    }
  } else {
    // 懒加载
    observe(props.src)
  }
}

// 监听src变化，重新加载图片
watch(
  () => props.src,
  (newSrc) => {
    if (newSrc) {
      isLoaded.value = false
      isError.value = false
      startLoading()
    }
  },
  { immediate: true },
)

onMounted(() => {
  if (props.src) {
    startLoading()
  }
})
</script>

<style scoped>
.lazy-image {
  position: relative;
  display: inline-block;
  overflow: hidden;
  background-color: var(--color-background-soft);
  border-radius: var(--radius-sm);
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 120px;
  background-color: var(--color-background-soft);
  color: var(--color-text-secondary);
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}

.placeholder-icon {
  width: 2rem;
  height: 2rem;
  opacity: 0.5;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid var(--color-border);
  border-top: 2px solid var(--maas-primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 120px;
  background-color: var(--color-background-soft);
  color: var(--color-text-secondary);
  gap: var(--space-sm);
}

.error-icon {
  width: 2rem;
  height: 2rem;
  color: var(--color-error);
}

.error-text {
  font-size: 0.875rem;
  text-align: center;
}

img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

/* 加载状态动画 */
.loading .placeholder {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: none;
  }

  .loading .placeholder {
    animation: none;
  }

  img {
    transition: none;
  }
}
</style>
