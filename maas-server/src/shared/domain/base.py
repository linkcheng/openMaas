"""共享领域层 - 基础实体和值对象"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4


# 领域事件基类
@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: UUID
    occurred_at: datetime
    event_type: str
    aggregate_id: UUID
    aggregate_type: str
    event_data: dict[str, Any]

    def __post_init__(self):
        if not self.event_id:
            self.event_id = uuid4()
        if not self.occurred_at:
            self.occurred_at = datetime.utcnow()


# 聚合根基类
class AggregateRoot(ABC):
    """聚合根基类"""

    def __init__(self, id: UUID):
        self.id = id
        self._domain_events: list[DomainEvent] = []

    def add_domain_event(self, event: DomainEvent) -> None:
        """添加领域事件"""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """清除领域事件"""
        self._domain_events.clear()

    def get_domain_events(self) -> list[DomainEvent]:
        """获取领域事件"""
        return self._domain_events.copy()


# 实体基类
class Entity(ABC):
    """实体基类"""

    def __init__(self, id: UUID):
        self.id = id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


# 值对象基类
@dataclass(frozen=True)
class ValueObject(ABC):
    """值对象基类"""

    def __post_init__(self):
        self._validate()

    @abstractmethod
    def _validate(self) -> None:
        """验证值对象的有效性"""
        pass


# 仓储接口基类
T = TypeVar("T", bound=AggregateRoot)


class Repository(Generic[T], ABC):
    """仓储接口基类"""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        """根据ID获取聚合根"""
        pass

    @abstractmethod
    async def save(self, aggregate: T) -> T:
        """保存聚合根"""
        pass

    @abstractmethod
    async def delete(self, aggregate: T) -> None:
        """删除聚合根"""
        pass


# 领域服务基类
class DomainService(ABC):
    """领域服务基类"""
    pass


# 常用值对象
@dataclass(frozen=True)
class EmailAddress(ValueObject):
    """邮箱地址值对象"""
    value: str

    def _validate(self) -> None:
        import re
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, self.value):
            raise ValueError(f"无效的邮箱地址: {self.value}")


@dataclass(frozen=True)
class UserId(ValueObject):
    """用户ID值对象"""
    value: UUID

    def _validate(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("用户ID必须是UUID类型")


@dataclass(frozen=True)
class ModelId(ValueObject):
    """模型ID值对象"""
    value: UUID

    def _validate(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("模型ID必须是UUID类型")


@dataclass(frozen=True)
class Money(ValueObject):
    """金额值对象"""
    amount: float
    currency: str = "USD"

    def _validate(self) -> None:
        if self.amount < 0:
            raise ValueError("金额不能为负数")
        if not self.currency:
            raise ValueError("货币类型不能为空")


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    """电话号码值对象"""
    value: str

    def _validate(self) -> None:
        import re
        # 简单的电话号码验证
        phone_regex = r"^\+?1?\d{9,15}$"
        if not re.match(phone_regex, self.value):
            raise ValueError(f"无效的电话号码: {self.value}")


# 领域异常
class DomainException(Exception):
    """领域异常基类"""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.code = code


class BusinessRuleViolationException(DomainException):
    """业务规则违反异常"""
    pass


class ResourceNotFoundException(DomainException):
    """资源未找到异常"""
    pass


class AccessDeniedException(DomainException):
    """访问被拒绝异常"""
    pass


class InvalidOperationException(DomainException):
    """无效操作异常"""
    pass
