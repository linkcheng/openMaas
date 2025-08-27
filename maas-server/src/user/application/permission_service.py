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

from shared.domain.base import DomainException
from shared.infrastructure.transaction_manager import transactional
from user.application.schemas import (
    BatchPermissionData,
    PermissionBatchRequest,
    PermissionExportResponse,
    PermissionRequest,
    PermissionResponse,
    PermissionSearchQuery,
    PermissionUpdateRequest,
)
from user.domain.repositories import (
    IPermissionRepository,
    IRoleRepository,
    IUserRepository,
)
from user.domain.services.permission_domain_service import PermissionDomainService


class PermissionApplicationService:
    """权限应用服务 - 负责编排和事务管理"""

    def __init__(
        self,
        permission_domain_service: PermissionDomainService,
        permission_repository: IPermissionRepository,
        role_repository: IRoleRepository,
        user_repository: IUserRepository,
    ):
        self._permission_domain_service = permission_domain_service
        self._permission_repository = permission_repository
        self._role_repository = role_repository
        self._user_repository = user_repository

    @transactional()
    async def create_permission(
        self,
        request: PermissionRequest,
    ) -> PermissionResponse:
        """创建权限 - 事务操作"""
        # 1. 检查权限是否已存在
        permission_name = self._permission_domain_service.validate_permission_creation_data(
            request.name, request.display_name, request.description
        )
        existing = await self._permission_repository.find_by_name(request.name)

        self._permission_domain_service.validate_permission_uniqueness(existing, permission_name)

        # 2. 使用Domain Service创建权限实体
        permission = self._permission_domain_service.create_permission_entity(
            name=request.name,
            display_name=request.display_name,
            description=request.description,
        )

        # 3. Application Service保存权限
        saved_permission = await self._permission_repository.save(permission)

        return self._to_permission_response(saved_permission)

    async def get_permission(
        self,
        permission_id: UUID,
    ) -> PermissionResponse | None:
        """获取权限 - 只读操作"""
        # Application Service直接查询Repository
        permission = await self._permission_repository.find_by_id(permission_id)
        if not permission:
            return None

        return self._to_permission_response(permission)

    @transactional()
    async def update_permission(
        self,
        permission_id: UUID,
        request: PermissionUpdateRequest,
    ) -> PermissionResponse:
        """更新权限 - 事务操作"""
        # 1. Application Service查询权限
        permission = await self._permission_repository.find_by_id(permission_id)
        if not permission:
            raise DomainException(f"权限 {permission_id} 不存在")

        # 2. 如果更新名称，检查唯一性
        if request.name is not None:
            _ = self._permission_domain_service.validate_permission_creation_data(
                request.name, request.display_name or permission.display_name, request.description or permission.description
            )
            existing = await self._permission_repository.find_by_name(request.name)
            self._permission_domain_service.validate_permission_name_uniqueness(
                existing, request.name, permission_id
            )

        # 3. 使用Domain Service更新权限实体
        updated_permission = self._permission_domain_service.update_permission_entity(
            permission=permission,
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            module=request.module
        )

        # 4. Application Service保存权限
        saved_permission = await self._permission_repository.save(updated_permission)
        # 事务在装饰器中自动提交
        return self._to_permission_response(saved_permission)

    @transactional()
    async def delete_permission(
        self,
        permission_id: UUID,
    ) -> bool:
        """删除权限 - 事务操作"""
        # 1. Application Service查询权限
        permission = await self._permission_repository.find_by_id(permission_id)
        if not permission:
            raise DomainException(f"权限 {permission_id} 不存在")

        # 2. 查询使用此权限的角色
        roles_with_permission = await self._role_repository.find_roles_with_permission([permission_id])

        # 3. 使用Domain Service验证删除规则
        self._permission_domain_service.validate_permission_deletion_rules(
            permission, roles_with_permission
        )

        # 4. Application Service执行删除
        await self._permission_repository.delete(permission_id)
        # 事务在装饰器中自动提交
        return True

    async def search_permissions(
        self,
        query: PermissionSearchQuery,
    ) -> list[PermissionResponse]:
        """搜索权限 - 只读操作"""
        # Application Service直接查询Repository
        permissions = await self._permission_repository.search_permissions(
            keyword=query.name,
            module=query.module,
            resource=query.resource,
            limit=query.limit,
            offset=query.offset,
        )

        return [self._to_permission_response(perm) for perm in permissions]

    async def get_permissions_by_module(
        self,
        module: str,
    ) -> list[PermissionResponse]:
        """按模块获取权限 - 只读操作"""
        # Application Service直接查询Repository
        permissions = await self._permission_repository.find_by_module(module)
        return [self._to_permission_response(perm) for perm in permissions]

    async def get_all_permissions(
        self,
    ) -> list[PermissionResponse]:
        """获取所有权限 - 只读操作"""
        # Application Service直接查询Repository
        permissions = await self._permission_repository.find_all()
        return [self._to_permission_response(perm) for perm in permissions]

    @transactional()
    async def batch_create_permissions(
        self,
        request: PermissionBatchRequest,
    ) -> list[PermissionResponse]:
        """批量创建权限 - 事务操作"""
        # 1. 准备数据
        permissions_data = []
        for perm_request in request.permissions:
            permissions_data.append({
                "name": perm_request.name,
                "display_name": perm_request.display_name,
                "description": perm_request.description,
                "module": perm_request.module,
            })

        # 2. 使用Domain Service验证数据
        valid_permissions, invalid_permissions = self._permission_domain_service.validate_batch_permission_data(
            permissions_data
        )

        # 3. Application Service批量创建权限
        created_responses = []
        for perm_data in valid_permissions:
            try:
                # 检查唯一性
                existing = await self._permission_repository.find_by_name(
                    perm_data["permission_name"].value,
                )
                if existing:
                    continue  # 跳过已存在的

                # 创建权限实体
                permission = self._permission_domain_service.create_permission_entity(
                    name=perm_data["name"],
                    display_name=perm_data["display_name"],
                    description=perm_data["description"]
                )

                # 保存
                saved_permission = await self._permission_repository.save(permission)
                created_responses.append(self._to_permission_response(saved_permission))

            except Exception:
                continue  # 跳过失败的

        # 事务在装饰器中自动提交
        return created_responses

    @transactional()
    async def batch_delete_permissions(
        self,
        permission_ids: list[UUID],
    ) -> BatchPermissionData:
        """批量删除权限 - 事务操作"""
        deleted_count = 0
        failed_deletions = []

        for permission_id in permission_ids:
            try:
                # 1. Application Service查询权限
                permission = await self._permission_repository.find_by_id(permission_id)
                if not permission:
                    failed_deletions.append({
                        "permission_id": str(permission_id),
                        "reason": f"权限 {permission_id} 不存在"
                    })
                    continue

                # 2. 查询使用此权限的角色
                roles_with_permission = await self._role_repository.find_roles_with_permission([permission_id])

                # 3. 使用Domain Service验证删除规则
                self._permission_domain_service.validate_permission_deletion_rules(
                    permission, roles_with_permission
                )

                # 4. Application Service执行删除
                await self._permission_repository.delete(permission_id)
                deleted_count += 1

            except Exception as e:
                failed_deletions.append({
                    "permission_id": str(permission_id),
                    "reason": str(e)
                })

        # 事务在装饰器中自动提交
        return BatchPermissionData(
            deleted_count=deleted_count,
            failed_deletions=failed_deletions
        )

    async def export_permissions(
        self,
        module: str | None = None,
    ) -> PermissionExportResponse:
        """导出权限配置 - 只读操作"""
        # 1. Application Service查询权限
        if module:
            permissions = await self._permission_repository.find_by_module(module)
        else:
            permissions = await self._permission_repository.find_all()

        # 2. 使用Domain Service格式化数据
        export_data = self._permission_domain_service.format_permissions_for_export(permissions)

        return PermissionExportResponse(
            permissions=export_data,
            total_count=len(export_data),
            export_module=module
        )

    @transactional()
    async def import_permissions(
        self,
        import_data: list[dict[str, Any]],
    ) -> BatchPermissionData:
        """导入权限配置 - 事务操作"""
        # 1. 使用Domain Service验证导入数据
        valid_imports, invalid_imports = self._permission_domain_service.validate_import_permission_data(
            import_data
        )

        # 2. Application Service处理导入
        imported_count = 0
        failed_imports = list(invalid_imports)  # 复制无效数据

        for perm_data in valid_imports:
            try:
                # 检查权限是否已存在
                existing = await self._permission_repository.find_by_name(
                    perm_data["name"]
                )
                if existing:
                    failed_imports.append({
                        "permission": perm_data["name"],
                        "reason": f"权限 {perm_data['resource']}:{perm_data['action']} 已存在"
                    })
                    continue

                # 创建权限
                permission = self._permission_domain_service.create_permission_entity(
                    perm_data["name"],
                    perm_data["display_name"],
                    perm_data["description"]
                )

                await self._permission_repository.save(permission)
                imported_count += 1

            except Exception as e:
                failed_imports.append({
                    "permission": perm_data.get("name", "未知"),
                    "reason": str(e)
                })

        # 事务在装饰器中自动提交
        return BatchPermissionData(
            imported_count=imported_count,
            failed_imports=failed_imports
        )

    async def validate_permission(
        self,
        user_id: UUID,
        permission_name: str,
    ) -> bool:
        """验证用户权限 - 只读操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)

        # 2. 使用Domain Service验证权限逻辑
        return self._permission_domain_service.validate_user_permission_logic(user, permission_name)

    async def validate_permission_by_parts(
        self,
        user_id: UUID,
        resource: str,
        action: str,
        module: str | None = None,
    ) -> bool:
        """通过资源和操作验证用户权限 - 只读操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)

        # 2. 使用Domain Service验证权限逻辑
        return self._permission_domain_service.validate_user_permission_by_parts_logic(
            user, resource, action, module
        )

    async def get_permission_usage_statistics(
        self,
        permission_id: UUID,
    ) -> dict:
        """获取权限使用统计 - 只读操作"""
        # 1. Application Service查询权限
        permission = await self._permission_repository.find_by_id(permission_id)
        if not permission:
            raise DomainException(f"权限 {permission_id} 不存在")

        # 2. 获取使用此权限的角色
        roles_with_permission = await self._role_repository.find_roles_with_permission([permission_id])

        # 3. 获取拥有此权限的用户（通过角色关联）
        users_with_permission = []
        for role in roles_with_permission:
            role_users = await self._user_repository.find_by_role_id(role.id)
            for user in role_users:
                if user not in users_with_permission:
                    users_with_permission.append(user)

        # 4. 使用Domain Service计算统计数据
        return self._permission_domain_service.calculate_permission_usage_statistics(
            permission, roles_with_permission, users_with_permission
        )

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
