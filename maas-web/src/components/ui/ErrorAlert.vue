<template>
  <div
    v-if="visible"
    class="error-alert"
    :class="[`variant-${variant}`, { dismissible: dismissible }]"
    role="alert"
    aria-live="assertive"
  >
    <div class="alert-icon">
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
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
      </slot>
    </div>

    <div class="alert-content">
      <h4 v-if="title" class="alert-title">{{ title }}</h4>
      <div class="alert-message">
        <slot>{{ message }}</slot>
      </div>

      <div v-if="$slots.actions || retryText" class="alert-actions">
        <slot name="actions">
          <button v-if="retryText" type="button" class="retry-button" @click="handleRetry">
            {{ retryText }}
          </button>
        </slot>
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  message?: string
  title?: string
  variant?: 'error' | 'warning' | 'info'
  dismissible?: boolean
  autoHide?: boolean
  autoHideDelay?: number
  retryText?: string
  dismissAriaLabel?: string
  modelValue?: boolean
}

interface Emits {
  (e: 'dismiss'): void
  (e: 'retry'): void
  (e: 'update:modelValue', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'error',
  dismissible: true,
  autoHide: false,
  autoHideDelay: 5000,
  dismissAriaLabel: '关闭提示',
})

const emit = defineEmits<Emits>()

const visible = ref(props.modelValue !== undefined ? props.modelValue : true)
let autoHideTimer: number | null = null

// Handle dismiss
const handleDismiss = () => {
  visible.value = false
  emit('dismiss')
  emit('update:modelValue', false)

  if (autoHideTimer) {
    clearTimeout(autoHideTimer)
    autoHideTimer = null
  }
}

// Handle retry
const handleRetry = () => {
  emit('retry')
}

// Auto hide functionality
const startAutoHide = () => {
  if (props.autoHide && props.autoHideDelay > 0) {
    autoHideTimer = window.setTimeout(() => {
      handleDismiss()
    }, props.autoHideDelay)
  }
}

const stopAutoHide = () => {
  if (autoHideTimer) {
    clearTimeout(autoHideTimer)
    autoHideTimer = null
  }
}

// Watch for visibility changes
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== undefined) {
      visible.value = newValue
      if (newValue) {
        startAutoHide()
      } else {
        stopAutoHide()
      }
    }
  },
)

// Watch for visible changes to start/stop auto hide
watch(
  visible,
  (newValue) => {
    if (newValue) {
      startAutoHide()
    } else {
      stopAutoHide()
    }
  },
  { immediate: true },
)

// Cleanup on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  stopAutoHide()
})
</script>

<style scoped>
.error-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid;
  animation: slideIn 0.3s ease-out;
}

.alert-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.default-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.alert-message {
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.alert-actions {
  margin-top: 0.75rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.retry-button {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
}

.retry-button:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.dismiss-button {
  flex-shrink: 0;
  padding: 0.25rem;
  background: none;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: -0.125rem;
  margin-right: -0.25rem;
}

.dismiss-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.dismiss-button:focus {
  outline: none;
  background-color: rgba(0, 0, 0, 0.1);
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

/* Variant styles */
.variant-error {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.variant-error .alert-icon {
  color: #dc2626;
}

.variant-error .retry-button {
  color: #991b1b;
  border-color: #fca5a5;
}

.variant-error .retry-button:hover {
  background-color: #fee2e2;
  border-color: #f87171;
}

.variant-error .dismiss-button {
  color: #991b1b;
}

.variant-warning {
  background-color: #fffbeb;
  border-color: #fed7aa;
  color: #92400e;
}

.variant-warning .alert-icon {
  color: #d97706;
}

.variant-warning .retry-button {
  color: #92400e;
  border-color: #fde68a;
}

.variant-warning .retry-button:hover {
  background-color: #fef3c7;
  border-color: #fbbf24;
}

.variant-warning .dismiss-button {
  color: #92400e;
}

.variant-info {
  background-color: #eff6ff;
  border-color: #bfdbfe;
  color: #1e40af;
}

.variant-info .alert-icon {
  color: #3b82f6;
}

.variant-info .retry-button {
  color: #1e40af;
  border-color: #93c5fd;
}

.variant-info .retry-button:hover {
  background-color: #dbeafe;
  border-color: #60a5fa;
}

.variant-info .dismiss-button {
  color: #1e40af;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .variant-error {
    background-color: #450a0a;
    border-color: #7f1d1d;
    color: #fca5a5;
  }

  .variant-error .alert-icon {
    color: #f87171;
  }

  .variant-warning {
    background-color: #451a03;
    border-color: #78350f;
    color: #fcd34d;
  }

  .variant-warning .alert-icon {
    color: #f59e0b;
  }

  .variant-info {
    background-color: #1e3a8a;
    border-color: #1d4ed8;
    color: #93c5fd;
  }

  .variant-info .alert-icon {
    color: #60a5fa;
  }

  .dismiss-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .dismiss-button:focus {
    background-color: rgba(255, 255, 255, 0.2);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .error-alert {
    border-width: 2px;
  }

  .retry-button {
    border-width: 2px;
  }
}

/* Responsive design */
@media (max-width: 640px) {
  .error-alert {
    padding: 0.875rem;
  }

  .alert-actions {
    flex-direction: column;
  }

  .retry-button {
    width: 100%;
    justify-content: center;
  }
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .error-alert {
    animation: none;
  }
}
</style>
