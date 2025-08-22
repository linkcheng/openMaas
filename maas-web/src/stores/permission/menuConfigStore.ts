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

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/utils/api'
import type {
  MenuPermissionConfig,
  CreateMenuConfigRequest,
  UpdateMenuConfigRequest,
  MenuTreeNode,
  MenuPermissionResult,
  MenuConfigExport,
  MenuConfigImportRequest,
  MenuConfigImportResult,
  MenuPreviewConfig,
  MenuPreviewResult,
  MenuQueryParams,
  MenuDragOperation,
  BatchMenuOperationRequest,
  MenuType,
  MenuStatus,
  PermissionLogic,
} from '@/types/permission/menuTypes'
import type {
  ApiResponse,
  BatchOperationResult,
} from '@/types/permission/commonTypes'

/**
 * 菜单权限配置状态管理 Store
 * Menu permission configuration state management store
 */
export const useMenuConfigStore = defineStore('menuConfig', () => {
  // ==================== 状态定义 ====================
  
  /** 菜单配置列表 */
  const menuConfigs = ref<MenuPermissionConfig[]>([])
  
  /** 菜单树结构 */
  const menuTree = ref<MenuTreeNode[]>([])
  
  /** 加载状态 */
  const loading = ref(false)
  
  /** 错误信息 */
  const error = ref<string | null>(null)
  
  /** 搜索关键词 */
  const searchQuery = ref('')
  
  /** 菜单类型筛选 */
  const menuTypeFilter = ref<MenuType | ''>('')
  
  /** 菜单状态筛选 */
  const statusFilter = ref<MenuStatus | ''>('')
  
  /** 父菜单筛选 */
  const parentFilter = ref('')
  
  /** 是否只显示根菜单 */
  const rootOnlyFilter = ref(false)
  
  /** 权限筛选 */
  const permissionFilter = ref('')
  
  /** 排序字段 */
  const sortBy = ref('sort_order')
  
  /** 排序方向 */
  const sortOrder = ref<'asc' | 'desc'>('asc')
  
  /** 缓存的菜单配置详情 */
  const configDetailsCache = ref<Map<string, MenuPermissionConfig>>(new Map())
  
  /** 批量操作状态 */
  const batchOperationLoading = ref(false)
  
  /** 树形结构展开状态 */
  const expandedNodes = ref<Set<string>>(new Set())
  
  /** 树形结构选中状态 */
  const selectedNodes = ref<Set<string>>(new Set())
  
  /** 拖拽状态 */
  const dragState = ref<{
    isDragging: boolean
    draggedNode: string | null
    dropTarget: string | null
  }>({
    isDragging: false,
    draggedNode: null,
    dropTarget: null,
  })
  
  /** 导入导出状态 */
  const importExportLoading = ref(false)
  
  /** 预览状态 */
  const previewLoading = ref(false)
  
  /** 预览结果 */
  const previewResult = ref<MenuPreviewResult | null>(null)

  // ==================== 计算属性 ====================
  
  /** 筛选后的菜单配置列表 */
  const filteredMenuConfigs = computed(() => {
    let filtered = menuConfigs.value

    // 搜索筛选
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(config =>
        config.menu_name.toLowerCase().includes(query) ||
        config.menu_key.toLowerCase().includes(query) ||
        config.menu_path.toLowerCase().includes(query)
      )
    }

    // 菜单类型筛选
    if (menuTypeFilter.value) {
      filtered = filtered.filter(config => config.menu_type === menuTypeFilter.value)
    }

    // 菜单状态筛选
    if (statusFilter.value) {
      filtered = filtered.filter(config => config.status === statusFilter.value)
    }

    // 父菜单筛选
    if (parentFilter.value) {
      filtered = filtered.filter(config => config.parent_key === parentFilter.value)
    }

    // 根菜单筛选
    if (rootOnlyFilter.value) {
      filtered = filtered.filter(config => !config.parent_key)
    }

    // 权限筛选
    if (permissionFilter.value) {
      filtered = filtered.filter(config =>
        config.required_permissions.some(permission =>
          permission.toLowerCase().includes(permissionFilter.value.toLowerCase())
        )
      )
    }

    return filtered
  })
  
  /** 根菜单配置列表 */
  const rootMenuConfigs = computed(() => 
    menuConfigs.value.filter(config => !config.parent_key)
  )
  
  /** 按类型分组的菜单配置 */
  const menuConfigsByType = computed(() => {
    const grouped: Record<MenuType, MenuPermissionConfig[]> = {
      menu: [],
      button: [],
      tab: [],
      section: [],
    }
    
    menuConfigs.value.forEach(config => {
      grouped[config.menu_type].push(config)
    })
    
    return grouped
  })
  
  /** 可见的菜单配置 */
  const visibleMenuConfigs = computed(() => 
    menuConfigs.value.filter(config => config.is_visible && config.status === 'visible')
  )
  
  /** 隐藏的菜单配置 */
  const hiddenMenuConfigs = computed(() => 
    menuConfigs.value.filter(config => !config.is_visible || config.status === 'hidden')
  )
  
  /** 可用的父菜单选项 */
  const availableParentMenus = computed(() => 
    menuConfigs.value
      .filter(config => config.menu_type === 'menu')
      .map(config => ({
        key: config.menu_key,
        name: config.menu_name,
        level: config.level,
      }))
      .sort((a, b) => a.level - b.level || a.name.localeCompare(b.name))
  )
  
  /** 所有使用的权限列表 */
  const usedPermissions = computed(() => {
    const permissions = new Set<string>()
    menuConfigs.value.forEach(config => {
      config.required_permissions.forEach(permission => permissions.add(permission))
    })
    return Array.from(permissions).sort()
  })

  // ==================== 基础操作方法 ====================
  
  /**
   * 设置加载状态
   */
  const setLoading = (value: boolean) => {
    loading.value = value
  }
  
  /**
   * 设置错误信息
   */
  const setError = (message: string | null) => {
    error.value = message
  }
  
  /**
   * 清除错误信息
   */
  const clearError = () => {
    error.value = null
  }
  
  /**
   * 重置筛选条件
   */
  const resetFilters = () => {
    searchQuery.value = ''
    menuTypeFilter.value = ''
    statusFilter.value = ''
    parentFilter.value = ''
    rootOnlyFilter.value = false
    permissionFilter.value = ''
  }

  // ==================== API 调用方法 ====================
  
  /**
   * 获取菜单配置列表
   */
  const fetchMenuConfigs = async (params?: Partial<MenuQueryParams>) => {
    setLoading(true)
    clearError()

    try {
      const queryParams: MenuQueryParams = {
        search: searchQuery.value || undefined,
        menu_type: menuTypeFilter.value || undefined,
        status: statusFilter.value || undefined,
        parent_key: parentFilter.value || undefined,
        root_only: rootOnlyFilter.value || undefined,
        permission: permissionFilter.value || undefined,
        sort_by: sortBy.value,
        sort_order: sortOrder.value,
        ...params,
      }

      const response = await apiClient.get<ApiResponse<MenuPermissionConfig[]>>(
        '/menu-configs',
        queryParams
      )

      if (response.data.success && response.data.data) {
        menuConfigs.value = response.data.data
        
        // 更新缓存
        response.data.data.forEach(config => {
          configDetailsCache.value.set(config.menu_key, config)
        })
        
        // 构建菜单树
        buildMenuTree()
      } else {
        throw new Error(response.data.error || '获取菜单配置列表失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取菜单配置列表失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 获取菜单配置详情
   */
  const fetchMenuConfigByKey = async (menuKey: string, useCache = true): Promise<MenuPermissionConfig> => {
    // 检查缓存
    if (useCache && configDetailsCache.value.has(menuKey)) {
      return configDetailsCache.value.get(menuKey)!
    }

    setLoading(true)
    clearError()

    try {
      const response = await apiClient.get<ApiResponse<MenuPermissionConfig>>(`/menu-configs/${menuKey}`)

      if (response.data.success && response.data.data) {
        const config = response.data.data
        
        // 更新缓存
        configDetailsCache.value.set(menuKey, config)
        
        // 更新列表中的配置
        const index = menuConfigs.value.findIndex(c => c.menu_key === menuKey)
        if (index !== -1) {
          menuConfigs.value[index] = config
        }
        
        return config
      } else {
        throw new Error(response.data.error || '获取菜单配置详情失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '获取菜单配置详情失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 创建菜单配置
   */
  const createMenuConfig = async (configData: CreateMenuConfigRequest): Promise<MenuPermissionConfig> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<MenuPermissionConfig>>('/menu-configs', configData)

      if (response.data.success && response.data.data) {
        const newConfig = response.data.data
        
        // 添加到列表
        menuConfigs.value.push(newConfig)
        
        // 更新缓存
        configDetailsCache.value.set(newConfig.menu_key, newConfig)
        
        // 重新构建菜单树
        buildMenuTree()
        
        return newConfig
      } else {
        throw new Error(response.data.error || '创建菜单配置失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '创建菜单配置失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 更新菜单配置
   */
  const updateMenuConfig = async (
    menuKey: string, 
    configData: UpdateMenuConfigRequest
  ): Promise<MenuPermissionConfig> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.put<ApiResponse<MenuPermissionConfig>>(
        `/menu-configs/${menuKey}`,
        configData
      )

      if (response.data.success && response.data.data) {
        const updatedConfig = response.data.data
        
        // 更新列表中的配置
        const index = menuConfigs.value.findIndex(config => config.menu_key === menuKey)
        if (index !== -1) {
          menuConfigs.value[index] = updatedConfig
        }
        
        // 更新缓存
        configDetailsCache.value.set(menuKey, updatedConfig)
        
        // 重新构建菜单树
        buildMenuTree()
        
        return updatedConfig
      } else {
        throw new Error(response.data.error || '更新菜单配置失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '更新菜单配置失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * 删除菜单配置
   */
  const deleteMenuConfig = async (menuKey: string): Promise<void> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.delete<ApiResponse<void>>(`/menu-configs/${menuKey}`)

      if (response.data.success) {
        // 从列表中移除
        menuConfigs.value = menuConfigs.value.filter(config => config.menu_key !== menuKey)
        
        // 从缓存中移除
        configDetailsCache.value.delete(menuKey)
        
        // 重新构建菜单树
        buildMenuTree()
      } else {
        throw new Error(response.data.error || '删除菜单配置失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '删除菜单配置失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // ==================== 菜单树操作方法 ====================
  
  /**
   * 构建菜单树结构
   */
  const buildMenuTree = () => {
    const configMap = new Map<string, MenuPermissionConfig>()
    const rootNodes: MenuTreeNode[] = []
    
    // 创建配置映射
    menuConfigs.value.forEach(config => {
      configMap.set(config.menu_key, config)
    })
    
    // 构建树结构
    menuConfigs.value.forEach(config => {
      if (!config.parent_key) {
        // 根节点
        const node = createTreeNode(config, configMap, 0)
        rootNodes.push(node)
      }
    })
    
    // 按排序顺序排序
    rootNodes.sort((a, b) => a.config.sort_order - b.config.sort_order)
    
    menuTree.value = rootNodes
  }
  
  /**
   * 创建菜单树节点
   */
  const createTreeNode = (
    config: MenuPermissionConfig,
    configMap: Map<string, MenuPermissionConfig>,
    level: number
  ): MenuTreeNode => {
    const children: MenuTreeNode[] = []
    
    // 查找子菜单
    menuConfigs.value
      .filter(c => c.parent_key === config.menu_key)
      .forEach(childConfig => {
        const childNode = createTreeNode(childConfig, configMap, level + 1)
        children.push(childNode)
      })
    
    // 按排序顺序排序子节点
    children.sort((a, b) => a.config.sort_order - b.config.sort_order)
    
    return {
      config,
      children,
      expanded: expandedNodes.value.has(config.menu_key),
      selected: selectedNodes.value.has(config.menu_key),
      draggable: true,
      level,
    }
  }
  
  /**
   * 展开/折叠节点
   */
  const toggleNodeExpanded = (menuKey: string) => {
    if (expandedNodes.value.has(menuKey)) {
      expandedNodes.value.delete(menuKey)
    } else {
      expandedNodes.value.add(menuKey)
    }
    
    // 重新构建树结构以更新展开状态
    buildMenuTree()
  }
  
  /**
   * 选择/取消选择节点
   */
  const toggleNodeSelected = (menuKey: string) => {
    if (selectedNodes.value.has(menuKey)) {
      selectedNodes.value.delete(menuKey)
    } else {
      selectedNodes.value.add(menuKey)
    }
    
    // 重新构建树结构以更新选中状态
    buildMenuTree()
  }
  
  /**
   * 展开所有节点
   */
  const expandAllNodes = () => {
    menuConfigs.value.forEach(config => {
      expandedNodes.value.add(config.menu_key)
    })
    buildMenuTree()
  }
  
  /**
   * 折叠所有节点
   */
  const collapseAllNodes = () => {
    expandedNodes.value.clear()
    buildMenuTree()
  }
  
  /**
   * 选择所有节点
   */
  const selectAllNodes = () => {
    menuConfigs.value.forEach(config => {
      selectedNodes.value.add(config.menu_key)
    })
    buildMenuTree()
  }
  
  /**
   * 取消选择所有节点
   */
  const deselectAllNodes = () => {
    selectedNodes.value.clear()
    buildMenuTree()
  }

  // ==================== 拖拽操作方法 ====================
  
  /**
   * 开始拖拽
   */
  const startDrag = (menuKey: string) => {
    dragState.value.isDragging = true
    dragState.value.draggedNode = menuKey
  }
  
  /**
   * 结束拖拽
   */
  const endDrag = () => {
    dragState.value.isDragging = false
    dragState.value.draggedNode = null
    dragState.value.dropTarget = null
  }
  
  /**
   * 设置拖拽目标
   */
  const setDropTarget = (menuKey: string | null) => {
    dragState.value.dropTarget = menuKey
  }
  
  /**
   * 执行拖拽操作
   */
  const performDragOperation = async (operation: MenuDragOperation): Promise<void> => {
    setLoading(true)
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<void>>('/menu-configs/drag', operation)

      if (response.data.success) {
        // 重新获取菜单配置以更新排序
        await fetchMenuConfigs()
      } else {
        throw new Error(response.data.error || '拖拽操作失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '拖拽操作失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
      endDrag()
    }
  }

  // ==================== 批量操作方法 ====================
  
  /**
   * 批量操作菜单配置
   */
  const batchOperateMenuConfigs = async (request: BatchMenuOperationRequest): Promise<BatchOperationResult> => {
    batchOperationLoading.value = true
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<BatchOperationResult>>(
        '/menu-configs/batch',
        request
      )

      if (response.data.success && response.data.data) {
        const result = response.data.data
        
        // 根据操作类型更新本地状态
        if (request.operation === 'delete' && result.success_ids.length > 0) {
          // 删除操作：从列表中移除成功删除的配置
          menuConfigs.value = menuConfigs.value.filter(
            config => !result.success_ids.includes(config.menu_key)
          )
          
          // 从缓存中移除
          result.success_ids.forEach(key => {
            configDetailsCache.value.delete(key)
          })
          
          // 重新构建菜单树
          buildMenuTree()
        } else if (['show', 'hide', 'enable', 'disable'].includes(request.operation) && result.success_ids.length > 0) {
          // 状态更新操作
          const updates: Partial<MenuPermissionConfig> = {}
          
          if (request.operation === 'show') {
            updates.is_visible = true
            updates.status = 'visible'
          } else if (request.operation === 'hide') {
            updates.is_visible = false
            updates.status = 'hidden'
          } else if (request.operation === 'enable') {
            updates.status = 'visible'
          } else if (request.operation === 'disable') {
            updates.status = 'disabled'
          }
          
          menuConfigs.value.forEach(config => {
            if (result.success_ids.includes(config.menu_key)) {
              Object.assign(config, updates)
              config.updated_at = new Date().toISOString()
            }
          })
          
          // 更新缓存
          result.success_ids.forEach(key => {
            const cachedConfig = configDetailsCache.value.get(key)
            if (cachedConfig) {
              Object.assign(cachedConfig, updates)
              cachedConfig.updated_at = new Date().toISOString()
            }
          })
        }
        
        return result
      } else {
        throw new Error(response.data.error || '批量操作菜单配置失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '批量操作菜单配置失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      batchOperationLoading.value = false
    }
  }

  // ==================== 导入导出方法 ====================
  
  /**
   * 导出菜单配置
   */
  const exportMenuConfigs = async (menuKeys?: string[]): Promise<MenuConfigExport> => {
    importExportLoading.value = true
    clearError()

    try {
      const params = menuKeys ? { menu_keys: menuKeys.join(',') } : {}
      const response = await apiClient.get<ApiResponse<MenuConfigExport>>(
        '/menu-configs/export',
        params
      )

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.error || '导出菜单配置失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '导出菜单配置失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      importExportLoading.value = false
    }
  }
  
  /**
   * 导入菜单配置
   */
  const importMenuConfigs = async (request: MenuConfigImportRequest): Promise<MenuConfigImportResult> => {
    importExportLoading.value = true
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<MenuConfigImportResult>>(
        '/menu-configs/import',
        request
      )

      if (response.data.success && response.data.data) {
        const result = response.data.data
        
        // 如果导入成功，重新获取菜单配置
        if (result.success && result.imported_count > 0) {
          await fetchMenuConfigs()
        }
        
        return result
      } else {
        throw new Error(response.data.error || '导入菜单配置失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '导入菜单配置失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      importExportLoading.value = false
    }
  }

  // ==================== 预览方法 ====================
  
  /**
   * 预览菜单权限
   */
  const previewMenuPermissions = async (config: MenuPreviewConfig): Promise<MenuPreviewResult> => {
    previewLoading.value = true
    clearError()

    try {
      const response = await apiClient.post<ApiResponse<MenuPreviewResult>>(
        '/menu-configs/preview',
        config
      )

      if (response.data.success && response.data.data) {
        previewResult.value = response.data.data
        return response.data.data
      } else {
        throw new Error(response.data.error || '预览菜单权限失败')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || '预览菜单权限失败'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      previewLoading.value = false
    }
  }
  
  /**
   * 清除预览结果
   */
  const clearPreviewResult = () => {
    previewResult.value = null
  }

  // ==================== 辅助方法 ====================
  
  /**
   * 根据菜单键查找配置
   */
  const findConfigByKey = (menuKey: string): MenuPermissionConfig | undefined => {
    return menuConfigs.value.find(config => config.menu_key === menuKey)
  }
  
  /**
   * 检查菜单键是否已存在
   */
  const isMenuKeyExists = (menuKey: string, excludeKey?: string): boolean => {
    return menuConfigs.value.some(config => 
      config.menu_key === menuKey && config.menu_key !== excludeKey
    )
  }
  
  /**
   * 获取菜单的子配置
   */
  const getChildConfigs = (menuKey: string): MenuPermissionConfig[] => {
    return menuConfigs.value.filter(config => config.parent_key === menuKey)
  }
  
  /**
   * 获取菜单的父配置
   */
  const getParentConfig = (menuKey: string): MenuPermissionConfig | undefined => {
    const config = findConfigByKey(menuKey)
    if (!config?.parent_key) return undefined
    return findConfigByKey(config.parent_key)
  }
  
  /**
   * 验证菜单权限
   */
  const validateMenuPermission = (
    menuKey: string, 
    userPermissions: string[]
  ): MenuPermissionResult => {
    const config = findConfigByKey(menuKey)
    
    if (!config) {
      return {
        menu_key: menuKey,
        hasPermission: false,
        isVisible: false,
        message: `菜单配置 ${menuKey} 不存在`,
      }
    }
    
    if (!config.is_visible || config.status !== 'visible') {
      return {
        menu_key: menuKey,
        hasPermission: false,
        isVisible: false,
        message: `菜单 ${config.menu_name} 不可见`,
      }
    }
    
    // 检查权限
    const requiredPermissions = config.required_permissions
    if (requiredPermissions.length === 0) {
      return {
        menu_key: menuKey,
        hasPermission: true,
        isVisible: true,
        message: `菜单 ${config.menu_name} 无需权限`,
      }
    }
    
    const missingPermissions: string[] = []
    let hasPermission = false
    
    if (config.permission_logic === 'AND') {
      // 需要所有权限
      hasPermission = requiredPermissions.every(permission => {
        const has = userPermissions.includes(permission)
        if (!has) missingPermissions.push(permission)
        return has
      })
    } else {
      // 需要任一权限
      hasPermission = requiredPermissions.some(permission => userPermissions.includes(permission))
      if (!hasPermission) {
        missingPermissions.push(...requiredPermissions)
      }
    }
    
    return {
      menu_key: menuKey,
      hasPermission,
      isVisible: hasPermission,
      missingPermissions: missingPermissions.length > 0 ? missingPermissions : undefined,
      message: hasPermission 
        ? `拥有菜单 ${config.menu_name} 的访问权限` 
        : `缺少菜单 ${config.menu_name} 的访问权限`,
    }
  }
  
  /**
   * 清除缓存
   */
  const clearCache = () => {
    configDetailsCache.value.clear()
  }
  
  /**
   * 刷新数据
   */
  const refresh = async () => {
    await fetchMenuConfigs()
  }

  // ==================== 筛选方法 ====================
  
  /**
   * 设置搜索关键词
   */
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
  }
  
  /**
   * 设置菜单类型筛选
   */
  const setMenuTypeFilter = (type: MenuType | '') => {
    menuTypeFilter.value = type
  }
  
  /**
   * 设置菜单状态筛选
   */
  const setStatusFilter = (status: MenuStatus | '') => {
    statusFilter.value = status
  }
  
  /**
   * 设置父菜单筛选
   */
  const setParentFilter = (parent: string) => {
    parentFilter.value = parent
  }
  
  /**
   * 设置根菜单筛选
   */
  const setRootOnlyFilter = (rootOnly: boolean) => {
    rootOnlyFilter.value = rootOnly
  }
  
  /**
   * 设置权限筛选
   */
  const setPermissionFilter = (permission: string) => {
    permissionFilter.value = permission
  }
  
  /**
   * 设置排序
   */
  const setSorting = (field: string, order: 'asc' | 'desc') => {
    sortBy.value = field
    sortOrder.value = order
  }

  return {
    // ==================== 状态 ====================
    menuConfigs,
    menuTree,
    loading,
    error,
    searchQuery,
    menuTypeFilter,
    statusFilter,
    parentFilter,
    rootOnlyFilter,
    permissionFilter,
    sortBy,
    sortOrder,
    batchOperationLoading,
    expandedNodes,
    selectedNodes,
    dragState,
    importExportLoading,
    previewLoading,
    previewResult,

    // ==================== 计算属性 ====================
    filteredMenuConfigs,
    rootMenuConfigs,
    menuConfigsByType,
    visibleMenuConfigs,
    hiddenMenuConfigs,
    availableParentMenus,
    usedPermissions,

    // ==================== 方法 ====================
    // 基础操作
    setLoading,
    setError,
    clearError,
    resetFilters,
    
    // API 调用
    fetchMenuConfigs,
    fetchMenuConfigByKey,
    createMenuConfig,
    updateMenuConfig,
    deleteMenuConfig,
    
    // 菜单树操作
    buildMenuTree,
    toggleNodeExpanded,
    toggleNodeSelected,
    expandAllNodes,
    collapseAllNodes,
    selectAllNodes,
    deselectAllNodes,
    
    // 拖拽操作
    startDrag,
    endDrag,
    setDropTarget,
    performDragOperation,
    
    // 批量操作
    batchOperateMenuConfigs,
    
    // 导入导出
    exportMenuConfigs,
    importMenuConfigs,
    
    // 预览
    previewMenuPermissions,
    clearPreviewResult,
    
    // 辅助方法
    findConfigByKey,
    isMenuKeyExists,
    getChildConfigs,
    getParentConfig,
    validateMenuPermission,
    clearCache,
    refresh,
    
    // 筛选
    setSearchQuery,
    setMenuTypeFilter,
    setStatusFilter,
    setParentFilter,
    setRootOnlyFilter,
    setPermissionFilter,
    setSorting,
  }
})