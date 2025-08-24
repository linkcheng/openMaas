<!--
 * Copyright 2025 MaaS Team
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
-->

<template>
  <DialogOverlay
    :model-value="modelValue"
    :close-on-overlay-click="!loading"
    :close-on-escape="!loading"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleCancel"
  >
    <div class="confirm-dialog">
      <div class="dialog-header">
        <div class="header-icon">
          <component :is="iconComponent" class="icon" :class="iconClass" />
        </div>
        <div class="header-content">
          <h2 class="dialog-title">{{ title }}</h2>
          <button
            v-if="!loading"
            @click="handleCancel"
            class="close-button"
            aria-label="关闭对话框"
          >
            <svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="dialog-body">
        <div class="message">{{ message }}</div>
        <div v-if="details" class="details">{{ details }}</div>
      </div>

      <div class="dialog-footer">
        <button
          @click="handleCancel"
          :disabled="loading"
          class="btn btn-secondary"
        >
          {{ cancelText }}
        </button>
        <button
          @click="handleConfirm"
          :disabled="loading"
          class="btn"
          :class="confirmButtonClass"
        >
          <svg v-if="loading" class="loading-spinner" viewBox="0 0 24 24">
            <path d="M21 12a9 9 0 11-6.219-8.56" />
          </svg>
          {{ loading ? loadingText : confirmText }}
        </button>
      </div>
    </div>
  </DialogOverlay>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DialogOverlay from './DialogOverlay.vue'

interface Props {
  modelValue: boolean
  type?: 'warning' | 'danger' | 'info' | 'success'
  title: string
  message: string
  details?: string
  confirmText?: string
  cancelText?: string
  loadingText?: string
  loading?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'warning',
  confirmText: '确认',
  cancelText: '取消',
  loadingText: '处理中...',
  loading: false,
})

const emit = defineEmits<Emits>()

const iconComponent = computed(() => {
  const icons = {
    warning: 'svg',
    danger: 'svg',
    info: 'svg',
    success: 'svg',
  }
  return icons[props.type]
})

const iconClass = computed(() => ({
  'warning-icon': props.type === 'warning',
  'danger-icon': props.type === 'danger',
  'info-icon': props.type === 'info',
  'success-icon': props.type === 'success',
}))

const confirmButtonClass = computed(() => ({
  'btn-warning': props.type === 'warning',
  'btn-danger': props.type === 'danger',
  'btn-primary': props.type === 'info',
  'btn-success': props.type === 'success',
  'loading': props.loading,
}))

const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm')
  }
}

const handleCancel = () => {
  if (!props.loading) {
    emit('cancel')
  }
}
</script>

<style scoped>
.confirm-dialog {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.dialog-header {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-icon {
  margin-right: 1rem;
}

.icon {
  width: 2rem;
  height: 2rem;
}

.warning-icon { color: #f59e0b; }
.danger-icon { color: #ef4444; }
.info-icon { color: #3b82f6; }
.success-icon { color: #10b981; }

.header-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.close-button {
  padding: 0.25rem;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.close-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.dialog-body {
  padding: 1.5rem;
}

.message {
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.5;
}

.details {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #6b7280;
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-warning {
  background: #f59e0b;
  border-color: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
}

.btn-danger {
  background: #ef4444;
  border-color: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-primary {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-success {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>