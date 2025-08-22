<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    :width="dialogWidth"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    destroy-on-close
    @close="handleClose"
  >
    <div class="role-edit-dialog">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        label-position="right"
        @submit.prevent
      >
        <!-- 角色名称 -->
        <el-form-item label="角色名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入角色名称（英文标识）"
            :disabled="mode === 'edit' && formData.is_system_role"
            clearable
            maxlength="50"
            show-word-limit
          >
            <template #prefix>
              <el-icon><Key /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            角色名称用作系统内部标识，建议使用英文和下划线，如：admin、editor
          </div>
        </el-form-item>

        <!-- 显示名称 -->
        <el-form-item label="显示名称" prop="display_name">
          <el-input
            v-model="formData.display_name"
            placeholder="请输入角色显示名称"
            clearable
            maxlength="100"
            show-word-limit
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            显示名称用于界面展示，支持中文，如：管理员、编辑者
          </div>
        </el-form-item>

        <!-- 角色类型 -->
        <el-form-item label="角色类型" prop="role_type">
          <el-radio-group
            v-model="formData.role_type"
            :disabled="mode === 'edit'"
          >
            <el-radio value="system">
              <div class="radio-content">
                <div class="radio-title">
                  <el-icon><Setting /></el-icon>
                  系统角色
                </div>
                <div class="radio-description">
                  系统预定义角色，具有特殊权限，不可删除
                </div>
              </div>
            </el-radio>
            <el-radio value="custom">
              <div class="radio-content">
                <div class="radio-title">
                  <el-icon><UserFilled /></el-icon>
                  自定义角色
                </div>
                <div class="radio-description">
                  用户自定义角色，可以自由配置权限和删除
                </div>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 角色描述 -->
        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入角色描述信息"
            :rows="4"
            maxlength="500"
            show-word-limit
            resize="none"
          />
          <div class="form-tip">
            详细描述角色的职责和用途，帮助其他管理员理解角色功能
          </div>
        </el-form-item>

        <!-- 权限预览 -->
        <el-form-item v-if="mode === 'edit' && role?.permissions" label="当前权限">
          <div class="permissions-preview">
            <div class="permissions-header">
              <span class="permissions-count">
                共 {{ role.permissions.length }} 个权限
              </span>
              <el-button
                type="primary"
                size="small"
                @click="handleManagePermissions"
              >
                <el-icon><Setting /></el-icon>
                管理权限
              </el-button>
            </div>
            
            <div v-if="role.permissions.length > 0" class="permissions-list">
              <el-tag
                v-for="permission in displayPermissions"
                :key="permission.id"
                :type="getPermissionTagType(permission)"
                size="small"
                class="permission-tag"
              >
                {{ permission.display_name }}
              </el-tag>
              
              <el-button
                v-if="role.permissions.length > maxDisplayPermissions"
                type="info"
                size="small"
                text
                @click="showAllPermissions = !showAllPermissions"
              >
                {{ showAllPermissions ? '收起' : `还有 ${role.permissions.length - maxDisplayPermissions} 个权限` }}
              </el-button>
            </div>
            
            <el-empty
              v-else
              description="暂无权限"
              :image-size="60"
            />
          </div>
        </el-form-item>

        <!-- 系统角色警告 -->
        <el-alert
          v-if="formData.role_type === 'system'"
          title="系统角色提示"
          type="warning"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="system-role-warning">
              <p>系统角色具有以下特点：</p>
              <ul>
                <li>角色名称创建后不可修改</li>
                <li>角色不可删除，确保系统稳定性</li>
                <li>权限配置需要谨慎操作</li>
                <li>建议仅在必要时创建系统角色</li>
              </ul>
            </div>
          </template>
        </el-alert>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <div class="footer-left">
          <el-button
            v-if="mode === 'edit' && !formData.is_system_role"
            type="danger"
            :loading="deleting"
            @click="handleDelete"
          >
            <el-icon><Delete /></el-icon>
            删除角色
          </el-button>
        </div>
        
        <div class="footer-right">
          <el-button @click="handleCancel">
            取消
          </el-button>
          <el-button
            type="primary"
            :loading="saving"
            @click="handleSave"
          >
            <el-icon><Check /></el-icon>
            {{ mode === 'create' ? '创建' : '保存' }}
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElRadioGroup,
  ElRadio,
  ElButton,
  ElIcon,
  ElTag,
  ElAlert,
  ElEmpty,
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules
} from 'element-plus'
import {
  Key,
  User,
  Setting,
  UserFilled,
  Delete,
  Check
} from '@element-plus/icons-vue'
import type { Role, Permission } from '@/types/permission'

interface Props {
  visible: boolean
  mode: 'create' | 'edit'
  role?: Role | null
}

interface Emits {
  (e: 'update:visible', visible: boolean): void
  (e: 'save', roleData: RoleFormData): void
  (e: 'delete', role: Role): void
  (e: 'manage-permissions', role: Role): void
}

interface RoleFormData {
  name: string
  display_name: string
  description: string
  role_type: 'system' | 'custom'
  is_system_role: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  mode: 'create',
  role: null
})

const emit = defineEmits<Emits>()

// 组件引用
const formRef = ref<FormInstance>()

// 状态
const saving = ref(false)
const deleting = ref(false)
const showAllPermissions = ref(false)
const maxDisplayPermissions = 10

// 表单数据
const formData = ref<RoleFormData>({
  name: '',
  display_name: '',
  description: '',
  role_type: 'custom',
  is_system_role: false
})

// 对话框可见性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 对话框标题
const dialogTitle = computed(() => {
  return props.mode === 'create' ? '创建角色' : '编辑角色'
})

// 对话框宽度
const dialogWidth = computed(() => {
  return props.mode === 'edit' && props.role?.permissions ? '800px' : '600px'
})

// 显示的权限列表
const displayPermissions = computed(() => {
  if (!props.role?.permissions) return []
  
  if (showAllPermissions.value) {
    return props.role.permissions
  }
  
  return props.role.permissions.slice(0, maxDisplayPermissions)
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/,
      message: '角色名称必须以字母开头，只能包含字母、数字和下划线',
      trigger: 'blur'
    }
  ],
  display_name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' },
    { min: 1, max: 100, message: '显示名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  role_type: [
    { required: true, message: '请选择角色类型', trigger: 'change' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 获取权限标签类型
function getPermissionTagType(permission: Permission) {
  const actionTypeMap: Record<string, string> = {
    'create': 'success',
    'read': 'info',
    'update': 'warning',
    'delete': 'danger',
    'manage': 'primary'
  }
  return actionTypeMap[permission.action] || 'info'
}

// 初始化表单数据
function initFormData() {
  if (props.mode === 'edit' && props.role) {
    formData.value = {
      name: props.role.name,
      display_name: props.role.display_name,
      description: props.role.description || '',
      role_type: props.role.role_type,
      is_system_role: props.role.is_system_role
    }
  } else {
    formData.value = {
      name: '',
      display_name: '',
      description: '',
      role_type: 'custom',
      is_system_role: false
    }
  }
  
  // 重置权限显示状态
  showAllPermissions.value = false
}

// 处理保存
async function handleSave() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    saving.value = true
    
    // 更新 is_system_role 字段
    const roleData: RoleFormData = {
      ...formData.value,
      is_system_role: formData.value.role_type === 'system'
    }
    
    emit('save', roleData)
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    saving.value = false
  }
}

// 处理取消
function handleCancel() {
  dialogVisible.value = false
}

// 处理关闭
function handleClose() {
  // 重置表单
  if (formRef.value) {
    formRef.value.resetFields()
  }
  
  // 重置状态
  saving.value = false
  deleting.value = false
  showAllPermissions.value = false
}

// 处理删除
async function handleDelete() {
  if (!props.role) return

  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${props.role.display_name}" 吗？此操作不可恢复。`,
      '删除角色',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger'
      }
    )

    deleting.value = true
    emit('delete', props.role)
  } catch {
    // 用户取消删除
  } finally {
    deleting.value = false
  }
}

// 处理权限管理
function handleManagePermissions() {
  if (props.role) {
    emit('manage-permissions', props.role)
  }
}

// 监听对话框可见性变化
watch(() => props.visible, (visible) => {
  if (visible) {
    nextTick(() => {
      initFormData()
    })
  }
})

// 监听角色类型变化
watch(() => formData.value.role_type, (newType) => {
  formData.value.is_system_role = newType === 'system'
})
</script>

<style scoped>
.role-edit-dialog {
  padding: 0 8px;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
  line-height: 1.4;
}

.radio-content {
  margin-left: 8px;
}

.radio-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.radio-description {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.permissions-preview {
  width: 100%;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  padding: 16px;
  background-color: var(--el-bg-color-page);
}

.permissions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.permissions-count {
  font-size: 14px;
  color: var(--el-text-color-regular);
  font-weight: 500;
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.permission-tag {
  margin: 0;
}

.system-role-warning {
  font-size: 13px;
}

.system-role-warning p {
  margin: 0 0 8px 0;
  font-weight: 500;
}

.system-role-warning ul {
  margin: 0;
  padding-left: 20px;
}

.system-role-warning li {
  margin-bottom: 4px;
  line-height: 1.4;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  flex: 1;
}

.footer-right {
  display: flex;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 5vh auto !important;
  }

  .dialog-footer {
    flex-direction: column;
    gap: 12px;
  }

  .footer-left,
  .footer-right {
    width: 100%;
    justify-content: center;
  }

  .permissions-header {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }

  .permissions-list {
    justify-content: center;
  }
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

:deep(.el-radio) {
  margin-bottom: 16px;
  align-items: flex-start;
}

:deep(.el-radio__input) {
  margin-top: 2px;
}

:deep(.el-textarea__inner) {
  font-family: inherit;
}

/* 权限标签样式 */
.permission-tag {
  cursor: default;
}

.permission-tag:hover {
  opacity: 0.8;
}

/* 加载状态 */
.el-button.is-loading {
  pointer-events: none;
}

/* 禁用状态 */
:deep(.el-input.is-disabled .el-input__inner) {
  background-color: var(--el-disabled-bg-color);
  color: var(--el-disabled-text-color);
}

:deep(.el-radio.is-disabled) {
  opacity: 0.6;
}
</style>