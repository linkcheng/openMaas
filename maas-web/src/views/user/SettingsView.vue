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

    </div>

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
