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

import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Mock global objects
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(() => null),
    setItem: vi.fn(() => null),
    removeItem: vi.fn(() => null),
    clear: vi.fn(() => null),
  },
  writable: true,
})

// Mock sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: {
    getItem: vi.fn(() => null),
    setItem: vi.fn(() => null),
    removeItem: vi.fn(() => null),
    clear: vi.fn(() => null),
  },
  writable: true,
})

// Mock URL.createObjectURL
Object.defineProperty(URL, 'createObjectURL', {
  value: vi.fn(() => 'mocked-url'),
  writable: true,
})

Object.defineProperty(URL, 'revokeObjectURL', {
  value: vi.fn(),
  writable: true,
})

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn(),
  log: vi.fn(),
}

// Global test configuration for Vue Test Utils
config.global.stubs = {
  // Stub out router components
  'router-link': true,
  'router-view': true,
  // Stub out transition components
  transition: false,
  'transition-group': false,
}

// Mock common Vue Router composables
vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: {},
    query: {},
    path: '/test',
    name: 'test',
    meta: {},
  }),
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
  }),
  createRouter: vi.fn(),
  createWebHistory: vi.fn(),
  createWebHashHistory: vi.fn(),
}))

// Mock Pinia
vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  createPinia: vi.fn(),
  setActivePinia: vi.fn(),
  storeToRefs: vi.fn(),
}))

// Mock common Element Plus components
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  },
  ElMessageBox: {
    confirm: vi.fn(),
    alert: vi.fn(),
    prompt: vi.fn(),
  },
  ElNotification: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock VueUse composables
vi.mock('@vueuse/core', () => ({
  useDebounceFn: vi.fn((fn) => fn),
  useThrottleFn: vi.fn((fn) => fn),
  useLocalStorage: vi.fn(() => ({ value: null })),
  useSessionStorage: vi.fn(() => ({ value: null })),
  useEventListener: vi.fn(),
  useResizeObserver: vi.fn(),
  useIntersectionObserver: vi.fn(),
  useMutationObserver: vi.fn(),
  useMediaQuery: vi.fn(() => ({ value: false })),
  usePreferredDark: vi.fn(() => ({ value: false })),
  useToggle: vi.fn(() => [{ value: false }, vi.fn()]),
  useClipboard: vi.fn(() => ({
    copy: vi.fn(),
    copied: { value: false },
    isSupported: { value: true },
  })),
}))

// Setup fake timers for tests that need them
beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  vi.useRealTimers()
  vi.clearAllMocks()
})
