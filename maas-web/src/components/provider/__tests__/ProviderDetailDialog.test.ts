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
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ProviderDetailDialog from '../ProviderDetailDialog.vue'
import type { Provider } from '../../../types/providerTypes'
import { ProviderType } from '../../../types/providerTypes'

// Mock the user store
const mockUserStore = {
  hasPermission: vi.fn(),
  isAdmin: false,
}

vi.mock('../../../stores/userStore', () => ({
  useUserStore: () => mockUserStore,
}))

// Mock DialogOverlay component
vi.mock('../../ui/DialogOverlay.vue', () => ({
  default: {
    name: 'DialogOverlay',
    template: '<div class="dialog-overlay"><slot /></div>',
    props: ['modelValue', 'aria-labelledby', 'aria-describedby'],
    emits: ['close', 'keydown'],
  },
}))

describe('ProviderDetailDialog', () => {
  const mockProvider: Provider = {
    provider_id: 1,
    provider_name: 'test-openai',
    provider_type: ProviderType.OPENAI,
    display_name: 'Test OpenAI',
    description: 'Test OpenAI provider',
    base_url: 'https://api.openai.com/v1',
    additional_config: {
      api_key: 'sk-test123456789',
      timeout: 30,
      max_retries: 3,
    },
    is_active: true,
    created_by: 'admin',
    created_at: '2024-01-01T00:00:00Z',
    updated_by: 'admin',
    updated_at: '2024-01-01T00:00:00Z',
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    // Default permissions
    mockUserStore.hasPermission.mockReturnValue(true)
    mockUserStore.isAdmin = false
  })

  it('should render provider information correctly', () => {
    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    expect(wrapper.text()).toContain('Test OpenAI')
    expect(wrapper.text()).toContain('test-openai')
    expect(wrapper.text()).toContain('OpenAI')
    expect(wrapper.text()).toContain('https://api.openai.com/v1')
    expect(wrapper.text()).toContain('Test OpenAI provider')
  })

  it('should show status badge correctly', () => {
    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    const statusBadge = wrapper.find('.status-badge')
    expect(statusBadge.classes()).toContain('status-active')
    expect(statusBadge.text()).toContain('激活')
  })

  it('should mask sensitive information by default', () => {
    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    // Should show masked API key
    expect(wrapper.text()).toContain('sk-t************')
    expect(wrapper.text()).not.toContain('sk-test123456789')
  })

  it('should show sensitive information when user has permission and toggles visibility', async () => {
    mockUserStore.hasPermission.mockImplementation((resource: string, action: string) => {
      return resource === 'provider' && action === 'view_sensitive'
    })

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    // Find and click the toggle button for API key
    const toggleButton = wrapper.find('.toggle-sensitive-button')
    await toggleButton.trigger('click')

    // Should show actual API key
    expect(wrapper.text()).toContain('sk-test123456789')
  })

  it('should hide sensitive information when user lacks permission', () => {
    mockUserStore.hasPermission.mockReturnValue(false)

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    // Should show permission denied message
    expect(wrapper.find('.permission-denied').exists()).toBe(true)
    expect(wrapper.find('.toggle-sensitive-button').exists()).toBe(false)
  })

  it('should show action buttons when user has permissions', () => {
    mockUserStore.hasPermission.mockReturnValue(true)

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    expect(wrapper.find('.edit-button').exists()).toBe(true)
    expect(wrapper.find('.toggle-button').exists()).toBe(true)
    expect(wrapper.find('.delete-button').exists()).toBe(true)
  })

  it('should hide action buttons when user lacks permissions', () => {
    mockUserStore.hasPermission.mockReturnValue(false)

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    expect(wrapper.find('.edit-button').exists()).toBe(false)
    expect(wrapper.find('.toggle-button').exists()).toBe(false)
    expect(wrapper.find('.delete-button').exists()).toBe(false)
  })

  it('should emit edit event when edit button is clicked', async () => {
    mockUserStore.hasPermission.mockReturnValue(true)

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    await wrapper.find('.edit-button').trigger('click')

    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')?.[0]).toEqual([mockProvider])
  })

  it('should emit delete event when delete button is clicked', async () => {
    mockUserStore.hasPermission.mockReturnValue(true)

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    await wrapper.find('.delete-button').trigger('click')

    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')?.[0]).toEqual([mockProvider])
  })

  it('should emit toggle-status event when toggle button is clicked', async () => {
    mockUserStore.hasPermission.mockReturnValue(true)

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    await wrapper.find('.toggle-button').trigger('click')

    expect(wrapper.emitted('toggle-status')).toBeTruthy()
    expect(wrapper.emitted('toggle-status')?.[0]).toEqual([mockProvider])
  })

  it('should show loading state on buttons', async () => {
    mockUserStore.hasPermission.mockReturnValue(true)

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
        loading: true,
      },
    })

    const editButton = wrapper.find('.edit-button')
    const deleteButton = wrapper.find('.delete-button')
    const toggleButton = wrapper.find('.toggle-button')

    expect(editButton.attributes('disabled')).toBeDefined()
    expect(deleteButton.attributes('disabled')).toBeDefined()
    expect(toggleButton.attributes('disabled')).toBeDefined()
  })

  it('should format configuration values correctly', () => {
    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    // Should show timeout and max_retries as normal values
    expect(wrapper.text()).toContain('30')
    expect(wrapper.text()).toContain('3')
  })

  it('should format date and time correctly', () => {
    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    // Should format the date in Chinese locale
    expect(wrapper.text()).toContain('2024')
    expect(wrapper.text()).toContain('01')
  })

  it('should emit close event when close button is clicked', async () => {
    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: mockProvider,
        modelValue: true,
      },
    })

    await wrapper.find('.close-button').trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should handle providers without additional config', () => {
    const providerWithoutConfig = {
      ...mockProvider,
      additional_config: undefined,
    }

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: providerWithoutConfig,
        modelValue: true,
      },
    })

    // Should not show configuration section
    expect(wrapper.find('.config-container').exists()).toBe(false)
  })

  it('should handle providers without description', () => {
    const providerWithoutDescription = {
      ...mockProvider,
      description: undefined,
    }

    const wrapper = mount(ProviderDetailDialog, {
      props: {
        provider: providerWithoutDescription,
        modelValue: true,
      },
    })

    // Should not show description field
    expect(wrapper.text()).not.toContain('Test OpenAI provider')
  })
})
