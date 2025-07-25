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

import hashlib
import secrets
from datetime import datetime
from uuid import UUID

from loguru import logger

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
from user.domain.models import (
    InvalidCredentialsException,
    User,
    UserAlreadyExistsException,
    UserProfile,
    UserStatus,
)
from user.domain.repositories import RoleRepository, UserRepository


class PasswordHashService:
    """密码哈希服务"""

    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )
        return f"{salt}:{password_hash.hex()}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码"""
        # 检查输入参数
        if not password or not hashed_password:
            return False

        try:
            salt, stored_hash = hashed_password.split(":")
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                100000
            )
            return password_hash.hex() == stored_hash
        except (ValueError, AttributeError, IndexError) as e:
            logger.error(f"密码验证失败: {e}")
            return False


class EmailVerificationService:
    """邮箱验证服务"""

    @staticmethod
    def generate_verification_code() -> str:
        """生成验证码"""
        return str(secrets.randbelow(900000) + 100000)

    @staticmethod
    def generate_verification_token() -> str:
        """生成验证令牌"""
        return secrets.token_urlsafe(32)


class UserApplicationService:
    """用户应用服务"""

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        password_service: PasswordHashService,
        email_service: EmailVerificationService,
    ):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._password_service = password_service
        self._email_service = email_service

    async def create_user(self, command: UserCreateCommand) -> UserResponse:
        """创建用户"""
        # 检查用户是否已存在
        existing_user = await self._user_repository.find_by_email(command.email)
        if existing_user:
            raise UserAlreadyExistsException(f"邮箱 {command.email} 已被使用")

        existing_user = await self._user_repository.find_by_username(command.username)
        if existing_user:
            raise UserAlreadyExistsException(f"用户名 {command.username} 已被使用")

        # 创建用户
        user = User.create(
            username=command.username,
            email=command.email,
            password_hash=command.password_hash,
            first_name=command.first_name,
            last_name=command.last_name,
            organization=command.organization
        )

        # 分配默认角色
        default_role = await self._role_repository.get_default_role()
        user.add_role(default_role)

        # 保存用户
        saved_user = await self._user_repository.save(user)

        logger.info(f"用户创建成功: {saved_user.username} ({saved_user.email.value})")

        return await self._to_user_response(saved_user)

    async def update_user_profile(self, command: UserUpdateCommand) -> UserResponse:
        """更新用户档案"""
        user = await self._user_repository.find_by_id(command.user_id)
        if not user:
            raise ApplicationException(f"用户 {command.user_id} 不存在")

        # 更新用户档案
        profile = UserProfile(
            first_name=command.first_name,
            last_name=command.last_name,
            avatar_url=command.avatar_url,
            organization=command.organization,
            bio=command.bio
        )
        user.update_profile(profile)

        # 保存用户
        saved_user = await self._user_repository.save(user)

        logger.info(f"用户 {saved_user.username} 档案已更新")

        return await self._to_user_response(saved_user)

    async def get_user_stats(self, user_id: UUID) -> UserStatsResponse:
        """获取用户统计信息"""
        # 这里可以添加特定用户的统计信息
        # 暂时返回全局统计
        return await self.get_user_stats()

    async def change_password(self, command: PasswordChangeCommand) -> bool:
        """修改密码"""
        user = await self._user_repository.find_by_id(command.user_id)
        if not user:
            raise ApplicationException(f"用户 {command.user_id} 不存在")

        # 验证旧密码
        if not self._password_service.verify_password(command.current_password, user.password_hash):
            raise InvalidCredentialsException("当前密码不正确")

        # 更新密码
        user.password_hash = command.new_password_hash

        # 增加密钥版本以使所有现有token失效
        user.increment_key_version()

        # 保存用户
        await self._user_repository.save(user)

        logger.info(f"用户 {user.username} 密码修改成功")

        return True

    async def update_user(self, user_id: UUID, command: UserUpdateCommand) -> UserResponse:
        """更新用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在")

        # 更新用户档案
        profile = UserProfile(
            first_name=command.first_name,
            last_name=command.last_name,
            avatar_url=command.avatar_url,
            organization=command.organization,
            bio=command.bio
        )
        user.update_profile(profile)

        # 保存用户
        saved_user = await self._user_repository.save(user)

        logger.info(f"用户更新成功: {saved_user.username}")

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

    async def get_user_stats(self) -> UserStatsResponse:
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
        for role in user.roles:
            role_permissions = []
            for perm in role.permissions:
                role_permissions.append(f"{perm.resource}:{perm.action}")

            roles.append(RoleResponse(
                id=role.id,
                name=role.name,
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
            roles=roles,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )

    async def authenticate_user(self, login_id: str, password: str) -> UserResponse:
        """认证用户"""
        # 根据登录ID查找用户(可以是用户名或邮箱)
        user = None
        if "@" in login_id:
            # 看起来是邮箱
            user = await self._user_repository.find_by_email(login_id)
        else:
            # 看起来是用户名
            user = await self._user_repository.find_by_username(login_id)

        if not user:
            raise InvalidCredentialsException("用户名或密码错误")

        # 验证密码
        if not self._password_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsException("用户名或密码错误")

        # 检查用户状态
        if user.status != UserStatus.ACTIVE:
            raise InvalidCredentialsException("用户账户已被禁用")

        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await self._user_repository.save(user)

        logger.info(f"用户 {user.username} 登录成功")

        return await self._to_user_response(user)

    async def get_user_by_id(self, user_id: UUID) -> UserResponse | None:
        """根据ID获取用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            return None

        return await self._to_user_response(user)

    async def logout_user(self, user_id: UUID) -> None:
        """用户登出,增加key_version使所有token失效"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在")

        # 增加密钥版本以使所有现有token失效
        user.increment_key_version()
        await self._user_repository.save(user)

        logger.info(f"用户 {user.username} 已登出,token已失效")

    async def invalidate_user_tokens(self, user_id: UUID, reason: str = "权限变更") -> None:
        """使用户所有token失效"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在")

        # 增加密钥版本以使所有现有token失效
        user.increment_key_version()
        await self._user_repository.save(user)

        logger.info(f"用户 {user.username} 的所有token已失效，原因: {reason}")

    async def change_user_role(self, user_id: UUID, new_role_ids: list[UUID]) -> UserResponse:
        """更改用户角色并使token失效"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在")

        # 获取新角色
        new_roles = []
        for role_id in new_role_ids:
            role = await self._role_repository.find_by_id(role_id)
            if role:
                new_roles.append(role)

        # 清除现有角色
        for existing_role in user.roles:
            user.remove_role(existing_role)

        # 添加新角色
        for new_role in new_roles:
            user.add_role(new_role)

        # 使所有现有token失效
        user.increment_key_version()

        # 保存用户
        saved_user = await self._user_repository.save(user)

        logger.info(f"用户 {user.username} 角色已更新，token已失效")

        return await self._to_user_response(saved_user)

    async def suspend_user(self, user_id: UUID, reason: str) -> bool:
        """暂停用户并使token失效"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在")

        # 暂停用户
        user.suspend(reason)

        # 使所有现有token失效
        user.increment_key_version()

        # 保存用户
        await self._user_repository.save(user)

        logger.info(f"用户 {user.username} 已暂停，原因: {reason}，token已失效")

        return True

    async def activate_user(self, user_id: UUID) -> bool:
        """激活用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException(f"用户 {user_id} 不存在")

        # 激活用户
        user.activate()

        # 保存用户（激活时不需要使token失效，用户需要重新登录才能获取token）
        await self._user_repository.save(user)

        logger.info(f"用户 {user.username} 已激活")

        return True

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
