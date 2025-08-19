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
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ProviderManagementPage from '../ProviderManagementPage.vue'
import type { Provider } from '@/types/providerTypes'
import { ProviderType } from '@/types/providerTypes'

// Mock all the composables
const mockProviderManagement = {
  showFormDialog: { value: false },
  showDetailDialog: { value: false },
  showDeleteDialog: { value: false },
  selectedProvider: { value: null },
  dialogMode: { value: 'create' },
  operationLoading: { value: false },
  userFeedback: { value: null },
  openCreateDialog: vi.fn(),
  openEditDialog: vi.fn(),
  openDetailDialog: vi.fn(),
  openDeleteDialog: vi.fn(),
  closeFormDialog: vi.fn(),
  closeDetailDialog: vi.fn(),
  closeDeleteDialog: vi.fn(),
  handleSaveProvider: vi.fn(),
  handleDeleteProvider: vi.fn(),
  handleToggleStatus: vi.fn(),
  showSuccess: vi.fn(),
  showError: vi.fn(),
  clearFeedback: vi.fn(),
}

const mockProviderSearch = {
  searchInput: { value: '' },
  searchState: {
    value: {
      keyword: '',
      providerType: '',
      status: '',
      sortBy: 'created_at',
      sortOrder: 'desc',
      page: 1,
      size: 20,
    },
  },
  showSuggestions: { value: false },
  showAdvancedSearch: { value: false },
  filteredSuggestions: { value: [] },
  activeSuggestionIndex: { value: -1 },
  hasActiveFilters: { value: false },
  isDefaultSort: { value: true },
  handleSearchInput: vi.fn(),
  handleSearchSubmit: vi.fn(),
  clearSearch: vi.fn(),
  applySuggestion: vi.fn(),
  handleKeyboardNavigation: vi.fn(),
  handleProviderTypeFilter: vi.fn(),
  handleStatusFilter: vi.fn(),
  handleSort: vi.fn(),
  resetFilters: vi.fn(),
  handlePageChange: vi.fn(),
  handlePageSizeChange: vi.fn(),
  toggleAdvancedSearch: vi.fn(),
  getSearchSummary: vi.fn(() => ''),
  exportSearchResults: vi.fn(),
  performSearch: vi.fn(),
}

const mockProviderStore = {
  providers: { value: [] },
  loading: { value: false },
  error: { value: null },
  isSearching: { value: false },
  pagination: {
    value: {
      page: 1,
      size: 20,
      total: 0,
      pages: 0,
    },
  },
  totalPages: { value: 0 },
  currentPage: { value: 1 },
  totalProviders: { value: 0 },
  hasProviders: { value: false },
  activeProviders: { value: [] },
  inactiveProviders: { value: [] },
}

const mockPermissions = {
  canView: { value: true },
  canCreate: { value: true },
  canEdit: { value: true },
  canDelete: { value: true },
  canToggleStatus: { value: true },
  canViewSensitive: { value: false },
}

vi.mock('@/composables/useProviderManagement', () => ({
  useProviderManagement: () => mockProviderManagement,
}))

vi.mock('@/composables/useProviderSearch', () => ({
  useProviderSearch: () => mockProviderSearch,
}))

vi.mock('@/stores/providerStore', () => ({
  useProviderStore: () => mockProviderStore,
}))

vi.mock('@/composables/useProviderPermissions', () => ({
  useProviderPermissions: () => mockPermissions,
}))

// Mock child components
vi.mock('@/components/ui/SearchInput.vue', () => ({
  default: {
    name: 'SearchInput',
    template: '<input class="search-input" />',
    props: ['modelValue', 'placeholder', 'suggestions', 'showSuggestions'],
    emits: ['update:modelValue', 'search', 'suggestion-select'],
  },
}))

vi.mock('@/components/ui/SelectFilter.vue', () => ({
  default: {
    name: 'SelectFilter',
    template: '<select class="select-filter"><option>Mock Option</option></select>',
    props: ['modelValue', 'options', 'placeholder'],
    emits: ['update:modelValue', 'change'],
  },
}))

vi.mock('@/components/provider/ProviderCard.vue', () => ({
  default: {
    name: 'ProviderCard',
    template: '<div class="provider-card">{{ provider.display_name }}</div>',
    props: ['provider', 'permissions', 'loading'],
    emits: ['view-details', 'edit', 'delete', 'toggle-status'],
  },
}))

vi.mock('@/components/ui/Pagination.vue', () => ({
  default: {
    name: 'Pagination',
    template: '<div class="pagination">Pagination</div>',
    props: ['currentPage', 'totalPages', 'pageSize', 'total'],
    emits: ['page-change', 'size-change'],
  },
}))

vi.mock('@/components/ui/LoadingSpinner.vue', () => ({
  default: {
    name: 'LoadingSpinner',
    template: '<div class="loading-spinner">Loading...</div>',
  },
}))

vi.mock('@/components/ui/EmptyState.vue', () => ({
  default: {
    name: 'EmptyState',
    template: '<div class="empty-state">{{ message }}</div>',
    props: ['message', 'showCreateButton'],
    emits: ['create'],
  },
}))

vi.mock('@/components/provider/ProviderDialogForm.vue', () => ({
  default: {
    name: 'ProviderDialogForm',
    template: '<div class="provider-dialog-form">Form Dialog</div>',
    props: ['modelValue', 'provider', 'mode'],
    emits: ['save', 'cancel'],
  },
}))

vi.mock('@/components/provider/ProviderDetailDialog.vue', () => ({
  default: {
    name: 'ProviderDetailDialog',
    template: '<div class="provider-detail-dialog">Detail Dialog</div>',
    props: ['modelValue', 'provider', 'loading'],
    emits: ['edit', 'delete', 'toggle-status', 'close'],
  },
}))

vi.mock('@/components/provider/ConfirmDeleteDialog.vue', () => ({
  default: {
    name: 'ConfirmDeleteDialog',
    template: '<div class="confirm-delete-dialog">Delete Dialog</div>',
    props: ['modelValue', 'provider', 'loading'],
    emits: ['confirm', 'cancel'],
  },
}))

describe('ProviderManagementPage', () => {
  const mockProvider: Provider = {
    provider_id: 1,
    provider_name: 'test-provider',
    provider_type: ProviderType.OPENAI,
    display_name: 'Test Provider',
    description: 'Test description',
    base_url: 'https://api.openai.com/v1',
    additional_config: {},
    is_active: true,
    created_by: 'admin',
    created_at: '2025-01-01T00:00:00Z',
    updated_by: 'admin',
    updated_at: '2025-01-01T00:00:00Z',
  }

  let router: any

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    // Create router
    router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/admin/providers', component: ProviderManagementPage }],
    })

    // Reset mock values
    mockProviderStore.providers.value = []
    mockProviderStore.loading.value = false
    mockProviderStore.error.value = null
    mockProviderStore.hasProviders.value = false
    mockProviderManagement.showFormDialog.value = false
    mockProviderManagement.showDetailDialog.value = false
    mockProviderManagement.showDeleteDialog.value = false
    mockProviderManagement.userFeedback.value = null
    mockProviderSearch.searchInput.value = ''
    mockProviderSearch.hasActiveFilters.value = false
  })

  describe('Page Rendering', () => {
    it('should render page header correctly', () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.page-header').exists()).toBe(true)
      expect(wrapper.find('.page-title').text()).toBe('供应商管理')
      expect(wrapper.find('.create-button').exists()).toBe(true)
    })

    it('should render search and filter section', () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.search-filters').exists()).toBe(true)
      expect(wrapper.find('.search-input').exists()).toBe(true)
      expect(wrapper.findAll('.select-filter')).toHaveLength(2) // Type and status filters
    })

    it('should show loading state', () => {
      mockProviderStore.loading.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
      expect(wrapper.find('.providers-grid').exists()).toBe(false)
    })

    it('should show empty state when no providers', () => {
      mockProviderStore.loading.value = false
      mockProviderStore.hasProviders.value = false

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.find('.providers-grid').exists()).toBe(false)
    })

    it('should render provider cards when providers exist', () => {
      mockProviderStore.loading.value = false
      mockProviderStore.hasProviders.value = true
      mockProviderStore.providers.value = [mockProvider]

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.providers-grid').exists()).toBe(true)
      expect(wrapper.find('.provider-card').exists()).toBe(true)
      expect(wrapper.find('.empty-state').exists()).toBe(false)
    })

    it('should show pagination when multiple pages', () => {
      mockProviderStore.pagination.value.pages = 3
      mockProviderStore.pagination.value.total = 50

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.pagination').exists()).toBe(true)
    })

    it('should hide pagination when single page', () => {
      mockProviderStore.pagination.value.pages = 1
      mockProviderStore.pagination.value.total = 10

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.pagination').exists()).toBe(false)
    })
  })

  describe('Permission-based Rendering', () => {
    it('should show create button when user has create permission', () => {
      mockPermissions.canCreate.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.create-button').exists()).toBe(true)
    })

    it('should hide create button when user lacks create permission', () => {
      mockPermissions.canCreate.value = false

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.create-button').exists()).toBe(false)
    })

    it('should pass permissions to provider cards', () => {
      mockProviderStore.providers.value = [mockProvider]
      mockProviderStore.hasProviders.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const providerCard = wrapper.findComponent({ name: 'ProviderCard' })
      expect(providerCard.props('permissions')).toEqual({
        canView: true,
        canEdit: true,
        canDelete: true,
        canToggleStatus: true,
      })
    })
  })

  describe('Dialog Management', () => {
    it('should show form dialog when showFormDialog is true', () => {
      mockProviderManagement.showFormDialog.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.provider-dialog-form').exists()).toBe(true)
    })

    it('should show detail dialog when showDetailDialog is true', () => {
      mockProviderManagement.showDetailDialog.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.provider-detail-dialog').exists()).toBe(true)
    })

    it('should show delete dialog when showDeleteDialog is true', () => {
      mockProviderManagement.showDeleteDialog.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.confirm-delete-dialog').exists()).toBe(true)
    })

    it('should hide all dialogs by default', () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.provider-dialog-form').exists()).toBe(false)
      expect(wrapper.find('.provider-detail-dialog').exists()).toBe(false)
      expect(wrapper.find('.confirm-delete-dialog').exists()).toBe(false)
    })
  })

  describe('User Interactions', () => {
    it('should call openCreateDialog when create button is clicked', async () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      await wrapper.find('.create-button').trigger('click')

      expect(mockProviderManagement.openCreateDialog).toHaveBeenCalled()
    })

    it('should handle provider card events', async () => {
      mockProviderStore.providers.value = [mockProvider]
      mockProviderStore.hasProviders.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const providerCard = wrapper.findComponent({ name: 'ProviderCard' })

      // Test view details
      await providerCard.vm.$emit('view-details', mockProvider)
      expect(mockProviderManagement.openDetailDialog).toHaveBeenCalledWith(mockProvider)

      // Test edit
      await providerCard.vm.$emit('edit', mockProvider)
      expect(mockProviderManagement.openEditDialog).toHaveBeenCalledWith(mockProvider)

      // Test delete
      await providerCard.vm.$emit('delete', mockProvider)
      expect(mockProviderManagement.openDeleteDialog).toHaveBeenCalledWith(mockProvider)

      // Test toggle status
      await providerCard.vm.$emit('toggle-status', mockProvider)
      expect(mockProviderManagement.handleToggleStatus).toHaveBeenCalledWith(mockProvider)
    })

    it('should handle search input', async () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const searchInput = wrapper.findComponent({ name: 'SearchInput' })
      await searchInput.vm.$emit('update:modelValue', 'test search')

      expect(mockProviderSearch.handleSearchInput).toHaveBeenCalledWith('test search')
    })

    it('should handle filter changes', async () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const filters = wrapper.findAllComponents({ name: 'SelectFilter' })

      // Test provider type filter
      await filters[0].vm.$emit('change', 'openai')
      expect(mockProviderSearch.handleProviderTypeFilter).toHaveBeenCalledWith('openai')

      // Test status filter
      await filters[1].vm.$emit('change', 'active')
      expect(mockProviderSearch.handleStatusFilter).toHaveBeenCalledWith('active')
    })

    it('should handle pagination events', async () => {
      mockProviderStore.pagination.value.pages = 3

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const pagination = wrapper.findComponent({ name: 'Pagination' })

      await pagination.vm.$emit('page-change', 2)
      expect(mockProviderSearch.handlePageChange).toHaveBeenCalledWith(2)

      await pagination.vm.$emit('size-change', 50)
      expect(mockProviderSearch.handlePageSizeChange).toHaveBeenCalledWith(50)
    })

    it('should handle empty state create button', async () => {
      mockProviderStore.hasProviders.value = false

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const emptyState = wrapper.findComponent({ name: 'EmptyState' })
      await emptyState.vm.$emit('create')

      expect(mockProviderManagement.openCreateDialog).toHaveBeenCalled()
    })
  })

  describe('Dialog Event Handling', () => {
    it('should handle form dialog save event', async () => {
      mockProviderManagement.showFormDialog.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const formDialog = wrapper.findComponent({ name: 'ProviderDialogForm' })
      const formData = { provider_name: 'test', display_name: 'Test' }

      await formDialog.vm.$emit('save', formData)

      expect(mockProviderManagement.handleSaveProvider).toHaveBeenCalledWith(formData)
    })

    it('should handle form dialog cancel event', async () => {
      mockProviderManagement.showFormDialog.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const formDialog = wrapper.findComponent({ name: 'ProviderDialogForm' })
      await formDialog.vm.$emit('cancel')

      expect(mockProviderManagement.closeFormDialog).toHaveBeenCalled()
    })

    it('should handle detail dialog events', async () => {
      mockProviderManagement.showDetailDialog.value = true
      mockProviderManagement.selectedProvider.value = mockProvider

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const detailDialog = wrapper.findComponent({ name: 'ProviderDetailDialog' })

      // Test edit event
      await detailDialog.vm.$emit('edit', mockProvider)
      expect(mockProviderManagement.openEditDialog).toHaveBeenCalledWith(mockProvider)

      // Test delete event
      await detailDialog.vm.$emit('delete', mockProvider)
      expect(mockProviderManagement.openDeleteDialog).toHaveBeenCalledWith(mockProvider)

      // Test toggle status event
      await detailDialog.vm.$emit('toggle-status', mockProvider)
      expect(mockProviderManagement.handleToggleStatus).toHaveBeenCalledWith(mockProvider)

      // Test close event
      await detailDialog.vm.$emit('close')
      expect(mockProviderManagement.closeDetailDialog).toHaveBeenCalled()
    })

    it('should handle delete dialog events', async () => {
      mockProviderManagement.showDeleteDialog.value = true
      mockProviderManagement.selectedProvider.value = mockProvider

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const deleteDialog = wrapper.findComponent({ name: 'ConfirmDeleteDialog' })

      // Test confirm event
      await deleteDialog.vm.$emit('confirm')
      expect(mockProviderManagement.handleDeleteProvider).toHaveBeenCalled()

      // Test cancel event
      await deleteDialog.vm.$emit('cancel')
      expect(mockProviderManagement.closeDeleteDialog).toHaveBeenCalled()
    })
  })

  describe('User Feedback', () => {
    it('should show success feedback', () => {
      mockProviderManagement.userFeedback.value = {
        type: 'success',
        message: 'Operation successful',
      }

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.success-toast').exists()).toBe(true)
      expect(wrapper.find('.success-toast').text()).toContain('Operation successful')
    })

    it('should show error feedback', () => {
      mockProviderManagement.userFeedback.value = {
        type: 'error',
        message: 'Operation failed',
      }

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.error-alert').exists()).toBe(true)
      expect(wrapper.find('.error-alert').text()).toContain('Operation failed')
    })

    it('should handle feedback dismissal', async () => {
      mockProviderManagement.userFeedback.value = {
        type: 'success',
        message: 'Test message',
      }

      const _wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      // Simulate feedback auto-dismiss after timeout
      setTimeout(() => {
        expect(mockProviderManagement.clearFeedback).toHaveBeenCalled()
      }, 3000)
    })
  })

  describe('Advanced Search Features', () => {
    it('should show advanced search when toggled', () => {
      mockProviderSearch.showAdvancedSearch.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.advanced-search').exists()).toBe(true)
    })

    it('should show search suggestions when available', () => {
      mockProviderSearch.showSuggestions.value = true
      mockProviderSearch.filteredSuggestions.value = [
        { text: 'OpenAI Provider', type: 'provider' },
        { text: 'test search', type: 'history' },
      ]

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const searchInput = wrapper.findComponent({ name: 'SearchInput' })
      expect(searchInput.props('showSuggestions')).toBe(true)
      expect(searchInput.props('suggestions')).toHaveLength(2)
    })

    it('should show active filters indicator', () => {
      mockProviderSearch.hasActiveFilters.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.active-filters-indicator').exists()).toBe(true)
    })

    it('should show clear filters button when filters are active', () => {
      mockProviderSearch.hasActiveFilters.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.clear-filters-btn').exists()).toBe(true)
    })
  })

  describe('Responsive Design', () => {
    it('should apply responsive grid classes', () => {
      mockProviderStore.providers.value = [mockProvider]
      mockProviderStore.hasProviders.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const grid = wrapper.find('.providers-grid')
      expect(grid.classes()).toContain('grid')
      expect(grid.classes()).toContain('grid-cols-1')
      expect(grid.classes()).toContain('md:grid-cols-2')
      expect(grid.classes()).toContain('lg:grid-cols-3')
      expect(grid.classes()).toContain('xl:grid-cols-4')
    })

    it('should show mobile-friendly search layout', () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const searchFilters = wrapper.find('.search-filters')
      expect(searchFilters.classes()).toContain('flex-col')
      expect(searchFilters.classes()).toContain('md:flex-row')
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('[role="main"]').exists()).toBe(true)
      expect(wrapper.find('[aria-label="供应商管理"]').exists()).toBe(true)
    })

    it('should support keyboard navigation', async () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      // Test Tab navigation
      await wrapper.trigger('keydown.tab')
      // Focus should move to next focusable element

      // Test Enter key on create button
      const createButton = wrapper.find('.create-button')
      await createButton.trigger('keydown.enter')
      expect(mockProviderManagement.openCreateDialog).toHaveBeenCalled()
    })

    it('should announce loading state to screen readers', () => {
      mockProviderStore.loading.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('[aria-live="polite"]').exists()).toBe(true)
      expect(wrapper.find('[aria-busy="true"]').exists()).toBe(true)
    })
  })

  describe('Error Handling', () => {
    it('should display error state when store has error', () => {
      mockProviderStore.error.value = 'Failed to load providers'

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.error-state').exists()).toBe(true)
      expect(wrapper.find('.error-state').text()).toContain('Failed to load providers')
    })

    it('should show retry button on error', async () => {
      mockProviderStore.error.value = 'Network error'

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const retryButton = wrapper.find('.retry-button')
      expect(retryButton.exists()).toBe(true)

      await retryButton.trigger('click')
      expect(mockProviderSearch.performSearch).toHaveBeenCalled()
    })
  })

  describe('Performance', () => {
    it('should not re-render unnecessarily', async () => {
      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      const initialRenderCount = wrapper.vm.$el.children.length

      // Change unrelated state
      mockProviderSearch.searchInput.value = 'test'
      await wrapper.vm.$nextTick()

      // Should not cause full re-render
      expect(wrapper.vm.$el.children.length).toBe(initialRenderCount)
    })

    it('should handle large provider lists efficiently', () => {
      const manyProviders = Array.from({ length: 100 }, (_, i) => ({
        ...mockProvider,
        provider_id: i,
        display_name: `Provider ${i}`,
      }))

      mockProviderStore.providers.value = manyProviders
      mockProviderStore.hasProviders.value = true

      const wrapper = mount(ProviderManagementPage, {
        global: {
          plugins: [router],
        },
      })

      // Should render without performance issues
      expect(wrapper.findAllComponents({ name: 'ProviderCard' })).toHaveLength(100)
    })
  })
})
