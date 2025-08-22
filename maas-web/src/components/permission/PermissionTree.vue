<template>
  <div class="permission-tree">
    <!-- 搜索框 -->
    <div v-if="searchable" class="tree-search">
      <el-input
        v-model="searchQuery"
        placeholder="搜索权限..."
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 工具栏 -->
    <div v-if="showToolbar" class="tree-toolbar">
      <div class="toolbar-left">
        <el-button
          v-if="selectable"
          size="small"
          @click="handleSelectAll"
        >
          全选
        </el-button>
        <el-button
          v-if="selectable"
          size="small"
          @click="handleUnselectAll"
        >
          取消全选
        </el-button>
        <el-button
          size="small"
          @click="handleExpandAll"
        >
          展开全部
        </el-button>
        <el-button
          size="small"
          @click="handleCollapseAll"
        >
          收起全部
        </el-button>
      </div>
      <div class="toolbar-right">
        <span v-if="selectable" class="selection-count">
          已选择: {{ selectedPermissions.length }} 项
        </span>
      </div>
    </div>

    <!-- 权限树 -->
    <div class="tree-container" v-loading="loading">
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="treeProps"
        :show-checkbox="selectable"
        :check-strictly="checkStrictly"
        :default-expanded-keys="defaultExpandedKeys"
        :default-checked-keys="defaultCheckedKeys"
        :filter-node-method="filterNode"
        :expand-on-click-node="false"
        :check-on-click-node="checkOnClickNode"
        node-key="id"
        class="permission-tree-component"
        @check="handleCheck"
        @node-click="handleNodeClick"
        @node-expand="handleNodeExpand"
        @node-collapse="handleNodeCollapse"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <div class="node-content">
              <!-- 权限图标 -->
              <div class="node-icon">
                <el-icon v-if="data.type === 'module'" class="module-icon">
                  <Folder />
                </el-icon>
                <el-icon v-else-if="data.type === 'resource'" class="resource-icon">
                  <Document />
                </el-icon>
                <el-icon v-else class="permission-icon">
                  <Key />
                </el-icon>
              </div>

              <!-- 权限信息 -->
              <div class="node-info">
                <div class="node-title">
                  <span class="node-name">{{ data.display_name || data.name }}</span>
                  <el-tag
                    v-if="data.type === 'permission'"
                    :type="getPermissionTagType(data)"
                    size="small"
                    class="permission-tag"
                  >
                    {{ data.action }}
                  </el-tag>
                </div>
                <div v-if="data.description" class="node-description">
                  {{ data.description }}
                </div>
                <div v-if="data.type === 'permission'" class="node-details">
                  <span class="detail-item">
                    <el-icon><Collection /></el-icon>
                    {{ data.resource }}
                  </span>
                  <span class="detail-item">
                    <el-icon><FolderOpened /></el-icon>
                    {{ data.module }}
                  </span>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div v-if="showActions" class="node-actions">
                <el-tooltip content="查看详情" placement="top">
                  <el-button
                    type="primary"
                    size="small"
                    circle
                    @click.stop="handleViewPermission(data)"
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>

                <el-tooltip
                  v-if="data.type === 'permission'"
                  content="查看使用此权限的角色"
                  placement="top"
                >
                  <el-button
                    type="info"
                    size="small"
                    circle
                    @click.stop="handleViewRoles(data)"
                  >
                    <el-icon><UserFilled /></el-icon>
                  </el-button>
                </el-tooltip>

                <el-tooltip
                  v-if="data.type === 'permission' && editable"
                  content="编辑权限"
                  placement="top"
                >
                  <el-button
                    type="warning"
                    size="small"
                    circle
                    @click.stop="handleEditPermission(data)"
                  >
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>

                <el-tooltip
                  v-if="data.type === 'permission' && deletable"
                  content="删除权限"
                  placement="top"
                >
                  <el-button
                    type="danger"
                    size="small"
                    circle
                    @click.stop="handleDeletePermission(data)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </div>

            <!-- 统计信息 -->
            <div v-if="showStats && data.children" class="node-stats">
              <el-badge
                :value="getChildrenCount(data)"
                :max="999"
                class="children-badge"
              >
                <el-icon><Grid /></el-icon>
              </el-badge>
            </div>
          </div>
        </template>

        <!-- 空状态 -->
        <template #empty>
          <el-empty
            description="暂无权限数据"
            :image-size="80"
          >
            <el-button type="primary" @click="$emit('refresh')">
              刷新数据
            </el-button>
          </el-empty>
        </template>
      </el-tree>
    </div>

    <!-- 批量操作面板 -->
    <div v-if="selectable && selectedPermissions.length > 0" class="batch-actions">
      <div class="batch-info">
        <span>已选择 {{ selectedPermissions.length }} 个权限</span>
      </div>
      <div class="batch-buttons">
        <el-button
          type="primary"
          size="small"
          @click="handleBatchAssign"
        >
          批量分配
        </el-button>
        <el-button
          size="small"
          @click="handleBatchRemove"
        >
          批量移除
        </el-button>
        <el-button
          size="small"
          @click="handleClearSelection"
        >
          清空选择
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  ElTree,
  ElInput,
  ElButton,
  ElIcon,
  ElTag,
  ElTooltip,
  ElBadge,
  ElEmpty
} from 'element-plus'
import {
  Search,
  Folder,
  Document,
  Key,
  Collection,
  FolderOpened,
  View,
  UserFilled,
  Edit,
  Delete,
  Grid
} from '@element-plus/icons-vue'
import type { Permission, PermissionTreeDisplayNode } from '@/types/permission'

interface Props {
  permissions: Permission[]
  selectedPermissions?: string[]
  loading?: boolean
  selectable?: boolean
  searchable?: boolean
  showToolbar?: boolean
  showActions?: boolean
  showStats?: boolean
  editable?: boolean
  deletable?: boolean
  checkStrictly?: boolean
  checkOnClickNode?: boolean
  defaultExpandedKeys?: string[]
  defaultCheckedKeys?: string[]
}

interface Emits {
  (e: 'select', permissions: string[]): void
  (e: 'node-click', permission: Permission, node: any): void
  (e: 'view-permission', permission: Permission): void
  (e: 'view-roles', permission: Permission): void
  (e: 'edit-permission', permission: Permission): void
  (e: 'delete-permission', permission: Permission): void
  (e: 'batch-assign', permissions: string[]): void
  (e: 'batch-remove', permissions: string[]): void
  (e: 'refresh'): void
}

const props = withDefaults(defineProps<Props>(), {
  selectedPermissions: () => [],
  loading: false,
  selectable: false,
  searchable: true,
  showToolbar: true,
  showActions: true,
  showStats: true,
  editable: false,
  deletable: false,
  checkStrictly: false,
  checkOnClickNode: false,
  defaultExpandedKeys: () => [],
  defaultCheckedKeys: () => []
})

const emit = defineEmits<Emits>()

// 组件引用
const treeRef = ref<InstanceType<typeof ElTree>>()

// 搜索状态
const searchQuery = ref('')

// 树形结构配置
const treeProps = {
  children: 'children',
  label: 'display_name',
  disabled: 'disabled'
}

// 构建树形数据
const treeData = computed(() => {
  return buildTreeData(props.permissions)
})

// 选中的权限
const selectedPermissions = computed(() => {
  return props.selectedPermissions || []
})

// 构建树形数据结构
function buildTreeData(permissions: Permission[]): PermissionTreeDisplayNode[] {
  const moduleMap = new Map<string, PermissionTreeDisplayNode>()
  const resourceMap = new Map<string, PermissionTreeDisplayNode>()
  const result: PermissionTreeDisplayNode[] = []

  permissions.forEach(permission => {
    // 创建模块节点
    if (!moduleMap.has(permission.module)) {
      const moduleNode: PermissionTreeDisplayNode = {
        id: `module-${permission.module}`,
        name: permission.module,
        display_name: permission.module,
        type: 'module',
        children: []
      }
      moduleMap.set(permission.module, moduleNode)
      result.push(moduleNode)
    }

    // 创建资源节点
    const resourceKey = `${permission.module}-${permission.resource}`
    if (!resourceMap.has(resourceKey)) {
      const resourceNode: PermissionTreeDisplayNode = {
        id: `resource-${resourceKey}`,
        name: permission.resource,
        display_name: permission.resource,
        type: 'resource',
        module: permission.module,
        children: []
      }
      resourceMap.set(resourceKey, resourceNode)
      moduleMap.get(permission.module)!.children!.push(resourceNode)
    }

    // 创建权限节点
    const permissionNode: PermissionTreeDisplayNode = {
      id: permission.id,
      name: permission.name,
      display_name: permission.display_name,
      description: permission.description,
      type: 'permission',
      module: permission.module,
      resource: permission.resource,
      action: permission.action,
      created_at: permission.created_at
    }

    resourceMap.get(resourceKey)!.children!.push(permissionNode)
  })

  return result
}

// 获取权限标签类型
function getPermissionTagType(permission: PermissionTreeDisplayNode): 'primary' | 'success' | 'warning' | 'info' | 'danger' {
  const actionTypeMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    'create': 'success',
    'read': 'info',
    'update': 'warning',
    'delete': 'danger',
    'manage': 'primary'
  }
  return actionTypeMap[permission.action || ''] || 'info'
}

// 获取子节点数量
function getChildrenCount(node: PermissionTreeDisplayNode): number {
  if (!node.children) return 0
  
  let count = 0
  function countChildren(children: PermissionTreeDisplayNode[]) {
    children.forEach(child => {
      if (child.type === 'permission') {
        count++
      }
      if (child.children) {
        countChildren(child.children)
      }
    })
  }
  
  countChildren(node.children)
  return count
}

// 搜索处理
function handleSearch(query: string) {
  if (treeRef.value) {
    treeRef.value.filter(query)
  }
}

// 过滤节点
function filterNode(value: string, data: PermissionTreeDisplayNode) {
  if (!value) return true
  
  const searchValue = value.toLowerCase()
  return (
    data.name.toLowerCase().includes(searchValue) ||
    data.display_name.toLowerCase().includes(searchValue) ||
    (data.description && data.description.toLowerCase().includes(searchValue))
  )
}

// 全选
function handleSelectAll() {
  if (treeRef.value) {
    const allPermissionIds = getAllPermissionIds(treeData.value)
    treeRef.value.setCheckedKeys(allPermissionIds)
    emit('select', allPermissionIds)
  }
}

// 取消全选
function handleUnselectAll() {
  if (treeRef.value) {
    treeRef.value.setCheckedKeys([])
    emit('select', [])
  }
}

// 展开全部
function handleExpandAll() {
  if (treeRef.value) {
    const allNodeIds = getAllNodeIds(treeData.value)
    allNodeIds.forEach(id => {
      treeRef.value!.store.nodesMap[id]?.expand()
    })
  }
}

// 收起全部
function handleCollapseAll() {
  if (treeRef.value) {
    const allNodeIds = getAllNodeIds(treeData.value)
    allNodeIds.forEach(id => {
      treeRef.value!.store.nodesMap[id]?.collapse()
    })
  }
}

// 获取所有权限ID
function getAllPermissionIds(nodes: PermissionTreeDisplayNode[]): string[] {
  const ids: string[] = []
  
  function collectIds(children: PermissionTreeDisplayNode[]) {
    children.forEach(child => {
      if (child.type === 'permission') {
        ids.push(child.id)
      }
      if (child.children) {
        collectIds(child.children)
      }
    })
  }
  
  collectIds(nodes)
  return ids
}

// 获取所有节点ID
function getAllNodeIds(nodes: PermissionTreeDisplayNode[]): string[] {
  const ids: string[] = []
  
  function collectIds(children: PermissionTreeDisplayNode[]) {
    children.forEach(child => {
      ids.push(child.id)
      if (child.children) {
        collectIds(child.children)
      }
    })
  }
  
  collectIds(nodes)
  return ids
}

// 选择变更处理
function handleCheck(data: PermissionTreeDisplayNode, checkedInfo: any) {
  const checkedKeys = checkedInfo.checkedKeys as string[]
  const permissionIds = checkedKeys.filter(key => {
    const node = findNodeById(treeData.value, key)
    return node?.type === 'permission'
  })
  emit('select', permissionIds)
}

// 节点点击处理
function handleNodeClick(data: PermissionTreeDisplayNode, node: any) {
  if (data.type === 'permission') {
    const permission = props.permissions.find(p => p.id === data.id)
    if (permission) {
      emit('node-click', permission, node)
    }
  }
}

// 节点展开处理
function handleNodeExpand(data: PermissionTreeDisplayNode, node: any) {
  // 可以在这里添加懒加载逻辑
}

// 节点收起处理
function handleNodeCollapse(data: PermissionTreeDisplayNode, node: any) {
  // 节点收起时的处理逻辑
}

// 查看权限详情
function handleViewPermission(data: PermissionTreeDisplayNode) {
  if (data.type === 'permission') {
    const permission = props.permissions.find(p => p.id === data.id)
    if (permission) {
      emit('view-permission', permission)
    }
  }
}

// 查看角色
function handleViewRoles(data: PermissionTreeDisplayNode) {
  if (data.type === 'permission') {
    const permission = props.permissions.find(p => p.id === data.id)
    if (permission) {
      emit('view-roles', permission)
    }
  }
}

// 编辑权限
function handleEditPermission(data: PermissionTreeDisplayNode) {
  if (data.type === 'permission') {
    const permission = props.permissions.find(p => p.id === data.id)
    if (permission) {
      emit('edit-permission', permission)
    }
  }
}

// 删除权限
function handleDeletePermission(data: PermissionTreeDisplayNode) {
  if (data.type === 'permission') {
    const permission = props.permissions.find(p => p.id === data.id)
    if (permission) {
      emit('delete-permission', permission)
    }
  }
}

// 批量分配
function handleBatchAssign() {
  emit('batch-assign', selectedPermissions.value)
}

// 批量移除
function handleBatchRemove() {
  emit('batch-remove', selectedPermissions.value)
}

// 清空选择
function handleClearSelection() {
  if (treeRef.value) {
    treeRef.value.setCheckedKeys([])
    emit('select', [])
  }
}

// 根据ID查找节点
function findNodeById(nodes: PermissionTreeDisplayNode[], id: string): PermissionTreeDisplayNode | null {
  for (const node of nodes) {
    if (node.id === id) {
      return node
    }
    if (node.children) {
      const found = findNodeById(node.children, id)
      if (found) {
        return found
      }
    }
  }
  return null
}

// 监听搜索查询变化
watch(searchQuery, (newQuery) => {
  handleSearch(newQuery)
})

// 监听选中权限变化，同步到树组件
watch(() => props.selectedPermissions, (newSelected) => {
  if (treeRef.value && newSelected) {
    nextTick(() => {
      treeRef.value!.setCheckedKeys(newSelected)
    })
  }
}, { immediate: true })
</script>

<style scoped>
.permission-tree {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-search {
  margin-bottom: 16px;
}

.tree-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-light);
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.selection-count {
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.tree-container {
  flex: 1;
  overflow: auto;
}

.permission-tree-component {
  width: 100%;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 0;
}

.node-content {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.node-icon {
  margin-right: 8px;
  flex-shrink: 0;
}

.module-icon {
  color: var(--el-color-warning);
}

.resource-icon {
  color: var(--el-color-info);
}

.permission-icon {
  color: var(--el-color-primary);
}

.node-info {
  flex: 1;
  min-width: 0;
}

.node-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.node-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.permission-tag {
  flex-shrink: 0;
}

.node-description {
  font-size: 12px;
  color: var(--el-text-color-regular);
  margin-bottom: 4px;
  line-height: 1.4;
}

.node-details {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--el-text-color-secondary);
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 2px;
}

.node-actions {
  display: flex;
  gap: 4px;
  margin-left: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.node-stats {
  margin-left: 8px;
}

.children-badge {
  cursor: pointer;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 12px;
  background-color: var(--el-color-primary-light-9);
  border-radius: 6px;
  border: 1px solid var(--el-color-primary-light-7);
}

.batch-info {
  font-size: 13px;
  color: var(--el-color-primary);
  font-weight: 500;
}

.batch-buttons {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tree-toolbar {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }

  .toolbar-left {
    justify-content: center;
  }

  .toolbar-right {
    justify-content: center;
  }

  .batch-actions {
    flex-direction: column;
    gap: 8px;
  }

  .batch-buttons {
    justify-content: center;
  }

  .node-details {
    flex-direction: column;
    gap: 4px;
  }

  .node-actions {
    opacity: 1;
  }
}

/* 树组件样式覆盖 */
:deep(.el-tree-node__content) {
  height: auto;
  min-height: 32px;
  padding: 4px 0;
}

:deep(.el-tree-node__expand-icon) {
  color: var(--el-text-color-secondary);
}

:deep(.el-tree-node__expand-icon.expanded) {
  transform: rotate(90deg);
}

:deep(.el-checkbox) {
  margin-right: 8px;
}

/* 不同类型节点的样式 */
:deep(.el-tree-node[data-type="module"]) {
  font-weight: 600;
}

:deep(.el-tree-node[data-type="resource"]) {
  font-weight: 500;
}

:deep(.el-tree-node[data-type="permission"]) {
  font-weight: normal;
}

/* 搜索高亮 */
:deep(.el-tree-node__label) {
  word-break: break-word;
}

/* 加载状态 */
.tree-container[v-loading] {
  min-height: 200px;
}
</style>