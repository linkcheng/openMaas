import { describe, it, expect, beforeEach, vi } from 'vitest'
import { RoutePreloader, routePreloader, preloadRouteComponents } from '../preloader'
import { memoryCache } from '@/utils/cache'

describe('RoutePreloader', () => {
  beforeEach(() => {
    memoryCache.clear()
    routePreloader.clearPreloadCache()
  })

  it('should create singleton instance', () => {
    const instance1 = RoutePreloader.getInstance()
    const instance2 = RoutePreloader.getInstance()
    expect(instance1).toBe(instance2)
  })

  it('should track preloaded routes', () => {
    expect(routePreloader.isRoutePreloaded('test-route')).toBe(false)
  })

  it('should handle unknown routes gracefully', async () => {
    await expect(routePreloader.preloadRoute('unknown-route')).resolves.toBeUndefined()
  })

  it('should handle multiple preload calls', async () => {
    // 应该能够多次调用同一路由的预加载而不出错
    await routePreloader.preloadRoute('unknown-route')
    await routePreloader.preloadRoute('unknown-route')
    
    // 不应该抛出异常
    expect(true).toBe(true)
  })

  it('should clear preload cache', () => {
    routePreloader.clearPreloadCache()
    expect(routePreloader.isRoutePreloaded('any-route')).toBe(false)
  })
})

describe('preloadRouteComponents', () => {
  it('should not throw error for any route name', () => {
    expect(() => preloadRouteComponents('test-route')).not.toThrow()
    expect(() => preloadRouteComponents('')).not.toThrow()
  })
})