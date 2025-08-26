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

from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.transaction_manager import transactional

from user.application.schemas import AuthTokenResponse
from user.domain.models import User
from user.domain.repositories import IUserRepository
from user.domain.services.auth_domain_service import AuthDomainService
from user.domain.services.user_domain_service import UserDomainService


class AuthService:
    """认证服务"""

    def __init__(
        self, 
        auth_domain_service: AuthDomainService, 
        user_domain_service: UserDomainService,
        user_repository: IUserRepository
    ):
        self._auth_domain_service = auth_domain_service
        self._user_domain_service = user_domain_service
        self._user_repository = user_repository

    @transactional()
    async def authenticate_user(
        self,
        login_id: str,
        password: str,
    ) -> tuple[User, AuthTokenResponse]:
        # 1. Application Service根据登录ID查找用户
        user = None
        if "@" in login_id:
            user = await self._user_repository.find_by_email(login_id)
        else:
            user = await self._user_repository.find_by_username(login_id)
        
        # 2. 使用Domain Service认证用户凭证
        auth_user = self._user_domain_service.authenticate_user_credentials(user, password)
    
        access_token = self._auth_domain_service.create_access_token(auth_user)
        refresh_token = self._auth_domain_service.create_refresh_token(auth_user)

        # 3. Application Service保存用户（更新最后登录时间）
        await self._user_repository.save(auth_user)

        return auth_user, AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=self._auth_domain_service._token_type,
            expires_in=self._auth_domain_service._access_token_expire_minutes,
        )


    @transactional()
    async def refresh_access_token(
        self,
        refresh_token: str,
        *,
        session: AsyncSession,
    ) -> AuthTokenResponse:
        """刷新访问令牌 - 只读操作"""
        logger.info(f"刷新访问令牌: {refresh_token}")
        
        # 1. 使用Domain Service验证刷新令牌并返回用户ID
        user_id: UUID = self._auth_domain_service.validate_refresh_token(refresh_token)
        
        # 2. Application Service查询Repository获取用户
        user = await self._user_repository.find_by_id(user_id)
        
        # 3. 使用Domain Service验证用户是否可以刷新令牌
        self._auth_domain_service.validate_user_for_token_refresh(user)
        
        # 4. 使用Domain Service创建令牌响应
        access_token = self._auth_domain_service.create_access_token(user)

        await self._user_repository.save(user)

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=self._auth_domain_service._token_type,
            expires_in=self._auth_domain_service._access_token_expire_minutes,
        )

