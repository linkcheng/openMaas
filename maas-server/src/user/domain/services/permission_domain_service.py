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
from user.domain.services.user_validation_service import UserValidationService


class PermissionDomainService:
    """权限领域服务，实现权限相关的核心业务逻辑"""

    def __init__(
        self,
        validation_service: UserValidationService | None = None,
    ):
        # ❌ 移除Repository依赖 - Domain Service应该是纯业务逻辑
        # self._permission_repository = permission_repository
        # self._role_repository = role_repository
        # self._user_repository = user_repository
        self._validation_service = validation_service or UserValidationService()

    def validate_permission_creation_data(
        self, name: str, display_name: str, description: str | None = None,
    ) -> PermissionName:
        """验证权限创建的数据格式（纯业务逻辑）"""
        # 数据格式验证
        self._validation_service.validate_permission_name(name)
        self._validation_service.validate_permission_display_name(display_name)
        self._validation_service.validate_permission_description(description)

        # 验证权限名称格式
        try:
            permission_name = PermissionName(name)
        except ValueError as e:
            raise DomainException(f"权限名称格式错误: {e!s}")

        return permission_name

    def validate_permission_uniqueness(self, existing_permission: Permission | None, permission_name: PermissionName) -> None:
        """验证权限唯一性（纯业务逻辑）"""
        if existing_permission:
            raise DomainException(f"权限 {permission_name.value} 已存在")

    def create_permission_entity(
        self, name: str, display_name: str, description: str | None = None,
    ) -> Permission:
        """创建权限实体（纯业务逻辑）"""
        # 验证权限数据格式
        permission_name = self.validate_permission_creation_data(name, display_name, description)

        # 创建权限实体
        permission = Permission(
            id=uuid7(),
            name=permission_name,
            display_name=display_name,
            description=description,
        )

        logger.info(f"权限实体创建成功: {permission.name.value}")
        return permission

    def update_permission_entity(
        self,
        permission: Permission,
        name: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
        module: str | None = None,
    ) -> Permission:
        """更新权限实体（纯业务逻辑）"""
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

        # 如果更新了名称，需要验证格式
        if name is not None:
            try:
                new_permission_name = PermissionName(name)
            except ValueError as e:
                raise DomainException(f"权限名称格式错误: {e!s}")
            permission.name = new_permission_name

        logger.info(f"权限实体更新成功: {permission.name.value}")
        return permission

    def validate_permission_name_uniqueness(
        self, existing_permission: Permission | None, new_name: str, permission_id: UUID
    ) -> None:
        """验证权限名称唯一性（纯业务逻辑）"""
        if existing_permission and existing_permission.id != permission_id:
            raise DomainException(f"权限名称 {new_name} 已被使用")

    def validate_permission_deletion_rules(
        self, permission: Permission, roles_with_permission: list
    ) -> None:
        """验证权限删除的业务规则（纯业务逻辑）"""
        # 检查是否有角色正在使用此权限
        if roles_with_permission:
            role_names = [role.name for role in roles_with_permission]
            raise DomainException(
                f"无法删除权限，以下角色正在使用: {', '.join(role_names)}"
            )

        logger.info(f"权限删除验证通过: {permission.name.value}")

    def validate_batch_permission_data(
        self, permissions_data: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        """验证批量权限数据（纯业务逻辑）"""
        valid_permissions = []
        invalid_permissions = []

        for perm_data in permissions_data:
            try:
                # 验证必需字段
                name = perm_data.get("name")
                display_name = perm_data.get("display_name")
                description = perm_data.get("description")
                module = perm_data.get("module")

                if not name or not display_name:
                    invalid_permissions.append({
                        "permission": name or "未知",
                        "reason": "缺少必需字段 name 或 display_name"
                    })
                    continue

                # 验证数据格式
                permission_name = self.validate_permission_creation_data(name, display_name, description)

                # 添加验证通过的数据
                valid_permissions.append({
                    "name": name,
                    "display_name": display_name,
                    "description": description,
                    "module": module,
                    "permission_name": permission_name
                })

            except Exception as e:
                invalid_permissions.append({
                    "permission": perm_data.get("name", "未知"),
                    "reason": str(e)
                })

        return valid_permissions, invalid_permissions

    def format_permissions_for_export(
        self, permissions: list[Permission]
    ) -> list[dict[str, Any]]:
        """格式化权限为导出数据（纯业务逻辑）"""
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

        logger.info(f"格式化权限数据完成，共 {len(export_data)} 个权限")
        return export_data

    def validate_import_permission_data(
        self, import_data: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        """验证导入权限数据（纯业务逻辑）"""
        valid_imports = []
        invalid_imports = []

        for perm_data in import_data:
            try:
                # 验证必需字段
                required_fields = ["name", "display_name", "description", "resource", "action"]
                for field in required_fields:
                    if field not in perm_data:
                        raise ValueError(f"缺少必需字段: {field}")

                # 验证数据格式
                permission_name = self.validate_permission_creation_data(
                    perm_data["name"],
                    perm_data["display_name"],
                    perm_data["description"]
                )

                valid_imports.append({
                    "name": perm_data["name"],
                    "display_name": perm_data["display_name"],
                    "description": perm_data["description"],
                    "resource": perm_data["resource"],
                    "action": perm_data["action"],
                    "module": perm_data.get("module"),
                    "permission_name": permission_name
                })

            except Exception as e:
                invalid_imports.append({
                    "permission": perm_data.get("name", "未知"),
                    "reason": str(e)
                })

        return valid_imports, invalid_imports

    def validate_user_permission_logic(self, user, permission_name: str) -> bool:
        """验证用户权限逻辑（纯业务逻辑）"""
        if not user:
            return False
        return user.has_permission(permission_name)

    def validate_user_permission_by_parts_logic(
        self, user, resource: str, action: str, module: str | None = None
    ) -> bool:
        """通过资源和操作验证用户权限逻辑（纯业务逻辑）"""
        if not user:
            return False
        return user.has_permission_by_parts(resource, action, module)

    def calculate_permission_usage_statistics(
        self, permission: Permission, roles_with_permission: list, users_with_permission: list
    ) -> dict:
        """计算权限使用统计（纯业务逻辑）"""
        return {
            "permission_id": str(permission.id),
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
