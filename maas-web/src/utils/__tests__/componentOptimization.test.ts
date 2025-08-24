import { describe, it, expect } from 'vitest'
import fs from 'fs'
import path from 'path'

describe('Component Optimization', () => {
  it('should have removed manual component preloader', () => {
    // 检查componentPreloader文件是否已删除
    let componentPreloaderExists = true
    try {
      require('../componentPreloader')
    } catch (error) {
      componentPreloaderExists = false
    }
    
    expect(componentPreloaderExists).toBe(false)
  })

  it('should use optimized ECharts imports', () => {
    // 检查EChart组件是否使用按需导入
    const echartPath = path.resolve(__dirname, '../../components/charts/EChart.vue')
    if (fs.existsSync(echartPath)) {
      const content = fs.readFileSync(echartPath, 'utf-8')
      
      // 应该使用echarts/core而不是完整的echarts包
      expect(content).toContain('echarts/core')
      expect(content).not.toContain("import * as echarts from 'echarts'")
    }
  })

  it('should have created icon utilities', () => {
    // 检查图标工具文件是否存在
    const iconsPath = path.resolve(__dirname, '../icons.ts')
    expect(fs.existsSync(iconsPath)).toBe(true)
  })

  it('should have optimized route code splitting', () => {
    // 检查路由是否都使用了动态导入
    const routesPath = path.resolve(__dirname, '../../router/routes.ts')
    if (fs.existsSync(routesPath)) {
      const content = fs.readFileSync(routesPath, 'utf-8')
      
      // 不应该有静态导入组件
      expect(content).not.toContain("import HomeView from")
      expect(content).not.toContain("import MainLayout from")
      
      // 应该使用动态导入
      expect(content).toContain("() => import(")
    }
  })

  it('should have eliminated unused Element Plus icons imports', () => {
    // 检查main.ts是否移除了全量图标导入
    const mainPath = path.resolve(__dirname, '../../main.ts')
    if (fs.existsSync(mainPath)) {
      const content = fs.readFileSync(mainPath, 'utf-8')
      
      // 不应该有全量图标导入
      expect(content).not.toContain("import * as ElementPlusIconsVue")
      expect(content).not.toContain("for (const [key, component] of Object.entries(ElementPlusIconsVue))")
    }
  })
})