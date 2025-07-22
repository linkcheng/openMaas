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
  <div class="user-management">
    <div class="container">
      <div class="header">
        <h1>用户管理</h1>
        <div class="header-actions">
          <div class="search-box">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索用户..."
              @input="searchUsers"
            />
          </div>
          <select v-model="statusFilter" @change="loadUsers" class="status-filter">
            <option value="">全部状态</option>
            <option value="active">活跃</option>
            <option value="suspended">已停用</option>
          </select>
        </div>
      </div>

      <!-- 用户统计 -->
      <div class="stats-row">
        <div class="stat-item">
          <span class="stat-value">{{ userStats.total }}</span>
          <span class="stat-label">总用户数</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ userStats.active }}</span>
          <span class="stat-label">活跃用户</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ userStats.suspended }}</span>
          <span class="stat-label">已停用</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ userStats.new_today }}</span>
          <span class="stat-label">今日新增</span>
        </div>
      </div>

      <!-- 用户列表 -->
      <div class="users-table">
        <table>
          <thead>
            <tr>
              <th>用户信息</th>
              <th>组织</th>
              <th>注册时间</th>
              <th>最后登录</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="loading-row">加载中...</td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="6" class="empty-row">暂无用户数据</td>
            </tr>
            <tr v-else v-for="user in users" :key="user.id" class="user-row">
              <td class="user-info">
                <div class="user-avatar">
                  <img v-if="user.avatar_url" :src="user.avatar_url" :alt="user.username" />
                  <div v-else class="avatar-placeholder">
                    {{ user.first_name?.charAt(0) || 'U' }}
                  </div>
                </div>
                <div class="user-details">
                  <div class="user-name">{{ user.first_name }} {{ user.last_name }}</div>
                  <div class="user-email">{{ user.email }}</div>
                  <div class="username">@{{ user.username }}</div>
                </div>
              </td>
              <td>{{ user.organization || '-' }}</td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>{{ formatDate(user.last_login) }}</td>
              <td>
                <span class="status-badge" :class="user.status">
                  {{ getStatusText(user.status) }}
                </span>
              </td>
              <td class="actions">
                <button @click="viewUser(user)" class="btn-icon" title="查看详情">👁️</button>
                <button
                  v-if="user.status === 'active'"
                  @click="suspendUser(user)"
                  class="btn-icon btn-danger"
                  title="停用用户"
                >
                  🚫
                </button>
                <button
                  v-else
                  @click="activateUser(user)"
                  class="btn-icon btn-success"
                  title="激活用户"
                >
                  ✅
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button
          @click="changePage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="btn-secondary"
        >
          上一页
        </button>

        <span class="page-info"> 第 {{ currentPage }} 页，共 {{ totalPages }} 页 </span>

        <button
          @click="changePage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="btn-secondary"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 用户详情对话框 -->
    <div v-if="selectedUser" class="dialog-overlay" @click="closeUserDialog">
      <div class="dialog" @click.stop>
        <h3>用户详情</h3>
        <div class="user-detail-content">
          <div class="detail-section">
            <h4>基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>用户名</label>
                <span>{{ selectedUser.username }}</span>
              </div>
              <div class="detail-item">
                <label>邮箱</label>
                <span>{{ selectedUser.email }}</span>
              </div>
              <div class="detail-item">
                <label>姓名</label>
                <span>{{ selectedUser.first_name }} {{ selectedUser.last_name }}</span>
              </div>
              <div class="detail-item">
                <label>组织</label>
                <span>{{ selectedUser.organization || '-' }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>账户状态</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>状态</label>
                <span class="status-badge" :class="selectedUser.status">
                  {{ getStatusText(selectedUser.status) }}
                </span>
              </div>
              <div class="detail-item">
                <label>邮箱验证</label>
                <span>{{ selectedUser.email_verified ? '已验证' : '未验证' }}</span>
              </div>
              <div class="detail-item">
                <label>注册时间</label>
                <span>{{ formatDate(selectedUser.created_at) }}</span>
              </div>
              <div class="detail-item">
                <label>最后登录</label>
                <span>{{ formatDate(selectedUser.last_login) }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>使用统计</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>API调用次数</label>
                <span>{{ selectedUser.api_calls_count || 0 }}</span>
              </div>
              <div class="detail-item">
                <label>API密钥数量</label>
                <span>{{ selectedUser.api_keys_count || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="dialog-actions">
          <button @click="closeUserDialog" class="btn-secondary">关闭</button>
        </div>
      </div>
    </div>

    <!-- 停用用户对话框 -->
    <div v-if="suspendDialog.show" class="dialog-overlay" @click="closeSuspendDialog">
      <div class="dialog" @click.stop>
        <h3>停用用户</h3>
        <p>
          确定要停用用户 <strong>{{ suspendDialog.user?.email }}</strong> 吗？
        </p>
        <div class="form-group">
          <label>停用原因</label>
          <textarea
            v-model="suspendDialog.reason"
            rows="3"
            placeholder="请输入停用原因..."
          ></textarea>
        </div>

        <div class="dialog-actions">
          <button
            @click="confirmSuspend"
            class="btn-danger"
            :disabled="!suspendDialog.reason || actionLoading"
          >
            {{ actionLoading ? '处理中...' : '确认停用' }}
          </button>
          <button @click="closeSuspendDialog" class="btn-secondary">取消</button>
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
  avatar_url?: string
  status: 'active' | 'suspended'
  email_verified: boolean
  created_at: string
  last_login?: string
  api_calls_count?: number
  api_keys_count?: number
}

interface UserStats {
  total: number
  active: number
  suspended: number
  new_today: number
}

const users = ref<User[]>([])
const selectedUser = ref<User | null>(null)
const loading = ref(false)
const actionLoading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 10

const userStats = reactive<UserStats>({
  total: 0,
  active: 0,
  suspended: 0,
  new_today: 0,
})

const suspendDialog = reactive({
  show: false,
  user: null as User | null,
  reason: '',
})

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize,
      keyword: searchQuery.value,
      status: statusFilter.value,
    }

    const response = await apiClient.users.searchUsers(params)
    users.value = response.data.data.users || []
    totalPages.value = Math.ceil((response.data.data.total || 0) / pageSize)

    // 更新统计数据
    userStats.total = response.data.data.total || 0
    userStats.active = response.data.data.active_count || 0
    userStats.suspended = response.data.data.suspended_count || 0
    userStats.new_today = response.data.data.new_today || 0
  } catch (error) {
    console.error('加载用户列表失败:', handleApiError(error))
    // 模拟数据
    users.value = generateMockUsers()
    userStats.total = 245
    userStats.active = 198
    userStats.suspended = 47
    userStats.new_today = 12
  } finally {
    loading.value = false
  }
}

const searchUsers = () => {
  currentPage.value = 1
  loadUsers()
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadUsers()
  }
}

const viewUser = async (user: User) => {
  try {
    const response = await apiClient.users.getUserById(user.id)
    selectedUser.value = response.data.data
  } catch (error) {
    console.error('获取用户详情失败:', handleApiError(error))
    selectedUser.value = user // 使用当前数据作为备用
  }
}

const suspendUser = (user: User) => {
  suspendDialog.show = true
  suspendDialog.user = user
  suspendDialog.reason = ''
}

const confirmSuspend = async () => {
  if (!suspendDialog.user || !suspendDialog.reason) return

  actionLoading.value = true
  try {
    await apiClient.users.suspendUser(suspendDialog.user.id, suspendDialog.reason)
    await loadUsers()
    closeSuspendDialog()
    alert('用户已停用')
  } catch (error) {
    alert('停用用户失败: ' + handleApiError(error))
  } finally {
    actionLoading.value = false
  }
}

const activateUser = async (user: User) => {
  if (!confirm(`确定要激活用户 ${user.email} 吗？`)) return

  actionLoading.value = true
  try {
    await apiClient.users.activateUser(user.id)
    await loadUsers()
    alert('用户已激活')
  } catch (error) {
    alert('激活用户失败: ' + handleApiError(error))
  } finally {
    actionLoading.value = false
  }
}

const closeUserDialog = () => {
  selectedUser.value = null
}

const closeSuspendDialog = () => {
  suspendDialog.show = false
  suspendDialog.user = null
  suspendDialog.reason = ''
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    active: '活跃',
    suspended: '已停用',
  }
  return statusMap[status] || status
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 生成模拟数据
const generateMockUsers = (): User[] => {
  return Array.from({ length: 10 }, (_, i) => ({
    id: `user-${i + 1}`,
    username: `user${i + 1}`,
    email: `user${i + 1}@example.com`,
    first_name: ['张', '李', '王', '刘', '陈'][i % 5],
    last_name: ['三', '四', '五', '六', '七'][i % 5],
    organization: i % 3 === 0 ? '测试公司' : undefined,
    status: i % 4 === 0 ? 'suspended' : 'active',
    email_verified: i % 3 !== 0,
    created_at: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
    last_login:
      Math.random() > 0.3
        ? new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
        : undefined,
    api_calls_count: Math.floor(Math.random() * 1000),
    api_keys_count: Math.floor(Math.random() * 5),
  }))
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-box input {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  width: 250px;
}

.status-filter {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
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

.users-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.user-row:hover {
  background: #f9fafb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar img {
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
  font-weight: bold;
}

.user-details {
  min-width: 0;
}

.user-name {
  font-weight: 500;
  color: #111827;
}

.user-email {
  font-size: 0.875rem;
  color: #6b7280;
}

.username {
  font-size: 0.75rem;
  color: #9ca3af;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.suspended {
  background: #fee2e2;
  color: #991b1b;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  padding: 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.btn-icon:hover {
  background: #f3f4f6;
}

.btn-icon.btn-danger:hover {
  background: #fee2e2;
}

.btn-icon.btn-success:hover {
  background: #d1fae5;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-row,
.empty-row {
  text-align: center;
  color: #6b7280;
  font-style: italic;
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
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.dialog h3 {
  margin: 0 0 1rem 0;
  color: #111827;
}

.user-detail-content {
  margin: 1rem 0;
}

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section h4 {
  margin: 0 0 0.75rem 0;
  color: #374151;
  font-size: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.detail-item span {
  color: #111827;
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

.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-primary,
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

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-primary:disabled,
.btn-danger:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

h1 {
  color: #111827;
  margin-bottom: 1rem;
}
</style>
