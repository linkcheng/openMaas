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
  <div v-if="hasPermission">
    <slot />
  </div>
  <div v-else-if="showFallback" class="permission-denied">
    <slot name="fallback">
      <div class="permission-denied-content">
        <div class="permission-denied-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
            />
          </svg>
        </div>
        <h3 class="permission-denied-title">权限不足</h3>
        <p class="permission-denied-message">{{ errorMessage }}</p>
        <button v-if="showContactAdmin" @click="contactAdmin" class="btn btn-secondary btn-sm">
          联系管理员
        </button>
      </div>
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { ElMessage } from 'element-plus'

interface Props {
  // 权限检查方式
  resource?: string
  action?: string
  role?: string
  customCheck?: () => boolean

  // 显示选项
  showFallback?: boolean
  errorMessage?: string
  showContactAdmin?: boolean

  // 逻辑操作符
  operator?: 'and' | 'or'

  // 多个权限检查
  permissions?: Array<{
    resource: string
    action: string
  }>
  roles?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  showFallback: false,
  errorMessage: '您没有权限访问此内容',
  showContactAdmin: false,
  operator: 'and',
})

const { hasPermission: checkPermission, hasRole: checkRole, isAuthenticated } = useAuth()

// 权限检查逻辑 - 暂时简化，只要用户已认证就允许访问
const hasPermission = computed(() => {
  // 只检查用户是否已认证
  return isAuthenticated.value
})

// 联系管理员
const contactAdmin = () => {
  ElMessage.info('请联系系统管理员获取相应权限')
}
</script>

<style scoped>
.permission-denied {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  min-height: 200px;
}

.permission-denied-content {
  text-align: center;
  max-width: 400px;
}

.permission-denied-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--space-md);
  color: var(--color-text-secondary);
  opacity: 0.6;
}

.permission-denied-icon svg {
  width: 100%;
  height: 100%;
}

.permission-denied-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-sm) 0;
}

.permission-denied-message {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-md) 0;
  line-height: 1.5;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary {
  background-color: var(--maas-white);
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.btn-secondary:hover {
  background-color: var(--color-background-soft);
  border-color: var(--color-border-hover);
}

.btn-sm {
  padding: var(--space-xs) var(--space-sm);
  font-size: 0.8125rem;
}
</style>
