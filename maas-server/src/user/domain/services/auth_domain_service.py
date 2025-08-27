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
from uuid import UUID

import jwt

from config.settings import settings
from shared.domain.base import DomainException
from user.domain.models import User


class AuthDomainService:
    """认证服务"""

    def __init__(self):
        # ❌ 移除Repository依赖 - Domain Service应该是纯业务逻辑
        # self._user_repository = user_repository
        self._secret_key = settings.get_jwt_secret_key()
        self._token_type= "Bearer"
        self._algorithm = "HS256"
        self._access_token_expire_minutes = settings.security.jwt_access_token_expire_minutes
        self._refresh_token_expire_days = settings.security.jwt_refresh_token_expire_days

    def create_access_token(self, user: User) -> str:
        """创建访问令牌"""
        user.increment_key_version()
        expire = datetime.utcnow() + timedelta(minutes=self._access_token_expire_minutes)
        payload = {
            "sub": str(user.id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "key_version": user.key_version,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user: User) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=self._refresh_token_expire_days)
        payload = {
            "sub": str(user.id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def validate_refresh_token(self, refresh_token: str) -> UUID:
        """验证刷新令牌并返回用户ID（纯业务逻辑）"""
        try:
            payload = jwt.decode(refresh_token, self._secret_key, algorithms=[self._algorithm])
        except jwt.InvalidTokenError:
            raise DomainException("无效的令牌")

        # 检查是否是刷新令牌
        if payload.get("type") != "refresh":
            raise DomainException("无效的刷新令牌")

        user_id = UUID(payload.get("sub"))
        return user_id

    def validate_user_for_token_refresh(self, user: User) -> None:
        """验证用户是否可以刷新令牌（纯业务逻辑）"""
        if not user:
            raise DomainException("用户不存在")

        if not user.is_active:
            raise DomainException("用户已被暂停")


