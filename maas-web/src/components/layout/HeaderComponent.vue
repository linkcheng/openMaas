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
  <el-header class="app-header">
    <div class="header-content">
      <!-- 左侧搜索区域 -->
      <div class="header-left">
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="搜索模型、应用、知识库..."
            :prefix-icon="Search"
            class="search-input"
            clearable
          />
        </div>
      </div>

      <!-- 右侧用户区域 -->
      <div class="header-right">
        <!-- 通知 -->
        <el-badge
          :value="notificationCount"
          :hidden="notificationCount === 0"
          class="notification-badge"
        >
          <el-button
            :icon="Bell"
            circle
            size="large"
            class="header-button"
            @click="showNotifications"
          />
        </el-badge>

        <!-- 设置 -->
        <el-button
          :icon="Setting"
          circle
          size="large"
          class="header-button"
          @click="showSettings"
        />

        <!-- 用户信息下拉菜单 -->
        <el-dropdown @command="handleUserMenuCommand" class="user-dropdown">
          <div class="user-info">
            <el-avatar :size="32" :src="currentUser?.profile?.avatar_url" class="user-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="username">{{ displayUsername }}</span>
            <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile" :icon="User"> 个人资料 </el-dropdown-item>
              <el-dropdown-item command="settings" :icon="Setting"> 设置 </el-dropdown-item>
              <el-dropdown-item divided command="logout" :icon="SwitchButton">
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Bell, Setting, User, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { currentUser, logout, getCurrentUser, isAuthenticated } = useAuth()

const searchQuery = ref('')
const notificationCount = ref(3)

// 计算用户显示名称
const displayUsername = computed(() => {
  if (!isAuthenticated.value) return '未登录'
  if (!currentUser.value) return '加载中...'
  return currentUser.value.username || currentUser.value.profile?.full_name || '用户'
})

// 组件挂载时确保用户信息已加载
onMounted(async () => {
  if (isAuthenticated.value && !currentUser.value) {
    try {
      await getCurrentUser()
    } catch (error) {
      console.warn('获取用户信息失败:', error)
    }
  }
})

const showNotifications = () => {
  ElMessage.info('通知功能开发中')
}

const showSettings = () => {
  router.push('/user/settings')
}

const handleUserMenuCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'settings':
      router.push('/user/settings')
      break
    case 'logout':
      try {
        await logout()
        ElMessage.success('退出登录成功')
        router.push('/auth/login')
      } catch {
        ElMessage.error('退出登录失败')
      }
      break
    default:
      break
  }
}
</script>

<style scoped>
.app-header {
  background: var(--el-bg-color-overlay);
  border-bottom: 1px solid var(--el-border-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  height: 60px;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.search-container {
  max-width: 400px;
  width: 100%;
}

.search-input {
  border-radius: 20px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 20px;
  background-color: var(--el-fill-color-light);
  border: none;
  box-shadow: none;
}

.search-input :deep(.el-input__wrapper:hover),
.search-input :deep(.el-input__wrapper.is-focus) {
  background-color: var(--el-fill-color);
  box-shadow: 0 0 0 1px var(--el-color-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-button {
  color: var(--el-text-color-regular);
  border: none;
  background: transparent;
}

.header-button:hover,
.header-button:focus {
  color: var(--el-color-primary);
  background: var(--el-fill-color-light);
}

.notification-badge :deep(.el-badge__content) {
  border: 2px solid var(--el-bg-color-overlay);
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: var(--el-fill-color-light);
}

.user-avatar {
  background-color: var(--el-color-primary);
}

.username {
  color: var(--el-text-color-primary);
  font-size: 14px;
  font-weight: 500;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  transition: transform 0.2s;
}

.user-dropdown:hover .dropdown-icon {
  color: var(--el-text-color-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }

  .search-container {
    max-width: 200px;
  }

  .username {
    display: none;
  }

  .header-right {
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .search-container {
    max-width: 150px;
  }

  .search-input :deep(.el-input__wrapper) {
    font-size: 12px;
  }
}
</style>
