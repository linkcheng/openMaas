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

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { providerApi } from '@/api'
import { handleApiError } from '@/utils/apiClient'
import { createListState } from './baseStore'
import type {
  Provider,
  CreateProviderRequest,
  UpdateProviderRequest,
  ListProvidersParams,
  SearchProvidersParams,
} from '@/types/providerTypes'

export const useProviderStore = defineStore('provider', () => {
  // 使用通用列表状态管理
  const {
    items: providers,
    selectedItems: selectedProviders,
    loading,
    error,
    lastUpdated,
    pagination,
    isEmpty,
    hasSelection,
    setItems,
    addItem,
    removeItem,
    updateItem,
    clearItems,
    selectItem,
    unselectItem,
    toggleSelection,
    clearSelection,
    selectAll,
    setLoading,
    setError,
    clearError,
    setPagination,
    resetPagination,
  } = createListState<Provider>()

  // 搜索状态（简化）
  const searchKeyword = ref('')
  const activeFilters = ref<Record<string, any>>({})

  // 计算属性
  const activeProviders = computed(() => providers.value.filter((p) => p.is_active))
  const inactiveProviders = computed(() => providers.value.filter((p) => !p.is_active))
  const providersByType = computed(() => {
    const grouped: Record<string, Provider[]> = {}
    providers.value.forEach((provider) => {
      if (!grouped[provider.provider_type]) {
        grouped[provider.provider_type] = []
      }
      grouped[provider.provider_type].push(provider)
    })
    return grouped
  })

  // 获取供应商列表
  const fetchProviders = async (params: ListProvidersParams = {}) => {
    try {
      setLoading(true)
      clearError()

      const response = await providerApi.listProviders(params)

      if (response.data.success && response.data.data) {
        setItems(response.data.data.items)
        setPagination(
          response.data.data.page,
          response.data.data.size,
          response.data.data.total
        )
      } else {
        throw new Error(response.data.message || '获取供应商列表失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 创建供应商
  const createProvider = async (data: CreateProviderRequest): Promise<Provider> => {
    try {
      setLoading(true)
      clearError()

      const response = await providerApi.createProvider(data)

      if (response.data.success && response.data.data) {
        const newProvider = response.data.data
        addItem(newProvider)
        return newProvider
      } else {
        throw new Error(response.data.message || '创建供应商失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 更新供应商
  const updateProvider = async (
    providerId: number,
    data: UpdateProviderRequest,
  ): Promise<Provider> => {
    try {
      setLoading(true)
      clearError()

      const response = await providerApi.updateProvider(providerId, data)

      if (response.data.success && response.data.data) {
        const updatedProvider = response.data.data
        updateItem((p) => p.provider_id === providerId, updatedProvider)
        return updatedProvider
      } else {
        throw new Error(response.data.message || '更新供应商失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 删除供应商
  const deleteProvider = async (providerId: number): Promise<void> => {
    try {
      setLoading(true)
      clearError()

      const response = await providerApi.deleteProvider(providerId)

      if (response.data.success) {
        removeItem((p) => p.provider_id === providerId)
      } else {
        throw new Error(response.data.message || '删除供应商失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 激活供应商
  const activateProvider = async (providerId: number): Promise<Provider> => {
    try {
      clearError()
      const response = await providerApi.activateProvider(providerId)

      if (response.data.success && response.data.data) {
        const updatedProvider = response.data.data
        updateItem((p) => p.provider_id === providerId, { is_active: true })
        return updatedProvider
      } else {
        throw new Error(response.data.message || '激活供应商失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    }
  }

  // 停用供应商
  const deactivateProvider = async (providerId: number): Promise<Provider> => {
    try {
      clearError()
      const response = await providerApi.deactivateProvider(providerId)

      if (response.data.success && response.data.data) {
        const updatedProvider = response.data.data
        updateItem((p) => p.provider_id === providerId, { is_active: false })
        return updatedProvider
      } else {
        throw new Error(response.data.message || '停用供应商失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    }
  }

  // 切换供应商状态
  const toggleProviderStatus = async (providerId: number): Promise<Provider> => {
    const provider = providers.value.find((p) => p.provider_id === providerId)
    if (!provider) {
      throw new Error('供应商不存在')
    }

    return provider.is_active 
      ? await deactivateProvider(providerId)
      : await activateProvider(providerId)
  }

  // 搜索供应商
  const searchProviders = async (params: SearchProvidersParams): Promise<void> => {
    try {
      setLoading(true)
      clearError()

      const response = await providerApi.searchProviders(params)

      if (response.data.success && response.data.data) {
        setItems(response.data.data.items)
        setPagination(
          response.data.data.page,
          response.data.data.size,
          response.data.data.total
        )
        searchKeyword.value = params.keyword || ''
      } else {
        throw new Error(response.data.message || '搜索供应商失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 测试供应商连接
  const testProvider = async (providerId: number): Promise<void> => {
    try {
      clearError()
      const response = await providerApi.testProvider(providerId)

      if (!response.data.success) {
        throw new Error(response.data.message || '测试供应商连接失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    }
  }

  // 批量操作供应商
  const batchUpdateProviders = async (
    providerIds: number[],
    action: 'activate' | 'deactivate' | 'delete',
  ): Promise<void> => {
    try {
      setLoading(true)
      clearError()

      const response = await providerApi.batchUpdateProviders({
        provider_ids: providerIds,
        action,
      })

      if (response.data.success) {
        // 根据操作类型更新本地状态
        switch (action) {
          case 'activate':
            providerIds.forEach((id) => {
              updateItem((p) => p.provider_id === id, { is_active: true })
            })
            break
          case 'deactivate':
            providerIds.forEach((id) => {
              updateItem((p) => p.provider_id === id, { is_active: false })
            })
            break
          case 'delete':
            providerIds.forEach((id) => {
              removeItem((p) => p.provider_id === id)
            })
            break
        }
      } else {
        throw new Error(response.data.message || '批量操作失败')
      }
    } catch (err) {
      setError(handleApiError(err))
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 查找供应商
  const findProviderById = (providerId: number): Provider | undefined => {
    return providers.value.find((provider) => provider.provider_id === providerId)
  }

  const findProviderByName = (providerName: string): Provider | undefined => {
    return providers.value.find((provider) => provider.provider_name === providerName)
  }

  // 重置状态
  const resetState = () => {
    clearItems()
    searchKeyword.value = ''
    activeFilters.value = {}
  }

  // 刷新列表
  const refreshProviders = async () => {
    const currentParams: ListProvidersParams = {
      page: pagination.value.page,
      size: pagination.value.size,
    }
    await fetchProviders(currentParams)
  }

  return {
    // 状态
    providers,
    selectedProviders,
    loading,
    error,
    lastUpdated,
    pagination,
    isEmpty,
    hasSelection,
    searchKeyword,
    activeFilters,

    // 计算属性
    activeProviders,
    inactiveProviders,
    providersByType,

    // 列表操作
    selectItem,
    unselectItem,
    toggleSelection,
    clearSelection,
    selectAll,

    // API 操作
    fetchProviders,
    createProvider,
    updateProvider,
    deleteProvider,
    activateProvider,
    deactivateProvider,
    toggleProviderStatus,
    searchProviders,
    testProvider,
    batchUpdateProviders,

    // 查找方法
    findProviderById,
    findProviderByName,

    // 状态管理
    resetState,
    refreshProviders,
    clearError,
  }
})