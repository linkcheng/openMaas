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

"""用户模块数据初始化器"""

from typing import Any

from shared.infrastructure.logging_service import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.initializer import DataInitializer
from user.domain.models import (
    RoleType,
    User,
    UserStatus,
)
from user.domain.repositories import (
    IPermissionRepository,
    IRoleRepository,
    IUserRepository,
)
from user.domain.services.permission_calculation_service import (
    PermissionCalculationService,
)
from user.domain.services.permission_domain_service import PermissionDomainService
from user.domain.services.role_domain_service import RoleDomainService
from user.domain.services.user_domain_service import UserDomainService
from user.domain.services.user_lifecycle_service import UserLifecycleService
from user.domain.services.user_validation_service import UserValidationService
from user.infrastructure.password_service import PasswordHashService
from user.infrastructure.repositories import (
    PermissionRepository,
    RoleRepository,
    UserRepository,
)

logger = get_logger()


class UserDataInitializer(DataInitializer):
    """用户模块数据初始化器"""

    def __init__(self) -> None:
        self._permissions_data = self._get_initial_permissions_data()
        self._roles_data = self._get_initial_roles_data()
        self._admin_data = self._get_initial_admin_data()

    def get_module_name(self) -> str:
        """获取模块名称"""
        return "user"

    def get_dependencies(self) -> list[str]:
        """获取依赖的模块列表"""
        return []  # 用户模块无依赖

    def _get_initial_permissions_data(self) -> list[dict[str, Any]]:
        """获取初始权限数据"""
        return [

            # 系统管理权限
            {
                "name": "system.system.view",
                "display_name": "查看系统",
                "description": "查看系统信息",
            },
            {
                "name": "system.system.update",
                "display_name": "更新系统",
                "description": "更新系统配置",
            },
            {
                "name": "system.system.monitor",
                "display_name": "系统监控",
                "description": "监控系统状态",
            },
            # 用户管理权限
            {
                "name": "system.users.view",
                "display_name": "查看用户",
                "description": "查看用户列表和详情",
            },
            {
                "name": "system.users.create",
                "display_name": "创建用户",
                "description": "创建新用户账户",
            },
            {
                "name": "system.users.update",
                "display_name": "更新用户",
                "description": "更新用户信息",
            },
            {
                "name": "system.users.delete",
                "display_name": "删除用户",
                "description": "删除用户账户",
            },
            # 角色管理权限
            {
                "name": "system.roles.view",
                "display_name": "查看角色",
                "description": "查看角色列表和详情",
            },
            {
                "name": "system.roles.create",
                "display_name": "创建角色",
                "description": "创建新角色",
            },
            {
                "name": "system.roles.update",
                "display_name": "更新角色",
                "description": "更新角色信息",
            },
            {
                "name": "system.roles.delete",
                "display_name": "删除角色",
                "description": "删除角色",
            },
            # 权限管理权限
            {
                "name": "system.permissions.view",
                "display_name": "查看权限",
                "description": "查看权限列表和详情",
            },
            {
                "name": "system.permissions.create",
                "display_name": "创建权限",
                "description": "创建新权限",
            },
            {
                "name": "system.permissions.update",
                "display_name": "更新权限",
                "description": "更新权限信息",
            },
            {
                "name": "system.permissions.delete",
                "display_name": "删除权限",
                "description": "删除权限",
            },
            # 审计日志管理权限
            {
                "name": "system.audit.view",
                "display_name": "查看审计日志",
                "description": "查看审计日志列表和详情",
            },
            {
                "name": "system.audit.create",
                "display_name": "创建审计日志",
                "description": "创建新审计日志",
            },
            {
                "name": "system.audit.update",
                "display_name": "更新审计日志",
                "description": "更新审计日志信息",
                "module": "system",
            },
            {
                "name": "system.audit.delete",
                "display_name": "删除审计日志",
                "description": "删除审计日志",
            },
            # 用户管理权限
            {
                "name": "user.users.view",
                "display_name": "查看用户",
                "description": "查看用户详情",
            },
            {
                "name": "user.users.update",
                "display_name": "更新用户",
                "description": "更新用户信息",
            },
            # 模型管理权限
            {
                "name": "model.models.view",
                "display_name": "查看模型",
                "description": "查看模型列表和详情",
            },
            {
                "name": "model.models.create",
                "display_name": "创建模型",
                "description": "创建新模型",
            },
            {
                "name": "model.models.update",
                "display_name": "更新模型",
                "description": "更新模型信息",
            },
            {
                "name": "model.models.delete",
                "display_name": "删除模型",
                "description": "删除模型",
            },
        ]

    def _get_initial_roles_data(self) -> list[dict[str, Any]]:
        """获取初始角色数据"""
        return [
            {
                "name": RoleType.ADMIN.value,
                "display_name": "系统管理员",
                "description": "系统管理员，拥有所有权限",
                "role_type": RoleType.ADMIN,
                "is_system_role": True,
                "permissions": [
                    "system.system.view", "system.system.update", "system.system.monitor",
                    "system.users.view", "system.users.create", "system.users.update", "system.users.delete",
                    "system.roles.view", "system.roles.create", "system.roles.update", "system.roles.delete",
                    "system.permissions.view", "system.permissions.create", "system.permissions.update", "system.permissions.delete",
                    "system.audit.view", "system.audit.create", "system.audit.update", "system.audit.delete",
                    "user.users.view", "user.users.update",
                    "model.models.view", "model.models.create", "model.models.update", "model.models.delete"
                ]
            },
            {
                "name": RoleType.DEVELOPER.value,
                "display_name": "开发人员",
                "description": "开发人员，拥有模型管理权限",
                "role_type": RoleType.DEVELOPER,
                "is_system_role": False,
                "permissions": [
                    "user.users.view", "user.users.update",
                    "model.models.view", "model.models.create", "model.models.update", "model.models.delete",
                    "system.system.view"
                ]
            },
            {
                "name": RoleType.USER.value,
                "display_name": "普通用户",
                "description": "普通用户，只能使用已部署的服务",
                "role_type": RoleType.USER,
                "is_system_role": False,
                "permissions": [
                    "user.users.view", "user.users.update",
                    "model.models.view"
                ]
            }
        ]

    def _get_initial_admin_data(self) -> dict[str, Any]:
        """获取初始管理员用户数据"""

        # 动态生成密码哈希
        admin_password = "admin123"  # 默认管理员密码
        password_hash = PasswordHashService.hash_password(admin_password)

        return {
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": password_hash,
            "first_name": "系统",
            "last_name": "管理员",
            "organization": "MaaS平台",
            "bio": "系统默认管理员账户",
            "status": UserStatus.ACTIVE.value,
            "email_verified": True,
        }

    async def initialize(self, session: AsyncSession) -> bool:
        """初始化用户模块数据"""
        try:
            # 创建仓储实例
            permission_repository = PermissionRepository(session)
            role_repository = RoleRepository(session)
            user_repository = UserRepository(session)
            password_service = PasswordHashService()
            validation_service = UserValidationService()
            lifecycle_service = UserLifecycleService()
            permission_calculation_service = PermissionCalculationService()

            # 创建领域服务实例
            permission_domain_service = PermissionDomainService()
            role_domain_service = RoleDomainService()
            user_domain_service = UserDomainService(
                password_service=password_service,
                validation_service=validation_service,
                lifecycle_service=lifecycle_service,
                permission_calculation_service=permission_calculation_service
            )

            # 初始化权限
            await self._initialize_permissions(permission_domain_service, permission_repository)

            # 初始化角色
            await self._initialize_roles(role_domain_service, role_repository, permission_repository)

            # 初始化管理员用户
            _ = await self._initialize_admin_user(user_domain_service, role_repository, user_repository)

            return True

        except Exception as e:
            logger.error(f"用户模块数据初始化失败: {e}")
            await session.rollback()
            return False

    async def _initialize_permissions(self, 
        permission_domain_service: PermissionDomainService,
        permission_repository: IPermissionRepository
    ) -> None:
        """初始化权限数据"""
        logger.info("初始化权限数据...")

        for permission_data in self._permissions_data:
            try:
                # 检查权限是否已存在
                existing_permissions = await permission_repository.find_by_names([permission_data["name"]])

                if existing_permissions:
                    logger.info(f"权限已存在，跳过: {permission_data['name']}")
                    continue

                """
                    "name": "user.users.view",
                    "display_name": "查看用户",
                    "description": "查看用户列表和详情",
                    "module": "user",
                    "resource": "users",
                    "action": "view"
                """
                # 创建新权限
                permission = permission_domain_service.create_permission_entity(
                    name=permission_data["name"],
                    display_name=permission_data["display_name"],
                    description=permission_data["description"],
                )
                _ = await permission_repository.save(permission)
                await permission_repository.commit()
                logger.info(f"创建权限: {permission.name.value}")

            except Exception as e:
                logger.warning(f"创建权限失败 {permission_data['name']}: {e}")

    async def _initialize_roles(
        self,
        role_domain_service: RoleDomainService,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository
    ) -> None:
        """初始化角色数据"""
        logger.info("初始化角色数据...")

        for role_data in self._roles_data:
            try:
                # 检查角色是否已存在
                existing_role = await role_repository.find_by_name(role_data["name"])

                if existing_role:
                    logger.info(f"角色已存在，跳过: {role_data['name']}")
                    continue

                # 获取权限列表
                permission_names = role_data["permissions"]
                permissions = await permission_repository.find_by_names(permission_names)
                permission_ids = [perm.id for perm in permissions]

                # 创建新角色
                role = role_domain_service.create_role_entity(
                    name=role_data["name"],
                    display_name=role_data["display_name"],
                    description=role_data["description"],
                    permissions=permissions,
                    role_type=role_data["role_type"],
                    is_system_role=role_data["is_system_role"],
                )
                _ = await role_repository.save(role)
                await role_repository.commit()
                logger.info(f"创建角色: {role.name}")

            except Exception as e:
                logger.warning(f"创建角色失败 {role_data['name']}: {e}")

    async def _initialize_admin_user(self, user_domain_service: UserDomainService, role_repository: IRoleRepository, user_repository: IUserRepository) -> User | None:
        """初始化管理员用户"""
        logger.info("初始化管理员用户...")

        admin_data = self._admin_data

        try:
            # 检查管理员用户是否已存在
            existing_user = await user_repository.find_by_username(admin_data["username"])

            if existing_user:
                logger.info(f"管理员用户已存在: {admin_data['username']}")
                return existing_user

            role = await role_repository.find_by_name(RoleType.ADMIN.value)

            # 创建新的管理员用户
            admin_user = user_domain_service.create_user_entity(
                username=admin_data["username"],
                email=admin_data["email"],
                password_hash=admin_data["password_hash"],
                first_name=admin_data["first_name"],
                last_name=admin_data["last_name"],
                organization=admin_data["organization"],
                role=role
            )
            logger.info(f"创建管理员用户: {admin_data['username']}")
            return admin_user

        except Exception as e:
            logger.error(f"创建管理员用户失败: {e}")
            return None
