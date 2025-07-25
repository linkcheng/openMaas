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

"""共享接口层 - 依赖注入容器"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from audit.application.services import AuditLogService
from audit.domain.repositories import AuditLogRepository
from audit.infrastructure.repositories import SQLAlchemyAuditLogRepository
from shared.infrastructure.database import get_db_session
from user.application.auth_service import AuthService
from user.application.services import (
    EmailVerificationService,
    PasswordHashService,
    UserApplicationService,
)
from user.domain.repositories import RoleRepository, UserRepository
from user.infrastructure.repositories import (
    SQLAlchemyRoleRepository,
    SQLAlchemyUserRepository,
)


class DependencyContainer:
    """依赖注入容器"""

    def __init__(self) -> None:
        self._password_service = PasswordHashService()
        self._email_verification_service = EmailVerificationService()

    async def get_user_repository(self, db: AsyncSession) -> UserRepository:
        """获取用户仓储"""
        return SQLAlchemyUserRepository(db)

    async def get_role_repository(self, db: AsyncSession) -> RoleRepository:
        """获取角色仓储"""
        return SQLAlchemyRoleRepository(db)

    async def get_user_application_service(
        self, db: AsyncSession
    ) -> UserApplicationService:
        """获取用户应用服务"""
        user_repo = await self.get_user_repository(db)
        role_repo = await self.get_role_repository(db)

        return UserApplicationService(
            user_repository=user_repo,
            role_repository=role_repo,
            password_service=self._password_service,
            email_service=self._email_verification_service,
        )

    async def get_auth_service(self, db: AsyncSession) -> AuthService:
        """获取认证服务"""
        user_repo = await self.get_user_repository(db)
        return AuthService(user_repo)

    async def get_audit_log_repository(self, db: AsyncSession) -> AuditLogRepository:
        """获取审计日志仓储"""
        return SQLAlchemyAuditLogRepository(db)

    async def get_audit_log_service(self, db: AsyncSession) -> AuditLogService:
        """获取审计日志应用服务"""
        audit_repo = await self.get_audit_log_repository(db)
        return AuditLogService(audit_repo)


# 全局容器实例
container = DependencyContainer()


# FastAPI依赖
async def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[UserRepository, None]:
    """获取用户仓储依赖"""
    yield await container.get_user_repository(db)


async def get_role_repository(
    db: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[RoleRepository, None]:
    """获取角色仓储依赖"""
    yield await container.get_role_repository(db)


async def get_user_application_service(
    db: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[UserApplicationService, None]:
    """获取用户应用服务依赖"""
    yield await container.get_user_application_service(db)


async def get_auth_service(
    db: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AuthService, None]:
    """获取认证服务依赖"""
    yield await container.get_auth_service(db)


async def get_audit_log_repository(
    db: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AuditLogRepository, None]:
    """获取审计日志仓储依赖"""
    yield await container.get_audit_log_repository(db)


async def get_audit_log_service(
    db: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AuditLogService, None]:
    """获取审计日志应用服务依赖"""
    yield await container.get_audit_log_service(db)

