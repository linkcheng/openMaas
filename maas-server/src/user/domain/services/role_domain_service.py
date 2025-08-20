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

"""角色领域服务 - 核心业务逻辑"""

from uuid import UUID

from loguru import logger
from uuid_extensions import uuid7

from shared.domain.base import DomainException
from user.domain.models import Role, RoleType
from user.domain.repositories import (
    IPermissionRepository,
    IRoleRepository,
    IUserRepository,
)
from user.domain.services.user_validation_service import UserValidationService


class RoleDomainService:
    """角色领域服务，实现角色相关的核心业务逻辑"""

    def __init__(
        self,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository,
        user_repository: IUserRepository,
        validation_service: UserValidationService | None = None,
    ):
        self._role_repository = role_repository
        self._permission_repository = permission_repository
        self._user_repository = user_repository
        self._validation_service = validation_service or UserValidationService()

    async def validate_role_creation(self, name: str, description: str | None = None) -> None:
        """验证角色创建的业务规则"""
        # 数据格式验证
        self._validation_service.validate_role_name(name)
        self._validation_service.validate_role_description(description)

        # 唯一性验证
        existing_role = await self._role_repository.find_by_name(name)
        if existing_role:
            raise DomainException(f"角色 {name} 已存在")

    async def create_role_with_permissions(
        self, name: str,
        description: str | None,
        permission_ids: list[UUID],
        display_name: str | None = None,
        role_type: RoleType = RoleType.USER,
        is_system_role: bool = False,
    ) -> Role:
        """创建角色并分配权限"""
        # 验证角色创建规则
        await self.validate_role_creation(name, description)

        # 获取权限列表（基于ID查找）
        permissions = []
        for permission_id in permission_ids:
            permission = await self._permission_repository.find_by_id(permission_id)
            if not permission:
                logger.warning(f"权限 {permission_id} 不存在，跳过")
                continue
            permissions.append(permission)

        # 创建角色
        role = Role(
            id=uuid7(),
            name=name,
            display_name=display_name or name,
            description=description,
            permissions=permissions,
            role_type=role_type,
            is_system_role=is_system_role,
        )
        await self._role_repository.save(role)
        logger.info(f"角色创建成功: {role.name}")
        return role

    async def update_role_information(
        self,
        role_id: UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> Role:
        """更新角色基本信息"""
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise DomainException(f"角色 {role_id} 不存在")

        # 验证新信息
        if name is not None:
            self._validation_service.validate_role_name(name)
            # 检查新名称是否已被使用
            existing_role = await self._role_repository.find_by_name(name)
            if existing_role and existing_role.id != role_id:
                raise DomainException(f"角色名称 {name} 已被使用")
            role.name = name

        if description is not None:
            self._validation_service.validate_role_description(description)
            role.description = description

        logger.info(f"角色更新成功: {role.name}")
        return role

    async def update_role_permissions(
        self, role_id: UUID, permission_ids: list[UUID]
    ) -> Role:
        """批量更新角色权限"""
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise DomainException(f"角色 {role_id} 不存在")

        # 检查是否为系统角色
        if role.is_system_role:
            raise DomainException(f"无法修改系统角色 {role.name} 的权限")

        # 获取新权限列表
        new_permissions = []
        for permission_id in permission_ids:
            permission = await self._permission_repository.find_by_id(permission_id)
            if not permission:
                logger.warning(f"权限 {permission_id} 不存在，跳过")
                continue
            new_permissions.append(permission)

        # 替换权限
        role.set_permissions(new_permissions)

        # 使所有拥有此角色的用户token失效
        users_with_role = await self._user_repository.find_by_role_id(role_id)
        for user in users_with_role:
            user.increment_key_version()
            await self._user_repository.save(user)

        logger.info(f"角色 {role.name} 权限已更新，影响用户数: {len(users_with_role)}")
        return role

    async def validate_role_deletion(self, role_id: UUID) -> Role:
        """验证角色删除的业务规则"""
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise DomainException(f"角色 {role_id} 不存在")

        # 检查是否为系统角色
        if role.is_system_role:
            raise DomainException(f"无法删除系统角色: {role.name}")

        # 检查是否有用户使用此角色
        users_with_role = await self._user_repository.find_by_role_id(role_id)
        if users_with_role:
            user_names = [user.username for user in users_with_role]
            raise DomainException(
                f"无法删除角色，以下用户正在使用: {', '.join(user_names)}"
            )

        # 检查是否为系统默认角色（额外的名称检查）
        system_roles = ["admin", "super_admin", "system_admin", "user", "developer"]
        if role.name.lower() in system_roles:
            raise DomainException(f"无法删除系统角色: {role.name}")

        logger.info(f"角色删除验证通过: {role.name}")
        return role

    async def assign_user_roles(
        self, user_id: UUID, role_ids: list[UUID]
    ) -> None:
        """为用户分配角色"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        # 获取角色列表
        new_roles = []
        for role_id in role_ids:
            role = await self._role_repository.find_by_id(role_id)
            if not role:
                raise DomainException(f"角色 {role_id} 不存在")
            new_roles.append(role)

        # 清空现有角色
        for existing_role in user.roles:
            user.remove_role(existing_role)

        # 添加新角色
        for new_role in new_roles:
            user.add_role(new_role)

        # 使用户token失效
        user.increment_key_version()

        await self._user_repository.save(user)
        logger.info(f"用户 {user.username} 角色分配成功")

    async def validate_role_assignment_authority(
        self, user_id: UUID, role_ids: list[UUID], assigner_id: UUID
    ) -> dict:
        """验证角色分配权限"""
        user = await self._user_repository.find_by_id(user_id)
        assigner = await self._user_repository.find_by_id(assigner_id)

        if not user:
            raise DomainException(f"用户 {user_id} 不存在")
        if not assigner:
            raise DomainException(f"分配者 {assigner_id} 不存在")

        validation_results = []

        for role_id in role_ids:
            role = await self._role_repository.find_by_id(role_id)
            if not role:
                validation_results.append(
                    {
                        "role_id": str(role_id),
                        "can_assign": False,
                        "reason": "角色不存在",
                    }
                )
                continue

            # 简化的权限检查逻辑 - 可以根据具体业务规则扩展
            can_assign = True
            reason = "可以分配"

            # 检查是否为系统角色且分配者不是超级管理员
            if role.is_system_role and not assigner.is_super_admin():
                can_assign = False
                reason = "只有超级管理员才能分配系统角色"

            validation_results.append(
                {
                    "role_id": str(role_id),
                    "role_name": role.name,
                    "can_assign": can_assign,
                    "reason": reason,
                }
            )

        all_assignable = all(result["can_assign"] for result in validation_results)

        return {
            "user_id": str(user_id),
            "assigner_id": str(assigner_id),
            "all_roles_assignable": all_assignable,
            "role_validations": validation_results,
        }

    async def get_role_usage_statistics(self, role_id: UUID) -> dict:
        """获取角色使用统计信息"""
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise DomainException(f"角色 {role_id} 不存在")

        # 获取使用此角色的用户
        users_with_role = await self._user_repository.find_by_role_id(role_id)

        return {
            "role_id": str(role_id),
            "role_name": role.name,
            "role_description": role.description,
            "is_system_role": role.is_system_role,
            "permission_count": len(role.permissions),
            "user_count": len(users_with_role),
            "users": [
                {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email.value,
                    "status": user.status.value,
                }
                for user in users_with_role
            ],
        }
