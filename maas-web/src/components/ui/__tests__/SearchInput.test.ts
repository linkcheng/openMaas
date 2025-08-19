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

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchInput from '../SearchInput.vue'

describe('SearchInput', () => {
  it('renders input with placeholder', () => {
    const wrapper = mount(SearchInput, {
      props: {
        placeholder: 'Search providers...',
      },
    })

    const input = wrapper.find('input')
    expect(input.attributes('placeholder')).toBe('Search providers...')
  })

  it('emits update:modelValue when input changes', async () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: '',
      },
    })

    const input = wrapper.find('input')
    await input.setValue('test search')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['test search'])
  })

  it('emits search event on Enter key', async () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: 'test',
      },
    })

    const input = wrapper.find('input')
    await input.trigger('keydown.enter')

    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('search')?.[0]).toEqual(['test'])
  })

  it('shows suggestions when provided', () => {
    const suggestions = [
      { text: 'OpenAI Provider', type: 'provider' as const },
      { text: 'test search', type: 'history' as const },
    ]

    const wrapper = mount(SearchInput, {
      props: {
        modelValue: 'test',
        suggestions,
        showSuggestions: true,
      },
    })

    expect(wrapper.find('.suggestions-list').exists()).toBe(true)
    expect(wrapper.findAll('.suggestion-item')).toHaveLength(2)
  })

  it('emits suggestion-select when suggestion is clicked', async () => {
    const suggestions = [{ text: 'OpenAI Provider', type: 'provider' as const }]

    const wrapper = mount(SearchInput, {
      props: {
        modelValue: 'test',
        suggestions,
        showSuggestions: true,
      },
    })

    const suggestionItem = wrapper.find('.suggestion-item')
    await suggestionItem.trigger('click')

    expect(wrapper.emitted('suggestion-select')).toBeTruthy()
    expect(wrapper.emitted('suggestion-select')?.[0]).toEqual([suggestions[0]])
  })

  it('handles keyboard navigation in suggestions', async () => {
    const suggestions = [
      { text: 'Suggestion 1', type: 'provider' as const },
      { text: 'Suggestion 2', type: 'history' as const },
    ]

    const wrapper = mount(SearchInput, {
      props: {
        modelValue: 'test',
        suggestions,
        showSuggestions: true,
      },
    })

    const input = wrapper.find('input')

    // Arrow down should highlight first suggestion
    await input.trigger('keydown.down')
    expect(wrapper.find('.suggestion-item.active').text()).toBe('Suggestion 1')

    // Arrow down again should highlight second suggestion
    await input.trigger('keydown.down')
    expect(wrapper.find('.suggestion-item.active').text()).toBe('Suggestion 2')

    // Arrow up should go back to first
    await input.trigger('keydown.up')
    expect(wrapper.find('.suggestion-item.active').text()).toBe('Suggestion 1')

    // Enter should select active suggestion
    await input.trigger('keydown.enter')
    expect(wrapper.emitted('suggestion-select')?.[0]).toEqual([suggestions[0]])
  })

  it('shows clear button when input has value', () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: 'test search',
      },
    })

    expect(wrapper.find('.clear-button').exists()).toBe(true)
  })

  it('clears input when clear button is clicked', async () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: 'test search',
      },
    })

    const clearButton = wrapper.find('.clear-button')
    await clearButton.trigger('click')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([''])
  })

  it('has proper accessibility attributes', () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: '',
        placeholder: 'Search...',
      },
    })

    const input = wrapper.find('input')
    expect(input.attributes('role')).toBe('searchbox')
    expect(input.attributes('aria-label')).toBe('搜索输入框')
  })

  it('supports disabled state', () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: '',
        disabled: true,
      },
    })

    const input = wrapper.find('input')
    expect(input.attributes('disabled')).toBeDefined()
  })
})
