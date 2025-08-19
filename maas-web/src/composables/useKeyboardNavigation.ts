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

import { ref, onMounted, onUnmounted, nextTick } from 'vue'

/**
 * 可聚焦元素选择器
 */
const FOCUSABLE_ELEMENTS_SELECTOR = [
  'button:not([disabled])',
  '[href]',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"]):not([disabled])',
  '[contenteditable="true"]',
].join(', ')

/**
 * 键盘导航和焦点管理 Composable
 */
export function useKeyboardNavigation() {
  const currentFocusIndex = ref(-1)
  const focusableElements = ref<HTMLElement[]>([])
  const containerRef = ref<HTMLElement>()

  /**
   * 获取容器内所有可聚焦元素
   */
  const getFocusableElements = (container?: HTMLElement): HTMLElement[] => {
    const targetContainer = container || containerRef.value
    if (!targetContainer) return []

    const elements = targetContainer.querySelectorAll(FOCUSABLE_ELEMENTS_SELECTOR)
    return Array.from(elements).filter((element) => {
      const htmlElement = element as HTMLElement
      // 过滤掉不可见或被禁用的元素
      return (
        htmlElement.offsetWidth > 0 &&
        htmlElement.offsetHeight > 0 &&
        !htmlElement.hasAttribute('disabled') &&
        htmlElement.getAttribute('tabindex') !== '-1'
      )
    }) as HTMLElement[]
  }

  /**
   * 更新可聚焦元素列表
   */
  const updateFocusableElements = (container?: HTMLElement) => {
    focusableElements.value = getFocusableElements(container)

    // 更新当前焦点索引
    const activeElement = document.activeElement as HTMLElement
    if (activeElement) {
      currentFocusIndex.value = focusableElements.value.indexOf(activeElement)
    }
  }

  /**
   * 聚焦到指定索引的元素
   */
  const focusElementAtIndex = (index: number) => {
    if (index >= 0 && index < focusableElements.value.length) {
      const element = focusableElements.value[index]
      element.focus()
      currentFocusIndex.value = index
      return true
    }
    return false
  }

  /**
   * 聚焦到第一个元素
   */
  const focusFirst = () => {
    return focusElementAtIndex(0)
  }

  /**
   * 聚焦到最后一个元素
   */
  const focusLast = () => {
    return focusElementAtIndex(focusableElements.value.length - 1)
  }

  /**
   * 聚焦到下一个元素
   */
  const focusNext = () => {
    const nextIndex = currentFocusIndex.value + 1
    if (nextIndex >= focusableElements.value.length) {
      return focusFirst() // 循环到第一个
    }
    return focusElementAtIndex(nextIndex)
  }

  /**
   * 聚焦到上一个元素
   */
  const focusPrevious = () => {
    const prevIndex = currentFocusIndex.value - 1
    if (prevIndex < 0) {
      return focusLast() // 循环到最后一个
    }
    return focusElementAtIndex(prevIndex)
  }

  /**
   * 处理键盘事件
   */
  const handleKeyDown = (event: KeyboardEvent) => {
    const { key, shiftKey, ctrlKey, metaKey } = event

    // 更新可聚焦元素列表
    updateFocusableElements()

    switch (key) {
      case 'Tab':
        // Tab 键导航
        if (shiftKey) {
          if (!focusPrevious()) {
            // 如果没有上一个元素，让浏览器处理默认行为
            return
          }
        } else {
          if (!focusNext()) {
            // 如果没有下一个元素，让浏览器处理默认行为
            return
          }
        }
        event.preventDefault()
        break

      case 'ArrowDown':
      case 'ArrowRight':
        // 方向键向下/右导航
        if (!ctrlKey && !metaKey) {
          focusNext()
          event.preventDefault()
        }
        break

      case 'ArrowUp':
      case 'ArrowLeft':
        // 方向键向上/左导航
        if (!ctrlKey && !metaKey) {
          focusPrevious()
          event.preventDefault()
        }
        break

      case 'Home':
        // Home 键聚焦第一个元素
        if (!ctrlKey && !metaKey) {
          focusFirst()
          event.preventDefault()
        }
        break

      case 'End':
        // End 键聚焦最后一个元素
        if (!ctrlKey && !metaKey) {
          focusLast()
          event.preventDefault()
        }
        break
    }
  }

  /**
   * 处理元素激活（Enter 或 Space 键）
   */
  const handleActivation = (event: KeyboardEvent, callback?: () => void) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      if (callback) {
        callback()
      } else {
        // 默认行为：触发点击事件
        const target = event.target as HTMLElement
        if (target) {
          target.click()
        }
      }
    }
  }

  return {
    containerRef,
    currentFocusIndex,
    focusableElements,
    getFocusableElements,
    updateFocusableElements,
    focusElementAtIndex,
    focusFirst,
    focusLast,
    focusNext,
    focusPrevious,
    handleKeyDown,
    handleActivation,
  }
}

/**
 * 焦点陷阱 Composable - 用于对话框等模态组件
 */
export function useFocusTrap() {
  const trapRef = ref<HTMLElement>()
  const previousActiveElement = ref<HTMLElement>()
  const isActive = ref(false)

  /**
   * 激活焦点陷阱
   */
  const activate = async () => {
    if (isActive.value) return

    // 保存当前焦点元素
    previousActiveElement.value = document.activeElement as HTMLElement

    await nextTick()

    if (!trapRef.value) return

    // 获取陷阱内的可聚焦元素
    const focusableElements = trapRef.value.querySelectorAll(FOCUSABLE_ELEMENTS_SELECTOR)
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    // 聚焦第一个元素
    if (firstElement) {
      firstElement.focus()
    } else {
      // 如果没有可聚焦元素，聚焦容器本身
      trapRef.value.focus()
    }

    // 添加键盘事件监听器
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return

      if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          event.preventDefault()
          lastElement?.focus()
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          event.preventDefault()
          firstElement?.focus()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    isActive.value = true

    // 返回清理函数
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      deactivate()
    }
  }

  /**
   * 停用焦点陷阱
   */
  const deactivate = () => {
    if (!isActive.value) return

    isActive.value = false

    // 恢复之前的焦点
    if (previousActiveElement.value) {
      previousActiveElement.value.focus()
      previousActiveElement.value = undefined
    }
  }

  return {
    trapRef,
    isActive,
    activate,
    deactivate,
  }
}

/**
 * 焦点指示器 Composable
 */
export function useFocusIndicator() {
  const isKeyboardUser = ref(false)

  const handleMouseDown = () => {
    isKeyboardUser.value = false
  }

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Tab') {
      isKeyboardUser.value = true
    }
  }

  onMounted(() => {
    document.addEventListener('mousedown', handleMouseDown)
    document.addEventListener('keydown', handleKeyDown)
  })

  onUnmounted(() => {
    document.removeEventListener('mousedown', handleMouseDown)
    document.removeEventListener('keydown', handleKeyDown)
  })

  return {
    isKeyboardUser,
  }
}

/**
 * 跳过链接 Composable - 用于无障碍访问
 */
export function useSkipLinks() {
  const skipLinks = ref<Array<{ href: string; text: string }>>([])

  const addSkipLink = (href: string, text: string) => {
    skipLinks.value.push({ href, text })
  }

  const removeSkipLink = (href: string) => {
    const index = skipLinks.value.findIndex((link) => link.href === href)
    if (index > -1) {
      skipLinks.value.splice(index, 1)
    }
  }

  const clearSkipLinks = () => {
    skipLinks.value = []
  }

  return {
    skipLinks,
    addSkipLink,
    removeSkipLink,
    clearSkipLinks,
  }
}
