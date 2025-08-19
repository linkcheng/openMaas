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

import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ProviderCard from '../ProviderCard.vue'
import type { Provider } from '@/types/providerTypes'
import { ProviderType } from '@/types/providerTypes'

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  Calendar: { name: 'Calendar' },
  User: { name: 'User' },
  View: { name: 'View' },
  Edit: { name: 'Edit' },
  Switch: { name: 'Switch' },
  Delete: { name: 'Delete' },
}))

const mockProvider: Provider = {
  provider_id: 1,
  provider_name: 'test-openai',
  provider_type: ProviderType.OPENAI,
  display_name: 'Test OpenAI',
  description: 'Test OpenAI provider',
  base_url: 'https://api.openai.com/v1',
  additional_config: {},
  is_active: true,
  created_by: 'admin',
  created_at: '2025-01-01T00:00:00Z',
  updated_by: 'admin',
  updated_at: '2025-01-01T00:00:00Z',
}

describe('ProviderCard', () => {
  it('renders provider information correctly', () => {
    const wrapper = mount(ProviderCard, {
      props: {
        provider: mockProvider,
      },
    })

    expect(wrapper.find('.provider-name').text()).toBe('Test OpenAI')
    expect(wrapper.find('.provider-type').text()).toBe('OpenAI')
    expect(wrapper.find('.provider-description').text()).toBe('Test OpenAI provider')
    expect(wrapper.find('.status-text').text()).toBe('激活')
  })

  it('shows inactive state correctly', () => {
    const inactiveProvider = { ...mockProvider, is_active: false }
    const wrapper = mount(ProviderCard, {
      props: {
        provider: inactiveProvider,
      },
    })

    expect(wrapper.find('.provider-card').classes()).toContain('inactive')
    expect(wrapper.find('.status-text').text()).toBe('停用')
    expect(wrapper.find('.status-indicator').classes()).toContain('status-inactive')
  })

  it('emits events when buttons are clicked', async () => {
    const wrapper = mount(ProviderCard, {
      props: {
        provider: mockProvider,
      },
    })

    // Test view details button
    await wrapper.find('.action-btn').trigger('click')
    expect(wrapper.emitted('view-details')).toBeTruthy()
    expect(wrapper.emitted('view-details')?.[0]).toEqual([mockProvider])

    // Test edit button
    const buttons = wrapper.findAll('.action-btn')
    await buttons[1].trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')?.[0]).toEqual([mockProvider])
  })

  it('respects permission settings', () => {
    const wrapper = mount(ProviderCard, {
      props: {
        provider: mockProvider,
        permissions: {
          canView: true,
          canEdit: false,
          canDelete: false,
          canToggleStatus: true,
        },
      },
    })

    const buttons = wrapper.findAll('.action-btn')
    // Should only show view and toggle-status buttons
    expect(buttons).toHaveLength(2)
  })

  it('disables delete button when provider is active', () => {
    const wrapper = mount(ProviderCard, {
      props: {
        provider: mockProvider,
      },
    })

    const deleteButton = wrapper
      .findAll('.action-btn')
      .find((btn) => btn.classes().includes('btn-danger'))
    expect(deleteButton?.attributes('disabled')).toBeDefined()
  })

  it('handles keyboard navigation', async () => {
    const wrapper = mount(ProviderCard, {
      props: {
        provider: mockProvider,
      },
    })

    // Test Enter key on card
    await wrapper.find('.provider-card').trigger('keydown.enter')
    expect(wrapper.emitted('view-details')).toBeTruthy()

    // Test Space key on card
    await wrapper.find('.provider-card').trigger('keydown.space')
    expect(wrapper.emitted('view-details')).toBeTruthy()
  })

  it('shows loading state correctly', () => {
    const wrapper = mount(ProviderCard, {
      props: {
        provider: mockProvider,
        loading: true,
      },
    })

    expect(wrapper.find('.provider-card').classes()).toContain('loading')

    const buttons = wrapper.findAll('.action-btn')
    buttons.forEach((button) => {
      expect(button.attributes('disabled')).toBeDefined()
    })
  })

  it('handles icon loading error gracefully', () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    const wrapper = mount(ProviderCard, {
      props: {
        provider: mockProvider,
      },
    })

    const img = wrapper.find('.provider-icon img')
    img.trigger('error')

    expect(consoleSpy).toHaveBeenCalledWith(
      `Failed to load icon for provider: ${mockProvider.provider_type}`,
    )

    consoleSpy.mockRestore()
  })

  it('displays fallback icon when image fails to load', () => {
    const wrapper = mount(ProviderCard, {
      props: {
        provider: { ...mockProvider, provider_type: 'unknown' as ProviderType },
      },
    })

    // Should show placeholder with first letter
    expect(wrapper.find('.icon-placeholder').text()).toBe('T')
  })
})
