<template>
  <div class="permission-layout">
    <div class="permission-header">
      <h2 class="page-title">权限管理</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item to="/admin/dashboard">管理后台</el-breadcrumb-item>
        <el-breadcrumb-item>权限管理</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentPageTitle">{{ currentPageTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="permission-content">
      <div class="permission-sidebar">
        <el-menu
          :default-active="activeMenu"
          @select="handleMenuSelect"
          class="permission-menu"
        >
          <el-menu-item index="roles">
            <el-icon><UserFilled /></el-icon>
            <span>角色管理</span>
          </el-menu-item>
          <el-menu-item index="permissions">
            <el-icon><Key /></el-icon>
            <span>权限管理</span>
          </el-menu-item>
          <el-menu-item index="user-roles">
            <el-icon><User /></el-icon>
            <span>用户权限</span>
          </el-menu-item>
        </el-menu>
      </div>

      <div class="permission-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMenu, ElMenuItem, ElIcon, ElBreadcrumb, ElBreadcrumbItem } from 'element-plus'
import { UserFilled, Key, User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 当前激活的菜单项
const activeMenu = computed(() => {
  const routeName = route.name as string
  if (routeName?.includes('role')) return 'roles'
  if (routeName?.includes('permission')) return 'permissions'
  if (routeName?.includes('user-role')) return 'user-roles'
  return 'roles'
})

// 当前页面标题
const currentPageTitle = computed(() => {
  const routeName = route.name as string
  const titleMap: Record<string, string> = {
    'permission-roles': '角色管理',
    'permission-permissions': '权限管理',
    'permission-user-roles': '用户权限',
  }
  return titleMap[routeName] || ''
})

// 菜单选择处理
const handleMenuSelect = (index: string) => {
  const routeMap: Record<string, string> = {
    'roles': 'permission-roles',
    'permissions': 'permission-permissions',
    'user-roles': 'permission-user-roles',
  }
  
  if (routeMap[index]) {
    router.push({ name: routeMap[index] })
  }
}
</script>

<style scoped>
.permission-layout {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.permission-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--el-border-color-light);
  background-color: var(--el-bg-color);
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.permission-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.permission-sidebar {
  width: 200px;
  border-right: 1px solid var(--el-border-color-light);
  background-color: var(--el-bg-color);
}

.permission-menu {
  height: 100%;
  border-right: none;
}

.permission-main {
  flex: 1;
  padding: 24px;
  overflow: auto;
  background-color: var(--el-bg-color-page);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .permission-content {
    flex-direction: column;
  }
  
  .permission-sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-light);
  }
  
  .permission-menu {
    height: auto;
  }
  
  .permission-main {
    padding: 16px;
  }
}
</style>