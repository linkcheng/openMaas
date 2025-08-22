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

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.database import get_db_session
from user.application.audit_service import AuditApplicationService
from user.application.auth_service import AuthService
from user.application.permission_service import PermissionApplicationService
from user.application.role_service import RoleApplicationService
from user.application.user_service import UserApplicationService
from user.domain.repositories import (
    IPermissionRepository,
    IRoleRepository,
    IUserRepository,
    IAuditLogRepository,
)
from user.domain.services.audit_domain_service import AuditDomainService
from user.domain.services.auth_domain_service import AuthDomainService
from user.domain.services.permission_domain_service import PermissionDomainService
from user.domain.services.role_domain_service import RoleDomainService
from user.domain.services.user_domain_service import UserDomainService
from user.domain.services.user_validation_service import UserValidationService
from user.domain.services.user_lifecycle_service import UserLifecycleService
from user.domain.services.permission_calculation_service import PermissionCalculationService
from user.infrastructure.email_service import EmailVerificationService
from user.infrastructure.password_service import PasswordHashService
from user.infrastructure.repositories import (
    AuditLogRepository,
    PermissionRepository,
    RoleRepository,
    UserRepository,
)


# Repository Dependencies
async def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[IUserRepository, None]:
    """获取用户仓储"""
    yield UserRepository(session=db)

async def get_permission_repository(db: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[IPermissionRepository, None]:
    """获取权限仓储"""
    yield PermissionRepository(session=db)

async def get_role_repository(db: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[IRoleRepository, None]:
    """获取角色仓储"""
    yield RoleRepository(session=db)

async def get_audit_repository(db: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[IAuditLogRepository, None]:
    """获取审计仓储"""
    yield AuditLogRepository(session=db)


# Infrastructure Service Dependencies
async def get_password_service() -> PasswordHashService:
    return PasswordHashService()

async def get_email_verification_service() -> EmailVerificationService:
    return EmailVerificationService()

async def get_user_validation_service() -> UserValidationService:
    return UserValidationService()

async def get_user_lifecycle_service() -> UserLifecycleService:
    return UserLifecycleService()

async def get_permission_calculation_service() -> PermissionCalculationService:
    return PermissionCalculationService()

# Domain Service Dependencies
async def get_user_domain_service(
    user_repo: IUserRepository = Depends(get_user_repository),
    role_repo: IRoleRepository = Depends(get_role_repository),
    password_service: PasswordHashService = Depends(get_password_service),
    validation_service: UserValidationService = Depends(get_user_validation_service),
    lifecycle_service: UserLifecycleService = Depends(get_user_lifecycle_service),
    permission_calculation_service: PermissionCalculationService = Depends(get_permission_calculation_service),
) -> AsyncGenerator[UserDomainService, None]:
    """获取用户领域服务"""
    yield UserDomainService(
        user_repository=user_repo,
        role_repository=role_repo,
        password_service=password_service,
        validation_service=validation_service,
        lifecycle_service=lifecycle_service,
        permission_calculation_service=permission_calculation_service,
    )

async def get_role_domain_service(
    role_repo: IRoleRepository = Depends(get_role_repository),
    permission_repo: IPermissionRepository = Depends(get_permission_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
    validation_service: UserValidationService = Depends(get_user_validation_service),
) -> AsyncGenerator[RoleDomainService, None]:
    """获取角色领域服务"""
    yield RoleDomainService(
        role_repository=role_repo,
        permission_repository=permission_repo,
        user_repository=user_repo,
        validation_service=validation_service,
    )

async def get_permission_domain_service(
    permission_repo: IPermissionRepository = Depends(get_permission_repository),
    role_repo: IRoleRepository = Depends(get_role_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
    validation_service: UserValidationService = Depends(get_user_validation_service),
) -> AsyncGenerator[PermissionDomainService, None]:
    """获取权限领域服务"""
    yield PermissionDomainService(
        permission_repository=permission_repo,
        role_repository=role_repo,
        user_repository=user_repo,
        validation_service=validation_service,
    )

async def get_auth_domain_service(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> AsyncGenerator[AuthDomainService, None]:
    """获取认证领域服务"""
    yield AuthDomainService(user_repo)

async def get_audit_domain_service(
    audit_repo: IAuditLogRepository = Depends(get_audit_repository),
) -> AsyncGenerator[AuditDomainService, None]:
    """获取审计领域服务"""
    yield AuditDomainService(audit_repo)


# Application Service Dependencies
async def get_user_application_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    user_domain_service: UserDomainService = Depends(get_user_domain_service),
) -> AsyncGenerator[UserApplicationService, None]:
    """获取用户应用服务"""
    yield UserApplicationService(
        user_repository=user_repository,
        user_domain_service=user_domain_service,
    )

async def get_role_application_service(
    role_repository: IRoleRepository = Depends(get_role_repository),
    role_domain_service: RoleDomainService = Depends(get_role_domain_service),
) -> AsyncGenerator[RoleApplicationService, None]:
    """获取角色应用服务"""
    yield RoleApplicationService(
        role_repository=role_repository,
        role_domain_service=role_domain_service,
    )

async def get_permission_application_service(
    permission_domain_service: PermissionDomainService = Depends(get_permission_domain_service),
) -> AsyncGenerator[PermissionApplicationService, None]:
    """获取权限应用服务"""
    yield PermissionApplicationService(
        permission_domain_service=permission_domain_service,
    )

async def get_audit_application_service(
    audit_domain_service: AuditDomainService = Depends(get_audit_domain_service),
) -> AsyncGenerator[AuditApplicationService, None]:
    """获取审计应用服务"""
    yield AuditApplicationService(audit_domain_service=audit_domain_service)

async def get_auth_service(
    auth_domain_svc: AuthDomainService = Depends(get_auth_domain_service),
    user_domain_svc: UserDomainService = Depends(get_user_domain_service),
) -> AsyncGenerator[AuthService, None]:
    """获取认证服务"""
    yield AuthService(auth_domain_svc, user_domain_svc)
