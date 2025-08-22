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

import { ref, computed, watch } from 'vue'
import { useMenuConfigStore } from '@/stores/permission/menuConfigStore'
import { usePermissionStore } from '@/stores/permission/permissionStore'
import { useRoleStore } from '@/stores/permission/roleStore'
import { useNotification } from '@/composables/useNotification'
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
  MenuDragOperation,
  BatchMenuOperationRequest,
  MenuType,
  MenuStatus,
  PermissionLogic,
} from '@/types/permission/menuTypes'
import type { Role } from '@/types/permission/roleTypes'
import type { Permission } from '@/types/permission/permissionTypes'
import type { BatchOperationResult } from '@/types/permission/commonTypes'

/**
 * 菜单权限配置业务逻辑组合式函数
 * Menu permission configuration business logic composable
 */
export const useMenuPermissionConfig = () => {
  const menuConfigStore = useMenuConfigStore()
  const permissionStore = usePermissionStore()
  const roleStore = useRoleStore()
  const { showSuccess, showError, showWarning, confirm, confirmDelete, confirmBatchDelete } = useNotification()

  // ==================== 对话框状态 ====================
  
  /** 菜单配置编辑对话框可见性 */
  const configDialogVisible = ref(false)
  
  /** 菜单预览对话框可见性 */
  const previewDialogVisible = ref(false)
  
  /** 导入配置对话框可见性 */
  const importDialogVisible = ref(false)
  
  /** 当前选中的菜单配置 */
  const selectedConfig = ref<MenuPermissionConfig | null>(null)
  
  /** 对话框模式 */
  const dialogMode = ref<'create' | 'edit' | 'view'>('create')
  
  /** 批量选中的菜单键 */
  const selectedMenuKeys = ref<string[]>([])
  
  /** 预览配置 */
  const previewConfig = ref<MenuPreviewConfig>({
    role_id: '',
    user_id: '',
    include_disabled: false,
  })

  // ==================== 表单状态 ====================
  
  /** 菜单配置表单数据 */
  const configFormData = ref<Partial<CreateMenuConfigRequest>>({
    menu_key: '',
    menu_name: '',
    menu_path: '',
    menu_type: 'menu',
    parent_key: undefined,
    required_permissions: [],
    permission_logic: 'AND',
    is_visible: true,
    sort_order: 0,
    icon: '',
    description: '',
  })
  
  /** 表单验证状态 */
  const formValidation = ref({
    menuKeyError: '',
    menuNameError: '',
    menuPathError: '',
    permissionsError: '',
  })
  
  /** 导入表单数据 */
  const importFormData = ref<MenuConfigImportRequest>({
    configs: [],
    merge_strategy: 'replace',
    validate_permissions: true,
    create_missing_parents: true,
  })

  // ==================== 树形结构状态 ====================
  
  /** 树形结构搜索关键词 */
  const treeSearchQuery = ref('')
  
  /** 树形结构展开状态 */
  const treeExpandAll = ref(false)
  
  /** 拖拽状态 */
  const isDragging = ref(false)

  // ==================== 计算属性 ====================
  
  /** 菜单配置列表 */
  const menuConfigs = computed(() => menuConfigStore.menuConfigs)
  
  /** 筛选后的菜单配置列表 */
  const filteredMenuConfigs = computed(() => menuConfigStore.filteredMenuConfigs)
  
  /** 菜单树结构 */
  const menuTree = computed(() => menuConfigStore.menuTree)
  
  /** 根菜单配置列表 */
  const rootMenuConfigs = computed(() => menuConfigStore.rootMenuConfigs)
  
  /** 按类型分组的菜单配置 */
  const menuConfigsByType = computed(() => menuConfigStore.menuConfigsByType)
  
  /** 可见的菜单配置 */
  const visibleMenuConfigs = computed(() => menuConfigStore.visibleMenuConfigs)
  
  /** 隐藏的菜单配置 */
  const hiddenMenuConfigs = computed(() => menuConfigStore.hiddenMenuConfigs)
  
  /** 可用的父菜单选项 */
  const availableParentMenus = computed(() => menuConfigStore.availableParentMenus)
  
  /** 所有使用的权限列表 */
  const usedPermissions = computed(() => menuConfigStore.usedPermissions)
  
  /** 加载状态 */
  const loading = computed(() => menuConfigStore.loading)
  
  /** 批量操作加载状态 */
  const batchLoading = computed(() => menuConfigStore.batchOperationLoading)
  
  /** 导入导出加载状态 */
  const importExportLoading = computed(() => menuConfigStore.importExportLoading)
  
  /** 预览加载状态 */
  const previewLoading = computed(() => menuConfigStore.previewLoading)
  
  /** 错误信息 */
  const error = computed(() => menuConfigStore.error)
  
  /** 筛选条件 */
  const filters = computed(() => ({
    searchQuery: menuConfigStore.searchQuery,
    menuTypeFilter: menuConfigStore.menuTypeFilter,
    statusFilter: menuConfigStore.statusFilter,
    parentFilter: menuConfigStore.parentFilter,
    rootOnlyFilter: menuConfigStore.rootOnlyFilter,
    permissionFilter: menuConfigStore.permissionFilter,
  }))
  
  /** 排序信息 */
  const sorting = computed(() => ({
    sortBy: menuConfigStore.sortBy,
    sortOrder: menuConfigStore.sortOrder,
  }))
  
  /** 是否有选中的菜单 */
  const hasSelectedMenus = computed(() => selectedMenuKeys.value.length > 0)
  
  /** 选中菜单数量 */
  const selectedMenuCount = computed(() => selectedMenuKeys.value.length)
  
  /** 可用的权限列表 */
  const availablePermissions = computed(() => permissionStore.activePermissions)
  
  /** 可用的角色列表 */
  const availableRoles = computed(() => roleStore.activeRoles)
  
  /** 预览结果 */
  const previewResult = computed(() => menuConfigStore.previewResult)
  
  /** 筛选后的菜单树 */
  const filteredMenuTree = computed(() => {
    if (!treeSearchQuery.value) return menuTree.value
    
    const query = treeSearchQuery.value.toLowerCase()
    return filterTreeNodes(menuTree.value, query)
  })

  // ==================== 初始化和数据获取 ====================
  
  /**
   * 初始化菜单权限配置管理
   */
  const initialize = async () => {
    try {
      await Promise.all([
        menuConfigStore.fetchMenuConfigs(),
        permissionStore.fetchPermissions(),
        roleStore.fetchRoles(),
      ])
    } catch (err) {
      console.error('初始化菜单权限配置管理失败:', err)
      showError('初始化菜单权限配置管理失败')
    }
  }
  
  /**
   * 刷新菜单配置列表
   */
  const refresh = async () => {
    try {
      await menuConfigStore.refresh()
      showSuccess('菜单配置列表已刷新')
    } catch (err) {
      console.error('刷新菜单配置列表失败:', err)
      showError('刷新菜单配置列表失败')
    }
  }
  
  /**
   * 获取菜单配置详情
   */
  const fetchConfigDetails = async (menuKey: string, useCache = true): Promise<MenuPermissionConfig | null> => {
    try {
      return await menuConfigStore.fetchMenuConfigByKey(menuKey, useCache)
    } catch (err) {
      console.error('获取菜单配置详情失败:', err)
      showError('获取菜单配置详情失败')
      return null
    }
  }

  // ==================== 菜单配置CRUD操作 ====================
  
  /**
   * 打开创建菜单配置对话框
   */
  const openCreateDialog = (parentConfig?: MenuPermissionConfig) => {
    selectedConfig.value = null
    dialogMode.value = 'create'
    configFormData.value = {
      menu_key: '',
      menu_name: '',
      menu_path: '',
      menu_type: 'menu',
      parent_key: parentConfig?.menu_key,
      required_permissions: [],
      permission_logic: 'AND',
      is_visible: true,
      sort_order: getNextSortOrder(parentConfig?.menu_key),
      icon: '',
      description: '',
    }
    clearFormValidation()
    configDialogVisible.value = true
  }
  
  /**
   * 打开编辑菜单配置对话框
   */
  const openEditDialog = (config: MenuPermissionConfig) => {
    selectedConfig.value = config
    dialogMode.value = 'edit'
    configFormData.value = {
      menu_key: config.menu_key,
      menu_name: config.menu_name,
      menu_path: config.menu_path,
      menu_type: config.menu_type,
      parent_key: config.parent_key,
      required_permissions: [...config.required_permissions],
      permission_logic: config.permission_logic,
      is_visible: config.is_visible,
      sort_order: config.sort_order,
      icon: config.icon,
      description: config.description,
    }
    clearFormValidation()
    configDialogVisible.value = true
  }
  
  /**
   * 打开查看菜单配置对话框
   */
  const openViewDialog = (config: MenuPermissionConfig) => {
    selectedConfig.value = config
    dialogMode.value = 'view'
    configDialogVisible.value = true
  }
  
  /**
   * 创建菜单配置
   */
  const createMenuConfig = async (configData: CreateMenuConfigRequest): Promise<boolean> => {
    try {
      // 验证表单
      if (!validateConfigForm(configData)) {
        return false
      }
      
      const newConfig = await menuConfigStore.createMenuConfig(configData)
      showSuccess(`菜单配置 "${newConfig.menu_name}" 创建成功`)
      configDialogVisible.value = false
      return true
    } catch (err) {
      console.error('创建菜单配置失败:', err)
      showError('创建菜单配置失败')
      return false
    }
  }
  
  /**
   * 更新菜单配置
   */
  const updateMenuConfig = async (menuKey: string, configData: UpdateMenuConfigRequest): Promise<boolean> => {
    try {
      // 验证表单
      if (!validateConfigForm(configData)) {
        return false
      }
      
      const updatedConfig = await menuConfigStore.updateMenuConfig(menuKey, configData)
      showSuccess(`菜单配置 "${updatedConfig.menu_name}" 更新成功`)
      configDialogVisible.value = false
      return true
    } catch (err) {
      console.error('更新菜单配置失败:', err)
      showError('更新菜单配置失败')
      return false
    }
  }
  
  /**
   * 删除菜单配置
   */
  const deleteMenuConfig = async (config: MenuPermissionConfig): Promise<boolean> => {
    try {
      // 检查是否有子菜单
      const childConfigs = menuConfigStore.getChildConfigs(config.menu_key)
      if (childConfigs.length > 0) {
        showWarning(`菜单 "${config.menu_name}" 有 ${childConfigs.length} 个子菜单，请先删除子菜单`)
        return false
      }
      
      // 确认删除
      const confirmed = await confirmDelete(
        config.menu_name,
        `确定要删除菜单配置 "${config.menu_name}" 吗？此操作不可撤销。`
      )
      
      if (!confirmed) return false
      
      await menuConfigStore.deleteMenuConfig(config.menu_key)
      showSuccess(`菜单配置 "${config.menu_name}" 删除成功`)
      return true
    } catch (err) {
      console.error('删除菜单配置失败:', err)
      showError('删除菜单配置失败')
      return false
    }
  }

  // ==================== 批量操作 ====================
  
  /**
   * 批量删除菜单配置
   */
  const batchDeleteMenuConfigs = async (): Promise<boolean> => {
    try {
      if (!hasSelectedMenus.value) {
        showWarning('请选择要删除的菜单配置')
        return false
      }
      
      // 确认批量删除
      const confirmed = await confirmBatchDelete(selectedMenuCount.value)
      if (!confirmed) return false
      
      const request: BatchMenuOperationRequest = {
        menu_keys: selectedMenuKeys.value,
        operation: 'delete',
      }
      
      const result = await menuConfigStore.batchOperateMenuConfigs(request)
      
      if (result.success_ids.length > 0) {
        showSuccess(`成功删除 ${result.success_ids.length} 个菜单配置`)
      }
      
      if (result.failed_ids.length > 0) {
        showWarning(`${result.failed_ids.length} 个菜单配置删除失败`)
      }
      
      // 清空选择
      selectedMenuKeys.value = []
      return true
    } catch (err) {
      console.error('批量删除菜单配置失败:', err)
      showError('批量删除菜单配置失败')
      return false
    }
  }
  
  /**
   * 批量显示菜单配置
   */
  const batchShowMenuConfigs = async (): Promise<boolean> => {
    try {
      if (!hasSelectedMenus.value) {
        showWarning('请选择要显示的菜单配置')
        return false
      }
      
      const request: BatchMenuOperationRequest = {
        menu_keys: selectedMenuKeys.value,
        operation: 'show',
      }
      
      const result = await menuConfigStore.batchOperateMenuConfigs(request)
      
      if (result.success_ids.length > 0) {
        showSuccess(`成功显示 ${result.success_ids.length} 个菜单配置`)
      }
      
      if (result.failed_ids.length > 0) {
        showWarning(`${result.failed_ids.length} 个菜单配置显示失败`)
      }
      
      // 清空选择
      selectedMenuKeys.value = []
      return true
    } catch (err) {
      console.error('批量显示菜单配置失败:', err)
      showError('批量显示菜单配置失败')
      return false
    }
  }
  
  /**
   * 批量隐藏菜单配置
   */
  const batchHideMenuConfigs = async (): Promise<boolean> => {
    try {
      if (!hasSelectedMenus.value) {
        showWarning('请选择要隐藏的菜单配置')
        return false
      }
      
      const request: BatchMenuOperationRequest = {
        menu_keys: selectedMenuKeys.value,
        operation: 'hide',
      }
      
      const result = await menuConfigStore.batchOperateMenuConfigs(request)
      
      if (result.success_ids.length > 0) {
        showSuccess(`成功隐藏 ${result.success_ids.length} 个菜单配置`)
      }
      
      if (result.failed_ids.length > 0) {
        showWarning(`${result.failed_ids.length} 个菜单配置隐藏失败`)
      }
      
      // 清空选择
      selectedMenuKeys.value = []
      return true
    } catch (err) {
      console.error('批量隐藏菜单配置失败:', err)
      showError('批量隐藏菜单配置失败')
      return false
    }
  }

  // ==================== 导入导出操作 ====================
  
  /**
   * 导出菜单配置
   */
  const exportMenuConfigs = async (menuKeys?: string[]): Promise<boolean> => {
    try {
      const exportData = await menuConfigStore.exportMenuConfigs(menuKeys)
      
      // 创建下载链接
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `menu-configs-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      showSuccess('菜单配置导出成功')
      return true
    } catch (err) {
      console.error('导出菜单配置失败:', err)
      showError('导出菜单配置失败')
      return false
    }
  }
  
  /**
   * 打开导入配置对话框
   */
  const openImportDialog = () => {
    importFormData.value = {
      configs: [],
      merge_strategy: 'replace',
      validate_permissions: true,
      create_missing_parents: true,
    }
    importDialogVisible.value = true
  }
  
  /**
   * 导入菜单配置
   */
  const importMenuConfigs = async (request: MenuConfigImportRequest): Promise<boolean> => {
    try {
      const result = await menuConfigStore.importMenuConfigs(request)
      
      if (result.success) {
        showSuccess(`成功导入 ${result.imported_count} 个菜单配置`)
        importDialogVisible.value = false
        
        if (result.warnings && result.warnings.length > 0) {
          showWarning(`导入时有 ${result.warnings.length} 个警告`)
        }
        
        return true
      } else {
        showError(`导入失败: ${result.error}`)
        return false
      }
    } catch (err) {
      console.error('导入菜单配置失败:', err)
      showError('导入菜单配置失败')
      return false
    }
  }
  
  /**
   * 处理文件上传
   */
  const handleFileUpload = (file: File): Promise<MenuPermissionConfig[]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string
          const data = JSON.parse(content)
          
          // 验证数据格式
          if (Array.isArray(data)) {
            resolve(data)
          } else if (data.configs && Array.isArray(data.configs)) {
            resolve(data.configs)
          } else {
            reject(new Error('无效的文件格式'))
          }
        } catch (error) {
          reject(new Error('文件解析失败'))
        }
      }
      
      reader.onerror = () => {
        reject(new Error('文件读取失败'))
      }
      
      reader.readAsText(file)
    })
  }

  // ==================== 预览功能 ====================
  
  /**
   * 打开菜单预览对话框
   */
  const openPreviewDialog = () => {
    previewConfig.value = {
      role_id: '',
      user_id: '',
      include_disabled: false,
    }
    previewDialogVisible.value = true
  }
  
  /**
   * 预览菜单权限
   */
  const previewMenuPermissions = async (config: MenuPreviewConfig): Promise<boolean> => {
    try {
      await menuConfigStore.previewMenuPermissions(config)
      showSuccess('菜单预览生成成功')
      return true
    } catch (err) {
      console.error('预览菜单权限失败:', err)
      showError('预览菜单权限失败')
      return false
    }
  }
  
  /**
   * 清除预览结果
   */
  const clearPreviewResult = () => {
    menuConfigStore.clearPreviewResult()
  }

  // ==================== 搜索和筛选 ====================
  
  /**
   * 设置搜索关键词
   */
  const setSearchQuery = (query: string) => {
    menuConfigStore.setSearchQuery(query)
  }
  
  /**
   * 设置菜单类型筛选
   */
  const setMenuTypeFilter = (type: MenuType | '') => {
    menuConfigStore.setMenuTypeFilter(type)
  }
  
  /**
   * 设置菜单状态筛选
   */
  const setStatusFilter = (status: MenuStatus | '') => {
    menuConfigStore.setStatusFilter(status)
  }
  
  /**
   * 设置父菜单筛选
   */
  const setParentFilter = (parent: string) => {
    menuConfigStore.setParentFilter(parent)
  }
  
  /**
   * 设置根菜单筛选
   */
  const setRootOnlyFilter = (rootOnly: boolean) => {
    menuConfigStore.setRootOnlyFilter(rootOnly)
  }
  
  /**
   * 设置权限筛选
   */
  const setPermissionFilter = (permission: string) => {
    menuConfigStore.setPermissionFilter(permission)
  }
  
  /**
   * 重置筛选条件
   */
  const resetFilters = () => {
    menuConfigStore.resetFilters()
  }

  // ==================== 排序操作 ====================
  
  /**
   * 设置排序
   */
  const setSorting = (field: string, order: 'asc' | 'desc') => {
    menuConfigStore.setSorting(field, order)
    menuConfigStore.fetchMenuConfigs()
  }

  // ==================== 树形结构操作 ====================
  
  /**
   * 展开/折叠节点
   */
  const toggleNodeExpanded = (menuKey: string) => {
    menuConfigStore.toggleNodeExpanded(menuKey)
  }
  
  /**
   * 选择/取消选择节点
   */
  const toggleNodeSelected = (menuKey: string) => {
    menuConfigStore.toggleNodeSelected(menuKey)
    
    // 同步到批量选择
    if (menuConfigStore.selectedNodes.has(menuKey)) {
      if (!selectedMenuKeys.value.includes(menuKey)) {
        selectedMenuKeys.value.push(menuKey)
      }
    } else {
      const index = selectedMenuKeys.value.indexOf(menuKey)
      if (index > -1) {
        selectedMenuKeys.value.splice(index, 1)
      }
    }
  }
  
  /**
   * 展开所有节点
   */
  const expandAllNodes = () => {
    menuConfigStore.expandAllNodes()
    treeExpandAll.value = true
  }
  
  /**
   * 折叠所有节点
   */
  const collapseAllNodes = () => {
    menuConfigStore.collapseAllNodes()
    treeExpandAll.value = false
  }
  
  /**
   * 选择所有节点
   */
  const selectAllNodes = () => {
    menuConfigStore.selectAllNodes()
    selectedMenuKeys.value = menuConfigs.value.map(config => config.menu_key)
  }
  
  /**
   * 取消选择所有节点
   */
  const deselectAllNodes = () => {
    menuConfigStore.deselectAllNodes()
    selectedMenuKeys.value = []
  }
  
  /**
   * 设置树形搜索关键词
   */
  const setTreeSearchQuery = (query: string) => {
    treeSearchQuery.value = query
  }

  // ==================== 拖拽操作 ====================
  
  /**
   * 开始拖拽
   */
  const startDrag = (menuKey: string) => {
    menuConfigStore.startDrag(menuKey)
    isDragging.value = true
  }
  
  /**
   * 结束拖拽
   */
  const endDrag = () => {
    menuConfigStore.endDrag()
    isDragging.value = false
  }
  
  /**
   * 设置拖拽目标
   */
  const setDropTarget = (menuKey: string | null) => {
    menuConfigStore.setDropTarget(menuKey)
  }
  
  /**
   * 执行拖拽操作
   */
  const performDragOperation = async (operation: MenuDragOperation): Promise<boolean> => {
    try {
      await menuConfigStore.performDragOperation(operation)
      showSuccess('菜单排序更新成功')
      return true
    } catch (err) {
      console.error('拖拽操作失败:', err)
      showError('拖拽操作失败')
      return false
    }
  }

  // ==================== 选择操作 ====================
  
  /**
   * 选择菜单
   */
  const selectMenu = (menuKey: string) => {
    if (!selectedMenuKeys.value.includes(menuKey)) {
      selectedMenuKeys.value.push(menuKey)
    }
  }
  
  /**
   * 取消选择菜单
   */
  const unselectMenu = (menuKey: string) => {
    const index = selectedMenuKeys.value.indexOf(menuKey)
    if (index > -1) {
      selectedMenuKeys.value.splice(index, 1)
    }
  }
  
  /**
   * 切换菜单选择状态
   */
  const toggleMenuSelection = (menuKey: string) => {
    if (selectedMenuKeys.value.includes(menuKey)) {
      unselectMenu(menuKey)
    } else {
      selectMenu(menuKey)
    }
  }
  
  /**
   * 全选/取消全选
   */
  const toggleSelectAll = () => {
    if (selectedMenuKeys.value.length === filteredMenuConfigs.value.length) {
      // 当前全选，取消全选
      selectedMenuKeys.value = []
    } else {
      // 全选当前筛选的菜单配置
      selectedMenuKeys.value = filteredMenuConfigs.value.map(config => config.menu_key)
    }
  }
  
  /**
   * 清空选择
   */
  const clearSelection = () => {
    selectedMenuKeys.value = []
  }

  // ==================== 表单验证 ====================
  
  /**
   * 验证菜单配置表单
   */
  const validateConfigForm = (configData: Partial<CreateMenuConfigRequest | UpdateMenuConfigRequest>): boolean => {
    clearFormValidation()
    let isValid = true
    
    // 验证菜单键
    if (!configData.menu_key || configData.menu_key.trim() === '') {
      formValidation.value.menuKeyError = '菜单键不能为空'
      isValid = false
    } else if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(configData.menu_key)) {
      formValidation.value.menuKeyError = '菜单键只能包含字母、数字、下划线和连字符，且必须以字母开头'
      isValid = false
    } else if (menuConfigStore.isMenuKeyExists(configData.menu_key, selectedConfig.value?.menu_key)) {
      formValidation.value.menuKeyError = '菜单键已存在'
      isValid = false
    }
    
    // 验证菜单名称
    if (!configData.menu_name || configData.menu_name.trim() === '') {
      formValidation.value.menuNameError = '菜单名称不能为空'
      isValid = false
    }
    
    // 验证菜单路径
    if (configData.menu_type === 'menu' && (!configData.menu_path || configData.menu_path.trim() === '')) {
      formValidation.value.menuPathError = '菜单类型为菜单时，菜单路径不能为空'
      isValid = false
    }
    
    return isValid
  }
  
  /**
   * 清除表单验证错误
   */
  const clearFormValidation = () => {
    formValidation.value = {
      menuKeyError: '',
      menuNameError: '',
      menuPathError: '',
      permissionsError: '',
    }
  }

  // ==================== 辅助方法 ====================
  
  /**
   * 根据菜单键查找配置
   */
  const findConfigByKey = (menuKey: string): MenuPermissionConfig | undefined => {
    return menuConfigStore.findConfigByKey(menuKey)
  }
  
  /**
   * 检查菜单是否被选中
   */
  const isMenuSelected = (menuKey: string): boolean => {
    return selectedMenuKeys.value.includes(menuKey)
  }
  
  /**
   * 获取菜单的子配置
   */
  const getChildConfigs = (menuKey: string): MenuPermissionConfig[] => {
    return menuConfigStore.getChildConfigs(menuKey)
  }
  
  /**
   * 获取菜单的父配置
   */
  const getParentConfig = (menuKey: string): MenuPermissionConfig | undefined => {
    return menuConfigStore.getParentConfig(menuKey)
  }
  
  /**
   * 获取下一个排序顺序
   */
  const getNextSortOrder = (parentKey?: string): number => {
    const siblings = parentKey 
      ? menuConfigs.value.filter(config => config.parent_key === parentKey)
      : rootMenuConfigs.value
    
    if (siblings.length === 0) return 0
    
    const maxOrder = Math.max(...siblings.map(config => config.sort_order))
    return maxOrder + 1
  }
  
  /**
   * 获取菜单类型显示文本
   */
  const getMenuTypeText = (type: MenuType): string => {
    const typeMap: Record<MenuType, string> = {
      menu: '菜单',
      button: '按钮',
      tab: '标签页',
      section: '区域',
    }
    return typeMap[type] || type
  }
  
  /**
   * 获取菜单状态显示文本
   */
  const getMenuStatusText = (status: MenuStatus): string => {
    const statusMap: Record<MenuStatus, string> = {
      visible: '可见',
      hidden: '隐藏',
      disabled: '禁用',
    }
    return statusMap[status] || status
  }
  
  /**
   * 获取权限逻辑显示文本
   */
  const getPermissionLogicText = (logic: PermissionLogic): string => {
    const logicMap: Record<PermissionLogic, string> = {
      AND: '需要所有权限',
      OR: '需要任一权限',
    }
    return logicMap[logic] || logic
  }
  
  /**
   * 验证菜单权限
   */
  const validateMenuPermission = (menuKey: string, userPermissions: string[]): MenuPermissionResult => {
    return menuConfigStore.validateMenuPermission(menuKey, userPermissions)
  }
  
  /**
   * 筛选树形节点
   */
  const filterTreeNodes = (nodes: MenuTreeNode[], query: string): MenuTreeNode[] => {
    return nodes.filter(node => {
      const matchesQuery = 
        node.config.menu_name.toLowerCase().includes(query) ||
        node.config.menu_key.toLowerCase().includes(query) ||
        node.config.menu_path.toLowerCase().includes(query)
      
      const hasMatchingChildren = node.children && filterTreeNodes(node.children, query).length > 0
      
      if (matchesQuery || hasMatchingChildren) {
        return {
          ...node,
          children: hasMatchingChildren ? filterTreeNodes(node.children!, query) : node.children,
        }
      }
      
      return false
    }).filter(Boolean) as MenuTreeNode[]
  }

  // ==================== 监听器 ====================
  
  // 监听搜索关键词变化，自动触发搜索
  watch(
    () => menuConfigStore.searchQuery,
    (newQuery) => {
      if (newQuery !== undefined) {
        // 延迟搜索，避免频繁请求
        setTimeout(() => {
          menuConfigStore.fetchMenuConfigs()
        }, 300)
      }
    }
  )
  
  // 监听筛选条件变化，自动刷新列表
  watch(
    [
      () => menuConfigStore.menuTypeFilter,
      () => menuConfigStore.statusFilter,
      () => menuConfigStore.parentFilter,
      () => menuConfigStore.rootOnlyFilter,
      () => menuConfigStore.permissionFilter,
    ],
    () => {
      menuConfigStore.fetchMenuConfigs()
    }
  )

  return {
    // ==================== 状态 ====================
    configDialogVisible,
    previewDialogVisible,
    importDialogVisible,
    selectedConfig,
    dialogMode,
    selectedMenuKeys,
    previewConfig,
    configFormData,
    formValidation,
    importFormData,
    treeSearchQuery,
    treeExpandAll,
    isDragging,

    // ==================== 计算属性 ====================
    menuConfigs,
    filteredMenuConfigs,
    menuTree,
    filteredMenuTree,
    rootMenuConfigs,
    menuConfigsByType,
    visibleMenuConfigs,
    hiddenMenuConfigs,
    availableParentMenus,
    usedPermissions,
    loading,
    batchLoading,
    importExportLoading,
    previewLoading,
    error,
    filters,
    sorting,
    hasSelectedMenus,
    selectedMenuCount,
    availablePermissions,
    availableRoles,
    previewResult,

    // ==================== 方法 ====================
    // 初始化和数据获取
    initialize,
    refresh,
    fetchConfigDetails,

    // 菜单配置CRUD操作
    openCreateDialog,
    openEditDialog,
    openViewDialog,
    createMenuConfig,
    updateMenuConfig,
    deleteMenuConfig,

    // 批量操作
    batchDeleteMenuConfigs,
    batchShowMenuConfigs,
    batchHideMenuConfigs,

    // 导入导出操作
    exportMenuConfigs,
    openImportDialog,
    importMenuConfigs,
    handleFileUpload,

    // 预览功能
    openPreviewDialog,
    previewMenuPermissions,
    clearPreviewResult,

    // 搜索和筛选
    setSearchQuery,
    setMenuTypeFilter,
    setStatusFilter,
    setParentFilter,
    setRootOnlyFilter,
    setPermissionFilter,
    resetFilters,

    // 排序操作
    setSorting,

    // 树形结构操作
    toggleNodeExpanded,
    toggleNodeSelected,
    expandAllNodes,
    collapseAllNodes,
    selectAllNodes,
    deselectAllNodes,
    setTreeSearchQuery,

    // 拖拽操作
    startDrag,
    endDrag,
    setDropTarget,
    performDragOperation,

    // 选择操作
    selectMenu,
    unselectMenu,
    toggleMenuSelection,
    toggleSelectAll,
    clearSelection,

    // 表单验证
    validateConfigForm,
    clearFormValidation,

    // 辅助方法
    findConfigByKey,
    isMenuSelected,
    getChildConfigs,
    getParentConfig,
    getNextSortOrder,
    getMenuTypeText,
    getMenuStatusText,
    getPermissionLogicText,
    validateMenuPermission,
  }
}