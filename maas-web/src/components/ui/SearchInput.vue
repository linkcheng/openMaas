<template>
  <div class="search-input" :class="{ 'is-loading': loading }">
    <div class="search-input-wrapper">
      <div class="search-icon">
        <svg
          v-if="!loading"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <div v-else class="loading-spinner">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="animate-spin"
          >
            <path d="M21 12a9 9 0 11-6.219-8.56"></path>
          </svg>
        </div>
      </div>

      <input
        ref="inputRef"
        v-model="inputValue"
        type="search"
        role="searchbox"
        :placeholder="placeholder"
        :disabled="disabled"
        :aria-label="ariaLabel || placeholder"
        :aria-describedby="ariaDescribedby"
        :aria-expanded="showSuggestions"
        :aria-haspopup="suggestions.length > 0 ? 'listbox' : undefined"
        :aria-owns="showSuggestions ? suggestionsId : undefined"
        :aria-activedescendant="
          highlightedIndex >= 0 ? `${suggestionsId}-${highlightedIndex}` : undefined
        "
        :aria-autocomplete="suggestions.length > 0 ? 'list' : 'none'"
        class="search-input-field"
        @input="handleInput"
        @keydown="handleKeydown"
        @focus="handleFocus"
        @blur="handleBlur"
      />

      <button
        v-if="inputValue && clearable"
        type="button"
        class="clear-button"
        :aria-label="clearAriaLabel"
        @click="clearInput"
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
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <!-- Search suggestions dropdown -->
    <div
      v-if="showSuggestions && suggestions.length > 0"
      :id="suggestionsId"
      class="suggestions-dropdown"
      role="listbox"
      :aria-label="suggestionsAriaLabel"
      :aria-multiselectable="false"
    >
      <button
        v-for="(suggestion, index) in suggestions"
        :key="index"
        :id="`${suggestionsId}-${index}`"
        type="button"
        class="suggestion-item"
        :class="{ highlighted: index === highlightedIndex }"
        role="option"
        :aria-selected="index === highlightedIndex"
        :aria-posinset="index + 1"
        :aria-setsize="suggestions.length"
        @click="selectSuggestion(suggestion)"
        @mouseenter="highlightedIndex = index"
      >
        {{ suggestion }}
      </button>
    </div>

    <!-- Screen reader announcements -->
    <div class="sr-only" aria-live="polite" aria-atomic="true">
      <span v-if="loading">正在搜索</span>
      <span v-else-if="showSuggestions"> 找到 {{ suggestions.length }} 个搜索建议 </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useAriaLabels } from '@/composables/useAriaAnnouncements'

interface Props {
  modelValue: string
  placeholder?: string
  disabled?: boolean
  loading?: boolean
  clearable?: boolean
  suggestions?: string[]
  debounceMs?: number
  ariaLabel?: string
  ariaDescribedby?: string
  clearAriaLabel?: string
  suggestionsAriaLabel?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'search', value: string): void
  (e: 'clear'): void
  (e: 'focus', event: FocusEvent): void
  (e: 'blur', event: FocusEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '搜索...',
  clearable: true,
  suggestions: () => [],
  debounceMs: 300,
  clearAriaLabel: '清除搜索',
  suggestionsAriaLabel: '搜索建议',
})

const emit = defineEmits<Emits>()

const { generateId } = useAriaLabels()

const inputRef = ref<HTMLInputElement>()
const inputValue = ref(props.modelValue)
const isFocused = ref(false)
const highlightedIndex = ref(-1)
const suggestionsId = generateId('suggestions')

// Computed properties
const showSuggestions = computed(() => {
  return isFocused.value && inputValue.value.length > 0 && props.suggestions.length > 0
})

// Debounced search function
const debouncedSearch = useDebounceFn((value: string) => {
  emit('search', value)
}, props.debounceMs)

// Handle input changes
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  inputValue.value = target.value
  emit('update:modelValue', target.value)

  // Reset highlighted index when typing
  highlightedIndex.value = -1

  // Trigger debounced search
  debouncedSearch(target.value)
}

// Handle keyboard navigation
const handleKeydown = (event: KeyboardEvent) => {
  if (!showSuggestions.value) return

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, props.suggestions.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
      break
    case 'Enter':
      event.preventDefault()
      if (highlightedIndex.value >= 0) {
        selectSuggestion(props.suggestions[highlightedIndex.value])
      } else {
        emit('search', inputValue.value)
      }
      break
    case 'Escape':
      isFocused.value = false
      highlightedIndex.value = -1
      inputRef.value?.blur()
      break
  }
}

// Handle focus events
const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  // Delay hiding suggestions to allow for clicks
  setTimeout(() => {
    isFocused.value = false
    highlightedIndex.value = -1
  }, 150)
  emit('blur', event)
}

// Select suggestion
const selectSuggestion = (suggestion: string) => {
  inputValue.value = suggestion
  emit('update:modelValue', suggestion)
  emit('search', suggestion)
  isFocused.value = false
  highlightedIndex.value = -1
}

// Clear input
const clearInput = () => {
  inputValue.value = ''
  emit('update:modelValue', '')
  emit('clear')
  inputRef.value?.focus()
}

// Focus method for external use
const focus = () => {
  inputRef.value?.focus()
}

// Watch for external model value changes
watch(
  () => props.modelValue,
  (newValue) => {
    inputValue.value = newValue
  },
)

// Expose methods
defineExpose({
  focus,
})
</script>

<style scoped>
.search-input {
  position: relative;
  width: 100%;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  z-index: 1;
  color: #6b7280;
  pointer-events: none;
}

.loading-spinner svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.search-input-field {
  width: 100%;
  padding: 0.75rem 0.75rem 0.75rem 2.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background-color: white;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.search-input-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input-field:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.search-input-field::placeholder {
  color: #9ca3af;
}

.clear-button {
  position: absolute;
  right: 0.75rem;
  padding: 0.25rem;
  color: #6b7280;
  background: none;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition:
    color 0.2s,
    background-color 0.2s;
}

.clear-button:hover {
  color: #374151;
  background-color: #f3f4f6;
}

.clear-button:focus {
  outline: none;
  color: #374151;
  background-color: #f3f4f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 50;
  background: white;
  border: 1px solid #d1d5db;
  border-top: none;
  border-radius: 0 0 0.375rem 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  width: 100%;
  padding: 0.75rem;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.875rem;
}

.suggestion-item:hover,
.suggestion-item.highlighted {
  background-color: #f3f4f6;
}

.suggestion-item:focus {
  outline: none;
  background-color: #e5e7eb;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .search-input-field {
    background-color: #1f2937;
    border-color: #4b5563;
    color: #f3f4f6;
  }

  .search-input-field:disabled {
    background-color: #111827;
    color: #9ca3af;
  }

  .search-input-field::placeholder {
    color: #6b7280;
  }

  .search-icon {
    color: #9ca3af;
  }

  .clear-button {
    color: #9ca3af;
  }

  .clear-button:hover,
  .clear-button:focus {
    color: #f3f4f6;
    background-color: #374151;
  }

  .suggestions-dropdown {
    background: #1f2937;
    border-color: #4b5563;
  }

  .suggestion-item:hover,
  .suggestion-item.highlighted {
    background-color: #374151;
  }

  .suggestion-item:focus {
    background-color: #4b5563;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .search-input-field {
    border-width: 2px;
  }

  .search-input-field:focus {
    border-width: 3px;
  }

  .suggestions-dropdown {
    border-width: 2px;
  }
}

/* Screen reader only content */
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

/* Responsive design */
@media (max-width: 640px) {
  .search-input-field {
    padding: 0.625rem 0.625rem 0.625rem 2.25rem;
  }

  .search-icon {
    left: 0.625rem;
  }

  .clear-button {
    right: 0.625rem;
  }
}
</style>
