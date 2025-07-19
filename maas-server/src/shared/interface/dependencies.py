"""共享接口层 - 依赖注入容器"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.database import get_db_session
from user.application.auth_service import AuthService, EmailService
from user.application.services import (
    ApiKeyService,
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

    def __init__(self):
        self._password_service = PasswordHashService()
        self._email_verification_service = EmailVerificationService()
        self._api_key_service = ApiKeyService()
        self._email_service = EmailService()

    async def get_user_repository(self, db: AsyncSession) -> UserRepository:
        """获取用户仓储"""
        return SQLAlchemyUserRepository(db)

    async def get_role_repository(self, db: AsyncSession) -> RoleRepository:
        """获取角色仓储"""
        return SQLAlchemyRoleRepository(db)

    async def get_user_application_service(self, db: AsyncSession) -> UserApplicationService:
        """获取用户应用服务"""
        user_repo = await self.get_user_repository(db)
        role_repo = await self.get_role_repository(db)

        return UserApplicationService(
            user_repository=user_repo,
            role_repository=role_repo,
            password_service=self._password_service,
            email_service=self._email_verification_service,
            api_key_service=self._api_key_service,
        )

    async def get_auth_service(self, db: AsyncSession) -> AuthService:
        """获取认证服务"""
        user_repo = await self.get_user_repository(db)
        return AuthService(user_repo)

    def get_email_service(self) -> EmailService:
        """获取邮件服务"""
        return self._email_service


# 全局容器实例
container = DependencyContainer()


# FastAPI依赖
async def get_user_repository(
    db: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[UserRepository, None]:
    """获取用户仓储依赖"""
    yield await container.get_user_repository(db)


async def get_role_repository(
    db: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[RoleRepository, None]:
    """获取角色仓储依赖"""
    yield await container.get_role_repository(db)


async def get_user_application_service(
    db: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[UserApplicationService, None]:
    """获取用户应用服务依赖"""
    yield await container.get_user_application_service(db)


async def get_auth_service(
    db: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[AuthService, None]:
    """获取认证服务依赖"""
    yield await container.get_auth_service(db)


def get_email_service() -> EmailService:
    """获取邮件服务依赖"""
    return container.get_email_service()
