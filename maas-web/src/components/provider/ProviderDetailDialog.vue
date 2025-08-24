<template>
  <DialogOverlay
    v-model="isOpen"
    :aria-labelledby="dialogTitleId"
    :aria-describedby="dialogDescId"
    @close="handleClose"
    @keydown="handleKeydown"
  >
    <div v-if="provider" class="provider-detail-dialog">
      <!-- Dialog Header -->
      <div class="dialog-header">
        <div class="header-content">
          <div class="provider-icon">
            <img
              v-if="providerIcon"
              :src="providerIcon"
              :alt="provider.display_name"
              class="icon-image"
            />
            <div v-else class="icon-placeholder">
              {{ provider.display_name.charAt(0).toUpperCase() }}
            </div>
          </div>
          <div class="header-info">
            <h2 :id="dialogTitleId" class="provider-title">
              {{ provider.display_name }}
            </h2>
            <div class="provider-meta">
              <span class="provider-type">{{ getProviderTypeLabel(provider.provider_type) }}</span>
              <div class="status-badge" :class="statusClass">
                <span class="status-dot"></span>
                <span class="status-text">{{ statusText }}</span>
              </div>
            </div>
          </div>
        </div>
        <button @click="handleClose" class="close-button" aria-label="关闭对话框" title="关闭">
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
      <div class="dialog-body" :id="dialogDescId">
        <!-- Basic Information Section -->
        <div class="info-section">
          <h3 class="section-title">基本信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">供应商名称</label>
              <div class="info-value">{{ provider.provider_name }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">显示名称</label>
              <div class="info-value">{{ provider.display_name }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">供应商类型</label>
              <div class="info-value">{{ getProviderTypeLabel(provider.provider_type) }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">基础URL</label>
              <div class="info-value url-value">
                <span class="url-text">{{ provider.base_url }}</span>
                <button
                  @click="copyToClipboard(provider.base_url)"
                  class="copy-button"
                  title="复制URL"
                  aria-label="复制基础URL"
                >
                  <svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
              </div>
            </div>
            <div class="info-item full-width" v-if="provider.description">
              <label class="info-label">描述</label>
              <div class="info-value description-value">{{ provider.description }}</div>
            </div>
          </div>
        </div>

        <!-- Configuration Section -->
        <div
          class="info-section"
          v-if="provider.additional_config && Object.keys(provider.additional_config).length > 0"
        >
          <h3 class="section-title">配置参数</h3>
          <div class="config-container">
            <div class="config-item" v-for="(value, key) in provider.additional_config" :key="key">
              <label class="config-label">{{ formatConfigKey(key) }}</label>
              <div class="config-value">
                <!-- Sensitive field with permission check -->
                <span v-if="isSensitiveField(key)" class="sensitive-value">
                  <span v-if="!canViewSensitiveData" class="permission-denied">
                    {{ maskSensitiveValue(value) }}
                    <span class="permission-hint" title="需要查看敏感信息的权限">
                      <svg class="lock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                        <circle cx="12" cy="16" r="1"></circle>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                      </svg>
                    </span>
                  </span>
                  <span v-else>
                    {{ showSensitiveData[key] ? value : maskSensitiveValue(value) }}
                    <button
                      @click="toggleSensitiveData(key)"
                      class="toggle-sensitive-button"
                      :title="showSensitiveData[key] ? '隐藏' : '显示'"
                      :aria-label="showSensitiveData[key] ? '隐藏敏感信息' : '显示敏感信息'"
                    >
                      <svg
                        v-if="showSensitiveData[key]"
                        class="eye-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <path
                          d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
                        ></path>
                        <line x1="1" y1="1" x2="23" y2="23"></line>
                      </svg>
                      <svg
                        v-else
                        class="eye-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                    </button>
                  </span>
                </span>
                <!-- Normal field -->
                <span v-else class="normal-value">{{ formatConfigValue(value) }}</span>
                <!-- Copy button with permission check for sensitive data -->
                <button
                  @click="copyToClipboard(String(value), isSensitiveField(key))"
                  class="copy-button"
                  :disabled="isSensitiveField(key) && !canViewSensitiveData"
                  :title="
                    isSensitiveField(key) && !canViewSensitiveData
                      ? '需要权限才能复制敏感信息'
                      : '复制值'
                  "
                  :aria-label="`复制${formatConfigKey(key)}的值`"
                >
                  <svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Metadata Section -->
        <div class="info-section">
          <h3 class="section-title">元数据</h3>
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">创建者</label>
              <div class="info-value">{{ provider.created_by }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">创建时间</label>
              <div class="info-value">{{ formatDateTime(provider.created_at) }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">更新者</label>
              <div class="info-value">{{ provider.updated_by }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">更新时间</label>
              <div class="info-value">{{ formatDateTime(provider.updated_at) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Dialog Footer -->
      <div class="dialog-footer">
        <div class="footer-actions">
          <button
            v-if="canEditProvider"
            @click="handleEdit"
            :disabled="operationLoading.edit || loading"
            class="action-button edit-button"
            :class="{ loading: operationLoading.edit }"
            title="编辑供应商 (Ctrl+E)"
          >
            <svg
              v-if="!operationLoading.edit"
              class="button-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <svg
              v-else
              class="button-icon loading-spinner"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path d="M21 12a9 9 0 11-6.219-8.56" />
            </svg>
            {{ operationLoading.edit ? '处理中...' : '编辑' }}
          </button>
          <button
            v-if="canToggleStatus"
            @click="handleToggleStatus"
            :disabled="operationLoading.toggleStatus || loading"
            class="action-button toggle-button"
            :class="{
              activate: !provider.is_active,
              deactivate: provider.is_active,
              loading: operationLoading.toggleStatus,
            }"
            :title="provider.is_active ? '停用供应商 (Ctrl+T)' : '激活供应商 (Ctrl+T)'"
          >
            <svg
              v-if="!operationLoading.toggleStatus"
              class="button-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
            <svg
              v-else
              class="button-icon loading-spinner"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path d="M21 12a9 9 0 11-6.219-8.56" />
            </svg>
            {{ operationLoading.toggleStatus ? '处理中...' : provider.is_active ? '停用' : '激活' }}
          </button>
          <button
            v-if="canDeleteProvider"
            @click="handleDelete"
            :disabled="operationLoading.delete || loading"
            class="action-button delete-button"
            :class="{ loading: operationLoading.delete }"
            title="删除供应商 (Ctrl+D)"
          >
            <svg
              v-if="!operationLoading.delete"
              class="button-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <polyline points="3,6 5,6 21,6"></polyline>
              <path
                d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
              ></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
            <svg
              v-else
              class="button-icon loading-spinner"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path d="M21 12a9 9 0 11-6.219-8.56" />
            </svg>
            {{ operationLoading.delete ? '删除中...' : '删除' }}
          </button>
        </div>
        <button @click="handleClose" class="close-footer-button">关闭</button>
      </div>
    </div>
  </DialogOverlay>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import DialogOverlay from '../ui/DialogOverlay.vue'
import type { Provider } from '../../types/providerTypes'
import { PROVIDER_TYPE_OPTIONS, PROVIDER_ICONS } from '../../types/providerTypes'
import { useUserStore } from '../../stores/userStore'

interface Props {
  provider: Provider | null
  modelValue: boolean
  loading?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
  (e: 'edit', provider: Provider): void
  (e: 'delete', provider: Provider): void
  (e: 'toggle-status', provider: Provider): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})
const emit = defineEmits<Emits>()

// Stores
const userStore = useUserStore()

// Dialog state
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

// Unique IDs for accessibility
const dialogTitleId = computed(() => `provider-detail-title-${props.provider?.provider_id || 'new'}`)
const dialogDescId = computed(() => `provider-detail-desc-${props.provider?.provider_id || 'new'}`)

// Sensitive data visibility state
const showSensitiveData = reactive<Record<string, boolean>>({})

// Loading states for individual operations
const operationLoading = reactive({
  edit: false,
  delete: false,
  toggleStatus: false,
})

// Permission checks - 暂时允许所有已认证用户执行所有操作
const canViewSensitiveData = computed(() => userStore.isAuthenticated)

const canEditProvider = computed(() => userStore.isAuthenticated)

const canDeleteProvider = computed(() => userStore.isAuthenticated)

const canToggleStatus = computed(() => userStore.isAuthenticated)

// Computed properties
const providerIcon = computed(() => {
  if (!props.provider) return null
  return PROVIDER_ICONS[props.provider.provider_type as keyof typeof PROVIDER_ICONS]
})

const statusClass = computed(() => ({
  'status-active': props.provider?.is_active || false,
  'status-inactive': !props.provider?.is_active,
}))

const statusText = computed(() => (props.provider?.is_active ? '激活' : '停用'))

// Methods
const getProviderTypeLabel = (type: string) => {
  const option = PROVIDER_TYPE_OPTIONS.find((opt) => opt.value === type)
  return option?.label || type
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const formatConfigKey = (key: string) => {
  // Convert snake_case to readable format
  return key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
}

const formatConfigValue = (value: any) => {
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }
  return String(value)
}

const isSensitiveField = (key: string) => {
  const sensitiveFields = ['api_key', 'secret', 'password', 'token', 'aws_secret_access_key']
  return sensitiveFields.some((field) => key.toLowerCase().includes(field))
}

const maskSensitiveValue = (value: unknown) => {
  const str = String(value)
  if (str.length <= 4) return '****'
  return str.slice(0, 4) + '*'.repeat(Math.min(str.length - 4, 20))
}

const toggleSensitiveData = (key: string) => {
  if (!canViewSensitiveData.value) {
    console.warn('用户没有查看敏感信息的权限')
    return
  }
  showSensitiveData[key] = !showSensitiveData[key]
}

const canShowSensitiveField = (key: string) => {
  return canViewSensitiveData.value && isSensitiveField(key)
}

const copyToClipboard = async (text: string, isSensitive = false) => {
  // Check permission for sensitive data
  if (isSensitive && !canViewSensitiveData.value) {
    console.warn('用户没有复制敏感信息的权限')
    return
  }

  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('复制成功')
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
  }
}

// Keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  // Ctrl/Cmd + E for edit
  if ((event.ctrlKey || event.metaKey) && event.key === 'e' && canEditProvider.value) {
    event.preventDefault()
    handleEdit()
  }
  // Ctrl/Cmd + D for delete
  else if ((event.ctrlKey || event.metaKey) && event.key === 'd' && canDeleteProvider.value) {
    event.preventDefault()
    handleDelete()
  }
  // Ctrl/Cmd + T for toggle status
  else if ((event.ctrlKey || event.metaKey) && event.key === 't' && canToggleStatus.value) {
    event.preventDefault()
    handleToggleStatus()
  }
}

// Event handlers
const handleClose = () => {
  // Reset all loading states when closing
  Object.keys(operationLoading).forEach((key) => {
    operationLoading[key as keyof typeof operationLoading] = false
  })
  emit('close')
}

const handleEdit = () => {
  if (!props.provider || !canEditProvider.value) {
    console.warn('用户没有编辑供应商的权限或供应商不存在')
    return
  }
  if (operationLoading.edit) return

  operationLoading.edit = true
  emit('edit', props.provider)
  // Note: Loading state should be reset by parent component
}

const handleDelete = () => {
  if (!props.provider || !canDeleteProvider.value) {
    console.warn('用户没有删除供应商的权限或供应商不存在')
    return
  }
  if (operationLoading.delete) return

  operationLoading.delete = true
  emit('delete', props.provider)
  // Note: Loading state should be reset by parent component
}

const handleToggleStatus = () => {
  if (!props.provider || !canToggleStatus.value) {
    console.warn('用户没有切换供应商状态的权限或供应商不存在')
    return
  }
  if (operationLoading.toggleStatus) return

  operationLoading.toggleStatus = true
  emit('toggle-status', props.provider)
  // Note: Loading state should be reset by parent component
}

// Method to reset operation loading states (can be called by parent)
const resetOperationLoading = (operation?: keyof typeof operationLoading) => {
  if (operation) {
    operationLoading[operation] = false
  } else {
    Object.keys(operationLoading).forEach((key) => {
      operationLoading[key as keyof typeof operationLoading] = false
    })
  }
}

// Expose methods for parent component
defineExpose({
  resetOperationLoading,
})
</script>

<style scoped>
.provider-detail-dialog {
  width: 100%;
  max-width: 800px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Dialog Header */
.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.provider-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
}

.icon-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.icon-placeholder {
  font-size: 1.25rem;
  font-weight: 600;
  color: #6b7280;
}

.header-info {
  flex: 1;
}

.provider-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  line-height: 1.2;
}

.provider-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.25rem;
}

.provider-type {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.status-inactive {
  background: #f3f4f6;
  color: #6b7280;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.status-active .status-dot {
  background: #22c55e;
}

.status-inactive .status-dot {
  background: #9ca3af;
}

.close-button {
  padding: 0.5rem;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 6px;
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

/* Dialog Body */
.dialog-body {
  padding: 2rem;
  max-height: 60vh;
  overflow-y: auto;
}

.info-section {
  margin-bottom: 2rem;
}

.info-section:last-child {
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.info-value {
  font-size: 0.875rem;
  color: #111827;
  word-break: break-all;
}

.url-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.url-text {
  flex: 1;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8125rem;
}

.description-value {
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  white-space: pre-wrap;
}

/* Configuration Section */
.config-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.config-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.config-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sensitive-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #fef3c7;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8125rem;
  border: 1px solid #fbbf24;
}

.permission-denied {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #fee2e2;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8125rem;
  border: 1px solid #fca5a5;
  color: #991b1b;
}

.permission-hint {
  display: flex;
  align-items: center;
  color: #dc2626;
}

.lock-icon {
  width: 0.875rem;
  height: 0.875rem;
}

.normal-value {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8125rem;
  white-space: pre-wrap;
}

.toggle-sensitive-button,
.copy-button {
  padding: 0.25rem;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-sensitive-button:hover,
.copy-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.copy-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.copy-button:disabled:hover {
  background: none;
  color: #6b7280;
}

.eye-icon,
.copy-icon {
  width: 1rem;
  height: 1rem;
}

/* Dialog Footer */
.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.footer-actions {
  display: flex;
  gap: 0.75rem;
}

.action-button {
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

.action-button:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-button.loading {
  pointer-events: none;
}

.edit-button:hover:not(:disabled) {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1d4ed8;
}

.toggle-button.activate:hover:not(:disabled) {
  background: #dcfce7;
  border-color: #22c55e;
  color: #166534;
}

.toggle-button.deactivate:hover:not(:disabled) {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}

.delete-button:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #ef4444;
  color: #dc2626;
}

.loading-spinner {
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

.button-icon {
  width: 1rem;
  height: 1rem;
}

.close-footer-button {
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

.close-footer-button:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

/* Responsive Design */
@media (max-width: 768px) {
  .provider-detail-dialog {
    max-width: 95vw;
    margin: 1rem;
  }

  .dialog-header,
  .dialog-body,
  .dialog-footer {
    padding: 1rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .footer-actions {
    flex-direction: column;
    width: 100%;
  }

  .dialog-footer {
    flex-direction: column;
    gap: 1rem;
  }

  .action-button {
    justify-content: center;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .provider-detail-dialog {
    background: #1f2937;
    color: #f9fafb;
  }

  .dialog-header,
  .dialog-footer {
    background: #111827;
    border-color: #374151;
  }

  .provider-title {
    color: #f9fafb;
  }

  .section-title {
    color: #f9fafb;
    border-color: #374151;
  }

  .info-value {
    color: #e5e7eb;
  }

  .url-text,
  .normal-value {
    background: #374151;
    color: #e5e7eb;
  }

  .description-value {
    background: #111827;
    border-color: #374151;
    color: #e5e7eb;
  }

  .sensitive-value {
    background: #451a03;
    border-color: #92400e;
    color: #fbbf24;
  }

  .permission-denied {
    background: #7f1d1d;
    border-color: #dc2626;
    color: #fca5a5;
  }

  .action-button,
  .close-footer-button {
    background: #374151;
    border-color: #4b5563;
    color: #e5e7eb;
  }

  .action-button:hover,
  .close-footer-button:hover {
    background: #4b5563;
    border-color: #6b7280;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .provider-detail-dialog {
    border: 2px solid currentColor;
  }

  .dialog-header,
  .dialog-footer {
    border-width: 2px;
  }

  .action-button,
  .close-footer-button {
    border-width: 2px;
  }
}
</style>
