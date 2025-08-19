<template>
  <div class="empty-state" :class="[`size-${size}`]">
    <div class="empty-icon">
      <slot name="icon">
        <svg
          class="default-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="9" cy="9" r="2" />
          <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
        </svg>
      </slot>
    </div>

    <div class="empty-content">
      <h3 v-if="title" class="empty-title">{{ title }}</h3>
      <p v-if="description" class="empty-description">{{ description }}</p>

      <div v-if="$slots.default || actionText" class="empty-actions">
        <slot>
          <button v-if="actionText" type="button" class="empty-action-button" @click="handleAction">
            {{ actionText }}
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  description?: string
  actionText?: string
  size?: 'sm' | 'md' | 'lg'
}

interface Emits {
  (e: 'action'): void
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
})

const emit = defineEmits<Emits>()

const handleAction = () => {
  emit('action')
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
}

.empty-icon {
  margin-bottom: 1rem;
  color: #9ca3af;
}

.default-icon {
  width: 3rem;
  height: 3rem;
}

.empty-content {
  max-width: 28rem;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.empty-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 1.5rem 0;
  line-height: 1.5;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.empty-action-button {
  display: inline-flex;
  align-items: center;
  padding: 0.625rem 1.25rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition:
    background-color 0.2s,
    transform 0.1s;
}

.empty-action-button:hover {
  background-color: #2563eb;
}

.empty-action-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.empty-action-button:active {
  transform: translateY(1px);
}

/* Size variants */
.size-sm {
  padding: 1.5rem;
}

.size-sm .default-icon {
  width: 2.5rem;
  height: 2.5rem;
}

.size-sm .empty-title {
  font-size: 1rem;
}

.size-sm .empty-description {
  font-size: 0.8125rem;
}

.size-lg {
  padding: 3rem;
}

.size-lg .default-icon {
  width: 4rem;
  height: 4rem;
}

.size-lg .empty-title {
  font-size: 1.25rem;
}

.size-lg .empty-description {
  font-size: 1rem;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .empty-icon {
    color: #6b7280;
  }

  .empty-title {
    color: #f9fafb;
  }

  .empty-description {
    color: #9ca3af;
  }

  .empty-action-button {
    background-color: #3b82f6;
  }

  .empty-action-button:hover {
    background-color: #2563eb;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .empty-icon {
    color: currentColor;
  }

  .empty-action-button {
    border: 2px solid currentColor;
  }
}

/* Responsive design */
@media (max-width: 640px) {
  .empty-state {
    padding: 1.5rem 1rem;
  }

  .empty-content {
    max-width: 100%;
  }

  .empty-actions {
    flex-direction: column;
    align-items: center;
  }

  .empty-action-button {
    width: 100%;
    max-width: 200px;
  }
}

/* Animation for better UX */
.empty-state {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .empty-state {
    animation: none;
  }

  .empty-action-button:active {
    transform: none;
  }
}
</style>
