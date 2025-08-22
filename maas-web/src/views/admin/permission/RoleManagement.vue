<template>
  <div class="role-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h3 class="page-title">角色管理</h3>
        <p class="page-description">管理系统角色，分配权限，控制用户访问</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleCreateRole">
          <el-icon><Plus /></el-icon>
          创建角色
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="stats">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_roles }}</div>
              <div class="stat-label">总角色数</div>
            </div>
            <el-icon class="stat-icon"><UserFilled /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.system_roles }}</div>
              <div class="stat-label">系统角色</div>
            </div>
            <el-icon class="stat-icon"><Setting /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.custom_roles }}</div>
              <div class="stat-label">自定义角色</div>
            </div>
            <el-icon class="stat-icon"><Edit /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.active_roles }}</div>
              <div class="stat-label">活跃角色</div>
            </div>
            <el-icon class="stat-icon"><Check /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索角色名称..."
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
            v-model="roleTypeFilter"
            placeholder="角色类型"
            clearable
            @change="handleTypeFilter"
          >
            <el-option label="系统角色" value="system" />
            <el-option label="自定义角色" value="custom" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="roleStatusFilter"
            placeholder="角色状态"
            clearable
            @change="handleStatusFilter"
          >
            <el-option label="激活" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <div class="filter-actions">
            <el-button @click="handleResetFilters">重置筛选</el-button>
            <el-button type="primary" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 批量操作 -->
    <div class="batch-actions" v-if="hasSelectedRoles">
      <el-alert
        :title="`已选择 ${selectedRoleCount} 个角色`"
        type="info"
        :closable="false"
        show-icon
      >
        <template #default>
          <div class="batch-buttons">
            <el-button
              size="small"
              :disabled="!canBatchDelete"
              @click="handleBatchDelete"
            >
              批量删除
            </el-button>
            <el-button size="small" @click="clearSelection">
              清空选择
            </el-button>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 角色表格 -->
    <div class="role-table-container">
      <RoleTable
        :roles="filteredRoles"
        :loading="loading"
        :selectable="true"
        @view="handleViewRole"
        @edit="handleEditRole"
        @delete="handleDeleteRole"
        @assign-permissions="handleAssignPermissions"
        @view-users="handleViewUsers"
        @sort-change="handleSortChange"
        @selection-change="handleSelectionChange"
        @refresh="handleRefresh"
      />
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="totalCount > 0">
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

    <!-- 角色编辑对话框 -->
    <RoleEditDialog
      v-model:visible="roleDialogVisible"
      :role="selectedRole"
      :mode="dialogMode"
      @submit="handleRoleSubmit"
    />

    <!-- 权限分配对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="分配权限"
      width="60%"
      :close-on-click-modal="false"
    >
      <div v-if="selectedRole">
        <h4>为角色 "{{ selectedRole.display_name }}" 分配权限</h4>
        <PermissionTree
          :permissions="permissions"
          :selected-permissions="selectedRole.permissions || []"
          :selectable="true"
          @select="handlePermissionSelect"
        />
      </div>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePermissionAssign">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ElButton,
  ElCard,
  ElRow,
  ElCol,
  ElInput,
  ElSelect,
  ElOption,
  ElIcon,
  ElAlert,
  ElPagination,
  ElDialog,
} from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  UserFilled,
  Setting,
  Edit,
  Check,
} from '@element-plus/icons-vue'
import { useRoleManagement } from '@/composables/permission/useRoleManagement'
import { usePermissionManagement } from '@/composables/permission/usePermissionManagement'
import RoleTable from '@/components/permission/RoleTable.vue'
import RoleEditDialog from '@/components/permission/RoleEditDialog.vue'
import PermissionTree from '@/components/permission/PermissionTree.vue'
import type { Role } from '@/types/permission'

const router = useRouter()

// 角色管理逻辑
const {
  // 状态
  roles,
  filteredRoles,
  loading,
  stats,
  pagination,
  filters,
  roleDialogVisible,
  permissionDialogVisible,
  selectedRole,
  dialogMode,
  selectedRoleIds,
  hasSelectedRoles,
  selectedRoleCount,
  canBatchDelete,
  
  // 方法
  initialize,
  refresh,
  openCreateDialog,
  openEditDialog,
  openPermissionDialog,
  createRole,
  updateRole,
  deleteRole,
  assignRolePermissions,
  batchDeleteRoles,
  setSearchQuery,
  setRoleTypeFilter,
  setRoleStatusFilter,
  resetFilters,
  setPage,
  setPageSize,
  setSorting,
  clearSelection,
} = useRoleManagement()

// 权限管理逻辑
const {
  permissions,
  fetchPermissions,
} = usePermissionManagement()

// 响应式数据
const searchQuery = computed({
  get: () => filters.value.searchQuery,
  set: (value) => setSearchQuery(value)
})

const roleTypeFilter = computed({
  get: () => filters.value.roleTypeFilter,
  set: (value) => setRoleTypeFilter(value)
})

const roleStatusFilter = computed({
  get: () => filters.value.roleStatusFilter,
  set: (value) => setRoleStatusFilter(value)
})

const currentPage = computed({
  get: () => pagination.value.currentPage,
  set: (value) => setPage(value)
})

const pageSize = computed({
  get: () => pagination.value.pageSize,
  set: (value) => setPageSize(value)
})

const totalCount = computed(() => pagination.value.totalCount)

// 选中的权限ID列表
const selectedPermissionIds = ref<string[]>([])

// 事件处理
const handleCreateRole = () => {
  openCreateDialog()
}

const handleViewRole = (role: Role) => {
  // 可以导航到详情页面或显示详情对话框
  console.log('查看角色:', role)
}

const handleEditRole = (role: Role) => {
  openEditDialog(role)
}

const handleDeleteRole = (role: Role) => {
  deleteRole(role)
}

const handleAssignPermissions = (role: Role) => {
  selectedPermissionIds.value = role.permissions || []
  openPermissionDialog(role)
}

const handleViewUsers = (role: Role) => {
  // 导航到用户管理页面，并筛选该角色的用户
  router.push({
    name: 'permission-user-roles',
    query: { roleId: role.id }
  })
}

const handleSearch = (query: string) => {
  setSearchQuery(query)
}

const handleTypeFilter = (type: string) => {
  setRoleTypeFilter(type as any)
}

const handleStatusFilter = (status: string) => {
  setRoleStatusFilter(status as any)
}

const handleResetFilters = () => {
  resetFilters()
}

const handleRefresh = () => {
  refresh()
}

const handleBatchDelete = () => {
  batchDeleteRoles()
}

const handleSortChange = (sort: { prop: string; order: string }) => {
  const order = sort.order === 'ascending' ? 'asc' : 'desc'
  setSorting(sort.prop, order)
}

const handleSelectionChange = (selection: Role[]) => {
  selectedRoleIds.value = selection.map(role => role.id)
}

const handlePageChange = (page: number) => {
  setPage(page)
}

const handleSizeChange = (size: number) => {
  setPageSize(size)
}

const handleRoleSubmit = async (roleData: any) => {
  if (dialogMode.value === 'create') {
    await createRole(roleData)
  } else {
    await updateRole(selectedRole.value!.id, roleData)
  }
}

const handlePermissionSelect = (permissionIds: string[]) => {
  selectedPermissionIds.value = permissionIds
}

const handlePermissionAssign = async () => {
  if (selectedRole.value) {
    await assignRolePermissions(selectedRole.value.id, {
      permission_ids: selectedPermissionIds.value
    })
  }
}

// 初始化
onMounted(async () => {
  await Promise.all([
    initialize(),
    fetchPermissions()
  ])
})
</script>

<style scoped>
.role-management {
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

.search-filters {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.batch-actions {
  margin-bottom: 16px;
}

.batch-buttons {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.role-table-container {
  flex: 1;
  overflow: hidden;
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
  
  .search-filters .el-col {
    margin-bottom: 8px;
  }
  
  .filter-actions {
    justify-content: flex-start;
  }
}
</style>