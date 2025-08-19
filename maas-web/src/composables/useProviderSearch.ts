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

import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProviderStore } from '@/stores/providerStore'

import { debounce, throttle, getOptimalConfig } from '@/utils/performance'
import type { SearchProvidersParams, ProviderType, SortOption } from '@/types/providerTypes'
import {
  ProviderStatus,
  PROVIDER_TYPE_OPTIONS,
  STATUS_OPTIONS,
  SORT_OPTIONS,
} from '@/types/providerTypes'

// 搜索状态类型
export interface SearchState {
  keyword: string
  providerType: ProviderType | ''
  status: ProviderStatus | ''
  sortBy: string
  sortOrder: 'asc' | 'desc'
  page: number
  size: number
}

// 搜索历史项类型
export interface SearchHistoryItem {
  keyword: string
  timestamp: number
  resultCount?: number
}

// 搜索建议类型
export interface SearchSuggestion {
  text: string
  type: 'history' | 'provider' | 'keyword'
  count?: number
}

// URL同步选项
export interface UrlSyncOptions {
  enabled: boolean
  paramPrefix: string
  excludeParams: string[]
}

export function useProviderSearch(options: Partial<UrlSyncOptions> = {}) {
  const route = useRoute()
  const router = useRouter()
  const providerStore = useProviderStore()

  const { providers, loading, isSearching, searchHistory, searchSuggestions, pagination } =
    storeToRefs(providerStore)

  // URL同步配置
  const urlSyncOptions: UrlSyncOptions = {
    enabled: true,
    paramPrefix: '',
    excludeParams: ['page'],
    ...options,
  }

  // 搜索状态
  const searchState = ref<SearchState>({
    keyword: '',
    providerType: '',
    status: '',
    sortBy: 'created_at',
    sortOrder: 'desc',
    page: 1,
    size: 20,
  })

  // 搜索输入框的值（用于防抖）
  const searchInput = ref('')

  // 搜索建议状态
  const showSuggestions = ref(false)
  const activeSuggestionIndex = ref(-1)

  // 高级搜索状态
  const showAdvancedSearch = ref(false)

  // 搜索统计
  const searchStats = ref({
    totalSearches: 0,
    lastSearchTime: null as Date | null,
    averageResultCount: 0,
  })

  // 计算属性
  const hasActiveFilters = computed(() => {
    return !!(
      searchState.value.keyword ||
      searchState.value.providerType ||
      searchState.value.status ||
      searchState.value.sortBy !== 'created_at' ||
      searchState.value.sortOrder !== 'desc'
    )
  })

  const isDefaultSort = computed(() => {
    return searchState.value.sortBy === 'created_at' && searchState.value.sortOrder === 'desc'
  })

  const currentSortOption = computed(() => {
    return SORT_OPTIONS.find(
      (option) =>
        option.field === searchState.value.sortBy && option.order === searchState.value.sortOrder,
    )
  })

  const filteredSuggestions = computed((): SearchSuggestion[] => {
    if (!searchInput.value || searchInput.value.length < 2) {
      return []
    }

    const keyword = searchInput.value.toLowerCase()
    const suggestions: SearchSuggestion[] = []

    // 从搜索历史中匹配
    searchHistory.value.forEach((historyKeyword) => {
      if (
        historyKeyword.toLowerCase().includes(keyword) &&
        !suggestions.find((s) => s.text === historyKeyword)
      ) {
        suggestions.push({
          text: historyKeyword,
          type: 'history',
        })
      }
    })

    // 从当前供应商列表中匹配
    providers.value.forEach((provider) => {
      if (
        provider.display_name.toLowerCase().includes(keyword) &&
        !suggestions.find((s) => s.text === provider.display_name)
      ) {
        suggestions.push({
          text: provider.display_name,
          type: 'provider',
        })
      }

      if (
        provider.provider_name.toLowerCase().includes(keyword) &&
        !suggestions.find((s) => s.text === provider.provider_name)
      ) {
        suggestions.push({
          text: provider.provider_name,
          type: 'provider',
        })
      }
    })

    // 限制建议数量
    return suggestions.slice(0, 8)
  })

  const searchParams = computed((): SearchProvidersParams => {
    const params: SearchProvidersParams = {
      page: searchState.value.page,
      size: searchState.value.size,
    }

    if (searchState.value.keyword) {
      params.keyword = searchState.value.keyword
    }

    if (searchState.value.providerType) {
      params.provider_type = searchState.value.providerType
    }

    if (searchState.value.status) {
      params.is_active = searchState.value.status === ProviderStatus.ACTIVE
    }

    return params
  })

  // 获取优化配置
  const optimalConfig = getOptimalConfig()

  // 防抖搜索函数（根据设备性能调整延迟）
  const debouncedSearch = debounce(async () => {
    searchState.value.keyword = searchInput.value.trim()
    searchState.value.page = 1 // 重置到第一页
    await performSearch()
  }, optimalConfig.debounceDelay)

  // 节流的URL更新函数（根据设备性能调整延迟）
  const throttledUrlUpdate = throttle(() => {
    if (urlSyncOptions.enabled) {
      updateUrl()
    }
  }, optimalConfig.throttleDelay)

  // 执行搜索
  const performSearch = async () => {
    try {
      await providerStore.searchProviders(searchParams.value)

      // 更新搜索统计
      searchStats.value.totalSearches++
      searchStats.value.lastSearchTime = new Date()

      // 隐藏建议
      showSuggestions.value = false
      activeSuggestionIndex.value = -1

      // 更新URL
      throttledUrlUpdate()
    } catch (error) {
      console.error('搜索失败:', error)
    }
  }

  // 处理搜索输入
  const handleSearchInput = (value: string) => {
    searchInput.value = value

    // 生成搜索建议
    if (value.length >= 2) {
      providerStore.generateSearchSuggestions(value)
      showSuggestions.value = true
      activeSuggestionIndex.value = -1
    } else {
      showSuggestions.value = false
    }

    // 防抖搜索
    debouncedSearch()
  }

  // 处理搜索提交
  const handleSearchSubmit = async () => {
    searchState.value.keyword = searchInput.value.trim()
    searchState.value.page = 1
    showSuggestions.value = false
    await performSearch()
  }

  // 清除搜索
  const clearSearch = async () => {
    searchInput.value = ''
    searchState.value.keyword = ''
    searchState.value.page = 1
    showSuggestions.value = false
    await performSearch()
  }

  // 应用建议
  const applySuggestion = async (suggestion: SearchSuggestion) => {
    searchInput.value = suggestion.text
    searchState.value.keyword = suggestion.text
    searchState.value.page = 1
    showSuggestions.value = false
    await performSearch()
  }

  // 处理键盘导航
  const handleKeyboardNavigation = (event: KeyboardEvent) => {
    if (!showSuggestions.value || filteredSuggestions.value.length === 0) {
      return
    }

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        activeSuggestionIndex.value = Math.min(
          activeSuggestionIndex.value + 1,
          filteredSuggestions.value.length - 1,
        )
        break
      case 'ArrowUp':
        event.preventDefault()
        activeSuggestionIndex.value = Math.max(activeSuggestionIndex.value - 1, -1)
        break
      case 'Enter':
        event.preventDefault()
        if (activeSuggestionIndex.value >= 0) {
          applySuggestion(filteredSuggestions.value[activeSuggestionIndex.value])
        } else {
          handleSearchSubmit()
        }
        break
      case 'Escape':
        showSuggestions.value = false
        activeSuggestionIndex.value = -1
        break
    }
  }

  // 处理供应商类型筛选
  const handleProviderTypeFilter = async (providerType: ProviderType | '') => {
    searchState.value.providerType = providerType
    searchState.value.page = 1
    await performSearch()
  }

  // 处理状态筛选
  const handleStatusFilter = async (status: ProviderStatus | '') => {
    searchState.value.status = status
    searchState.value.page = 1
    await performSearch()
  }

  // 处理排序
  const handleSort = async (sortBy: string, sortOrder: 'asc' | 'desc') => {
    searchState.value.sortBy = sortBy
    searchState.value.sortOrder = sortOrder
    searchState.value.page = 1
    await performSearch()
  }

  // 应用排序选项
  const applySortOption = async (option: SortOption) => {
    await handleSort(option.field, option.order)
  }

  // 处理分页
  const handlePageChange = async (page: number) => {
    searchState.value.page = page
    await performSearch()
  }

  // 处理页面大小变化
  const handlePageSizeChange = async (size: number) => {
    searchState.value.size = size
    searchState.value.page = 1
    await performSearch()
  }

  // 重置所有筛选
  const resetFilters = async () => {
    searchInput.value = ''
    searchState.value = {
      keyword: '',
      providerType: '',
      status: '',
      sortBy: 'created_at',
      sortOrder: 'desc',
      page: 1,
      size: searchState.value.size, // 保持页面大小
    }
    showSuggestions.value = false
    showAdvancedSearch.value = false
    await performSearch()
  }

  // 切换高级搜索
  const toggleAdvancedSearch = () => {
    showAdvancedSearch.value = !showAdvancedSearch.value
  }

  // 从URL读取搜索参数
  const loadFromUrl = () => {
    if (!urlSyncOptions.enabled) return

    const query = route.query
    const prefix = urlSyncOptions.paramPrefix

    // 读取搜索关键词
    const keyword = query[`${prefix}keyword`] as string
    if (keyword) {
      searchInput.value = keyword
      searchState.value.keyword = keyword
    }

    // 读取供应商类型
    const providerType = query[`${prefix}type`] as ProviderType
    if (providerType && PROVIDER_TYPE_OPTIONS.find((opt) => opt.value === providerType)) {
      searchState.value.providerType = providerType
    }

    // 读取状态
    const status = query[`${prefix}status`] as ProviderStatus
    if (status && STATUS_OPTIONS.find((opt) => opt.value === status)) {
      searchState.value.status = status
    }

    // 读取排序
    const sortBy = query[`${prefix}sort`] as string
    const sortOrder = query[`${prefix}order`] as 'asc' | 'desc'
    if (sortBy && SORT_OPTIONS.find((opt) => opt.field === sortBy)) {
      searchState.value.sortBy = sortBy
    }
    if (sortOrder && ['asc', 'desc'].includes(sortOrder)) {
      searchState.value.sortOrder = sortOrder
    }

    // 读取页面
    const page = parseInt(query[`${prefix}page`] as string)
    if (page && page > 0) {
      searchState.value.page = page
    }

    // 读取页面大小
    const size = parseInt(query[`${prefix}size`] as string)
    if (size && size > 0 && size <= 100) {
      searchState.value.size = size
    }
  }

  // 更新URL
  const updateUrl = () => {
    if (!urlSyncOptions.enabled) return

    const query = { ...route.query } as Record<string, string>
    const prefix = urlSyncOptions.paramPrefix

    // 清除旧的搜索参数
    Object.keys(query).forEach((key) => {
      if (key.startsWith(prefix)) {
        delete query[key]
      }
    })

    // 添加新的搜索参数
    if (searchState.value.keyword) {
      query[`${prefix}keyword`] = searchState.value.keyword
    }

    if (searchState.value.providerType) {
      query[`${prefix}type`] = searchState.value.providerType
    }

    if (searchState.value.status) {
      query[`${prefix}status`] = searchState.value.status
    }

    if (!isDefaultSort.value) {
      query[`${prefix}sort`] = searchState.value.sortBy
      query[`${prefix}order`] = searchState.value.sortOrder
    }

    if (searchState.value.page > 1 && !urlSyncOptions.excludeParams.includes('page')) {
      query[`${prefix}page`] = searchState.value.page.toString()
    }

    if (searchState.value.size !== 20) {
      query[`${prefix}size`] = searchState.value.size.toString()
    }

    // 更新路由
    router.replace({ query }).catch(() => {
      // 忽略导航重复错误
    })
  }

  // 获取搜索历史
  const getSearchHistory = (): string[] => {
    return searchHistory.value.slice(0, 10) // 最多返回10条历史记录
  }

  // 清除搜索历史
  const clearSearchHistory = () => {
    providerStore.clearSearchHistory()
  }

  // 从搜索历史中移除项目
  const removeFromSearchHistory = (keyword: string) => {
    providerStore.removeFromSearchHistory(keyword)
  }

  // 导出搜索结果
  const exportSearchResults = () => {
    const results = providers.value.map((provider) => ({
      供应商名称: provider.provider_name,
      显示名称: provider.display_name,
      类型: provider.provider_type,
      状态: provider.is_active ? '激活' : '停用',
      基础URL: provider.base_url,
      描述: provider.description || '',
      创建时间: provider.created_at,
      更新时间: provider.updated_at,
    }))

    const csv = [
      Object.keys(results[0] || {}).join(','),
      ...results.map((row) => Object.values(row).join(',')),
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `providers_search_${Date.now()}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // 获取搜索摘要
  const getSearchSummary = () => {
    const total = pagination.value.total
    const filters = []

    if (searchState.value.keyword) {
      filters.push(`关键词: "${searchState.value.keyword}"`)
    }

    if (searchState.value.providerType) {
      const typeOption = PROVIDER_TYPE_OPTIONS.find(
        (opt) => opt.value === searchState.value.providerType,
      )
      filters.push(`类型: ${typeOption?.label}`)
    }

    if (searchState.value.status) {
      const statusOption = STATUS_OPTIONS.find((opt) => opt.value === searchState.value.status)
      filters.push(`状态: ${statusOption?.label}`)
    }

    const filterText = filters.length > 0 ? ` (${filters.join(', ')})` : ''
    return `找到 ${total} 个供应商${filterText}`
  }

  // 监听路由变化
  watch(
    () => route.query,
    () => {
      if (urlSyncOptions.enabled) {
        loadFromUrl()
      }
    },
    { deep: true },
  )

  // 监听搜索状态变化
  watch(
    searchState,
    () => {
      throttledUrlUpdate()
    },
    { deep: true },
  )

  // 初始化
  onMounted(async () => {
    // 从URL加载搜索参数
    loadFromUrl()

    // 如果有搜索条件，执行搜索
    if (hasActiveFilters.value) {
      await performSearch()
    }
  })

  // 清理
  onUnmounted(() => {
    showSuggestions.value = false
  })

  return {
    // 状态
    searchState,
    searchInput,
    showSuggestions,
    activeSuggestionIndex,
    showAdvancedSearch,
    searchStats,

    // Store状态
    providers,
    loading,
    isSearching,
    searchHistory,
    searchSuggestions,
    pagination,

    // 计算属性
    hasActiveFilters,
    isDefaultSort,
    currentSortOption,
    filteredSuggestions,
    searchParams,

    // 搜索方法
    handleSearchInput,
    handleSearchSubmit,
    clearSearch,
    applySuggestion,
    handleKeyboardNavigation,
    performSearch,

    // 筛选方法
    handleProviderTypeFilter,
    handleStatusFilter,
    handleSort,
    applySortOption,
    resetFilters,
    toggleAdvancedSearch,

    // 分页方法
    handlePageChange,
    handlePageSizeChange,

    // URL同步方法
    loadFromUrl,
    updateUrl,

    // 搜索历史方法
    getSearchHistory,
    clearSearchHistory,
    removeFromSearchHistory,

    // 工具方法
    exportSearchResults,
    getSearchSummary,

    // 常量
    PROVIDER_TYPE_OPTIONS,
    STATUS_OPTIONS,
    SORT_OPTIONS,
  }
}
