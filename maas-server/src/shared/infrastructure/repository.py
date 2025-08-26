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

"""共享基础设施层 - 仓储基类实现"""

from abc import ABC
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.base import AggregateRoot, Repository
from shared.infrastructure.database import Base
from shared.infrastructure.transaction_manager import TransactionManager

T = TypeVar("T", bound=AggregateRoot)
M = TypeVar("M", bound=Base)


class SQLAlchemyRepository(Repository[T], Generic[T, M]):
    """SQLAlchemy仓储基类 - 支持事务上下文感知"""

    def __init__(self, session: AsyncSession, entity_class, model_class):
        self._default_session = session
        self.entity_class = entity_class
        self.model_class = model_class
    
    @property
    def session(self) -> AsyncSession:
        """动态获取当前应该使用的session - 事务上下文感知
        
        优先使用事务上下文中的session，确保在@transactional装饰器管理的方法中
        使用同一个session，保证事务一致性。
        """
        current_session = TransactionManager.get_current_session()
        return current_session or self._default_session

    async def commit(self):
        await self.session.commit()

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
        """保存聚合根 - 仅负责数据持久化"""
        orm_obj = await self._get_orm_object(aggregate.id)
        if orm_obj:
            # 更新现有对象
            orm_obj = self._update_orm_object(orm_obj, aggregate)
        else:
            # 创建新对象
            orm_obj = self._create_orm_object(aggregate)
            self.session.add(orm_obj)

        # ✅ 仅flush，确保获得ID等，但不提交事务
        await self.session.flush()
        # ❌ 移除事务提交 - 由上层应用服务层管理
        # await self.session.commit()

        return self._to_domain_entity(orm_obj)

    async def delete(self, aggregate: T) -> None:
        """删除聚合根 - 仅负责数据操作"""
        stmt = delete(self.model_class).where(self.model_class.id == aggregate.id)
        await self.session.execute(stmt)
        # ✅ 仅flush，不提交事务
        await self.session.flush()
        # ❌ 移除事务提交 - 由上层应用服务层管理

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

    def _to_entity(self, model: M) -> T:
        """将ORM模型转换为领域实体"""
        if not model:
            return None

        # 获取模型的所有属性
        attrs = {}
        for key in self.entity_class.__annotations__.keys():
            if hasattr(model, key):
                attrs[key] = getattr(model, key)

        return self.entity_class(**attrs)

    def _to_model(self, entity: T) -> M:
        """将领域实体转换为ORM模型"""
        if not entity:
            return None

        # 如果已有ID，则查询现有模型
        if getattr(entity, "id", None):
            model = self.model_class()
            for key, value in entity.__dict__.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            return model

        # 创建新模型
        attrs = {}
        for key, value in entity.__dict__.items():
            if hasattr(self.model_class, key):
                attrs[key] = value

        return self.model_class(**attrs)


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
