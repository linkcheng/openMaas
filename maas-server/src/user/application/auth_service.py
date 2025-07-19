"""用户应用层 - 认证服务"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from config.settings import settings
from shared.application.exceptions import ApplicationException
from user.application.schemas import AuthTokenResponse
from user.domain.repositories import UserRepository


class AuthService:
    """认证服务"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
        self._secret_key = settings.get_jwt_secret_key()
        self._algorithm = "HS256"
        self._access_token_expire_minutes = settings.security.jwt_access_token_expire_minutes
        self._refresh_token_expire_days = settings.security.jwt_refresh_token_expire_days

    def create_access_token(self, user_id: UUID, permissions: list[str] | None = None) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=self._access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "permissions": permissions or [],
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: UUID) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=self._refresh_token_expire_days)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str) -> dict[str, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ApplicationException("令牌已过期")
        except jwt.InvalidTokenError:
            raise ApplicationException("无效令牌")

    def get_user_from_token(self, token: str) -> UUID | None:
        """从令牌获取用户ID"""
        try:
            payload = self.verify_token(token)
            user_id_str = payload.get("sub")
            if user_id_str:
                return UUID(user_id_str)
        except Exception:
            pass
        return None

    async def refresh_access_token(self, refresh_token: str) -> AuthTokenResponse:
        """刷新访问令牌"""
        try:
            payload = self.verify_token(refresh_token)

            # 检查是否是刷新令牌
            if payload.get("type") != "refresh":
                raise ApplicationException("无效的刷新令牌")

            user_id = UUID(payload.get("sub"))
            user = await self._user_repository.find_by_id(user_id)

            if not user:
                raise ApplicationException("用户不存在")

            if not user.is_active:
                raise ApplicationException("用户已被暂停")

            # 创建新的令牌
            return await self._create_token_response(user)

        except jwt.ExpiredSignatureError:
            raise ApplicationException("刷新令牌已过期")
        except jwt.InvalidTokenError:
            raise ApplicationException("无效的刷新令牌")

    async def _create_token_response(self, user) -> AuthTokenResponse:
        """创建令牌响应"""
        from .services import UserApplicationService

        # 获取用户权限
        permissions = []
        for role in user.roles:
            permissions.extend([str(perm) for perm in role.permissions])

        access_token = self.create_access_token(user.id, permissions)
        refresh_token = self.create_refresh_token(user.id)

        # 创建用户响应数据
        user_app_service = UserApplicationService(
            user_repository=self._user_repository,
            role_repository=None,  # 这里需要依赖注入
            password_service=None,
            email_service=None,
            api_key_service=None,
        )
        user_response = await user_app_service._map_to_response(user)

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._access_token_expire_minutes * 60,
            user=user_response,
        )


class ApiKeyAuthService:
    """API密钥认证服务"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def authenticate_api_key(self, api_key: str) -> UUID | None:
        """通过API密钥认证"""
        from .services import ApiKeyService

        # 哈希API密钥
        key_hash = ApiKeyService.hash_api_key(api_key)

        # 查找用户
        user = await self._user_repository.find_by_api_key_hash(key_hash)
        if not user:
            return None

        # 检查用户状态
        if not user.is_active:
            return None

        # 查找并验证API密钥
        api_key_entity = None
        for key in user.api_keys:
            if key.key_hash == key_hash:
                api_key_entity = key
                break

        if not api_key_entity or not api_key_entity.is_valid():
            return None

        # 记录使用
        api_key_entity.use()
        await self._user_repository.save(user)

        return user.id


class PermissionService:
    """权限服务"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def check_permission(self, user_id: UUID, resource: str, action: str) -> bool:
        """检查用户权限"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            return False

        return user.has_permission(resource, action)

    async def get_user_permissions(self, user_id: UUID) -> list[str]:
        """获取用户所有权限"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            return []

        permissions = []
        for role in user.roles:
            permissions.extend([str(perm) for perm in role.permissions])

        return list(set(permissions))  # 去重


class EmailService:
    """邮件服务"""

    def __init__(self):
        # 这里应该配置邮件发送服务（如SMTP等）
        pass

    async def send_verification_email(self, email: str, verification_token: str) -> bool:
        """发送验证邮件"""
        # 实现邮件发送逻辑
        # 这里暂时返回True，实际应该集成邮件服务
        verification_url = f"{settings.security.frontend_url}/verify-email?token={verification_token}"
        print(f"发送验证邮件到: {email}")
        print(f"验证链接: {verification_url}")
        return True

    async def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """发送密码重置邮件"""
        # 实现密码重置邮件发送逻辑
        reset_url = f"{settings.security.frontend_url}/reset-password?token={reset_token}"
        print(f"发送密码重置邮件到: {email}")
        print(f"重置链接: {reset_url}")
        return True

    async def send_welcome_email(self, email: str, username: str) -> bool:
        """发送欢迎邮件"""
        # 实现欢迎邮件发送逻辑
        print(f"发送欢迎邮件到: {email}, 用户名: {username}")
        return True
