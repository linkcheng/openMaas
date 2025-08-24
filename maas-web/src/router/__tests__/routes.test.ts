import { describe, it, expect } from 'vitest'
import { routes, basicRoutes, authRoutes, maasRoutes, userRoutes, adminRoutes } from '../routes'

describe('Routes Configuration', () => {
  it('should include all basic routes', () => {
    expect(basicRoutes).toHaveLength(2)
    expect(basicRoutes[0].name).toBe('home')
    expect(basicRoutes[1].name).toBe('about')
  })

  it('should include all auth routes', () => {
    expect(authRoutes).toHaveLength(3)
    expect(authRoutes[0].name).toBe('login')
    expect(authRoutes[1].name).toBe('register')
    expect(authRoutes[2].name).toBe('forgot-password')
    
    // 所有认证路由应该需要游客状态
    authRoutes.forEach(route => {
      expect(route.meta?.requiresGuest).toBe(true)
    })
  })

  it('should include all MaaS routes', () => {
    expect(maasRoutes).toHaveLength(9)
    
    // 所有MaaS路由应该需要认证
    maasRoutes.forEach(route => {
      expect(route.meta?.requiresAuth).toBe(true)
    })
  })

  it('should include user management routes', () => {
    expect(userRoutes).toHaveLength(2)
    expect(userRoutes[0].name).toBe('profile')
    expect(userRoutes[1].name).toBe('settings')
    
    // 用户路由应该需要认证
    userRoutes.forEach(route => {
      expect(route.meta?.requiresAuth).toBe(true)
    })
  })

  it('should include admin routes', () => {
    expect(adminRoutes).toHaveLength(4)
    
    // 检查前三个管理员路由（跳过providers路由，因为它的结构不同）
    const standardAdminRoutes = [adminRoutes[0], adminRoutes[1], adminRoutes[3]] // admin, admin-users, admin-audit-logs
    standardAdminRoutes.forEach(route => {
      expect(route.meta?.requiresAuth).toBe(true)
      expect(route.meta?.requiresAdmin).toBe(true)
    })
  })

  it('should have correct route structure', () => {
    expect(routes).toHaveLength(6) // basicRoutes(2) + authRoutes(3) + mainRoutes(1) = 6
    
    // 检查是否包含基本路由
    const homeRoute = routes.find(route => route.name === 'home')
    expect(homeRoute).toBeDefined()
    
    // 检查是否包含认证路由
    const loginRoute = routes.find(route => route.name === 'login')
    expect(loginRoute).toBeDefined()
  })

  it('should have valid route paths', () => {
    const flatRoutes = [
      ...basicRoutes,
      ...authRoutes,
      ...maasRoutes,
      ...userRoutes,
      ...adminRoutes
    ]

    flatRoutes.forEach(route => {
      expect(route.path).toBeTruthy()
      expect(route.name).toBeTruthy()
    })
  })

  it('should have consistent meta properties', () => {
    const protectedRoutes = [...maasRoutes, ...userRoutes]
    
    protectedRoutes.forEach(route => {
      expect(route.meta).toBeDefined()
      expect(route.meta?.requiresAuth).toBe(true)
      expect(route.meta?.title).toBeTruthy()
    })
  })
})