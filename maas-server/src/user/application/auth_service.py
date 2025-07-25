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

"""用户应用层 - 认证服务"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from config.settings import settings
from shared.application.exceptions import (
    ApplicationException,
    TokenRefreshRequiredException,
    TokenVersionMismatchException,
)
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

    def create_access_token(self, user_id: UUID, key_version: int, permissions: list[str] | None = None) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=self._access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "key_version": key_version,
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

    async def verify_token(self, token: str) -> dict[str, Any]:
        """验证令牌并检查用户key_version"""
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

            # 如果是访问令牌，需要验证key_version
            if payload.get("type") == "access":
                user_id = UUID(payload.get("sub"))
                token_key_version = payload.get("key_version")

                if token_key_version is None:
                    raise ApplicationException("令牌缺少版本信息")

                # 从数据库获取用户当前的key_version
                user = await self._user_repository.find_by_id(user_id)
                if not user:
                    raise ApplicationException("用户不存在")

                # 验证key_version是否匹配
                if user.key_version != token_key_version:
                    raise TokenVersionMismatchException()

            return payload
        except jwt.ExpiredSignatureError:
            raise TokenRefreshRequiredException("令牌已过期")
        except jwt.InvalidTokenError:
            raise ApplicationException("无效令牌")

    async def get_user_from_token(self, token: str) -> UUID | None:
        """从令牌获取用户ID"""
        try:
            payload = await self.verify_token(token)
            user_id_str = payload.get("sub")
            if user_id_str:
                return UUID(user_id_str)
        except Exception:
            pass
        return None

    async def refresh_access_token(self, refresh_token: str) -> AuthTokenResponse:
        """刷新访问令牌"""
        try:
            payload = await self.verify_token(refresh_token)

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
            from .services import UserApplicationService

            # 创建临时的 UserApplicationService 来转换用户对象
            user_app_service = UserApplicationService(
                user_repository=self._user_repository,
                role_repository=None,
                password_service=None,
                email_service=None,
            )
            user_response = await user_app_service._to_user_response(user)
            return await self._create_token_response(user_response)

        except jwt.ExpiredSignatureError:
            raise ApplicationException("刷新令牌已过期")
        except jwt.InvalidTokenError:
            raise ApplicationException("无效的刷新令牌")

    async def _create_token_response(self, user_response) -> AuthTokenResponse:
        """创建令牌响应"""
        # 获取用户权限
        permissions = []
        for role in user_response.roles:
            permissions.extend(role.permissions)

        # 获取用户的key_version
        user = await self._user_repository.find_by_id(user_response.id)
        if not user:
            raise ApplicationException("用户不存在")

        access_token = self.create_access_token(user_response.id, user.key_version, permissions)
        refresh_token = self.create_refresh_token(user_response.id)

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._access_token_expire_minutes * 60,
            user=user_response,
        )


