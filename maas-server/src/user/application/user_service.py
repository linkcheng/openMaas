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

from sqlalchemy.ext.asyncio import AsyncSession

from shared.application.exceptions import ApplicationException, ErrorCode
from shared.infrastructure.transaction_manager import transactional
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
from user.domain.repositories import IUserRepository, IRoleRepository
from user.domain.services.user_domain_service import UserDomainService


class UserApplicationService:
    """用户应用服务 - 负责编排和事务管理"""

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
    ):
        self._user_domain_service = user_domain_service
        self._user_repository = user_repository
        self._role_repository = role_repository

    @transactional()
    async def create_user(
        self,
        command: UserCreateCommand,
        session: AsyncSession
    ) -> UserResponse:
        """创建用户 - 事务操作"""
        # 1. 使用Domain Service验证创建数据
        self._user_domain_service.validate_user_creation_data(
            command.username, command.email
        )
        
        # 2. Application Service检查用户唯一性
        existing_user_by_email = await self._user_repository.find_by_email(command.email)
        existing_user_by_username = await self._user_repository.find_by_username(command.username)
        self._user_domain_service.validate_user_uniqueness(
            existing_user_by_email, existing_user_by_username, command.email, command.username
        )
        
        # 3. Application Service获取默认角色
        role = await self._role_repository.find_by_name(command.role_type)
        
        # 4. 使用Domain Service创建用户实体
        user = self._user_domain_service.create_user_entity(
            username=command.username,
            email=command.email,
            password_hash=command.password_hash,
            default_role=role,
            first_name=command.first_name,
            last_name=command.last_name,
            organization=command.organization,
        )
        
        # 5. Application Service保存用户
        saved_user = await self._user_repository.save(user)
        # 事务在装饰器中自动提交
        return await self._to_user_response(saved_user)

    @transactional()
    async def update_user_profile(
        self,
        command: UserUpdateCommand,
        session: AsyncSession
    ) -> UserResponse:
        """更新用户档案 - 事务操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(command.user_id)
        if not user:
            raise ApplicationException(f"用户 {command.user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. 使用Domain Service更新用户档案
        updated_user = self._user_domain_service.update_user_profile_entity(
            user=user,
            first_name=command.first_name,
            last_name=command.last_name,
            avatar_url=command.avatar_url,
            organization=command.organization,
            bio=command.bio
        )

        # 3. Application Service保存用户
        saved_user = await self._user_repository.save(updated_user)
        # 事务在装饰器中自动提交
        return await self._to_user_response(saved_user)

    @transactional()
    async def change_password(
        self,
        command: PasswordChangeCommand,
        session: AsyncSession
    ) -> bool:
        """修改密码 - 事务操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(command.user_id)
        if not user:
            raise ApplicationException(f"用户 {command.user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. 使用Domain Service修改密码
        updated_user = self._user_domain_service.change_user_password_entity(
            user=user,
            current_password=command.current_password,
            new_password_hash=command.new_password_hash
        )

        # 3. Application Service保存用户
        await self._user_repository.save(updated_user)
        # 事务在装饰器中自动提交
        return True

    async def search_users(
        self,
        query: UserSearchQuery,
    ) -> list[UserSummaryResponse]:
        """搜索用户 - 只读操作"""
        users = await self._user_repository.search_users(
            keyword=query.keyword,
            status=query.status.value if query.status else None,
            organization=query.organization,
            limit=query.limit,
            offset=query.offset
        )

        return [self._to_user_summary_response(user) for user in users]

    async def get_global_user_stats(
        self,
    ) -> UserStatsResponse:
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

    @transactional()
    async def logout_user(
        self, 
        user_id: UUID,
        session: AsyncSession
    ) -> None:
        """用户登出,增加key_version使所有token失效 - 事务操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. 使用Domain Service处理登出逻辑
        updated_user = self._user_domain_service.logout_user_entity(user)

        # 3. Application Service保存用户
        await self._user_repository.save(updated_user)
        # 事务在装饰器中自动提交

    @transactional()
    async def invalidate_user_tokens(
        self, 
        user_id: UUID, 
        *,
        reason: str = "权限变更",
        session: AsyncSession
    ) -> None:
        """使用户所有token失效 - 事务操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. 使用Domain Service处理token失效逻辑
        updated_user = self._user_domain_service.invalidate_user_tokens_entity(user, reason)

        # 3. Application Service保存用户
        await self._user_repository.save(updated_user)
        # 事务在装饰器中自动提交

    @transactional()
    async def suspend_user(
        self, 
        user_id: UUID, 
        reason: str, 
        suspended_by: UUID,
        session: AsyncSession
    ) -> bool:
        """暂停用户并使token失效 - 事务操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. 使用Domain Service处理暂停逻辑
        updated_user = self._user_domain_service.suspend_user_entity(user, reason, suspended_by)

        # 3. Application Service保存用户
        await self._user_repository.save(updated_user)
        # 事务在装饰器中自动提交
        return True

    @transactional()
    async def assign_user_roles(
        self, 
        user_id: UUID, 
        role_ids: list[UUID], 
        assigned_by: UUID,
        session: AsyncSession
    ) -> UserResponse:
        """分配用户角色 - 事务操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. Application Service查询角色
        new_roles = []
        for role_id in role_ids:
            role = await self._role_repository.find_by_id(role_id)
            if role:
                new_roles.append(role)
        
        # 3. 使用Domain Service处理角色分配逻辑
        updated_user = self._user_domain_service.change_user_roles_entity(
            user=user,
            new_roles=new_roles,
            operator_id=assigned_by
        )

        # 4. Application Service保存用户
        saved_user = await self._user_repository.save(updated_user)
        # 事务在装饰器中自动提交
        return await self._to_user_response(saved_user)

    async def get_user_permissions(
        self, 
        user_id: UUID,
    ) -> dict[str, Any]:
        """获取用户完整权限 - 只读操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. 使用Domain Service计算权限
        return self._user_domain_service.calculate_user_permissions(user)

    async def check_user_permission(
        self, 
        user_id: UUID, 
        permission_name: str,
    ) -> dict[str, Any]:
        """验证用户权限 - 只读操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. 使用Domain Service检查权限
        return self._user_domain_service.check_user_permission_logic(user, permission_name)

    @transactional()
    async def activate_user(
        self, 
        user_id: UUID,
        session: AsyncSession
    ) -> bool:
        """激活用户 - 事务操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在", ErrorCode.BIZ_USER_NOT_FOUND)
        
        # 2. 使用Domain Service处理激活逻辑
        updated_user = self._user_domain_service.activate_user_entity(user)

        # 3. Application Service保存用户
        await self._user_repository.save(updated_user)
        # 事务在装饰器中自动提交
        return True

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
