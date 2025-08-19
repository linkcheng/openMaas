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
import { setActivePinia, createPinia } from 'pinia'
import { useProviderStore } from '../providerStore'
import type { Provider, CreateProviderRequest, UpdateProviderRequest } from '@/types/providerTypes'
import { ProviderType } from '@/types/providerTypes'

// Mock the API
const mockApi = {
  listProviders: vi.fn(),
  createProvider: vi.fn(),
  updateProvider: vi.fn(),
  deleteProvider: vi.fn(),
  activateProvider: vi.fn(),
  deactivateProvider: vi.fn(),
  searchProviders: vi.fn(),
  generateSearchSuggestions: vi.fn(),
}

vi.mock('@/utils/api', () => ({
  providerApi: mockApi,
}))

// Mock notification composable
const mockNotification = {
  showSuccess: vi.fn(),
  showError: vi.fn(),
}

vi.mock('@/composables/useNotification', () => ({
  useNotification: () => mockNotification,
}))

describe('useProviderStore', () => {
  const mockProvider: Provider = {
    provider_id: 1,
    provider_name: 'test-provider',
    provider_type: ProviderType.OPENAI,
    display_name: 'Test Provider',
    description: 'Test description',
    base_url: 'https://api.openai.com/v1',
    additional_config: { timeout: 30 },
    is_active: true,
    created_by: 'admin',
    created_at: '2025-01-01T00:00:00Z',
    updated_by: 'admin',
    updated_at: '2025-01-01T00:00:00Z',
  }

  const mockProviders: Provider[] = [
    mockProvider,
    {
      ...mockProvider,
      provider_id: 2,
      provider_name: 'test-provider-2',
      display_name: 'Test Provider 2',
      is_active: false,
    },
  ]

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with default state', () => {
      const store = useProviderStore()

      expect(store.providers).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.isSearching).toBe(false)
      expect(store.searchHistory).toEqual([])
      expect(store.searchSuggestions).toEqual([])
      expect(store.pagination).toEqual({
        page: 1,
        size: 20,
        total: 0,
        pages: 0,
      })
    })

    it('should have correct computed properties', () => {
      const store = useProviderStore()

      expect(store.totalPages).toBe(0)
      expect(store.currentPage).toBe(1)
      expect(store.totalProviders).toBe(0)
      expect(store.hasProviders).toBe(false)
      expect(store.activeProviders).toEqual([])
      expect(store.inactiveProviders).toEqual([])
    })
  })

  describe('fetchProviders', () => {
    it('should fetch providers successfully', async () => {
      const mockResponse = {
        data: {
          items: mockProviders,
          page: 1,
          size: 20,
          total: 2,
          pages: 1,
        },
      }

      mockApi.listProviders.mockResolvedValue(mockResponse)

      const store = useProviderStore()
      await store.fetchProviders({ page: 1, size: 20 })

      expect(store.loading).toBe(false)
      expect(store.providers).toEqual(mockProviders)
      expect(store.pagination).toEqual({
        page: 1,
        size: 20,
        total: 2,
        pages: 1,
      })
      expect(store.error).toBe(null)
    })

    it('should handle fetch providers error', async () => {
      const error = new Error('Failed to fetch providers')
      mockApi.listProviders.mockRejectedValue(error)

      const store = useProviderStore()

      await expect(store.fetchProviders({})).rejects.toThrow('Failed to fetch providers')

      expect(store.loading).toBe(false)
      expect(store.error).toBe('Failed to fetch providers')
      expect(store.providers).toEqual([])
    })

    it('should set loading state during fetch', async () => {
      let resolvePromise: (value: any) => void
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      mockApi.listProviders.mockReturnValue(promise)

      const store = useProviderStore()
      const fetchPromise = store.fetchProviders({})

      expect(store.loading).toBe(true)

      resolvePromise!({
        data: {
          items: [],
          page: 1,
          size: 20,
          total: 0,
          pages: 0,
        },
      })

      await fetchPromise
      expect(store.loading).toBe(false)
    })
  })

  describe('createProvider', () => {
    it('should create provider successfully', async () => {
      const createRequest: CreateProviderRequest = {
        provider_name: 'new-provider',
        provider_type: ProviderType.OPENAI,
        display_name: 'New Provider',
        base_url: 'https://api.openai.com/v1',
        api_key: 'test-key',
        is_active: true,
      }

      const mockResponse = {
        data: {
          ...mockProvider,
          provider_id: 3,
          provider_name: 'new-provider',
          display_name: 'New Provider',
        },
      }

      mockApi.createProvider.mockResolvedValue(mockResponse)

      const store = useProviderStore()
      const result = await store.createProvider(createRequest)

      expect(result).toEqual(mockResponse.data)
      expect(mockApi.createProvider).toHaveBeenCalledWith(createRequest)
      expect(mockNotification.showSuccess).toHaveBeenCalledWith('供应商创建成功')
    })

    it('should handle create provider error', async () => {
      const createRequest: CreateProviderRequest = {
        provider_name: 'new-provider',
        provider_type: ProviderType.OPENAI,
        display_name: 'New Provider',
        base_url: 'https://api.openai.com/v1',
        is_active: true,
      }

      const error = new Error('Failed to create provider')
      mockApi.createProvider.mockRejectedValue(error)

      const store = useProviderStore()

      await expect(store.createProvider(createRequest)).rejects.toThrow('Failed to create provider')

      expect(store.error).toBe('Failed to create provider')
      expect(mockNotification.showError).toHaveBeenCalledWith(
        '创建供应商失败: Failed to create provider',
      )
    })
  })

  describe('updateProvider', () => {
    it('should update provider successfully', async () => {
      const updateRequest: UpdateProviderRequest = {
        display_name: 'Updated Provider',
        description: 'Updated description',
      }

      const updatedProvider = {
        ...mockProvider,
        display_name: 'Updated Provider',
        description: 'Updated description',
      }

      const mockResponse = {
        data: updatedProvider,
      }

      mockApi.updateProvider.mockResolvedValue(mockResponse)

      const store = useProviderStore()
      // Set initial providers
      store.providers = [mockProvider]

      const result = await store.updateProvider(1, updateRequest)

      expect(result).toEqual(updatedProvider)
      expect(mockApi.updateProvider).toHaveBeenCalledWith(1, updateRequest)
      expect(store.providers[0]).toEqual(updatedProvider)
      expect(mockNotification.showSuccess).toHaveBeenCalledWith('供应商更新成功')
    })

    it('should handle update provider error', async () => {
      const updateRequest: UpdateProviderRequest = {
        display_name: 'Updated Provider',
      }

      const error = new Error('Failed to update provider')
      mockApi.updateProvider.mockRejectedValue(error)

      const store = useProviderStore()

      await expect(store.updateProvider(1, updateRequest)).rejects.toThrow(
        'Failed to update provider',
      )

      expect(store.error).toBe('Failed to update provider')
      expect(mockNotification.showError).toHaveBeenCalledWith(
        '更新供应商失败: Failed to update provider',
      )
    })

    it('should not update local state if provider not found', async () => {
      const updateRequest: UpdateProviderRequest = {
        display_name: 'Updated Provider',
      }

      const mockResponse = {
        data: { ...mockProvider, display_name: 'Updated Provider' },
      }

      mockApi.updateProvider.mockResolvedValue(mockResponse)

      const store = useProviderStore()
      // Set providers without the target provider
      store.providers = [{ ...mockProvider, provider_id: 2 }]

      await store.updateProvider(1, updateRequest)

      // Local state should not change
      expect(store.providers[0].provider_id).toBe(2)
      expect(store.providers[0].display_name).toBe('Test Provider')
    })
  })

  describe('deleteProvider', () => {
    it('should delete provider successfully', async () => {
      mockApi.deleteProvider.mockResolvedValue({})

      const store = useProviderStore()
      // Set initial providers
      store.providers = [...mockProviders]

      const result = await store.deleteProvider(1)

      expect(result).toBe(true)
      expect(mockApi.deleteProvider).toHaveBeenCalledWith(1)
      expect(store.providers).toHaveLength(1)
      expect(store.providers[0].provider_id).toBe(2)
      expect(mockNotification.showSuccess).toHaveBeenCalledWith('供应商删除成功')
    })

    it('should handle delete provider error', async () => {
      const error = new Error('Failed to delete provider')
      mockApi.deleteProvider.mockRejectedValue(error)

      const store = useProviderStore()

      await expect(store.deleteProvider(1)).rejects.toThrow('Failed to delete provider')

      expect(store.error).toBe('Failed to delete provider')
      expect(mockNotification.showError).toHaveBeenCalledWith(
        '删除供应商失败: Failed to delete provider',
      )
    })
  })

  describe('activateProvider', () => {
    it('should activate provider successfully', async () => {
      mockApi.activateProvider.mockResolvedValue({})

      const store = useProviderStore()
      // Set initial providers with inactive provider
      const inactiveProvider = { ...mockProvider, is_active: false }
      store.providers = [inactiveProvider]

      const result = await store.activateProvider(1)

      expect(result).toBe(true)
      expect(mockApi.activateProvider).toHaveBeenCalledWith(1)
      expect(store.providers[0].is_active).toBe(true)
      expect(mockNotification.showSuccess).toHaveBeenCalledWith('供应商激活成功')
    })

    it('should handle activate provider error', async () => {
      const error = new Error('Failed to activate provider')
      mockApi.activateProvider.mockRejectedValue(error)

      const store = useProviderStore()

      await expect(store.activateProvider(1)).rejects.toThrow('Failed to activate provider')

      expect(store.error).toBe('Failed to activate provider')
      expect(mockNotification.showError).toHaveBeenCalledWith(
        '激活供应商失败: Failed to activate provider',
      )
    })
  })

  describe('deactivateProvider', () => {
    it('should deactivate provider successfully', async () => {
      mockApi.deactivateProvider.mockResolvedValue({})

      const store = useProviderStore()
      // Set initial providers with active provider
      store.providers = [mockProvider]

      const result = await store.deactivateProvider(1)

      expect(result).toBe(true)
      expect(mockApi.deactivateProvider).toHaveBeenCalledWith(1)
      expect(store.providers[0].is_active).toBe(false)
      expect(mockNotification.showSuccess).toHaveBeenCalledWith('供应商停用成功')
    })

    it('should handle deactivate provider error', async () => {
      const error = new Error('Failed to deactivate provider')
      mockApi.deactivateProvider.mockRejectedValue(error)

      const store = useProviderStore()

      await expect(store.deactivateProvider(1)).rejects.toThrow('Failed to deactivate provider')

      expect(store.error).toBe('Failed to deactivate provider')
      expect(mockNotification.showError).toHaveBeenCalledWith(
        '停用供应商失败: Failed to deactivate provider',
      )
    })
  })

  describe('searchProviders', () => {
    it('should search providers successfully', async () => {
      const mockResponse = {
        data: {
          items: [mockProvider],
          page: 1,
          size: 20,
          total: 1,
          pages: 1,
        },
      }

      mockApi.searchProviders.mockResolvedValue(mockResponse)

      const store = useProviderStore()
      await store.searchProviders({ keyword: 'test' })

      expect(store.isSearching).toBe(false)
      expect(store.providers).toEqual([mockProvider])
      expect(store.pagination).toEqual({
        page: 1,
        size: 20,
        total: 1,
        pages: 1,
      })
    })

    it('should handle search providers error', async () => {
      const error = new Error('Search failed')
      mockApi.searchProviders.mockRejectedValue(error)

      const store = useProviderStore()

      await expect(store.searchProviders({ keyword: 'test' })).rejects.toThrow('Search failed')

      expect(store.isSearching).toBe(false)
      expect(store.error).toBe('Search failed')
    })

    it('should add search term to history', async () => {
      const mockResponse = {
        data: {
          items: [],
          page: 1,
          size: 20,
          total: 0,
          pages: 0,
        },
      }

      mockApi.searchProviders.mockResolvedValue(mockResponse)

      const store = useProviderStore()
      await store.searchProviders({ keyword: 'test search' })

      expect(store.searchHistory).toContain('test search')
    })

    it('should not add empty search terms to history', async () => {
      const mockResponse = {
        data: {
          items: [],
          page: 1,
          size: 20,
          total: 0,
          pages: 0,
        },
      }

      mockApi.searchProviders.mockResolvedValue(mockResponse)

      const store = useProviderStore()
      await store.searchProviders({ keyword: '' })

      expect(store.searchHistory).not.toContain('')
    })

    it('should limit search history to 10 items', async () => {
      const mockResponse = {
        data: {
          items: [],
          page: 1,
          size: 20,
          total: 0,
          pages: 0,
        },
      }

      mockApi.searchProviders.mockResolvedValue(mockResponse)

      const store = useProviderStore()

      // Add 12 search terms
      for (let i = 0; i < 12; i++) {
        await store.searchProviders({ keyword: `search ${i}` })
      }

      expect(store.searchHistory).toHaveLength(10)
      expect(store.searchHistory[0]).toBe('search 11') // Most recent first
    })
  })

  describe('generateSearchSuggestions', () => {
    it('should generate search suggestions', async () => {
      const mockSuggestions = [
        { text: 'OpenAI Provider', type: 'provider' as const },
        { text: 'test-provider', type: 'provider' as const },
      ]

      mockApi.generateSearchSuggestions.mockResolvedValue({
        data: mockSuggestions,
      })

      const store = useProviderStore()
      await store.generateSearchSuggestions('test')

      expect(store.searchSuggestions).toEqual(mockSuggestions)
      expect(mockApi.generateSearchSuggestions).toHaveBeenCalledWith('test')
    })

    it('should handle generate suggestions error', async () => {
      const error = new Error('Failed to generate suggestions')
      mockApi.generateSearchSuggestions.mockRejectedValue(error)

      const store = useProviderStore()

      // Should not throw error, just log it
      await store.generateSearchSuggestions('test')

      expect(store.searchSuggestions).toEqual([])
    })
  })

  describe('Search History Management', () => {
    it('should clear search history', () => {
      const store = useProviderStore()
      store.searchHistory = ['search 1', 'search 2']

      store.clearSearchHistory()

      expect(store.searchHistory).toEqual([])
    })

    it('should remove item from search history', () => {
      const store = useProviderStore()
      store.searchHistory = ['search 1', 'search 2', 'search 3']

      store.removeFromSearchHistory('search 2')

      expect(store.searchHistory).toEqual(['search 1', 'search 3'])
    })

    it('should not fail when removing non-existent item', () => {
      const store = useProviderStore()
      store.searchHistory = ['search 1', 'search 2']

      store.removeFromSearchHistory('non-existent')

      expect(store.searchHistory).toEqual(['search 1', 'search 2'])
    })
  })

  describe('Computed Properties', () => {
    it('should calculate totalPages correctly', () => {
      const store = useProviderStore()

      store.pagination = { page: 1, size: 20, total: 45, pages: 3 }
      expect(store.totalPages).toBe(3)

      store.pagination = { page: 1, size: 20, total: 0, pages: 0 }
      expect(store.totalPages).toBe(0)
    })

    it('should return currentPage correctly', () => {
      const store = useProviderStore()

      store.pagination = { page: 2, size: 20, total: 45, pages: 3 }
      expect(store.currentPage).toBe(2)
    })

    it('should return totalProviders correctly', () => {
      const store = useProviderStore()

      store.pagination = { page: 1, size: 20, total: 45, pages: 3 }
      expect(store.totalProviders).toBe(45)
    })

    it('should return hasProviders correctly', () => {
      const store = useProviderStore()

      expect(store.hasProviders).toBe(false)

      store.providers = [mockProvider]
      expect(store.hasProviders).toBe(true)
    })

    it('should filter activeProviders correctly', () => {
      const store = useProviderStore()
      store.providers = mockProviders

      const activeProviders = store.activeProviders
      expect(activeProviders).toHaveLength(1)
      expect(activeProviders[0].is_active).toBe(true)
    })

    it('should filter inactiveProviders correctly', () => {
      const store = useProviderStore()
      store.providers = mockProviders

      const inactiveProviders = store.inactiveProviders
      expect(inactiveProviders).toHaveLength(1)
      expect(inactiveProviders[0].is_active).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should clear error when operation succeeds', async () => {
      const store = useProviderStore()
      store.error = 'Previous error'

      const mockResponse = {
        data: {
          items: [],
          page: 1,
          size: 20,
          total: 0,
          pages: 0,
        },
      }

      mockApi.listProviders.mockResolvedValue(mockResponse)

      await store.fetchProviders({})

      expect(store.error).toBe(null)
    })

    it('should handle network errors gracefully', async () => {
      const networkError = new Error('Network Error')
      networkError.name = 'NetworkError'
      mockApi.listProviders.mockRejectedValue(networkError)

      const store = useProviderStore()

      await expect(store.fetchProviders({})).rejects.toThrow('Network Error')

      expect(store.error).toBe('Network Error')
    })

    it('should handle API errors with custom messages', async () => {
      const apiError = {
        response: {
          data: {
            message: 'Custom API error message',
          },
        },
      }
      mockApi.createProvider.mockRejectedValue(apiError)

      const store = useProviderStore()

      await expect(
        store.createProvider({
          provider_name: 'test',
          provider_type: ProviderType.OPENAI,
          display_name: 'Test',
          base_url: 'https://api.test.com',
          is_active: true,
        }),
      ).rejects.toEqual(apiError)
    })
  })

  describe('State Persistence', () => {
    it('should maintain state consistency during concurrent operations', async () => {
      const store = useProviderStore()
      store.providers = [mockProvider]

      // Simulate concurrent update and delete
      const updatePromise = store.updateProvider(1, { display_name: 'Updated' })
      const deletePromise = store.deleteProvider(1)

      mockApi.updateProvider.mockResolvedValue({
        data: { ...mockProvider, display_name: 'Updated' },
      })
      mockApi.deleteProvider.mockResolvedValue({})

      await Promise.all([updatePromise, deletePromise])

      // Delete should win, provider should be removed
      expect(store.providers).toHaveLength(0)
    })
  })
})
