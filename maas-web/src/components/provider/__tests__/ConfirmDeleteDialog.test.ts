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
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ConfirmDeleteDialog from '../ConfirmDeleteDialog.vue'

import type { Provider } from '@/types/providerTypes'

// Mock the composable
vi.mock('@/composables/useConfirmDelete', () => ({
  useConfirmDelete: () => ({
    deleteState: {
      loading: false,
      error: null,
      retryCount: 0,
      canRetry: true,
    },
    isDeleting: false,
    deleteError: null,
    canRetryDelete: true,
    executeDelete: vi.fn().mockResolvedValue({ success: true, message: '删除成功' }),
    retryDelete: vi.fn().mockResolvedValue({ success: true, message: '删除成功' }),
    clearDeleteError: vi.fn(),
    resetDeleteState: vi.fn(),
    checkDeletePreconditions: vi.fn().mockResolvedValue({
      canDelete: true,
      warnings: [],
      blockers: [],
    }),
    getDeleteImpact: vi.fn().mockResolvedValue({
      affectedModels: 0,
      affectedConnections: 0,
      estimatedDowntime: '无影响',
      recoverySteps: [],
    }),
    generateConfirmationMessage: vi
      .fn()
      .mockReturnValue('您即将删除供应商 "Test Provider"。此操作无法撤销，请确认您要继续。'),
  }),
}))

// Mock DialogOverlay component
vi.mock('@/components/ui/DialogOverlay.vue', () => ({
  default: {
    name: 'DialogOverlay',
    template: '<div class="dialog-overlay"><slot /></div>',
    props: [
      'modelValue',
      'closeOnOverlayClick',
      'closeOnEscape',
      'ariaLabelledby',
      'ariaDescribedby',
    ],
    emits: ['update:modelValue', 'close'],
  },
}))

describe('ConfirmDeleteDialog', () => {
  let wrapper: VueWrapper
  let pinia: ReturnType<typeof createPinia>

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
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(ConfirmDeleteDialog, {
      props: {
        modelValue: true,
        provider: mockProvider,
        ...props,
      },
      global: {
        plugins: [pinia],
      },
    })
  }

  describe('Rendering', () => {
    it('should render dialog when modelValue is true', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.confirm-delete-dialog').exists()).toBe(true)
    })

    it('should not render dialog when modelValue is false', () => {
      wrapper = createWrapper({ modelValue: false })
      expect(wrapper.find('.confirm-delete-dialog').exists()).toBe(false)
    })

    it('should display provider information', () => {
      wrapper = createWrapper()

      expect(wrapper.text()).toContain('Test Provider')
      expect(wrapper.text()).toContain('openai')
      expect(wrapper.text()).toContain('ID: 1')
    })

    it('should display provider icon placeholder when no icon available', () => {
      wrapper = createWrapper()

      const iconPlaceholder = wrapper.find('.icon-placeholder')
      expect(iconPlaceholder.exists()).toBe(true)
      expect(iconPlaceholder.text()).toBe('T') // First letter of "Test Provider"
    })

    it('should display confirmation input field', () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')
      expect(confirmationInput.exists()).toBe(true)
      expect(confirmationInput.attributes('placeholder')).toBe('test-provider')
    })

    it('should display cancel and confirm buttons', () => {
      wrapper = createWrapper()

      const cancelButton = wrapper.find('.cancel-button')
      const confirmButton = wrapper.find('.confirm-button')

      expect(cancelButton.exists()).toBe(true)
      expect(confirmButton.exists()).toBe(true)
      expect(cancelButton.text()).toBe('取消')
      expect(confirmButton.text()).toBe('确认删除')
    })
  })

  describe('Confirmation Input', () => {
    it('should validate confirmation input correctly', async () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')
      const confirmButton = wrapper.find('.confirm-button')

      // Initially disabled
      expect(confirmButton.attributes('disabled')).toBeDefined()

      // Enter wrong name
      await confirmationInput.setValue('wrong-name')
      await confirmationInput.trigger('blur')

      expect(wrapper.find('.confirmation-error').text()).toBe('输入的供应商名称不匹配')
      expect(confirmButton.attributes('disabled')).toBeDefined()

      // Enter correct name
      await confirmationInput.setValue('test-provider')
      await confirmationInput.trigger('blur')

      expect(wrapper.find('.confirmation-error').exists()).toBe(false)
      // Note: Button might still be disabled due to other conditions in the actual implementation
    })

    it('should show error when input is empty', async () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')

      await confirmationInput.setValue('')
      await confirmationInput.trigger('blur')

      expect(wrapper.find('.confirmation-error').text()).toBe('请输入供应商名称')
    })

    it('should clear error when user starts typing', async () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')

      // Trigger error first
      await confirmationInput.setValue('wrong')
      await confirmationInput.trigger('blur')
      expect(wrapper.find('.confirmation-error').exists()).toBe(true)

      // Start typing correct name
      await confirmationInput.setValue('test')
      expect(wrapper.find('.confirmation-error').exists()).toBe(false)
    })
  })

  describe('Button Actions', () => {
    it('should emit cancel when cancel button is clicked', async () => {
      wrapper = createWrapper()

      const cancelButton = wrapper.find('.cancel-button')
      await cancelButton.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should not emit confirm when confirmation is invalid', async () => {
      wrapper = createWrapper()

      const confirmButton = wrapper.find('.confirm-button')
      await confirmButton.trigger('click')

      expect(wrapper.emitted('confirm')).toBeFalsy()
    })

    it('should emit confirm when confirmation is valid', async () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')
      const confirmButton = wrapper.find('.confirm-button')

      // Enter correct confirmation
      await confirmationInput.setValue('test-provider')
      await confirmButton.trigger('click')

      // Should emit success and confirm events
      expect(wrapper.emitted('success')).toBeTruthy()
      expect(wrapper.emitted('confirm')).toBeTruthy()
    })
  })

  describe('Loading States', () => {
    it('should disable inputs and buttons when loading', () => {
      wrapper = createWrapper()

      // Mock loading state
      wrapper.vm.checkingPreconditions = true

      const confirmationInput = wrapper.find('.confirmation-input')
      const cancelButton = wrapper.find('.cancel-button')
      const confirmButton = wrapper.find('.confirm-button')

      expect(confirmationInput.attributes('disabled')).toBeDefined()
      expect(cancelButton.attributes('disabled')).toBeDefined()
      expect(confirmButton.attributes('disabled')).toBeDefined()
    })

    it('should show loading spinner when deleting', async () => {
      // Mock the composable to return loading state
      vi.doMock('@/composables/useConfirmDelete', () => ({
        useConfirmDelete: () => ({
          deleteState: {
            loading: true,
            error: null,
            retryCount: 0,
            canRetry: true,
          },
          isDeleting: true,
          deleteError: null,
          canRetryDelete: true,
          executeDelete: vi.fn(),
          retryDelete: vi.fn(),
          clearDeleteError: vi.fn(),
          resetDeleteState: vi.fn(),
          checkDeletePreconditions: vi.fn().mockResolvedValue({
            canDelete: true,
            warnings: [],
            blockers: [],
          }),
          getDeleteImpact: vi.fn().mockResolvedValue({
            affectedModels: 0,
            affectedConnections: 0,
            estimatedDowntime: '无影响',
            recoverySteps: [],
          }),
          generateConfirmationMessage: vi.fn().mockReturnValue('删除确认消息'),
        }),
      }))

      wrapper = createWrapper()

      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
      expect(wrapper.find('.confirm-button').text()).toContain('删除中...')
    })
  })

  describe('Error Handling', () => {
    it('should display error message when delete fails', async () => {
      // Mock the composable to return error state
      vi.doMock('@/composables/useConfirmDelete', () => ({
        useConfirmDelete: () => ({
          deleteState: {
            loading: false,
            error: '删除失败：供应商正在被使用',
            retryCount: 1,
            canRetry: true,
          },
          isDeleting: false,
          deleteError: '删除失败：供应商正在被使用',
          canRetryDelete: true,
          executeDelete: vi
            .fn()
            .mockResolvedValue({ success: false, error: '删除失败：供应商正在被使用' }),
          retryDelete: vi.fn(),
          clearDeleteError: vi.fn(),
          resetDeleteState: vi.fn(),
          checkDeletePreconditions: vi.fn().mockResolvedValue({
            canDelete: true,
            warnings: [],
            blockers: [],
          }),
          getDeleteImpact: vi.fn().mockResolvedValue({
            affectedModels: 0,
            affectedConnections: 0,
            estimatedDowntime: '无影响',
            recoverySteps: [],
          }),
          generateConfirmationMessage: vi.fn().mockReturnValue('删除确认消息'),
        }),
      }))

      wrapper = createWrapper()

      expect(wrapper.find('.error-section').exists()).toBe(true)
      expect(wrapper.find('.error-message').text()).toBe('删除失败：供应商正在被使用')
      expect(wrapper.find('.retry-button').exists()).toBe(true)
    })

    it('should handle retry action', async () => {
      const mockRetryDelete = vi.fn().mockResolvedValue({ success: true, message: '重试成功' })

      vi.doMock('@/composables/useConfirmDelete', () => ({
        useConfirmDelete: () => ({
          deleteState: {
            loading: false,
            error: '删除失败',
            retryCount: 1,
            canRetry: true,
          },
          isDeleting: false,
          deleteError: '删除失败',
          canRetryDelete: true,
          executeDelete: vi.fn(),
          retryDelete: mockRetryDelete,
          clearDeleteError: vi.fn(),
          resetDeleteState: vi.fn(),
          checkDeletePreconditions: vi.fn().mockResolvedValue({
            canDelete: true,
            warnings: [],
            blockers: [],
          }),
          getDeleteImpact: vi.fn().mockResolvedValue({
            affectedModels: 0,
            affectedConnections: 0,
            estimatedDowntime: '无影响',
            recoverySteps: [],
          }),
          generateConfirmationMessage: vi.fn().mockReturnValue('删除确认消息'),
        }),
      }))

      wrapper = createWrapper()

      const retryButton = wrapper.find('.retry-button')
      await retryButton.trigger('click')

      expect(mockRetryDelete).toHaveBeenCalledWith(mockProvider)
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      wrapper = createWrapper()

      const dialog = wrapper.find('[role="dialog"]')
      expect(dialog.exists()).toBe(true)
      expect(dialog.attributes('aria-modal')).toBe('true')
      expect(dialog.attributes('aria-labelledby')).toBe('delete-dialog-title')
      expect(dialog.attributes('aria-describedby')).toBe('delete-dialog-description')
    })

    it('should have proper form labels and descriptions', () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')
      expect(confirmationInput.attributes('aria-label')).toBe('确认删除输入框')
      expect(confirmationInput.attributes('aria-describedby')).toBe('confirmation-error')
    })

    it('should have proper error announcements', async () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')
      await confirmationInput.setValue('wrong')
      await confirmationInput.trigger('blur')

      const errorElement = wrapper.find('#confirmation-error')
      expect(errorElement.attributes('role')).toBe('alert')
    })
  })

  describe('Keyboard Navigation', () => {
    it('should handle Enter key to confirm', async () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')
      await confirmationInput.setValue('test-provider')
      await confirmationInput.trigger('keydown.enter')

      expect(wrapper.emitted('success')).toBeTruthy()
      expect(wrapper.emitted('confirm')).toBeTruthy()
    })

    it('should not confirm on Enter when input is invalid', async () => {
      wrapper = createWrapper()

      const confirmationInput = wrapper.find('.confirmation-input')
      await confirmationInput.setValue('wrong')
      await confirmationInput.trigger('keydown.enter')

      expect(wrapper.emitted('confirm')).toBeFalsy()
    })
  })

  describe('Props Validation', () => {
    it('should handle null provider gracefully', () => {
      wrapper = createWrapper({ provider: null })

      expect(wrapper.find('.confirm-delete-dialog').exists()).toBe(true)
      expect(wrapper.find('.provider-name').text()).toBe('')
    })

    it('should update when provider changes', async () => {
      wrapper = createWrapper()

      const newProvider: Provider = {
        ...mockProvider,
        provider_id: 2,
        provider_name: 'new-provider',
        display_name: 'New Provider',
      }

      await wrapper.setProps({ provider: newProvider })

      expect(wrapper.text()).toContain('New Provider')
      expect(wrapper.find('.confirmation-input').attributes('placeholder')).toBe('new-provider')
    })
  })
})
