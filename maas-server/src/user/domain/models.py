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
class UserQuota(ValueObject):
    """用户配额值对象"""
    api_calls_limit: int
    api_calls_used: int
    storage_limit: int  # bytes
    storage_used: int   # bytes
    compute_hours_limit: int
    compute_hours_used: int

    def _validate(self) -> None:
        if self.api_calls_limit < 0:
            raise ValueError("API调用限制不能为负数")
        if self.storage_limit < 0:
            raise ValueError("存储限制不能为负数")
        if self.compute_hours_limit < 0:
            raise ValueError("计算时间限制不能为负数")

    def can_make_api_call(self, count: int = 1) -> bool:
        """检查是否可以进行API调用"""
        return self.api_calls_used + count <= self.api_calls_limit

    def can_use_storage(self, size: int) -> bool:
        """检查是否可以使用存储空间"""
        return self.storage_used + size <= self.storage_limit

    def can_use_compute_hours(self, hours: int) -> bool:
        """检查是否可以使用计算时间"""
        return self.compute_hours_used + hours <= self.compute_hours_limit

    def get_api_usage_percentage(self) -> float:
        """获取API使用百分比"""
        if self.api_calls_limit == 0:
            return 0
        return (self.api_calls_used / self.api_calls_limit) * 100

    def get_storage_usage_percentage(self) -> float:
        """获取存储使用百分比"""
        if self.storage_limit == 0:
            return 0
        return (self.storage_used / self.storage_limit) * 100


class Permission(Entity):
    """权限实体"""

    def __init__(
        self,
        id: UUID,
        name: str,
        description: str,
        resource: str,
        action: str
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.resource = resource
        self.action = action

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"


class Role(Entity):
    """角色实体"""

    def __init__(
        self,
        id: UUID,
        name: str,
        description: str,
        permissions: list[Permission]
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self._permissions = permissions.copy()

    @property
    def permissions(self) -> list[Permission]:
        """权限列表"""
        return self._permissions.copy()

    def add_permission(self, permission: Permission) -> None:
        """添加权限"""
        if permission not in self._permissions:
            self._permissions.append(permission)

    def remove_permission(self, permission: Permission) -> None:
        """移除权限"""
        if permission in self._permissions:
            self._permissions.remove(permission)

    def has_permission(self, resource: str, action: str) -> bool:
        """检查是否有特定权限"""
        for perm in self._permissions:
            if perm.resource == resource and perm.action == action:
                return True
            # 检查通配符权限
            if perm.resource == resource and perm.action == "*":
                return True
            if perm.resource == "*" and perm.action == "*":
                return True
        return False


class ApiKey(Entity):
    """API密钥实体"""

    def __init__(
        self,
        id: UUID,
        name: str,
        key_hash: str,
        permissions: list[str],
        expires_at: datetime | None = None,
        last_used_at: datetime | None = None,
        created_at: datetime | None = None
    ):
        super().__init__(id)
        self.name = name
        self.key_hash = key_hash
        self.permissions = permissions
        self.expires_at = expires_at
        self.last_used_at = last_used_at
        self.created_at = created_at or datetime.utcnow()
        self.is_active = True

    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """检查是否有效"""
        return self.is_active and not self.is_expired()

    def use(self) -> None:
        """使用API密钥"""
        if not self.is_valid():
            raise BusinessRuleViolationException("API密钥无效或已过期")
        self.last_used_at = datetime.utcnow()

    def revoke(self) -> None:
        """撤销API密钥"""
        self.is_active = False


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


@dataclass
class ApiKeyCreatedEvent(DomainEvent):
    """API密钥创建事件"""
    user_id: UUID
    api_key_id: UUID
    api_key_name: str

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "user.api_key_created"
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
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_login_at = last_login_at

        self._roles: list[Role] = []
        self._api_keys: list[ApiKey] = []
        self._quota: UserQuota | None = None

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
            profile=profile
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
            }
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
            event_data={
                "user_id": str(self.id),
                "old_profile": old_profile,
                "new_profile": {
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "organization": profile.organization,
                    "bio": profile.bio
                }
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

    def has_permission(self, resource: str, action: str) -> bool:
        """检查是否有权限"""
        return any(role.has_permission(resource, action) for role in self._roles)

    def create_api_key(
        self,
        name: str,
        key_hash: str,
        permissions: list[str],
        expires_at: datetime | None = None
    ) -> ApiKey:
        """创建API密钥"""
        if len(self._api_keys) >= 10:  # 限制API密钥数量
            raise BusinessRuleViolationException("API密钥数量已达上限")

        api_key = ApiKey(
            id=uuid7(),
            name=name,
            key_hash=key_hash,
            permissions=permissions,
            expires_at=expires_at
        )

        self._api_keys.append(api_key)
        self.updated_at = datetime.utcnow()

        # 添加领域事件
        self.add_domain_event(ApiKeyCreatedEvent(
            event_id=uuid7(),
            occurred_at=datetime.utcnow(),
            event_type="user.api_key_created",
            aggregate_id=self.id,
            aggregate_type="User",
            event_data={
                "user_id": str(self.id),
                "api_key_id": str(api_key.id),
                "api_key_name": name
            }
        ))

        return api_key

    def revoke_api_key(self, api_key_id: UUID) -> None:
        """撤销API密钥"""
        api_key = next((key for key in self._api_keys if key.id == api_key_id), None)
        if not api_key:
            raise BusinessRuleViolationException("API密钥不存在")

        api_key.revoke()
        self.updated_at = datetime.utcnow()

    def set_quota(self, quota: UserQuota) -> None:
        """设置用户配额"""
        self._quota = quota
        self.updated_at = datetime.utcnow()

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

    @property
    def roles(self) -> list[Role]:
        """角色列表"""
        return self._roles.copy()

    @property
    def api_keys(self) -> list[ApiKey]:
        """API密钥列表"""
        return self._api_keys.copy()

    @property
    def quota(self) -> UserQuota | None:
        """用户配额"""
        return self._quota

    @property
    def is_active(self) -> bool:
        """是否活跃"""
        return self.status == UserStatus.ACTIVE and self.email_verified


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
