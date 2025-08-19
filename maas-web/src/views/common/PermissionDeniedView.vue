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
  <div class="permission-denied-page">
    <div class="permission-denied-container">
      <!-- 图标 -->
      <div class="permission-denied-icon">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm4.59-12.42L10 14.17l-2.59-2.58L6 13l4 4 8-8-1.41-1.42z"
          />
        </svg>
      </div>

      <!-- 标题和描述 -->
      <h1 class="permission-denied-title">访问被拒绝</h1>
      <p class="permission-denied-description">
        {{ message || '您没有权限访问此页面，请联系管理员获取相应权限。' }}
      </p>

      <!-- 错误详情 -->
      <div v-if="showDetails" class="permission-details">
        <h3>权限要求：</h3>
        <ul>
          <li v-if="requiredRole">角色：{{ requiredRole }}</li>
          <li v-if="requiredPermission">权限：{{ requiredPermission }}</li>
        </ul>
      </div>

      <!-- 操作按钮 -->
      <div class="permission-actions">
        <button @click="goBack" class="btn btn-secondary">
          <svg class="icon" viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
              clip-rule="evenodd"
            />
          </svg>
          返回上页
        </button>

        <button @click="goHome" class="btn btn-primary">
          <svg class="icon" viewBox="0 0 20 20" fill="currentColor">
            <path
              d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"
            />
          </svg>
          回到首页
        </button>

        <button v-if="showContactAdmin" @click="contactAdmin" class="btn btn-outline">
          <svg class="icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
            <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
          </svg>
          联系管理员
        </button>
      </div>

      <!-- 用户信息 -->
      <div v-if="showUserInfo && currentUser" class="user-info">
        <p class="user-info-text">
          当前用户：{{ currentUser.profile.full_name || currentUser.username }}
          <span v-if="currentUser.roles.length > 0">
            （{{ currentUser.roles.map((r) => r.name).join(', ') }}）
          </span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuth } from '@/composables/useAuth'

interface Props {
  message?: string
  requiredRole?: string
  requiredPermission?: string
  showDetails?: boolean
  showContactAdmin?: boolean
  showUserInfo?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: false,
  showContactAdmin: true,
  showUserInfo: true,
})

const router = useRouter()
const { currentUser } = useAuth()

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}

// 回到首页
const goHome = () => {
  router.push('/dashboard')
}

// 联系管理员
const contactAdmin = () => {
  ElMessage.info('请通过系统内消息或邮件联系管理员申请权限')
  // 这里可以集成实际的联系管理员功能
  // 比如打开工单系统、发送邮件等
}
</script>

<style scoped>
.permission-denied-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background);
  padding: var(--space-lg);
}

.permission-denied-container {
  max-width: 600px;
  text-align: center;
  background: var(--maas-white);
  padding: var(--space-2xl);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

.permission-denied-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-xl);
  color: var(--maas-red-500);
  opacity: 0.8;
}

.permission-denied-icon svg {
  width: 100%;
  height: 100%;
}

.permission-denied-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-md) 0;
}

.permission-denied-description {
  font-size: 1.125rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--space-xl) 0;
}

.permission-details {
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  margin: 0 0 var(--space-xl) 0;
  text-align: left;
}

.permission-details h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-sm) 0;
}

.permission-details ul {
  margin: 0;
  padding-left: var(--space-lg);
  color: var(--color-text-secondary);
}

.permission-details li {
  margin-bottom: var(--space-xs);
}

.permission-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: var(--space-xl);
}

.user-info {
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border);
}

.user-info-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
}

.btn-primary {
  background-color: var(--maas-primary-600);
  color: var(--maas-white);
  border-color: var(--maas-primary-600);
}

.btn-primary:hover {
  background-color: var(--maas-primary-700);
  border-color: var(--maas-primary-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background-color: var(--maas-white);
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.btn-secondary:hover {
  background-color: var(--color-background-soft);
  border-color: var(--color-border-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn-outline {
  background-color: transparent;
  color: var(--maas-primary-600);
  border-color: var(--maas-primary-600);
}

.btn-outline:hover {
  background-color: var(--maas-primary-50);
  border-color: var(--maas-primary-700);
  color: var(--maas-primary-700);
}

.icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .permission-denied-container {
    padding: var(--space-lg);
    margin: var(--space-md);
  }

  .permission-denied-title {
    font-size: 1.5rem;
  }

  .permission-denied-description {
    font-size: 1rem;
  }

  .permission-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .btn {
    justify-content: center;
  }
}
</style>
