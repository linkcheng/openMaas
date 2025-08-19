<template>
  <div
    class="form-field"
    :class="{
      'has-error': error,
      required: required,
      'has-help': help,
    }"
    role="group"
    :aria-labelledby="label ? labelId : undefined"
    :aria-describedby="describedByIds"
  >
    <label v-if="label" :id="labelId" :for="fieldId" class="form-label">
      {{ label }}
      <span v-if="required" class="required-indicator" aria-label="必填字段" title="此字段为必填项"
        >*</span
      >
    </label>

    <div class="form-input-wrapper">
      <slot
        :field-id="fieldId"
        :aria-attributes="ariaAttributes"
        :has-error="!!error"
        :required="required"
      />
    </div>

    <div v-if="help && !error" :id="helpId" class="form-help" role="note" aria-label="帮助信息">
      {{ help }}
    </div>

    <div
      v-if="error"
      :id="errorId"
      class="form-error"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <span class="error-icon" aria-hidden="true">⚠</span>
      <span class="error-text">{{ error }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAriaLabels } from '@/composables/useAriaAnnouncements'

interface Props {
  label?: string
  error?: string
  help?: string
  required?: boolean
  fieldId?: string
}

const props = defineProps<Props>()

const { generateId, createErrorId, createHelpId, buildDescribedBy, getFieldAriaAttributes } =
  useAriaLabels()

// Generate unique IDs
const fieldId = computed(() => {
  return props.fieldId || generateId('field')
})

const labelId = computed(() => `${fieldId.value}-label`)
const errorId = computed(() => createErrorId(fieldId.value))
const helpId = computed(() => createHelpId(fieldId.value))

// Build describedby attribute
const describedByIds = computed(() => {
  return buildDescribedBy(
    props.help ? helpId.value : undefined,
    props.error ? errorId.value : undefined,
  )
})

// ARIA attributes for the input element
const ariaAttributes = computed(() => {
  return getFieldAriaAttributes(fieldId.value, {
    hasError: !!props.error,
    hasHelp: !!props.help,
    required: props.required,
    invalid: !!props.error,
  })
})
</script>

<style scoped>
.form-field {
  margin-bottom: var(--space-md);
}

.form-label {
  display: block;
  font-weight: 500;
  margin-bottom: var(--space-sm);
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.required-indicator {
  color: var(--maas-error);
  margin-left: var(--space-xs);
}

.form-input-wrapper {
  position: relative;
}

.form-input-wrapper :deep(input),
.form-input-wrapper :deep(select),
.form-input-wrapper :deep(textarea) {
  width: 100%;
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.form-input-wrapper :deep(input:focus),
.form-input-wrapper :deep(select:focus),
.form-input-wrapper :deep(textarea:focus) {
  outline: none;
  border-color: var(--maas-primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input-wrapper :deep(input:disabled),
.form-input-wrapper :deep(select:disabled),
.form-input-wrapper :deep(textarea:disabled) {
  background-color: var(--color-background-soft);
  color: var(--color-text-tertiary);
  cursor: not-allowed;
}

.has-error .form-input-wrapper :deep(input),
.has-error .form-input-wrapper :deep(select),
.has-error .form-input-wrapper :deep(textarea) {
  border-color: var(--maas-error);
}

.has-error .form-input-wrapper :deep(input:focus),
.has-error .form-input-wrapper :deep(select:focus),
.has-error .form-input-wrapper :deep(textarea:focus) {
  border-color: var(--maas-error);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-help {
  margin-top: var(--space-xs);
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.form-error {
  margin-top: var(--space-xs);
  font-size: 0.75rem;
  color: var(--maas-error);
  display: flex;
  align-items: center;
}

.error-icon {
  margin-right: var(--space-xs);
  font-size: 0.875rem;
}

.error-text {
  flex: 1;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .form-input-wrapper :deep(input:focus),
  .form-input-wrapper :deep(select:focus),
  .form-input-wrapper :deep(textarea:focus) {
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
}

.dark .form-input-wrapper :deep(input:focus),
.dark .form-input-wrapper :deep(select:focus),
.dark .form-input-wrapper :deep(textarea:focus) {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .form-input-wrapper :deep(input),
  .form-input-wrapper :deep(select),
  .form-input-wrapper :deep(textarea) {
    border-width: 2px;
  }

  .form-input-wrapper :deep(input:focus),
  .form-input-wrapper :deep(select:focus),
  .form-input-wrapper :deep(textarea:focus) {
    border-width: 3px;
  }
}

/* Responsive design */
@media (max-width: 640px) {
  .form-field {
    margin-bottom: var(--space-sm);
  }

  .form-input-wrapper :deep(input),
  .form-input-wrapper :deep(select),
  .form-input-wrapper :deep(textarea) {
    padding: var(--space-xs);
  }
}
</style>
