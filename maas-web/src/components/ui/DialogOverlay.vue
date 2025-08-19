<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="dialog-overlay"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="ariaLabelledby"
      :aria-describedby="ariaDescribedby"
      @click="handleOverlayClick"
      @keydown="handleKeydown"
    >
      <div ref="dialogRef" class="dialog-container" tabindex="-1" @click.stop>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useFocusTrap } from '@/composables/useKeyboardNavigation'

interface Props {
  modelValue: boolean
  closeOnOverlayClick?: boolean
  closeOnEscape?: boolean
  ariaLabelledby?: string
  ariaDescribedby?: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  closeOnOverlayClick: true,
  closeOnEscape: true,
})

const emit = defineEmits<Emits>()

const dialogRef = ref<HTMLElement>()
const { trapRef, activate, deactivate } = useFocusTrap()

// Set trap ref to dialog ref
watch(dialogRef, (newRef) => {
  trapRef.value = newRef
})

// Handle overlay click
const handleOverlayClick = () => {
  if (props.closeOnOverlayClick) {
    closeDialog()
  }
}

// Handle keyboard events
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.closeOnEscape) {
    closeDialog()
  }
  // Focus trap handles Tab navigation automatically
}

// Close dialog
const closeDialog = () => {
  emit('update:modelValue', false)
  emit('close')
}

// Watch for dialog open/close
watch(
  () => props.modelValue,
  async (isOpen) => {
    if (isOpen) {
      // Prevent body scroll
      document.body.style.overflow = 'hidden'

      // Activate focus trap
      await nextTick()
      activate()
    } else {
      // Restore body scroll
      document.body.style.overflow = ''

      // Deactivate focus trap
      deactivate()
    }
  },
)

// Cleanup on unmount
onUnmounted(() => {
  if (props.modelValue) {
    document.body.style.overflow = ''
    deactivate()
  }
})
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-md);
  backdrop-filter: blur(4px);
}

.dialog-container {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
  outline: none;
  color: var(--color-text-primary);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .dialog-overlay {
    background-color: rgba(0, 0, 0, 0.7);
  }
}

.dark .dialog-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

/* Animation */
.dialog-overlay {
  animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dialog-container {
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 退出动画 */
.dialog-overlay.dialog-leaving {
  animation: fadeOut 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.dialog-overlay.dialog-leaving .dialog-container {
  animation: slideOut 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes slideOut {
  from {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
  to {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .dialog-overlay {
    background-color: rgba(0, 0, 0, 0.8);
  }

  .dialog-container {
    border: 2px solid currentColor;
  }
}
</style>
