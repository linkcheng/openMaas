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

from loguru import logger
from config.settings import settings
from user.application.schemas import (
    AuthTokenResponse,
)
from user.domain.services.auth_domain_service import AuthDomainService
from user.domain.services.user_domain_service import UserDomainService
from user.domain.models import User


class AuthService:
    """认证服务"""

    def __init__(self, auth_domain_svc: AuthDomainService, user_domain_svc: UserDomainService):
        self._auth_domain_svc = auth_domain_svc
        self._user_domain_svc = user_domain_svc

    async def refresh_access_token(self, refresh_token: str) -> AuthTokenResponse:
        """刷新访问令牌"""
        logger.info(f"刷新访问令牌: {refresh_token}")
        auth_token = await self._auth_domain_svc.refresh_access_token(refresh_token)
        return AuthTokenResponse(
            access_token=auth_token.access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=auth_token.expires_in,
        )

    async def create_token_response(self, user: User) -> AuthTokenResponse:
        """创建令牌响应"""
        access_token = self._auth_domain_svc.create_access_token(user)
        refresh_token = self._auth_domain_svc.create_refresh_token(user)

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.security.jwt_access_token_expire_minutes * 60,
        )


