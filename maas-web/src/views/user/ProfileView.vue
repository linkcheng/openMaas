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
    <div class="container">
      <h1>用户资料</h1>

      <div class="profile-card">
        <div class="avatar-section">
          <div class="avatar">
            <img v-if="user?.avatar_url" :src="user.avatar_url" :alt="user.username" />
            <div v-else class="avatar-placeholder">
              {{ user?.first_name?.charAt(0) || 'U' }}
            </div>
          </div>
          <button class="btn-secondary">更换头像</button>
        </div>

        <div class="info-section">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="form.username" type="text" :disabled="!isEditing" />
          </div>

          <div class="form-group">
            <label>邮箱</label>
            <input v-model="form.email" type="email" disabled />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>姓名</label>
              <input v-model="form.first_name" type="text" :disabled="!isEditing" />
            </div>

            <div class="form-group">
              <label>姓氏</label>
              <input v-model="form.last_name" type="text" :disabled="!isEditing" />
            </div>
          </div>

          <div class="form-group">
            <label>组织</label>
            <input v-model="form.organization" type="text" :disabled="!isEditing" />
          </div>

          <div class="form-group">
            <label>个人简介</label>
            <textarea v-model="form.bio" rows="3" :disabled="!isEditing"></textarea>
          </div>

          <div class="form-actions">
            <button v-if="!isEditing" @click="isEditing = true" class="btn-primary">
              编辑资料
            </button>
            <template v-else>
              <button @click="saveProfile" class="btn-primary" :disabled="loading">
                {{ loading ? '保存中...' : '保存' }}
              </button>
              <button @click="cancelEdit" class="btn-secondary">取消</button>
            </template>
          </div>
        </div>
      </div>

      <div class="stats-section">
        <h2>使用统计</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-value">{{ stats?.total_requests || 0 }}</span>
            <span class="stat-label">总请求数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats?.api_keys_count || 0 }}</span>
            <span class="stat-label">API密钥数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ formatDate(user?.created_at) }}</span>
            <span class="stat-label">注册时间</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { apiClient, handleApiError } from '@/utils/api'

interface User {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  organization?: string
  bio?: string
  avatar_url?: string
  created_at: string
}

interface Stats {
  total_requests: number
  api_keys_count: number
}

const user = ref<User | null>(null)
const stats = ref<Stats | null>(null)
const isEditing = ref(false)
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  organization: '',
  bio: '',
})

const loadProfile = async () => {
  try {
    const response = await apiClient.users.getProfile()
    user.value = response.data.data
    Object.assign(form, user.value)
  } catch (error) {
    console.error('加载用户资料失败:', handleApiError(error))
  }
}

const loadStats = async () => {
  try {
    const response = await apiClient.users.getStats()
    stats.value = response.data.data
  } catch (error) {
    console.error('加载统计数据失败:', handleApiError(error))
  }
}

const saveProfile = async () => {
  loading.value = true
  try {
    const updateData = {
      first_name: form.first_name,
      last_name: form.last_name,
      organization: form.organization,
      bio: form.bio,
    }

    const response = await apiClient.users.updateProfile(updateData)
    user.value = response.data.data
    isEditing.value = false
  } catch (error) {
    console.error('保存用户资料失败:', handleApiError(error))
  } finally {
    loading.value = false
  }
}

const cancelEdit = () => {
  isEditing.value = false
  Object.assign(form, user.value)
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadProfile()
  loadStats()
})
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: flex;
  gap: 2rem;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e5e7eb;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: #6366f1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
}

.info-section {
  flex: 1;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:disabled,
.form-group textarea:disabled {
  background: #f9fafb;
  color: #6b7280;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
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

.stats-section {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 4px;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #6366f1;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

h1,
h2 {
  color: #111827;
  margin-bottom: 1rem;
}
</style>
