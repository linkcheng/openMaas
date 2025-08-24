import { ref, computed, watch } from 'vue'
import { LocalStorageCache, CACHE_KEYS } from '../utils/cache'

export type Theme = 'light' | 'dark' | 'auto'

// 主题状态
const currentTheme = ref<Theme>('auto')
const isDark = ref(false)

// 检测系统主题偏好
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// 应用主题到 DOM
const applyTheme = (theme: 'light' | 'dark') => {
  if (typeof document === 'undefined') return

  const root = document.documentElement

  if (theme === 'dark') {
    root.classList.add('dark')
    root.setAttribute('data-theme', 'dark')
  } else {
    root.classList.remove('dark')
    root.setAttribute('data-theme', 'light')
  }

  isDark.value = theme === 'dark'
}

// 更新主题
const updateTheme = () => {
  const theme = currentTheme.value === 'auto' ? getSystemTheme() : currentTheme.value
  applyTheme(theme)
}

// 初始化主题
const initTheme = () => {
  // 从缓存读取主题设置（永久缓存）
  const savedTheme = LocalStorageCache.get<Theme>(CACHE_KEYS.USER_THEME)
  if (savedTheme && ['light', 'dark', 'auto'].includes(savedTheme)) {
    currentTheme.value = savedTheme
  }

  updateTheme()

  // 监听系统主题变化
  if (typeof window !== 'undefined') {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', () => {
      if (currentTheme.value === 'auto') {
        updateTheme()
      }
    })
  }
}

export function useTheme() {
  // 设置主题
  const setTheme = (theme: Theme) => {
    currentTheme.value = theme
    // 永久缓存主题设置
    LocalStorageCache.set(CACHE_KEYS.USER_THEME, theme, Number.MAX_SAFE_INTEGER)
    updateTheme()
  }

  // 切换主题
  const toggleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'auto']
    const currentIndex = themes.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex])
  }

  // 计算属性
  const theme = computed(() => currentTheme.value)
  const isLight = computed(() => !isDark.value)
  const effectiveTheme = computed(() =>
    currentTheme.value === 'auto' ? getSystemTheme() : currentTheme.value,
  )

  // 主题选项
  const themeOptions = [
    { value: 'light', label: '浅色模式', icon: '☀️' },
    { value: 'dark', label: '深色模式', icon: '🌙' },
    { value: 'auto', label: '跟随系统', icon: '🔄' },
  ] as const

  // 监听主题变化
  watch(currentTheme, updateTheme)

  return {
    theme,
    isDark: computed(() => isDark.value),
    isLight,
    effectiveTheme,
    themeOptions,
    setTheme,
    toggleTheme,
    initTheme,
  }
}

// 自动初始化
if (typeof window !== 'undefined') {
  initTheme()
}
