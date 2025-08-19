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

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useProviderSearch } from '../useProviderSearch'
import { useProviderStore } from '@/stores/providerStore'
import type { Provider, ProviderType } from '@/types/providerTypes'
import { ProviderStatus } from '@/types/providerTypes'

// Mock the store
vi.mock('@/stores/providerStore')
vi.mock('pinia', () => ({
  storeToRefs: vi.fn(() => ({
    providers: { value: [] },
    loading: { value: false },
    isSearching: { value: false },
    searchHistory: { value: [] },
    searchSuggestions: { value: [] },
    pagination: { value: { page: 1, size: 20, total: 0, pages: 0 } },
  })),
}))

// Mock Vue Router
const mockRoute = {
  query: {},
}
const mockRouter = {
  replace: vi.fn(() => Promise.resolve()),
}

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
  useRouter: () => mockRouter,
}))

// Mock Vue composition functions
vi.mock('vue', async () => {
  const actual = await vi.importActual('vue')
  return {
    ...actual,
    onMounted: vi.fn((fn) => fn()),
    onUnmounted: vi.fn(),
    watch: vi.fn(),
    nextTick: vi.fn(() => Promise.resolve()),
  }
})

// Mock VueUse functions
vi.mock('@vueuse/core', () => ({
  useDebounceFn: vi.fn((fn) => fn),
  useThrottleFn: vi.fn((fn) => fn),
}))

describe('useProviderSearch', () => {
  const mockProviders: Provider[] = [
    {
      provider_id: 1,
      provider_name: 'openai-provider',
      provider_type: 'openai',
      display_name: 'OpenAI Provider',
      description: 'OpenAI API provider',
      base_url: 'https://api.openai.com/v1',
      additional_config: {},
      is_active: true,
      created_by: 'test-user',
      created_at: '2025-01-01T00:00:00Z',
      updated_by: 'test-user',
      updated_at: '2025-01-01T00:00:00Z',
    },
    {
      provider_id: 2,
      provider_name: 'anthropic-provider',
      provider_type: 'anthropic',
      display_name: 'Anthropic Provider',
      description: 'Anthropic API provider',
      base_url: 'https://api.anthropic.com',
      additional_config: {},
      is_active: false,
      created_by: 'test-user',
      created_at: '2025-01-01T00:00:00Z',
      updated_by: 'test-user',
      updated_at: '2025-01-01T00:00:00Z',
    },
  ]

  let mockProviderStore: any

  beforeEach(() => {
    vi.clearAllMocks()
    mockProviderStore = {
      searchProviders: vi.fn(),
      generateSearchSuggestions: vi.fn(),
      clearSearchHistory: vi.fn(),
      removeFromSearchHistory: vi.fn(),
    }
    vi.mocked(useProviderStore).mockReturnValue(mockProviderStore)

    // Reset route query
    mockRoute.query = {}
  })

  describe('Search State Management', () => {
    it('should initialize with default search state', () => {
      const { searchState, searchInput, showSuggestions, showAdvancedSearch } = useProviderSearch()

      expect(searchState.value.keyword).toBe('')
      expect(searchState.value.providerType).toBe('')
      expect(searchState.value.status).toBe('')
      expect(searchState.value.sortBy).toBe('created_at')
      expect(searchState.value.sortOrder).toBe('desc')
      expect(searchState.value.page).toBe(1)
      expect(searchState.value.size).toBe(20)
      expect(searchInput.value).toBe('')
      expect(showSuggestions.value).toBe(false)
      expect(showAdvancedSearch.value).toBe(false)
    })

    it('should track active filters correctly', () => {
      const { searchState, hasActiveFilters } = useProviderSearch()

      // Initially no active filters
      expect(hasActiveFilters.value).toBe(false)

      // Add keyword filter
      searchState.value.keyword = 'test'
      expect(hasActiveFilters.value).toBe(true)

      // Clear keyword, add provider type filter
      searchState.value.keyword = ''
      searchState.value.providerType = 'openai' as ProviderType
      expect(hasActiveFilters.value).toBe(true)

      // Clear provider type, add status filter
      searchState.value.providerType = ''
      searchState.value.status = ProviderStatus.ACTIVE
      expect(hasActiveFilters.value).toBe(true)

      // Clear status, change sort
      searchState.value.status = ''
      searchState.value.sortBy = 'display_name'
      expect(hasActiveFilters.value).toBe(true)
    })

    it('should detect default sort correctly', () => {
      const { searchState, isDefaultSort } = useProviderSearch()

      // Initially default sort
      expect(isDefaultSort.value).toBe(true)

      // Change sort field
      searchState.value.sortBy = 'display_name'
      expect(isDefaultSort.value).toBe(false)

      // Reset sort field but change order
      searchState.value.sortBy = 'created_at'
      searchState.value.sortOrder = 'asc'
      expect(isDefaultSort.value).toBe(false)
    })

    it('should generate search parameters correctly', () => {
      const { searchState, searchParams } = useProviderSearch()

      // Test with all parameters
      searchState.value.keyword = 'test'
      searchState.value.providerType = 'openai' as ProviderType
      searchState.value.status = ProviderStatus.ACTIVE
      searchState.value.page = 2
      searchState.value.size = 10

      const params = searchParams.value

      expect(params.keyword).toBe('test')
      expect(params.provider_type).toBe('openai')
      expect(params.is_active).toBe(true)
      expect(params.page).toBe(2)
      expect(params.size).toBe(10)
    })
  })

  describe('Search Input Handling', () => {
    it('should handle search input changes', () => {
      const { handleSearchInput, searchInput, showSuggestions } = useProviderSearch()

      // Test with short input (should not show suggestions)
      handleSearchInput('a')
      expect(searchInput.value).toBe('a')
      expect(showSuggestions.value).toBe(false)

      // Test with longer input (should show suggestions)
      handleSearchInput('test')
      expect(searchInput.value).toBe('test')
      expect(showSuggestions.value).toBe(true)
      expect(mockProviderStore.generateSearchSuggestions).toHaveBeenCalledWith('test')
    })

    it('should handle search submission', async () => {
      const { handleSearchSubmit, searchInput, searchState, showSuggestions } = useProviderSearch()

      searchInput.value = '  test keyword  '

      await handleSearchSubmit()

      expect(searchState.value.keyword).toBe('test keyword')
      expect(searchState.value.page).toBe(1)
      expect(showSuggestions.value).toBe(false)
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })

    it('should clear search correctly', async () => {
      const { clearSearch, searchInput, searchState, showSuggestions } = useProviderSearch()

      // Set some search state
      searchInput.value = 'test'
      searchState.value.keyword = 'test'
      searchState.value.page = 2

      await clearSearch()

      expect(searchInput.value).toBe('')
      expect(searchState.value.keyword).toBe('')
      expect(searchState.value.page).toBe(1)
      expect(showSuggestions.value).toBe(false)
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })
  })

  describe('Search Suggestions', () => {
    it('should generate filtered suggestions', () => {
      const { searchInput, filteredSuggestions } = useProviderSearch()

      // Mock providers and search history through store refs
      const _mockStoreRefs = vi.mocked(require('pinia').storeToRefs).mockReturnValue({
        providers: { value: mockProviders },
        loading: { value: false },
        isSearching: { value: false },
        searchHistory: { value: ['previous search', 'another search'] },
        searchSuggestions: { value: [] },
        pagination: { value: { page: 1, size: 20, total: 0, pages: 0 } },
      })

      searchInput.value = 'open'

      const suggestions = filteredSuggestions.value

      // Should include matching providers and history
      expect(suggestions.some((s) => s.text === 'OpenAI Provider')).toBe(true)
      expect(suggestions.some((s) => s.text === 'openai-provider')).toBe(true)
      expect(suggestions.every((s) => s.text.toLowerCase().includes('open'))).toBe(true)
    })

    it('should apply suggestions correctly', async () => {
      const { applySuggestion, searchInput, searchState, showSuggestions } = useProviderSearch()

      const suggestion = {
        text: 'OpenAI Provider',
        type: 'provider' as const,
      }

      await applySuggestion(suggestion)

      expect(searchInput.value).toBe('OpenAI Provider')
      expect(searchState.value.keyword).toBe('OpenAI Provider')
      expect(searchState.value.page).toBe(1)
      expect(showSuggestions.value).toBe(false)
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })

    it('should handle keyboard navigation', () => {
      const {
        handleKeyboardNavigation,
        activeSuggestionIndex,
        showSuggestions,
        filteredSuggestions,
      } = useProviderSearch()

      // Mock suggestions
      showSuggestions.value = true
      filteredSuggestions.value = [
        { text: 'suggestion 1', type: 'history' },
        { text: 'suggestion 2', type: 'provider' },
      ]

      // Test arrow down
      const downEvent = new KeyboardEvent('keydown', { key: 'ArrowDown' })
      handleKeyboardNavigation(downEvent)
      expect(activeSuggestionIndex.value).toBe(0)

      // Test arrow down again
      handleKeyboardNavigation(downEvent)
      expect(activeSuggestionIndex.value).toBe(1)

      // Test arrow up
      const upEvent = new KeyboardEvent('keydown', { key: 'ArrowUp' })
      handleKeyboardNavigation(upEvent)
      expect(activeSuggestionIndex.value).toBe(0)

      // Test escape
      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' })
      handleKeyboardNavigation(escapeEvent)
      expect(showSuggestions.value).toBe(false)
      expect(activeSuggestionIndex.value).toBe(-1)
    })
  })

  describe('Filter Handling', () => {
    it('should handle provider type filter', async () => {
      const { handleProviderTypeFilter, searchState } = useProviderSearch()

      await handleProviderTypeFilter('openai' as ProviderType)

      expect(searchState.value.providerType).toBe('openai')
      expect(searchState.value.page).toBe(1)
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })

    it('should handle status filter', async () => {
      const { handleStatusFilter, searchState } = useProviderSearch()

      await handleStatusFilter(ProviderStatus.ACTIVE)

      expect(searchState.value.status).toBe(ProviderStatus.ACTIVE)
      expect(searchState.value.page).toBe(1)
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })

    it('should handle sort changes', async () => {
      const { handleSort, searchState } = useProviderSearch()

      await handleSort('display_name', 'asc')

      expect(searchState.value.sortBy).toBe('display_name')
      expect(searchState.value.sortOrder).toBe('asc')
      expect(searchState.value.page).toBe(1)
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })

    it('should reset all filters', async () => {
      const { resetFilters, searchInput, searchState, showSuggestions, showAdvancedSearch } =
        useProviderSearch()

      // Set some filters
      searchInput.value = 'test'
      searchState.value.keyword = 'test'
      searchState.value.providerType = 'openai' as ProviderType
      searchState.value.status = ProviderStatus.ACTIVE
      searchState.value.sortBy = 'display_name'
      searchState.value.page = 2
      showSuggestions.value = true
      showAdvancedSearch.value = true

      await resetFilters()

      expect(searchInput.value).toBe('')
      expect(searchState.value.keyword).toBe('')
      expect(searchState.value.providerType).toBe('')
      expect(searchState.value.status).toBe('')
      expect(searchState.value.sortBy).toBe('created_at')
      expect(searchState.value.sortOrder).toBe('desc')
      expect(searchState.value.page).toBe(1)
      expect(showSuggestions.value).toBe(false)
      expect(showAdvancedSearch.value).toBe(false)
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })
  })

  describe('Pagination Handling', () => {
    it('should handle page changes', async () => {
      const { handlePageChange, searchState } = useProviderSearch()

      await handlePageChange(3)

      expect(searchState.value.page).toBe(3)
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })

    it('should handle page size changes', async () => {
      const { handlePageSizeChange, searchState } = useProviderSearch()

      await handlePageSizeChange(50)

      expect(searchState.value.size).toBe(50)
      expect(searchState.value.page).toBe(1) // Should reset to first page
      expect(mockProviderStore.searchProviders).toHaveBeenCalled()
    })
  })

  describe('URL Synchronization', () => {
    it('should load search parameters from URL', () => {
      // Set up URL query parameters
      mockRoute.query = {
        keyword: 'test search',
        type: 'openai',
        status: 'active',
        sort: 'display_name',
        order: 'asc',
        page: '2',
        size: '50',
      }

      const { loadFromUrl, searchState, searchInput } = useProviderSearch()

      loadFromUrl()

      expect(searchInput.value).toBe('test search')
      expect(searchState.value.keyword).toBe('test search')
      expect(searchState.value.providerType).toBe('openai')
      expect(searchState.value.status).toBe('active')
      expect(searchState.value.sortBy).toBe('display_name')
      expect(searchState.value.sortOrder).toBe('asc')
      expect(searchState.value.page).toBe(2)
      expect(searchState.value.size).toBe(50)
    })

    it('should update URL with search parameters', () => {
      const { updateUrl, searchState } = useProviderSearch()

      // Set search state
      searchState.value.keyword = 'test'
      searchState.value.providerType = 'openai' as ProviderType
      searchState.value.status = ProviderStatus.ACTIVE
      searchState.value.sortBy = 'display_name'
      searchState.value.sortOrder = 'asc'
      searchState.value.page = 2

      updateUrl()

      expect(mockRouter.replace).toHaveBeenCalledWith({
        query: expect.objectContaining({
          keyword: 'test',
          type: 'openai',
          status: 'active',
          sort: 'display_name',
          order: 'asc',
          page: '2',
        }),
      })
    })

    it('should handle URL sync options', () => {
      const options = {
        enabled: false,
        paramPrefix: 'search_',
        excludeParams: ['page'],
      }

      const { updateUrl } = useProviderSearch(options)

      // Should not update URL when disabled
      updateUrl()
      expect(mockRouter.replace).not.toHaveBeenCalled()
    })
  })

  describe('Search History Management', () => {
    it('should get search history', () => {
      const { getSearchHistory, searchHistory } = useProviderSearch()

      searchHistory.value = ['search 1', 'search 2', 'search 3']

      const history = getSearchHistory()
      expect(history).toEqual(['search 1', 'search 2', 'search 3'])
    })

    it('should clear search history', () => {
      const { clearSearchHistory } = useProviderSearch()

      clearSearchHistory()

      expect(mockProviderStore.clearSearchHistory).toHaveBeenCalled()
    })

    it('should remove item from search history', () => {
      const { removeFromSearchHistory } = useProviderSearch()

      removeFromSearchHistory('test search')

      expect(mockProviderStore.removeFromSearchHistory).toHaveBeenCalledWith('test search')
    })
  })

  describe('Advanced Features', () => {
    it('should toggle advanced search', () => {
      const { toggleAdvancedSearch, showAdvancedSearch } = useProviderSearch()

      expect(showAdvancedSearch.value).toBe(false)

      toggleAdvancedSearch()
      expect(showAdvancedSearch.value).toBe(true)

      toggleAdvancedSearch()
      expect(showAdvancedSearch.value).toBe(false)
    })

    it('should generate search summary', () => {
      const { getSearchSummary, searchState, pagination } = useProviderSearch()

      pagination.value.total = 25
      searchState.value.keyword = 'test'
      searchState.value.providerType = 'openai' as ProviderType
      searchState.value.status = ProviderStatus.ACTIVE

      const summary = getSearchSummary()

      expect(summary).toContain('找到 25 个供应商')
      expect(summary).toContain('关键词: "test"')
      expect(summary).toContain('类型: OpenAI')
      expect(summary).toContain('状态: 激活')
    })

    it('should export search results', () => {
      const { exportSearchResults } = useProviderSearch()

      // Mock providers through store refs
      vi.mocked(require('pinia').storeToRefs).mockReturnValue({
        providers: { value: mockProviders },
        loading: { value: false },
        isSearching: { value: false },
        searchHistory: { value: [] },
        searchSuggestions: { value: [] },
        pagination: { value: { page: 1, size: 20, total: 0, pages: 0 } },
      })

      // Mock DOM methods
      const mockLink = {
        setAttribute: vi.fn(),
        click: vi.fn(),
        style: { visibility: '' },
      }
      const mockCreateElement = vi.fn(() => mockLink as unknown as HTMLElement)
      const mockCreateObjectURL = vi.fn(() => 'blob:url')
      const mockAppendChild = vi.fn()
      const mockRemoveChild = vi.fn()

      Object.defineProperty(global.document, 'createElement', {
        value: mockCreateElement,
        writable: true,
      })
      Object.defineProperty(global.URL, 'createObjectURL', {
        value: mockCreateObjectURL,
        writable: true,
      })
      Object.defineProperty(global.document.body, 'appendChild', {
        value: mockAppendChild,
        writable: true,
      })
      Object.defineProperty(global.document.body, 'removeChild', {
        value: mockRemoveChild,
        writable: true,
      })

      exportSearchResults()

      expect(mockCreateElement).toHaveBeenCalledWith('a')
      expect(mockLink.setAttribute).toHaveBeenCalledWith('href', 'blob:url')
      expect(mockLink.setAttribute).toHaveBeenCalledWith(
        'download',
        expect.stringContaining('providers_search_'),
      )
      expect(mockLink.click).toHaveBeenCalled()
    })
  })

  describe('Error Handling', () => {
    it('should handle search errors gracefully', async () => {
      const { performSearch } = useProviderSearch()

      mockProviderStore.searchProviders.mockRejectedValue(new Error('Search failed'))

      // Should not throw error
      await expect(performSearch()).resolves.not.toThrow()
    })

    it('should handle invalid URL parameters', () => {
      mockRoute.query = {
        keyword: 'valid',
        type: 'invalid-type',
        status: 'invalid-status',
        sort: 'invalid-sort',
        order: 'invalid-order',
        page: 'invalid-page',
        size: 'invalid-size',
      }

      const { loadFromUrl, searchState } = useProviderSearch()

      loadFromUrl()

      // Should only load valid parameters
      expect(searchState.value.keyword).toBe('valid')
      expect(searchState.value.providerType).toBe('') // Invalid type ignored
      expect(searchState.value.status).toBe('') // Invalid status ignored
      expect(searchState.value.sortBy).toBe('created_at') // Invalid sort ignored
      expect(searchState.value.sortOrder).toBe('desc') // Invalid order ignored
      expect(searchState.value.page).toBe(1) // Invalid page ignored
      expect(searchState.value.size).toBe(20) // Invalid size ignored
    })

    it('should handle empty suggestions gracefully', () => {
      const { handleKeyboardNavigation, showSuggestions, filteredSuggestions } = useProviderSearch()

      showSuggestions.value = true
      filteredSuggestions.value = []

      const downEvent = new KeyboardEvent('keydown', { key: 'ArrowDown' })

      // Should not throw error with empty suggestions
      expect(() => handleKeyboardNavigation(downEvent)).not.toThrow()
    })
  })

  describe('Performance Considerations', () => {
    it('should debounce search input', () => {
      const { handleSearchInput } = useProviderSearch()

      // Mock debounce function was called
      expect(vi.mocked(require('@vueuse/core')).useDebounceFn).toHaveBeenCalled()

      handleSearchInput('test')
      // The actual debouncing behavior is handled by the mocked function
    })

    it('should throttle URL updates', () => {
      const { updateUrl } = useProviderSearch()

      // Mock throttle function was called
      expect(vi.mocked(require('@vueuse/core')).useThrottleFn).toHaveBeenCalled()

      updateUrl()
      // The actual throttling behavior is handled by the mocked function
    })

    it('should limit suggestion count', () => {
      const { searchInput, filteredSuggestions } = useProviderSearch()

      // Create many providers and history items
      const manyProviders = Array.from({ length: 20 }, (_, i) => ({
        ...mockProviders[0],
        provider_id: i,
        display_name: `Provider ${i}`,
        provider_name: `provider-${i}`,
      }))
      const manyHistory = Array.from({ length: 20 }, (_, i) => `search ${i}`)

      // Mock store refs with many items
      vi.mocked(require('pinia').storeToRefs).mockReturnValue({
        providers: { value: manyProviders },
        loading: { value: false },
        isSearching: { value: false },
        searchHistory: { value: manyHistory },
        searchSuggestions: { value: [] },
        pagination: { value: { page: 1, size: 20, total: 0, pages: 0 } },
      })

      searchInput.value = 'provider'

      const suggestions = filteredSuggestions.value

      // Should limit to 8 suggestions
      expect(suggestions.length).toBeLessThanOrEqual(8)
    })
  })
})
