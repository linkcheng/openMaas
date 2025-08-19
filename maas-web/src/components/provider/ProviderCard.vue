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
  <div
    class="provider-card"
    :class="{
      inactive: !provider.is_active,
      clickable: true,
      loading: loading,
    }"
    role="article"
    :aria-label="`供应商 ${provider.display_name}，状态：${statusText}，类型：${getProviderTypeLabel(provider.provider_type)}`"
    tabindex="0"
    @click="handleCardClick"
    @keydown="handleCardKeyDown"
  >
    <!-- 卡片头部：图标、名称、状态 -->
    <div class="card-header">
      <div class="provider-icon">
        <LazyImage
          v-if="providerIcon"
          :src="providerIcon"
          :alt="`${provider.display_name} 图标`"
          class="icon-image"
          image-class="icon-img"
          :show-placeholder-icon="false"
          :eager="false"
          @error="handleIconError"
        />
        <div v-else class="icon-placeholder">
          {{ provider.display_name.charAt(0).toUpperCase() }}
        </div>
      </div>

      <div class="provider-info">
        <h3 class="provider-name" :id="`provider-${provider.provider_id}`">
          {{ provider.display_name }}
        </h3>
        <p class="provider-type">{{ getProviderTypeLabel(provider.provider_type) }}</p>
      </div>

      <div class="status-indicator" :class="statusClass">
        <span class="status-dot" :aria-hidden="true"></span>
        <span class="status-text">{{ statusText }}</span>
      </div>
    </div>

    <!-- 卡片内容：描述和元数据 -->
    <div class="card-body">
      <p class="provider-description">
        {{ provider.description || '暂无描述' }}
      </p>

      <div class="provider-meta">
        <span class="meta-item" :title="`创建时间: ${formatDate(provider.created_at)}`">
          <el-icon class="meta-icon" aria-hidden="true">
            <Calendar />
          </el-icon>
          <span class="sr-only">创建时间:</span>
          {{ formatDate(provider.created_at) }}
        </span>
        <span class="meta-item" :title="`创建者: ${provider.created_by}`">
          <el-icon class="meta-icon" aria-hidden="true">
            <User />
          </el-icon>
          <span class="sr-only">创建者:</span>
          {{ provider.created_by }}
        </span>
      </div>
    </div>

    <!-- 卡片操作按钮 -->
    <div class="card-actions">
      <button
        v-if="buttonStates.view.visible"
        @click.stop="handleViewDetails"
        @keydown="handleKeyDown($event, 'view')"
        class="action-btn btn-secondary"
        :class="{ loading: loading }"
        :disabled="buttonStates.view.disabled"
        :title="`查看 ${provider.display_name} 详情`"
        :aria-describedby="`provider-${provider.provider_id}`"
        :aria-label="`查看供应商 ${provider.display_name} 的详细信息`"
      >
        <el-icon class="btn-icon" aria-hidden="true">
          <View />
        </el-icon>
        <span class="sr-only">查看详情</span>
      </button>

      <button
        v-if="buttonStates.edit.visible"
        @click.stop="handleEdit"
        @keydown="handleKeyDown($event, 'edit')"
        class="action-btn btn-secondary"
        :class="{ loading: loading }"
        :disabled="buttonStates.edit.disabled"
        :title="`编辑 ${provider.display_name}`"
        :aria-describedby="`provider-${provider.provider_id}`"
        :aria-label="`编辑供应商 ${provider.display_name} 的配置`"
      >
        <el-icon class="btn-icon" aria-hidden="true">
          <Edit />
        </el-icon>
        <span class="sr-only">编辑</span>
      </button>

      <button
        v-if="buttonStates.toggleStatus.visible"
        @click.stop="handleStatusToggle"
        @keydown="handleKeyDown($event, 'toggle-status')"
        class="action-btn btn-secondary"
        :class="{ loading: loading }"
        :disabled="buttonStates.toggleStatus.disabled"
        :title="
          provider.is_active ? `停用 ${provider.display_name}` : `激活 ${provider.display_name}`
        "
        :aria-describedby="`provider-${provider.provider_id}`"
        :aria-label="
          provider.is_active
            ? `停用供应商 ${provider.display_name}`
            : `激活供应商 ${provider.display_name}`
        "
      >
        <el-icon
          class="btn-icon"
          :class="{
            'text-green': provider.is_active,
            'text-gray': !provider.is_active,
          }"
          aria-hidden="true"
        >
          <Switch />
        </el-icon>
        <span class="sr-only">{{ provider.is_active ? '停用' : '激活' }}</span>
      </button>

      <button
        v-if="buttonStates.delete.visible"
        @click.stop="handleDelete"
        @keydown="handleKeyDown($event, 'delete')"
        class="action-btn btn-danger"
        :class="{ loading: loading }"
        :disabled="buttonStates.delete.disabled"
        :title="provider.is_active ? '激活状态下无法删除' : `删除 ${provider.display_name}`"
        :aria-describedby="`provider-${provider.provider_id}`"
        :aria-label="
          provider.is_active
            ? '供应商处于激活状态，无法删除'
            : `删除供应商 ${provider.display_name}`
        "
      >
        <el-icon class="btn-icon" aria-hidden="true">
          <Delete />
        </el-icon>
        <span class="sr-only">删除</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Provider } from '@/types/providerTypes'
import { PROVIDER_ICONS, PROVIDER_TYPE_OPTIONS } from '@/types/providerTypes'
import LazyImage from '@/components/ui/LazyImage.vue'

// Element Plus 图标组件
import { Calendar, User, View, Edit, Switch, Delete } from '@element-plus/icons-vue'

interface Props {
  provider: Provider
  canEdit?: boolean
  canDelete?: boolean
  canToggleStatus?: boolean
  canViewDetails?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canEdit: true,
  canDelete: true,
  canToggleStatus: true,
  canViewDetails: true,
  loading: false,
})

const emit = defineEmits<{
  'view-details': [provider: Provider]
  edit: [provider: Provider]
  delete: [provider: Provider]
  'toggle-status': [provider: Provider]
}>()

// 供应商图标
const providerIcon = computed(() => {
  return PROVIDER_ICONS[props.provider.provider_type as keyof typeof PROVIDER_ICONS]
})

// 供应商类型标签
const getProviderTypeLabel = (type: string) => {
  const option = PROVIDER_TYPE_OPTIONS.find((opt) => opt.value === type)
  return option?.label || type
}

// 状态相关计算属性
const statusClass = computed(() => ({
  'status-active': props.provider.is_active,
  'status-inactive': !props.provider.is_active,
}))

// 多语言状态文本支持
const statusText = computed(() => {
  // 这里可以集成 i18n 国际化库
  const statusLabels = {
    active: {
      'zh-CN': '激活',
      'en-US': 'Active',
      'ja-JP': 'アクティブ',
    },
    inactive: {
      'zh-CN': '停用',
      'en-US': 'Inactive',
      'ja-JP': '非アクティブ',
    },
  }

  // 默认使用中文，可以从全局状态或配置中获取当前语言
  const currentLang = 'zh-CN' // 可以从 useI18n() 或其他地方获取
  const status = props.provider.is_active ? 'active' : 'inactive'

  return statusLabels[status][currentLang] || statusLabels[status]['zh-CN']
})

// 日期格式化
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// 处理卡片点击
const handleCardClick = () => {
  emit('view-details', props.provider)
}

// 处理图标加载错误
const handleIconError = () => {
  // 图标加载失败时的处理逻辑
  console.warn(`Failed to load icon for provider: ${props.provider.provider_type}`)
}

// 权限检查
const canPerformAction = (action: string) => {
  switch (action) {
    case 'view':
      return props.canViewDetails
    case 'edit':
      return props.canEdit
    case 'delete':
      return props.canDelete
    case 'toggle-status':
      return props.canToggleStatus
    default:
      return false
  }
}

// 按钮状态计算
const buttonStates = computed(() => ({
  view: {
    visible: canPerformAction('view'),
    disabled: props.loading,
  },
  edit: {
    visible: canPerformAction('edit'),
    disabled: props.loading,
  },
  toggleStatus: {
    visible: canPerformAction('toggle-status'),
    disabled: props.loading,
  },
  delete: {
    visible: canPerformAction('delete'),
    disabled: props.loading || props.provider.is_active, // 激活状态下不能删除
  },
}))

// 处理状态切换动画
const handleStatusToggle = (event: Event) => {
  if (props.loading || !canPerformAction('toggle-status')) {
    return
  }

  const statusIndicator = (event.currentTarget as HTMLElement)
    .closest('.provider-card')
    ?.querySelector('.status-indicator')

  if (statusIndicator) {
    statusIndicator.classList.add('status-changing')
    setTimeout(() => {
      statusIndicator.classList.remove('status-changing')
    }, 600)
  }

  emit('toggle-status', props.provider)
}

// 处理其他操作
const handleViewDetails = () => {
  if (props.loading || !canPerformAction('view')) return
  emit('view-details', props.provider)
}

const handleEdit = () => {
  if (props.loading || !canPerformAction('edit')) return
  emit('edit', props.provider)
}

const handleDelete = () => {
  if (props.loading || !canPerformAction('delete') || props.provider.is_active) return
  emit('delete', props.provider)
}

// 键盘导航处理
const handleKeyDown = (event: KeyboardEvent, action: string) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    switch (action) {
      case 'view':
        handleViewDetails()
        break
      case 'edit':
        handleEdit()
        break
      case 'toggle-status':
        handleStatusToggle(event)
        break
      case 'delete':
        handleDelete()
        break
    }
  }
}

// 卡片级别的键盘导航
const handleCardKeyDown = (event: KeyboardEvent) => {
  const card = event.currentTarget as HTMLElement
  const buttons = card.querySelectorAll(
    '.action-btn:not([disabled])',
  ) as NodeListOf<HTMLButtonElement>

  switch (event.key) {
    case 'Enter':
    case ' ':
      // 如果卡片本身有焦点，触发查看详情
      if (document.activeElement === card) {
        event.preventDefault()
        handleCardClick()
      }
      break

    case 'ArrowRight':
    case 'ArrowDown':
      // 方向键向右/下导航到第一个按钮
      if (document.activeElement === card && buttons.length > 0) {
        event.preventDefault()
        buttons[0].focus()
      } else if (buttons.length > 0) {
        // 在按钮间导航
        event.preventDefault()
        const currentIndex = Array.from(buttons).findIndex((btn) => btn === document.activeElement)
        const nextIndex = currentIndex >= buttons.length - 1 ? 0 : currentIndex + 1
        buttons[nextIndex].focus()
      }
      break

    case 'ArrowLeft':
    case 'ArrowUp':
      // 方向键向左/上导航
      if (buttons.length > 0) {
        const currentIndex = Array.from(buttons).findIndex((btn) => btn === document.activeElement)
        if (currentIndex > 0) {
          event.preventDefault()
          buttons[currentIndex - 1].focus()
        } else if (currentIndex === 0) {
          // 从第一个按钮返回到卡片
          event.preventDefault()
          card.focus()
        }
      }
      break

    case 'Home':
      // Home键聚焦到卡片
      if (Array.from(buttons).some((btn: HTMLButtonElement) => btn === document.activeElement)) {
        event.preventDefault()
        card.focus()
      }
      break

    case 'End':
      // End键聚焦到最后一个按钮
      if (
        buttons.length > 0 &&
        (document.activeElement === card ||
          Array.from(buttons).some((btn: HTMLButtonElement) => btn === document.activeElement))
      ) {
        event.preventDefault()
        buttons[buttons.length - 1].focus()
      }
      break

    case 'Escape':
      // Escape键返回到卡片
      if (Array.from(buttons).some((btn: HTMLButtonElement) => btn === document.activeElement)) {
        event.preventDefault()
        card.focus()
      }
      break
  }
}
</script>

<style scoped>
.provider-card {
  background: var(--maas-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
}

.provider-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
  border-color: var(--maas-primary-500);
}

.provider-card:active {
  transform: translateY(-1px);
  transition-duration: 0.1s;
}

.provider-card:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
}

.provider-card.inactive {
  opacity: 0.7;
  background: var(--color-background-soft);
  border-color: var(--color-border);
  position: relative;
}

.provider-card.inactive::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 10px,
    rgba(0, 0, 0, 0.02) 10px,
    rgba(0, 0, 0, 0.02) 20px
  );
  pointer-events: none;
  border-radius: 12px;
}

.provider-card.inactive:hover {
  opacity: 0.85;
  transform: translateY(-1px);
}

.provider-card.inactive .provider-name {
  color: var(--color-text-secondary);
}

.provider-card.inactive .provider-description {
  color: var(--color-text-tertiary);
}

.provider-card.inactive .action-btn {
  opacity: 0.8;
}

.provider-card.inactive .action-btn:hover {
  opacity: 1;
}

.provider-card.loading {
  pointer-events: none;
  position: relative;
}

.provider-card.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(1px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.provider-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;
}

.provider-card:hover .provider-icon {
  transform: scale(1.05);
  border-color: var(--maas-primary-500);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.provider-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.icon-placeholder {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  background: linear-gradient(135deg, var(--maas-primary-500), var(--maas-primary-600));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.provider-info {
  flex: 1;
  min-width: 0;
}

.provider-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-xs) 0;
  line-height: 1.4;
  word-break: break-word;
}

.provider-type {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
  font-weight: 500;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xs) var(--space-sm);
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  flex-shrink: 0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.status-indicator::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.6s ease;
}

.provider-card:hover .status-indicator::before {
  left: 100%;
}

.status-indicator.status-active {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  color: var(--maas-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);
}

.status-indicator.status-active:hover {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
  transform: translateY(-1px) scale(1.02);
}

.status-indicator.status-inactive {
  background: linear-gradient(135deg, var(--color-background-soft), var(--color-background-mute));
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.status-indicator.status-inactive:hover {
  background: linear-gradient(135deg, var(--maas-gray-100), var(--maas-gray-200));
  box-shadow: var(--shadow-md);
  transform: translateY(-1px) scale(1.02);
}

/* 状态切换时的闪烁效果 */
.status-indicator.status-changing {
  animation: status-change 0.6s ease;
}

.status-indicator.status-changing .status-dot {
  animation: dot-pulse 0.6s ease;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  transition: all 0.3s ease;
  position: relative;
}

.status-active .status-dot {
  background: var(--maas-success);
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
  animation: pulse-green 2s infinite;
}

.status-inactive .status-dot {
  background: var(--color-text-secondary);
  box-shadow: 0 0 0 2px rgba(115, 115, 115, 0.1);
}

/* 状态切换动画 */
@keyframes pulse-green {
  0% {
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
  }
  100% {
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
  }
}

@keyframes status-change {
  0% {
    transform: scale(1);
  }
  25% {
    transform: scale(1.05);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
  }
  75% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes dot-pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.status-indicator.status-changing {
  animation: status-change 0.6s ease;
}

/* 卡片内容 */
.card-body {
  margin-bottom: var(--space-lg);
}

.provider-description {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0 0 var(--space-md) 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.provider-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.meta-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  font-size: 14px;
}

/* 卡片操作 */
.card-actions {
  display: flex;
  gap: var(--space-sm);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border);
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--maas-white);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.action-btn:hover {
  background: var(--color-background-soft);
  border-color: var(--maas-primary-500);
  color: var(--maas-primary-600);
  transform: translateY(-2px) scale(1.05);
  box-shadow: var(--shadow-md);
}

.action-btn:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
  transform: scale(1.02);
}

.action-btn:active {
  transform: translateY(0) scale(0.98);
  transition-duration: 0.1s;
}

/* 按钮点击波纹效果 */
.action-btn {
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.3);
  transform: translate(-50%, -50%);
  transition:
    width 0.3s ease,
    height 0.3s ease;
}

.action-btn:active::before {
  width: 100px;
  height: 100px;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.action-btn.loading {
  position: relative;
  color: transparent;
}

.action-btn.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 12px;
  height: 12px;
  margin: -6px 0 0 -6px;
  border: 2px solid currentColor;
  border-radius: 50%;
  border-top-color: transparent;
  animation: button-loading 0.8s linear infinite;
  color: var(--color-text-secondary);
}

@keyframes button-loading {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.btn-danger {
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--maas-error);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.05);
  border-color: var(--maas-error);
  color: var(--maas-error);
}

.btn-danger:disabled {
  opacity: 0.4;
  background: var(--color-background-soft);
  border-color: var(--color-border);
  color: var(--color-text-tertiary);
}

.btn-danger:disabled:hover {
  background: var(--color-background-soft);
  border-color: var(--color-border);
  color: var(--color-text-tertiary);
  transform: none;
  box-shadow: none;
}

.btn-icon {
  width: 16px;
  height: 16px;
  font-size: 16px;
}

.text-green {
  color: var(--maas-success) !important;
}

.text-gray {
  color: var(--color-text-secondary) !important;
}

/* 无障碍访问 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 焦点指示器增强 */
.provider-card:focus-visible {
  outline: 3px solid var(--maas-primary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.1);
}

.action-btn:focus-visible {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

/* 键盘用户的焦点增强 */
.keyboard-user .provider-card:focus {
  outline: 3px solid var(--maas-primary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.1);
}

.keyboard-user .action-btn:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

/* 跳过链接样式 */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--maas-primary-600);
  color: white;
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 1000;
  font-weight: 600;
  font-size: 0.875rem;
  transition: top 0.3s ease;
}

.skip-link:focus {
  top: 6px;
  outline: 2px solid white;
  outline-offset: 2px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .provider-card {
    padding: var(--space-md);
  }

  .card-header {
    gap: var(--space-sm);
  }

  .provider-icon {
    width: 40px;
    height: 40px;
  }

  .icon-placeholder {
    font-size: 1.25rem;
  }

  .provider-name {
    font-size: 1rem;
  }

  .provider-meta {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .card-actions {
    gap: var(--space-xs);
  }

  .action-btn {
    width: 32px;
    height: 32px;
  }

  .btn-icon {
    width: 14px;
    height: 14px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .provider-card {
    padding: var(--space-sm);
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }

  .status-indicator {
    align-self: flex-end;
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .provider-card {
    background: var(--color-background);
    border-color: var(--color-border);
  }

  .provider-card.inactive {
    background: var(--color-background-soft);
  }

  .provider-icon {
    background: var(--color-background-soft);
    border-color: var(--color-border);
  }

  .action-btn {
    background: var(--color-background);
    border-color: var(--color-border);
  }

  .action-btn:hover {
    background: var(--color-background-soft);
  }

  .status-indicator.status-active {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
    border-color: rgba(16, 185, 129, 0.3);
  }

  .status-indicator.status-inactive {
    background: linear-gradient(135deg, var(--color-background-soft), var(--color-background-mute));
    border-color: var(--color-border);
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .provider-card {
    border-width: 2px;
  }

  .provider-card:focus {
    outline-width: 3px;
  }

  .action-btn {
    border-width: 2px;
  }

  .status-dot {
    border: 2px solid currentColor;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .provider-card,
  .action-btn,
  .status-indicator {
    transition: none;
  }

  .provider-card:hover {
    transform: none;
  }

  .action-btn:hover {
    transform: none;
  }
}
</style>
