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

用户应用层 - 应用服务
"""

from typing import Any
from uuid import UUID

from shared.application.exceptions import ApplicationException
from user.application.schemas import (
    PasswordChangeCommand,
    RoleResponse,
    UserCreateCommand,
    UserProfileResponse,
    UserResponse,
    UserSearchQuery,
    UserStatsResponse,
    UserSummaryResponse,
    UserUpdateCommand,
)
from user.domain.models import User
from user.domain.repositories import IUserRepository
from user.domain.services.user_domain_service import UserDomainService
from user.infrastructure.email_service import EmailVerificationService
from user.infrastructure.password_service import PasswordHashService


class UserApplicationService:
    """用户应用服务 - 负责编排和事务管理"""

    def __init__(
        self,
        user_repository: IUserRepository,
        user_domain_service: UserDomainService,
    ):
        self._user_repository = user_repository
        self._user_domain_service = user_domain_service

    async def authenticate_user(self, login_id: str, password: str) -> User:
        return await self._user_domain_service.authenticate_user(login_id, password)

    async def create_user(self, command: UserCreateCommand) -> UserResponse:
        """创建用户"""
        # 使用 Domain Service 创建用户
        user = await self._user_domain_service.create_user_with_role(
            username=command.username,
            email=command.email,
            password_hash=command.password_hash,
            first_name=command.first_name,
            last_name=command.last_name,
            organization=command.organization,
        )
        return await self._to_user_response(user)

    async def update_user_profile(self, command: UserUpdateCommand) -> UserResponse:
        """更新用户档案"""
        # 使用 Domain Service 更新用户档案
        user = await self._user_domain_service.update_user_profile(
            user_id=command.user_id,
            first_name=command.first_name,
            last_name=command.last_name,
            avatar_url=command.avatar_url,
            organization=command.organization,
            bio=command.bio
        )

        # 保存用户
        saved_user = await self._user_repository.save(user)
        return await self._to_user_response(saved_user)

    async def get_user_stats(self, user_id: UUID) -> UserStatsResponse:
        """获取用户统计信息"""
        # 这里可以添加特定用户的统计信息
        # 暂时返回全局统计
        return await self.get_global_user_stats()

    async def change_password(self, command: PasswordChangeCommand) -> bool:
        """修改密码"""
        # 使用 Domain Service 修改密码
        user = await self._user_domain_service.change_user_password(
            user_id=command.user_id,
            current_password=command.current_password,
            new_password_hash=command.new_password_hash
        )

        # 保存用户
        await self._user_repository.save(user)
        return True

    async def update_user(self, user_id: UUID, command: UserUpdateCommand) -> UserResponse:
        """更新用户"""
        # 使用 Domain Service 更新用户档案
        user = await self._user_domain_service.update_user_profile(
            user_id=user_id,
            first_name=command.first_name,
            last_name=command.last_name,
            avatar_url=command.avatar_url,
            organization=command.organization,
            bio=command.bio
        )

        # 保存用户
        saved_user = await self._user_repository.save(user)
        return await self._to_user_response(saved_user)

    async def get_user(self, user_id: UUID) -> UserResponse | None:
        """获取用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            return None

        return await self._to_user_response(user)

    async def search_users(self, query: UserSearchQuery) -> list[UserSummaryResponse]:
        """搜索用户"""
        users = await self._user_repository.search_users(
            keyword=query.keyword,
            status=query.status.value if query.status else None,
            organization=query.organization,
            limit=query.limit,
            offset=query.offset
        )

        return [self._to_user_summary_response(user) for user in users]

    async def get_global_user_stats(self) -> UserStatsResponse:
        """获取用户统计"""
        active_count = len(await self._user_repository.find_by_status("active"))
        inactive_count = len(await self._user_repository.find_by_status("inactive"))
        suspended_count = len(await self._user_repository.find_by_status("suspended"))

        return UserStatsResponse(
            total_users=active_count + inactive_count + suspended_count,
            active_users=active_count,
            inactive_users=inactive_count,
            suspended_users=suspended_count
        )

    async def get_user_by_id(self, user_id: UUID) -> UserResponse | None:
        """根据ID获取用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            return None

        return await self._to_user_response(user)

    async def logout_user(self, user_id: UUID) -> None:
        """用户登出,增加key_version使所有token失效"""
        # 使用 Domain Service 处理登出逻辑
        user = await self._user_domain_service.logout_user(user_id)

        # 保存用户
        await self._user_repository.save(user)

    async def invalidate_user_tokens(self, user_id: UUID, reason: str = "权限变更") -> None:
        """使用户所有token失效"""
        # 使用 Domain Service 处理token失效逻辑
        user = await self._user_domain_service.invalidate_user_tokens(user_id, reason)

        # 保存用户
        await self._user_repository.save(user)

    async def change_user_role(self, user_id: UUID, new_role_ids: list[UUID]) -> UserResponse:
        """更改用户角色并使token失效"""
        # 使用 Domain Service 处理角色变更逻辑
        user = await self._user_domain_service.change_user_roles(
            user_id=user_id,
            new_role_ids=new_role_ids,
            operator_id=user_id  # 这里应该传入操作者ID，暂时使用用户自己的ID
        )

        # 保存用户
        saved_user = await self._user_repository.save(user)
        return await self._to_user_response(saved_user)

    async def suspend_user(self, user_id: UUID, reason: str, suspended_by: UUID) -> bool:
        """暂停用户并使token失效"""
        # 使用 Domain Service 处理暂停逻辑
        user = await self._user_domain_service.suspend_user(user_id, reason, suspended_by)

        # 保存用户
        await self._user_repository.save(user)
        return True

    async def assign_user_roles(self, user_id: UUID, role_ids: list[UUID], assigned_by: UUID) -> UserResponse:
        """分配用户角色"""
        # 使用 Domain Service 处理角色分配逻辑
        user = await self._user_domain_service.change_user_roles(
            user_id=user_id,
            new_role_ids=role_ids,
            operator_id=assigned_by
        )

        # 保存用户
        saved_user = await self._user_repository.save(user)
        return await self._to_user_response(saved_user)

    async def get_user_permissions(self, user_id: UUID) -> dict[str, Any]:
        """获取用户完整权限"""
        # 使用 Domain Service 获取权限
        return await self._user_domain_service.get_user_permissions(user_id)

    async def check_user_permission(
        self, user_id: UUID, permission_name: str
    ) -> dict[str, Any]:
        """验证用户权限"""
        # 使用 Domain Service 检查权限
        return await self._user_domain_service.check_user_permission(user_id, permission_name)

    async def check_user_permission_by_parts(
        self, user_id: UUID, resource: str, action: str, module: str | None = None
    ) -> dict[str, Any]:
        """通过资源和操作验证用户权限"""
        # 使用 Domain Service 检查权限
        return await self._user_domain_service.check_user_permission_by_parts(
            user_id, resource, action, module
        )

    async def activate_user(self, user_id: UUID) -> bool:
        """激活用户"""
        # 使用 Domain Service 处理激活逻辑
        user = await self._user_domain_service.activate_user(user_id)

        # 保存用户
        await self._user_repository.save(user)
        return True

    async def validate_role_assignment(self, user_id: UUID, role_ids: list[UUID], assigner_id: UUID) -> dict:
        """验证角色分配权限"""
        # 这个方法需要角色相关的Domain Service，暂时保留简单实现
        user = await self._user_repository.find_by_id(user_id)
        assigner = await self._user_repository.find_by_id(assigner_id)

        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在")
        if not assigner:
            raise ApplicationException(f"分配者 {assigner_id} 不存在")

        validation_results = []

        for role_id in role_ids:
            role = await self._role_repository.find_by_id(role_id)
            if not role:
                validation_results.append({
                    "role_id": str(role_id),
                    "can_assign": False,
                    "reason": "角色不存在"
                })
                continue

            # 简化的权限检查
            can_assign = True
            reason = "可以分配"

            if role.is_system_role and not assigner.is_super_admin():
                can_assign = False
                reason = "只有超级管理员才能分配系统角色"

            validation_results.append({
                "role_id": str(role_id),
                "role_name": role.name,
                "can_assign": can_assign,
                "reason": reason
            })

        all_assignable = all(result["can_assign"] for result in validation_results)

        return {
            "user_id": str(user_id),
            "assigner_id": str(assigner_id),
            "all_roles_assignable": all_assignable,
            "role_validations": validation_results
        }

    async def _to_user_response(self, user: User) -> UserResponse:
        """转换为用户响应DTO"""
        profile = UserProfileResponse(
            first_name=user.profile.first_name,
            last_name=user.profile.last_name,
            full_name=user.profile.full_name,
            avatar_url=user.profile.avatar_url,
            organization=user.profile.organization,
            bio=user.profile.bio
        )

        roles = []
        is_system_role = False
        for role in user.roles:
            if role.is_system_role:
                is_system_role = True

            role_permissions = []
            for perm in role.permissions:
                role_permissions.append(f"{perm.module}.{perm.resource}:{perm.action}")

            roles.append(RoleResponse(
                id=role.id,
                name=role.name,
                role_type=role.role_type,
                is_system_role=role.is_system_role,
                description=role.description,
                permissions=role_permissions
            ))

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email.value,
            profile=profile,
            status=user.status,
            email_verified=user.email_verified,
            is_system_role=is_system_role,
            roles=roles,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )

    def _to_user_summary_response(self, user: User) -> UserSummaryResponse:
        """转换为用户摘要响应DTO"""
        return UserSummaryResponse(
            id=user.id,
            username=user.username,
            email=user.email.value,
            full_name=user.profile.full_name,
            organization=user.profile.organization,
            status=user.status,
            email_verified=user.email_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
