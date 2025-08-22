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
  <div class="profile-view">
    <el-page-header @back="$router.back()" content="个人资料" />

    <div class="profile-container">
      <!-- 基本信息卡片 -->
      <el-card class="profile-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-button v-if="!isEditing" type="primary" :icon="Edit" @click="startEdit">
              编辑资料
            </el-button>
            <div v-else class="edit-actions">
              <el-button type="primary" :loading="loading" @click="saveProfile"> 保存 </el-button>
              <el-button @click="cancelEdit">取消</el-button>
            </div>
          </div>
        </template>

        <div class="profile-content">
          <!-- 头像区域 -->
          <div class="avatar-section">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="uploadAvatar"
              :disabled="!isEditing"
            >
              <el-avatar
                :size="120"
                :src="user?.profile?.avatar_url || form.avatar_url"
                class="avatar"
              >
                <el-icon :size="40">
                  <UserFilled />
                </el-icon>
              </el-avatar>
              <div v-if="isEditing" class="avatar-overlay">
                <el-icon :size="24">
                  <Camera />
                </el-icon>
                <span>更换头像</span>
              </div>
            </el-upload>
          </div>

          <!-- 表单区域 -->
          <div class="form-section">
            <el-form
              :model="form"
              :rules="rules"
              ref="formRef"
              label-width="100px"
              label-position="left"
            >
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="用户名" prop="username">
                    <el-input v-model="form.username" :disabled="true" :prefix-icon="User" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="form.email" :disabled="true" :prefix-icon="Message" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="姓名" prop="first_name">
                    <el-input
                      v-model="form.first_name"
                      :disabled="!isEditing"
                      placeholder="请输入姓名"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="姓氏" prop="last_name">
                    <el-input
                      v-model="form.last_name"
                      :disabled="!isEditing"
                      placeholder="请输入姓氏"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="组织机构" prop="organization">
                <el-input
                  v-model="form.organization"
                  :disabled="!isEditing"
                  :prefix-icon="OfficeBuilding"
                  placeholder="请输入组织机构"
                />
              </el-form-item>

              <el-form-item label="个人简介" prop="bio">
                <el-input
                  v-model="form.bio"
                  :disabled="!isEditing"
                  type="textarea"
                  :rows="4"
                  placeholder="请介绍一下自己..."
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-card>

      <!-- 账户信息卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span>账户信息</span>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">
            <el-tag type="info">{{ user?.id || '-' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">
            {{ formatDateTime(user?.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后登录">
            {{ formatDateTime(user?.last_login_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="账户状态">
            <el-tag :type="user?.status === 'active' ? 'success' : 'danger'">
              {{ user?.status === 'active' ? '正常' : '已禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="邮箱验证">
            <el-tag :type="user?.email_verified ? 'success' : 'warning'">
              {{ user?.email_verified ? '已验证' : '未验证' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="450px"
      @close="resetPasswordDialog"
    >
      <el-form
        :model="passwordForm"
        :rules="passwordRules"
        ref="passwordFormRef"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="current_password">
          <el-input
            v-model="passwordForm.current_password"
            type="password"
            :prefix-icon="Lock"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            :prefix-icon="Key"
            placeholder="请输入新密码"
            show-password
          />
          <div class="help-text">密码至少8个字符，包含大小写字母和数字</div>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            :prefix-icon="Key"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPasswordDialog = false">取消</el-button>
          <el-button type="primary" :loading="passwordLoading" @click="changePassword">
            修改密码
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type UploadRequestOptions,
  type UploadRawFile,
} from 'element-plus'
import {
  Edit,
  UserFilled,
  Camera,
  User,
  Message,
  OfficeBuilding,
  DataAnalysis,
  Key,
  Calendar,
  TrendCharts,
  Lock,
} from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'
import { apiClient, handleApiError } from '@/utils/api'
import { SM2CryptoUtil } from '@/utils/crypto'

interface User {
  id: string
  username: string
  email: string
  profile: {
    first_name: string
    last_name: string
    full_name: string
    avatar_url?: string
    organization?: string
    bio?: string
  }
  status: string
  email_verified: boolean
  two_factor_enabled?: boolean
  password_updated_at?: string
  roles: {
    id: string
    name: string
    description: string
    permissions: string[]
  }[]
  created_at: string
  updated_at: string
  last_login_at?: string
}

interface Stats {
  total_requests: number
  api_keys_count: number
  success_rate: number
}

const { currentUser: authUser } = useAuth()
const user = ref<User | null>(null)
const stats = ref<Stats | null>(null)
const isEditing = ref(false)
const loading = ref(false)
const passwordLoading = ref(false)
const showPasswordDialog = ref(false)
const formRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  organization: '',
  bio: '',
  avatar_url: '',
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const rules = {
  first_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 50, message: '姓名长度在1-50个字符之间', trigger: 'blur' },
    {
      pattern: /^[\u4e00-\u9fa5a-zA-Z\s]+$/,
      message: '姓名只能包含中文、英文字母和空格',
      trigger: 'blur',
    },
  ],
  last_name: [
    { min: 0, max: 50, message: '姓氏长度不能超过50个字符', trigger: 'blur' },
    {
      pattern: /^[\u4e00-\u9fa5a-zA-Z\s]*$/,
      message: '姓氏只能包含中文、英文字母和空格',
      trigger: 'blur',
    },
  ],
  organization: [{ max: 100, message: '组织机构名称不能超过100个字符', trigger: 'blur' }],
  bio: [{ max: 500, message: '个人简介不能超过500个字符', trigger: 'blur' }],
}

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

const loadProfile = async () => {
  try {
    // 调用 /users/me API 获取当前用户信息
    const response = await apiClient.users.getProfile()

    if (response.data.success && response.data.data) {
      const userData = response.data.data as User
      user.value = userData

      // 将用户数据映射到表单，优先使用 profile 中的信息
      Object.assign(form, {
        username: userData.username || '',
        email: userData.email || '',
        first_name: userData.profile?.first_name || '',
        last_name: userData.profile?.last_name || '',
        organization: userData.profile?.organization || '',
        bio: userData.profile?.bio || '',
        avatar_url: userData.profile?.avatar_url || '',
      })
    } else {
      throw new Error(response.data.message || '获取用户信息失败')
    }
  } catch (error) {
    const errorMessage = handleApiError(error)
    ElMessage.error(`加载用户资料失败: ${errorMessage}`)
    console.error('加载用户资料失败:', error)

    // 如果 API 调用失败，尝试使用 auth 中的用户信息作为备用
    if (authUser.value) {
      const userData = authUser.value
      user.value = userData
      Object.assign(form, {
        username: userData.username || '',
        email: userData.email || '',
        first_name: userData.profile?.first_name || '',
        last_name: userData.profile?.last_name || '',
        organization: userData.profile?.organization || '',
        bio: userData.profile?.bio || '',
        avatar_url: userData.profile?.avatar_url || '',
      })
    } else {
      // 如果都没有，使用默认值
      user.value = null
      Object.assign(form, {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        organization: '',
        bio: '',
        avatar_url: '',
      })
    }
  }
}

const startEdit = () => {
  isEditing.value = true
}

const saveProfile = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) {
      ElMessage.warning('请检查输入信息')
      return
    }
  } catch (error) {
    ElMessage.warning('请检查输入信息')
    return
  }

  loading.value = true
  try {
    // 准备更新数据，只发送有值的字段，过滤空字符串
    const updateData: any = {}

    if (form.first_name && form.first_name.trim()) {
      updateData.first_name = form.first_name.trim()
    }
    if (form.last_name && form.last_name.trim()) {
      updateData.last_name = form.last_name.trim()
    }
    if (form.organization && form.organization.trim()) {
      updateData.organization = form.organization.trim()
    }
    if (form.bio && form.bio.trim()) {
      updateData.bio = form.bio.trim()
    }
    if (form.avatar_url) {
      updateData.avatar_url = form.avatar_url
    }

    console.log('发送更新数据:', updateData)

    // 调用 /users/me API 更新用户资料
    const response = await apiClient.users.updateProfile(updateData)

    console.log('更新响应:', response.data)

    if (response.data.success) {
      // 更新成功后，重新加载用户信息
      await loadProfile()
      isEditing.value = false
      ElMessage.success('保存成功')
    } else {
      throw new Error(response.data.message || '保存失败')
    }
  } catch (error) {
    const errorMessage = handleApiError(error)
    ElMessage.error(`保存失败: ${errorMessage}`)
    console.error('保存用户资料失败:', error)
    console.error('错误详情:', (error as any)?.response?.data)
  } finally {
    loading.value = false
  }
}

const cancelEdit = async () => {
  // 检查是否有未保存的更改
  const originalData = {
    first_name: user.value?.profile?.first_name || '',
    last_name: user.value?.profile?.last_name || '',
    organization: user.value?.profile?.organization || '',
    bio: user.value?.profile?.bio || '',
    avatar_url: user.value?.profile?.avatar_url || '',
  }

  const currentData = {
    first_name: form.first_name,
    last_name: form.last_name,
    organization: form.organization,
    bio: form.bio,
    avatar_url: form.avatar_url,
  }

  const hasChanges = JSON.stringify(originalData) !== JSON.stringify(currentData)

  if (hasChanges) {
    const result = await ElMessageBox.confirm('您有未保存的更改，确定要取消编辑吗？', '确认取消', {
      confirmButtonText: '确定',
      cancelButtonText: '继续编辑',
      type: 'warning',
    }).catch(() => false)

    if (!result) return
  }

  isEditing.value = false
  // 重置表单数据到原始状态
  if (user.value) {
    Object.assign(form, {
      username: user.value.username || '',
      email: user.value.email || '',
      first_name: user.value.profile?.first_name || '',
      last_name: user.value.profile?.last_name || '',
      organization: user.value.profile?.organization || '',
      bio: user.value.profile?.bio || '',
      avatar_url: user.value.profile?.avatar_url || '',
    })
  }

  // 清除表单验证状态
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const beforeAvatarUpload = (rawFile: UploadRawFile) => {
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(rawFile.type)) {
    ElMessage.error('头像只能是 JPG、PNG、GIF 或 WebP 格式!')
    return false
  }

  // 检查文件大小 (2MB)
  const isLt2M = rawFile.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }

  // 检查图片尺寸
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      const { width, height } = img

      // 建议尺寸不超过 1000x1000
      if (width > 1000 || height > 1000) {
        ElMessage.warning('建议上传尺寸不超过 1000x1000 的图片以获得更好的效果')
      }

      resolve(true)
    }
    img.onerror = () => {
      ElMessage.error('无法读取图片文件')
      resolve(false)
    }
    img.src = URL.createObjectURL(rawFile)
  })
}

const uploadAvatar = async (options: UploadRequestOptions) => {
  // 临时的加载消息ID
  let loadingMessage: any

  try {
    loadingMessage = ElMessage.loading('头像上传中...')

    const formData = new FormData()
    formData.append('avatar', options.file)

    // TODO: 实现真实的上传 API，目前使用模拟
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // 模拟成功响应
    const fakeUrl = URL.createObjectURL(options.file)
    form.avatar_url = fakeUrl

    if (loadingMessage) {
      loadingMessage.close()
    }
    ElMessage.success('头像上传成功')
    options.onSuccess?.({ avatar_url: fakeUrl })
  } catch (error) {
    if (loadingMessage) {
      loadingMessage.close()
    }
    const errorMessage = handleApiError(error)
    ElMessage.error(`头像上传失败: ${errorMessage}`)
    console.error('头像上传失败:', error)

    options.onError?.(error as any)
  }
}

const formatDateTime = (dateString?: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const getDaysFromRegistration = () => {
  if (!user.value?.created_at) return 0
  const now = new Date()
  const created = new Date(user.value.created_at)
  const diffTime = Math.abs(now.getTime() - created.getTime())
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
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

    resetPasswordDialog()
    showPasswordDialog.value = false
    ElMessage.success('密码修改成功')
  } catch (error) {
    ElMessage.error('密码修改失败: ' + handleApiError(error))
  } finally {
    passwordLoading.value = false
  }
}

// 重置密码对话框
const resetPasswordDialog = () => {
  Object.assign(passwordForm, {
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-view {
  padding: 24px;
  background-color: var(--el-bg-color-page);
  min-height: 100vh;
}

.profile-container {
  max-width: 1200px;
  margin: 24px auto 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.edit-actions {
  display: flex;
  gap: 12px;
}

.profile-content {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.avatar-section {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatar-uploader {
  position: relative;
  cursor: pointer;
}

.avatar {
  border: 3px solid var(--el-border-color);
  transition: border-color 0.3s;
}

.avatar-uploader:hover .avatar {
  border-color: var(--el-color-primary);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-uploader:hover .avatar-overlay {
  opacity: 1;
}

.form-section {
  flex: 1;
  min-width: 0;
}

.info-card,
.stats-card {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
}

.role-tag {
  margin-right: 8px;
  margin-bottom: 4px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--el-fill-color-extra-light);
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.help-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-view {
    padding: 16px;
  }

  .profile-container {
    margin-top: 16px;
    gap: 16px;
  }

  .profile-content {
    flex-direction: column;
    gap: 24px;
  }

  .avatar-section {
    align-self: center;
  }

  .stat-item {
    padding: 16px;
  }

  .stat-value {
    font-size: 20px;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .stat-item {
    background: var(--el-fill-color-darker);
  }
}
</style>
