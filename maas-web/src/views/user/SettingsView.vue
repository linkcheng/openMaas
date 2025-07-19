<template>
  <div class="settings-view">
    <div class="container">
      <h1>账户设置</h1>

      <!-- 密码设置 -->
      <div class="settings-card">
        <h2>密码设置</h2>
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label>当前密码</label>
            <input
              v-model="passwordForm.current_password"
              type="password"
              required
              autocomplete="current-password"
            />
          </div>

          <div class="form-group">
            <label>新密码</label>
            <input
              v-model="passwordForm.new_password"
              type="password"
              required
              autocomplete="new-password"
              minlength="8"
            />
            <small class="help-text">密码至少8个字符，包含大小写字母和数字</small>
          </div>

          <div class="form-group">
            <label>确认新密码</label>
            <input
              v-model="passwordForm.confirm_password"
              type="password"
              required
              autocomplete="new-password"
            />
          </div>

          <button type="submit" class="btn-primary" :disabled="passwordLoading || !isPasswordValid">
            {{ passwordLoading ? '修改中...' : '修改密码' }}
          </button>
        </form>
      </div>

      <!-- API密钥管理 -->
      <div class="settings-card">
        <div class="card-header">
          <h2>API密钥管理</h2>
          <button @click="showCreateDialog = true" class="btn-primary">创建新密钥</button>
        </div>

        <div class="api-keys-list">
          <div v-if="apiKeys.length === 0" class="empty-state">暂无API密钥</div>

          <div v-for="key in apiKeys" :key="key.id" class="api-key-item">
            <div class="key-info">
              <h3>{{ key.name }}</h3>
              <p class="key-details">
                创建时间: {{ formatDate(key.created_at) }} | 权限: {{ key.permissions.join(', ') }}
                <span v-if="key.expires_at"> | 过期时间: {{ formatDate(key.expires_at) }}</span>
              </p>
              <code class="key-value">{{ key.key }}</code>
            </div>
            <button @click="revokeApiKey(key.id)" class="btn-danger" :disabled="loading">
              撤销
            </button>
          </div>
        </div>
      </div>

      <!-- 通知设置 -->
      <div class="settings-card">
        <h2>通知设置</h2>
        <div class="notification-settings">
          <div class="setting-item">
            <label class="checkbox-label">
              <input v-model="notificationSettings.email_notifications" type="checkbox" />
              <span class="checkmark"></span>
              邮件通知
            </label>
            <p class="setting-description">接收系统重要通知和更新</p>
          </div>

          <div class="setting-item">
            <label class="checkbox-label">
              <input v-model="notificationSettings.security_alerts" type="checkbox" />
              <span class="checkmark"></span>
              安全警报
            </label>
            <p class="setting-description">当账户有异常登录活动时通知</p>
          </div>

          <div class="setting-item">
            <label class="checkbox-label">
              <input v-model="notificationSettings.api_usage_alerts" type="checkbox" />
              <span class="checkmark"></span>
              API使用警报
            </label>
            <p class="setting-description">当API使用量接近限额时通知</p>
          </div>
        </div>

        <button @click="saveNotificationSettings" class="btn-primary" :disabled="loading">
          {{ loading ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </div>

    <!-- 创建API密钥对话框 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click="closeCreateDialog">
      <div class="dialog" @click.stop>
        <h3>创建API密钥</h3>
        <form @submit.prevent="createApiKey">
          <div class="form-group">
            <label>密钥名称</label>
            <input v-model="createForm.name" type="text" required />
          </div>

          <div class="form-group">
            <label>权限</label>
            <div class="permissions-list">
              <label
                v-for="permission in availablePermissions"
                :key="permission"
                class="checkbox-label"
              >
                <input v-model="createForm.permissions" :value="permission" type="checkbox" />
                <span class="checkmark"></span>
                {{ permission }}
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>过期时间（可选）</label>
            <input v-model="createForm.expires_at" type="datetime-local" />
          </div>

          <div class="dialog-actions">
            <button type="submit" class="btn-primary" :disabled="createLoading">
              {{ createLoading ? '创建中...' : '创建' }}
            </button>
            <button type="button" @click="closeCreateDialog" class="btn-secondary">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { apiClient, handleApiError } from '@/utils/api'

interface ApiKey {
  id: string
  name: string
  key: string
  permissions: string[]
  created_at: string
  expires_at?: string
}

const apiKeys = ref<ApiKey[]>([])
const showCreateDialog = ref(false)
const loading = ref(false)
const passwordLoading = ref(false)
const createLoading = ref(false)

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const createForm = reactive({
  name: '',
  permissions: [] as string[],
  expires_at: '',
})

const notificationSettings = reactive({
  email_notifications: true,
  security_alerts: true,
  api_usage_alerts: false,
})

const availablePermissions = ['read', 'write', 'admin']

const isPasswordValid = computed(() => {
  return (
    passwordForm.current_password &&
    passwordForm.new_password &&
    passwordForm.new_password === passwordForm.confirm_password &&
    passwordForm.new_password.length >= 8
  )
})

const loadApiKeys = async () => {
  try {
    const response = await apiClient.users.getApiKeys()
    apiKeys.value = response.data.data
  } catch (error) {
    console.error('加载API密钥失败:', handleApiError(error))
  }
}

const changePassword = async () => {
  if (!isPasswordValid.value) return

  passwordLoading.value = true
  try {
    await apiClient.users.changePassword({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    })

    // 重置表单
    Object.assign(passwordForm, {
      current_password: '',
      new_password: '',
      confirm_password: '',
    })

    alert('密码修改成功')
  } catch (error) {
    alert('密码修改失败: ' + handleApiError(error))
  } finally {
    passwordLoading.value = false
  }
}

const createApiKey = async () => {
  if (!createForm.name || createForm.permissions.length === 0) return

  createLoading.value = true
  try {
    const data = {
      name: createForm.name,
      permissions: createForm.permissions,
      expires_at: createForm.expires_at || undefined,
    }

    await apiClient.users.createApiKey(data)
    await loadApiKeys()
    closeCreateDialog()
    alert('API密钥创建成功')
  } catch (error) {
    alert('创建API密钥失败: ' + handleApiError(error))
  } finally {
    createLoading.value = false
  }
}

const revokeApiKey = async (keyId: string) => {
  if (!confirm('确定要撤销这个API密钥吗？')) return

  loading.value = true
  try {
    await apiClient.users.revokeApiKey(keyId)
    await loadApiKeys()
    alert('API密钥已撤销')
  } catch (error) {
    alert('撤销API密钥失败: ' + handleApiError(error))
  } finally {
    loading.value = false
  }
}

const saveNotificationSettings = async () => {
  loading.value = true
  try {
    // 这里需要实现保存通知设置的API
    await new Promise((resolve) => setTimeout(resolve, 1000)) // 模拟API调用
    alert('通知设置已保存')
  } catch {
    alert('保存设置失败')
  } finally {
    loading.value = false
  }
}

const closeCreateDialog = () => {
  showCreateDialog.value = false
  Object.assign(createForm, {
    name: '',
    permissions: [],
    expires_at: '',
  })
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadApiKeys()
})
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.settings-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.password-form {
  max-width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 1rem;
}

.help-text {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #6366f1;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5855eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.api-keys-list {
  space-y: 1rem;
}

.empty-state {
  text-align: center;
  color: #6b7280;
  padding: 2rem;
}

.api-key-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.key-info {
  flex: 1;
}

.key-info h3 {
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.key-details {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
}

.key-value {
  background: #f3f4f6;
  padding: 0.5rem;
  border-radius: 4px;
  font-family: monospace;
  word-break: break-all;
}

.notification-settings {
  space-y: 1rem;
}

.setting-item {
  margin-bottom: 1.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-label input[type='checkbox'] {
  margin-right: 0.5rem;
}

.setting-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0.25rem 0 0 1.5rem;
}

.permissions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.dialog h3 {
  margin: 0 0 1rem 0;
  color: #111827;
}

.dialog-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

h1,
h2 {
  color: #111827;
  margin-bottom: 1rem;
}
</style>
