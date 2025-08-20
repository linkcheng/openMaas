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

"""认证服务"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from config.settings import settings
from shared.domain.base import DomainException
from user.domain.models import AuthToken, User
from user.domain.repositories import IUserRepository


class AuthDomainService:
    """认证服务"""

    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
        self._secret_key = settings.get_jwt_secret_key()
        self._algorithm = "HS256"
        self._access_token_expire_minutes = settings.security.jwt_access_token_expire_minutes
        self._refresh_token_expire_days = settings.security.jwt_refresh_token_expire_days

    def create_access_token(self, user_id: UUID, key_version: int) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=self._access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "key_version": key_version,
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

    async def verify_access_token(self, token: str) -> dict[str, Any]:
        """验证令牌并检查用户key_version"""

        payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

        # 如果是访问令牌，需要验证key_version
        if payload.get("type") == "access":
            user_id = UUID(payload.get("sub"))
            token_key_version = payload.get("key_version")

            if token_key_version is None:
                raise DomainException("令牌缺少版本信息")

            # 从数据库获取用户当前的key_version
            user = await self._user_repository.find_by_id(user_id)
            if not user:
                raise DomainException("用户不存在")

            # 验证key_version是否匹配
            if user.key_version != token_key_version:
                raise DomainException("令牌版本不匹配")

        return payload

    async def verify_token_and_check_user(self, token: str) -> tuple[dict[str, Any], User]:
        """验证令牌并返回关联用户

        额外校验：
        - 确保用户存在
        - access token 下校验 key_version 一致
        - 校验用户是否处于可用状态
        """
        payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

        user_id = UUID(payload.get("sub"))
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException("用户不存在")

        # access token 校验版本
        if payload.get("type") == "access":
            token_key_version = payload.get("key_version")
            if token_key_version is None:
                raise DomainException("令牌缺少版本信息")
            if user.key_version != token_key_version:
                raise DomainException("令牌版本不匹配")

        # 校验用户状态
        if not user.is_active:
            raise DomainException("用户已被暂停")

        return payload, user


    async def refresh_access_token(self, refresh_token: str) -> AuthToken:
        """刷新访问令牌"""

        payload = jwt.decode(refresh_token, self._secret_key, algorithms=[self._algorithm])

        # 检查是否是刷新令牌
        if payload.get("type") != "refresh":
            raise DomainException("无效的刷新令牌")

        user_id = UUID(payload.get("sub"))
        user = await self._user_repository.find_by_id(user_id)

        if not user:
            raise DomainException("用户不存在")

        if not user.is_active:
            raise DomainException("用户已被暂停")

        access_token = self.create_access_token(user.id, user.key_version)

        return AuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._access_token_expire_minutes * 60,
        )


