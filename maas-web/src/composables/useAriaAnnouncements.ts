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

import { ref } from 'vue'

/**
 * ARIA 公告类型
 */
export type AriaAnnouncementType = 'polite' | 'assertive'

/**
 * ARIA 公告接口
 */
export interface AriaAnnouncement {
  id: string
  message: string
  type: AriaAnnouncementType
  timestamp: number
}

/**
 * ARIA 公告和屏幕阅读器支持 Composable
 */
export function useAriaAnnouncements() {
  const announcements = ref<AriaAnnouncement[]>([])
  const politeRegionRef = ref<HTMLElement>()
  const assertiveRegionRef = ref<HTMLElement>()

  /**
   * 创建公告
   */
  const announce = (message: string, type: AriaAnnouncementType = 'polite') => {
    if (!message.trim()) return

    const announcement: AriaAnnouncement = {
      id: `announcement-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      message: message.trim(),
      type,
      timestamp: Date.now(),
    }

    announcements.value.push(announcement)

    // 更新对应的 live region
    updateLiveRegion(announcement)

    // 清理旧的公告（保留最近的10条）
    if (announcements.value.length > 10) {
      announcements.value = announcements.value.slice(-10)
    }

    return announcement.id
  }

  /**
   * 更新 live region
   */
  const updateLiveRegion = (announcement: AriaAnnouncement) => {
    const targetRef = announcement.type === 'assertive' ? assertiveRegionRef : politeRegionRef

    if (targetRef.value) {
      // 清空然后设置新内容，确保屏幕阅读器能够读取
      targetRef.value.textContent = ''

      // 使用 setTimeout 确保屏幕阅读器能够检测到变化
      setTimeout(() => {
        if (targetRef.value) {
          targetRef.value.textContent = announcement.message
        }
      }, 100)

      // 5秒后清空内容
      setTimeout(() => {
        if (targetRef.value && targetRef.value.textContent === announcement.message) {
          targetRef.value.textContent = ''
        }
      }, 5000)
    }
  }

  /**
   * 礼貌公告（不会打断当前的屏幕阅读器输出）
   */
  const announcePolite = (message: string) => {
    return announce(message, 'polite')
  }

  /**
   * 断言公告（会立即打断当前的屏幕阅读器输出）
   */
  const announceAssertive = (message: string) => {
    return announce(message, 'assertive')
  }

  /**
   * 公告成功消息
   */
  const announceSuccess = (message: string) => {
    return announcePolite(`成功：${message}`)
  }

  /**
   * 公告错误消息
   */
  const announceError = (message: string) => {
    return announceAssertive(`错误：${message}`)
  }

  /**
   * 公告警告消息
   */
  const announceWarning = (message: string) => {
    return announcePolite(`警告：${message}`)
  }

  /**
   * 公告信息消息
   */
  const announceInfo = (message: string) => {
    return announcePolite(`信息：${message}`)
  }

  /**
   * 公告加载状态
   */
  const announceLoading = (message: string = '正在加载') => {
    return announcePolite(message)
  }

  /**
   * 公告加载完成
   */
  const announceLoadingComplete = (message: string = '加载完成') => {
    return announcePolite(message)
  }

  /**
   * 公告页面变化
   */
  const announcePageChange = (pageName: string) => {
    return announcePolite(`已导航到${pageName}页面`)
  }

  /**
   * 公告表单验证错误
   */
  const announceFormError = (fieldName: string, errorMessage: string) => {
    return announceAssertive(`${fieldName}字段错误：${errorMessage}`)
  }

  /**
   * 公告表单提交状态
   */
  const announceFormSubmission = (status: 'submitting' | 'success' | 'error', message?: string) => {
    switch (status) {
      case 'submitting':
        return announcePolite(message || '正在提交表单')
      case 'success':
        return announceSuccess(message || '表单提交成功')
      case 'error':
        return announceError(message || '表单提交失败')
    }
  }

  /**
   * 公告搜索结果
   */
  const announceSearchResults = (count: number, query?: string) => {
    const queryText = query ? `"${query}"` : ''
    if (count === 0) {
      return announcePolite(`未找到${queryText}的搜索结果`)
    } else {
      return announcePolite(`找到${count}个${queryText}的搜索结果`)
    }
  }

  /**
   * 公告筛选结果
   */
  const announceFilterResults = (count: number, filterDescription?: string) => {
    const filterText = filterDescription ? `应用${filterDescription}筛选后，` : ''
    return announcePolite(`${filterText}显示${count}个结果`)
  }

  /**
   * 公告分页变化
   */
  const announcePagination = (currentPage: number, totalPages: number, totalItems: number) => {
    return announcePolite(`第${currentPage}页，共${totalPages}页，总计${totalItems}项`)
  }

  /**
   * 清除所有公告
   */
  const clearAnnouncements = () => {
    announcements.value = []
    if (politeRegionRef.value) {
      politeRegionRef.value.textContent = ''
    }
    if (assertiveRegionRef.value) {
      assertiveRegionRef.value.textContent = ''
    }
  }

  /**
   * 获取最近的公告
   */
  const getRecentAnnouncements = (limit: number = 5) => {
    return announcements.value.slice(-limit)
  }

  return {
    announcements,
    politeRegionRef,
    assertiveRegionRef,
    announce,
    announcePolite,
    announceAssertive,
    announceSuccess,
    announceError,
    announceWarning,
    announceInfo,
    announceLoading,
    announceLoadingComplete,
    announcePageChange,
    announceFormError,
    announceFormSubmission,
    announceSearchResults,
    announceFilterResults,
    announcePagination,
    clearAnnouncements,
    getRecentAnnouncements,
  }
}

/**
 * ARIA 描述和标签管理 Composable
 */
export function useAriaLabels() {
  /**
   * 生成唯一的 ID
   */
  const generateId = (prefix: string = 'aria') => {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * 创建描述性文本的 ID
   */
  const createDescriptionId = (baseId: string) => {
    return `${baseId}-description`
  }

  /**
   * 创建错误信息的 ID
   */
  const createErrorId = (baseId: string) => {
    return `${baseId}-error`
  }

  /**
   * 创建帮助文本的 ID
   */
  const createHelpId = (baseId: string) => {
    return `${baseId}-help`
  }

  /**
   * 构建 aria-describedby 属性值
   */
  const buildDescribedBy = (...ids: (string | undefined)[]) => {
    return ids.filter(Boolean).join(' ') || undefined
  }

  /**
   * 构建 aria-labelledby 属性值
   */
  const buildLabelledBy = (...ids: (string | undefined)[]) => {
    return ids.filter(Boolean).join(' ') || undefined
  }

  /**
   * 获取表单字段的 ARIA 属性
   */
  const getFieldAriaAttributes = (
    fieldId: string,
    options: {
      hasError?: boolean
      hasHelp?: boolean
      hasDescription?: boolean
      required?: boolean
      invalid?: boolean
    } = {},
  ) => {
    const { hasError, hasHelp, hasDescription, required, invalid } = options

    const describedByIds: string[] = []

    if (hasDescription) {
      describedByIds.push(createDescriptionId(fieldId))
    }

    if (hasHelp) {
      describedByIds.push(createHelpId(fieldId))
    }

    if (hasError) {
      describedByIds.push(createErrorId(fieldId))
    }

    return {
      'aria-required': required ? 'true' : undefined,
      'aria-invalid': invalid || hasError ? 'true' : undefined,
      'aria-describedby': describedByIds.length > 0 ? describedByIds.join(' ') : undefined,
    }
  }

  /**
   * 获取按钮的 ARIA 属性
   */
  const getButtonAriaAttributes = (
    options: {
      pressed?: boolean
      expanded?: boolean
      hasPopup?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog'
      controls?: string
      describedBy?: string
      labelledBy?: string
      disabled?: boolean
    } = {},
  ) => {
    const { pressed, expanded, hasPopup, controls, describedBy, labelledBy, disabled } = options

    return {
      'aria-pressed': pressed !== undefined ? pressed.toString() : undefined,
      'aria-expanded': expanded !== undefined ? expanded.toString() : undefined,
      'aria-haspopup': hasPopup === true ? 'true' : hasPopup || undefined,
      'aria-controls': controls,
      'aria-describedby': describedBy,
      'aria-labelledby': labelledBy,
      'aria-disabled': disabled ? 'true' : undefined,
    }
  }

  /**
   * 获取列表的 ARIA 属性
   */
  const getListAriaAttributes = (
    totalItems: number,
    options: {
      multiselectable?: boolean
      orientation?: 'horizontal' | 'vertical'
      label?: string
      labelledBy?: string
    } = {},
  ) => {
    const { multiselectable, orientation, label, labelledBy } = options

    return {
      'aria-label': label,
      'aria-labelledby': labelledBy,
      'aria-multiselectable': multiselectable ? 'true' : undefined,
      'aria-orientation': orientation,
      'aria-setsize': totalItems.toString(),
    }
  }

  /**
   * 获取列表项的 ARIA 属性
   */
  const getListItemAriaAttributes = (
    position: number,
    totalItems: number,
    options: {
      selected?: boolean
      level?: number
      expanded?: boolean
      hasChildren?: boolean
    } = {},
  ) => {
    const { selected, level, expanded, hasChildren } = options

    return {
      'aria-posinset': position.toString(),
      'aria-setsize': totalItems.toString(),
      'aria-selected': selected !== undefined ? selected.toString() : undefined,
      'aria-level': level?.toString(),
      'aria-expanded': hasChildren && expanded !== undefined ? expanded.toString() : undefined,
    }
  }

  return {
    generateId,
    createDescriptionId,
    createErrorId,
    createHelpId,
    buildDescribedBy,
    buildLabelledBy,
    getFieldAriaAttributes,
    getButtonAriaAttributes,
    getListAriaAttributes,
    getListItemAriaAttributes,
  }
}
