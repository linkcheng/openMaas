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
  <el-aside
    :width="collapsed ? '64px' : '240px'"
    class="app-sidebar"
    :class="{ 'is-collapsed': collapsed }"
  >
    <!-- 平台标题 -->
    <div class="sidebar-header">
      <div class="brand" @click="goToHome">
        <el-icon class="brand-icon" :size="24" color="var(--el-color-primary)">
          <TrendCharts />
        </el-icon>
        <h1 v-show="!collapsed" class="brand-title">AI MaaS 平台</h1>
      </div>

      <!-- 折叠按钮 -->
      <el-button
        :icon="collapsed ? Expand : Fold"
        circle
        size="small"
        class="collapse-button"
        @click="toggleCollapse"
      />
    </div>

    <!-- 导航菜单 -->
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="collapsed"
      :collapse-transition="true"
      router
      @select="handleMenuSelect"
    >
      <!-- 仪表盘 -->
      <el-menu-item index="/dashboard">
        <el-icon><HomeFilled /></el-icon>
        <template #title>仪表盘</template>
      </el-menu-item>

      <!-- 数据管理 -->
      <el-menu-item index="/data-management">
        <el-icon><FolderOpened /></el-icon>
        <template #title>数据管理</template>
      </el-menu-item>

      <!-- 模型相关 -->
      <el-sub-menu index="model">
        <template #title>
          <el-icon><Operation /></el-icon>
          <span>模型服务</span>
        </template>
        <el-menu-item index="/model-management">
          <el-icon><Box /></el-icon>
          <template #title>模型管理</template>
        </el-menu-item>
        <el-menu-item index="/model-finetune">
          <el-icon><Setting /></el-icon>
          <template #title>模型微调</template>
        </el-menu-item>
        <el-menu-item index="/model-deployment">
          <el-icon><Cloudy /></el-icon>
          <template #title>模型部署</template>
        </el-menu-item>
        <el-menu-item index="/model-inference">
          <el-icon><Lightning /></el-icon>
          <template #title>模型推理</template>
        </el-menu-item>
      </el-sub-menu>

      <!-- 知识库管理 -->
      <el-menu-item index="/knowledge-base">
        <el-icon><Reading /></el-icon>
        <template #title>知识库管理</template>
      </el-menu-item>

      <!-- 应用相关 -->
      <el-sub-menu index="application">
        <template #title>
          <el-icon><Grid /></el-icon>
          <span>应用服务</span>
        </template>
        <el-menu-item index="/application-management">
          <el-icon><Management /></el-icon>
          <template #title>应用管理</template>
        </el-menu-item>
        <el-menu-item index="/application-scenarios">
          <el-icon><Connection /></el-icon>
          <template #title>应用场景</template>
        </el-menu-item>
      </el-sub-menu>

      <!-- 管理员功能 -->
      <template v-if="isAdmin">
        <el-divider class="menu-divider" />
        <el-sub-menu index="admin">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/admin/dashboard">
            <el-icon><Monitor /></el-icon>
            <template #title>管理后台</template>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><UserFilled /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/audit-logs">
            <el-icon><Document /></el-icon>
            <template #title>系统日志</template>
          </el-menu-item>
        </el-sub-menu>
      </template>
    </el-menu>

    <!-- 底部信息 -->
    <div v-show="!collapsed" class="sidebar-footer">
      <div class="footer-info">
        <el-text type="info" size="small"> © 2024 AI MaaS 平台 </el-text>
      </div>
    </div>
  </el-aside>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  TrendCharts,
  Expand,
  Fold,
  HomeFilled,
  FolderOpened,
  Operation,
  Box,
  Setting,
  Cloudy,
  Lightning,
  Reading,
  Grid,
  Management,
  Connection,
  Tools,
  Monitor,
  UserFilled,
  Document,
} from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { isAdmin } = useAuth()

const collapsed = ref(false)
const activeMenu = ref(route.path)

// 监听路由变化更新活跃菜单
watch(
  () => route.path,
  (newPath) => {
    activeMenu.value = newPath
  },
)

const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
}

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.app-sidebar {
  background: var(--el-bg-color-overlay);
  border-right: 1px solid var(--el-border-color);
  height: 100vh;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  position: relative;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color);
  min-height: 60px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
  cursor: pointer;
  transition: opacity 0.2s;
}

.brand:hover {
  opacity: 0.8;
}

.brand-icon {
  flex-shrink: 0;
}

.brand-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.collapse-button {
  flex-shrink: 0;
  background: transparent;
  border: none;
  color: var(--el-text-color-regular);
}

.collapse-button:hover,
.collapse-button:focus {
  color: var(--el-color-primary);
  background: var(--el-fill-color-light);
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 2px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-darker);
}

.menu-divider {
  margin: 8px 16px;
  border-color: var(--el-border-color);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--el-border-color);
  background: var(--el-bg-color);
}

.footer-info {
  text-align: center;
}

/* 折叠状态样式 */
.is-collapsed .sidebar-header {
  padding: 16px 12px;
  justify-content: center;
}

.is-collapsed .brand {
  justify-content: center;
}

.is-collapsed .collapse-button {
  position: absolute;
  top: 20px;
  right: 8px;
  z-index: 10;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    height: calc(100vh - 60px);
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }

  .app-sidebar.is-mobile-open {
    transform: translateX(0);
  }

  .app-sidebar:not(.is-collapsed) {
    width: 240px !important;
  }
}

/* Element Plus 菜单自定义样式 */
.sidebar-menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 4px 8px;
  border-radius: 8px;
  color: var(--el-text-color-regular);
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary-light-8);
  font-weight: 500;
}

.sidebar-menu :deep(.el-sub-menu .el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  margin: 4px 8px;
  border-radius: 8px;
  color: var(--el-text-color-regular);
}

.sidebar-menu :deep(.el-sub-menu .el-sub-menu__title:hover) {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  margin: 2px 8px;
  padding-left: 48px !important;
}

.sidebar-menu :deep(.el-menu--collapse .el-sub-menu .el-menu-item) {
  padding-left: 20px !important;
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .app-sidebar {
    background: var(--el-bg-color-page);
  }

  .sidebar-footer {
    background: var(--el-bg-color-overlay);
  }
}
</style>
