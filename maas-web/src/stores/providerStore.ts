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
import { apiClient, handleApiError } from '@/utils/api'
import { apiCache, performanceMonitor, debounce } from '@/utils/performance'
import type {
  Provider,
  CreateProviderRequest,
  UpdateProviderRequest,
  ListProvidersParams,
  SearchProvidersParams,
  PaginationInfo,
  PaginatedResponse,
} from '@/types/providerTypes'

export const useProviderStore = defineStore('provider', () => {
  // 状态
  const providers = ref<Provider[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref<PaginationInfo>({
    page: 1,
    size: 20,
    total: 0,
    pages: 0,
  })

  // 搜索和筛选状态
  const searchCache = ref<Map<string, PaginatedResponse<Provider>>>(new Map())
  const lastSearchParams = ref<string>('')
  const searchHistory = ref<string[]>([])
  const searchSuggestions = ref<string[]>([])
  const isSearching = ref(false)

  // 计算属性
  const totalPages = computed(() => pagination.value.pages)
  const currentPage = computed(() => pagination.value.page)
  const totalProviders = computed(() => pagination.value.total)
  const hasProviders = computed(() => providers.value.length > 0)
  const isFirstPage = computed(() => pagination.value.page === 1)
  const isLastPage = computed(() => pagination.value.page >= pagination.value.pages)

  // 按类型分组的供应商
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

  // 激活的供应商
  const activeProviders = computed(() => providers.value.filter((provider) => provider.is_active))

  // 停用的供应商
  const inactiveProviders = computed(() =>
    providers.value.filter((provider) => !provider.is_active),
  )

  // 获取供应商列表（带缓存）
  const fetchProviders = async (params: ListProvidersParams = {}) => {
    loading.value = true
    error.value = null

    // 生成缓存键
    const cacheKey = `providers:${JSON.stringify(params)}`

    // 检查缓存
    const cachedData = apiCache.get(cacheKey)
    if (cachedData) {
      providers.value = cachedData.items
      pagination.value = cachedData.pagination
      loading.value = false
      return
    }

    try {
      const response = await performanceMonitor.measureAsync('fetchProviders', async () => {
        return await apiClient.providers.listProviders(params)
      })

      if (response.data.success && response.data.data) {
        const data = {
          items: response.data.data.items,
          pagination: {
            page: response.data.data.page,
            size: response.data.data.size,
            total: response.data.data.total,
            pages: Math.ceil(response.data.data.total / response.data.data.size),
          },
        }

        providers.value = data.items
        pagination.value = data.pagination

        // 缓存数据（5分钟）
        apiCache.set(cacheKey, data, 5 * 60 * 1000)
      } else {
        throw new Error(response.data.message || '获取供应商列表失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('获取供应商列表失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 重试机制
  const retryFetchProviders = async (params: ListProvidersParams = {}, maxRetries = 3) => {
    let retryCount = 0

    while (retryCount < maxRetries) {
      try {
        await fetchProviders(params)
        return // 成功则退出
      } catch (err) {
        retryCount++
        if (retryCount >= maxRetries) {
          throw err // 达到最大重试次数，抛出错误
        }

        // 等待一段时间后重试，使用指数退避
        const delay = Math.pow(2, retryCount) * 1000
        await new Promise((resolve) => setTimeout(resolve, delay))
        console.log(`重试获取供应商列表，第 ${retryCount} 次`)
      }
    }
  }

  // 刷新当前页面数据
  const refreshProviders = async () => {
    const currentParams: ListProvidersParams = {
      page: pagination.value.page,
      size: pagination.value.size,
    }
    await fetchProviders(currentParams)
  }

  // 清除错误状态
  const clearError = () => {
    error.value = null
  }

  // 重置状态
  const resetState = () => {
    providers.value = []
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      size: 20,
      total: 0,
      pages: 0,
    }
    searchCache.value.clear()
    lastSearchParams.value = ''
    searchSuggestions.value = []
    isSearching.value = false
  }

  // 根据ID查找供应商
  const findProviderById = (providerId: number): Provider | undefined => {
    return providers.value.find((provider) => provider.provider_id === providerId)
  }

  // 根据名称查找供应商
  const findProviderByName = (providerName: string): Provider | undefined => {
    return providers.value.find((provider) => provider.provider_name === providerName)
  }

  // 创建供应商
  const createProvider = async (data: CreateProviderRequest): Promise<Provider> => {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.providers.createProvider(data)

      if (response.data.success && response.data.data) {
        const newProvider = response.data.data

        // 乐观更新：将新供应商添加到列表开头
        providers.value.unshift(newProvider)

        // 更新分页信息
        pagination.value.total += 1
        pagination.value.pages = Math.ceil(pagination.value.total / pagination.value.size)

        // 如果当前页已满，移除最后一个项目
        if (providers.value.length > pagination.value.size) {
          providers.value.pop()
        }

        // 清除搜索缓存
        searchCache.value.clear()

        return newProvider
      } else {
        throw new Error(response.data.message || '创建供应商失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('创建供应商失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新供应商
  const updateProvider = async (
    providerId: number,
    data: UpdateProviderRequest,
  ): Promise<Provider> => {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.providers.updateProvider(providerId, data)

      if (response.data.success && response.data.data) {
        const updatedProvider = response.data.data

        // 乐观更新：在本地状态中更新供应商
        const index = providers.value.findIndex((p) => p.provider_id === providerId)
        if (index !== -1) {
          providers.value[index] = updatedProvider
        }

        // 清除搜索缓存
        searchCache.value.clear()

        return updatedProvider
      } else {
        throw new Error(response.data.message || '更新供应商失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('更新供应商失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除供应商
  const deleteProvider = async (providerId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.providers.deleteProvider(providerId)

      if (response.data.success) {
        // 乐观更新：从本地状态中移除供应商
        const index = providers.value.findIndex((p) => p.provider_id === providerId)
        if (index !== -1) {
          providers.value.splice(index, 1)

          // 更新分页信息
          pagination.value.total -= 1
          pagination.value.pages = Math.ceil(pagination.value.total / pagination.value.size)

          // 如果当前页没有数据且不是第一页，跳转到上一页
          if (providers.value.length === 0 && pagination.value.page > 1) {
            pagination.value.page -= 1
          }
        }

        // 清除搜索缓存
        searchCache.value.clear()
      } else {
        throw new Error(response.data.message || '删除供应商失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('删除供应商失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 激活供应商
  const activateProvider = async (providerId: number): Promise<Provider> => {
    error.value = null

    try {
      const response = await apiClient.providers.activateProvider(providerId)

      if (response.data.success && response.data.data) {
        const updatedProvider = response.data.data

        // 乐观更新：更新本地状态中的供应商状态
        const provider = providers.value.find((p) => p.provider_id === providerId)
        if (provider) {
          provider.is_active = true
          provider.updated_at = updatedProvider.updated_at
        }

        // 清除搜索缓存
        searchCache.value.clear()

        return updatedProvider
      } else {
        throw new Error(response.data.message || '激活供应商失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('激活供应商失败:', err)

      // 回滚乐观更新
      const provider = providers.value.find((p) => p.provider_id === providerId)
      if (provider) {
        provider.is_active = false
      }

      throw err
    }
  }

  // 停用供应商
  const deactivateProvider = async (providerId: number): Promise<Provider> => {
    error.value = null

    try {
      const response = await apiClient.providers.deactivateProvider(providerId)

      if (response.data.success && response.data.data) {
        const updatedProvider = response.data.data

        // 乐观更新：更新本地状态中的供应商状态
        const provider = providers.value.find((p) => p.provider_id === providerId)
        if (provider) {
          provider.is_active = false
          provider.updated_at = updatedProvider.updated_at
        }

        // 清除搜索缓存
        searchCache.value.clear()

        return updatedProvider
      } else {
        throw new Error(response.data.message || '停用供应商失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('停用供应商失败:', err)

      // 回滚乐观更新
      const provider = providers.value.find((p) => p.provider_id === providerId)
      if (provider) {
        provider.is_active = true
      }

      throw err
    }
  }

  // 切换供应商状态
  const toggleProviderStatus = async (providerId: number): Promise<Provider> => {
    const provider = findProviderById(providerId)
    if (!provider) {
      throw new Error('供应商不存在')
    }

    if (provider.is_active) {
      return await deactivateProvider(providerId)
    } else {
      return await activateProvider(providerId)
    }
  }

  // 批量操作供应商
  const batchUpdateProviders = async (
    providerIds: number[],
    action: 'activate' | 'deactivate' | 'delete',
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.providers.batchUpdateProviders({
        provider_ids: providerIds,
        action,
      })

      if (response.data.success) {
        // 根据操作类型更新本地状态
        switch (action) {
          case 'activate':
            providerIds.forEach((id) => {
              const provider = providers.value.find((p) => p.provider_id === id)
              if (provider) {
                provider.is_active = true
              }
            })
            break
          case 'deactivate':
            providerIds.forEach((id) => {
              const provider = providers.value.find((p) => p.provider_id === id)
              if (provider) {
                provider.is_active = false
              }
            })
            break
          case 'delete':
            providers.value = providers.value.filter((p) => !providerIds.includes(p.provider_id))
            pagination.value.total -= providerIds.length
            pagination.value.pages = Math.ceil(pagination.value.total / pagination.value.size)
            break
        }

        // 清除搜索缓存
        searchCache.value.clear()
      } else {
        throw new Error(response.data.message || '批量操作失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('批量操作供应商失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 搜索供应商
  const searchProviders = async (params: SearchProvidersParams): Promise<void> => {
    isSearching.value = true
    error.value = null

    // 生成缓存键
    const cacheKey = JSON.stringify(params)

    // 检查缓存
    if (searchCache.value.has(cacheKey)) {
      const cachedResult = searchCache.value.get(cacheKey)!
      providers.value = cachedResult.items
      pagination.value = {
        page: cachedResult.page,
        size: cachedResult.size,
        total: cachedResult.total,
        pages: Math.ceil(cachedResult.total / cachedResult.size),
      }
      lastSearchParams.value = cacheKey
      isSearching.value = false
      return
    }

    try {
      const response = await apiClient.providers.searchProviders(params)

      if (response.data.success && response.data.data) {
        const searchResult = response.data.data

        // 更新状态
        providers.value = searchResult.items
        pagination.value = {
          page: searchResult.page,
          size: searchResult.size,
          total: searchResult.total,
          pages: Math.ceil(searchResult.total / searchResult.size),
        }

        // 缓存搜索结果
        searchCache.value.set(cacheKey, searchResult)
        lastSearchParams.value = cacheKey

        // 添加到搜索历史
        if (params.keyword && params.keyword.trim()) {
          addToSearchHistory(params.keyword.trim())
        }
      } else {
        throw new Error(response.data.message || '搜索供应商失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('搜索供应商失败:', err)
      throw err
    } finally {
      isSearching.value = false
    }
  }

  // 添加到搜索历史
  const addToSearchHistory = (keyword: string) => {
    // 移除重复项
    const index = searchHistory.value.indexOf(keyword)
    if (index > -1) {
      searchHistory.value.splice(index, 1)
    }

    // 添加到开头
    searchHistory.value.unshift(keyword)

    // 限制历史记录数量
    if (searchHistory.value.length > 10) {
      searchHistory.value = searchHistory.value.slice(0, 10)
    }

    // 持久化到localStorage
    try {
      localStorage.setItem('provider_search_history', JSON.stringify(searchHistory.value))
    } catch (error) {
      console.warn('无法保存搜索历史:', error)
    }
  }

  // 清除搜索历史
  const clearSearchHistory = () => {
    searchHistory.value = []
    try {
      localStorage.removeItem('provider_search_history')
    } catch (error) {
      console.warn('无法清除搜索历史:', error)
    }
  }

  // 从搜索历史中移除项目
  const removeFromSearchHistory = (keyword: string) => {
    const index = searchHistory.value.indexOf(keyword)
    if (index > -1) {
      searchHistory.value.splice(index, 1)
      try {
        localStorage.setItem('provider_search_history', JSON.stringify(searchHistory.value))
      } catch (error) {
        console.warn('无法更新搜索历史:', error)
      }
    }
  }

  // 生成搜索建议
  const generateSearchSuggestions = (keyword: string) => {
    if (!keyword || keyword.length < 2) {
      searchSuggestions.value = []
      return
    }

    const suggestions = new Set<string>()

    // 从搜索历史中匹配
    searchHistory.value.forEach((historyItem) => {
      if (historyItem.toLowerCase().includes(keyword.toLowerCase())) {
        suggestions.add(historyItem)
      }
    })

    // 从当前供应商列表中匹配
    providers.value.forEach((provider) => {
      if (provider.display_name.toLowerCase().includes(keyword.toLowerCase())) {
        suggestions.add(provider.display_name)
      }
      if (provider.provider_name.toLowerCase().includes(keyword.toLowerCase())) {
        suggestions.add(provider.provider_name)
      }
    })

    searchSuggestions.value = Array.from(suggestions).slice(0, 5)
  }

  // 按类型筛选供应商
  const filterByType = (providerType: string) => {
    const params: SearchProvidersParams = {
      provider_type: providerType,
      page: 1,
      size: pagination.value.size,
    }
    return searchProviders(params)
  }

  // 按状态筛选供应商
  const filterByStatus = (isActive: boolean) => {
    const params: SearchProvidersParams = {
      is_active: isActive,
      page: 1,
      size: pagination.value.size,
    }
    return searchProviders(params)
  }

  // 组合筛选
  const filterProviders = (filters: {
    keyword?: string
    providerType?: string
    isActive?: boolean
    page?: number
    size?: number
  }) => {
    const params: SearchProvidersParams = {
      keyword: filters.keyword,
      provider_type: filters.providerType,
      is_active: filters.isActive,
      page: filters.page || 1,
      size: filters.size || pagination.value.size,
    }
    return searchProviders(params)
  }

  // 清除搜索和筛选
  const clearSearchAndFilters = () => {
    searchCache.value.clear()
    lastSearchParams.value = ''
    searchSuggestions.value = []
    isSearching.value = false

    // 重新加载默认列表
    return fetchProviders({ page: 1, size: pagination.value.size })
  }

  // 初始化搜索历史
  const initializeSearchHistory = () => {
    try {
      const saved = localStorage.getItem('provider_search_history')
      if (saved) {
        searchHistory.value = JSON.parse(saved)
      }
    } catch (error) {
      console.warn('无法加载搜索历史:', error)
      searchHistory.value = []
    }
  }

  // 测试供应商连接
  const testProvider = async (providerId: number): Promise<void> => {
    error.value = null

    try {
      const response = await apiClient.providers.testProvider(providerId)

      if (!response.data.success) {
        throw new Error(response.data.message || '测试供应商连接失败')
      }
    } catch (err) {
      error.value = handleApiError(err)
      console.error('测试供应商连接失败:', err)
      throw err
    }
  }

  // 清除搜索缓存
  const clearSearchCache = () => {
    searchCache.value.clear()
  }

  // 获取供应商关联的模型配置
  const getRelatedModels = async (
    providerId: number,
  ): Promise<Array<{ id: number; name: string; is_active: boolean }>> => {
    try {
      const response = await apiClient.providers.getRelatedModels(providerId)

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        return []
      }
    } catch (err) {
      console.error('获取关联模型失败:', err)
      return []
    }
  }

  // 获取供应商使用情况
  const getProviderUsage = async (
    providerId: number,
  ): Promise<{
    activeConnections: number
    recentRequests: number
    lastUsed?: string
  }> => {
    try {
      const response = await apiClient.providers.getProviderUsage(providerId)

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        return {
          activeConnections: 0,
          recentRequests: 0,
        }
      }
    } catch (err) {
      console.error('获取供应商使用情况失败:', err)
      return {
        activeConnections: 0,
        recentRequests: 0,
      }
    }
  }

  // 清除所有缓存
  const clearAllCache = () => {
    // 清除API缓存中的供应商相关数据
    const keys = ['providers:', 'provider:', 'search:']
    keys.forEach((_keyPrefix) => {
      // 这里需要遍历所有缓存键，删除匹配的
      // 由于apiCache没有提供遍历方法，我们可以在需要时清除整个缓存
    })
    searchCache.value.clear()
  }

  // 清除特定供应商的缓存
  const clearProviderCache = (providerId?: number) => {
    if (providerId) {
      apiCache.delete(`provider:${providerId}`)
    }
    // 清除列表缓存
    apiCache.clear() // 简单粗暴的方式，清除所有缓存
    searchCache.value.clear()
  }

  // 预加载下一页数据
  const preloadNextPage = debounce(async () => {
    if (currentPage.value < totalPages.value) {
      const nextPageParams = {
        ...lastSearchParams.value,
        page: currentPage.value + 1,
      }

      try {
        // 静默预加载，不更新UI状态
        await apiClient.providers.listProviders(nextPageParams)
      } catch (err) {
        // 预加载失败不影响用户体验
        console.debug('预加载下一页失败:', err)
      }
    }
  }, 1000)

  return {
    // 状态
    providers,
    loading,
    error,
    pagination,
    searchCache,
    lastSearchParams,
    searchHistory,
    searchSuggestions,
    isSearching,

    // 计算属性
    totalPages,
    currentPage,
    totalProviders,
    hasProviders,
    isFirstPage,
    isLastPage,
    providersByType,
    activeProviders,
    inactiveProviders,

    // 基础方法
    fetchProviders,
    retryFetchProviders,
    refreshProviders,
    clearError,
    resetState,
    findProviderById,
    findProviderByName,

    // CRUD方法
    createProvider,
    updateProvider,
    deleteProvider,
    activateProvider,
    deactivateProvider,
    toggleProviderStatus,
    batchUpdateProviders,
    testProvider,

    // 搜索和筛选方法
    searchProviders,
    addToSearchHistory,
    clearSearchHistory,
    removeFromSearchHistory,

    // 缓存管理方法
    clearAllCache,
    clearProviderCache,
    preloadNextPage,
    generateSearchSuggestions,
    filterByType,
    filterByStatus,
    filterProviders,
    clearSearchAndFilters,
    initializeSearchHistory,
    clearSearchCache,

    // 删除相关方法
    getRelatedModels,
    getProviderUsage,
  }
})
