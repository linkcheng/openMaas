"""
Copyright 2025 MaaS Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""权限应用服务 - 负责编排和事务管理"""

from typing import Any
from uuid import UUID

from user.application.schemas import (
    PermissionBatchRequest,
    PermissionExportResponse,
    PermissionRequest,
    PermissionResponse,
    PermissionSearchQuery,
    PermissionUpdateRequest,
)
from user.domain.services.permission_domain_service import PermissionDomainService


class PermissionApplicationService:
    """权限应用服务 - 负责编排和事务管理"""

    def __init__(
        self,
        permission_domain_service: PermissionDomainService,
    ):
        self._permission_domain_service = permission_domain_service

    async def create_permission(self, request: PermissionRequest) -> PermissionResponse:
        """创建权限"""
        # 使用 Domain Service 创建权限
        permission = await self._permission_domain_service.create_permission(
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            module=request.module
        )
        return self._to_permission_response(permission)

    async def get_permission(self, permission_id: UUID) -> PermissionResponse | None:
        """获取权限"""
        permission = await self._permission_domain_service.get_permission(permission_id)
        if not permission:
            return None

        return self._to_permission_response(permission)

    async def update_permission(
        self, permission_id: UUID, request: PermissionUpdateRequest
    ) -> PermissionResponse:
        """更新权限"""
        # 使用 Domain Service 更新权限
        permission = await self._permission_domain_service.update_permission_information(
            permission_id=permission_id,
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            module=request.module
        )

        return self._to_permission_response(permission)

    async def delete_permission(self, permission_id: UUID) -> bool:
        """删除权限"""
        # 使用 Domain Service 验证删除规则
        _ = await self._permission_domain_service.validate_permission_deletion(permission_id)

        # 执行删除
        await self._permission_domain_service.delete_permission(permission_id)
        return True

    async def search_permissions(self, query: PermissionSearchQuery) -> list[PermissionResponse]:
        """搜索权限"""
        permissions = await self._permission_domain_service.search_permissions(
            name=query.name,
            module=query.module,
            resource=query.resource,
            action=query.action,
            limit=query.limit,
            offset=query.offset,
        )

        return [self._to_permission_response(perm) for perm in permissions]

    async def get_permissions_by_module(self, module: str) -> list[PermissionResponse]:
        """按模块获取权限"""
        permissions = await self._permission_domain_service.get_permissions_by_module(module)
        return [self._to_permission_response(perm) for perm in permissions]

    async def get_all_permissions(self) -> list[PermissionResponse]:
        """获取所有权限"""  
        permissions = await self._permission_domain_service.get_all_permissions()
        return [self._to_permission_response(perm) for perm in permissions]

    async def batch_create_permissions(
        self, request: PermissionBatchRequest
    ) -> list[PermissionResponse]:
        """批量创建权限"""
        # 准备数据
        permissions_data = []
        for perm_request in request.permissions:
            permissions_data.append({
                "name": perm_request.name,
                "display_name": perm_request.display_name,
                "description": perm_request.description,
                "module": perm_request.module,
            })

        # 使用 Domain Service 批量创建
        created_permissions, failed_permissions = await self._permission_domain_service.batch_create_permissions(
            permissions_data
        )

        return created_permissions

    async def batch_delete_permissions(self, permission_ids: list[UUID]) -> dict[str, Any]:
        """批量删除权限"""
        # 使用 Domain Service 批量删除
        deleted_count, failed_deletions = await self._permission_domain_service.batch_delete_permissions(
            permission_ids
        )

        return {
            "deleted_count": deleted_count,
            "failed_deletions": failed_deletions
        }

    async def export_permissions(self, module: str | None = None) -> PermissionExportResponse:
        """导出权限配置"""
        # 使用 Domain Service 导出数据
        export_data = await self._permission_domain_service.export_permissions_by_module(module)

        return PermissionExportResponse(
            permissions=export_data,
            total_count=len(export_data),
            export_module=module
        )

    async def import_permissions(self, import_data: list[dict[str, Any]]) -> dict[str, Any]:
        """导入权限配置"""
        # 使用 Domain Service 导入权限
        imported_count, failed_imports = await self._permission_domain_service.import_permissions_from_config(
            import_data
        )

        return {
            "imported_count": imported_count,
            "failed_imports": failed_imports
        }

    async def validate_permission(self, user_id: UUID, permission_name: str) -> bool:
        """验证用户权限"""
        # 使用 Domain Service 验证权限
        return await self._permission_domain_service.validate_user_permission(user_id, permission_name)

    async def validate_permission_by_parts(
        self, user_id: UUID, resource: str, action: str, module: str | None = None
    ) -> bool:
        """通过资源和操作验证用户权限"""
        # 使用 Domain Service 验证权限
        return await self._permission_domain_service.validate_user_permission_by_parts(
            user_id, resource, action, module
        )

    async def get_permission_usage_statistics(self, permission_id: UUID) -> dict:
        """获取权限使用统计"""
        # 使用 Domain Service 获取统计信息
        return await self._permission_domain_service.get_permission_usage_statistics(permission_id)

    def _to_permission_response(self, permission) -> PermissionResponse:
        """转换为权限响应DTO"""
        return PermissionResponse(
            id=permission.id,
            name=permission.name.value,
            display_name=permission.display_name,
            description=permission.description,
            resource=permission.resource,
            action=permission.action,
            module=permission.module,
        )
