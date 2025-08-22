<template>
  <div class="permission-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h3 class="page-title">权限管理</h3>
        <p class="page-description">查看和管理系统权限，了解权限层级结构</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-cards" v-if="stats">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_permissions }}</div>
              <div class="stat-label">总权限数</div>
            </div>
            <el-icon class="stat-icon"><Key /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.system_permissions }}</div>
              <div class="stat-label">系统权限</div>
            </div>
            <el-icon class="stat-icon"><Setting /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.custom_permissions }}</div>
              <div class="stat-label">自定义权限</div>
            </div>
            <el-icon class="stat-icon"><Edit /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.active_permissions }}</div>
              <div class="stat-label">活跃权限</div>
            </div>
            <el-icon class="stat-icon"><Check /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-bar">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索权限名称或描述..."
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="moduleFilter"
            placeholder="筛选模块"
            clearable
            @change="handleModuleFilter"
          >
            <el-option
              v-for="module in modules"
              :key="module"
              :label="module"
              :value="module"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="actionFilter"
            placeholder="筛选操作"
            clearable
            @change="handleActionFilter"
          >
            <el-option
              v-for="action in actions"
              :key="action"
              :label="getActionLabel(action)"
              :value="action"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="statusFilter"
            placeholder="筛选状态"
            clearable
            @change="handleStatusFilter"
          >
            <el-option label="激活" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <div class="filter-actions">
            <el-button @click="handleResetFilters">重置筛选</el-button>
            <el-switch
              v-model="treeMode"
              active-text="树形模式"
              inactive-text="列表模式"
              @change="handleViewModeChange"
            />
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 权限树形视图 -->
    <div v-if="treeMode" class="permission-tree-container">
      <PermissionTree
        :permissions="filteredPermissions"
        :loading="loading"
        :searchable="false"
        :selectable="false"
        :show-actions="true"
        :show-stats="true"
        @view-permission="handleViewPermission"
        @view-roles="handleViewRoles"
        @refresh="handleRefresh"
      />
    </div>

    <!-- 权限列表视图 -->
    <div v-else class="permission-list-container">
      <el-table
        :data="paginatedPermissions"
        :loading="loading"
        v-loading="loading"
        element-loading-text="加载中..."
        stripe
        border
        style="width: 100%"
      >
        <!-- 权限名称 -->
        <el-table-column label="权限名称" min-width="200">
          <template #default="{ row }">
            <div class="permission-name">
              <el-icon class="permission-icon">
                <Key />
              </el-icon>
              <div class="name-info">
                <div class="name-primary">{{ row.display_name }}</div>
                <div class="name-secondary">{{ row.name }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 模块 -->
        <el-table-column prop="module" label="模块" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.module }}</el-tag>
          </template>
        </el-table-column>

        <!-- 资源 -->
        <el-table-column prop="resource" label="资源" width="100" />

        <!-- 操作 -->
        <el-table-column prop="action" label="操作" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getActionTagType(row.action)"
              size="small"
            >
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 描述 -->
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />

        <!-- 状态 -->
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : 'danger'"
              size="small"
            >
              {{ row.status === 'active' ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 权限级别 -->
        <el-table-column label="级别" width="80" align="center">
          <template #default="{ row }">
            <el-badge
              :value="row.level || 1"
              :type="getLevelBadgeType(row.level)"
            />
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-tooltip content="查看详情" placement="top">
                <el-button
                  type="primary"
                  size="small"
                  circle
                  @click="handleViewPermission(row)"
                >
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>

              <el-tooltip content="查看角色" placement="top">
                <el-button
                  type="info"
                  size="small"
                  circle
                  @click="handleViewRoles(row)"
                >
                  <el-icon><UserFilled /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <!-- 空状态 -->
        <template #empty>
          <el-empty
            description="暂无权限数据"
            :image-size="100"
          >
            <el-button type="primary" @click="handleRefresh">
              刷新数据
            </el-button>
          </el-empty>
        </template>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="!treeMode && totalCount > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalCount"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 权限详情对话框 -->
    <el-dialog
      v-model="permissionDetailVisible"
      title="权限详情"
      width="50%"
    >
      <div v-if="selectedPermission">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="权限名称">
            {{ selectedPermission.display_name }}
          </el-descriptions-item>
          <el-descriptions-item label="权限标识">
            {{ selectedPermission.name }}
          </el-descriptions-item>
          <el-descriptions-item label="所属模块">
            {{ selectedPermission.module }}
          </el-descriptions-item>
          <el-descriptions-item label="资源类型">
            {{ selectedPermission.resource }}
          </el-descriptions-item>
          <el-descriptions-item label="操作类型">
            <el-tag :type="getActionTagType(selectedPermission.action)">
              {{ getActionLabel(selectedPermission.action) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="权限级别">
            <el-badge
              :value="selectedPermission.level || 1"
              :type="getLevelBadgeType(selectedPermission.level)"
            />
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="selectedPermission.status === 'active' ? 'success' : 'danger'"
            >
              {{ selectedPermission.status === 'active' ? '激活' : '停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="系统权限">
            <el-tag :type="selectedPermission.is_system_permission ? 'warning' : 'primary'">
              {{ selectedPermission.is_system_permission ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDateTime(selectedPermission.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">
            {{ formatDateTime(selectedPermission.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ selectedPermission.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 角色列表对话框 -->
    <el-dialog
      v-model="rolesDialogVisible"
      title="使用此权限的角色"
      width="60%"
    >
      <div v-if="selectedPermission">
        <p>权限：<strong>{{ selectedPermission.display_name }}</strong></p>
        <el-table :data="permissionRoles" stripe>
          <el-table-column prop="display_name" label="角色名称" />
          <el-table-column prop="description" label="描述" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_system_role ? 'warning' : 'primary'" size="small">
                {{ row.is_system_role ? '系统' : '自定义' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                {{ row.status === 'active' ? '激活' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElTag,
  ElBadge,
  ElIcon,
  ElTooltip,
  ElEmpty,
  ElCard,
  ElRow,
  ElCol,
  ElInput,
  ElSelect,
  ElOption,
  ElSwitch,
  ElPagination,
  ElDialog,
  ElDescriptions,
  ElDescriptionsItem,
} from 'element-plus'
import {
  Search,
  Refresh,
  Key,
  Setting,
  Edit,
  Check,
  View,
  UserFilled,
} from '@element-plus/icons-vue'
import { usePermissionManagement } from '@/composables/permission/usePermissionManagement'
import { useRoleManagement } from '@/composables/permission/useRoleManagement'
import PermissionTree from '@/components/permission/PermissionTree.vue'
import { formatDateTime } from '@/utils/date'
import type { Permission, Role } from '@/types/permission'

// 权限管理
const {
  permissions,
  filteredPermissions,
  loading,
  stats,
  initialize,
  refresh,
  setSearchQuery,
  setModuleFilter,
  setActionFilter,
  setStatusFilter,
  resetFilters,
} = usePermissionManagement()

// 角色管理
const {
  roles,
} = useRoleManagement()

// 本地状态
const searchQuery = ref('')
const moduleFilter = ref('')
const actionFilter = ref('')
const statusFilter = ref('')
const treeMode = ref(true)
const currentPage = ref(1)
const pageSize = ref(20)
const permissionDetailVisible = ref(false)
const rolesDialogVisible = ref(false)
const selectedPermission = ref<Permission | null>(null)
const permissionRoles = ref<Role[]>([])

// 计算属性
const modules = computed(() => {
  const moduleSet = new Set<string>()
  permissions.value.forEach(permission => {
    moduleSet.add(permission.module)
  })
  return Array.from(moduleSet).sort()
})

const actions = computed(() => {
  const actionSet = new Set<string>()
  permissions.value.forEach(permission => {
    actionSet.add(permission.action)
  })
  return Array.from(actionSet).sort()
})

const totalCount = computed(() => filteredPermissions.value.length)

const paginatedPermissions = computed(() => {
  if (treeMode.value) return filteredPermissions.value
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPermissions.value.slice(start, end)
})

// 工具函数
const getActionLabel = (action: string): string => {
  const actionMap: Record<string, string> = {
    'create': '创建',
    'read': '读取',
    'update': '更新',
    'delete': '删除',
    'manage': '管理',
    'view': '查看',
    'execute': '执行',
  }
  return actionMap[action] || action
}

const getActionTagType = (action: string): string => {
  const typeMap: Record<string, string> = {
    'create': 'success',
    'read': 'info',
    'update': 'warning',
    'delete': 'danger',
    'manage': 'primary',
    'view': 'info',
    'execute': 'warning',
  }
  return typeMap[action] || 'info'
}

const getLevelBadgeType = (level?: number): string => {
  if (!level || level <= 1) return 'info'
  if (level <= 2) return 'success'
  if (level <= 3) return 'warning'
  return 'danger'
}

// 事件处理
const handleSearch = (query: string) => {
  setSearchQuery(query)
}

const handleModuleFilter = (module: string) => {
  setModuleFilter(module)
}

const handleActionFilter = (action: string) => {
  setActionFilter(action)
}

const handleStatusFilter = (status: string) => {
  setStatusFilter(status)
}

const handleResetFilters = () => {
  searchQuery.value = ''
  moduleFilter.value = ''
  actionFilter.value = ''
  statusFilter.value = ''
  resetFilters()
}

const handleRefresh = () => {
  refresh()
}

const handleViewModeChange = () => {
  currentPage.value = 1
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleViewPermission = (permission: Permission) => {
  selectedPermission.value = permission
  permissionDetailVisible.value = true
}

const handleViewRoles = (permission: Permission) => {
  selectedPermission.value = permission
  
  // 查找使用此权限的角色
  permissionRoles.value = roles.value.filter(role => 
    role.permissions?.includes(permission.name)
  )
  
  rolesDialogVisible.value = true
}

// 初始化
onMounted(async () => {
  await initialize()
})
</script>

<style scoped>
.permission-management {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-content {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.page-description {
  margin: 0;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.header-actions {
  flex-shrink: 0;
}

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--el-color-primary);
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.stat-icon {
  font-size: 32px;
  color: var(--el-color-primary);
  opacity: 0.3;
}

.filter-bar {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

.permission-tree-container,
.permission-list-container {
  flex: 1;
  overflow: hidden;
}

.permission-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.permission-icon {
  color: var(--el-color-primary);
  flex-shrink: 0;
}

.name-info {
  flex: 1;
  min-width: 0;
}

.name-primary {
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.name-secondary {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-family: monospace;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    display: flex;
    justify-content: flex-start;
  }
  
  .stats-cards .el-col {
    margin-bottom: 16px;
  }
  
  .filter-bar .el-col {
    margin-bottom: 8px;
  }
  
  .filter-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
  
  .action-buttons .el-button {
    width: 28px;
    height: 28px;
  }
}
</style>