<template>
  <div class="user-role-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h3 class="page-title">用户权限管理</h3>
        <p class="page-description">管理用户角色分配，查看用户权限</p>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名或邮箱..."
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
            v-model="roleFilter"
            placeholder="筛选角色"
            clearable
            @change="handleRoleFilter"
          >
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.display_name"
              :value="role.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 用户列表 -->
    <div class="user-table-container">
      <el-table
        :data="filteredUsers"
        :loading="loading"
        v-loading="loading"
        element-loading-text="加载中..."
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <!-- 选择列 -->
        <el-table-column type="selection" width="55" align="center" />

        <!-- 用户信息 -->
        <el-table-column label="用户信息" min-width="200">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="40" :src="row.avatar_url">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="user-details">
                <div class="user-name">{{ row.username }}</div>
                <div class="user-email">{{ row.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 用户角色 -->
        <el-table-column label="分配角色" min-width="200">
          <template #default="{ row }">
            <div class="user-roles">
              <el-tag
                v-for="role in row.roles"
                :key="role.id"
                :type="role.is_system_role ? 'warning' : 'primary'"
                size="small"
                class="role-tag"
              >
                {{ role.display_name }}
              </el-tag>
              <el-tag v-if="!row.roles || row.roles.length === 0" type="info" size="small">
                未分配角色
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <!-- 权限数量 -->
        <el-table-column label="权限数量" width="100" align="center">
          <template #default="{ row }">
            <el-badge
              :value="getUserPermissionCount(row)"
              :max="999"
              class="permissions-badge"
            >
              <el-icon><Key /></el-icon>
            </el-badge>
          </template>
        </el-table-column>

        <!-- 状态 -->
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.is_active ? 'success' : 'danger'"
              size="small"
            >
              {{ row.is_active ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-tooltip content="分配角色" placement="top">
                <el-button
                  type="primary"
                  size="small"
                  circle
                  @click="handleAssignRoles(row)"
                >
                  <el-icon><UserFilled /></el-icon>
                </el-button>
              </el-tooltip>

              <el-tooltip content="查看权限" placement="top">
                <el-button
                  type="info"
                  size="small"
                  circle
                  @click="handleViewPermissions(row)"
                >
                  <el-icon><Key /></el-icon>
                </el-button>
              </el-tooltip>

              <el-tooltip content="用户详情" placement="top">
                <el-button
                  type="success"
                  size="small"
                  circle
                  @click="handleViewUser(row)"
                >
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <!-- 空状态 -->
        <template #empty>
          <el-empty
            description="暂无用户数据"
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

    <!-- 角色分配对话框 -->
    <el-dialog
      v-model="roleAssignDialogVisible"
      title="分配角色"
      width="50%"
      :close-on-click-modal="false"
    >
      <div v-if="selectedUser">
        <div class="user-info-header">
          <el-avatar :size="60" :src="selectedUser.avatar_url">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <h4>{{ selectedUser.username }}</h4>
            <p>{{ selectedUser.email }}</p>
          </div>
        </div>

        <el-divider />

        <h4>选择角色</h4>
        <div class="role-selection">
          <el-checkbox-group v-model="selectedRoleIds">
            <div class="role-list">
              <div
                v-for="role in roles"
                :key="role.id"
                class="role-item"
              >
                <el-checkbox :value="role.id">
                  <div class="role-info">
                    <div class="role-name">
                      <el-tag
                        :type="role.is_system_role ? 'warning' : 'primary'"
                        size="small"
                      >
                        {{ role.is_system_role ? '系统' : '自定义' }}
                      </el-tag>
                      {{ role.display_name }}
                    </div>
                    <div class="role-description">{{ role.description }}</div>
                  </div>
                </el-checkbox>
              </div>
            </div>
          </el-checkbox-group>
        </div>
      </div>
      <template #footer>
        <el-button @click="roleAssignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRoleAssign">确定</el-button>
      </template>
    </el-dialog>

    <!-- 权限查看对话框 -->
    <el-dialog
      v-model="permissionViewDialogVisible"
      title="用户权限"
      width="60%"
    >
      <div v-if="selectedUser">
        <div class="user-info-header">
          <el-avatar :size="60" :src="selectedUser.avatar_url">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <h4>{{ selectedUser.username }}</h4>
            <p>{{ selectedUser.email }}</p>
          </div>
        </div>

        <el-divider />

        <h4>用户权限列表</h4>
        <PermissionTree
          :permissions="userPermissions"
          :selectable="false"
          :show-actions="false"
          :searchable="true"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElTag,
  ElBadge,
  ElIcon,
  ElTooltip,
  ElEmpty,
  ElRow,
  ElCol,
  ElInput,
  ElSelect,
  ElOption,
  ElPagination,
  ElDialog,
  ElAvatar,
  ElDivider,
  ElCheckboxGroup,
  ElCheckbox,
} from 'element-plus'
import {
  Search,
  Refresh,
  User,
  UserFilled,
  Key,
  View,
} from '@element-plus/icons-vue'
import { useRoleManagement } from '@/composables/permission/useRoleManagement'
import { useUserRoleAssign } from '@/composables/permission/useUserRoleAssign'
import PermissionTree from '@/components/permission/PermissionTree.vue'
import type { Role, Permission } from '@/types/permission'

interface User {
  id: string
  username: string
  email: string
  avatar_url?: string
  is_active: boolean
  roles?: Role[]
  created_at: string
  updated_at: string
}

const route = useRoute()
const router = useRouter()

// 角色管理
const {
  roles,
  activeRoles,
  initialize: initializeRoles,
} = useRoleManagement()

// 用户角色分配
const {
  // 状态会根据实际API调整
  loading,
  assignUserRoles,
  getUserPermissions,
} = useUserRoleAssign()

// 本地状态
const searchQuery = ref('')
const roleFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const selectedUsers = ref<User[]>([])
const roleAssignDialogVisible = ref(false)
const permissionViewDialogVisible = ref(false)
const selectedUser = ref<User | null>(null)
const selectedRoleIds = ref<string[]>([])
const userPermissions = ref<Permission[]>([])

// 模拟用户数据 - 实际应该从API获取
const users = ref<User[]>([
  {
    id: 'user-1',
    username: 'admin',
    email: 'admin@example.com',
    is_active: true,
    roles: [
      {
        id: 'role-1',
        name: 'admin',
        display_name: '管理员',
        description: '系统管理员',
        is_system_role: true,
        role_type: 'system',
        status: 'active',
        permissions: ['*:*'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }
    ],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'user-2',
    username: 'user1',
    email: 'user1@example.com',
    is_active: true,
    roles: [],
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
])

// 计算属性
const filteredUsers = computed(() => {
  let filtered = users.value

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user =>
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    )
  }

  // 角色筛选
  if (roleFilter.value) {
    filtered = filtered.filter(user => 
      user.roles?.some(role => role.id === roleFilter.value)
    )
  }

  return filtered
})

// 获取用户权限数量
const getUserPermissionCount = (user: User): number => {
  if (!user.roles) return 0
  
  let count = 0
  user.roles.forEach(role => {
    if (role.permissions) {
      count += role.permissions.length
    }
  })
  return count
}

// 事件处理
const handleSearch = (query: string) => {
  searchQuery.value = query
  currentPage.value = 1
}

const handleRoleFilter = (roleId: string) => {
  roleFilter.value = roleId
  currentPage.value = 1
}

const handleRefresh = () => {
  // 刷新用户列表
  console.log('刷新用户列表')
}

const handleSelectionChange = (selection: User[]) => {
  selectedUsers.value = selection
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleAssignRoles = (user: User) => {
  selectedUser.value = user
  selectedRoleIds.value = user.roles?.map(role => role.id) || []
  roleAssignDialogVisible.value = true
}

const handleViewPermissions = async (user: User) => {
  selectedUser.value = user
  
  // 获取用户的所有权限
  try {
    userPermissions.value = await getUserPermissions(user.id)
    permissionViewDialogVisible.value = true
  } catch (error) {
    console.error('获取用户权限失败:', error)
  }
}

const handleViewUser = (user: User) => {
  // 导航到用户详情页面
  router.push({
    name: 'admin-users',
    query: { userId: user.id }
  })
}

const handleRoleAssign = async () => {
  if (!selectedUser.value) return

  try {
    await assignUserRoles(selectedUser.value.id, selectedRoleIds.value)
    
    // 更新本地用户数据
    const userIndex = users.value.findIndex(u => u.id === selectedUser.value!.id)
    if (userIndex !== -1) {
      const assignedRoles = roles.value.filter(role => 
        selectedRoleIds.value.includes(role.id)
      )
      users.value[userIndex].roles = assignedRoles
    }
    
    roleAssignDialogVisible.value = false
  } catch (error) {
    console.error('分配角色失败:', error)
  }
}

// 监听路由参数
watch(() => route.query.roleId, (roleId) => {
  if (roleId) {
    roleFilter.value = roleId as string
  }
}, { immediate: true })

// 初始化
onMounted(async () => {
  await initializeRoles()
  totalCount.value = users.value.length
})
</script>

<style scoped>
.user-role-management {
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

.search-filters {
  margin-bottom: 16px;
}

.user-table-container {
  flex: 1;
  overflow: hidden;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.user-email {
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.user-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.role-tag {
  margin: 0;
}

.permissions-badge {
  cursor: pointer;
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

.user-info-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.user-info-header .user-details h4 {
  margin: 0 0 4px 0;
  color: var(--el-text-color-primary);
}

.user-info-header .user-details p {
  margin: 0;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.role-selection {
  max-height: 300px;
  overflow-y: auto;
}

.role-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.role-item {
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  padding: 12px;
  transition: border-color 0.2s;
}

.role-item:hover {
  border-color: var(--el-color-primary);
}

.role-info {
  margin-left: 8px;
}

.role-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.role-description {
  font-size: 13px;
  color: var(--el-text-color-regular);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-filters .el-col {
    margin-bottom: 8px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
  
  .action-buttons .el-button {
    width: 28px;
    height: 28px;
  }
  
  .user-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .user-roles {
    max-width: 100%;
  }
}
</style>