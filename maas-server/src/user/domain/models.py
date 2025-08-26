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

"""用户领域 - 领域模型"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from uuid_extensions import uuid7

from shared.domain.base import (
    AggregateRoot,
    BusinessRuleViolationException,
    DomainEvent,
    DomainException,
    EmailAddress,
    Entity,
    ValueObject,
)


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class RoleType(str, Enum):
    """角色类型"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"



@dataclass(frozen=True)
class UserProfile(ValueObject):
    """用户档案值对象"""
    first_name: str
    last_name: str
    avatar_url: str | None = None
    organization: str | None = None
    bio: str | None = None

    def _validate(self) -> None:
        if not self.first_name or not self.first_name.strip():
            raise ValueError("名字不能为空")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("姓氏不能为空")
        if len(self.first_name) > 50:
            raise ValueError("名字长度不能超过50个字符")
        if len(self.last_name) > 50:
            raise ValueError("姓氏长度不能超过50个字符")

    @property
    def full_name(self) -> str:
        """全名"""
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True)
class AuthToken(ValueObject):
    """认证令牌"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


@dataclass(frozen=True)
class PermissionName(ValueObject):
    """权限名称值对象"""
    value: str

    def _validate(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("权限名称不能为空")

        # 验证权限命名规范: {module}.{resource}.{action}
        parts = self.value.split(".")
        if len(parts) != 3:
            raise ValueError("权限名称必须遵循 {module}.{resource}.{action} 格式")

        module, resource, action = parts
        if not all(part.strip() for part in [module, resource, action]):
            raise ValueError("权限名称的各部分不能为空")

        # 验证字符规范
        import re
        pattern = r"^[a-z][a-z0-9_]*$"
        for part in [module, resource]:
            if not re.match(pattern, part) and part != "*":
                raise ValueError(f"权限名称部分 '{part}' 只能包含小写字母、数字和下划线，且必须以字母开头")

        # action 可以是 * 或符合规范的字符串
        if action != "*" and not re.match(pattern, action):
            raise ValueError(f"权限操作 '{action}' 只能包含小写字母、数字和下划线，且必须以字母开头，或者是通配符 '*'")

    @property
    def module(self) -> str:
        """获取模块名"""
        return self.value.split(".")[0]

    @property
    def resource(self) -> str:
        """获取资源名"""
        return self.value.split(".")[1]

    @property
    def action(self) -> str:
        """获取操作名"""
        return self.value.split(".")[2]

    def matches(self, other: "PermissionName") -> bool:
        """检查权限是否匹配（支持通配符）"""
        if self.value == other.value:
            return True

        # 检查通配符匹配
        self_parts = self.value.split(".")
        other_parts = other.value.split(".")

        for i, (self_part, other_part) in enumerate(zip(self_parts, other_parts, strict=False)):
            if self_part == "*" or other_part == "*":
                # 如果是最后一部分的通配符，匹配成功
                if i == 2:  # action 部分
                    return True
                # 如果是 resource 部分的通配符，需要检查后续
                continue
            elif self_part != other_part:
                return False

        return True


class Permission(Entity):
    """权限实体"""

    def __init__(
        self,
        id: UUID,
        name: PermissionName,
        display_name: str,
        description: str,
        module: str | None = None
    ):
        super().__init__(id)
        self.name = name
        self.display_name = display_name
        self.description = description
        # module 可以从 name 中提取，但也可以单独设置
        self.module = module or name.module

    @property
    def resource(self) -> str:
        """资源名"""
        return self.name.resource

    @property
    def action(self) -> str:
        """操作名"""
        return self.name.action

    def matches(self, required_permission: "Permission") -> bool:
        """检查是否匹配所需权限（支持通配符）"""
        return self.name.matches(required_permission.name)

    def __str__(self) -> str:
        return self.name.value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Permission):
            return False
        return self.name.value == other.name.value

    def __hash__(self) -> int:
        return hash(self.name.value)


class Role(Entity):
    """角色实体"""

    def __init__(
        self,
        id: UUID,
        name: str,
        display_name: str,
        description: str,
        permissions: list[Permission] | None = None,
        is_system_role: bool = False,
        role_type: RoleType = RoleType.USER
    ):
        super().__init__(id)
        self.name = name
        self.display_name = display_name
        self.description = description
        self._permissions = permissions.copy() if permissions else []
        self.is_system_role = is_system_role
        self.role_type = role_type

    @property
    def permissions(self) -> list[Permission]:
        """权限列表"""
        return self._permissions.copy()

    def add_permission(self, permission: Permission) -> None:
        """添加权限"""
        if self.is_system_role:
            raise BusinessRuleViolationException("不能修改系统角色的权限")

        if permission not in self._permissions:
            self._permissions.append(permission)

    def remove_permission(self, permission: Permission) -> None:
        """移除权限"""
        if self.is_system_role:
            raise BusinessRuleViolationException("不能修改系统角色的权限")

        if permission in self._permissions:
            self._permissions.remove(permission)

    def add_permissions(self, permissions: list[Permission]) -> None:
        """批量添加权限"""
        if self.is_system_role:
            raise BusinessRuleViolationException("不能修改系统角色的权限")

        for permission in permissions:
            if permission not in self._permissions:
                self._permissions.append(permission)

    def remove_permissions(self, permissions: list[Permission]) -> None:
        """批量移除权限"""
        if self.is_system_role:
            raise BusinessRuleViolationException("不能修改系统角色的权限")

        for permission in permissions:
            if permission in self._permissions:
                self._permissions.remove(permission)

    def set_permissions(self, permissions: list[Permission]) -> None:
        """设置权限列表（替换现有权限）"""
        if self.is_system_role:
            raise BusinessRuleViolationException("不能修改系统角色的权限")

        self._permissions = permissions.copy()

    def has_permission(self, permission_name: str) -> bool:
        """检查是否有特定权限"""
        try:
            required_permission_name = PermissionName(permission_name)
        except ValueError:
            return False

        for perm in self._permissions:
            if perm.name.matches(required_permission_name):
                return True
        return False

    def has_permission_by_parts(self, resource: str, action: str, module: str | None = None) -> bool:
        """通过资源和操作检查权限"""
        if module:
            permission_name = f"{module}.{resource}.{action}"
        else:
            # 尝试匹配任何模块
            for perm in self._permissions:
                if perm.resource == resource and perm.action == action:
                    return True
                # 检查通配符权限
                if perm.resource == resource and perm.action == "*":
                    return True
                if perm.resource == "*" and perm.action == "*":
                    return True
            return False

        return self.has_permission(permission_name)

    def merge_permissions(self, other_role: "Role") -> list[Permission]:
        """合并另一个角色的权限（返回合并后的权限列表，不修改当前角色）"""
        merged_permissions = self._permissions.copy()

        for permission in other_role.permissions:
            if permission not in merged_permissions:
                merged_permissions.append(permission)

        return merged_permissions

    def can_be_deleted(self) -> bool:
        """检查角色是否可以被删除"""
        return not self.is_system_role

    def __eq__(self, other) -> bool:
        if not isinstance(other, Role):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


# 领域事件
@dataclass
class UserRegisteredEvent(DomainEvent):
    """用户注册事件"""
    user_id: UUID
    email: str
    username: str

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "user.registered"
        self.aggregate_type = "User"


@dataclass
class UserEmailVerifiedEvent(DomainEvent):
    """用户邮箱验证事件"""
    user_id: UUID
    email: str

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "user.email_verified"
        self.aggregate_type = "User"


@dataclass
class UserProfileUpdatedEvent(DomainEvent):
    """用户档案更新事件"""
    user_id: UUID
    old_profile: dict[str, Any]
    new_profile: dict[str, Any]

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "user.profile_updated"
        self.aggregate_type = "User"


# 用户聚合根
class User(AggregateRoot):
    """用户聚合根"""

    def __init__(
        self,
        id: UUID,
        username: str,
        email: EmailAddress,
        password_hash: str,
        profile: UserProfile,
        status: UserStatus = UserStatus.ACTIVE,
        email_verified: bool = False,
        key_version: int = 1,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        last_login_at: datetime | None = None
    ):
        super().__init__(id)
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.profile = profile
        self.status = status
        self.email_verified = email_verified
        self.key_version = key_version
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_login_at = last_login_at
        self._roles: list[Role] = []

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        organization: str | None = None
    ) -> "User":
        """创建新用户"""
        # 验证输入
        if not username or len(username) < 3:
            raise BusinessRuleViolationException("用户名至少需要3个字符")
        if len(username) > 50:
            raise BusinessRuleViolationException("用户名不能超过50个字符")

        # 创建用户
        user_id = uuid7()
        email_addr = EmailAddress(email)
        profile = UserProfile(
            first_name=first_name,
            last_name=last_name,
            organization=organization
        )

        user = cls(
            id=user_id,
            username=username,
            email=email_addr,
            password_hash=password_hash,
            profile=profile,
            email_verified=True  # 新用户默认为邮箱已验证，简化注册流程
        )

        # 添加领域事件
        user.add_domain_event(UserRegisteredEvent(
            event_id=uuid7(),
            occurred_at=datetime.utcnow(),
            event_type="user.registered",
            aggregate_id=user_id,
            aggregate_type="User",
            event_data={
                "user_id": str(user_id),
                "email": email,
                "username": username
            },
            user_id=user_id,
            email=email,
            username=username
        ))

        return user

    def update_profile(self, profile: UserProfile) -> None:
        """更新用户档案"""
        old_profile = {
            "first_name": self.profile.first_name,
            "last_name": self.profile.last_name,
            "organization": self.profile.organization,
            "bio": self.profile.bio
        }

        self.profile = profile
        self.updated_at = datetime.utcnow()

        # 添加领域事件
        self.add_domain_event(UserProfileUpdatedEvent(
            event_id=uuid7(),
            occurred_at=datetime.utcnow(),
            event_type="user.profile_updated",
            aggregate_id=self.id,
            aggregate_type="User",
            event_data={},
            user_id=self.id,
            old_profile=old_profile,
            new_profile={
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "organization": profile.organization,
                "bio": profile.bio
            }
        ))

    def verify_email(self) -> None:
        """验证邮箱"""
        if self.email_verified:
            raise BusinessRuleViolationException("邮箱已经验证过了")

        self.email_verified = True
        self.updated_at = datetime.utcnow()

        # 添加领域事件
        self.add_domain_event(UserEmailVerifiedEvent(
            event_id=uuid7(),
            occurred_at=datetime.utcnow(),
            event_type="user.email_verified",
            aggregate_id=self.id,
            aggregate_type="User",
            event_data={
                "user_id": str(self.id),
                "email": self.email.value
            }
        ))

    def add_role(self, role: Role) -> None:
        """添加角色"""
        if role not in self._roles:
            self._roles.append(role)
            self.updated_at = datetime.utcnow()


    def remove_role(self, role: Role) -> None:
        """移除角色"""
        if role in self._roles:
            self._roles.remove(role)
            self.updated_at = datetime.utcnow()


    def set_roles(self, roles: list[Role]) -> None:
        """设置角色列表（替换现有角色）"""
        self._roles = roles.copy()
        self.updated_at = datetime.utcnow()


    def has_permission(self, permission_name: str) -> bool:
        """检查是否有权限"""
        # 检查是否是超级管理员（拥有通配符权限）
        if self.is_super_admin():
            return True

        return any(role.has_permission(permission_name) for role in self._roles)

    def has_permission_by_parts(self, resource: str, action: str, module: str | None = None) -> bool:
        """通过资源和操作检查权限"""
        # 检查是否是超级管理员
        if self.is_super_admin():
            return True

        return any(role.has_permission_by_parts(resource, action, module) for role in self._roles)

    def is_super_admin(self) -> bool:
        """检查是否是超级管理员"""
        # 检查是否有通配符权限
        for role in self._roles:
            if role.is_system_role:
                return True
            for permission in role.permissions:
                if permission.name.value == "*" or permission.name.value == "*.*.*":
                    return True
        return False

    def get_all_permissions(self) -> list[Permission]:
        """获取用户的所有权限（合并多个角色的权限）"""
        if self.is_super_admin():
            # 超级管理员拥有所有权限，返回通配符权限
            wildcard_permission = Permission(
                id=uuid7(),
                name=PermissionName("*.*.*"),
                display_name="所有权限",
                description="超级管理员通配符权限"
            )
            return [wildcard_permission]

        all_permissions = []
        for role in self._roles:
            for permission in role.permissions:
                if permission not in all_permissions:
                    all_permissions.append(permission)

        return all_permissions

    def get_permissions_by_module(self, module: str) -> list[Permission]:
        """获取指定模块的权限"""
        all_permissions = self.get_all_permissions()
        return [perm for perm in all_permissions if perm.module == module or perm.name.value == "*.*.*"]

    def suspend(self, reason: str) -> None:
        """暂停用户"""
        if self.status == UserStatus.SUSPENDED:
            raise BusinessRuleViolationException("用户已被暂停")

        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """激活用户"""
        if self.status == UserStatus.ACTIVE:
            raise BusinessRuleViolationException("用户已处于激活状态")

        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def record_login(self) -> None:
        """记录登录"""
        self.last_login_at = datetime.utcnow()

    def increment_key_version(self) -> None:
        """递增token版本号，使所有现有token失效"""
        self.key_version += 1
        self.updated_at = datetime.utcnow()

    @property
    def roles(self) -> list[Role]:
        """角色列表"""
        return self._roles.copy()

    @property
    def is_active(self) -> bool:
        """是否活跃"""
        return self.status == UserStatus.ACTIVE


# 领域异常
class UserAlreadyExistsException(DomainException):
    """用户已存在异常"""
    pass


class InvalidCredentialsException(DomainException):
    """无效凭证异常"""
    pass


class EmailNotVerifiedException(DomainException):
    """邮箱未验证异常"""
    pass


class AuditLog(Entity):
    """审计日志实体（简化版）"""

    def __init__(
        self,
        id: UUID | None,
        user_id: UUID | None,
        username: str | None,
        action: str | None,
        description: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        success: bool = True,
        error_message: str | None = None,
        created_at: datetime | None = None
    ):
        super().__init__(id)
        self.user_id = user_id
        self.username = username
        self.action = action
        self.description = description
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.success = success
        self.error_message = error_message
        self.created_at = created_at or datetime.utcnow()

        # 验证领域规则
        self._validate()

    def _validate(self) -> None:
        """验证领域规则"""
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("操作描述不能为空")

        if not self.success and not self.error_message:
            raise ValueError("操作失败时必须提供错误信息")

    @property
    def is_system_operation(self) -> bool:
        """是否为系统操作"""
        return self.user_id is None

    def get_operation_summary(self) -> str:
        """获取操作摘要"""
        actor = self.username if self.username else "系统"
        return f"{actor} {self.action}"
