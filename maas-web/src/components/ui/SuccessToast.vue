<template>
  <Teleport to="body">
    <Transition name="toast" @enter="onEnter" @leave="onLeave">
      <div
        v-if="visible"
        class="success-toast"
        :class="[`position-${position}`, `variant-${variant}`]"
        role="status"
        aria-live="polite"
        @mouseenter="pauseAutoHide"
        @mouseleave="resumeAutoHide"
      >
        <div class="toast-icon">
          <slot name="icon">
            <svg
              class="default-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22,4 12,14.01 9,11.01" />
            </svg>
          </slot>
        </div>

        <div class="toast-content">
          <h4 v-if="title" class="toast-title">{{ title }}</h4>
          <div class="toast-message">
            <slot>{{ message }}</slot>
          </div>
        </div>

        <button
          v-if="dismissible"
          type="button"
          class="dismiss-button"
          :aria-label="dismissAriaLabel"
          @click="handleDismiss"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        <!-- Progress bar for auto-hide -->
        <div v-if="showProgress && autoHide" class="progress-bar">
          <div class="progress-fill" :style="{ animationDuration: `${autoHideDelay}ms` }"></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  message?: string
  title?: string
  variant?: 'success' | 'info' | 'warning'
  position?:
    | 'top-right'
    | 'top-left'
    | 'bottom-right'
    | 'bottom-left'
    | 'top-center'
    | 'bottom-center'
  dismissible?: boolean
  autoHide?: boolean
  autoHideDelay?: number
  showProgress?: boolean
  dismissAriaLabel?: string
  modelValue?: boolean
}

interface Emits {
  (e: 'dismiss'): void
  (e: 'update:modelValue', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'success',
  position: 'top-right',
  dismissible: true,
  autoHide: true,
  autoHideDelay: 4000,
  showProgress: true,
  dismissAriaLabel: '关闭提示',
})

const emit = defineEmits<Emits>()

const visible = ref(props.modelValue !== undefined ? props.modelValue : true)
let autoHideTimer: number | null = null
const remainingTime = ref(props.autoHideDelay)
let pausedAt: number | null = null

// Handle dismiss
const handleDismiss = () => {
  visible.value = false
  emit('dismiss')
  emit('update:modelValue', false)
  stopAutoHide()
}

// Auto hide functionality
const startAutoHide = () => {
  if (props.autoHide && remainingTime.value > 0) {
    autoHideTimer = window.setTimeout(() => {
      handleDismiss()
    }, remainingTime.value)
  }
}

const stopAutoHide = () => {
  if (autoHideTimer) {
    clearTimeout(autoHideTimer)
    autoHideTimer = null
  }
}

const pauseAutoHide = () => {
  if (autoHideTimer && props.autoHide) {
    stopAutoHide()
    pausedAt = Date.now()
  }
}

const resumeAutoHide = () => {
  if (pausedAt && props.autoHide) {
    const elapsed = Date.now() - pausedAt
    remainingTime.value = Math.max(0, remainingTime.value - elapsed)
    pausedAt = null
    startAutoHide()
  }
}

// Transition handlers
const onEnter = (el: Element) => {
  // Force reflow to ensure animation works
  el.offsetHeight
}

const onLeave = (el: Element) => {
  // Clean up any remaining timers
  stopAutoHide()
}

// Watch for visibility changes
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== undefined) {
      visible.value = newValue
      if (newValue) {
        remainingTime.value = props.autoHideDelay
        startAutoHide()
      } else {
        stopAutoHide()
      }
    }
  },
)

// Watch for visible changes
watch(
  visible,
  (newValue) => {
    if (newValue) {
      remainingTime.value = props.autoHideDelay
      startAutoHide()
    } else {
      stopAutoHide()
    }
  },
  { immediate: true },
)

// Cleanup on unmount
onUnmounted(() => {
  stopAutoHide()
})
</script>

<style scoped>
.success-toast {
  position: fixed;
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  min-width: 300px;
  max-width: 400px;
  padding: var(--space-md);
  background: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.toast-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.default-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.toast-message {
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.dismiss-button {
  flex-shrink: 0;
  padding: var(--space-xs);
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: calc(-1 * var(--space-xs));
  margin-right: calc(-1 * var(--space-xs));
  color: var(--color-text-tertiary);
}

.dismiss-button:hover {
  background-color: var(--color-background-soft);
  color: var(--color-text-secondary);
  transform: scale(1.1);
}

.dismiss-button:focus {
  outline: none;
  background-color: var(--color-background-mute);
  box-shadow: 0 0 0 2px var(--maas-primary-500);
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: currentColor;
  width: 100%;
  animation: progress linear;
  transform-origin: left;
}

/* Position variants */
.position-top-right {
  top: 1rem;
  right: 1rem;
}

.position-top-left {
  top: 1rem;
  left: 1rem;
}

.position-bottom-right {
  bottom: 1rem;
  right: 1rem;
}

.position-bottom-left {
  bottom: 1rem;
  left: 1rem;
}

.position-top-center {
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
}

.position-bottom-center {
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
}

/* Variant styles */
.variant-success {
  border-left: 4px solid var(--maas-success);
}

.variant-success .toast-icon {
  color: var(--maas-success);
}

.variant-success .progress-fill {
  background-color: var(--maas-success);
}

.variant-info {
  border-left: 4px solid var(--maas-info);
}

.variant-info .toast-icon {
  color: var(--maas-info);
}

.variant-info .progress-fill {
  background-color: var(--maas-info);
}

.variant-warning {
  border-left: 4px solid var(--maas-warning);
}

.variant-warning .toast-icon {
  color: var(--maas-warning);
}

.variant-warning .progress-fill {
  background-color: var(--maas-warning);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .success-toast {
    background: #1f2937;
    border-color: #374151;
    color: #f9fafb;
  }

  .dismiss-button {
    color: #9ca3af;
  }

  .dismiss-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #f3f4f6;
  }

  .progress-bar {
    background-color: rgba(255, 255, 255, 0.1);
  }
}

/* Responsive design */
@media (max-width: 640px) {
  .success-toast {
    min-width: 280px;
    max-width: calc(100vw - 2rem);
    margin: 0 1rem;
  }

  .position-top-center,
  .position-bottom-center {
    left: 1rem;
    right: 1rem;
    transform: none;
    max-width: none;
  }
}

/* Animations */
@keyframes progress {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

/* Toast transitions */
.toast-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

/* Position-specific transitions */
.position-top-left .toast-enter-from,
.position-bottom-left .toast-leave-to {
  transform: translateX(-100%) scale(0.95);
}

.position-top-center .toast-enter-from,
.position-top-center .toast-leave-to {
  transform: translateY(-100%) translateX(-50%) scale(0.95);
}

.position-bottom-center .toast-enter-from,
.position-bottom-center .toast-leave-to {
  transform: translateY(100%) translateX(-50%) scale(0.95);
}

.position-bottom-right .toast-enter-from,
.position-bottom-right .toast-leave-to,
.position-bottom-left .toast-enter-from,
.position-bottom-left .toast-leave-to {
  transform: translateY(100%) scale(0.95);
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .toast-enter-active,
  .toast-leave-active {
    transition: opacity 0.2s ease;
  }

  .toast-enter-from,
  .toast-leave-to {
    transform: none;
  }

  .progress-fill {
    animation: none;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .success-toast {
    border-width: 2px;
  }
}
</style>
