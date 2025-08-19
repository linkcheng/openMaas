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
import Pagination from '../Pagination.vue'

describe('Pagination', () => {
  it('renders pagination info correctly', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 2,
        totalPages: 5,
        pageSize: 20,
        total: 95,
      },
    })

    expect(wrapper.text()).toContain('第 2 页，共 5 页')
    expect(wrapper.text()).toContain('共 95 条记录')
  })

  it('shows correct page numbers', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalPages: 7,
        pageSize: 20,
        total: 140,
      },
    })

    const pageButtons = wrapper.findAll('.page-button')
    // Should show pages around current page
    expect(pageButtons.some((btn) => btn.text() === '1')).toBe(true)
    expect(pageButtons.some((btn) => btn.text() === '2')).toBe(true)
    expect(pageButtons.some((btn) => btn.text() === '3')).toBe(true)
    expect(pageButtons.some((btn) => btn.text() === '4')).toBe(true)
  })

  it('highlights current page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalPages: 5,
        pageSize: 20,
        total: 100,
      },
    })

    const currentPageButton = wrapper.find('.page-button.active')
    expect(currentPageButton.text()).toBe('3')
  })

  it('emits page-change when page button is clicked', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 2,
        totalPages: 5,
        pageSize: 20,
        total: 100,
      },
    })

    const pageButton = wrapper.findAll('.page-button').find((btn) => btn.text() === '4')
    await pageButton?.trigger('click')

    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')?.[0]).toEqual([4])
  })

  it('disables previous button on first page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5,
        pageSize: 20,
        total: 100,
      },
    })

    const prevButton = wrapper.find('.prev-button')
    expect(prevButton.attributes('disabled')).toBeDefined()
  })

  it('disables next button on last page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 5,
        totalPages: 5,
        pageSize: 20,
        total: 100,
      },
    })

    const nextButton = wrapper.find('.next-button')
    expect(nextButton.attributes('disabled')).toBeDefined()
  })

  it('emits page-change when previous button is clicked', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalPages: 5,
        pageSize: 20,
        total: 100,
      },
    })

    const prevButton = wrapper.find('.prev-button')
    await prevButton.trigger('click')

    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')?.[0]).toEqual([2])
  })

  it('emits page-change when next button is clicked', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalPages: 5,
        pageSize: 20,
        total: 100,
      },
    })

    const nextButton = wrapper.find('.next-button')
    await nextButton.trigger('click')

    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')?.[0]).toEqual([4])
  })

  it('shows page size selector', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5,
        pageSize: 20,
        total: 100,
        showSizeChanger: true,
      },
    })

    expect(wrapper.find('.page-size-selector').exists()).toBe(true)
  })

  it('emits size-change when page size is changed', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5,
        pageSize: 20,
        total: 100,
        showSizeChanger: true,
      },
    })

    const sizeSelector = wrapper.find('.page-size-selector select')
    await sizeSelector.setValue('50')

    expect(wrapper.emitted('size-change')).toBeTruthy()
    expect(wrapper.emitted('size-change')?.[0]).toEqual([50])
  })

  it('shows ellipsis for large page ranges', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 10,
        totalPages: 20,
        pageSize: 20,
        total: 400,
      },
    })

    expect(wrapper.text()).toContain('...')
  })

  it('supports jump to page input', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 5,
        totalPages: 10,
        pageSize: 20,
        total: 200,
        showQuickJumper: true,
      },
    })

    expect(wrapper.find('.quick-jumper').exists()).toBe(true)
    expect(wrapper.find('.jump-input').exists()).toBe(true)
  })

  it('emits page-change when jump input is used', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 5,
        totalPages: 10,
        pageSize: 20,
        total: 200,
        showQuickJumper: true,
      },
    })

    const jumpInput = wrapper.find('.jump-input')
    await jumpInput.setValue('7')
    await jumpInput.trigger('keydown.enter')

    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')?.[0]).toEqual([7])
  })

  it('validates jump input range', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 5,
        totalPages: 10,
        pageSize: 20,
        total: 200,
        showQuickJumper: true,
      },
    })

    const jumpInput = wrapper.find('.jump-input')

    // Test invalid page number (too high)
    await jumpInput.setValue('15')
    await jumpInput.trigger('keydown.enter')

    // Should not emit page-change for invalid page
    expect(wrapper.emitted('page-change')).toBeFalsy()
  })

  it('has proper accessibility attributes', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalPages: 5,
        pageSize: 20,
        total: 100,
      },
    })

    const nav = wrapper.find('nav')
    expect(nav.attributes('role')).toBe('navigation')
    expect(nav.attributes('aria-label')).toBe('分页导航')

    const currentPageButton = wrapper.find('.page-button.active')
    expect(currentPageButton.attributes('aria-current')).toBe('page')
  })

  it('handles single page correctly', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 1,
        pageSize: 20,
        total: 15,
      },
    })

    expect(wrapper.find('.prev-button').attributes('disabled')).toBeDefined()
    expect(wrapper.find('.next-button').attributes('disabled')).toBeDefined()
    expect(wrapper.findAll('.page-button')).toHaveLength(1)
  })

  it('handles zero pages correctly', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 0,
        pageSize: 20,
        total: 0,
      },
    })

    expect(wrapper.text()).toContain('共 0 条记录')
    expect(wrapper.findAll('.page-button')).toHaveLength(0)
  })
})
