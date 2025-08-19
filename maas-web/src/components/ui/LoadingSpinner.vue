<template>
  <div
    class="loading-spinner"
    :class="[`size-${size}`, `variant-${variant}`]"
    role="status"
    :aria-label="ariaLabel"
  >
    <svg class="spinner-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle class="spinner-track" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" />
      <circle
        class="spinner-fill"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-dasharray="62.83"
        stroke-dashoffset="62.83"
      />
    </svg>

    <span v-if="text" class="loading-text">{{ text }}</span>
    <span v-else class="sr-only">{{ ariaLabel }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'primary' | 'secondary' | 'white' | 'current'
  text?: string
  ariaLabel?: string
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  variant: 'primary',
  ariaLabel: '加载中...',
})
</script>

<style scoped>
.loading-spinner {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
}

.spinner-svg {
  animation: spin 1s linear infinite;
}

.spinner-track {
  opacity: 0.2;
}

.spinner-fill {
  animation: dash 1.5s ease-in-out infinite;
}

/* Size variants */
.size-xs .spinner-svg {
  width: 1rem;
  height: 1rem;
}

.size-sm .spinner-svg {
  width: 1.25rem;
  height: 1.25rem;
}

.size-md .spinner-svg {
  width: 1.5rem;
  height: 1.5rem;
}

.size-lg .spinner-svg {
  width: 2rem;
  height: 2rem;
}

.size-xl .spinner-svg {
  width: 2.5rem;
  height: 2.5rem;
}

/* Color variants */
.variant-primary {
  color: var(--maas-primary-600);
}

.variant-secondary {
  color: var(--color-text-secondary);
}

.variant-white {
  color: var(--maas-white);
}

.variant-current {
  color: currentColor;
}

/* Text styling */
.loading-text {
  font-size: 0.875rem;
  color: currentColor;
  font-weight: 500;
}

.size-xs .loading-text {
  font-size: 0.75rem;
}

.size-sm .loading-text {
  font-size: 0.8125rem;
}

.size-lg .loading-text {
  font-size: 1rem;
}

.size-xl .loading-text {
  font-size: 1.125rem;
}

/* Screen reader only text */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Animations */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .spinner-svg {
    animation: none;
  }

  .spinner-fill {
    animation: none;
    stroke-dasharray: none;
    stroke-dashoffset: 0;
    opacity: 0.8;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .spinner-track {
    opacity: 0.4;
  }

  .spinner-fill {
    opacity: 1;
  }
}
</style>
