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

from shared.application.exceptions import (
    ApplicationException,
    TokenRefreshRequiredException,
    TokenVersionMismatchException,
)
from shared.domain.base import DomainException
from config.settings import settings
from user.application.schemas import (
    AuthTokenResponse,
    RoleResponse,
    UserProfileResponse,
    UserResponse,
)
from user.domain.services.auth_domain_service import AuthDomainService
from user.domain.services.user_domain_service import UserDomainService

class AuthService:
    """认证服务"""

    def __init__(self, auth_domain_svc: AuthDomainService, user_domain_svc: UserDomainService):
        self._auth_domain_svc = auth_domain_svc
        self._user_domain_svc = user_domain_svc

    async def refresh_access_token(self, refresh_token: str) -> AuthTokenResponse:
        """刷新访问令牌"""

        auth_token = self._auth_domain_svc.refresh_access_token(refresh_token)
        return AuthTokenResponse(
            access_token=auth_token.access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=auth_token.expires_in,
        )

    async def create_token_response(self, login_id: str, password: str) -> AuthTokenResponse:
        """创建令牌响应"""
        user = await self._user_domain_svc.authenticate_user(login_id, password)

        access_token = self._auth_domain_svc.create_access_token(user.id, user.key_version)
        refresh_token = self._auth_domain_svc.create_refresh_token(user.id)

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.security.jwt_access_token_expire_minutes * 60,
        )


