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
import { createPinia, setActivePinia } from 'pinia'
import { useConfirmDelete } from '../useConfirmDelete'
import { useProviderStore } from '@/stores/providerStore'
import type { Provider } from '@/types/providerTypes'

// Mock the provider store
vi.mock('@/stores/providerStore', () => ({
  useProviderStore: vi.fn(() => ({
    deleteProvider: vi.fn(),
    getRelatedModels: vi.fn(),
    getProviderUsage: vi.fn(),
  })),
}))

// Mock the API error handler
vi.mock('@/utils/api', () => ({
  handleApiError: vi.fn((error) => error.message || 'API Error'),
}))

describe('useConfirmDelete', () => {
  let pinia: ReturnType<typeof createPinia>
  let mockProviderStore: any

  const mockProvider: Provider = {
    provider_id: 1,
    provider_name: 'test-provider',
    provider_type: 'openai',
    display_name: 'Test Provider',
    description: 'Test provider description',
    base_url: 'https://api.openai.com/v1',
    additional_config: {},
    is_active: true,
    created_by: 'admin',
    created_at: '2024-01-01T00:00:00Z',
    updated_by: 'admin',
    updated_at: '2024-01-01T00:00:00Z',
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    mockProviderStore = {
      deleteProvider: vi.fn().mockResolvedValue(undefined),
      getRelatedModels: vi.fn().mockResolvedValue([]),
      getProviderUsage: vi.fn().mockResolvedValue({
        activeConnections: 0,
        recentRequests: 0,
      }),
    }

    vi.mocked(useProviderStore).mockReturnValue(mockProviderStore)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with correct default state', () => {
      const { deleteState, isDeleting, deleteError, canRetryDelete } = useConfirmDelete()

      expect(deleteState.value).toEqual({
        loading: false,
        error: null,
        retryCount: 0,
        canRetry: true,
      })
      expect(isDeleting.value).toBe(false)
      expect(deleteError.value).toBe(null)
      expect(canRetryDelete.value).toBe(true)
    })
  })

  describe('executeDelete', () => {
    it('should successfully delete a provider', async () => {
      const { executeDelete } = useConfirmDelete()

      const result = await executeDelete(mockProvider)

      expect(result.success).toBe(true)
      expect(result.message).toBe('供应商 "Test Provider" 删除成功')
      expect(mockProviderStore.deleteProvider).toHaveBeenCalledWith(1)
    })

    it('should handle delete failure', async () => {
      const { executeDelete, deleteState } = useConfirmDelete()

      const error = new Error('Provider is in use')
      mockProviderStore.deleteProvider.mockRejectedValue(error)

      const result = await executeDelete(mockProvider)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Provider is in use')
      expect(deleteState.value.error).toBe('Provider is in use')
      expect(deleteState.value.retryCount).toBe(1)
    })

    it('should handle null provider', async () => {
      const { executeDelete, deleteState } = useConfirmDelete()

      const result = await executeDelete(null as any)

      expect(result.success).toBe(false)
      expect(result.error).toBe('未指定要删除的供应商')
      expect(deleteState.value.error).toBe('未指定要删除的供应商')
    })

    it('should set loading state during execution', async () => {
      const { executeDelete, isDeleting } = useConfirmDelete()

      let loadingDuringExecution = false
      mockProviderStore.deleteProvider.mockImplementation(async () => {
        loadingDuringExecution = isDeleting.value
        return Promise.resolve()
      })

      await executeDelete(mockProvider)

      expect(loadingDuringExecution).toBe(true)
      expect(isDeleting.value).toBe(false) // Should be false after completion
    })

    it('should increment retry count on failure', async () => {
      const { executeDelete, deleteState } = useConfirmDelete()

      mockProviderStore.deleteProvider.mockRejectedValue(new Error('Network error'))

      await executeDelete(mockProvider)
      expect(deleteState.value.retryCount).toBe(1)

      await executeDelete(mockProvider)
      expect(deleteState.value.retryCount).toBe(2)
    })

    it('should disable retry after max attempts', async () => {
      const { executeDelete, deleteState, canRetryDelete } = useConfirmDelete()

      mockProviderStore.deleteProvider.mockRejectedValue(new Error('Network error'))

      // Execute 3 times to reach max retries
      await executeDelete(mockProvider)
      await executeDelete(mockProvider)
      await executeDelete(mockProvider)

      expect(deleteState.value.retryCount).toBe(3)
      expect(deleteState.value.canRetry).toBe(false)
      expect(canRetryDelete.value).toBe(false)
    })
  })

  describe('retryDelete', () => {
    it('should retry delete operation', async () => {
      const { executeDelete, retryDelete, deleteState } = useConfirmDelete()

      // First attempt fails
      mockProviderStore.deleteProvider.mockRejectedValueOnce(new Error('Network error'))
      await executeDelete(mockProvider)

      expect(deleteState.value.retryCount).toBe(1)
      expect(deleteState.value.error).toBe('Network error')

      // Retry succeeds
      mockProviderStore.deleteProvider.mockResolvedValueOnce(undefined)
      const result = await retryDelete(mockProvider)

      expect(result.success).toBe(true)
      expect(mockProviderStore.deleteProvider).toHaveBeenCalledTimes(2)
    })

    it('should not retry when max retries reached', async () => {
      const { executeDelete, retryDelete, deleteState } = useConfirmDelete()

      mockProviderStore.deleteProvider.mockRejectedValue(new Error('Network error'))

      // Reach max retries
      await executeDelete(mockProvider)
      await executeDelete(mockProvider)
      await executeDelete(mockProvider)

      expect(deleteState.value.canRetry).toBe(false)

      const result = await retryDelete(mockProvider)

      expect(result.success).toBe(false)
      expect(result.error).toBe('无法重试删除操作')
    })

    it('should clear error before retrying', async () => {
      const {
        executeDelete,
        retryDelete,
        deleteState,
        clearDeleteError: _clearDeleteError,
      } = useConfirmDelete()

      // First attempt fails
      mockProviderStore.deleteProvider.mockRejectedValueOnce(new Error('Network error'))
      await executeDelete(mockProvider)

      expect(deleteState.value.error).toBe('Network error')

      // Retry should clear error first
      mockProviderStore.deleteProvider.mockResolvedValueOnce(undefined)
      await retryDelete(mockProvider)

      expect(deleteState.value.error).toBe(null)
    })
  })

  describe('checkDeletePreconditions', () => {
    it('should check preconditions successfully', async () => {
      const { checkDeletePreconditions } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockResolvedValue([])
      mockProviderStore.getProviderUsage.mockResolvedValue({
        activeConnections: 0,
        recentRequests: 0,
      })

      const result = await checkDeletePreconditions(mockProvider)

      expect(result.canDelete).toBe(true)
      expect(result.warnings).toEqual([])
      expect(result.blockers).toEqual([])
    })

    it('should detect active model blockers', async () => {
      const { checkDeletePreconditions } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockResolvedValue([
        { id: 1, name: 'Model 1', is_active: true },
        { id: 2, name: 'Model 2', is_active: false },
      ])
      mockProviderStore.getProviderUsage.mockResolvedValue({
        activeConnections: 0,
        recentRequests: 0,
      })

      const result = await checkDeletePreconditions(mockProvider)

      expect(result.canDelete).toBe(false)
      expect(result.blockers).toContain('供应商关联了 1 个激活的模型配置')
    })

    it('should detect inactive model warnings', async () => {
      const { checkDeletePreconditions } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockResolvedValue([
        { id: 1, name: 'Model 1', is_active: false },
        { id: 2, name: 'Model 2', is_active: false },
      ])
      mockProviderStore.getProviderUsage.mockResolvedValue({
        activeConnections: 0,
        recentRequests: 0,
      })

      const result = await checkDeletePreconditions(mockProvider)

      expect(result.canDelete).toBe(true)
      expect(result.warnings).toContain(
        '供应商关联了 2 个已停用的模型配置，删除后这些配置也将被移除',
      )
    })

    it('should detect active connections blocker', async () => {
      const { checkDeletePreconditions } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockResolvedValue([])
      mockProviderStore.getProviderUsage.mockResolvedValue({
        activeConnections: 5,
        recentRequests: 100,
      })

      const result = await checkDeletePreconditions(mockProvider)

      expect(result.canDelete).toBe(false)
      expect(result.blockers).toContain('供应商当前有 5 个活跃连接')
      expect(result.warnings).toContain('供应商在过去24小时内处理了 100 个请求')
    })

    it('should warn about active provider status', async () => {
      const { checkDeletePreconditions } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockResolvedValue([])
      mockProviderStore.getProviderUsage.mockResolvedValue({
        activeConnections: 0,
        recentRequests: 0,
      })

      const result = await checkDeletePreconditions(mockProvider)

      expect(result.canDelete).toBe(true)
      expect(result.warnings).toContain('供应商当前处于激活状态，建议先停用后再删除')
    })

    it('should handle API errors gracefully', async () => {
      const { checkDeletePreconditions } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockRejectedValue(new Error('API Error'))
      mockProviderStore.getProviderUsage.mockRejectedValue(new Error('API Error'))

      const result = await checkDeletePreconditions(mockProvider)

      expect(result.canDelete).toBe(true)
      expect(result.warnings).toContain('无法检查删除前置条件，请谨慎操作')
    })
  })

  describe('getDeleteImpact', () => {
    it('should calculate delete impact correctly', async () => {
      const { getDeleteImpact } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockResolvedValue([
        { id: 1, name: 'Model 1', is_active: true },
        { id: 2, name: 'Model 2', is_active: false },
      ])
      mockProviderStore.getProviderUsage.mockResolvedValue({
        activeConnections: 3,
        recentRequests: 50,
      })

      const result = await getDeleteImpact(mockProvider)

      expect(result.affectedModels).toBe(2)
      expect(result.affectedConnections).toBe(3)
      expect(result.estimatedDowntime).toBe('立即生效')
      expect(result.recoverySteps).toContain('重新配置受影响的模型')
      expect(result.recoverySteps).toContain('等待活跃连接自然结束')
      expect(result.recoverySteps).toContain('验证其他供应商配置正常')
    })

    it('should handle no impact scenario', async () => {
      const { getDeleteImpact } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockResolvedValue([])
      mockProviderStore.getProviderUsage.mockResolvedValue({
        activeConnections: 0,
        recentRequests: 0,
      })

      const result = await getDeleteImpact(mockProvider)

      expect(result.affectedModels).toBe(0)
      expect(result.affectedConnections).toBe(0)
      expect(result.estimatedDowntime).toBe('无影响')
      expect(result.recoverySteps).toEqual(['验证其他供应商配置正常'])
    })

    it('should handle API errors gracefully', async () => {
      const { getDeleteImpact } = useConfirmDelete()

      mockProviderStore.getRelatedModels.mockRejectedValue(new Error('API Error'))
      mockProviderStore.getProviderUsage.mockRejectedValue(new Error('API Error'))

      const result = await getDeleteImpact(mockProvider)

      expect(result.affectedModels).toBe(0)
      expect(result.affectedConnections).toBe(0)
      expect(result.estimatedDowntime).toBe('未知')
      expect(result.recoverySteps).toEqual(['请手动检查相关配置'])
    })
  })

  describe('formatDeleteError', () => {
    it('should format known error types', () => {
      const { formatDeleteError } = useConfirmDelete()

      expect(formatDeleteError('PROVIDER_HAS_ACTIVE_MODELS')).toBe(
        '供应商关联了激活的模型配置，请先停用相关模型后再删除',
      )
      expect(formatDeleteError('PROVIDER_IN_USE')).toBe('供应商正在被使用中，请稍后再试')
      expect(formatDeleteError('PROVIDER_NOT_FOUND')).toBe('供应商不存在或已被删除')
      expect(formatDeleteError('INSUFFICIENT_PERMISSIONS')).toBe('权限不足，无法删除供应商')
    })

    it('should format HTTP status code errors', () => {
      const { formatDeleteError } = useConfirmDelete()

      expect(formatDeleteError('404 Not Found')).toBe('供应商不存在或已被删除')
      expect(formatDeleteError('403 Forbidden')).toBe('权限不足，无法删除供应商')
      expect(formatDeleteError('409 Conflict')).toBe('供应商正在被使用，无法删除')
      expect(formatDeleteError('500 Internal Server Error')).toBe('服务器内部错误，请稍后重试')
    })

    it('should return original message for unknown errors', () => {
      const { formatDeleteError } = useConfirmDelete()

      const unknownError = 'Some unknown error message'
      expect(formatDeleteError(unknownError)).toBe(unknownError)
    })
  })

  describe('generateConfirmationMessage', () => {
    it('should generate message for active provider', () => {
      const { generateConfirmationMessage } = useConfirmDelete()

      const message = generateConfirmationMessage(mockProvider)

      expect(message).toContain('您即将删除供应商 "Test Provider"')
      expect(message).toContain('此供应商当前处于激活状态')
    })

    it('should generate message for inactive provider', () => {
      const { generateConfirmationMessage } = useConfirmDelete()

      const inactiveProvider = { ...mockProvider, is_active: false }
      const message = generateConfirmationMessage(inactiveProvider)

      expect(message).toContain('您即将删除供应商 "Test Provider"')
      expect(message).toContain('此操作无法撤销')
    })
  })

  describe('State Management', () => {
    it('should clear delete error', () => {
      const { deleteState, clearDeleteError } = useConfirmDelete()

      deleteState.value.error = 'Some error'
      clearDeleteError()

      expect(deleteState.value.error).toBe(null)
    })

    it('should reset delete state', () => {
      const { deleteState, resetDeleteState } = useConfirmDelete()

      deleteState.value.loading = true
      deleteState.value.error = 'Some error'
      deleteState.value.retryCount = 2
      deleteState.value.canRetry = false

      resetDeleteState()

      expect(deleteState.value).toEqual({
        loading: false,
        error: null,
        retryCount: 0,
        canRetry: true,
      })
    })
  })
})
