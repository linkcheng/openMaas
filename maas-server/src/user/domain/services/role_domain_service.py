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
from user.domain.models import Role, RoleType, Permission
from user.domain.services.user_validation_service import UserValidationService


class RoleDomainService:
    """角色领域服务，实现角色相关的核心业务逻辑"""

    def __init__(
        self,
        validation_service: UserValidationService | None = None,
    ):
        # ❌ 移除Repository依赖 - Domain Service应该是纯业务逻辑
        # self._role_repository = role_repository
        # self._permission_repository = permission_repository
        # self._user_repository = user_repository
        self._validation_service = validation_service or UserValidationService()

    def validate_role_creation_data(self, name: str, description: str | None = None) -> None:
        """验证角色创建的数据格式（纯业务逻辑）"""
        # 数据格式验证
        self._validation_service.validate_role_name(name)
        self._validation_service.validate_role_description(description)
    
    def validate_role_name_uniqueness(self, existing_role: Role | None, name: str) -> None:
        """验证角色名称唯一性（纯业务逻辑）"""
        if existing_role:
            raise DomainException(f"角色 {name} 已存在")

    def create_role_entity(
        self, name: str,
        description: str | None,
        permissions: list[Permission] | None = None,
        display_name: str | None = None,
        role_type: RoleType = RoleType.USER,
        is_system_role: bool = False,
    ) -> Role:
        """创建角色实体（纯业务逻辑）"""
        # 验证角色创建数据格式
        self.validate_role_creation_data(name, description)

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
        
        logger.info(f"角色实体创建成功: {role.name}")
        return role

    def update_role_entity(
        self,
        role: Role,
        name: str | None = None,
        description: str | None = None,
    ) -> Role:
        """更新角色实体（纯业务逻辑）"""
        # 验证新信息
        if name is not None:
            self._validation_service.validate_role_name(name)
            role.name = name

        if description is not None:
            self._validation_service.validate_role_description(description)
            role.description = description

        logger.info(f"角色实体更新成功: {role.name}")
        return role
        
    def validate_role_name_update_uniqueness(
        self, existing_role: Role | None, name: str, role_id: UUID
    ) -> None:
        """验证角色名称更新时的唯一性（纯业务逻辑）"""
        if existing_role and existing_role.id != role_id:
            raise DomainException(f"角色名称 {name} 已被使用")

    def validate_role_permission_update_rules(self, role: Role) -> None:
        """验证角色权限更新的业务规则（纯业务逻辑）"""
        # 检查是否为系统角色
        if role.is_system_role:
            raise DomainException(f"无法修改系统角色 {role.name} 的权限")
            
    def update_role_permissions_entity(
        self, role: Role, new_permissions: list
    ) -> Role:
        """更新角色权限实体（纯业务逻辑）"""
        # 替换权限
        role.set_permissions(new_permissions)
        logger.info(f"角色 {role.name} 权限已更新")
        return role
        
    def invalidate_users_tokens_for_role_change(self, users_with_role: list) -> list:
        """使角色变更影响的用户token失效（纯业务逻辑）"""
        for user in users_with_role:
            user.increment_key_version()
        logger.info(f"角色权限变更，影响用户数: {len(users_with_role)}")
        return users_with_role

    def validate_role_deletion_rules(self, role: Role, users_with_role: list) -> None:
        """验证角色删除的业务规则（纯业务逻辑）"""
        # 检查是否为系统角色
        if role.is_system_role:
            raise DomainException(f"无法删除系统角色: {role.name}")

        # 检查是否有用户使用此角色
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

    def assign_user_roles_entity(self, user, new_roles: list) -> None:
        """为用户分配角色实体操作（纯业务逻辑）"""
        # 清空现有角色
        for existing_role in user.roles:
            user.remove_role(existing_role)

        # 添加新角色
        for new_role in new_roles:
            user.add_role(new_role)

        # 使用户token失效
        user.increment_key_version()
        logger.info(f"用户 {user.username} 角色分配成功")

    def validate_role_assignment_authority_logic(
        self, user, assigner, roles: list
    ) -> dict:
        """验证角色分配权限逻辑（纯业务逻辑）"""
        validation_results = []

        for role in roles:
            # 简化的权限检查逻辑 - 可以根据具体业务规则扩展
            can_assign = True
            reason = "可以分配"

            # 检查是否为系统角色且分配者不是超级管理员
            if role.is_system_role and not assigner.is_super_admin():
                can_assign = False
                reason = "只有超级管理员才能分配系统角色"

            validation_results.append(
                {
                    "role_id": str(role.id),
                    "role_name": role.name,
                    "can_assign": can_assign,
                    "reason": reason,
                }
            )

        all_assignable = all(result["can_assign"] for result in validation_results)

        return {
            "user_id": str(user.id),
            "assigner_id": str(assigner.id),
            "all_roles_assignable": all_assignable,
            "role_validations": validation_results,
        }

    def calculate_role_usage_statistics(self, role, users_with_role: list) -> dict:
        """计算角色使用统计信息（纯业务逻辑）"""
        return {
            "role_id": str(role.id),
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
