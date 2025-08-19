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
import { useProviderManagement } from '../useProviderManagement'

import type { Provider } from '@/types/providerTypes'

// Mock the store
vi.mock('@/stores/providerStore')
vi.mock('pinia', () => ({
  storeToRefs: vi.fn(() => ({
    providers: { value: [] },
    loading: { value: false },
    error: { value: null },
    pagination: { value: { page: 1, size: 20, total: 0, pages: 0 } },
    totalPages: { value: 0 },
    currentPage: { value: 1 },
    totalProviders: { value: 0 },
    hasProviders: { value: false },
  })),
}))

// Mock Vue composition functions
vi.mock('vue', async () => {
  const actual = await vi.importActual('vue')
  return {
    ...actual,
    onMounted: vi.fn((fn) => fn()),
    watch: vi.fn(),
    nextTick: vi.fn(() => Promise.resolve()),
  }
})

describe('useProviderManagement', () => {
  const mockProvider: Provider = {
    provider_id: 1,
    provider_name: 'test-provider',
    provider_type: 'openai',
    display_name: 'Test Provider',
    description: 'Test description',
    base_url: 'https://api.test.com',
    additional_config: {},
    is_active: true,
    created_by: 'test-user',
    created_at: '2025-01-01T00:00:00Z',
    updated_by: 'test-user',
    updated_at: '2025-01-01T00:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with default state', () => {
    const {
      showFormDialog,
      showDetailDialog,
      showDeleteDialog,
      selectedProvider,
      dialogMode,
      operationLoading,
      isEditMode,
      isCreateMode,
    } = useProviderManagement()

    expect(showFormDialog.value).toBe(false)
    expect(showDetailDialog.value).toBe(false)
    expect(showDeleteDialog.value).toBe(false)
    expect(selectedProvider.value).toBe(null)
    expect(dialogMode.value).toBe('create')
    expect(operationLoading.value).toBe(false)
    expect(isEditMode.value).toBe(false)
    expect(isCreateMode.value).toBe(true)
  })

  it('should open create dialog correctly', () => {
    const { openCreateDialog, showFormDialog, dialogMode, selectedProvider } =
      useProviderManagement()

    openCreateDialog()

    expect(showFormDialog.value).toBe(true)
    expect(dialogMode.value).toBe('create')
    expect(selectedProvider.value).toBe(null)
  })

  it('should open edit dialog correctly', () => {
    const { openEditDialog, showFormDialog, dialogMode, selectedProvider } = useProviderManagement()

    openEditDialog(mockProvider)

    expect(showFormDialog.value).toBe(true)
    expect(dialogMode.value).toBe('edit')
    expect(selectedProvider.value).toBe(mockProvider)
  })

  it('should open detail dialog correctly', () => {
    const { openDetailDialog, showDetailDialog, selectedProvider } = useProviderManagement()

    openDetailDialog(mockProvider)

    expect(showDetailDialog.value).toBe(true)
    expect(selectedProvider.value).toBe(mockProvider)
  })

  it('should open delete dialog correctly', () => {
    const { openDeleteDialog, showDeleteDialog, dialogMode, selectedProvider } =
      useProviderManagement()

    openDeleteDialog(mockProvider)

    expect(showDeleteDialog.value).toBe(true)
    expect(dialogMode.value).toBe('delete')
    expect(selectedProvider.value).toBe(mockProvider)
  })

  it('should close dialogs correctly', () => {
    const {
      openEditDialog,
      closeFormDialog,
      showFormDialog,
      selectedProvider: _selectedProvider,
      dialogMode,
    } = useProviderManagement()

    // Open dialog first
    openEditDialog(mockProvider)
    expect(showFormDialog.value).toBe(true)

    // Close dialog
    closeFormDialog()
    expect(showFormDialog.value).toBe(false)
    expect(dialogMode.value).toBe('create')
  })

  it('should show success feedback', () => {
    const { showSuccess, userFeedback } = useProviderManagement()

    showSuccess('Test success message')

    expect(userFeedback.value).toEqual({
      type: 'success',
      message: 'Test success message',
    })
  })

  it('should show error feedback', () => {
    const { showError, userFeedback } = useProviderManagement()

    showError('Test error message')

    expect(userFeedback.value).toEqual({
      type: 'error',
      message: 'Test error message',
    })
  })

  it('should clear feedback', () => {
    const { showSuccess, clearFeedback, userFeedback } = useProviderManagement()

    showSuccess('Test message')
    expect(userFeedback.value).toBeTruthy()

    clearFeedback()
    expect(userFeedback.value).toBe(null)
  })
})
