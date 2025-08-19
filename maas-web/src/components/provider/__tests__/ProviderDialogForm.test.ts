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
import ProviderDialogForm from '../ProviderDialogForm.vue'
import type { Provider } from '@/types/providerTypes'
import { ProviderType } from '@/types/providerTypes'

// Mock the composables
vi.mock('@/composables/useProviderForm', () => ({
  useProviderForm: () => ({
    form: {
      provider_name: '',
      provider_type: '',
      display_name: '',
      description: '',
      base_url: '',
      api_key: '',
      additional_config: {},
      is_active: true,
    },
    formState: {
      isDirty: false,
      isTouched: false,
      isSubmitting: false,
      hasChanges: false,
    },
    errors: {},
    additionalConfigText: '',
    additionalConfigError: '',
    isEditMode: false,
    isFormValid: false,
    hasFormChanges: false,
    canSubmit: false,
    handleFieldChange: vi.fn(),
    handleFieldBlur: vi.fn(),
    handleProviderTypeChange: vi.fn(),
    validateAdditionalConfig: vi.fn(),
    formatAdditionalConfig: vi.fn(),
    getFieldError: vi.fn(() => ''),
    hasFieldError: vi.fn(() => false),
    isFieldRequired: vi.fn(() => false),
    getFieldHint: vi.fn(() => ''),
    getAutoFillSuggestions: vi.fn(() => []),
    applyAutoFill: vi.fn(),
    submitForm: vi.fn(),
    resetForm: vi.fn(),
    initializeForm: vi.fn(),
  }),
}))

describe('ProviderDialogForm', () => {
  const mockProvider: Provider = {
    provider_id: 1,
    provider_name: 'test-provider',
    provider_type: ProviderType.OPENAI,
    display_name: 'Test Provider',
    description: 'Test description',
    base_url: 'https://api.test.com/v1',
    additional_config: { timeout: 30 },
    is_active: true,
    created_by: 'admin',
    created_at: '2025-01-01T00:00:00Z',
    updated_by: 'admin',
    updated_at: '2025-01-01T00:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders create mode dialog correctly', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    expect(wrapper.find('.dialog-title').text()).toBe('创建供应商')
    expect(wrapper.find('.dialog-description').text()).toBe('添加新的AI模型供应商')
  })

  it('renders edit mode dialog correctly', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        provider: mockProvider,
        mode: 'edit',
      },
    })

    expect(wrapper.find('.dialog-title').text()).toBe('编辑供应商')
    expect(wrapper.find('.dialog-description').text()).toBe('修改供应商配置信息')
  })

  it('renders all form sections', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    const sections = wrapper.findAll('.form-section')
    expect(sections).toHaveLength(3)

    const sectionTitles = sections.map((section) => section.find('.section-title').text())
    expect(sectionTitles).toEqual(['基本信息', '认证配置', '其他配置'])
  })

  it('renders all required form fields', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    // Check for all form fields
    expect(wrapper.find('#provider-name').exists()).toBe(true)
    expect(wrapper.find('#display-name').exists()).toBe(true)
    expect(wrapper.find('#provider-type').exists()).toBe(true)
    expect(wrapper.find('#base-url').exists()).toBe(true)
    expect(wrapper.find('#api-key').exists()).toBe(true)
    expect(wrapper.find('#description').exists()).toBe(true)
    expect(wrapper.find('#additional-config').exists()).toBe(true)
    expect(wrapper.find('#is-active').exists()).toBe(true)
  })

  it('renders provider type options', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    const select = wrapper.find('#provider-type')
    const options = select.findAll('option')

    // Should have placeholder + provider type options
    expect(options.length).toBeGreaterThan(1)
    expect(options[0].text()).toBe('请选择供应商类型')
  })

  it('shows password toggle for API key field', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    const passwordToggle = wrapper.find('.password-toggle-btn')
    expect(passwordToggle.exists()).toBe(true)
  })

  it('shows JSON format button for additional config', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    const formatBtn = wrapper.find('.format-btn')
    expect(formatBtn.exists()).toBe(true)
    expect(formatBtn.text()).toContain('格式化')
  })

  it('renders footer buttons correctly', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    const buttons = wrapper.findAll('.footer-actions .btn')
    expect(buttons).toHaveLength(3)

    const buttonTexts = buttons.map((btn) => btn.text())
    expect(buttonTexts).toEqual(['取消', '重置', '创建'])
  })

  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    const cancelBtn = wrapper.find('.btn-secondary')
    await cancelBtn.trigger('click')

    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('emits close event when close button is clicked', async () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        mode: 'create',
      },
    })

    const closeBtn = wrapper.find('.dialog-close-btn')
    await closeBtn.trigger('click')

    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('does not render when modelValue is false', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: false,
        mode: 'create',
      },
    })

    expect(wrapper.find('.provider-dialog-form').exists()).toBe(false)
  })

  it('disables provider name field in edit mode', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        provider: mockProvider,
        mode: 'edit',
      },
    })

    const providerNameInput = wrapper.find('#provider-name')
    expect(providerNameInput.attributes('disabled')).toBeDefined()
  })

  it('shows different button text for edit mode', () => {
    const wrapper = mount(ProviderDialogForm, {
      props: {
        modelValue: true,
        provider: mockProvider,
        mode: 'edit',
      },
    })

    const submitBtn = wrapper.find('.btn-primary')
    expect(submitBtn.text()).toContain('更新')
  })
})
