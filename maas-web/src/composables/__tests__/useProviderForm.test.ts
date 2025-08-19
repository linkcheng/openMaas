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

import { useProviderForm } from '../useProviderForm'
import type { Provider, ProviderType } from '@/types/providerTypes'

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

describe('useProviderForm', () => {
  const mockProvider: Provider = {
    provider_id: 1,
    provider_name: 'test-provider',
    provider_type: 'openai',
    display_name: 'Test Provider',
    description: 'Test description',
    base_url: 'https://api.openai.com/v1',
    additional_config: { timeout: 30 },
    is_active: true,
    created_by: 'test-user',
    created_at: '2025-01-01T00:00:00Z',
    updated_by: 'test-user',
    updated_at: '2025-01-01T00:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Form Initialization', () => {
    it('should initialize with default values for create mode', () => {
      const { form, isEditMode, formState } = useProviderForm()

      expect(isEditMode.value).toBe(false)
      expect(form.provider_name).toBe('')
      expect(form.provider_type).toBe('')
      expect(form.display_name).toBe('')
      expect(form.description).toBe('')
      expect(form.base_url).toBe('')
      expect(form.api_key).toBe('')
      expect(form.additional_config).toEqual({})
      expect(form.is_active).toBe(true)
      expect(formState.isDirty).toBe(false)
      expect(formState.isTouched).toBe(false)
    })

    it('should initialize with provider data for edit mode', () => {
      const { form, isEditMode, additionalConfigText } = useProviderForm(mockProvider)

      expect(isEditMode.value).toBe(true)
      expect(form.provider_name).toBe(mockProvider.provider_name)
      expect(form.provider_type).toBe(mockProvider.provider_type)
      expect(form.display_name).toBe(mockProvider.display_name)
      expect(form.description).toBe(mockProvider.description)
      expect(form.base_url).toBe(mockProvider.base_url)
      expect(form.api_key).toBe('') // Should be empty in edit mode
      expect(form.additional_config).toEqual(mockProvider.additional_config)
      expect(form.is_active).toBe(mockProvider.is_active)
      expect(additionalConfigText.value).toBe(
        JSON.stringify(mockProvider.additional_config, null, 2),
      )
    })
  })

  describe('Form Validation', () => {
    it('should validate required fields', () => {
      const { validateField, errors } = useProviderForm()

      // Test provider_name validation
      expect(validateField('provider_name')).toBe(false)
      expect(errors.provider_name).toBeTruthy()

      // Test display_name validation
      expect(validateField('display_name')).toBe(false)
      expect(errors.display_name).toBeTruthy()

      // Test provider_type validation
      expect(validateField('provider_type')).toBe(false)
      expect(errors.provider_type).toBeTruthy()

      // Test base_url validation
      expect(validateField('base_url')).toBe(false)
      expect(errors.base_url).toBeTruthy()
    })

    it('should validate field formats', () => {
      const { form, validateField, errors } = useProviderForm()

      // Test invalid provider_name format
      form.provider_name = 'invalid name with spaces'
      expect(validateField('provider_name')).toBe(false)
      expect(errors.provider_name).toContain('只能包含字母、数字、下划线和连字符')

      // Test valid provider_name format
      form.provider_name = 'valid-provider_name123'
      expect(validateField('provider_name')).toBe(true)
      expect(errors.provider_name).toBe('')

      // Test invalid base_url format
      form.base_url = 'not-a-url'
      expect(validateField('base_url')).toBe(false)
      expect(errors.base_url).toContain('请输入有效的URL地址')

      // Test valid base_url format
      form.base_url = 'https://api.example.com/v1'
      expect(validateField('base_url')).toBe(true)
      expect(errors.base_url).toBe('')
    })

    it('should validate field lengths', () => {
      const { form, validateField, errors } = useProviderForm()

      // Test provider_name length limits
      form.provider_name = 'a'.repeat(65) // Too long
      expect(validateField('provider_name')).toBe(false)
      expect(errors.provider_name).toContain('长度应在1-64个字符之间')

      form.provider_name = 'valid-name'
      expect(validateField('provider_name')).toBe(true)
      expect(errors.provider_name).toBe('')

      // Test description length limit
      form.description = 'a'.repeat(1001) // Too long
      expect(validateField('description')).toBe(false)
      expect(errors.description).toContain('长度不能超过1000个字符')

      form.description = 'Valid description'
      expect(validateField('description')).toBe(true)
      expect(errors.description).toBe('')
    })

    it('should validate all fields at once', () => {
      const { form, validateAllFields } = useProviderForm()

      // Test with empty form
      const result1 = validateAllFields()
      expect(result1.isValid).toBe(false)
      expect(Object.keys(result1.errors).length).toBeGreaterThan(0)

      // Test with valid form
      form.provider_name = 'test-provider'
      form.provider_type = 'openai' as ProviderType
      form.display_name = 'Test Provider'
      form.base_url = 'https://api.openai.com/v1'
      form.api_key = 'test-key'

      const result2 = validateAllFields()
      expect(result2.isValid).toBe(true)
      expect(Object.keys(result2.errors).length).toBe(0)
    })
  })

  describe('Additional Config Validation', () => {
    it('should validate JSON format', () => {
      const { additionalConfigText, validateAdditionalConfig, additionalConfigError } =
        useProviderForm()

      // Test invalid JSON
      additionalConfigText.value = '{ invalid json }'
      expect(validateAdditionalConfig()).toBe(false)
      expect(additionalConfigError.value).toBe('请输入有效的JSON格式')

      // Test valid JSON
      additionalConfigText.value = '{"timeout": 30, "retries": 3}'
      expect(validateAdditionalConfig()).toBe(true)
      expect(additionalConfigError.value).toBe('')

      // Test empty string (should be valid)
      additionalConfigText.value = ''
      expect(validateAdditionalConfig()).toBe(true)
      expect(additionalConfigError.value).toBe('')
    })

    it('should validate JSON object type', () => {
      const { additionalConfigText, validateAdditionalConfig, additionalConfigError } =
        useProviderForm()

      // Test array (should be invalid)
      additionalConfigText.value = '[1, 2, 3]'
      expect(validateAdditionalConfig()).toBe(false)
      expect(additionalConfigError.value).toBe('额外配置必须是有效的JSON对象')

      // Test primitive value (should be invalid)
      additionalConfigText.value = '"string value"'
      expect(validateAdditionalConfig()).toBe(false)
      expect(additionalConfigError.value).toBe('额外配置必须是有效的JSON对象')

      // Test null (should be invalid)
      additionalConfigText.value = 'null'
      expect(validateAdditionalConfig()).toBe(false)
      expect(additionalConfigError.value).toBe('额外配置必须是有效的JSON对象')

      // Test valid object
      additionalConfigText.value = '{"key": "value"}'
      expect(validateAdditionalConfig()).toBe(true)
      expect(additionalConfigError.value).toBe('')
    })

    it('should format JSON correctly', () => {
      const { additionalConfigText, formatAdditionalConfig } = useProviderForm()

      // Test formatting compact JSON
      additionalConfigText.value = '{"timeout":30,"retries":3}'
      formatAdditionalConfig()
      expect(additionalConfigText.value).toBe('{\n  "timeout": 30,\n  "retries": 3\n}')

      // Test with invalid JSON (should remain unchanged)
      additionalConfigText.value = '{ invalid }'
      const original = additionalConfigText.value
      formatAdditionalConfig()
      expect(additionalConfigText.value).toBe(original)
    })
  })

  describe('Form State Management', () => {
    it('should track form validity', () => {
      const { form, isFormValid } = useProviderForm()

      // Initially invalid
      expect(isFormValid.value).toBe(false)

      // Fill required fields
      form.provider_name = 'test-provider'
      form.provider_type = 'openai' as ProviderType
      form.display_name = 'Test Provider'
      form.base_url = 'https://api.openai.com/v1'

      // Should be valid now
      expect(isFormValid.value).toBe(true)
    })

    it('should track form changes in edit mode', () => {
      const { form, hasFormChanges } = useProviderForm(mockProvider)

      // Initially no changes
      expect(hasFormChanges.value).toBe(false)

      // Make a change
      form.display_name = 'Modified Name'
      expect(hasFormChanges.value).toBe(true)

      // Revert change
      form.display_name = mockProvider.display_name
      expect(hasFormChanges.value).toBe(false)
    })

    it('should track touched fields', () => {
      const { touchField, touchedFields, formState } = useProviderForm()

      expect(formState.isTouched).toBe(false)
      expect(touchedFields.provider_name).toBe(false)

      touchField('provider_name')

      expect(formState.isTouched).toBe(true)
      expect(touchedFields.provider_name).toBe(true)
    })

    it('should handle field changes', () => {
      const { form, handleFieldChange, formState, touchedFields } = useProviderForm()

      handleFieldChange('provider_name', 'new-name')

      expect(form.provider_name).toBe('new-name')
      expect(formState.isDirty).toBe(true)
      expect(touchedFields.provider_name).toBe(true)
    })

    it('should handle field blur', () => {
      const { form, handleFieldBlur, touchedFields, errors } = useProviderForm()

      // Set invalid value
      form.provider_name = ''
      handleFieldBlur('provider_name')

      expect(touchedFields.provider_name).toBe(true)
      expect(errors.provider_name).toBeTruthy()
    })
  })

  describe('Provider Type Handling', () => {
    it('should handle provider type changes', () => {
      const { form, handleProviderTypeChange, additionalConfigText } = useProviderForm()

      handleProviderTypeChange('openai' as ProviderType)

      expect(form.provider_type).toBe('openai')
      // Should apply default config for OpenAI
      expect(additionalConfigText.value).toBeTruthy()
    })

    it('should get current template for provider type', () => {
      const { form, currentTemplate } = useProviderForm()

      // No template for empty type
      expect(currentTemplate.value).toBe(null)

      form.provider_type = 'openai' as ProviderType
      expect(currentTemplate.value).toBeTruthy()
      expect(currentTemplate.value?.provider_type).toBe('openai')
    })

    it('should determine required fields based on provider type', () => {
      const { form, requiredFields } = useProviderForm()

      // Base required fields
      expect(requiredFields.value).toContain('provider_name')
      expect(requiredFields.value).toContain('provider_type')
      expect(requiredFields.value).toContain('display_name')
      expect(requiredFields.value).toContain('base_url')

      // API key should be required for create mode with certain provider types
      form.provider_type = 'openai' as ProviderType
      expect(requiredFields.value).toContain('api_key')
    })
  })

  describe('Form Submission', () => {
    it('should submit valid form data', async () => {
      const { form, submitForm } = useProviderForm()

      // Fill valid form data
      form.provider_name = 'test-provider'
      form.provider_type = 'openai' as ProviderType
      form.display_name = 'Test Provider'
      form.base_url = 'https://api.openai.com/v1'
      form.api_key = 'test-key'

      const result = await submitForm()

      expect(result).toBeTruthy()
      expect(result?.provider_name).toBe('test-provider')
      expect(result?.provider_type).toBe('openai')
    })

    it('should not submit invalid form data', async () => {
      const { submitForm } = useProviderForm()

      // Empty form should not submit
      const result = await submitForm()

      expect(result).toBe(null)
    })

    it('should exclude empty api_key in edit mode', async () => {
      const { form, submitForm } = useProviderForm(mockProvider)

      // Fill required fields but leave api_key empty
      form.display_name = 'Modified Name'

      const result = await submitForm()

      expect(result).toBeTruthy()
      expect(result).not.toHaveProperty('api_key')
    })

    it('should get form data correctly', () => {
      const { form, getFormData } = useProviderForm()

      form.provider_name = 'test-provider'
      form.provider_type = 'openai' as ProviderType
      form.display_name = 'Test Provider'
      form.base_url = 'https://api.openai.com/v1'
      form.api_key = 'test-key'

      const data = getFormData()

      expect(data.provider_name).toBe('test-provider')
      expect(data.provider_type).toBe('openai')
      expect(data.display_name).toBe('Test Provider')
      expect(data.base_url).toBe('https://api.openai.com/v1')
      expect(data.api_key).toBe('test-key')
    })
  })

  describe('Form Reset', () => {
    it('should reset form to default values', () => {
      const { form, formState, touchedFields, errors, resetForm } = useProviderForm()

      // Modify form
      form.provider_name = 'test'
      formState.isDirty = true
      touchedFields.provider_name = true
      errors.provider_name = 'error'

      resetForm()

      expect(form.provider_name).toBe('')
      expect(form.provider_type).toBe('')
      expect(form.is_active).toBe(true)
      expect(formState.isDirty).toBe(false)
      expect(touchedFields.provider_name).toBe(false)
      expect(errors.provider_name).toBe('')
    })
  })

  describe('Helper Methods', () => {
    it('should check field errors correctly', () => {
      const { hasFieldError, getFieldError, touchField, errors } = useProviderForm()

      errors.provider_name = 'Test error'

      // Should not show error if field not touched
      expect(hasFieldError('provider_name')).toBe(false)
      expect(getFieldError('provider_name')).toBe('')

      // Should show error after field is touched
      touchField('provider_name')
      expect(hasFieldError('provider_name')).toBe(true)
      expect(getFieldError('provider_name')).toBe('Test error')
    })

    it('should check if field is required', () => {
      const { form, isFieldRequired } = useProviderForm()

      expect(isFieldRequired('provider_name')).toBe(true)
      expect(isFieldRequired('description')).toBe(false)

      // API key requirement depends on mode and provider type
      form.provider_type = 'openai' as ProviderType
      expect(isFieldRequired('api_key')).toBe(true)
    })

    it('should provide field hints', () => {
      const { getFieldHint } = useProviderForm()

      expect(getFieldHint('provider_name')).toContain('唯一标识符')
      expect(getFieldHint('display_name')).toContain('显示名称')
      expect(getFieldHint('base_url')).toContain('基础URL')
      expect(getFieldHint('api_key')).toContain('访问密钥')
    })

    it('should provide auto-fill suggestions', () => {
      const { form, getAutoFillSuggestions } = useProviderForm()

      form.provider_type = 'openai' as ProviderType
      const suggestions = getAutoFillSuggestions('base_url')

      expect(suggestions).toContain('https://api.openai.com/v1')
    })

    it('should apply auto-fill correctly', () => {
      const { form, applyAutoFill } = useProviderForm()

      applyAutoFill('base_url', 'https://api.openai.com/v1')

      expect(form.base_url).toBe('https://api.openai.com/v1')
    })
  })

  describe('Edge Cases and Error Scenarios', () => {
    it('should handle malformed additional config gracefully', () => {
      const { additionalConfigText, form, getFormData } = useProviderForm()

      // Set malformed JSON
      additionalConfigText.value = '{ malformed }'
      form.additional_config = { existing: 'config' }

      const data = getFormData()

      // Should use existing form config when JSON parsing fails
      expect(data.additional_config).toEqual({ existing: 'config' })
    })

    it('should handle provider type change with existing config', () => {
      const { form, handleProviderTypeChange, additionalConfigText } = useProviderForm()

      // Set initial config
      form.additional_config = { existing: 'config' }
      additionalConfigText.value = '{"existing": "config"}'

      // Change provider type
      handleProviderTypeChange('anthropic' as ProviderType)

      expect(form.provider_type).toBe('anthropic')
      // Config should be reset to default for new provider type
      expect(form.additional_config).not.toEqual({ existing: 'config' })
    })

    it('should handle validation with special characters', () => {
      const { form, validateField, errors } = useProviderForm()

      // Test provider name with special characters
      form.provider_name = 'test@provider#'
      expect(validateField('provider_name')).toBe(false)
      expect(errors.provider_name).toBeTruthy()

      // Test with allowed characters
      form.provider_name = 'test-provider_123'
      expect(validateField('provider_name')).toBe(true)
      expect(errors.provider_name).toBe('')
    })

    it('should handle empty and whitespace values', () => {
      const { form, validateField, errors } = useProviderForm()

      // Test with whitespace-only value
      form.provider_name = '   '
      expect(validateField('provider_name')).toBe(false)
      expect(errors.provider_name).toBeTruthy()

      // Test with valid value after whitespace
      form.provider_name = 'valid-name'
      expect(validateField('provider_name')).toBe(true)
      expect(errors.provider_name).toBe('')
    })
  })
})
