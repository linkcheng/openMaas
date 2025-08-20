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

"""权限领域服务 - 核心业务逻辑"""

from typing import Any
from uuid import UUID

from loguru import logger
from uuid_extensions import uuid7

from shared.domain.base import DomainException
from user.domain.models import Permission, PermissionName
from user.domain.repositories import (
    IPermissionRepository,
    IRoleRepository,
    IUserRepository,
)
from user.domain.services.user_validation_service import UserValidationService


class PermissionDomainService:
    """权限领域服务，实现权限相关的核心业务逻辑"""

    def __init__(
        self,
        permission_repository: IPermissionRepository,
        role_repository: IRoleRepository,
        user_repository: IUserRepository,
        validation_service: UserValidationService | None = None,
    ):
        self._permission_repository = permission_repository
        self._role_repository = role_repository
        self._user_repository = user_repository
        self._validation_service = validation_service or UserValidationService()

    async def get_permission(self, permission_id: UUID) -> Permission | None:
        """根据ID获取权限"""
        return await self._permission_repository.find_by_id(permission_id)

    async def get_permissions_by_module(self, module: str) -> list[Permission]:
        """根据模块获取权限"""
        return await self._permission_repository.find_by_module(module)

    async def get_all_permissions(self) -> list[Permission]:
        """获取所有权限"""
        return await self._permission_repository.find_all()

    async def validate_permission_creation(
        self, name: str, display_name: str, description: str | None = None,
        module: str | None = None
    ) -> None:
        """验证权限创建的业务规则"""
        # 数据格式验证
        self._validation_service.validate_permission_name(name)
        self._validation_service.validate_permission_display_name(display_name)
        self._validation_service.validate_permission_description(description)
        self._validation_service.validate_permission_module(module)

        # 验证权限名称格式
        try:
            permission_name = PermissionName(name)
        except ValueError as e:
            raise DomainException(f"权限名称格式错误: {e!s}")

        # 检查权限是否已存在
        existing = await self._permission_repository.find_by_resource_action(
            permission_name.resource, permission_name.action
        )
        if existing:
            raise DomainException(f"权限 {permission_name.resource}:{permission_name.action} 已存在")

    async def create_permission(
        self, name: str, display_name: str, description: str | None = None,
        module: str | None = None
    ) -> Permission:
        """创建权限"""
        # 验证权限创建规则
        await self.validate_permission_creation(name, display_name, description, module)

        # 验证权限名称格式
        permission_name = PermissionName(name)

        # 创建权限
        permission = Permission(
            id=uuid7(),
            name=permission_name,
            display_name=display_name,
            description=description,
            module=module,
        )

        # 保存权限
        await self._permission_repository.save(permission)
        logger.info(f"权限创建成功: {permission.name.value}")
        return permission

    async def update_permission_information(
        self,
        permission_id: UUID,
        name: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
        module: str | None = None,
    ) -> Permission:
        """更新权限信息"""
        permission = await self._permission_repository.find_by_id(permission_id)
        if not permission:
            raise DomainException(f"权限 {permission_id} 不存在")

        # 更新权限信息
        if display_name is not None:
            self._validation_service.validate_permission_display_name(display_name)
            permission.display_name = display_name

        if description is not None:
            self._validation_service.validate_permission_description(description)
            permission.description = description

        if module is not None:
            self._validation_service.validate_permission_module(module)
            permission.module = module

        # 如果更新了名称，需要验证格式和唯一性
        if name is not None:
            try:
                new_permission_name = PermissionName(name)
            except ValueError as e:
                raise DomainException(f"权限名称格式错误: {e!s}")

            # 检查新名称是否已被使用
            existing = await self._permission_repository.find_by_resource_action(
                new_permission_name.resource, new_permission_name.action
            )
            if existing and existing.id != permission_id:
                raise DomainException(f"权限名称 {name} 已被使用")

            permission.name = new_permission_name

        # 保存权限
        await self._permission_repository.save(permission)
        logger.info(f"权限更新成功: {permission.name.value}")
        
        return permission

    async def validate_permission_deletion(self, permission_id: UUID) -> Permission:
        """验证权限删除的业务规则"""
        permission = await self._permission_repository.find_by_id(permission_id)
        if not permission:
            raise DomainException(f"权限 {permission_id} 不存在")

        # 检查是否有角色正在使用此权限
        roles_with_permission = await self._role_repository.find_roles_with_permission([permission_id])
        if roles_with_permission:
            role_names = [role.name for role in roles_with_permission]
            raise DomainException(
                f"无法删除权限，以下角色正在使用: {', '.join(role_names)}"
            )

        logger.info(f"权限删除验证通过: {permission.name.value}")
        return permission

    async def delete_permission(self, permission_id: UUID) -> Permission:
        """删除权限"""
        return await self._permission_repository.delete(permission_id)

    async def search_permissions(
        self,
        keyword: str | None = None,
        module: str | None = None,
        resource: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Permission]:
        """搜索权限"""
        return await self._permission_repository.search_permissions(keyword, module, resource, limit, offset)

    async def batch_create_permissions(
        self, permissions_data: list[dict[str, Any]]
    ) -> tuple[list[Permission], list[dict[str, str]]]:
        """批量创建权限"""
        created_permissions = []
        failed_permissions = []

        for perm_data in permissions_data:
            try:
                # 验证必需字段
                name = perm_data.get("name")
                display_name = perm_data.get("display_name")
                description = perm_data.get("description")
                module = perm_data.get("module")

                if not name or not display_name:
                    failed_permissions.append({
                        "permission": name or "未知",
                        "reason": "缺少必需字段 name 或 display_name"
                    })
                    continue

                # 验证权限创建规则
                await self.validate_permission_creation(name, display_name, description, module)

                # 创建权限
                permission = await self.create_permission(name, display_name, description, module)
                created_permissions.append(permission)

            except Exception as e:
                failed_permissions.append({
                    "permission": perm_data.get("name", "未知"),
                    "reason": str(e)
                })

        if failed_permissions:
            logger.warning(f"批量创建权限部分失败: {failed_permissions}")

        logger.info(f"批量创建权限完成，成功: {len(created_permissions)}, 失败: {len(failed_permissions)}")
        return created_permissions, failed_permissions

    async def batch_delete_permissions(
        self, permission_ids: list[UUID]
    ) -> tuple[int, list[dict[str, str]]]:
        """批量删除权限"""
        deleted_count = 0
        failed_deletions = []

        for permission_id in permission_ids:
            try:
                # 验证删除规则
                await self.validate_permission_deletion(permission_id)

                # 执行删除
                await self._permission_repository.delete(permission_id)
                deleted_count += 1

            except Exception as e:
                failed_deletions.append({
                    "permission_id": str(permission_id),
                    "reason": str(e)
                })

        logger.info(f"批量删除权限完成，成功: {deleted_count}, 失败: {len(failed_deletions)}")
        return deleted_count, failed_deletions

    async def export_permissions_by_module(
        self, module: str | None = None
    ) -> list[dict[str, Any]]:
        """按模块导出权限配置"""
        if module:
            permissions = await self._permission_repository.find_by_module(module)
        else:
            permissions = await self._permission_repository.find_all()

        export_data = []
        for perm in permissions:
            export_data.append({
                "name": perm.name.value,
                "display_name": perm.display_name,
                "description": perm.description,
                "resource": perm.resource,
                "action": perm.action,
                "module": perm.module,
            })

        logger.info(f"导出权限配置完成，共 {len(export_data)} 个权限")
        return export_data

    async def import_permissions_from_config(
        self, import_data: list[dict[str, Any]]
    ) -> tuple[int, list[dict[str, str]]]:
        """从配置导入权限"""
        imported_count = 0
        failed_imports = []

        for perm_data in import_data:
            try:
                # 验证必需字段
                required_fields = ["name", "display_name", "description", "resource", "action"]
                for field in required_fields:
                    if field not in perm_data:
                        raise ValueError(f"缺少必需字段: {field}")

                # 检查权限是否已存在
                existing = await self._permission_repository.find_by_resource_action(
                    perm_data["resource"], perm_data["action"]
                )
                if existing:
                    failed_imports.append({
                        "permission": perm_data["name"],
                        "reason": f"权限 {perm_data['resource']}:{perm_data['action']} 已存在"
                    })
                    continue

                # 创建权限
                permission = await self.create_permission(
                    perm_data["name"],
                    perm_data["display_name"],
                    perm_data["description"],
                    perm_data.get("module")
                )

                await self._permission_repository.save(permission)
                imported_count += 1

            except Exception as e:
                failed_imports.append({
                    "permission": perm_data.get("name", "未知"),
                    "reason": str(e)
                })

        logger.info(f"导入权限配置完成，成功: {imported_count}, 失败: {len(failed_imports)}")
        return imported_count, failed_imports

    async def validate_user_permission(self, user_id: UUID, permission_name: str) -> bool:
        """验证用户权限"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            return False

        return user.has_permission(permission_name)

    async def validate_user_permission_by_parts(
        self, user_id: UUID, resource: str, action: str, module: str | None = None
    ) -> bool:
        """通过资源和操作验证用户权限"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            return False

        return user.has_permission_by_parts(resource, action, module)

    async def get_permission_usage_statistics(self, permission_id: UUID) -> dict:
        """获取权限使用统计信息"""
        permission = await self._permission_repository.find_by_id(permission_id)
        if not permission:
            raise DomainException(f"权限 {permission_id} 不存在")

        # 获取使用此权限的角色
        roles_with_permission = await self._role_repository.find_roles_with_permission([permission_id])

        # 获取拥有此权限的用户（通过角色关联）
        users_with_permission = []
        for role in roles_with_permission:
            role_users = await self._user_repository.find_by_role_id(role.id)
            for user in role_users:
                if user not in users_with_permission:
                    users_with_permission.append(user)

        return {
            "permission_id": str(permission_id),
            "permission_name": permission.name.value,
            "permission_display_name": permission.display_name,
            "resource": permission.resource,
            "action": permission.action,
            "module": permission.module,
            "role_count": len(roles_with_permission),
            "user_count": len(users_with_permission),
            "roles": [
                {
                    "id": str(role.id),
                    "name": role.name,
                    "description": role.description,
                    "is_system_role": role.is_system_role,
                }
                for role in roles_with_permission
            ],
            "users": [
                {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email.value,
                    "status": user.status.value,
                }
                for user in users_with_permission
            ],
        }
