<template>
  <div class="role-table">
    <el-table
      :data="roles"
      :loading="loading"
      v-loading="loading"
      element-loading-text="加载中..."
      stripe
      border
      style="width: 100%"
      @sort-change="handleSortChange"
      @selection-change="handleSelectionChange"
    >
      <!-- 选择列 -->
      <el-table-column
        v-if="selectable"
        type="selection"
        width="55"
        align="center"
      />

      <!-- 角色名称 -->
      <el-table-column
        prop="name"
        label="角色名称"
        min-width="150"
        sortable="custom"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <div class="role-name-cell">
            <el-tag
              :type="row.is_system_role ? 'warning' : 'primary'"
              size="small"
              class="role-type-tag"
            >
              {{ row.is_system_role ? '系统' : '自定义' }}
            </el-tag>
            <span class="role-name">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>

      <!-- 显示名称 -->
      <el-table-column
        prop="display_name"
        label="显示名称"
        min-width="150"
        sortable="custom"
        show-overflow-tooltip
      />

      <!-- 描述 -->
      <el-table-column
        prop="description"
        label="描述"
        min-width="200"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <span class="role-description">
            {{ row.description || '暂无描述' }}
          </span>
        </template>
      </el-table-column>

      <!-- 权限数量 -->
      <el-table-column
        label="权限数量"
        width="100"
        align="center"
        sortable="custom"
        prop="permissions_count"
      >
        <template #default="{ row }">
          <el-badge
            :value="row.permissions?.length || 0"
            :max="999"
            class="permissions-badge"
          >
            <el-icon><Key /></el-icon>
          </el-badge>
        </template>
      </el-table-column>

      <!-- 用户数量 -->
      <el-table-column
        label="用户数量"
        width="100"
        align="center"
        sortable="custom"
        prop="user_count"
      >
        <template #default="{ row }">
          <el-badge
            :value="row.user_count || 0"
            :max="999"
            class="users-badge"
          >
            <el-icon><User /></el-icon>
          </el-badge>
        </template>
      </el-table-column>

      <!-- 状态 -->
      <el-table-column
        label="状态"
        width="80"
        align="center"
      >
        <template #default="{ row }">
          <el-tag
            :type="getRoleStatusType(row)"
            size="small"
          >
            {{ getRoleStatusText(row) }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- 创建时间 -->
      <el-table-column
        prop="created_at"
        label="创建时间"
        width="160"
        sortable="custom"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <div class="time-cell">
            <el-icon><Clock /></el-icon>
            <span>{{ formatDateTime(row.created_at) }}</span>
          </div>
        </template>
      </el-table-column>

      <!-- 操作列 -->
      <el-table-column
        label="操作"
        width="200"
        align="center"
        fixed="right"
      >
        <template #default="{ row }">
          <div class="action-buttons">
            <el-tooltip content="查看详情" placement="top">
              <el-button
                type="primary"
                size="small"
                circle
                @click="handleView(row)"
              >
                <el-icon><View /></el-icon>
              </el-button>
            </el-tooltip>

            <el-tooltip content="编辑角色" placement="top">
              <el-button
                type="warning"
                size="small"
                circle
                :disabled="!canEdit(row)"
                @click="handleEdit(row)"
              >
                <el-icon><Edit /></el-icon>
              </el-button>
            </el-tooltip>

            <el-tooltip content="分配权限" placement="top">
              <el-button
                type="success"
                size="small"
                circle
                :disabled="!canAssignPermissions(row)"
                @click="handleAssignPermissions(row)"
              >
                <el-icon><Key /></el-icon>
              </el-button>
            </el-tooltip>

            <el-tooltip content="查看用户" placement="top">
              <el-button
                type="info"
                size="small"
                circle
                @click="handleViewUsers(row)"
              >
                <el-icon><User /></el-icon>
              </el-button>
            </el-tooltip>

            <el-tooltip content="删除角色" placement="top">
              <el-button
                type="danger"
                size="small"
                circle
                :disabled="!canDelete(row)"
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>

      <!-- 空状态 -->
      <template #empty>
        <el-empty
          description="暂无角色数据"
          :image-size="100"
        >
          <el-button type="primary" @click="$emit('refresh')">
            刷新数据
          </el-button>
        </el-empty>
      </template>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElTag,
  ElBadge,
  ElIcon,
  ElTooltip,
  ElEmpty
} from 'element-plus'
import {
  View,
  Edit,
  Delete,
  Key,
  User,
  Clock
} from '@element-plus/icons-vue'
import type { Role } from '@/types/permission'
import { formatDateTime } from '@/utils/date'

interface Props {
  roles: Role[]
  loading?: boolean
  selectable?: boolean
}

interface Emits {
  (e: 'view', role: Role): void
  (e: 'edit', role: Role): void
  (e: 'delete', role: Role): void
  (e: 'assign-permissions', role: Role): void
  (e: 'view-users', role: Role): void
  (e: 'sort-change', sort: { prop: string; order: string }): void
  (e: 'selection-change', selection: Role[]): void
  (e: 'refresh'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selectable: false
})

const emit = defineEmits<Emits>()

// 角色状态类型
const getRoleStatusType = (role: Role) => {
  if (role.is_system_role) return 'warning'
  return 'success'
}

// 角色状态文本
const getRoleStatusText = (role: Role) => {
  if (role.is_system_role) return '系统'
  return '正常'
}

// 权限检查
const canEdit = (role: Role) => {
  // 系统角色通常不允许编辑基本信息
  return !role.is_system_role
}

const canDelete = (role: Role) => {
  // 系统角色不允许删除，且有用户的角色也不允许删除
  return !role.is_system_role && (role.user_count || 0) === 0
}

const canAssignPermissions = (role: Role) => {
  // 所有角色都可以分配权限
  return true
}

// 事件处理
const handleView = (role: Role) => {
  emit('view', role)
}

const handleEdit = (role: Role) => {
  if (canEdit(role)) {
    emit('edit', role)
  }
}

const handleDelete = (role: Role) => {
  if (canDelete(role)) {
    emit('delete', role)
  }
}

const handleAssignPermissions = (role: Role) => {
  if (canAssignPermissions(role)) {
    emit('assign-permissions', role)
  }
}

const handleViewUsers = (role: Role) => {
  emit('view-users', role)
}

const handleSortChange = (sort: { prop: string; order: string }) => {
  emit('sort-change', sort)
}

const handleSelectionChange = (selection: Role[]) => {
  emit('selection-change', selection)
}
</script>

<style scoped>
.role-table {
  width: 100%;
}

.role-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-type-tag {
  flex-shrink: 0;
}

.role-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.role-description {
  color: var(--el-text-color-regular);
  font-size: 13px;
}

.permissions-badge,
.users-badge {
  cursor: pointer;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
  
  .action-buttons .el-button {
    width: 28px;
    height: 28px;
  }
}

/* 表格行悬停效果 */
:deep(.el-table__row:hover) {
  background-color: var(--el-table-row-hover-bg-color);
}

/* 系统角色行样式 */
:deep(.el-table__row[data-system-role="true"]) {
  background-color: var(--el-color-warning-light-9);
}

/* 禁用状态样式 */
:deep(.el-button.is-disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 徽章样式 */
.permissions-badge :deep(.el-badge__content) {
  background-color: var(--el-color-primary);
}

.users-badge :deep(.el-badge__content) {
  background-color: var(--el-color-success);
}
</style>