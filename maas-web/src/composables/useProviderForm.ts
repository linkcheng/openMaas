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

import { ref, reactive, computed, watch, onMounted } from 'vue'
import type {
  Provider,
  ProviderFormData,
  FormErrors,
  ValidationRule,
  ProviderType,
  CreateProviderRequest,
  UpdateProviderRequest,
  ProviderConfigTemplate,
} from '@/types/providerTypes'
import { PROVIDER_VALIDATION_RULES, PROVIDER_CONFIG_TEMPLATES } from '@/types/providerTypes'

// 表单字段类型
export type FormField = keyof ProviderFormData

// 验证结果类型
export interface ValidationResult {
  isValid: boolean
  errors: FormErrors
}

// 表单状态类型
export interface FormState {
  isDirty: boolean
  isTouched: boolean
  isSubmitting: boolean
  hasChanges: boolean
}

export function useProviderForm(initialProvider?: Provider) {
  // 表单数据
  const form = reactive<ProviderFormData>({
    provider_name: '',
    provider_type: '' as ProviderType,
    display_name: '',
    description: '',
    base_url: '',
    api_key: '',
    additional_config: {},
    is_active: true,
  })

  // 原始表单数据（用于检测变化）
  const originalForm = ref<ProviderFormData | null>(null)

  // 表单错误
  const errors = reactive<FormErrors>({})

  // 表单状态
  const formState = reactive<FormState>({
    isDirty: false,
    isTouched: false,
    isSubmitting: false,
    hasChanges: false,
  })

  // 字段触摸状态
  const touchedFields = reactive<Record<FormField, boolean>>({
    provider_name: false,
    provider_type: false,
    display_name: false,
    description: false,
    base_url: false,
    api_key: false,
    additional_config: false,
    is_active: false,
  })

  // 额外配置JSON文本
  const additionalConfigText = ref('')
  const additionalConfigError = ref('')

  // 是否为编辑模式
  const isEditMode = computed(() => !!initialProvider)

  // 当前供应商类型的配置模板
  const currentTemplate = computed((): ProviderConfigTemplate | null => {
    if (!form.provider_type) return null
    return PROVIDER_CONFIG_TEMPLATES[form.provider_type as ProviderType] || null
  })

  // 必填字段列表
  const requiredFields = computed((): FormField[] => {
    const baseRequired: FormField[] = ['provider_name', 'provider_type', 'display_name', 'base_url']

    if (currentTemplate.value) {
      // 根据供应商类型添加额外的必填字段
      const templateRequired = currentTemplate.value.required_fields
      if (templateRequired.includes('api_key') && !isEditMode.value) {
        baseRequired.push('api_key')
      }
    }

    return baseRequired
  })

  // 表单验证状态
  const isFormValid = computed(() => {
    // 检查是否有错误
    const hasErrors = Object.values(errors).some((error) => !!error)
    if (hasErrors) return false

    // 检查必填字段
    for (const field of requiredFields.value) {
      const value = form[field]
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        return false
      }
    }

    // 检查额外配置JSON格式
    if (additionalConfigError.value) {
      return false
    }

    return true
  })

  // 表单是否有变化
  const hasFormChanges = computed(() => {
    if (!originalForm.value) return false

    return Object.keys(form).some((key) => {
      const formKey = key as FormField
      const currentValue = form[formKey]
      const originalValue = originalForm.value![formKey]

      // 特殊处理对象类型
      if (formKey === 'additional_config') {
        return JSON.stringify(currentValue) !== JSON.stringify(originalValue)
      }

      return currentValue !== originalValue
    })
  })

  // 表单是否可以提交
  const canSubmit = computed(() => {
    return (
      isFormValid.value &&
      !formState.isSubmitting &&
      (isEditMode.value ? hasFormChanges.value : true)
    )
  })

  // 获取字段验证规则
  const getFieldRules = (fieldName: FormField): ValidationRule[] => {
    const rules =
      PROVIDER_VALIDATION_RULES[fieldName as keyof typeof PROVIDER_VALIDATION_RULES] || []

    // 如果是编辑模式，API密钥不是必填的
    if (fieldName === 'api_key' && isEditMode.value) {
      return rules.filter((rule) => !rule.required)
    }

    // 根据供应商类型添加额外验证规则
    if (currentTemplate.value && currentTemplate.value.validation_schema[fieldName]) {
      return [...rules, ...currentTemplate.value.validation_schema[fieldName]]
    }

    return rules
  }

  // 验证单个字段
  const validateField = (fieldName: FormField): boolean => {
    const rules = getFieldRules(fieldName)
    const value = form[fieldName]

    // 清除之前的错误
    errors[fieldName] = ''

    // 执行验证规则
    for (const rule of rules) {
      // 必填验证
      if (rule.required) {
        if (!value || (typeof value === 'string' && value.trim() === '')) {
          errors[fieldName] = rule.message
          return false
        }
      }

      // 如果值为空且不是必填，跳过其他验证
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        continue
      }

      const stringValue = String(value)

      // 最小长度验证
      if (rule.min !== undefined && stringValue.length < rule.min) {
        errors[fieldName] = rule.message
        return false
      }

      // 最大长度验证
      if (rule.max !== undefined && stringValue.length > rule.max) {
        errors[fieldName] = rule.message
        return false
      }

      // 正则表达式验证
      if (rule.pattern && !rule.pattern.test(stringValue)) {
        errors[fieldName] = rule.message
        return false
      }
    }

    return true
  }

  // 验证所有字段
  const validateAllFields = (): ValidationResult => {
    let isValid = true
    const fieldErrors: FormErrors = {}

    // 验证所有表单字段
    Object.keys(form).forEach((key) => {
      const fieldName = key as FormField
      const fieldValid = validateField(fieldName)
      if (!fieldValid) {
        isValid = false
        fieldErrors[fieldName] = errors[fieldName]
      }
    })

    // 验证额外配置JSON
    if (!validateAdditionalConfig()) {
      isValid = false
      fieldErrors.additional_config = additionalConfigError.value
    }

    return { isValid, errors: fieldErrors }
  }

  // 验证额外配置JSON
  const validateAdditionalConfig = (): boolean => {
    additionalConfigError.value = ''

    if (!additionalConfigText.value.trim()) {
      form.additional_config = {}
      return true
    }

    try {
      const parsed = JSON.parse(additionalConfigText.value)

      // 确保解析结果是对象
      if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
        additionalConfigError.value = '额外配置必须是有效的JSON对象'
        return false
      }

      form.additional_config = parsed
      return true
    } catch {
      additionalConfigError.value = '请输入有效的JSON格式'
      return false
    }
  }

  // 格式化额外配置JSON
  const formatAdditionalConfig = () => {
    if (!additionalConfigText.value.trim()) return

    try {
      const parsed = JSON.parse(additionalConfigText.value)
      additionalConfigText.value = JSON.stringify(parsed, null, 2)
    } catch {
      // 格式化失败，保持原样
    }
  }

  // 标记字段为已触摸
  const touchField = (fieldName: FormField) => {
    touchedFields[fieldName] = true
    formState.isTouched = true
  }

  // 处理字段值变化
  const handleFieldChange = (fieldName: FormField, value: unknown) => {
    form[fieldName] = value as never
    touchField(fieldName)
    formState.isDirty = true

    // 实时验证
    if (touchedFields[fieldName]) {
      validateField(fieldName)
    }

    // 更新变化状态
    formState.hasChanges = hasFormChanges.value
  }

  // 处理字段失焦
  const handleFieldBlur = (fieldName: FormField) => {
    touchField(fieldName)
    validateField(fieldName)
  }

  // 处理供应商类型变化
  const handleProviderTypeChange = (providerType: ProviderType) => {
    const oldType = form.provider_type
    form.provider_type = providerType

    // 如果类型发生变化，重置相关配置
    if (oldType !== providerType) {
      // 应用默认配置
      const template = PROVIDER_CONFIG_TEMPLATES[providerType as ProviderType]
      if (template) {
        form.additional_config = { ...template.default_config }
        additionalConfigText.value = JSON.stringify(template.default_config, null, 2)
      } else {
        form.additional_config = {}
        additionalConfigText.value = ''
      }

      // 重新验证相关字段
      validateField('provider_type')
      validateAdditionalConfig()
    }

    touchField('provider_type')
    formState.isDirty = true
    formState.hasChanges = hasFormChanges.value
  }

  // 初始化表单数据
  const initializeForm = () => {
    if (initialProvider) {
      // 编辑模式：填充现有数据
      Object.assign(form, {
        provider_name: initialProvider.provider_name,
        provider_type: initialProvider.provider_type as ProviderType,
        display_name: initialProvider.display_name,
        description: initialProvider.description || '',
        base_url: initialProvider.base_url,
        api_key: '', // 编辑模式下不显示现有密钥
        additional_config: initialProvider.additional_config || {},
        is_active: initialProvider.is_active,
      })

      // 格式化额外配置
      if (initialProvider.additional_config) {
        additionalConfigText.value = JSON.stringify(initialProvider.additional_config, null, 2)
      }
    } else {
      // 创建模式：使用默认值
      resetForm()
    }

    // 保存原始数据
    originalForm.value = { ...form }

    // 重置状态
    formState.isDirty = false
    formState.isTouched = false
    formState.hasChanges = false
    Object.keys(touchedFields).forEach((key) => {
      touchedFields[key as FormField] = false
    })

    // 清除错误
    Object.keys(errors).forEach((key) => {
      errors[key as FormField] = ''
    })
    additionalConfigError.value = ''
  }

  // 重置表单
  const resetForm = () => {
    Object.assign(form, {
      provider_name: '',
      provider_type: '' as ProviderType,
      display_name: '',
      description: '',
      base_url: '',
      api_key: '',
      additional_config: {},
      is_active: true,
    })

    additionalConfigText.value = ''
    additionalConfigError.value = ''

    // 重置状态
    formState.isDirty = false
    formState.isTouched = false
    formState.isSubmitting = false
    formState.hasChanges = false

    // 重置触摸状态
    Object.keys(touchedFields).forEach((key) => {
      touchedFields[key as FormField] = false
    })

    // 清除错误
    Object.keys(errors).forEach((key) => {
      errors[key as FormField] = ''
    })
  }

  // 获取表单数据用于提交
  const getFormData = (): CreateProviderRequest | UpdateProviderRequest => {
    const data: Record<string, unknown> = { ...form }

    // 如果是编辑模式且API密钥为空，则不包含该字段
    if (isEditMode.value && !data.api_key) {
      delete data.api_key
    }

    // 确保额外配置是最新的
    if (additionalConfigText.value.trim()) {
      try {
        data.additional_config = JSON.parse(additionalConfigText.value)
      } catch {
        // 如果JSON解析失败，使用表单中的值
      }
    }

    return data as CreateProviderRequest | UpdateProviderRequest
  }

  // 提交表单
  const submitForm = async (): Promise<CreateProviderRequest | UpdateProviderRequest | null> => {
    formState.isSubmitting = true

    try {
      // 验证表单
      const validation = validateAllFields()
      if (!validation.isValid) {
        return null
      }

      return getFormData()
    } finally {
      formState.isSubmitting = false
    }
  }

  // 检查字段是否有错误
  const hasFieldError = (fieldName: FormField): boolean => {
    return !!errors[fieldName] && touchedFields[fieldName]
  }

  // 获取字段错误信息
  const getFieldError = (fieldName: FormField): string => {
    return hasFieldError(fieldName) ? errors[fieldName] : ''
  }

  // 检查字段是否为必填
  const isFieldRequired = (fieldName: FormField): boolean => {
    return requiredFields.value.includes(fieldName)
  }

  // 获取字段提示信息
  const getFieldHint = (fieldName: FormField): string => {
    switch (fieldName) {
      case 'provider_name':
        return '供应商的唯一标识符，只能包含字母、数字、下划线和连字符'
      case 'display_name':
        return '供应商的显示名称，用于界面展示'
      case 'base_url':
        return '供应商API的基础URL地址'
      case 'api_key':
        return isEditMode.value ? '留空表示不修改现有密钥' : '供应商API的访问密钥'
      case 'additional_config':
        return 'JSON格式的额外配置参数，根据供应商类型可能包含不同的选项'
      default:
        return ''
    }
  }

  // 自动填充建议
  const getAutoFillSuggestions = (fieldName: FormField): string[] => {
    switch (fieldName) {
      case 'base_url':
        if (form.provider_type) {
          const suggestions: Record<ProviderType, string[]> = {
            openai: ['https://api.openai.com/v1'],
            anthropic: ['https://api.anthropic.com'],
            azure: ['https://{your-resource-name}.openai.azure.com'],
            bedrock: ['https://bedrock-runtime.{region}.amazonaws.com'],
            cohere: ['https://api.cohere.ai/v1'],
            custom: [],
          }
          return suggestions[form.provider_type as ProviderType] || []
        }
        return []
      default:
        return []
    }
  }

  // 应用自动填充
  const applyAutoFill = (fieldName: FormField, value: string) => {
    handleFieldChange(fieldName, value)
  }

  // 监听额外配置文本变化
  watch(additionalConfigText, (_newValue) => {
    if (formState.isTouched) {
      validateAdditionalConfig()
    }
  })

  // 监听供应商类型变化
  watch(
    () => form.provider_type,
    (newType, oldType) => {
      if (newType !== oldType && formState.isTouched) {
        handleProviderTypeChange(newType as ProviderType)
      }
    },
  )

  // 初始化
  onMounted(() => {
    initializeForm()
  })

  return {
    // 表单数据
    form,
    originalForm,
    errors,
    formState,
    touchedFields,
    additionalConfigText,
    additionalConfigError,

    // 计算属性
    isEditMode,
    currentTemplate,
    requiredFields,
    isFormValid,
    hasFormChanges,
    canSubmit,

    // 验证方法
    validateField,
    validateAllFields,
    validateAdditionalConfig,
    formatAdditionalConfig,

    // 表单操作方法
    handleFieldChange,
    handleFieldBlur,
    handleProviderTypeChange,
    touchField,
    initializeForm,
    resetForm,
    getFormData,
    submitForm,

    // 辅助方法
    hasFieldError,
    getFieldError,
    isFieldRequired,
    getFieldHint,
    getAutoFillSuggestions,
    applyAutoFill,
    getFieldRules,
  }
}
