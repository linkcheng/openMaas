<!--
 Copyright 2025 MaaS Team

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

<template>
  <DialogOverlay
    v-model="isOpen"
    :aria-labelledby="dialogTitleId"
    :aria-describedby="dialogDescId"
    @close="handleCancel"
  >
    <div class="provider-dialog-form">
      <!-- Dialog Header -->
      <div class="dialog-header">
        <div class="dialog-title-section">
          <h2 :id="dialogTitleId" class="dialog-title">
            {{ isEditMode ? '编辑供应商' : '创建供应商' }}
          </h2>
          <p :id="dialogDescId" class="dialog-description">
            {{ isEditMode ? '修改供应商配置信息' : '添加新的AI模型供应商' }}
          </p>
        </div>
        <button
          type="button"
          class="dialog-close-btn"
          :aria-label="'关闭' + (isEditMode ? '编辑' : '创建') + '对话框'"
          @click="handleCancel"
        >
          <svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <!-- Dialog Body -->
      <div class="dialog-body">
        <form @submit.prevent="handleSubmit" class="provider-form">
          <!-- Basic Information Section -->
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">基本信息</h3>
              <p class="section-description">配置供应商的基本标识和连接信息</p>
            </div>

            <div class="form-grid">
              <!-- Provider Name -->
              <FormField
                :label="'供应商名称'"
                :error="getFieldError('provider_name')"
                :help="getFieldHint('provider_name')"
                :required="isFieldRequired('provider_name')"
                :field-id="'provider-name'"
              >
                <input
                  id="provider-name"
                  v-model="form.provider_name"
                  type="text"
                  placeholder="例如：openai-main"
                  :disabled="isEditMode || formState.isSubmitting"
                  :aria-invalid="hasFieldError('provider_name')"
                  :aria-describedby="
                    hasFieldError('provider_name') ? 'provider-name-error' : undefined
                  "
                  @blur="handleFieldBlur('provider_name')"
                  @input="handleFieldChange('provider_name', $event.target.value)"
                />
              </FormField>

              <!-- Display Name -->
              <FormField
                :label="'显示名称'"
                :error="getFieldError('display_name')"
                :help="getFieldHint('display_name')"
                :required="isFieldRequired('display_name')"
                :field-id="'display-name'"
              >
                <input
                  id="display-name"
                  v-model="form.display_name"
                  type="text"
                  placeholder="例如：OpenAI 主要服务"
                  :disabled="formState.isSubmitting"
                  :aria-invalid="hasFieldError('display_name')"
                  :aria-describedby="
                    hasFieldError('display_name') ? 'display-name-error' : undefined
                  "
                  @blur="handleFieldBlur('display_name')"
                  @input="handleFieldChange('display_name', $event.target.value)"
                />
              </FormField>

              <!-- Provider Type -->
              <FormField
                :label="'供应商类型'"
                :error="getFieldError('provider_type')"
                :required="isFieldRequired('provider_type')"
                :field-id="'provider-type'"
              >
                <select
                  id="provider-type"
                  v-model="form.provider_type"
                  :disabled="formState.isSubmitting"
                  :aria-invalid="hasFieldError('provider_type')"
                  :aria-describedby="
                    hasFieldError('provider_type') ? 'provider-type-error' : undefined
                  "
                  @blur="handleFieldBlur('provider_type')"
                  @change="handleProviderTypeChange($event.target.value)"
                >
                  <option value="">请选择供应商类型</option>
                  <option
                    v-for="option in providerTypeOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </FormField>

              <!-- Base URL -->
              <FormField
                :label="'API基础URL'"
                :error="getFieldError('base_url')"
                :help="getFieldHint('base_url')"
                :required="isFieldRequired('base_url')"
                :field-id="'base-url'"
              >
                <div class="url-input-wrapper">
                  <input
                    id="base-url"
                    v-model="form.base_url"
                    type="url"
                    placeholder="https://api.example.com/v1"
                    :disabled="formState.isSubmitting"
                    :aria-invalid="hasFieldError('base_url')"
                    :aria-describedby="hasFieldError('base_url') ? 'base-url-error' : undefined"
                    @blur="handleFieldBlur('base_url')"
                    @input="handleFieldChange('base_url', $event.target.value)"
                  />
                  <!-- Auto-fill suggestions -->
                  <div v-if="urlSuggestions.length > 0" class="url-suggestions">
                    <button
                      v-for="suggestion in urlSuggestions"
                      :key="suggestion"
                      type="button"
                      class="suggestion-btn"
                      :title="`使用建议URL: ${suggestion}`"
                      @click="applyAutoFill('base_url', suggestion)"
                    >
                      {{ suggestion }}
                    </button>
                  </div>
                </div>
              </FormField>
            </div>
          </div>

          <!-- Authentication Section -->
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">认证配置</h3>
              <p class="section-description">配置访问供应商API所需的认证信息</p>
            </div>

            <div class="form-grid">
              <!-- API Key -->
              <FormField
                :label="'API密钥'"
                :error="getFieldError('api_key')"
                :help="getFieldHint('api_key')"
                :required="isFieldRequired('api_key')"
                :field-id="'api-key'"
                class="full-width"
              >
                <div class="password-input-wrapper">
                  <input
                    id="api-key"
                    v-model="form.api_key"
                    :type="showApiKey ? 'text' : 'password'"
                    placeholder="请输入API密钥"
                    :disabled="formState.isSubmitting"
                    :aria-invalid="hasFieldError('api_key')"
                    :aria-describedby="hasFieldError('api_key') ? 'api-key-error' : undefined"
                    @blur="handleFieldBlur('api_key')"
                    @input="handleFieldChange('api_key', $event.target.value)"
                  />
                  <button
                    type="button"
                    class="password-toggle-btn"
                    :aria-label="showApiKey ? '隐藏API密钥' : '显示API密钥'"
                    @click="showApiKey = !showApiKey"
                  >
                    <svg
                      v-if="showApiKey"
                      class="eye-icon"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
                      />
                    </svg>
                    <svg
                      v-else
                      class="eye-icon"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                  </button>
                </div>
              </FormField>
            </div>
          </div>

          <!-- Additional Configuration Section -->
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">其他配置</h3>
              <p class="section-description">配置供应商的描述信息和额外参数</p>
            </div>

            <div class="form-grid">
              <!-- Description -->
              <FormField
                :label="'描述'"
                :error="getFieldError('description')"
                :field-id="'description'"
                class="full-width"
              >
                <textarea
                  id="description"
                  v-model="form.description"
                  rows="3"
                  placeholder="请输入供应商描述信息（可选）"
                  :disabled="formState.isSubmitting"
                  :aria-invalid="hasFieldError('description')"
                  :aria-describedby="hasFieldError('description') ? 'description-error' : undefined"
                  @blur="handleFieldBlur('description')"
                  @input="handleFieldChange('description', $event.target.value)"
                ></textarea>
              </FormField>

              <!-- Additional Config -->
              <FormField
                :label="'额外配置'"
                :error="additionalConfigError || getFieldError('additional_config')"
                :help="getFieldHint('additional_config')"
                :field-id="'additional-config'"
                class="full-width"
              >
                <div class="json-input-wrapper">
                  <textarea
                    id="additional-config"
                    v-model="additionalConfigText"
                    rows="6"
                    placeholder='{"timeout": 30, "max_retries": 3}'
                    :disabled="formState.isSubmitting"
                    :aria-invalid="!!additionalConfigError"
                    :aria-describedby="
                      additionalConfigError ? 'additional-config-error' : undefined
                    "
                    @blur="handleAdditionalConfigBlur"
                    @input="handleAdditionalConfigInput"
                  ></textarea>
                  <div class="json-actions">
                    <button
                      type="button"
                      class="format-btn"
                      :disabled="!additionalConfigText.trim() || formState.isSubmitting"
                      title="格式化JSON"
                      @click="formatAdditionalConfig"
                    >
                      <svg
                        class="format-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4 6h16M4 12h16M4 18h16"
                        />
                      </svg>
                      格式化
                    </button>
                  </div>
                </div>
              </FormField>

              <!-- Active Status -->
              <FormField :label="'状态'" :field-id="'is-active'">
                <label class="checkbox-wrapper">
                  <input
                    id="is-active"
                    v-model="form.is_active"
                    type="checkbox"
                    :disabled="formState.isSubmitting"
                    @change="handleFieldChange('is_active', $event.target.checked)"
                  />
                  <span class="checkbox-label">启用供应商</span>
                  <span class="checkbox-help">启用后供应商将可用于模型配置</span>
                </label>
              </FormField>
            </div>
          </div>
        </form>
      </div>

      <!-- Dialog Footer -->
      <div class="dialog-footer">
        <div class="footer-info">
          <span v-if="hasFormChanges" class="changes-indicator">
            <svg class="changes-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="3" />
            </svg>
            有未保存的更改
          </span>
        </div>
        <div class="footer-actions">
          <button
            type="button"
            class="btn btn-secondary"
            :disabled="formState.isSubmitting"
            @click="handleCancel"
          >
            取消
          </button>
          <button
            type="button"
            class="btn btn-outline"
            :disabled="formState.isSubmitting || !formState.isDirty"
            @click="handleReset"
          >
            重置
          </button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="!canSubmit"
            @click="handleSubmit"
          >
            <svg v-if="formState.isSubmitting" class="loading-icon" viewBox="0 0 24 24">
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
                fill="none"
                opacity="0.25"
              />
              <path
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                opacity="0.75"
              />
            </svg>
            {{ formState.isSubmitting ? '保存中...' : isEditMode ? '更新' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </DialogOverlay>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import DialogOverlay from '@/components/ui/DialogOverlay.vue'
import FormField from '@/components/ui/FormField.vue'
import { useProviderForm } from '@/composables/useProviderForm'
import { useAriaAnnouncements } from '@/composables/useAriaAnnouncements'
import type { Provider, CreateProviderRequest, UpdateProviderRequest } from '@/types/providerTypes'
import { PROVIDER_TYPE_OPTIONS } from '@/types/providerTypes'

// Props
interface Props {
  modelValue: boolean
  provider?: Provider
  mode?: 'create' | 'edit'
}

// Emits
interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'save', data: CreateProviderRequest | UpdateProviderRequest): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create',
})

const emit = defineEmits<Emits>()

// Dialog state
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

// Form composable
const {
  form,
  formState,
  errors,
  additionalConfigText,
  additionalConfigError,
  isEditMode,
  isFormValid,
  hasFormChanges,
  canSubmit,
  handleFieldChange,
  handleFieldBlur,
  handleProviderTypeChange,
  validateAdditionalConfig,
  formatAdditionalConfig,
  getFieldError,
  hasFieldError,
  isFieldRequired,
  getFieldHint,
  getAutoFillSuggestions,
  applyAutoFill,
  submitForm,
  resetForm,
  initializeForm,
} = useProviderForm(props.provider)

// Local state
const showApiKey = ref(false)

// ARIA announcements
const { announceFormError, announceFormSubmission, announceSuccess } = useAriaAnnouncements()

// Computed properties
const dialogTitleId = computed(() => `dialog-title-${Math.random().toString(36).substr(2, 9)}`)
const dialogDescId = computed(() => `dialog-desc-${Math.random().toString(36).substr(2, 9)}`)

const providerTypeOptions = computed(() => PROVIDER_TYPE_OPTIONS)

const urlSuggestions = computed(() => {
  if (!form.provider_type || form.base_url) return []
  return getAutoFillSuggestions('base_url')
})

// Event handlers
const handleSubmit = async () => {
  announceFormSubmission('submitting', '正在保存供应商配置')

  try {
    const formData = await submitForm()
    if (formData) {
      announceFormSubmission('success', `供应商${isEditMode.value ? '更新' : '创建'}成功`)
      emit('save', formData)
    }
  } catch (error) {
    announceFormSubmission('error', `供应商${isEditMode.value ? '更新' : '创建'}失败`)
  }
}

const handleCancel = () => {
  if (hasFormChanges.value && !confirm('有未保存的更改，确定要关闭吗？')) {
    return
  }
  emit('cancel')
}

const handleReset = () => {
  if (confirm('确定要重置表单吗？所有更改将丢失。')) {
    resetForm()
    if (props.provider) {
      initializeForm()
    }
  }
}

const handleAdditionalConfigInput = () => {
  validateAdditionalConfig()
}

const handleAdditionalConfigBlur = () => {
  validateAdditionalConfig()
}

// Watch for provider changes
watch(
  () => props.provider,
  () => {
    if (isOpen.value) {
      initializeForm()
    }
  },
  { deep: true },
)

// Watch for dialog open/close
watch(isOpen, (newValue) => {
  if (newValue) {
    nextTick(() => {
      initializeForm()
      showApiKey.value = false
    })
  }
})
</script>

<style scoped>
/* Dialog Container */
.provider-dialog-form {
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

/* Dialog Header */
.dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.5rem 2rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.dialog-title-section {
  flex: 1;
}

.dialog-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
  line-height: 1.25;
}

.dialog-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

.dialog-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: none;
  background: none;
  color: #6b7280;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 1rem;
  flex-shrink: 0;
}

.dialog-close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.dialog-close-btn:focus {
  outline: none;
  background: #f3f4f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.close-icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* Dialog Body */
.dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.provider-form {
  padding: 1.5rem 2rem;
}

/* Form Sections */
.form-section {
  margin-bottom: 2rem;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-header {
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
  line-height: 1.25;
}

.section-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

/* Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-grid :deep(.full-width) {
  grid-column: 1 / -1;
}

/* Input Wrappers */
.url-input-wrapper {
  position: relative;
}

.url-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d1d5db;
  border-top: none;
  border-radius: 0 0 0.375rem 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-btn {
  display: block;
  width: 100%;
  padding: 0.75rem;
  text-align: left;
  border: none;
  background: none;
  color: #374151;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.suggestion-btn:hover {
  background: #f3f4f6;
}

.suggestion-btn:focus {
  outline: none;
  background: #e0e7ff;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  padding-right: 3rem;
}

.password-toggle-btn {
  position: absolute;
  right: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.2s ease;
}

.password-toggle-btn:hover {
  color: #374151;
}

.password-toggle-btn:focus {
  outline: none;
  color: #3b82f6;
}

.eye-icon {
  width: 1rem;
  height: 1rem;
}

.json-input-wrapper {
  position: relative;
}

.json-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.format-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.format-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
  color: #374151;
}

.format-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.format-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.format-icon {
  width: 0.875rem;
  height: 0.875rem;
}

/* Checkbox Wrapper */
.checkbox-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  cursor: pointer;
}

.checkbox-wrapper input[type='checkbox'] {
  width: auto;
  margin-right: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.checkbox-help {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 1.25rem;
}

/* Dialog Footer */
.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.footer-info {
  flex: 1;
}

.changes-indicator {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: #d97706;
  font-weight: 500;
}

.changes-icon {
  width: 0.75rem;
  height: 0.75rem;
  fill: currentColor;
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Buttons */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 2.5rem;
  min-width: 5rem;
}

.btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
}

.btn-secondary {
  background: #f9fafb;
  color: #374151;
  border-color: #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-outline {
  background: transparent;
  color: #6b7280;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f9fafb;
  color: #374151;
  border-color: #9ca3af;
}

.loading-icon {
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

/* Responsive Design */
@media (max-width: 768px) {
  .provider-dialog-form {
    max-width: 95vw;
    margin: 0.5rem;
  }

  .dialog-header {
    padding: 1rem 1.5rem 0.75rem;
  }

  .dialog-title {
    font-size: 1.25rem;
  }

  .provider-form {
    padding: 1rem 1.5rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .form-section {
    margin-bottom: 1.5rem;
  }

  .section-header {
    margin-bottom: 1rem;
  }

  .dialog-footer {
    padding: 0.75rem 1.5rem 1rem;
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .footer-actions {
    justify-content: stretch;
  }

  .btn {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .provider-dialog-form {
    max-width: 100vw;
    max-height: 100vh;
    margin: 0;
    border-radius: 0;
  }

  .dialog-header {
    padding: 0.75rem 1rem 0.5rem;
  }

  .dialog-title {
    font-size: 1.125rem;
  }

  .provider-form {
    padding: 0.75rem 1rem;
  }

  .dialog-footer {
    padding: 0.5rem 1rem 0.75rem;
  }

  .footer-actions {
    flex-direction: column;
  }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  .provider-dialog-form {
    background: #1f2937;
    color: #f3f4f6;
  }

  .dialog-header,
  .dialog-footer {
    background: #111827;
    border-color: #374151;
  }

  .dialog-title {
    color: #f3f4f6;
  }

  .dialog-description,
  .section-description {
    color: #9ca3af;
  }

  .section-title {
    color: #f3f4f6;
  }

  .section-header {
    border-color: #374151;
  }

  .dialog-close-btn {
    color: #9ca3af;
  }

  .dialog-close-btn:hover {
    background: #374151;
    color: #f3f4f6;
  }

  .url-suggestions {
    background: #1f2937;
    border-color: #4b5563;
  }

  .suggestion-btn {
    color: #f3f4f6;
  }

  .suggestion-btn:hover {
    background: #374151;
  }

  .format-btn {
    background: #374151;
    border-color: #4b5563;
    color: #9ca3af;
  }

  .format-btn:hover:not(:disabled) {
    background: #4b5563;
    border-color: #6b7280;
    color: #f3f4f6;
  }

  .checkbox-label {
    color: #f3f4f6;
  }

  .checkbox-help {
    color: #9ca3af;
  }

  .btn-secondary {
    background: #374151;
    color: #f3f4f6;
    border-color: #4b5563;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #4b5563;
    border-color: #6b7280;
  }

  .btn-outline {
    color: #9ca3af;
    border-color: #4b5563;
  }

  .btn-outline:hover:not(:disabled) {
    background: #374151;
    color: #f3f4f6;
    border-color: #6b7280;
  }
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
  .provider-dialog-form {
    border: 2px solid currentColor;
  }

  .dialog-header,
  .dialog-footer {
    border-width: 2px;
  }

  .section-header {
    border-width: 2px;
  }

  .btn {
    border-width: 2px;
  }

  .btn:focus {
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .btn,
  .dialog-close-btn,
  .password-toggle-btn,
  .format-btn,
  .suggestion-btn {
    transition: none;
  }

  .loading-icon {
    animation: none;
  }
}

/* Print Styles */
@media print {
  .provider-dialog-form {
    box-shadow: none;
    border: 1px solid #000;
  }

  .dialog-footer {
    display: none;
  }
}
</style>
