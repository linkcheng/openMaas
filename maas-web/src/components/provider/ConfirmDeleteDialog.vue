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
    aria-labelledby="delete-dialog-title"
    aria-describedby="delete-dialog-description"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleCancel"
  >
    <div class="confirm-delete-dialog">
      <!-- Dialog Header -->
      <div class="dialog-header">
        <div class="header-icon">
          <svg
            class="warning-icon"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>
        <div class="header-content">
          <h2 id="delete-dialog-title" class="dialog-title">确认删除供应商</h2>
          <button
            v-if="!loading"
            @click="handleCancel"
            class="close-button"
            type="button"
            aria-label="关闭对话框"
          >
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Dialog Body -->
      <div class="dialog-body">
        <div id="delete-dialog-description" class="warning-content">
          <!-- Provider Information -->
          <div class="provider-info">
            <div class="provider-details">
              <div class="provider-icon">
                <img
                  v-if="providerIcon"
                  :src="providerIcon"
                  :alt="provider?.display_name"
                  class="icon-image"
                />
                <div v-else class="icon-placeholder">
                  {{ provider?.display_name?.charAt(0)?.toUpperCase() }}
                </div>
              </div>
              <div class="provider-meta">
                <h3 class="provider-name">{{ provider?.display_name }}</h3>
                <p class="provider-type">{{ provider?.provider_type }}</p>
                <p class="provider-id">ID: {{ provider?.provider_id }}</p>
              </div>
            </div>
          </div>

          <!-- Loading Preconditions -->
          <div v-if="checkingPreconditions" class="loading-section">
            <div class="loading-content">
              <svg
                class="loading-spinner"
                fill="none"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <span>正在检查删除条件...</span>
            </div>
          </div>

          <!-- Delete Blockers -->
          <div v-if="hasBlockers" class="blocker-section">
            <div class="blocker-alert">
              <svg
                class="blocker-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"
                />
              </svg>
              <div class="blocker-content">
                <h4 class="blocker-title">无法删除</h4>
                <p class="blocker-description">以下问题阻止了删除操作：</p>
                <ul class="blocker-list">
                  <li v-for="blocker in deletePreconditions?.blockers" :key="blocker">
                    {{ blocker }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Delete Impact -->
          <div v-if="deleteImpact && !hasBlockers" class="impact-section">
            <h4 class="impact-title">
              <svg
                class="warning-icon-small"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
              删除影响范围
            </h4>
            <div class="impact-grid">
              <div class="impact-item">
                <span class="impact-label">受影响模型：</span>
                <span class="impact-value">{{ deleteImpact.affectedModels }} 个</span>
              </div>
              <div class="impact-item">
                <span class="impact-label">活跃连接：</span>
                <span class="impact-value">{{ deleteImpact.affectedConnections }} 个</span>
              </div>
              <div class="impact-item">
                <span class="impact-label">预计停机时间：</span>
                <span class="impact-value">{{ deleteImpact.estimatedDowntime }}</span>
              </div>
            </div>
            <div v-if="deleteImpact.recoverySteps.length > 0" class="recovery-steps">
              <p class="recovery-title">恢复步骤：</p>
              <ol class="recovery-list">
                <li v-for="step in deleteImpact.recoverySteps" :key="step">
                  {{ step }}
                </li>
              </ol>
            </div>
          </div>

          <!-- Warning Message -->
          <div v-if="hasWarnings && !hasBlockers" class="warning-message">
            <h4 class="warning-title">
              <svg
                class="warning-icon-small"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
              注意事项
            </h4>
            <ul class="warning-list">
              <li v-for="warning in deletePreconditions?.warnings" :key="warning">
                <svg
                  class="list-icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                  aria-hidden="true"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
                {{ warning }}
              </li>
            </ul>
          </div>

          <!-- General Warning (fallback) -->
          <div v-if="!checkingPreconditions && !deletePreconditions" class="warning-message">
            <h4 class="warning-title">
              <svg
                class="warning-icon-small"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
              删除风险提示
            </h4>
            <div class="warning-text">
              <p class="primary-warning">
                {{ confirmationMessage }}
              </p>
              <ul class="impact-list">
                <li>
                  <svg
                    class="list-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  所有使用此供应商的模型配置将无法正常工作
                </li>
                <li>
                  <svg
                    class="list-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  相关的API调用和服务将立即停止
                </li>
                <li>
                  <svg
                    class="list-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  供应商的配置信息将被永久删除
                </li>
                <li>
                  <svg
                    class="list-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  此操作无法撤销
                </li>
              </ul>
            </div>
          </div>

          <!-- Error Display -->
          <div v-if="error" class="error-section">
            <div class="error-alert">
              <svg
                class="error-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div class="error-content">
                <h4 class="error-title">删除失败</h4>
                <p class="error-message">{{ error }}</p>
                <div v-if="canRetryDelete" class="error-actions">
                  <button
                    @click="handleRetry"
                    :disabled="loading"
                    class="retry-button"
                    type="button"
                  >
                    <svg
                      v-if="loading"
                      class="loading-spinner-small"
                      fill="none"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                      aria-hidden="true"
                    >
                      <circle
                        class="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                      />
                      <path
                        class="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    <svg
                      v-else
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                      aria-hidden="true"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    <span v-if="loading">重试中...</span>
                    <span v-else>重试 ({{ deleteState.retryCount }}/3)</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Confirmation Input -->
          <div v-if="!hasBlockers" class="confirmation-section">
            <p class="confirmation-instruction">
              请输入供应商名称 <strong>{{ provider?.provider_name }}</strong> 以确认删除：
            </p>
            <input
              v-model="confirmationInput"
              type="text"
              class="confirmation-input"
              :class="{ error: confirmationError }"
              :placeholder="provider?.provider_name"
              :disabled="loading || checkingPreconditions"
              @input="validateConfirmation"
              @keydown.enter="handleConfirm"
              aria-label="确认删除输入框"
              aria-describedby="confirmation-error"
            />
            <p
              v-if="confirmationError"
              id="confirmation-error"
              class="confirmation-error"
              role="alert"
            >
              {{ confirmationError }}
            </p>
          </div>
        </div>
      </div>

      <!-- Dialog Footer -->
      <div class="dialog-footer">
        <button @click="handleCancel" :disabled="loading" class="cancel-button" type="button">
          {{ hasBlockers ? '关闭' : '取消' }}
        </button>
        <button
          v-if="!hasBlockers"
          @click="handleConfirm"
          :disabled="!isConfirmationValid || loading || checkingPreconditions"
          class="confirm-button"
          :class="{ loading: loading }"
          type="button"
        >
          <svg
            v-if="loading"
            class="loading-spinner"
            fill="none"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span v-if="loading">删除中...</span>
          <span v-else-if="checkingPreconditions">检查中...</span>
          <span v-else>确认删除</span>
        </button>
      </div>
    </div>
  </DialogOverlay>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import DialogOverlay from '../ui/DialogOverlay.vue'
import { useConfirmDelete } from '../../composables/useConfirmDelete'
import type { Provider } from '../../types/providerTypes'
import { PROVIDER_ICONS } from '../../types/providerTypes'

interface Props {
  modelValue: boolean
  provider: Provider | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'success', message: string): void
  (e: 'error', error: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Use delete confirmation composable
const {
  deleteState,
  isDeleting,
  deleteError,
  canRetryDelete,
  executeDelete,
  retryDelete,
  clearDeleteError,
  resetDeleteState,
  checkDeletePreconditions,
  getDeleteImpact,
  generateConfirmationMessage,
} = useConfirmDelete()

// Confirmation input state
const confirmationInput = ref('')
const confirmationError = ref('')

// Delete preconditions and impact
const deletePreconditions = ref<{
  canDelete: boolean
  warnings: string[]
  blockers: string[]
} | null>(null)

const deleteImpact = ref<{
  affectedModels: number
  affectedConnections: number
  estimatedDowntime: string
  recoverySteps: string[]
} | null>(null)

// Loading states
const checkingPreconditions = ref(false)
const loadingImpact = ref(false)

// Computed properties
const providerIcon = computed(() => {
  if (!props.provider?.provider_type) return null
  return PROVIDER_ICONS[props.provider.provider_type as keyof typeof PROVIDER_ICONS]
})

const isConfirmationValid = computed(() => {
  return (
    confirmationInput.value === props.provider?.provider_name &&
    !confirmationError.value &&
    deletePreconditions.value?.canDelete !== false
  )
})

const loading = computed(
  () => isDeleting.value || checkingPreconditions.value || loadingImpact.value,
)

const error = computed(() => deleteError.value)

const confirmationMessage = computed(() => {
  if (!props.provider) return ''
  return generateConfirmationMessage(props.provider)
})

const hasBlockers = computed(
  () => deletePreconditions.value?.blockers && deletePreconditions.value.blockers.length > 0,
)

const hasWarnings = computed(
  () => deletePreconditions.value?.warnings && deletePreconditions.value.warnings.length > 0,
)

// Methods
const validateConfirmation = () => {
  if (!confirmationInput.value) {
    confirmationError.value = '请输入供应商名称'
    return
  }

  if (confirmationInput.value !== props.provider?.provider_name) {
    confirmationError.value = '输入的供应商名称不匹配'
    return
  }

  confirmationError.value = ''
}

const loadDeletePreconditions = async () => {
  if (!props.provider) return

  checkingPreconditions.value = true
  try {
    deletePreconditions.value = await checkDeletePreconditions(props.provider)
  } catch (err) {
    console.error('检查删除前置条件失败:', err)
    deletePreconditions.value = {
      canDelete: true,
      warnings: ['无法检查删除前置条件，请谨慎操作'],
      blockers: [],
    }
  } finally {
    checkingPreconditions.value = false
  }
}

const loadDeleteImpact = async () => {
  if (!props.provider) return

  loadingImpact.value = true
  try {
    deleteImpact.value = await getDeleteImpact(props.provider)
  } catch (err) {
    console.error('获取删除影响范围失败:', err)
    deleteImpact.value = {
      affectedModels: 0,
      affectedConnections: 0,
      estimatedDowntime: '未知',
      recoverySteps: ['请手动检查相关配置'],
    }
  } finally {
    loadingImpact.value = false
  }
}

const handleConfirm = async () => {
  if (!props.provider) return

  validateConfirmation()

  if (!isConfirmationValid.value || loading.value) {
    return
  }

  try {
    const result = await executeDelete(props.provider)

    if (result.success) {
      emit('success', result.message || '删除成功')
      emit('confirm')
    } else {
      emit('error', result.error || '删除失败')
    }
  } catch (err) {
    console.error('删除操作失败:', err)
    emit('error', '删除操作失败，请重试')
  }
}

const handleRetry = async () => {
  if (!props.provider || !canRetryDelete.value) return

  try {
    const result = await retryDelete(props.provider)

    if (result.success) {
      emit('success', result.message || '删除成功')
      emit('confirm')
    } else {
      emit('error', result.error || '重试失败')
    }
  } catch (err) {
    console.error('重试删除失败:', err)
    emit('error', '重试失败，请稍后再试')
  }
}

const handleCancel = () => {
  if (!loading.value) {
    emit('cancel')
  }
}

const resetDialog = () => {
  confirmationInput.value = ''
  confirmationError.value = ''
  deletePreconditions.value = null
  deleteImpact.value = null
  resetDeleteState()
  clearDeleteError()
}

// Initialize dialog when it opens
const initializeDialog = async () => {
  if (!props.provider || !props.modelValue) return

  resetDialog()

  // Load preconditions and impact in parallel
  await Promise.all([loadDeletePreconditions(), loadDeleteImpact()])
}

// Watch for dialog open/close and provider changes
watch(
  [() => props.modelValue, () => props.provider],
  async ([isOpen, provider]) => {
    if (isOpen && provider) {
      await initializeDialog()
    } else if (!isOpen) {
      resetDialog()
    }
  },
  { immediate: true },
)

// Clear error when user starts typing
watch(confirmationInput, () => {
  if (confirmationError.value && confirmationInput.value) {
    confirmationError.value = ''
  }
})

// Keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  if (!props.modelValue) return

  // Enter to confirm (if valid)
  if (event.key === 'Enter' && isConfirmationValid.value && !loading.value) {
    event.preventDefault()
    handleConfirm()
  }

  // Escape to cancel
  if (event.key === 'Escape' && !loading.value) {
    event.preventDefault()
    handleCancel()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.confirm-delete-dialog {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

/* Dialog Header */
.dialog-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem 1.5rem 0;
  background: #fef2f2;
  border-bottom: 1px solid #fecaca;
}

.header-icon {
  flex-shrink: 0;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fee2e2;
  border-radius: 50%;
}

.warning-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #dc2626;
}

.header-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.dialog-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #dc2626;
  line-height: 1.5;
}

.close-button {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 4px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.close-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.close-button svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* Dialog Body */
.dialog-body {
  padding: 1.5rem;
}

.warning-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Provider Information */
.provider-info {
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.provider-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.provider-icon {
  flex-shrink: 0;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  overflow: hidden;
}

.icon-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.icon-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e7eb;
  color: #6b7280;
  font-weight: 600;
  font-size: 1rem;
}

.provider-meta {
  flex: 1;
  min-width: 0;
}

.provider-name {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  line-height: 1.4;
}

.provider-type {
  margin: 0 0 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
}

.provider-id {
  margin: 0;
  font-size: 0.75rem;
  color: #9ca3af;
  font-family: monospace;
  line-height: 1.4;
}

/* Warning Message */
.warning-message {
  padding: 1rem;
  background: #fffbeb;
  border: 1px solid #fed7aa;
  border-radius: 8px;
}

.warning-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  color: #d97706;
  line-height: 1.4;
}

.warning-icon-small {
  width: 1.25rem;
  height: 1.25rem;
  color: #d97706;
}

.primary-warning {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: #92400e;
  font-weight: 500;
  line-height: 1.5;
}

.impact-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.impact-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #92400e;
  line-height: 1.5;
}

.impact-list li:last-child {
  margin-bottom: 0;
}

.list-icon {
  flex-shrink: 0;
  width: 1rem;
  height: 1rem;
  color: #dc2626;
  margin-top: 0.125rem;
}

/* Loading Section */
.loading-section {
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #6b7280;
}

/* Blocker Section */
.blocker-section {
  margin-top: 1rem;
}

.blocker-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #fef2f2;
  border: 2px solid #dc2626;
  border-radius: 8px;
}

.blocker-icon {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  color: #dc2626;
  margin-top: 0.125rem;
}

.blocker-content {
  flex: 1;
  min-width: 0;
}

.blocker-title {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #dc2626;
  line-height: 1.4;
}

.blocker-description {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: #b91c1c;
  line-height: 1.5;
}

.blocker-list {
  margin: 0;
  padding: 0 0 0 1.25rem;
  list-style: disc;
}

.blocker-list li {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #b91c1c;
  line-height: 1.5;
}

.blocker-list li:last-child {
  margin-bottom: 0;
}

/* Impact Section */
.impact-section {
  padding: 1rem;
  background: #fffbeb;
  border: 1px solid #fed7aa;
  border-radius: 8px;
}

.impact-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #d97706;
  line-height: 1.4;
}

.impact-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.impact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #fef3c7;
  border-radius: 6px;
}

.impact-label {
  font-size: 0.875rem;
  color: #92400e;
  font-weight: 500;
}

.impact-value {
  font-size: 0.875rem;
  color: #92400e;
  font-weight: 600;
}

.recovery-steps {
  border-top: 1px solid #fed7aa;
  padding-top: 1rem;
}

.recovery-title {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  color: #92400e;
  font-weight: 600;
  line-height: 1.4;
}

.recovery-list {
  margin: 0;
  padding: 0 0 0 1.25rem;
  list-style: decimal;
}

.recovery-list li {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #92400e;
  line-height: 1.5;
}

.recovery-list li:last-child {
  margin-bottom: 0;
}

/* Warning List */
.warning-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.warning-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #92400e;
  line-height: 1.5;
}

.warning-list li:last-child {
  margin-bottom: 0;
}

/* Error Section */
.error-section {
  margin-top: 1rem;
}

.error-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
}

.error-icon {
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  color: #dc2626;
  margin-top: 0.125rem;
}

.error-content {
  flex: 1;
  min-width: 0;
}

.error-title {
  margin: 0 0 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #dc2626;
  line-height: 1.4;
}

.error-message {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: #b91c1c;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 0.5rem;
}

.retry-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #dc2626;
  border: 1px solid #dc2626;
  border-radius: 4px;
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-button:hover:not(:disabled) {
  background: #b91c1c;
  border-color: #b91c1c;
}

.retry-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.retry-button svg {
  width: 0.875rem;
  height: 0.875rem;
}

.loading-spinner-small {
  width: 0.875rem;
  height: 0.875rem;
  animation: spin 1s linear infinite;
}

/* Confirmation Section */
.confirmation-section {
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.confirmation-instruction {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.5;
}

.confirmation-instruction strong {
  font-weight: 600;
  color: #111827;
  font-family: monospace;
  background: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
}

.confirmation-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  font-family: monospace;
  background: white;
  transition: all 0.2s;
}

.confirmation-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.confirmation-input.error {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.confirmation-input:disabled {
  background: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.confirmation-error {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  color: #dc2626;
  line-height: 1.4;
}

/* Dialog Footer */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem 1.5rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.cancel-button,
.confirm-button {
  padding: 0.75rem 1.5rem;
  border: 1px solid;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 6rem;
  justify-content: center;
}

.cancel-button {
  background: white;
  border-color: #d1d5db;
  color: #374151;
}

.cancel-button:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.cancel-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-button {
  background: #dc2626;
  border-color: #dc2626;
  color: white;
}

.confirm-button:hover:not(:disabled) {
  background: #b91c1c;
  border-color: #b91c1c;
}

.confirm-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
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

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .confirm-delete-dialog {
    background: #1f2937;
    color: #f9fafb;
  }

  .dialog-header {
    background: #7f1d1d;
    border-bottom-color: #991b1b;
  }

  .header-icon {
    background: #991b1b;
  }

  .dialog-title {
    color: #fca5a5;
  }

  .close-button {
    color: #d1d5db;
  }

  .close-button:hover {
    background: #374151;
    color: #f9fafb;
  }

  .provider-info {
    background: #374151;
    border-color: #4b5563;
  }

  .provider-name {
    color: #f9fafb;
  }

  .provider-type {
    color: #d1d5db;
  }

  .provider-id {
    color: #9ca3af;
  }

  .icon-placeholder {
    background: #4b5563;
    color: #d1d5db;
  }

  .warning-message {
    background: #451a03;
    border-color: #92400e;
  }

  .warning-title {
    color: #fbbf24;
  }

  .warning-icon-small {
    color: #fbbf24;
  }

  .primary-warning {
    color: #fcd34d;
  }

  .impact-list li {
    color: #fcd34d;
  }

  .loading-section {
    background: #374151;
    border-color: #4b5563;
  }

  .loading-content {
    color: #d1d5db;
  }

  .blocker-alert {
    background: #7f1d1d;
    border-color: #dc2626;
  }

  .blocker-title {
    color: #fca5a5;
  }

  .blocker-description {
    color: #fca5a5;
  }

  .blocker-list li {
    color: #fca5a5;
  }

  .impact-section {
    background: #451a03;
    border-color: #92400e;
  }

  .impact-title {
    color: #fbbf24;
  }

  .impact-item {
    background: #78350f;
  }

  .impact-label,
  .impact-value {
    color: #fcd34d;
  }

  .recovery-steps {
    border-top-color: #92400e;
  }

  .recovery-title {
    color: #fcd34d;
  }

  .recovery-list li {
    color: #fcd34d;
  }

  .warning-list li {
    color: #fcd34d;
  }

  .error-alert {
    background: #7f1d1d;
    border-color: #991b1b;
  }

  .error-title {
    color: #fca5a5;
  }

  .error-message {
    color: #fca5a5;
  }

  .retry-button {
    background: #dc2626;
    border-color: #dc2626;
  }

  .retry-button:hover:not(:disabled) {
    background: #b91c1c;
    border-color: #b91c1c;
  }

  .confirmation-section {
    background: #374151;
    border-color: #4b5563;
  }

  .confirmation-instruction {
    color: #d1d5db;
  }

  .confirmation-instruction strong {
    color: #f9fafb;
    background: #4b5563;
  }

  .confirmation-input {
    background: #1f2937;
    border-color: #4b5563;
    color: #f9fafb;
  }

  .confirmation-input:focus {
    border-color: #3b82f6;
  }

  .confirmation-input:disabled {
    background: #374151;
    color: #9ca3af;
  }

  .dialog-footer {
    background: #374151;
    border-top-color: #4b5563;
  }

  .cancel-button {
    background: #1f2937;
    border-color: #4b5563;
    color: #d1d5db;
  }

  .cancel-button:hover:not(:disabled) {
    background: #374151;
    border-color: #6b7280;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .dialog-header {
    border-bottom-width: 2px;
  }

  .provider-info,
  .warning-message,
  .error-alert,
  .confirmation-section {
    border-width: 2px;
  }

  .confirmation-input {
    border-width: 2px;
  }

  .confirmation-input:focus {
    box-shadow: 0 0 0 3px currentColor;
  }

  .dialog-footer {
    border-top-width: 2px;
  }

  .cancel-button,
  .confirm-button {
    border-width: 2px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none;
  }

  .close-button,
  .confirmation-input,
  .cancel-button,
  .confirm-button {
    transition: none;
  }
}
</style>
