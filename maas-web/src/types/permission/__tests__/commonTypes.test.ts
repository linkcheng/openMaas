/**
 * 权限管理通用类型定义单元测试
 * Unit tests for common permission management type definitions
 */

import { describe, it, expect } from 'vitest'
import type {
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
} from '../commonTypes'

describe('Common Types', () => {
  describe('ApiResponse interface', () => {
    it('should accept successful API response', () => {
      const successResponse: ApiResponse<string> = {
        success: true,
        data: 'test data',
        message: '操作成功',
        code: 200,
        request_id: 'req-123',
        timestamp: '2024-01-01T00:00:00Z',
      }

      expect(successResponse.success).toBe(true)
      expect(successResponse.data).toBe('test data')
      expect(successResponse.message).toBe('操作成功')
      expect(successResponse.code).toBe(200)
    })

    it('should accept error API response', () => {
      const errorResponse: ApiResponse = {
        success: false,
        error: '操作失败',
        message: '请求处理失败',
        code: 400,
        request_id: 'req-456',
        timestamp: '2024-01-01T00:00:00Z',
      }

      expect(errorResponse.success).toBe(false)
      expect(errorResponse.error).toBe('操作失败')
      expect(errorResponse.data).toBeUndefined()
    })

    it('should accept minimal API response', () => {
      const minimalResponse: ApiResponse = {
        success: true,
      }

      expect(minimalResponse.success).toBe(true)
      expect(minimalResponse.data).toBeUndefined()
      expect(minimalResponse.error).toBeUndefined()
    })
  })

  describe('PaginatedResponse interface', () => {
    it('should accept valid paginated response', () => {
      const paginatedResponse: PaginatedResponse<string> = {
        items: ['item1', 'item2', 'item3'],
        total: 100,
        page: 1,
        page_size: 10,
        total_pages: 10,
        has_next: true,
        has_prev: false,
        next_page: 2,
      }

      expect(paginatedResponse.items).toHaveLength(3)
      expect(paginatedResponse.total).toBe(100)
      expect(paginatedResponse.page).toBe(1)
      expect(paginatedResponse.page_size).toBe(10)
      expect(paginatedResponse.total_pages).toBe(10)
      expect(paginatedResponse.has_next).toBe(true)
      expect(paginatedResponse.has_prev).toBe(false)
    })

    it('should calculate pagination correctly', () => {
      const response: PaginatedResponse<number> = {
        items: [1, 2, 3, 4, 5],
        total: 25,
        page: 2,
        page_size: 5,
        total_pages: 5,
        has_next: true,
        has_prev: true,
        next_page: 3,
        prev_page: 1,
      }

      expect(response.total_pages).toBe(Math.ceil(response.total / response.page_size))
      expect(response.has_prev).toBe(response.page > 1)
      expect(response.has_next).toBe(response.page < response.total_pages)
    })
  })

  describe('PaginationParams interface', () => {
    it('should accept valid pagination parameters', () => {
      const paginationParams: PaginationParams = {
        page: 1,
        page_size: 20,
        sort_by: 'created_at',
        sort_order: 'desc',
      }

      expect(paginationParams.page).toBe(1)
      expect(paginationParams.page_size).toBe(20)
      expect(paginationParams.sort_by).toBe('created_at')
      expect(paginationParams.sort_order).toBe('desc')
    })

    it('should accept empty pagination parameters', () => {
      const emptyParams: PaginationParams = {}

      expect(Object.keys(emptyParams)).toHaveLength(0)
    })
  })

  describe('SearchParams interface', () => {
    it('should accept valid search parameters', () => {
      const searchParams: SearchParams = {
        search: 'test query',
        search_fields: ['name', 'description'],
        exact_match: false,
        case_sensitive: true,
      }

      expect(searchParams.search).toBe('test query')
      expect(searchParams.search_fields).toEqual(['name', 'description'])
      expect(searchParams.exact_match).toBe(false)
      expect(searchParams.case_sensitive).toBe(true)
    })
  })

  describe('FilterParams interface', () => {
    it('should accept valid filter parameters', () => {
      const filterParams: FilterParams = {
        filters: {
          status: 'active',
          type: 'system',
        },
        date_range: {
          start_date: '2024-01-01',
          end_date: '2024-12-31',
          field: 'created_at',
        },
        status: ['active', 'inactive'],
        tags: ['important', 'system'],
      }

      expect(filterParams.filters).toEqual({ status: 'active', type: 'system' })
      expect(filterParams.date_range?.start_date).toBe('2024-01-01')
      expect(filterParams.status).toEqual(['active', 'inactive'])
      expect(filterParams.tags).toEqual(['important', 'system'])
    })
  })

  describe('BatchOperationRequest interface', () => {
    it('should accept valid batch operation request', () => {
      const batchRequest: BatchOperationRequest<{ reason: string }> = {
        ids: ['id1', 'id2', 'id3'],
        operation: 'delete',
        params: { reason: 'cleanup' },
        force: true,
      }

      expect(batchRequest.ids).toEqual(['id1', 'id2', 'id3'])
      expect(batchRequest.operation).toBe('delete')
      expect(batchRequest.params?.reason).toBe('cleanup')
      expect(batchRequest.force).toBe(true)
    })
  })

  describe('BatchOperationResult interface', () => {
    it('should accept valid batch operation result', () => {
      const batchResult: BatchOperationResult = {
        success: true,
        success_count: 8,
        failed_count: 2,
        skipped_count: 0,
        success_ids: ['id1', 'id2', 'id3', 'id4', 'id5', 'id6', 'id7', 'id8'],
        failed_ids: ['id9', 'id10'],
        errors: [
          { id: 'id9', error: '权限不足' },
          { id: 'id10', error: '资源不存在' },
        ],
        warnings: [
          { id: 'id1', warning: '操作可能影响其他用户' },
        ],
      }

      expect(batchResult.success).toBe(true)
      expect(batchResult.success_count).toBe(8)
      expect(batchResult.failed_count).toBe(2)
      expect(batchResult.success_ids).toHaveLength(8)
      expect(batchResult.failed_ids).toHaveLength(2)
      expect(batchResult.errors).toHaveLength(2)
      expect(batchResult.warnings).toHaveLength(1)
    })
  })

  describe('OperationLog interface', () => {
    it('should accept valid operation log', () => {
      const operationLog: OperationLog = {
        id: 'log-123',
        operation: 'create_role',
        target_type: 'role',
        target_id: 'role-456',
        operator_id: 'user-789',
        operator: {
          id: 'user-789',
          username: 'admin',
          display_name: '系统管理员',
        },
        description: '创建新角色: 编辑者',
        before_data: null,
        after_data: {
          name: 'editor',
          display_name: '编辑者',
          permissions: ['content.edit'],
        },
        result: 'success',
        created_at: '2024-01-01T00:00:00Z',
        client_ip: '192.168.1.100',
        user_agent: 'Mozilla/5.0...',
      }

      expect(operationLog.id).toBe('log-123')
      expect(operationLog.operation).toBe('create_role')
      expect(operationLog.target_type).toBe('role')
      expect(operationLog.result).toBe('success')
      expect(operationLog.operator.username).toBe('admin')
    })
  })

  describe('UserInfo interface', () => {
    it('should accept valid user info', () => {
      const userInfo: UserInfo = {
        id: 'user-123',
        username: 'john_doe',
        email: 'john@example.com',
        profile: {
          full_name: 'John Doe',
          avatar_url: 'https://example.com/avatar.jpg',
          department: 'IT',
          position: '软件工程师',
        },
        status: 'active',
        last_login_at: '2024-01-01T12:00:00Z',
        created_at: '2023-01-01T00:00:00Z',
      }

      expect(userInfo.id).toBe('user-123')
      expect(userInfo.username).toBe('john_doe')
      expect(userInfo.email).toBe('john@example.com')
      expect(userInfo.profile.full_name).toBe('John Doe')
      expect(userInfo.status).toBe('active')
    })
  })

  describe('ValidationError interface', () => {
    it('should accept valid validation error', () => {
      const validationError: ValidationError = {
        field: 'email',
        message: '邮箱格式不正确',
        code: 'INVALID_EMAIL',
        rejected_value: 'invalid-email',
      }

      expect(validationError.field).toBe('email')
      expect(validationError.message).toBe('邮箱格式不正确')
      expect(validationError.code).toBe('INVALID_EMAIL')
      expect(validationError.rejected_value).toBe('invalid-email')
    })
  })

  describe('FormValidationResult interface', () => {
    it('should accept valid form validation result', () => {
      const validationResult: FormValidationResult = {
        valid: false,
        errors: [
          {
            field: 'name',
            message: '名称不能为空',
            code: 'REQUIRED',
          },
          {
            field: 'email',
            message: '邮箱格式不正确',
            code: 'INVALID_FORMAT',
          },
        ],
        warnings: [
          {
            field: 'password',
            message: '密码强度较弱',
            code: 'WEAK_PASSWORD',
          },
        ],
      }

      expect(validationResult.valid).toBe(false)
      expect(validationResult.errors).toHaveLength(2)
      expect(validationResult.warnings).toHaveLength(1)
    })

    it('should accept successful validation result', () => {
      const successResult: FormValidationResult = {
        valid: true,
        errors: [],
      }

      expect(successResult.valid).toBe(true)
      expect(successResult.errors).toHaveLength(0)
      expect(successResult.warnings).toBeUndefined()
    })
  })

  describe('ExportConfig interface', () => {
    it('should accept valid export config', () => {
      const exportConfig: ExportConfig = {
        format: 'json',
        fields: ['id', 'name', 'email', 'created_at'],
        filters: { status: 'active' },
        include_relations: true,
        filename: 'users_export_2024.json',
      }

      expect(exportConfig.format).toBe('json')
      expect(exportConfig.fields).toEqual(['id', 'name', 'email', 'created_at'])
      expect(exportConfig.filters).toEqual({ status: 'active' })
      expect(exportConfig.include_relations).toBe(true)
      expect(exportConfig.filename).toBe('users_export_2024.json')
    })

    it('should accept different export formats', () => {
      const jsonConfig: ExportConfig = { format: 'json' }
      const csvConfig: ExportConfig = { format: 'csv' }
      const excelConfig: ExportConfig = { format: 'excel' }

      expect(jsonConfig.format).toBe('json')
      expect(csvConfig.format).toBe('csv')
      expect(excelConfig.format).toBe('excel')
    })
  })

  describe('ImportConfig interface', () => {
    it('should accept valid import config', () => {
      const importConfig: ImportConfig = {
        format: 'csv',
        field_mapping: {
          'Full Name': 'full_name',
          'Email Address': 'email',
          'Department': 'department',
        },
        mode: 'upsert',
        skip_errors: true,
        validate_data: true,
      }

      expect(importConfig.format).toBe('csv')
      expect(importConfig.field_mapping).toEqual({
        'Full Name': 'full_name',
        'Email Address': 'email',
        'Department': 'department',
      })
      expect(importConfig.mode).toBe('upsert')
      expect(importConfig.skip_errors).toBe(true)
      expect(importConfig.validate_data).toBe(true)
    })

    it('should accept different import modes', () => {
      const createConfig: ImportConfig = { format: 'json', mode: 'create' }
      const updateConfig: ImportConfig = { format: 'json', mode: 'update' }
      const upsertConfig: ImportConfig = { format: 'json', mode: 'upsert' }

      expect(createConfig.mode).toBe('create')
      expect(updateConfig.mode).toBe('update')
      expect(upsertConfig.mode).toBe('upsert')
    })
  })

  describe('Type consistency', () => {
    it('should ensure pagination calculations are consistent', () => {
      const response: PaginatedResponse<any> = {
        items: [],
        total: 100,
        page: 3,
        page_size: 10,
        total_pages: 10,
        has_next: true,
        has_prev: true,
        next_page: 4,
        prev_page: 2,
      }

      // Verify pagination logic
      expect(response.total_pages).toBe(Math.ceil(response.total / response.page_size))
      expect(response.has_prev).toBe(response.page > 1)
      expect(response.has_next).toBe(response.page < response.total_pages)
      
      if (response.has_next) {
        expect(response.next_page).toBe(response.page + 1)
      }
      
      if (response.has_prev) {
        expect(response.prev_page).toBe(response.page - 1)
      }
    })

    it('should ensure batch operation counts are consistent', () => {
      const result: BatchOperationResult = {
        success: true,
        success_count: 5,
        failed_count: 2,
        skipped_count: 1,
        success_ids: ['1', '2', '3', '4', '5'],
        failed_ids: ['6', '7'],
      }

      expect(result.success_ids.length).toBe(result.success_count)
      expect(result.failed_ids.length).toBe(result.failed_count)
    })
  })
})