"""共享基础设施层 - 仓储基类实现"""

from abc import ABC
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.base import AggregateRoot, Repository
from shared.infrastructure.database import Base

T = TypeVar("T", bound=AggregateRoot)
M = TypeVar("M", bound=Base)


class SQLAlchemyRepository(Repository[T], Generic[T, M]):
    """SQLAlchemy仓储基类"""

    def __init__(self, session: AsyncSession, model_class: type[M]):
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, id: UUID) -> T | None:
        """根据ID获取聚合根"""
        try:
            stmt = select(self.model_class).where(self.model_class.id == id)
            result = await self.session.execute(stmt)
            orm_obj = result.scalar_one()
            return self._to_domain_entity(orm_obj) if orm_obj else None
        except NoResultFound:
            return None

    async def save(self, aggregate: T) -> T:
        """保存聚合根"""
        orm_obj = await self._get_orm_object(aggregate.id)
        if orm_obj:
            # 更新现有对象
            orm_obj = self._update_orm_object(orm_obj, aggregate)
        else:
            # 创建新对象
            orm_obj = self._create_orm_object(aggregate)
            self.session.add(orm_obj)

        await self.session.flush()
        return self._to_domain_entity(orm_obj)

    async def delete(self, aggregate: T) -> None:
        """删除聚合根"""
        stmt = delete(self.model_class).where(self.model_class.id == aggregate.id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def find_by_criteria(self, criteria: dict[str, Any]) -> list[T]:
        """根据条件查找"""
        stmt = select(self.model_class)
        for key, value in criteria.items():
            if hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)

        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def count_by_criteria(self, criteria: dict[str, Any]) -> int:
        """根据条件统计数量"""
        from sqlalchemy import func
        stmt = select(func.count(self.model_class.id))
        for key, value in criteria.items():
            if hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)

        result = await self.session.execute(stmt)
        return result.scalar()

    async def _get_orm_object(self, id: UUID) -> M | None:
        """获取ORM对象"""
        try:
            stmt = select(self.model_class).where(self.model_class.id == id)
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except NoResultFound:
            return None

    def _to_domain_entity(self, orm_obj: M) -> T:
        """将ORM对象转换为领域实体"""
        raise NotImplementedError("子类必须实现此方法")

    def _create_orm_object(self, aggregate: T) -> M:
        """创建ORM对象"""
        raise NotImplementedError("子类必须实现此方法")

    def _update_orm_object(self, orm_obj: M, aggregate: T) -> M:
        """更新ORM对象"""
        raise NotImplementedError("子类必须实现此方法")


class RedisRepository(ABC):
    """Redis仓储基类"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def _get_key(self, *args) -> str:
        """生成Redis键"""
        return ":".join(str(arg) for arg in args)

    async def set_with_expiry(self, key: str, value: str, expiry_seconds: int) -> None:
        """设置带过期时间的键值"""
        await self.redis.setex(key, expiry_seconds, value)

    async def get(self, key: str) -> str | None:
        """获取值"""
        return await self.redis.get(key)

    async def delete(self, key: str) -> None:
        """删除键"""
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.redis.exists(key)
