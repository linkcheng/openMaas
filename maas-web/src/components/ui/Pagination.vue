<template>
  <nav class="pagination" :class="[`size-${size}`]" role="navigation" :aria-label="ariaLabel">
    <!-- Mobile pagination (simplified) -->
    <div class="pagination-mobile">
      <button
        type="button"
        class="pagination-button"
        :disabled="currentPage <= 1"
        :aria-label="prevAriaLabel"
        @click="goToPage(currentPage - 1)"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="15,18 9,12 15,6"></polyline>
        </svg>
        <span class="button-text">上一页</span>
      </button>

      <div class="page-info">
        <span class="current-page">{{ currentPage }}</span>
        <span class="page-separator">/</span>
        <span class="total-pages">{{ totalPages }}</span>
      </div>

      <button
        type="button"
        class="pagination-button"
        :disabled="currentPage >= totalPages"
        :aria-label="nextAriaLabel"
        @click="goToPage(currentPage + 1)"
      >
        <span class="button-text">下一页</span>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="9,18 15,12 9,6"></polyline>
        </svg>
      </button>
    </div>

    <!-- Desktop pagination (full) -->
    <div class="pagination-desktop">
      <!-- Previous button -->
      <button
        type="button"
        class="pagination-button prev-button"
        :disabled="currentPage <= 1"
        :aria-label="prevAriaLabel"
        @click="goToPage(currentPage - 1)"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="15,18 9,12 15,6"></polyline>
        </svg>
        <span v-if="showLabels" class="button-text">上一页</span>
      </button>

      <!-- Page numbers -->
      <div class="page-numbers">
        <!-- First page -->
        <button
          v-if="showFirstLast && currentPage > 3"
          type="button"
          class="page-button"
          :aria-label="`转到第 1 页`"
          @click="goToPage(1)"
        >
          1
        </button>

        <!-- First ellipsis -->
        <span v-if="showFirstLast && currentPage > 4" class="ellipsis" aria-hidden="true">
          ...
        </span>

        <!-- Visible page numbers -->
        <button
          v-for="page in visiblePages"
          :key="page"
          type="button"
          class="page-button"
          :class="{ active: page === currentPage }"
          :aria-label="`转到第 ${page} 页`"
          :aria-current="page === currentPage ? 'page' : undefined"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>

        <!-- Last ellipsis -->
        <span
          v-if="showFirstLast && currentPage < totalPages - 3"
          class="ellipsis"
          aria-hidden="true"
        >
          ...
        </span>

        <!-- Last page -->
        <button
          v-if="showFirstLast && currentPage < totalPages - 2"
          type="button"
          class="page-button"
          :aria-label="`转到第 ${totalPages} 页`"
          @click="goToPage(totalPages)"
        >
          {{ totalPages }}
        </button>
      </div>

      <!-- Next button -->
      <button
        type="button"
        class="pagination-button next-button"
        :disabled="currentPage >= totalPages"
        :aria-label="nextAriaLabel"
        @click="goToPage(currentPage + 1)"
      >
        <span v-if="showLabels" class="button-text">下一页</span>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="9,18 15,12 9,6"></polyline>
        </svg>
      </button>
    </div>

    <!-- Page size selector -->
    <div v-if="showPageSize" class="page-size-selector">
      <label :for="pageSizeId" class="page-size-label">每页显示</label>
      <select
        :id="pageSizeId"
        :value="pageSize"
        class="page-size-select"
        @change="handlePageSizeChange"
      >
        <option v-for="size in pageSizeOptions" :key="size" :value="size">
          {{ size }}
        </option>
      </select>
      <span class="page-size-suffix">条</span>
    </div>

    <!-- Jump to page -->
    <div v-if="showJumpTo" class="jump-to-page">
      <label :for="jumpToId" class="jump-to-label">跳转到</label>
      <input
        :id="jumpToId"
        ref="jumpToInput"
        v-model.number="jumpToValue"
        type="number"
        :min="1"
        :max="totalPages"
        class="jump-to-input"
        @keydown.enter="handleJumpTo"
        @blur="handleJumpTo"
      />
      <button type="button" class="jump-to-button" :disabled="!isValidJumpTo" @click="handleJumpTo">
        跳转
      </button>
    </div>

    <!-- Total info -->
    <div v-if="showTotal" class="total-info">
      <slot name="total" :total="total" :range="currentRange">
        显示第 {{ currentRange.start }} - {{ currentRange.end }} 条，共 {{ total }} 条
      </slot>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  currentPage: number
  totalPages: number
  total?: number
  pageSize?: number
  pageSizeOptions?: number[]
  showPageSize?: boolean
  showJumpTo?: boolean
  showTotal?: boolean
  showLabels?: boolean
  showFirstLast?: boolean
  size?: 'sm' | 'md' | 'lg'
  maxVisiblePages?: number
  ariaLabel?: string
  prevAriaLabel?: string
  nextAriaLabel?: string
}

interface Emits {
  (e: 'page-change', page: number): void
  (e: 'page-size-change', size: number): void
}

const props = withDefaults(defineProps<Props>(), {
  total: 0,
  pageSize: 10,
  pageSizeOptions: () => [10, 20, 50, 100],
  showPageSize: false,
  showJumpTo: false,
  showTotal: true,
  showLabels: true,
  showFirstLast: true,
  size: 'md',
  maxVisiblePages: 7,
  ariaLabel: '分页导航',
  prevAriaLabel: '上一页',
  nextAriaLabel: '下一页',
})

const emit = defineEmits<Emits>()

const jumpToValue = ref<number>(props.currentPage)
const jumpToInput = ref<HTMLInputElement>()

// Generate unique IDs
const pageSizeId = computed(() => `page-size-${Math.random().toString(36).substr(2, 9)}`)
const jumpToId = computed(() => `jump-to-${Math.random().toString(36).substr(2, 9)}`)

// Computed properties
const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = props.maxVisiblePages
  const current = props.currentPage
  const total = props.totalPages

  if (total <= maxVisible) {
    // Show all pages if total is less than max visible
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Calculate start and end of visible range
    let start = Math.max(1, current - Math.floor(maxVisible / 2))
    const end = Math.min(total, start + maxVisible - 1)

    // Adjust start if end is at the boundary
    if (end === total) {
      start = Math.max(1, end - maxVisible + 1)
    }

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
  }

  return pages
})

const currentRange = computed(() => {
  const start = (props.currentPage - 1) * props.pageSize + 1
  const end = Math.min(props.currentPage * props.pageSize, props.total)
  return { start, end }
})

const isValidJumpTo = computed(() => {
  return (
    jumpToValue.value >= 1 &&
    jumpToValue.value <= props.totalPages &&
    jumpToValue.value !== props.currentPage
  )
})

// Methods
const goToPage = (page: number) => {
  if (page >= 1 && page <= props.totalPages && page !== props.currentPage) {
    emit('page-change', page)
  }
}

const handlePageSizeChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const newSize = parseInt(target.value, 10)
  emit('page-size-change', newSize)
}

const handleJumpTo = () => {
  if (isValidJumpTo.value) {
    goToPage(jumpToValue.value)
  }
}

// Watch for current page changes to update jump to value
watch(
  () => props.currentPage,
  (newPage) => {
    jumpToValue.value = newPage
  },
)
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Mobile pagination */
.pagination-mobile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 1rem;
}

.pagination-desktop {
  display: none;
  align-items: center;
  gap: 0.5rem;
}

@media (min-width: 768px) {
  .pagination-mobile {
    display: none;
  }

  .pagination-desktop {
    display: flex;
  }
}

/* Buttons */
.pagination-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.pagination-button:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f9fafb;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.page-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
  padding: 0.5rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.page-button:hover:not(.active) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.page-button:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.page-button.active {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.ellipsis {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
  color: #6b7280;
  font-weight: 500;
}

/* Page info (mobile) */
.page-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.current-page {
  color: #3b82f6;
}

.page-separator {
  color: #6b7280;
}

/* Page size selector */
.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.page-size-label,
.page-size-suffix {
  color: #6b7280;
  white-space: nowrap;
}

.page-size-select {
  padding: 0.375rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
}

.page-size-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* Jump to page */
.jump-to-page {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.jump-to-label {
  color: #6b7280;
  white-space: nowrap;
}

.jump-to-input {
  width: 4rem;
  padding: 0.375rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  text-align: center;
}

.jump-to-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.jump-to-button {
  padding: 0.375rem 0.75rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.jump-to-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.jump-to-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.jump-to-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #9ca3af;
}

/* Total info */
.total-info {
  font-size: 0.875rem;
  color: #6b7280;
  white-space: nowrap;
}

/* Size variants */
.size-sm .pagination-button,
.size-sm .page-button {
  padding: 0.375rem 0.5rem;
  font-size: 0.8125rem;
  min-width: 2rem;
  height: 2rem;
}

.size-sm .page-size-select,
.size-sm .jump-to-input,
.size-sm .jump-to-button {
  padding: 0.25rem 0.375rem;
  font-size: 0.8125rem;
}

.size-lg .pagination-button,
.size-lg .page-button {
  padding: 0.75rem 1rem;
  font-size: 1rem;
  min-width: 3rem;
  height: 3rem;
}

.size-lg .page-size-select,
.size-lg .jump-to-input,
.size-lg .jump-to-button {
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .pagination-button,
  .page-button {
    background: #1f2937;
    border-color: #4b5563;
    color: #f3f4f6;
  }

  .pagination-button:hover:not(:disabled),
  .page-button:hover:not(.active) {
    background-color: #374151;
    border-color: #6b7280;
  }

  .pagination-button:disabled {
    background-color: #111827;
    color: #6b7280;
  }

  .page-button.active {
    background-color: #3b82f6;
    border-color: #3b82f6;
  }

  .page-size-select,
  .jump-to-input {
    background: #1f2937;
    border-color: #4b5563;
    color: #f3f4f6;
  }

  .page-info,
  .page-size-label,
  .page-size-suffix,
  .jump-to-label,
  .total-info {
    color: #d1d5db;
  }

  .current-page {
    color: #60a5fa;
  }

  .ellipsis {
    color: #9ca3af;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .pagination-button,
  .page-button {
    border-width: 2px;
  }

  .page-button.active {
    border-width: 3px;
  }
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .pagination {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .page-size-selector,
  .jump-to-page {
    justify-content: center;
  }

  .total-info {
    text-align: center;
  }
}

/* Button text visibility */
.button-text {
  display: none;
}

@media (min-width: 1024px) {
  .button-text {
    display: inline;
  }
}
</style>
