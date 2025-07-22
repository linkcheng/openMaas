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

"""用户应用层 - 应用服务"""

import hashlib
import secrets
from datetime import datetime
from uuid import UUID
from loguru import logger

from shared.application.exceptions import ApplicationException
from user.application.schemas import (
    ApiKeyCreateResponse,
    PasswordChangeCommand,
    UserCreateCommand,
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
    UserQuota,
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
    def generate_verification_token() -> str:
        """生成验证令牌"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_reset_token() -> str:
        """生成重置令牌"""
        return secrets.token_urlsafe(32)


class ApiKeyService:
    """API密钥服务"""

    @staticmethod
    def generate_api_key() -> str:
        """生成API密钥"""
        return f"mk-{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """哈希API密钥"""
        return hashlib.sha256(api_key.encode()).hexdigest()


class UserApplicationService:
    """用户应用服务"""

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        password_service: PasswordHashService,
        email_service: EmailVerificationService,
        api_key_service: ApiKeyService,
    ):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._password_service = password_service
        self._email_service = email_service
        self._api_key_service = api_key_service

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
            organization=command.organization,
        )

        # 分配默认角色
        default_role = await self._role_repository.find_by_name("user")
        if default_role:
            user.add_role(default_role)

        # 设置默认配额
        default_quota = UserQuota(
            api_calls_limit=1000,
            api_calls_used=0,
            storage_limit=1024 * 1024 * 1024,  # 1GB
            storage_used=0,
            compute_hours_limit=10,
            compute_hours_used=0,
        )
        user.set_quota(default_quota)

        # 保存用户
        await self._user_repository.save(user)

        return await self._map_to_response(user)

    async def authenticate_user(self, login_id: str, password: str) -> UserResponse:
        """认证用户 - 支持邮箱或用户名登录"""
        # 首先尝试按邮箱查找
        user = None
        if "@" in login_id:
            # 包含@符号，当作邮箱处理
            user = await self._user_repository.find_by_email(login_id)
        else:
            # 不包含@符号，当作用户名处理
            user = await self._user_repository.find_by_username(login_id)

        # 如果用户名查找失败，再尝试邮箱查找（防止用户名中有@的情况）
        if not user and "@" not in login_id:
            user = await self._user_repository.find_by_email(login_id)

        if not user:
            raise InvalidCredentialsException("用户名/邮箱或密码错误")

        if not self._password_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsException("用户名/邮箱或密码错误")

        # TODO: 暂时移除邮箱验证要求，后续可重新启用
        # if not user.email_verified:
        #     raise EmailNotVerifiedException("邮箱未验证")

        if user.status != UserStatus.ACTIVE:
            raise ApplicationException("账户已被暂停")

        # 记录登录
        user.record_login()
        await self._user_repository.save(user)

        return await self._map_to_response(user)

    async def get_user_by_id(self, user_id: UUID) -> UserResponse | None:
        """根据ID获取用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            return None
        return await self._map_to_response(user)

    async def update_user_profile(self, command: UserUpdateCommand) -> UserResponse:
        """更新用户档案"""
        user = await self._user_repository.find_by_id(command.user_id)
        if not user:
            raise ApplicationException("用户不存在")

        # 创建新的用户档案
        new_profile = UserProfile(
            first_name=command.first_name or user.profile.first_name,
            last_name=command.last_name or user.profile.last_name,
            avatar_url=command.avatar_url or user.profile.avatar_url,
            organization=command.organization or user.profile.organization,
            bio=command.bio or user.profile.bio,
        )

        user.update_profile(new_profile)
        await self._user_repository.save(user)

        return await self._map_to_response(user)

    async def change_password(self, command: PasswordChangeCommand) -> bool:
        """修改密码"""
        user = await self._user_repository.find_by_id(command.user_id)
        if not user:
            raise ApplicationException("用户不存在")

        if not self._password_service.verify_password(
            command.current_password, user.password_hash
        ):
            raise InvalidCredentialsException("当前密码错误")

        user.password_hash = command.new_password_hash
        user.updated_at = datetime.utcnow()
        await self._user_repository.save(user)

        return True

    async def verify_email(self, user_id: UUID) -> bool:
        """验证邮箱"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException("用户不存在")

        user.verify_email()
        await self._user_repository.save(user)

        return True

    async def create_api_key(
        self, user_id: UUID, name: str, permissions: list[str], expires_at: datetime | None = None
    ) -> ApiKeyCreateResponse:
        """创建API密钥"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException("用户不存在")

        # 生成API密钥
        api_key = self._api_key_service.generate_api_key()
        key_hash = self._api_key_service.hash_api_key(api_key)

        # 创建API密钥实体
        api_key_entity = user.create_api_key(
            name=name,
            key_hash=key_hash,
            permissions=permissions,
            expires_at=expires_at,
        )

        await self._user_repository.save(user)

        return ApiKeyCreateResponse(
            id=api_key_entity.id,
            name=api_key_entity.name,
            api_key=api_key,  # 只在创建时返回
            permissions=api_key_entity.permissions,
            expires_at=api_key_entity.expires_at,
            created_at=api_key_entity.created_at,
        )

    async def revoke_api_key(self, user_id: UUID, api_key_id: UUID) -> bool:
        """撤销API密钥"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException("用户不存在")

        user.revoke_api_key(api_key_id)
        await self._user_repository.save(user)

        return True

    async def search_users(self, query: UserSearchQuery) -> list[UserSummaryResponse]:
        """搜索用户"""
        users = await self._user_repository.search(query)
        return [
            UserSummaryResponse(
                id=user.id,
                username=user.username,
                email=user.email.value,
                full_name=user.profile.full_name,
                organization=user.profile.organization,
                status=user.status,
                email_verified=user.email_verified,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
            )
            for user in users
        ]

    async def get_user_stats(self, user_id: UUID) -> UserStatsResponse:
        """获取用户统计"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException("用户不存在")

        # 这里应该从实际的使用统计服务获取数据
        # 暂时返回模拟数据
        return UserStatsResponse(
            total_api_calls=user.quota.api_calls_used if user.quota else 0,
            total_storage_used=user.quota.storage_used if user.quota else 0,
            total_compute_hours=user.quota.compute_hours_used if user.quota else 0,
            models_created=0,
            applications_created=0,
            last_30_days_activity={},
        )

    async def suspend_user(self, user_id: UUID, reason: str) -> bool:
        """暂停用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException("用户不存在")

        user.suspend(reason)
        await self._user_repository.save(user)

        return True

    async def activate_user(self, user_id: UUID) -> bool:
        """激活用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise ApplicationException("用户不存在")

        user.activate()
        await self._user_repository.save(user)

        return True

    async def _map_to_response(self, user: User) -> UserResponse:
        """映射到响应DTO"""
        from .schemas import RoleResponse, UserProfileResponse, UserQuotaResponse

        profile = UserProfileResponse(
            first_name=user.profile.first_name,
            last_name=user.profile.last_name,
            full_name=user.profile.full_name,
            avatar_url=user.profile.avatar_url,
            organization=user.profile.organization,
            bio=user.profile.bio,
        )

        quota = None
        if user.quota:
            quota = UserQuotaResponse(
                api_calls_limit=user.quota.api_calls_limit,
                api_calls_used=user.quota.api_calls_used,
                api_calls_remaining=user.quota.api_calls_limit - user.quota.api_calls_used,
                api_usage_percentage=user.quota.get_api_usage_percentage(),
                storage_limit=user.quota.storage_limit,
                storage_used=user.quota.storage_used,
                storage_remaining=user.quota.storage_limit - user.quota.storage_used,
                storage_usage_percentage=user.quota.get_storage_usage_percentage(),
                compute_hours_limit=user.quota.compute_hours_limit,
                compute_hours_used=user.quota.compute_hours_used,
                compute_hours_remaining=user.quota.compute_hours_limit - user.quota.compute_hours_used,
            )

        roles = [
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                permissions=[str(perm) for perm in role.permissions],
            )
            for role in user.roles
        ]

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email.value,
            profile=profile,
            status=user.status,
            email_verified=user.email_verified,
            roles=roles,
            quota=quota,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
        )
