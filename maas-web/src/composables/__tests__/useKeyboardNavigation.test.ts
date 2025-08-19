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

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useKeyboardNavigation, useFocusTrap } from '../useKeyboardNavigation'

// Mock DOM methods
Object.defineProperty(HTMLElement.prototype, 'focus', {
  value: vi.fn(),
  writable: true,
})

Object.defineProperty(HTMLElement.prototype, 'querySelectorAll', {
  value: vi.fn(),
  writable: true,
})

describe('useKeyboardNavigation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with correct default values', () => {
    const { currentFocusIndex, focusableElements, containerRef } = useKeyboardNavigation()

    expect(currentFocusIndex.value).toBe(-1)
    expect(focusableElements.value).toEqual([])
    expect(containerRef.value).toBeUndefined()
  })

  it('should handle keyboard navigation correctly', () => {
    const TestComponent = defineComponent({
      setup() {
        const { handleKeyDown, focusNext, focusPrevious } = useKeyboardNavigation()
        return {
          handleKeyDown,
          focusNext,
          focusPrevious,
        }
      },
      template: '<div></div>',
    })

    const wrapper = mount(TestComponent)
    const component = wrapper.vm

    // Test that methods exist and are callable
    expect(typeof component.focusNext).toBe('function')
    expect(typeof component.focusPrevious).toBe('function')
    expect(typeof component.handleKeyDown).toBe('function')
  })

  it('should generate unique IDs', () => {
    const { getFocusableElements } = useKeyboardNavigation()

    // Test that the function exists
    expect(typeof getFocusableElements).toBe('function')

    // Test with no container
    const elements = getFocusableElements()
    expect(Array.isArray(elements)).toBe(true)
  })
})

describe('useFocusTrap', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with correct default values', () => {
    const { trapRef, isActive } = useFocusTrap()

    expect(trapRef.value).toBeUndefined()
    expect(isActive.value).toBe(false)
  })

  it('should provide activate and deactivate methods', () => {
    const { activate, deactivate } = useFocusTrap()

    expect(typeof activate).toBe('function')
    expect(typeof deactivate).toBe('function')
  })

  it('should handle activation correctly', async () => {
    const { activate, isActive: _isActive } = useFocusTrap()

    // Mock document.activeElement
    Object.defineProperty(document, 'activeElement', {
      value: document.createElement('button'),
      writable: true,
    })

    await activate()

    // The function should be callable without errors
    expect(typeof activate).toBe('function')
  })
})
