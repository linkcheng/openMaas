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

"""用户领域服务 - 核心业务逻辑"""

from datetime import datetime
from typing import Any
from uuid import UUID

from loguru import logger

from shared.domain.base import DomainException
from user.domain.models import (
    InvalidCredentialsException,
    User,
    UserAlreadyExistsException,
    UserProfile,
    UserStatus,
)
from user.domain.repositories import IRoleRepository, IUserRepository
from user.domain.services.user_validation_service import UserValidationService
from user.infrastructure.password_service import PasswordHashService
from user.domain.services.user_lifecycle_service import UserLifecycleService
from user.domain.services.permission_calculation_service import PermissionCalculationService

class UserDomainService:
    """用户领域服务，实现用户相关的核心业务逻辑"""

    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
        password_service: PasswordHashService,
        validation_service: UserValidationService,
        lifecycle_service: UserLifecycleService,
        permission_calculation_service: PermissionCalculationService,
    ):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._password_service = password_service
        self._validation_service = validation_service
        self._lifecycle_service = lifecycle_service 
        self._permission_calculation_service = permission_calculation_service

    async def validate_user_creation(
        self, username: str, email: str, password: str | None = None
    ) -> None:
        """验证用户创建的业务规则"""
        # 数据格式验证
        self._validation_service.validate_username(username)
        self._validation_service.validate_email(email)
        if password:
            self._validation_service.validate_password(password)

        # 唯一性验证
        existing_user = await self._user_repository.find_by_email(email)
        if existing_user:
            raise UserAlreadyExistsException(f"邮箱 {email} 已被使用")

        existing_user = await self._user_repository.find_by_username(username)
        if existing_user:
            raise UserAlreadyExistsException(f"用户名 {username} 已被使用")

    async def create_user_with_role(
        self,
        username: str,
        email: str,
        password_hash: str,
        first_name: str | None = None,
        last_name: str | None = None,
        organization: str | None = None,
        default_role_type: str | None = None,
    ) -> User:
        """创建用户并分配默认角色"""
        # 验证用户创建规则
        await self.validate_user_creation(username, email)

        # 验证档案信息
        self._validation_service.validate_user_profile(
            first_name, last_name, organization, None
        )

        # 创建用户
        user = User.create(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            organization=organization,
        )

        # 分配默认角色
        if not default_role_type:
            default_role = await self._role_repository.get_default_role()
        else:
            default_role = await self._role_repository.find_by_name(default_role_type)

        user.add_role(default_role)
        await self._user_repository.save(user)
        logger.info(f"用户创建成功: {user.username} ({user.email.value})")
        return user

    async def authenticate_user(self, login_id: str, password: str) -> User:
        """认证用户"""
        # 根据登录ID查找用户(可以是用户名或邮箱)
        user = None
        if "@" in login_id:
            user = await self._user_repository.find_by_email(login_id)
        else:
            user = await self._user_repository.find_by_username(login_id)

        if not user:
            raise InvalidCredentialsException("用户名或密码错误")

        # 验证密码
        if not self._password_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsException("用户名或密码错误")

        # 检查用户状态
        if user.status != UserStatus.ACTIVE:
            raise InvalidCredentialsException("用户账户已被禁用")

        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()

        # 保存用户
        await self._user_repository.update(user)

        logger.info(f"用户 {user.username} 登录成功")
        return user

    async def change_user_password(
        self, user_id: UUID, current_password: str, new_password_hash: str
    ) -> User:
        """修改用户密码"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        # 验证旧密码
        if not self._password_service.verify_password(current_password, user.password_hash):
            raise InvalidCredentialsException("当前密码不正确")

        # 更新密码并增加密钥版本
        user.password_hash = new_password_hash
        user.increment_key_version()

        logger.info(f"用户 {user.username} 密码修改成功")
        return user

    async def update_user_profile(
        self,
        user_id: UUID,
        first_name: str | None = None,
        last_name: str | None = None,
        avatar_url: str | None = None,
        organization: str | None = None,
        bio: str | None = None,
    ) -> User:
        """更新用户档案"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        # 验证档案信息
        self._validation_service.validate_user_profile(
            first_name, last_name, organization, bio
        )

        # 更新用户档案
        profile = UserProfile(
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
            organization=organization,
            bio=bio,
        )
        user.update_profile(profile)

        logger.info(f"用户 {user.username} 档案已更新")
        return user

    async def change_user_roles(
        self, user_id: UUID, new_role_ids: list[UUID], operator_id: UUID
    ) -> User:
        """更改用户角色并使token失效"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        # 获取新角色
        new_roles = []
        for role_id in new_role_ids:
            role = await self._role_repository.find_by_id(role_id)
            if role:
                new_roles.append(role)

        # 清除现有角色
        for existing_role in user.roles:
            user.remove_role(existing_role)

        # 添加新角色
        for new_role in new_roles:
            user.add_role(new_role)

        # 使所有现有token失效
        user.increment_key_version()

        logger.info(f"用户 {user.username} 角色已更新，token已失效")
        return user

    async def suspend_user(
        self, user_id: UUID, reason: str, suspended_by: UUID
    ) -> User:
        """暂停用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        if user.status == UserStatus.SUSPENDED:
            raise DomainException("用户已处于暂停状态")

        # 使用用户生命周期服务执行暂停
        operation_result = self._lifecycle_service.execute_user_suspension(
            user, reason, suspended_by
        )

        logger.info(f"用户暂停成功: {operation_result}")
        return user

    async def activate_user(self, user_id: UUID) -> User:
        """激活用户"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        if user.status == UserStatus.ACTIVE:
            raise DomainException("用户已处于激活状态")

        # 使用用户生命周期服务执行激活
        operation_result = self._lifecycle_service.execute_user_activation(user)

        logger.info(f"用户激活成功: {operation_result}")
        return user

    async def logout_user(self, user_id: UUID) -> User:
        """用户登出,增加key_version使所有token失效"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        # 增加密钥版本以使所有现有token失效
        user.increment_key_version()

        logger.info(f"用户 {user.username} 已登出,token已失效")
        return user

    async def invalidate_user_tokens(
        self, user_id: UUID, reason: str = "权限变更"
    ) -> User:
        """使用户所有token失效"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        # 增加密钥版本以使所有现有token失效
        user.increment_key_version()

        logger.info(f"用户 {user.username} 的所有token已失效，原因: {reason}")
        return user

    async def get_user_permissions(self, user_id: UUID) -> dict[str, Any]:
        """获取用户完整权限"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        # 使用permission service计算有效权限
        effective_permissions = self._permission_calculation_service.calculate_effective_permissions(user)
        permission_matrix = self._permission_calculation_service.get_permission_matrix(user)

        # 构建权限列表
        permission_list = [perm.name.value for perm in effective_permissions]

        # 按模块分组权限
        permissions_by_module = {}
        for perm in effective_permissions:
            module = perm.module or "default"
            if module not in permissions_by_module:
                permissions_by_module[module] = []

            permissions_by_module[module].append(
                {
                    "id": str(perm.id),
                    "name": perm.name.value,
                    "display_name": perm.display_name,
                    "description": perm.description,
                    "resource": perm.resource,
                    "action": perm.action,
                }
            )

        # 获取角色信息
        roles = []
        for role in user.roles:
            role_permissions = []
            for perm in role.permissions:
                role_permissions.append(perm.name.value)

            roles.append(
                {
                    "id": str(role.id),
                    "name": role.name,
                    "display_name": role.display_name,
                    "description": role.description,
                    "permissions": role_permissions,
                    "is_system_role": role.is_system_role,
                }
            )

        return {
            "user_id": str(user_id),
            "username": user.username,
            "is_super_admin": user.is_super_admin(),
            "permissions": permission_list,
            "permissions_by_module": permissions_by_module,
            "permission_matrix": permission_matrix,
            "roles": roles,
            "total_permissions": len(permission_list),
        }

    async def check_user_permission(
        self, user_id: UUID, permission_name: str
    ) -> dict[str, Any]:
        """验证用户权限"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        has_permission = user.has_permission(permission_name)

        # 查找授予权限的角色
        granted_by_roles = []
        if has_permission and not user.is_super_admin():
            for role in user.roles:
                if role.has_permission(permission_name):
                    granted_by_roles.append(role.name)

        return {
            "user_id": str(user_id),
            "username": user.username,
            "permission": permission_name,
            "has_permission": has_permission,
            "is_super_admin": user.is_super_admin(),
            "granted_by_roles": granted_by_roles,
        }

    async def check_user_permission_by_parts(
        self, user_id: UUID, resource: str, action: str, module: str | None = None
    ) -> dict[str, Any]:
        """通过资源和操作验证用户权限"""
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise DomainException(f"用户 {user_id} 不存在")

        has_permission = user.has_permission_by_parts(resource, action, module)

        # 构建权限名称用于显示
        if module:
            permission_name = f"{module}.{resource}.{action}"
        else:
            permission_name = f"*.{resource}.{action}"

        # 查找授予权限的角色
        granted_by_roles = []
        if has_permission and not user.is_super_admin():
            for role in user.roles:
                if role.has_permission_by_parts(resource, action, module):
                    granted_by_roles.append(role.name)

        return {
            "user_id": str(user_id),
            "username": user.username,
            "permission": permission_name,
            "resource": resource,
            "action": action,
            "module": module,
            "has_permission": has_permission,
            "is_super_admin": user.is_super_admin(),
            "granted_by_roles": granted_by_roles,
        }
