<template>
  <div class="provider-management" :class="{ 'keyboard-user': isKeyboardUser }" ref="containerRef">
    <!-- 跳过链接 -->
    <div class="skip-links">
      <a v-for="link in skipLinks" :key="link.href" :href="link.href" class="skip-link">
        {{ link.text }}
      </a>
    </div>

    <div class="container">
      <!-- 页面头部 -->
      <header class="header" role="banner">
        <div class="header-content">
          <h1 id="page-title">供应商管理</h1>
          <p class="header-description">管理AI模型供应商配置</p>
        </div>
        <div class="header-actions">
          <button
            v-if="canCreateProvider"
            @click="handleCreateProvider"
            class="btn btn-primary"
            :disabled="loading"
            :aria-describedby="loading ? 'loading-status' : undefined"
          >
            <svg class="icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path
                fill-rule="evenodd"
                d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                clip-rule="evenodd"
              />
            </svg>
            添加供应商
          </button>
        </div>
      </header>

      <!-- 搜索筛选区域 -->
      <section
        id="search-filters"
        class="search-filters"
        role="search"
        aria-labelledby="search-heading"
      >
        <h2 id="search-heading" class="sr-only">搜索和筛选供应商</h2>
        <div class="filters-row">
          <div class="search-section">
            <SearchInput
              v-model="searchInput"
              placeholder="搜索供应商名称..."
              :loading="loading"
              aria-label="搜索供应商名称"
              @search="handleSearch"
            />
          </div>
          <div class="filter-section" role="group" aria-label="筛选选项">
            <SelectFilter
              v-model="searchState.providerType"
              :options="PROVIDER_TYPE_OPTIONS"
              placeholder="供应商类型"
              aria-label="按供应商类型筛选"
              @change="handleProviderTypeFilter"
            />
            <SelectFilter
              v-model="searchState.status"
              :options="STATUS_OPTIONS"
              placeholder="状态"
              aria-label="按状态筛选"
              @change="handleStatusFilter"
            />
            <button
              v-if="hasActiveFilters"
              @click="clearFilters"
              class="btn btn-secondary btn-sm"
              aria-label="清除所有筛选条件"
            >
              清除筛选
            </button>
          </div>
        </div>
      </section>

      <!-- 页面内容区域 -->
      <main id="main-content" class="page-content" role="main" aria-labelledby="page-title">
        <!-- 状态公告区域 -->
        <div id="loading-status" class="sr-only" aria-live="polite" aria-atomic="true">
          {{ loading ? '正在加载供应商数据' : '' }}
        </div>

        <!-- 错误提示 -->
        <ErrorAlert
          v-if="error && !loading"
          :error="error"
          role="alert"
          @dismiss="clearError"
          @retry="loadProviders"
          :show-retry="true"
        />

        <!-- 加载状态 -->
        <div
          v-if="loading && providers.length === 0"
          class="loading-container"
          role="status"
          aria-label="正在加载供应商数据"
        >
          <LoadingSpinner />
          <p class="loading-text">正在加载供应商数据...</p>
        </div>

        <!-- 供应商卡片网格 -->
        <section
          v-else-if="providers.length > 0"
          id="providers-grid"
          class="providers-grid"
          role="region"
          :aria-label="`供应商列表，共 ${totalItems} 个供应商`"
        >
          <h2 class="sr-only">供应商列表</h2>
          <ProviderCard
            v-for="provider in providers"
            :key="provider.provider_id"
            :provider="provider"
            :can-edit="canEditProvider"
            :can-delete="canDeleteProvider"
            :can-toggle-status="canToggleProviderStatus"
            :can-view-details="canViewProviderDetails"
            @edit="handleEditProvider"
            @delete="handleDeleteProviderAction"
            @toggle-status="handleToggleProviderStatus"
            @view-details="handleViewProviderDetails"
          />
        </section>

        <!-- 空状态 -->
        <EmptyState
          v-else-if="!loading"
          :title="hasActiveFilters ? '未找到匹配的供应商' : '暂无供应商数据'"
          :description="
            hasActiveFilters ? '请尝试调整搜索条件或筛选器' : '开始添加您的第一个AI模型供应商'
          "
          :show-create-button="!hasActiveFilters && canCreateProvider"
          create-button-text="添加供应商"
          role="region"
          aria-label="空状态提示"
          @create="handleCreateProvider"
        />
      </main>

      <!-- 分页组件 -->
      <div v-if="totalPages > 1" class="pagination-container">
        <Pagination
          :current-page="currentPage"
          :total-pages="totalPages"
          :total-items="totalItems"
          :page-size="pageSize"
          @page-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 对话框组件 -->
    <ProviderDialogForm
      v-model="showFormDialog"
      :provider="selectedProvider"
      :mode="formMode"
      @save="handleSaveProvider"
      @cancel="closeFormDialog"
    />

    <ProviderDetailDialog
      v-model="showDetailDialog"
      :provider="selectedProvider"
      @edit="openEditDialog"
      @delete="handleDeleteProviderAction"
      @toggle-status="handleToggleStatus"
      @close="closeDetailDialog"
    />

    <ConfirmDeleteDialog
      v-model="showDeleteDialog"
      :provider="selectedProvider"
      @confirm="handleDeleteProvider"
      @cancel="closeDeleteDialog"
    />

    <!-- 成功提示 -->
    <SuccessToast v-if="showSuccessToast" :message="successMessage" @close="hideSuccessToast" />

    <!-- ARIA Live Regions for screen reader announcements -->
    <AriaLiveRegions
      :loading="loading"
      :loading-message="loading ? '正在加载供应商数据' : ''"
      :error-message="error || ''"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElBreadcrumb, ElBreadcrumbItem } from 'element-plus'
import { useAuth } from '@/composables/useAuth'
import { useNotification } from '@/composables/useNotification'
import { useProviderPermissions } from '@/composables/useProviderPermissions'
import { useProviderManagement } from '@/composables/useProviderManagement'
import { useProviderSearch } from '@/composables/useProviderSearch'
import {
  useKeyboardNavigation,
  useFocusIndicator,
  useSkipLinks,
} from '@/composables/useKeyboardNavigation'
import { useAriaAnnouncements } from '@/composables/useAriaAnnouncements'

// 组件导入
import SearchInput from '@/components/ui/SearchInput.vue'
import SelectFilter from '@/components/ui/SelectFilter.vue'
import ErrorAlert from '@/components/ui/ErrorAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import Pagination from '@/components/ui/Pagination.vue'
import SuccessToast from '@/components/ui/SuccessToast.vue'
import ProviderCard from '@/components/provider/ProviderCard.vue'
import ProviderDialogForm from '@/components/provider/ProviderDialogForm.vue'
import ProviderDetailDialog from '@/components/provider/ProviderDetailDialog.vue'
import ConfirmDeleteDialog from '@/components/provider/ConfirmDeleteDialog.vue'
import AriaLiveRegions from '@/components/ui/AriaLiveRegions.vue'

// 类型导入
import type { Provider } from '@/types/providerTypes'

// 路由和权限
const router = useRouter()
const { isAuthenticated } = useAuth()
const { showError } = useNotification()
const {
  canAccessProviderManagement,
  canCreateProvider,
  canEditProvider,
  canDeleteProvider,
  canToggleProviderStatus,
  canViewProviderDetails,
  checkProviderPermission,
  getPermissionErrorMessage,
} = useProviderPermissions()

// 键盘导航和无障碍访问
const { containerRef, handleKeyDown } = useKeyboardNavigation()
const { isKeyboardUser } = useFocusIndicator()
const { skipLinks, addSkipLink } = useSkipLinks()
const {
  announceSuccess,
  announceError,
  announceLoading,
  announceLoadingComplete,
  announceSearchResults,
  announceFilterResults,
  announcePagination,
} = useAriaAnnouncements()

// Composables
const {
  providers,
  loading,
  error,
  pagination,
  showFormDialog,
  showDetailDialog,
  showDeleteDialog,
  selectedProvider,
  isEditMode,
  userFeedback,
  isEmpty,
  loadProviders,
  openCreateDialog,
  openEditDialog,
  openDetailDialog,
  openDeleteDialog,
  handleSaveProvider,
  handleDeleteProvider,
  handleToggleStatus,
  closeFormDialog,
  closeDetailDialog,
  closeDeleteDialog,
  clearError,
  clearFeedback,
  handlePageChange: managementPageChange,
  cleanup,
} = useProviderManagement()

const {
  searchInput,
  searchState,
  hasActiveFilters,
  handleSearchInput,
  handleProviderTypeFilter,
  handleStatusFilter,
  resetFilters,
  handlePageChange: searchPageChange,
  PROVIDER_TYPE_OPTIONS,
  STATUS_OPTIONS,
} = useProviderSearch()

// 计算属性
const currentPage = computed(() => pagination.value.page)
const totalPages = computed(() => pagination.value.pages)
const totalItems = computed(() => pagination.value.total)
const pageSize = computed(() => pagination.value.size)

const formMode = computed(() => (isEditMode.value ? 'edit' : 'create'))

const showSuccessToast = computed(() => userFeedback.value?.type === 'success')

const successMessage = computed(() =>
  userFeedback.value?.type === 'success' ? userFeedback.value.message : '',
)

// 搜索和筛选处理
const handleSearch = (value: string) => {
  handleSearchInput(value)

  // 公告搜索结果
  setTimeout(() => {
    if (!loading.value) {
      announceSearchResults(providers.value.length, value)
    }
  }, 500)
}

const handleFilter = () => {
  // 筛选逻辑已在useProviderSearch中处理

  // 公告筛选结果
  setTimeout(() => {
    if (!loading.value) {
      const filterDesc = getActiveFilterDescription()
      announceFilterResults(providers.value.length, filterDesc)
    }
  }, 500)
}

const clearFilters = () => {
  resetFilters()
  announceSuccess('已清除所有筛选条件')
}

// 分页处理
const handlePageChange = (page: number) => {
  searchPageChange(page)

  // 公告分页变化
  setTimeout(() => {
    if (!loading.value) {
      announcePagination(currentPage.value, totalPages.value, totalItems.value)
    }
  }, 300)
}

// 获取当前激活的筛选描述
const getActiveFilterDescription = () => {
  const filters = []
  if (searchState.providerType) {
    const typeOption = PROVIDER_TYPE_OPTIONS.find((opt) => opt.value === searchState.providerType)
    filters.push(`类型：${typeOption?.label || searchState.providerType}`)
  }
  if (searchState.status) {
    const statusOption = STATUS_OPTIONS.find((opt) => opt.value === searchState.status)
    filters.push(`状态：${statusOption?.label || searchState.status}`)
  }
  return filters.join('，')
}

// 成功提示处理
const hideSuccessToast = () => {
  clearFeedback()
}

// 权限检查的操作处理方法
const handleCreateProvider = () => {
  if (checkOperationPermission('create')) {
    openCreateDialog()
    announceSuccess('已打开创建供应商对话框')
  }
}

const handleEditProvider = (provider: Provider) => {
  if (checkOperationPermission('edit')) {
    openEditDialog(provider)
    announceSuccess(`已打开编辑供应商"${provider.display_name}"的对话框`)
  }
}

const handleDeleteProviderAction = (provider: Provider) => {
  if (checkOperationPermission('delete')) {
    openDeleteDialog(provider)
    announceSuccess(`已打开删除供应商"${provider.display_name}"的确认对话框`)
  }
}

const handleToggleProviderStatus = async (provider: Provider) => {
  if (checkOperationPermission('toggle_status')) {
    const action = provider.is_active ? '停用' : '激活'
    announceLoading(`正在${action}供应商"${provider.display_name}"`)

    try {
      await handleToggleStatus(provider)
      announceSuccess(`已成功${action}供应商"${provider.display_name}"`)
    } catch (error) {
      announceError(`${action}供应商"${provider.display_name}"失败`)
    }
  }
}

const handleViewProviderDetails = (provider: Provider) => {
  if (checkOperationPermission('view_details')) {
    openDetailDialog(provider)
    announceSuccess(`已打开供应商"${provider.display_name}"的详情对话框`)
  }
}

// 权限检查 - 暂时简化，只检查用户是否已认证
const checkPermissions = () => {
  if (!isAuthenticated.value) {
    showError('请先登录系统')
    router.push('/auth/login')
    return false
  }
  return true
}

// 操作权限检查 - 暂时简化，只检查用户是否已认证
const checkOperationPermission = (action: string): boolean => {
  if (!isAuthenticated.value) {
    showError('请先登录系统')
    return false
  }
  return true
}

// 页面初始化
onMounted(() => {
  // 首先检查权限
  if (!checkPermissions()) {
    return
  }

  // 添加跳过链接
  addSkipLink('#main-content', '跳转到主要内容')
  addSkipLink('#search-filters', '跳转到搜索筛选')
  addSkipLink('#providers-grid', '跳转到供应商列表')

  // 添加键盘导航事件监听
  document.addEventListener('keydown', handleKeyDown)

  // 添加键盘用户检测类
  if (isKeyboardUser.value) {
    document.body.classList.add('keyboard-user')
  }
})

// 页面清理
onUnmounted(() => {
  cleanup()

  // 移除键盘导航事件监听
  document.removeEventListener('keydown', handleKeyDown)

  // 移除键盘用户检测类
  document.body.classList.remove('keyboard-user')
})
</script>

<style scoped>
.provider-management {
  min-height: 100vh;
  background-color: var(--color-background);
}

.container {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: var(--space-lg);
}

/* 页面头部 - 与其他管理页面保持一致 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.header-content h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-sm) 0;
}

.header-description {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
}

/* 搜索筛选区域 */
.search-filters {
  margin-bottom: var(--space-xl);
}

.filters-row {
  display: flex;
  gap: var(--space-md);
  align-items: flex-start;
}

.search-section {
  flex: 1;
  max-width: 400px;
}

.filter-section {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

/* 页面内容 */
.page-content {
  min-height: 400px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl) 0;
}

.loading-text {
  margin-top: var(--space-md);
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

/* 供应商网格布局 - 响应式设计 */
.providers-grid {
  display: grid;
  gap: var(--space-lg);
  margin-bottom: var(--space-2xl);

  /* 桌面端：3-4列布局 */
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));

  /* 确保卡片在大屏幕上不会过宽 */
  max-width: 100%;
}

/* 大屏幕优化 - 4列布局 */
@media (min-width: 1400px) {
  .providers-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-xl);
  }
}

/* 桌面端 - 3列布局 */
@media (min-width: 1024px) and (max-width: 1399px) {
  .providers-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-lg);
  }
}

/* 分页容器 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: var(--space-xl);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border);
}

/* 按钮样式 - 使用设计系统 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--maas-primary-600);
  color: var(--maas-white);
  border-color: var(--maas-primary-600);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--maas-primary-700);
  border-color: var(--maas-primary-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background-color: var(--maas-white);
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-background-soft);
  border-color: var(--color-border-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn-sm {
  padding: var(--space-xs) var(--space-sm);
  font-size: 0.8125rem;
}

.icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

/* 平板设备响应式设计 - 2-3列布局 */
@media (min-width: 768px) and (max-width: 1023px) {
  .providers-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-md);
    /* 在平板上最多3列 */
    max-width: calc(3 * 280px + 2 * var(--space-md));
    margin: 0 auto var(--space-2xl);
  }

  .container {
    padding: var(--space-md);
  }
}

/* 小平板设备 - 2列布局 */
@media (min-width: 640px) and (max-width: 767px) {
  .providers-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-md);
  }

  .container {
    padding: var(--space-md);
  }

  .filters-row {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .search-section {
    max-width: none;
  }

  .filter-section {
    flex-wrap: wrap;
    gap: var(--space-sm);
  }
}

/* 移动设备响应式设计 - 单列布局 */
@media (max-width: 639px) {
  .providers-grid {
    grid-template-columns: 1fr;
    gap: var(--space-md);
  }

  .container {
    padding: var(--space-sm);
  }

  .header {
    flex-direction: column;
    gap: var(--space-md);
    align-items: stretch;
  }

  .header-actions {
    justify-content: flex-end;
  }

  .filters-row {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .search-section {
    max-width: none;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-sm);
  }
}

/* 超小屏幕优化 */
@media (max-width: 480px) {
  .header-content h1 {
    font-size: 1.5rem;
  }

  .btn {
    padding: 0.625rem 0.875rem;
    font-size: 0.8125rem;
  }

  .providers-grid {
    gap: var(--space-sm);
  }
}

/* 无障碍访问样式 */
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

/* 跳过链接 */
.skip-links {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 9999;
}

.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--maas-primary-600);
  color: white;
  padding: 8px 12px;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
  transition: top 0.3s ease;
  white-space: nowrap;
}

.skip-link:focus {
  top: 6px;
  outline: 2px solid white;
  outline-offset: 2px;
}

/* 键盘用户的焦点增强 */
.keyboard-user *:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
}

.keyboard-user .btn:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.keyboard-user .providers-grid:focus-within {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 4px;
  border-radius: var(--radius-lg);
}

/* 焦点指示器增强 */
.btn:focus-visible {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .skip-link {
    border: 2px solid white;
  }

  .btn {
    border-width: 2px;
  }

  .keyboard-user *:focus {
    outline-width: 3px;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .skip-link {
    transition: none;
  }

  .btn {
    transition: none;
  }
}
</style>
