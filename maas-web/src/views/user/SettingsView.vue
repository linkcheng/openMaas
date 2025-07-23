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
  <div class="settings-view">
    <el-page-header @back="$router.back()" content="账户设置" />

    <div class="settings-container">
      <!-- 密码设置 -->
      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>密码设置</span>
          </div>
        </template>

        <el-form
          :model="passwordForm"
          :rules="passwordRules"
          ref="passwordFormRef"
          label-width="120px"
          @submit.prevent="changePassword"
        >
          <el-form-item label="当前密码" prop="current_password">
            <el-input
              v-model="passwordForm.current_password"
              type="password"
              :prefix-icon="Lock"
              placeholder="请输入当前密码"
              autocomplete="current-password"
              show-password
            />
          </el-form-item>

          <el-form-item label="新密码" prop="new_password">
            <el-input
              v-model="passwordForm.new_password"
              type="password"
              :prefix-icon="Key"
              placeholder="请输入新密码"
              autocomplete="new-password"
              show-password
            />
            <div class="help-text">密码至少8个字符，包含大小写字母和数字</div>
          </el-form-item>

          <el-form-item label="确认新密码" prop="confirm_password">
            <el-input
              v-model="passwordForm.confirm_password"
              type="password"
              :prefix-icon="Key"
              placeholder="请再次输入新密码"
              autocomplete="new-password"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="passwordLoading" @click="changePassword">
              修改密码
            </el-button>
            <el-button @click="resetPasswordForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- API密钥管理 -->
      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>API密钥管理</span>
            <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
              创建新密钥
            </el-button>
          </div>
        </template>

        <div class="api-keys-list">
          <el-empty v-if="apiKeys.length === 0" description="暂无API密钥" />

          <div v-for="key in apiKeys" :key="key.id" class="api-key-item">
            <div class="key-info">
              <div class="key-header">
                <h3>{{ key.name }}</h3>
                <el-tag v-if="key.expires_at" type="warning" size="small">
                  {{ getExpiryStatus(key.expires_at) }}
                </el-tag>
              </div>
              <el-descriptions :column="1" size="small" class="key-details">
                <el-descriptions-item label="创建时间">
                  {{ formatDate(key.created_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="权限">
                  <el-tag
                    v-for="permission in key.permissions"
                    :key="permission"
                    type="info"
                    size="small"
                    class="permission-tag"
                  >
                    {{ permission }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item v-if="key.expires_at" label="过期时间">
                  {{ formatDate(key.expires_at) }}
                </el-descriptions-item>
              </el-descriptions>
              <div class="key-value">
                <el-input :model-value="key.key" readonly type="textarea" :rows="2">
                  <template #append>
                    <el-button
                      :icon="CopyDocument"
                      @click="copyToClipboard(key.key)"
                      title="复制密钥"
                    />
                  </template>
                </el-input>
              </div>
            </div>
            <div class="key-actions">
              <el-popconfirm
                title="确定要撤销这个API密钥吗？"
                @confirm="revokeApiKey(key.id)"
                confirm-button-text="确定"
                cancel-button-text="取消"
              >
                <template #reference>
                  <el-button type="danger" size="small" :loading="loading"> 撤销 </el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 通知设置 -->
      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>通知设置</span>
          </div>
        </template>

        <div class="notification-settings">
          <div class="setting-item">
            <div class="setting-header">
              <el-switch
                v-model="notificationSettings.email_notifications"
                :loading="notificationLoading"
                @change="saveNotificationSettings"
              />
              <span class="setting-title">邮件通知</span>
            </div>
            <p class="setting-description">接收系统重要通知和更新</p>
          </div>

          <el-divider />

          <div class="setting-item">
            <div class="setting-header">
              <el-switch
                v-model="notificationSettings.security_alerts"
                :loading="notificationLoading"
                @change="saveNotificationSettings"
              />
              <span class="setting-title">安全警报</span>
            </div>
            <p class="setting-description">当账户有异常登录活动时通知</p>
          </div>

          <el-divider />

          <div class="setting-item">
            <div class="setting-header">
              <el-switch
                v-model="notificationSettings.api_usage_alerts"
                :loading="notificationLoading"
                @change="saveNotificationSettings"
              />
              <span class="setting-title">API使用警报</span>
            </div>
            <p class="setting-description">当API使用量接近限额时通知</p>
          </div>
        </div>
      </el-card>

      <!-- 主题设置 -->
      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>外观设置</span>
          </div>
        </template>

        <div class="theme-settings">
          <el-form-item label="主题模式">
            <el-radio-group v-model="themeSettings.mode" @change="saveThemeSettings">
              <el-radio value="light">
                <el-icon><Sunny /></el-icon>
                浅色模式
              </el-radio>
              <el-radio value="dark">
                <el-icon><Moon /></el-icon>
                深色模式
              </el-radio>
              <el-radio value="auto">
                <el-icon><Monitor /></el-icon>
                跟随系统
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="语言设置">
            <el-select v-model="themeSettings.language" @change="saveThemeSettings">
              <el-option label="简体中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
            </el-select>
          </el-form-item>
        </div>
      </el-card>
    </div>

    <!-- 创建API密钥对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建API密钥"
      width="500px"
      @close="resetCreateForm"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="密钥名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入密钥名称" :prefix-icon="Edit" />
        </el-form-item>

        <el-form-item label="权限" prop="permissions">
          <el-checkbox-group v-model="createForm.permissions">
            <el-checkbox
              v-for="permission in availablePermissions"
              :key="permission.value"
              :value="permission.value"
            >
              {{ permission.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="过期时间">
          <el-date-picker
            v-model="createForm.expires_at"
            type="datetime"
            placeholder="选择过期时间（可选）"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" :loading="createLoading" @click="createApiKey">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Lock, Key, Plus, Edit, CopyDocument, Sunny, Moon, Monitor } from '@element-plus/icons-vue'
import { apiClient, handleApiError } from '@/utils/api'
import { SM2CryptoUtil } from '@/utils/crypto'

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
const notificationLoading = ref(false)

const passwordFormRef = ref<FormInstance>()
const createFormRef = ref<FormInstance>()

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

const themeSettings = reactive({
  mode: 'light' as 'light' | 'dark' | 'auto',
  language: 'zh-CN',
})

const availablePermissions = [
  { label: '读取权限', value: 'read' },
  { label: '写入权限', value: 'write' },
  { label: '管理权限', value: 'admin' },
]

// 表单验证规则
const passwordRules = {
  current_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少8个字符', trigger: 'blur' },
    {
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      message: '密码必须包含大小写字母和数字',
      trigger: 'blur',
    },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

const createRules = {
  name: [
    { required: true, message: '请输入密钥名称', trigger: 'blur' },
    { min: 2, max: 50, message: '密钥名称长度在2-50个字符之间', trigger: 'blur' },
  ],
  permissions: [{ required: true, message: '请选择至少一个权限', trigger: 'change' }],
}

const isPasswordValid = computed(() => {
  return (
    passwordForm.current_password &&
    passwordForm.new_password &&
    passwordForm.new_password === passwordForm.confirm_password &&
    passwordForm.new_password.length >= 8
  )
})

// 获取过期状态
const getExpiryStatus = (expiresAt: string) => {
  const now = new Date()
  const expiry = new Date(expiresAt)
  const diffDays = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

  if (diffDays < 0) return '已过期'
  if (diffDays <= 7) return `${diffDays}天后过期`
  return '正常'
}

// 复制到剪贴板
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 加载API密钥
const loadApiKeys = async () => {
  try {
    const response = await apiClient.users.getApiKeys()
    if (response.data.success) {
      apiKeys.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载API密钥失败:', handleApiError(error))
    ElMessage.warning('加载API密钥失败')
  }
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    const valid = await passwordFormRef.value.validate()
    if (!valid) return
  } catch (error) {
    return
  }

  passwordLoading.value = true
  try {
    // 加密密码
    const encryptedCurrentPassword = await SM2CryptoUtil.encryptPassword(
      passwordForm.current_password,
    )
    const encryptedNewPassword = await SM2CryptoUtil.encryptPassword(passwordForm.new_password)

    await apiClient.users.changePassword({
      current_password: encryptedCurrentPassword,
      new_password: encryptedNewPassword,
    })

    resetPasswordForm()
    ElMessage.success('密码修改成功')
  } catch (error) {
    ElMessage.error('密码修改失败: ' + handleApiError(error))
  } finally {
    passwordLoading.value = false
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  Object.assign(passwordForm, {
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

// 创建API密钥
const createApiKey = async () => {
  if (!createFormRef.value) return

  try {
    const valid = await createFormRef.value.validate()
    if (!valid) return
  } catch (error) {
    return
  }

  createLoading.value = true
  try {
    const data = {
      name: createForm.name.trim(),
      permissions: createForm.permissions,
      expires_at: createForm.expires_at || undefined,
    }

    await apiClient.users.createApiKey(data)
    await loadApiKeys()
    showCreateDialog.value = false
    resetCreateForm()
    ElMessage.success('API密钥创建成功')
  } catch (error) {
    ElMessage.error('创建API密钥失败: ' + handleApiError(error))
  } finally {
    createLoading.value = false
  }
}

// 撤销API密钥
const revokeApiKey = async (keyId: string) => {
  loading.value = true
  try {
    await apiClient.users.revokeApiKey(keyId)
    await loadApiKeys()
    ElMessage.success('API密钥已撤销')
  } catch (error) {
    ElMessage.error('撤销API密钥失败: ' + handleApiError(error))
  } finally {
    loading.value = false
  }
}

// 保存通知设置
const saveNotificationSettings = async () => {
  notificationLoading.value = true
  try {
    // TODO: 实现保存通知设置的API
    await new Promise((resolve) => setTimeout(resolve, 1000))
    ElMessage.success('通知设置已保存')
  } catch (error) {
    ElMessage.error('保存设置失败')
  } finally {
    notificationLoading.value = false
  }
}

// 保存主题设置
const saveThemeSettings = async () => {
  try {
    // TODO: 实现保存主题设置的API
    localStorage.setItem('theme-settings', JSON.stringify(themeSettings))
    ElMessage.success('外观设置已保存')
  } catch (error) {
    ElMessage.error('保存设置失败')
  }
}

// 重置创建表单
const resetCreateForm = () => {
  Object.assign(createForm, {
    name: '',
    permissions: [],
    expires_at: '',
  })
  if (createFormRef.value) {
    createFormRef.value.clearValidate()
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 加载保存的设置
const loadSettings = () => {
  try {
    const savedTheme = localStorage.getItem('theme-settings')
    if (savedTheme) {
      Object.assign(themeSettings, JSON.parse(savedTheme))
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

onMounted(() => {
  loadApiKeys()
  loadSettings()
})
</script>

<style scoped>
.settings-view {
  padding: 24px;
  background-color: var(--el-bg-color-page);
  min-height: 100vh;
}

.settings-container {
  max-width: 1000px;
  margin: 24px auto 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-card {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.help-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.api-keys-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.api-key-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-fill-color-extra-light);
  transition: all 0.3s;
}

.api-key-item:hover {
  border-color: var(--el-border-color);
  background: var(--el-bg-color);
}

.key-info {
  flex: 1;
  margin-right: 16px;
}

.key-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.key-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 600;
}

.key-details {
  margin-bottom: 12px;
}

.permission-tag {
  margin-right: 6px;
  margin-bottom: 4px;
}

.key-value {
  margin-top: 12px;
}

.key-actions {
  flex-shrink: 0;
}

.notification-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-title {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.setting-description {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0;
  padding-left: 40px;
}

.theme-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.theme-settings .el-form-item {
  margin-bottom: 0;
}

.theme-settings .el-radio {
  margin-right: 16px;
  margin-bottom: 8px;
}

.theme-settings .el-radio .el-icon {
  margin-right: 6px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-view {
    padding: 16px;
  }

  .settings-container {
    margin-top: 16px;
    gap: 16px;
  }

  .api-key-item {
    flex-direction: column;
    gap: 16px;
  }

  .key-info {
    margin-right: 0;
  }

  .key-actions {
    align-self: stretch;
  }

  .setting-description {
    padding-left: 0;
  }

  .theme-settings .el-radio {
    margin-bottom: 12px;
    display: flex;
    align-items: center;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .api-key-item {
    background: var(--el-fill-color-darker);
  }

  .api-key-item:hover {
    background: var(--el-fill-color-dark);
  }
}
</style>
