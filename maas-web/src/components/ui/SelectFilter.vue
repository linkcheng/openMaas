<template>
  <div class="select-filter" :class="{ 'is-open': isOpen, 'has-error': error }">
    <button
      ref="triggerRef"
      type="button"
      class="select-trigger"
      :class="{ 'has-value': hasValue }"
      :disabled="disabled"
      :aria-expanded="isOpen"
      :aria-haspopup="true"
      :aria-labelledby="labelId"
      :aria-describedby="ariaDescribedby"
      @click="toggleDropdown"
      @keydown="handleTriggerKeydown"
    >
      <span class="select-value">
        <span v-if="!hasValue" class="placeholder">{{ placeholder }}</span>
        <span v-else-if="multiple && selectedItems.length > 0" class="multiple-values">
          <span v-if="selectedItems.length === 1">{{ selectedItems[0].label }}</span>
          <span v-else>已选择 {{ selectedItems.length }} 项</span>
        </span>
        <span v-else-if="!multiple && selectedItem">{{ selectedItem.label }}</span>
      </span>

      <div class="select-icons">
        <div v-if="clearable && hasValue" class="clear-icon" @click.stop="clearSelection">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </div>
        <div class="chevron-icon" :class="{ rotated: isOpen }">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="6,9 12,15 18,9"></polyline>
          </svg>
        </div>
      </div>
    </button>

    <!-- Dropdown -->
    <div
      v-if="isOpen"
      ref="dropdownRef"
      class="select-dropdown"
      role="listbox"
      :aria-multiselectable="multiple"
      :aria-labelledby="labelId"
    >
      <!-- Search input for filterable -->
      <div v-if="filterable" class="search-wrapper">
        <input
          ref="searchRef"
          v-model="searchQuery"
          type="text"
          class="search-input"
          :placeholder="searchPlaceholder"
          @keydown="handleSearchKeydown"
        />
      </div>

      <!-- Options -->
      <div class="options-container">
        <div
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          class="option-item"
          :class="{
            selected: isSelected(option),
            highlighted: index === highlightedIndex,
          }"
          role="option"
          :aria-selected="isSelected(option)"
          @click="selectOption(option)"
          @mouseenter="highlightedIndex = index"
        >
          <div v-if="multiple" class="checkbox-wrapper">
            <input
              type="checkbox"
              :checked="isSelected(option)"
              :disabled="option.disabled"
              tabindex="-1"
              class="option-checkbox"
            />
          </div>

          <span class="option-label">{{ option.label }}</span>

          <span v-if="option.description" class="option-description">
            {{ option.description }}
          </span>
        </div>

        <div v-if="filteredOptions.length === 0" class="no-options">
          {{ noOptionsText }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

interface SelectOption {
  value: string | number
  label: string
  description?: string
  disabled?: boolean
}

interface Props {
  modelValue: string | number | (string | number)[]
  options: SelectOption[]
  placeholder?: string
  multiple?: boolean
  clearable?: boolean
  filterable?: boolean
  disabled?: boolean
  error?: string
  labelId?: string
  ariaDescribedby?: string
  searchPlaceholder?: string
  noOptionsText?: string
}

interface Emits {
  (e: 'update:modelValue', value: string | number | (string | number)[]): void
  (e: 'change', value: string | number | (string | number)[]): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择...',
  searchPlaceholder: '搜索选项...',
  noOptionsText: '无可选项',
})

const emit = defineEmits<Emits>()

const triggerRef = ref<HTMLButtonElement>()
const dropdownRef = ref<HTMLDivElement>()
const searchRef = ref<HTMLInputElement>()
const isOpen = ref(false)
const searchQuery = ref('')
const highlightedIndex = ref(-1)

// Computed properties
const hasValue = computed(() => {
  if (props.multiple) {
    return Array.isArray(props.modelValue) && props.modelValue.length > 0
  }
  return props.modelValue !== null && props.modelValue !== undefined && props.modelValue !== ''
})

const selectedItems = computed(() => {
  if (!props.multiple || !Array.isArray(props.modelValue)) return []
  return props.options.filter((option) => props.modelValue.includes(option.value))
})

const selectedItem = computed(() => {
  if (props.multiple) return null
  return props.options.find((option) => option.value === props.modelValue) || null
})

const filteredOptions = computed(() => {
  if (!props.filterable || !searchQuery.value) {
    return props.options
  }

  const query = searchQuery.value.toLowerCase()
  return props.options.filter(
    (option) =>
      option.label.toLowerCase().includes(query) ||
      (option.description && option.description.toLowerCase().includes(query)),
  )
})

// Methods
const toggleDropdown = () => {
  if (props.disabled) return

  isOpen.value = !isOpen.value

  if (isOpen.value) {
    nextTick(() => {
      if (props.filterable && searchRef.value) {
        searchRef.value.focus()
      }
      highlightedIndex.value = -1
    })
  }
}

const closeDropdown = () => {
  isOpen.value = false
  searchQuery.value = ''
  highlightedIndex.value = -1
}

const isSelected = (option: SelectOption) => {
  if (props.multiple && Array.isArray(props.modelValue)) {
    return props.modelValue.includes(option.value)
  }
  return props.modelValue === option.value
}

const selectOption = (option: SelectOption) => {
  if (option.disabled) return

  let newValue: string | number | (string | number)[]

  if (props.multiple) {
    const currentValue = Array.isArray(props.modelValue) ? props.modelValue : []
    if (currentValue.includes(option.value)) {
      newValue = currentValue.filter((v) => v !== option.value)
    } else {
      newValue = [...currentValue, option.value]
    }
  } else {
    newValue = option.value
    closeDropdown()
  }

  emit('update:modelValue', newValue)
  emit('change', newValue)
}

const clearSelection = () => {
  const newValue = props.multiple ? [] : ''
  emit('update:modelValue', newValue)
  emit('change', newValue)
}

// Keyboard navigation
const handleTriggerKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'Enter':
    case ' ':
    case 'ArrowDown':
      event.preventDefault()
      if (!isOpen.value) {
        toggleDropdown()
      }
      break
    case 'ArrowUp':
      event.preventDefault()
      if (!isOpen.value) {
        toggleDropdown()
      }
      break
    case 'Escape':
      if (isOpen.value) {
        event.preventDefault()
        closeDropdown()
      }
      break
  }
}

const handleSearchKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      highlightedIndex.value = Math.min(
        highlightedIndex.value + 1,
        filteredOptions.value.length - 1,
      )
      break
    case 'ArrowUp':
      event.preventDefault()
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
      break
    case 'Enter':
      event.preventDefault()
      if (highlightedIndex.value >= 0) {
        selectOption(filteredOptions.value[highlightedIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      closeDropdown()
      triggerRef.value?.focus()
      break
  }
}

// Click outside to close
const handleClickOutside = (event: Event) => {
  if (!triggerRef.value || !dropdownRef.value) return

  const target = event.target as Node
  if (!triggerRef.value.contains(target) && !dropdownRef.value.contains(target)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.select-filter {
  position: relative;
  width: 100%;
}

.select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.select-trigger:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-trigger:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.has-error .select-trigger {
  border-color: #ef4444;
}

.has-error .select-trigger:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.select-value {
  flex: 1;
  min-width: 0;
}

.placeholder {
  color: #9ca3af;
}

.multiple-values {
  color: #374151;
}

.select-icons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 0.5rem;
}

.clear-icon {
  padding: 0.25rem;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.25rem;
  transition:
    color 0.2s,
    background-color 0.2s;
}

.clear-icon:hover {
  color: #374151;
  background-color: #f3f4f6;
}

.chevron-icon {
  color: #6b7280;
  transition: transform 0.2s;
}

.chevron-icon.rotated {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 50;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow: hidden;
  margin-top: 0.25rem;
}

.search-wrapper {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.options-container {
  max-height: 200px;
  overflow-y: auto;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.option-item:hover,
.option-item.highlighted {
  background-color: #f3f4f6;
}

.option-item.selected {
  background-color: #eff6ff;
  color: #1d4ed8;
}

.checkbox-wrapper {
  margin-right: 0.75rem;
}

.option-checkbox {
  width: 1rem;
  height: 1rem;
}

.option-label {
  flex: 1;
  font-weight: 500;
}

.option-description {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 0.5rem;
}

.no-options {
  padding: 0.75rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .select-trigger {
    background-color: #1f2937;
    border-color: #4b5563;
    color: #f3f4f6;
  }

  .select-trigger:disabled {
    background-color: #111827;
    color: #9ca3af;
  }

  .placeholder {
    color: #6b7280;
  }

  .select-dropdown {
    background: #1f2937;
    border-color: #4b5563;
  }

  .search-wrapper {
    border-color: #4b5563;
  }

  .search-input {
    background-color: #374151;
    border-color: #6b7280;
    color: #f3f4f6;
  }

  .option-item:hover,
  .option-item.highlighted {
    background-color: #374151;
  }

  .option-item.selected {
    background-color: #1e40af;
    color: #dbeafe;
  }

  .option-description {
    color: #9ca3af;
  }

  .no-options {
    color: #9ca3af;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .select-trigger {
    border-width: 2px;
  }

  .select-trigger:focus {
    border-width: 3px;
  }

  .select-dropdown {
    border-width: 2px;
  }
}

/* Responsive design */
@media (max-width: 640px) {
  .select-trigger {
    padding: 0.625rem;
  }

  .option-item {
    padding: 0.625rem;
  }

  .search-wrapper {
    padding: 0.625rem;
  }
}
</style>
