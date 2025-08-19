/*
 * Copyright 2025 MaaS Team
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useProviderStore } from '@/stores/providerStore'
import { handleApiError } from '@/utils/api'
import type {
  Provider,
  CreateProviderRequest,
  UpdateProviderRequest,
  ListProvidersParams,
} from '@/types/providerTypes'

// 对话框模式类型
export type DialogMode = 'create' | 'edit' | 'view' | 'delete'

// 操作结果类型
export interface OperationResult {
  success: boolean
  message?: string
  error?: string
}

// 用户反馈类型
export interface UserFeedback {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

export function useProviderManagement() {
  const providerStore = useProviderStore()
  const {
    providers,
    loading,
    error,
    pagination,
    totalPages,
    currentPage,
    totalProviders,
    hasProviders,
  } = storeToRefs(providerStore)

  // 对话框状态管理
  const showFormDialog = ref(false)
  const showDetailDialog = ref(false)
  const showDeleteDialog = ref(false)
  const selectedProvider = ref<Provider | null>(null)
  const dialogMode = ref<DialogMode>('create')

  // 操作状态
  const operationLoading = ref(false)
  const operationError = ref<string | null>(null)

  // 用户反馈状态
  const userFeedback = ref<UserFeedback | null>(null)

  // 页面状态
  const isInitialized = ref(false)
  const retryCount = ref(0)
  const maxRetries = 3

  // 计算属性
  const isEditMode = computed(() => dialogMode.value === 'edit')
  const isCreateMode = computed(() => dialogMode.value === 'create')
  const isViewMode = computed(() => dialogMode.value === 'view')
  const isDeleteMode = computed(() => dialogMode.value === 'delete')

  const hasError = computed(() => !!error.value || !!operationError.value)
  const currentError = computed(() => error.value || operationError.value)

  const canLoadMore = computed(() => pagination.value.page < pagination.value.pages)

  const isEmpty = computed(() => !loading.value && !hasProviders.value && isInitialized.value)

  // 清除错误状态
  const clearError = () => {
    operationError.value = null
    providerStore.clearError()
  }

  // 清除用户反馈
  const clearFeedback = () => {
    userFeedback.value = null
  }

  // 显示用户反馈
  const showFeedback = (feedback: UserFeedback) => {
    userFeedback.value = feedback

    // 自动清除反馈（除非是错误类型）
    if (feedback.type !== 'error') {
      const duration = feedback.duration || 3000
      setTimeout(() => {
        if (userFeedback.value === feedback) {
          clearFeedback()
        }
      }, duration)
    }
  }

  // 显示成功反馈
  const showSuccess = (message: string, duration?: number) => {
    showFeedback({ type: 'success', message, duration })
  }

  // 显示错误反馈
  const showError = (message: string) => {
    showFeedback({ type: 'error', message })
  }

  // 显示警告反馈
  const showWarning = (message: string, duration?: number) => {
    showFeedback({ type: 'warning', message, duration })
  }

  // 显示信息反馈
  const showInfo = (message: string, duration?: number) => {
    showFeedback({ type: 'info', message, duration })
  }

  // 加载供应商列表
  const loadProviders = async (params: ListProvidersParams = {}) => {
    clearError()

    try {
      await providerStore.fetchProviders(params)
      isInitialized.value = true
      retryCount.value = 0
    } catch (err) {
      console.error('加载供应商列表失败:', err)
      operationError.value = handleApiError(err)

      // 如果是初始加载失败，显示重试选项
      if (!isInitialized.value) {
        showError('加载供应商列表失败，请重试')
      }

      throw err
    }
  }

  // 重试加载
  const retryLoad = async () => {
    if (retryCount.value >= maxRetries) {
      showError('重试次数已达上限，请刷新页面')
      return
    }

    retryCount.value++
    showInfo(`正在重试加载... (${retryCount.value}/${maxRetries})`)

    try {
      await loadProviders()
      showSuccess('加载成功')
    } catch {
      if (retryCount.value >= maxRetries) {
        showError('重试失败，请检查网络连接后刷新页面')
      } else {
        showWarning('重试失败，请稍后再试')
      }
    }
  }

  // 刷新当前页面
  const refreshProviders = async () => {
    try {
      await providerStore.refreshProviders()
      showSuccess('刷新成功')
    } catch (err) {
      console.error('刷新供应商列表失败:', err)
      showError('刷新失败，请重试')
    }
  }

  // 分页处理
  const handlePageChange = async (page: number) => {
    if (page < 1 || page > totalPages.value) {
      return
    }

    const params: ListProvidersParams = {
      page,
      size: pagination.value.size,
    }

    try {
      await loadProviders(params)
    } catch {
      showError('切换页面失败，请重试')
    }
  }

  // 跳转到上一页
  const goToPreviousPage = () => {
    if (currentPage.value > 1) {
      handlePageChange(currentPage.value - 1)
    }
  }

  // 跳转到下一页
  const goToNextPage = () => {
    if (currentPage.value < totalPages.value) {
      handlePageChange(currentPage.value + 1)
    }
  }

  // 跳转到第一页
  const goToFirstPage = () => {
    if (currentPage.value !== 1) {
      handlePageChange(1)
    }
  }

  // 跳转到最后一页
  const goToLastPage = () => {
    if (currentPage.value !== totalPages.value) {
      handlePageChange(totalPages.value)
    }
  }

  // 打开创建对话框
  const openCreateDialog = () => {
    selectedProvider.value = null
    dialogMode.value = 'create'
    showFormDialog.value = true
    clearError()
  }

  // 打开编辑对话框
  const openEditDialog = (provider: Provider) => {
    selectedProvider.value = provider
    dialogMode.value = 'edit'
    showFormDialog.value = true
    clearError()
  }

  // 打开详情对话框
  const openDetailDialog = (provider: Provider) => {
    selectedProvider.value = provider
    dialogMode.value = 'view'
    showDetailDialog.value = true
    clearError()
  }

  // 打开删除确认对话框
  const openDeleteDialog = (provider: Provider) => {
    selectedProvider.value = provider
    dialogMode.value = 'delete'
    showDeleteDialog.value = true
    clearError()
  }

  // 关闭表单对话框
  const closeFormDialog = () => {
    showFormDialog.value = false
    selectedProvider.value = null
    dialogMode.value = 'create'
    clearError()

    // 延迟清除，确保动画完成
    setTimeout(() => {
      selectedProvider.value = null
    }, 300)
  }

  // 关闭详情对话框
  const closeDetailDialog = () => {
    showDetailDialog.value = false
    selectedProvider.value = null
    clearError()

    setTimeout(() => {
      selectedProvider.value = null
    }, 300)
  }

  // 关闭删除确认对话框
  const closeDeleteDialog = () => {
    showDeleteDialog.value = false
    selectedProvider.value = null
    dialogMode.value = 'create'
    clearError()

    setTimeout(() => {
      selectedProvider.value = null
    }, 300)
  }

  // 保存供应商（创建或更新）
  const handleSaveProvider = async (
    providerData: CreateProviderRequest | UpdateProviderRequest,
  ): Promise<OperationResult> => {
    if (!selectedProvider.value && dialogMode.value === 'edit') {
      const error = '未选择要编辑的供应商'
      showError(error)
      return { success: false, error }
    }

    operationLoading.value = true
    clearError()

    try {
      let result: Provider

      if (dialogMode.value === 'create') {
        result = await providerStore.createProvider(providerData as CreateProviderRequest)
        showSuccess(`供应商 "${result.display_name}" 创建成功`)
      } else {
        const providerId = selectedProvider.value!.provider_id
        result = await providerStore.updateProvider(
          providerId,
          providerData as UpdateProviderRequest,
        )
        showSuccess(`供应商 "${result.display_name}" 更新成功`)
      }

      closeFormDialog()

      // 如果是创建操作且当前不在第一页，跳转到第一页查看新创建的项目
      if (dialogMode.value === 'create' && currentPage.value !== 1) {
        await handlePageChange(1)
      }

      return { success: true, message: '操作成功' }
    } catch (err) {
      const errorMessage = handleApiError(err)
      operationError.value = errorMessage
      showError(errorMessage)
      console.error('保存供应商失败:', err)
      return { success: false, error: errorMessage }
    } finally {
      operationLoading.value = false
    }
  }

  // 删除供应商
  const handleDeleteProvider = async (): Promise<OperationResult> => {
    if (!selectedProvider.value) {
      const error = '未选择要删除的供应商'
      showError(error)
      return { success: false, error }
    }

    operationLoading.value = true
    clearError()

    const providerName = selectedProvider.value.display_name

    try {
      await providerStore.deleteProvider(selectedProvider.value.provider_id)
      showSuccess(`供应商 "${providerName}" 删除成功`)
      closeDeleteDialog()

      // 如果当前页没有数据了，跳转到上一页
      await nextTick()
      if (!hasProviders.value && currentPage.value > 1) {
        await handlePageChange(currentPage.value - 1)
      }

      return { success: true, message: '删除成功' }
    } catch (err) {
      const errorMessage = handleApiError(err)
      operationError.value = errorMessage
      showError(errorMessage)
      console.error('删除供应商失败:', err)
      return { success: false, error: errorMessage }
    } finally {
      operationLoading.value = false
    }
  }

  // 切换供应商状态
  const handleToggleStatus = async (provider: Provider): Promise<OperationResult> => {
    operationLoading.value = true
    clearError()

    const action = provider.is_active ? '停用' : '激活'
    const actionPast = provider.is_active ? '停用' : '激活'

    try {
      const result = await providerStore.toggleProviderStatus(provider.provider_id)
      showSuccess(`供应商 "${result.display_name}" ${actionPast}成功`)
      return { success: true, message: `${actionPast}成功` }
    } catch (err) {
      const errorMessage = handleApiError(err)
      operationError.value = errorMessage
      showError(`${action}供应商失败: ${errorMessage}`)
      console.error(`${action}供应商失败:`, err)
      return { success: false, error: errorMessage }
    } finally {
      operationLoading.value = false
    }
  }

  // 批量操作供应商
  const handleBatchOperation = async (
    providerIds: number[],
    action: 'activate' | 'deactivate' | 'delete',
  ): Promise<OperationResult> => {
    if (providerIds.length === 0) {
      const error = '请选择要操作的供应商'
      showWarning(error)
      return { success: false, error }
    }

    operationLoading.value = true
    clearError()

    const actionMap = {
      activate: '激活',
      deactivate: '停用',
      delete: '删除',
    }
    const actionText = actionMap[action]

    try {
      await providerStore.batchUpdateProviders(providerIds, action)
      showSuccess(`批量${actionText}成功，共处理 ${providerIds.length} 个供应商`)

      // 如果是删除操作，可能需要调整页面
      if (action === 'delete') {
        await nextTick()
        if (!hasProviders.value && currentPage.value > 1) {
          await handlePageChange(currentPage.value - 1)
        }
      }

      return { success: true, message: `批量${actionText}成功` }
    } catch (err) {
      const errorMessage = handleApiError(err)
      operationError.value = errorMessage
      showError(`批量${actionText}失败: ${errorMessage}`)
      console.error(`批量${actionText}失败:`, err)
      return { success: false, error: errorMessage }
    } finally {
      operationLoading.value = false
    }
  }

  // 测试供应商连接
  const testProviderConnection = async (provider: Provider): Promise<OperationResult> => {
    operationLoading.value = true
    clearError()

    try {
      await providerStore.testProvider(provider.provider_id)
      showSuccess(`供应商 "${provider.display_name}" 连接测试成功`)
      return { success: true, message: '连接测试成功' }
    } catch (err) {
      const errorMessage = handleApiError(err)
      operationError.value = errorMessage
      showError(`连接测试失败: ${errorMessage}`)
      console.error('测试供应商连接失败:', err)
      return { success: false, error: errorMessage }
    } finally {
      operationLoading.value = false
    }
  }

  // 从详情对话框快速编辑
  const editFromDetail = (provider: Provider) => {
    closeDetailDialog()
    setTimeout(() => {
      openEditDialog(provider)
    }, 100)
  }

  // 从详情对话框快速删除
  const deleteFromDetail = (provider: Provider) => {
    closeDetailDialog()
    setTimeout(() => {
      openDeleteDialog(provider)
    }, 100)
  }

  // 从详情对话框快速切换状态
  const toggleStatusFromDetail = async (provider: Provider) => {
    const result = await handleToggleStatus(provider)
    if (result.success) {
      // 更新详情对话框中的供应商信息
      const updatedProvider = providerStore.findProviderById(provider.provider_id)
      if (updatedProvider) {
        selectedProvider.value = updatedProvider
      }
    }
    return result
  }

  // 键盘快捷键处理
  const handleKeyboardShortcut = (event: KeyboardEvent) => {
    // Ctrl/Cmd + N: 创建新供应商
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
      event.preventDefault()
      openCreateDialog()
    }

    // ESC: 关闭对话框
    if (event.key === 'Escape') {
      if (showFormDialog.value) {
        closeFormDialog()
      } else if (showDetailDialog.value) {
        closeDetailDialog()
      } else if (showDeleteDialog.value) {
        closeDeleteDialog()
      }
    }

    // F5: 刷新列表
    if (event.key === 'F5') {
      event.preventDefault()
      refreshProviders()
    }
  }

  // 监听错误状态变化
  watch(error, (newError) => {
    if (newError) {
      showError(newError)
    }
  })

  // 监听操作错误状态变化
  watch(operationError, (newError) => {
    if (newError) {
      showError(newError)
    }
  })

  // 初始化
  onMounted(async () => {
    // 添加键盘事件监听
    document.addEventListener('keydown', handleKeyboardShortcut)

    // 初始化搜索历史
    providerStore.initializeSearchHistory()

    // 加载初始数据
    try {
      await loadProviders()
    } catch {
      // 初始加载失败已在loadProviders中处理
    }
  })

  // 清理
  const cleanup = () => {
    document.removeEventListener('keydown', handleKeyboardShortcut)
    clearFeedback()
    clearError()
  }

  return {
    // 状态
    providers,
    loading,
    error: currentError,
    pagination,
    operationLoading,
    operationError,
    userFeedback,
    isInitialized,
    retryCount,

    // 对话框状态
    showFormDialog,
    showDetailDialog,
    showDeleteDialog,
    selectedProvider,
    dialogMode,

    // 计算属性
    isEditMode,
    isCreateMode,
    isViewMode,
    isDeleteMode,
    hasError,
    canLoadMore,
    isEmpty,
    totalPages,
    currentPage,
    totalProviders,
    hasProviders,

    // 基础方法
    loadProviders,
    retryLoad,
    refreshProviders,
    clearError,
    clearFeedback,

    // 用户反馈方法
    showFeedback,
    showSuccess,
    showError,
    showWarning,
    showInfo,

    // 分页方法
    handlePageChange,
    goToPreviousPage,
    goToNextPage,
    goToFirstPage,
    goToLastPage,

    // 对话框方法
    openCreateDialog,
    openEditDialog,
    openDetailDialog,
    openDeleteDialog,
    closeFormDialog,
    closeDetailDialog,
    closeDeleteDialog,

    // 供应商操作方法
    handleSaveProvider,
    handleDeleteProvider,
    handleToggleStatus,
    handleBatchOperation,
    testProviderConnection,

    // 快捷操作方法
    editFromDetail,
    deleteFromDetail,
    toggleStatusFromDetail,

    // 清理方法
    cleanup,
  }
}
