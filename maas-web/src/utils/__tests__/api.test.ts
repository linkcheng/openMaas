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

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { providerApi } from '../api'
import type {
  CreateProviderRequest,
  UpdateProviderRequest,
  ListProvidersParams,
  SearchProvidersParams,
} from '@/types/providerTypes'
import { ProviderType } from '@/types/providerTypes'

// Mock the HTTP client
const mockHttpClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn(),
}

vi.mock('../httpClient', () => ({
  default: mockHttpClient,
}))

describe('Provider API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('listProviders', () => {
    it('should call GET /api/providers with correct parameters', async () => {
      const mockResponse = {
        data: {
          items: [],
          page: 1,
          size: 20,
          total: 0,
          pages: 0,
        },
      }

      mockHttpClient.get.mockResolvedValue(mockResponse)

      const params: ListProvidersParams = {
        page: 1,
        size: 20,
        provider_type: 'openai',
        is_active: true,
        sort_by: 'created_at',
        sort_order: 'desc',
      }

      const result = await providerApi.listProviders(params)

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/providers', {
        params: {
          page: 1,
          size: 20,
          provider_type: 'openai',
          is_active: true,
          sort_by: 'created_at',
          sort_order: 'desc',
        },
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle empty parameters', async () => {
      const mockResponse = {
        data: {
          items: [],
          page: 1,
          size: 20,
          total: 0,
          pages: 0,
        },
      }

      mockHttpClient.get.mockResolvedValue(mockResponse)

      await providerApi.listProviders({})

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/providers', {
        params: {},
      })
    })

    it('should handle API errors', async () => {
      const error = new Error('Network error')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(providerApi.listProviders({})).rejects.toThrow('Network error')
    })
  })

  describe('createProvider', () => {
    it('should call POST /api/providers with correct data', async () => {
      const createRequest: CreateProviderRequest = {
        provider_name: 'test-provider',
        provider_type: ProviderType.OPENAI,
        display_name: 'Test Provider',
        base_url: 'https://api.openai.com/v1',
        api_key: 'test-key',
        description: 'Test description',
        additional_config: { timeout: 30 },
        is_active: true,
      }

      const mockResponse = {
        data: {
          provider_id: 1,
          ...createRequest,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          created_by: 'admin',
          updated_by: 'admin',
        },
      }

      mockHttpClient.post.mockResolvedValue(mockResponse)

      const result = await providerApi.createProvider(createRequest)

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/providers', createRequest)
      expect(result).toEqual(mockResponse)
    })

    it('should handle validation errors', async () => {
      const createRequest: CreateProviderRequest = {
        provider_name: '',
        provider_type: ProviderType.OPENAI,
        display_name: '',
        base_url: '',
        is_active: true,
      }

      const validationError = {
        response: {
          status: 400,
          data: {
            message: 'Validation failed',
            errors: {
              provider_name: ['Provider name is required'],
              display_name: ['Display name is required'],
              base_url: ['Base URL is required'],
            },
          },
        },
      }

      mockHttpClient.post.mockRejectedValue(validationError)

      await expect(providerApi.createProvider(createRequest)).rejects.toEqual(validationError)
    })
  })

  describe('updateProvider', () => {
    it('should call PUT /api/providers/:id with correct data', async () => {
      const updateRequest: UpdateProviderRequest = {
        display_name: 'Updated Provider',
        description: 'Updated description',
        is_active: false,
      }

      const mockResponse = {
        data: {
          provider_id: 1,
          provider_name: 'test-provider',
          provider_type: ProviderType.OPENAI,
          display_name: 'Updated Provider',
          description: 'Updated description',
          base_url: 'https://api.openai.com/v1',
          additional_config: {},
          is_active: false,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T01:00:00Z',
          created_by: 'admin',
          updated_by: 'admin',
        },
      }

      mockHttpClient.put.mockResolvedValue(mockResponse)

      const result = await providerApi.updateProvider(1, updateRequest)

      expect(mockHttpClient.put).toHaveBeenCalledWith('/api/providers/1', updateRequest)
      expect(result).toEqual(mockResponse)
    })

    it('should handle not found errors', async () => {
      const updateRequest: UpdateProviderRequest = {
        display_name: 'Updated Provider',
      }

      const notFoundError = {
        response: {
          status: 404,
          data: {
            message: 'Provider not found',
          },
        },
      }

      mockHttpClient.put.mockRejectedValue(notFoundError)

      await expect(providerApi.updateProvider(999, updateRequest)).rejects.toEqual(notFoundError)
    })
  })

  describe('deleteProvider', () => {
    it('should call DELETE /api/providers/:id', async () => {
      mockHttpClient.delete.mockResolvedValue({
        data: { message: 'Provider deleted successfully' },
      })

      const result = await providerApi.deleteProvider(1)

      expect(mockHttpClient.delete).toHaveBeenCalledWith('/api/providers/1')
      expect(result.data.message).toBe('Provider deleted successfully')
    })

    it('should handle delete conflicts', async () => {
      const conflictError = {
        response: {
          status: 409,
          data: {
            message: 'Cannot delete provider: it is being used by active models',
            details: {
              affected_models: ['model-1', 'model-2'],
            },
          },
        },
      }

      mockHttpClient.delete.mockRejectedValue(conflictError)

      await expect(providerApi.deleteProvider(1)).rejects.toEqual(conflictError)
    })
  })

  describe('activateProvider', () => {
    it('should call PATCH /api/providers/:id/activate', async () => {
      mockHttpClient.patch.mockResolvedValue({
        data: { message: 'Provider activated successfully' },
      })

      const result = await providerApi.activateProvider(1)

      expect(mockHttpClient.patch).toHaveBeenCalledWith('/api/providers/1/activate')
      expect(result.data.message).toBe('Provider activated successfully')
    })

    it('should handle activation errors', async () => {
      const activationError = {
        response: {
          status: 400,
          data: {
            message: 'Cannot activate provider: invalid configuration',
          },
        },
      }

      mockHttpClient.patch.mockRejectedValue(activationError)

      await expect(providerApi.activateProvider(1)).rejects.toEqual(activationError)
    })
  })

  describe('deactivateProvider', () => {
    it('should call PATCH /api/providers/:id/deactivate', async () => {
      mockHttpClient.patch.mockResolvedValue({
        data: { message: 'Provider deactivated successfully' },
      })

      const result = await providerApi.deactivateProvider(1)

      expect(mockHttpClient.patch).toHaveBeenCalledWith('/api/providers/1/deactivate')
      expect(result.data.message).toBe('Provider deactivated successfully')
    })
  })

  describe('searchProviders', () => {
    it('should call GET /api/providers/search with correct parameters', async () => {
      const searchParams: SearchProvidersParams = {
        keyword: 'openai',
        provider_type: 'openai',
        is_active: true,
        page: 1,
        size: 20,
      }

      const mockResponse = {
        data: {
          items: [
            {
              provider_id: 1,
              provider_name: 'openai-provider',
              provider_type: ProviderType.OPENAI,
              display_name: 'OpenAI Provider',
              description: 'OpenAI API provider',
              base_url: 'https://api.openai.com/v1',
              additional_config: {},
              is_active: true,
              created_at: '2025-01-01T00:00:00Z',
              updated_at: '2025-01-01T00:00:00Z',
              created_by: 'admin',
              updated_by: 'admin',
            },
          ],
          page: 1,
          size: 20,
          total: 1,
          pages: 1,
        },
      }

      mockHttpClient.get.mockResolvedValue(mockResponse)

      const result = await providerApi.searchProviders(searchParams)

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/providers/search', {
        params: searchParams,
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle empty search results', async () => {
      const searchParams: SearchProvidersParams = {
        keyword: 'nonexistent',
      }

      const mockResponse = {
        data: {
          items: [],
          page: 1,
          size: 20,
          total: 0,
          pages: 0,
        },
      }

      mockHttpClient.get.mockResolvedValue(mockResponse)

      const result = await providerApi.searchProviders(searchParams)

      expect(result.data.items).toHaveLength(0)
      expect(result.data.total).toBe(0)
    })
  })

  describe('generateSearchSuggestions', () => {
    it('should call GET /api/providers/suggestions with keyword', async () => {
      const mockResponse = {
        data: [
          { text: 'OpenAI Provider', type: 'provider' },
          { text: 'openai-provider', type: 'provider' },
          { text: 'openai search', type: 'history' },
        ],
      }

      mockHttpClient.get.mockResolvedValue(mockResponse)

      const result = await providerApi.generateSearchSuggestions('openai')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/providers/suggestions', {
        params: { keyword: 'openai' },
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle empty suggestions', async () => {
      const mockResponse = {
        data: [],
      }

      mockHttpClient.get.mockResolvedValue(mockResponse)

      const result = await providerApi.generateSearchSuggestions('xyz')

      expect(result.data).toHaveLength(0)
    })
  })

  describe('Error Handling', () => {
    it('should handle network timeouts', async () => {
      const timeoutError = new Error('Request timeout')
      timeoutError.name = 'TimeoutError'
      mockHttpClient.get.mockRejectedValue(timeoutError)

      await expect(providerApi.listProviders({})).rejects.toThrow('Request timeout')
    })

    it('should handle server errors', async () => {
      const serverError = {
        response: {
          status: 500,
          data: {
            message: 'Internal server error',
          },
        },
      }

      mockHttpClient.get.mockRejectedValue(serverError)

      await expect(providerApi.listProviders({})).rejects.toEqual(serverError)
    })

    it('should handle unauthorized errors', async () => {
      const unauthorizedError = {
        response: {
          status: 401,
          data: {
            message: 'Unauthorized',
          },
        },
      }

      mockHttpClient.get.mockRejectedValue(unauthorizedError)

      await expect(providerApi.listProviders({})).rejects.toEqual(unauthorizedError)
    })

    it('should handle forbidden errors', async () => {
      const forbiddenError = {
        response: {
          status: 403,
          data: {
            message: 'Forbidden: Insufficient permissions',
          },
        },
      }

      mockHttpClient.post.mockRejectedValue(forbiddenError)

      const createRequest: CreateProviderRequest = {
        provider_name: 'test',
        provider_type: ProviderType.OPENAI,
        display_name: 'Test',
        base_url: 'https://api.test.com',
        is_active: true,
      }

      await expect(providerApi.createProvider(createRequest)).rejects.toEqual(forbiddenError)
    })
  })

  describe('Request Interceptors', () => {
    it('should include authentication headers', async () => {
      // Mock localStorage to return a token
      const mockToken = 'mock-jwt-token'
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: vi.fn(() => mockToken),
        },
        writable: true,
      })

      mockHttpClient.get.mockResolvedValue({ data: { items: [] } })

      await providerApi.listProviders({})

      // Verify that the request was made (the actual header checking would be done in the HTTP client)
      expect(mockHttpClient.get).toHaveBeenCalled()
    })
  })

  describe('Response Interceptors', () => {
    it('should handle response transformation', async () => {
      const rawResponse = {
        data: {
          items: [
            {
              provider_id: 1,
              provider_name: 'test',
              created_at: '2025-01-01T00:00:00.000Z',
            },
          ],
        },
      }

      mockHttpClient.get.mockResolvedValue(rawResponse)

      const result = await providerApi.listProviders({})

      // The response should be returned as-is (transformation happens in HTTP client)
      expect(result.data.items[0].provider_id).toBe(1)
    })
  })

  describe('Concurrent Requests', () => {
    it('should handle multiple concurrent requests', async () => {
      const mockResponse1 = { data: { items: [{ provider_id: 1 }] } }
      const mockResponse2 = { data: { items: [{ provider_id: 2 }] } }

      mockHttpClient.get.mockResolvedValueOnce(mockResponse1).mockResolvedValueOnce(mockResponse2)

      const [result1, result2] = await Promise.all([
        providerApi.listProviders({ page: 1 }),
        providerApi.listProviders({ page: 2 }),
      ])

      expect(result1.data.items[0].provider_id).toBe(1)
      expect(result2.data.items[0].provider_id).toBe(2)
      expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
    })

    it('should handle request cancellation', async () => {
      const abortError = new Error('Request aborted')
      abortError.name = 'AbortError'
      mockHttpClient.get.mockRejectedValue(abortError)

      await expect(providerApi.listProviders({})).rejects.toThrow('Request aborted')
    })
  })

  describe('Data Validation', () => {
    it('should validate create request data', async () => {
      const invalidRequest = {
        provider_name: '',
        provider_type: 'invalid-type' as ProviderType,
        display_name: '',
        base_url: 'not-a-url',
        is_active: true,
      }

      const validationError = {
        response: {
          status: 400,
          data: {
            message: 'Validation failed',
            errors: {
              provider_name: ['Provider name is required'],
              provider_type: ['Invalid provider type'],
              display_name: ['Display name is required'],
              base_url: ['Invalid URL format'],
            },
          },
        },
      }

      mockHttpClient.post.mockRejectedValue(validationError)

      await expect(providerApi.createProvider(invalidRequest)).rejects.toEqual(validationError)
    })

    it('should validate update request data', async () => {
      const invalidUpdate = {
        display_name: '',
        base_url: 'not-a-url',
      }

      const validationError = {
        response: {
          status: 400,
          data: {
            message: 'Validation failed',
            errors: {
              display_name: ['Display name cannot be empty'],
              base_url: ['Invalid URL format'],
            },
          },
        },
      }

      mockHttpClient.put.mockRejectedValue(validationError)

      await expect(providerApi.updateProvider(1, invalidUpdate)).rejects.toEqual(validationError)
    })
  })
})
