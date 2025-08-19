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
import { useAriaAnnouncements, useAriaLabels } from '../useAriaAnnouncements'

describe('useAriaAnnouncements', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with empty announcements', () => {
    const { announcements } = useAriaAnnouncements()
    expect(announcements.value).toEqual([])
  })

  it('should create announcements correctly', () => {
    const { announce, announcements } = useAriaAnnouncements()

    const id = announce('Test message', 'polite')

    expect(announcements.value).toHaveLength(1)
    expect(announcements.value[0].message).toBe('Test message')
    expect(announcements.value[0].type).toBe('polite')
    expect(announcements.value[0].id).toBe(id)
  })

  it('should provide convenience methods for different announcement types', () => {
    const { announceSuccess, announceError, announceWarning, announceInfo, announcements } =
      useAriaAnnouncements()

    announceSuccess('Success message')
    announceError('Error message')
    announceWarning('Warning message')
    announceInfo('Info message')

    expect(announcements.value).toHaveLength(4)
    expect(announcements.value[0].message).toBe('成功：Success message')
    expect(announcements.value[1].message).toBe('错误：Error message')
    expect(announcements.value[2].message).toBe('警告：Warning message')
    expect(announcements.value[3].message).toBe('信息：Info message')
  })

  it('should announce search results correctly', () => {
    const { announceSearchResults, announcements } = useAriaAnnouncements()

    announceSearchResults(5, 'test query')
    expect(announcements.value[0].message).toBe('找到5个"test query"的搜索结果')

    announceSearchResults(0, 'no results')
    expect(announcements.value[1].message).toBe('未找到"no results"的搜索结果')
  })

  it('should announce pagination correctly', () => {
    const { announcePagination, announcements } = useAriaAnnouncements()

    announcePagination(2, 5, 50)
    expect(announcements.value[0].message).toBe('第2页，共5页，总计50项')
  })

  it('should clear announcements', () => {
    const { announce, clearAnnouncements, announcements } = useAriaAnnouncements()

    announce('Test message')
    expect(announcements.value).toHaveLength(1)

    clearAnnouncements()
    expect(announcements.value).toHaveLength(0)
  })

  it('should limit announcements to 10 items', () => {
    const { announce, announcements } = useAriaAnnouncements()

    // Add 15 announcements
    for (let i = 0; i < 15; i++) {
      announce(`Message ${i}`)
    }

    expect(announcements.value).toHaveLength(10)
    expect(announcements.value[0].message).toBe('Message 5') // Should keep the last 10
  })
})

describe('useAriaLabels', () => {
  it('should generate unique IDs', () => {
    const { generateId } = useAriaLabels()

    const id1 = generateId('test')
    const id2 = generateId('test')

    expect(id1).toMatch(/^test-\d+-[a-z0-9]+$/)
    expect(id2).toMatch(/^test-\d+-[a-z0-9]+$/)
    expect(id1).not.toBe(id2)
  })

  it('should create description and error IDs', () => {
    const { createDescriptionId, createErrorId, createHelpId } = useAriaLabels()

    expect(createDescriptionId('field')).toBe('field-description')
    expect(createErrorId('field')).toBe('field-error')
    expect(createHelpId('field')).toBe('field-help')
  })

  it('should build describedby attributes correctly', () => {
    const { buildDescribedBy } = useAriaLabels()

    expect(buildDescribedBy('id1', 'id2', 'id3')).toBe('id1 id2 id3')
    expect(buildDescribedBy('id1', undefined, 'id3')).toBe('id1 id3')
    expect(buildDescribedBy(undefined, undefined)).toBeUndefined()
  })

  it('should get field ARIA attributes correctly', () => {
    const { getFieldAriaAttributes } = useAriaLabels()

    const attributes = getFieldAriaAttributes('test-field', {
      hasError: true,
      hasHelp: true,
      required: true,
      invalid: true,
    })

    expect(attributes['aria-required']).toBe('true')
    expect(attributes['aria-invalid']).toBe('true')
    expect(attributes['aria-describedby']).toBe('test-field-help test-field-error')
  })

  it('should get button ARIA attributes correctly', () => {
    const { getButtonAriaAttributes } = useAriaLabels()

    const attributes = getButtonAriaAttributes({
      pressed: true,
      expanded: false,
      hasPopup: 'menu',
      controls: 'menu-id',
    })

    expect(attributes['aria-pressed']).toBe('true')
    expect(attributes['aria-expanded']).toBe('false')
    expect(attributes['aria-haspopup']).toBe('menu')
    expect(attributes['aria-controls']).toBe('menu-id')
  })

  it('should get list ARIA attributes correctly', () => {
    const { getListAriaAttributes } = useAriaLabels()

    const attributes = getListAriaAttributes(10, {
      multiselectable: true,
      orientation: 'vertical',
      label: 'Test list',
    })

    expect(attributes['aria-label']).toBe('Test list')
    expect(attributes['aria-multiselectable']).toBe('true')
    expect(attributes['aria-orientation']).toBe('vertical')
    expect(attributes['aria-setsize']).toBe('10')
  })

  it('should get list item ARIA attributes correctly', () => {
    const { getListItemAriaAttributes } = useAriaLabels()

    const attributes = getListItemAriaAttributes(3, 10, {
      selected: true,
      level: 2,
      expanded: false,
      hasChildren: true,
    })

    expect(attributes['aria-posinset']).toBe('3')
    expect(attributes['aria-setsize']).toBe('10')
    expect(attributes['aria-selected']).toBe('true')
    expect(attributes['aria-level']).toBe('2')
    expect(attributes['aria-expanded']).toBe('false')
  })
})
