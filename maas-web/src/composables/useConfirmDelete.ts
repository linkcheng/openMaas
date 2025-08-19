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

import { ref, computed, watch } from 'vue'
import { useProviderStore } from '@/stores/providerStore'
import { handleApiError } from '@/utils/api'
import type { Provider } from '@/types/providerTypes'

// 删除操作结果类型
export interface DeleteResult {
  success: boolean
  message?: string
  error?: string
}

// 删除状态类型
export interface DeleteState {
  loading: boolean
  error: string | null
  retryCount: number
  canRetry: boolean
}

export function useConfirmDelete() {
  const providerStore = useProviderStore()

  // 删除状态
  const deleteState = ref<DeleteState>({
    loading: false,
    error: null,
    retryCount: 0,
    canRetry: true,
  })

  // 最大重试次数
  const maxRetries = 3

  // 计算属性
  const isDeleting = computed(() => deleteState.value.loading)
  const deleteError = computed(() => deleteState.value.error)
  const canRetryDelete = computed(
    () =>
      deleteState.value.canRetry &&
      deleteState.value.retryCount < maxRetries &&
      !deleteState.value.loading,
  )

  // 清除删除错误
  const clearDeleteError = () => {
    deleteState.value.error = null
  }

  // 重置删除状态
  const resetDeleteState = () => {
    deleteState.value = {
      loading: false,
      error: null,
      retryCount: 0,
      canRetry: true,
    }
  }

  // 执行删除操作
  const executeDelete = async (provider: Provider): Promise<DeleteResult> => {
    if (!provider) {
      const error = '未指定要删除的供应商'
      deleteState.value.error = error
      return { success: false, error }
    }

    deleteState.value.loading = true
    deleteState.value.error = null

    const providerName = provider.display_name
    const providerId = provider.provider_id

    try {
      // 调用删除API
      await providerStore.deleteProvider(providerId)

      // 删除成功
      resetDeleteState()
      return {
        success: true,
        message: `供应商 "${providerName}" 删除成功`,
      }
    } catch (err) {
      // 删除失败
      const errorMessage = handleApiError(err)
      deleteState.value.error = errorMessage
      deleteState.value.retryCount++

      // 检查是否可以重试
      if (deleteState.value.retryCount >= maxRetries) {
        deleteState.value.canRetry = false
      }

      console.error('删除供应商失败:', err)
      return {
        success: false,
        error: errorMessage,
      }
    } finally {
      deleteState.value.loading = false
    }
  }

  // 重试删除操作
  const retryDelete = async (provider: Provider): Promise<DeleteResult> => {
    if (!canRetryDelete.value) {
      const error = '无法重试删除操作'
      return { success: false, error }
    }

    // 清除之前的错误状态
    clearDeleteError()

    // 执行删除
    return await executeDelete(provider)
  }

  // 检查删除前置条件
  const checkDeletePreconditions = async (
    provider: Provider,
  ): Promise<{
    canDelete: boolean
    warnings: string[]
    blockers: string[]
  }> => {
    const warnings: string[] = []
    const blockers: string[] = []

    try {
      // 检查供应商是否有关联的模型配置
      const relatedModels = await providerStore.getRelatedModels(provider.provider_id)

      if (relatedModels.length > 0) {
        if (relatedModels.some((model) => model.is_active)) {
          // 有激活的模型配置，阻止删除
          blockers.push(
            `供应商关联了 ${relatedModels.filter((m) => m.is_active).length} 个激活的模型配置`,
          )
        } else {
          // 只有停用的模型配置，给出警告
          warnings.push(
            `供应商关联了 ${relatedModels.length} 个已停用的模型配置，删除后这些配置也将被移除`,
          )
        }
      }

      // 检查供应商是否正在被使用
      const usageInfo = await providerStore.getProviderUsage(provider.provider_id)

      if (usageInfo.activeConnections > 0) {
        blockers.push(`供应商当前有 ${usageInfo.activeConnections} 个活跃连接`)
      }

      if (usageInfo.recentRequests > 0) {
        warnings.push(`供应商在过去24小时内处理了 ${usageInfo.recentRequests} 个请求`)
      }

      // 检查供应商状态
      if (provider.is_active) {
        warnings.push('供应商当前处于激活状态，建议先停用后再删除')
      }

      return {
        canDelete: blockers.length === 0,
        warnings,
        blockers,
      }
    } catch (err) {
      console.error('检查删除前置条件失败:', err)
      // 如果检查失败，允许删除但给出警告
      return {
        canDelete: true,
        warnings: ['无法检查删除前置条件，请谨慎操作'],
        blockers: [],
      }
    }
  }

  // 获取删除影响范围
  const getDeleteImpact = async (
    provider: Provider,
  ): Promise<{
    affectedModels: number
    affectedConnections: number
    estimatedDowntime: string
    recoverySteps: string[]
  }> => {
    try {
      const [relatedModels, usageInfo] = await Promise.all([
        providerStore.getRelatedModels(provider.provider_id),
        providerStore.getProviderUsage(provider.provider_id),
      ])

      const recoverySteps: string[] = []

      if (relatedModels.length > 0) {
        recoverySteps.push('重新配置受影响的模型')
      }

      if (usageInfo.activeConnections > 0) {
        recoverySteps.push('等待活跃连接自然结束')
      }

      recoverySteps.push('验证其他供应商配置正常')

      return {
        affectedModels: relatedModels.length,
        affectedConnections: usageInfo.activeConnections,
        estimatedDowntime: usageInfo.activeConnections > 0 ? '立即生效' : '无影响',
        recoverySteps,
      }
    } catch (err) {
      console.error('获取删除影响范围失败:', err)
      return {
        affectedModels: 0,
        affectedConnections: 0,
        estimatedDowntime: '未知',
        recoverySteps: ['请手动检查相关配置'],
      }
    }
  }

  // 格式化错误消息
  const formatDeleteError = (error: string): string => {
    // 常见错误消息的友好化处理
    const errorMappings: Record<string, string> = {
      PROVIDER_HAS_ACTIVE_MODELS: '供应商关联了激活的模型配置，请先停用相关模型后再删除',
      PROVIDER_IN_USE: '供应商正在被使用中，请稍后再试',
      PROVIDER_NOT_FOUND: '供应商不存在或已被删除',
      INSUFFICIENT_PERMISSIONS: '权限不足，无法删除供应商',
      NETWORK_ERROR: '网络连接失败，请检查网络后重试',
      SERVER_ERROR: '服务器错误，请稍后重试',
    }

    // 尝试匹配已知错误类型
    for (const [key, message] of Object.entries(errorMappings)) {
      if (error.includes(key) || error.toLowerCase().includes(key.toLowerCase())) {
        return message
      }
    }

    // 如果是HTTP状态码错误
    if (error.includes('404')) {
      return '供应商不存在或已被删除'
    } else if (error.includes('403')) {
      return '权限不足，无法删除供应商'
    } else if (error.includes('409')) {
      return '供应商正在被使用，无法删除'
    } else if (error.includes('500')) {
      return '服务器内部错误，请稍后重试'
    }

    // 返回原始错误消息
    return error
  }

  // 生成删除确认消息
  const generateConfirmationMessage = (provider: Provider): string => {
    const baseMessage = `您即将删除供应商 "${provider.display_name}"`

    if (provider.is_active) {
      return `${baseMessage}。此供应商当前处于激活状态，删除后可能影响相关服务的正常运行。`
    }

    return `${baseMessage}。此操作无法撤销，请确认您要继续。`
  }

  // 监听删除状态变化
  watch(
    () => deleteState.value.error,
    (newError) => {
      if (newError) {
        // 格式化错误消息
        deleteState.value.error = formatDeleteError(newError)
      }
    },
  )

  return {
    // 状态
    deleteState: computed(() => deleteState.value),
    isDeleting,
    deleteError,
    canRetryDelete,

    // 方法
    executeDelete,
    retryDelete,
    clearDeleteError,
    resetDeleteState,
    checkDeletePreconditions,
    getDeleteImpact,
    formatDeleteError,
    generateConfirmationMessage,
  }
}
