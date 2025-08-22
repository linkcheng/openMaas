/**
 * 权限管理类型定义入口文件
 * Permission management types entry point
 */

// 角色相关类型
export type {
  RoleType,
  RoleStatus,
  Role,
  CreateRoleRequest,
  UpdateRoleRequest,
  RolePermissionAssignRequest,
  RoleQueryParams,
  RoleStats,
} from './roleTypes'

// 权限相关类型
export type {
  PermissionStatus,
  PermissionAction,
  PermissionResource,
  PermissionModule,
  Permission,
  CreatePermissionRequest,
  UpdatePermissionRequest,
  PermissionQueryParams,
  PermissionTreeNode,
  PermissionTreeDisplayNode,
  PermissionTreeDisplayNodeType,
  PermissionCheckResult,
  PermissionStats,
  BatchPermissionRequest,
  PermissionDependency,
} from './permissionTypes'

// 菜单权限配置相关类型
export type {
  PermissionLogic,
  MenuType,
  MenuStatus,
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
} from './menuTypes'

// 通用类型
export type {
  ApiResponse,
  PaginatedResponse,
  PaginationParams,
  SearchParams,
  FilterParams,
  BaseQueryParams,
  BatchOperationRequest,
  BatchOperationResult,
  OperationLog,
  UserInfo,
  UserRole,
  ErrorDetail,
  ValidationError,
  FormValidationResult,
  ExportConfig,
  ImportConfig,
} from './commonTypes'