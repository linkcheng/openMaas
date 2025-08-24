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

import { ref, computed, type Ref } from 'vue'

/**
 * 通用状态管理基础接口
 */
export interface BaseState {
  loading: boolean
  error: string | null
  lastUpdated: Date | null
}

/**
 * 分页状态接口
 */
export interface PaginationState {
  page: number
  size: number
  total: number
  pages: number
}

/**
 * 创建基础状态
 */
export function createBaseState(): {
  loading: Ref<boolean>
  error: Ref<string | null>
  lastUpdated: Ref<Date | null>
  setLoading: (value: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  updateTimestamp: () => void
} {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdated = ref<Date | null>(null)

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setError = (errorValue: string | null) => {
    error.value = errorValue
    if (errorValue) {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const updateTimestamp = () => {
    lastUpdated.value = new Date()
  }

  return {
    loading,
    error,
    lastUpdated,
    setLoading,
    setError,
    clearError,
    updateTimestamp,
  }
}

/**
 * 创建分页状态
 */
export function createPaginationState(initialSize = 20): {
  pagination: Ref<PaginationState>
  setPagination: (page: number, size: number, total: number) => void
  resetPagination: () => void
  nextPage: () => void
  prevPage: () => void
  hasNextPage: () => boolean
  hasPrevPage: () => boolean
} {
  const pagination = ref<PaginationState>({
    page: 1,
    size: initialSize,
    total: 0,
    pages: 0,
  })

  const setPagination = (page: number, size: number, total: number) => {
    pagination.value = {
      page,
      size,
      total,
      pages: Math.ceil(total / size),
    }
  }

  const resetPagination = () => {
    pagination.value = {
      page: 1,
      size: initialSize,
      total: 0,
      pages: 0,
    }
  }

  const nextPage = () => {
    if (hasNextPage()) {
      pagination.value.page += 1
    }
  }

  const prevPage = () => {
    if (hasPrevPage()) {
      pagination.value.page -= 1
    }
  }

  const hasNextPage = () => {
    return pagination.value.page < pagination.value.pages
  }

  const hasPrevPage = () => {
    return pagination.value.page > 1
  }

  return {
    pagination,
    setPagination,
    resetPagination,
    nextPage,
    prevPage,
    hasNextPage,
    hasPrevPage,
  }
}

/**
 * 创建列表状态管理
 */
export function createListState<T>(initialSize = 20) {
  const items = ref<T[]>([]) as Ref<T[]>
  const selectedItems = ref<T[]>([]) as Ref<T[]>
  const { loading, error, lastUpdated, setLoading, setError, clearError, updateTimestamp } =
    createBaseState()
  const { pagination, setPagination, resetPagination, nextPage, prevPage, hasNextPage, hasPrevPage } =
    createPaginationState(initialSize)

  const isEmpty = computed(() => items.value.length === 0)
  const hasSelection = computed(() => selectedItems.value.length > 0)

  const setItems = (newItems: T[]) => {
    items.value = newItems
    updateTimestamp()
  }

  const addItem = (item: T) => {
    items.value.push(item)
    updateTimestamp()
  }

  const removeItem = (predicate: (item: T) => boolean) => {
    const index = items.value.findIndex(predicate)
    if (index !== -1) {
      items.value.splice(index, 1)
      updateTimestamp()
    }
  }

  const updateItem = (predicate: (item: T) => boolean, updates: Partial<T>) => {
    const index = items.value.findIndex(predicate)
    if (index !== -1) {
      items.value[index] = { ...items.value[index], ...updates }
      updateTimestamp()
    }
  }

  const clearItems = () => {
    items.value = []
    selectedItems.value = []
    resetPagination()
    clearError()
  }

  const selectItem = (item: T) => {
    if (!selectedItems.value.includes(item)) {
      selectedItems.value.push(item)
    }
  }

  const unselectItem = (item: T) => {
    const index = selectedItems.value.indexOf(item)
    if (index !== -1) {
      selectedItems.value.splice(index, 1)
    }
  }

  const toggleSelection = (item: T) => {
    if (selectedItems.value.includes(item)) {
      unselectItem(item)
    } else {
      selectItem(item)
    }
  }

  const clearSelection = () => {
    selectedItems.value = []
  }

  const selectAll = () => {
    selectedItems.value = [...items.value]
  }

  return {
    items,
    selectedItems,
    loading,
    error,
    lastUpdated,
    pagination,
    isEmpty,
    hasSelection,
    setItems,
    addItem,
    removeItem,
    updateItem,
    clearItems,
    selectItem,
    unselectItem,
    toggleSelection,
    clearSelection,
    selectAll,
    setLoading,
    setError,
    clearError,
    setPagination,
    resetPagination,
    nextPage,
    prevPage,
    hasNextPage,
    hasPrevPage,
  }
}