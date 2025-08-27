"""
模型供应商数据访问仓库

"""
from typing import Any
from loguru import logger

from sqlalchemy import and_, asc, desc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from model.domain.models.provider_model import ModelConfigEntity, ProviderEntity
from model.domain.repository.provider_repository import (
    IModelConfigRepository,
    IProviderRepository,
)
from model.infrastructure.models import ModelConfigORM, ProviderORM
from shared.infrastructure.repository import SQLAlchemyRepository


class ProviderRepository(SQLAlchemyRepository[ProviderEntity, ProviderORM], IProviderRepository):
    """模型供应商仓库实现类"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ProviderEntity, ProviderORM)

    def _to_entity(self, model: ProviderORM | None) -> ProviderEntity | None:
        """将ORM模型转换为领域实体"""
        if not model:
            return None

        return ProviderEntity(
            provider_id=model.provider_id,
            provider_name=model.provider_name,
            provider_type=model.provider_type,
            display_name=model.display_name,
            description=model.description,
            base_url=model.base_url,
            api_key=model.api_key,
            additional_config=model.additional_config,
            is_active=model.is_active,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_by=model.updated_by,
            updated_at=model.updated_at,
            is_delete=model.is_delete
        )

    def _to_model(self, entity: ProviderEntity) -> ProviderORM:
        """将领域实体转换为ORM模型"""
        if not entity:
            return None

        return ProviderORM(
            provider_id=entity.provider_id,
            provider_name=entity.provider_name,
            provider_type=entity.provider_type,
            display_name=entity.display_name,
            description=entity.description,
            base_url=entity.base_url,
            api_key=entity.api_key,
            additional_config=entity.additional_config,
            is_active=entity.is_active,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_by=entity.updated_by,
            updated_at=entity.updated_at,
            is_delete=entity.is_delete
        )

    async def create(self, provider: ProviderEntity) -> ProviderEntity:
        """创建供应商"""
        model = self._to_model(provider)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, provider_id: int) -> ProviderEntity | None:
        """根据ID获取供应商"""
        stmt = select(ProviderORM).where(
            ProviderORM.provider_id == provider_id,
            not ProviderORM.is_delete
        ).options(selectinload(ProviderORM.model_configs))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model)

    async def get_by_name(self, provider_name: str) -> ProviderEntity | None:
        """根据名称获取供应商"""
        stmt = select(ProviderORM).where(
            ProviderORM.provider_name == provider_name,
            not ProviderORM.is_delete
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model)

    async def get_all(self, include_deleted: bool = False) -> list[ProviderEntity]:
        """获取所有供应商"""
        stmt = select(ProviderORM)
        if not include_deleted:
            stmt = stmt.where(not ProviderORM.is_delete)
        stmt = stmt.order_by(desc(ProviderORM.created_at))
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_by_type(self, provider_type: str) -> list[ProviderEntity]:
        """根据类型获取供应商列表"""
        stmt = select(ProviderORM).where(
            ProviderORM.provider_type == provider_type,
            not ProviderORM.is_delete
        ).order_by(asc(ProviderORM.display_name))
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_active_providers(self) -> list[ProviderEntity]:
        """获取所有活跃的供应商"""
        stmt = select(ProviderORM).where(
            ProviderORM.is_active,
            not ProviderORM.is_delete
        ).order_by(asc(ProviderORM.display_name))
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, provider_id: int, update_data: dict[str, Any]) -> bool:
        """更新供应商信息"""
        stmt = update(ProviderORM).where(
            ProviderORM.provider_id == provider_id,
            not ProviderORM.is_delete
        ).values(**update_data)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete(self, provider_id: int) -> bool:
        """软删除供应商"""
        return await self.update(provider_id, {"is_delete": True})

    async def activate(self, provider_id: int) -> bool:
        """激活供应商"""
        return await self.update(provider_id, {"is_active": True})

    async def deactivate(self, provider_id: int) -> bool:
        """停用供应商"""
        return await self.update(provider_id, {"is_active": False})

    async def search(self, keyword: str, provider_type: str | None = None,
                    is_active: bool | None = None) -> list[ProviderEntity]:
        """搜索供应商"""
        conditions = [ProviderORM.is_delete == False]  # 使用显式比较以利用索引

        # 供应商类型过滤 - 优先添加索引字段条件
        if provider_type:
            conditions.append(ProviderORM.provider_type == provider_type)

        # 活跃状态过滤 - 使用索引字段
        if is_active is not None:
            conditions.append(ProviderORM.is_active == is_active)

        # 关键词搜索 - 优化搜索条件顺序，优先使用索引字段
        if keyword:
            keyword_condition = or_(
                ProviderORM.provider_name.ilike(f"%{keyword}%"),  # 使用ilike支持大小写不敏感搜索
                ProviderORM.display_name.ilike(f"%{keyword}%"),
                ProviderORM.description.ilike(f"%{keyword}%")
            )
            conditions.append(keyword_condition)

        # 优化查询：添加查询提示和限制结果集
        stmt = (
            select(ProviderORM)
            .where(and_(*conditions))
            .order_by(desc(ProviderORM.created_at))
            .limit(1000)  # 限制最大结果数以防止大量数据查询
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_paginated(self, conditions: dict[str, Any], offset: int, limit: int,
                           sort_by: str = "created_at", sort_order: str = "desc") -> list[ProviderEntity]:
        """分页查询供应商"""
        stmt = select(ProviderORM)

        # 添加查询条件 - 优化条件顺序，优先使用索引字段
        indexed_conditions = []
        other_conditions = []

        for key, value in conditions.items():
            if hasattr(ProviderORM, key):
                condition = getattr(ProviderORM, key) == value
                # 优先处理索引字段
                if key in ["is_delete", "is_active", "provider_type", "provider_name"]:
                    indexed_conditions.append(condition)
                else:
                    other_conditions.append(condition)

        # 先应用索引条件，再应用其他条件
        all_conditions = indexed_conditions + other_conditions
        if all_conditions:
            stmt = stmt.where(and_(*all_conditions))

        # 添加排序
        sort_column = getattr(ProviderORM, sort_by, ProviderORM.created_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        # 优化分页 - 对于大偏移量给出警告
        if offset > 10000:
            logger.warning(f"Large offset detected ({offset}). Consider using cursor-based pagination.")

        # 限制最大页面大小
        limit = min(limit, 1000)
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count_by_criteria(self, conditions: dict[str, Any]) -> int:
        """根据条件统计数量"""
        from sqlalchemy import func
        stmt = select(func.count(ProviderORM.provider_id))

        # 添加查询条件
        for key, value in conditions.items():
            if hasattr(ProviderORM, key):
                stmt = stmt.where(getattr(ProviderORM, key) == value)

        result = await self.session.execute(stmt)
        return result.scalar() or 0


class ModelConfigRepository(SQLAlchemyRepository[ModelConfigEntity, ModelConfigORM], IModelConfigRepository):
    """供应商模型配置仓库实现类"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ModelConfigEntity, ModelConfigORM)

    def _to_entity(self, model: ModelConfigORM | None) -> ModelConfigEntity | None:
        """将ORM模型转换为领域实体"""
        if not model:
            return None

        return ModelConfigEntity(
            config_id=model.config_id,
            provider_id=model.provider_id,
            model_name=model.model_name,
            model_display_name=model.model_display_name,
            model_type=model.model_type,
            model_params=model.model_params,
            max_tokens=model.max_tokens,
            max_input_tokens=model.max_input_tokens,
            temperature=model.temperature,
            pricing_config=model.pricing_config,
            is_active=model.is_active,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_by=model.updated_by,
            updated_at=model.updated_at,
            is_delete=model.is_delete
        )

    def _to_model(self, entity: ModelConfigEntity) -> ModelConfigORM:
        """将领域实体转换为ORM模型"""
        if not entity:
            return None

        return ModelConfigORM(
            config_id=entity.config_id,
            provider_id=entity.provider_id,
            model_name=entity.model_name,
            model_display_name=entity.model_display_name,
            model_type=entity.model_type,
            model_params=entity.model_params,
            max_tokens=entity.max_tokens,
            max_input_tokens=entity.max_input_tokens,
            temperature=entity.temperature,
            pricing_config=entity.pricing_config,
            is_active=entity.is_active,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_by=entity.updated_by,
            updated_at=entity.updated_at,
            is_delete=entity.is_delete
        )

    async def create(self, config: ModelConfigEntity) -> ModelConfigEntity:
        """创建模型配置"""
        model = self._to_model(config)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, config_id: int) -> ModelConfigEntity | None:
        """根据ID获取模型配置"""
        stmt = select(ModelConfigORM).where(
            ModelConfigORM.config_id == config_id,
            not ModelConfigORM.is_delete
        ).options(joinedload(ModelConfigORM.provider))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model)

    async def update(self, config_id: int, update_data: dict[str, Any]) -> bool:
        """更新模型配置"""
        stmt = update(ModelConfigORM).where(
            ModelConfigORM.config_id == config_id,
            not ModelConfigORM.is_delete
        ).values(**update_data)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete(self, config_id: int) -> bool:
        """软删除模型配置"""
        return await self.update(config_id, {"is_delete": True})

    async def activate(self, config_id: int) -> bool:
        """激活模型配置"""
        return await self.update(config_id, {"is_active": True})

    async def deactivate(self, config_id: int) -> bool:
        """停用模型配置"""
        return await self.update(config_id, {"is_active": False})

    async def search(self, keyword: str, provider_id: int | None = None,
                    model_type: str | None = None, is_active: bool | None = None) -> list[ModelConfigEntity]:
        """搜索模型配置"""
        conditions = [not ModelConfigORM.is_delete]

        # 关键词搜索
        if keyword:
            keyword_condition = or_(
                ModelConfigORM.model_name.contains(keyword),
                ModelConfigORM.model_display_name.contains(keyword)
            )
            conditions.append(keyword_condition)

        # 供应商过滤
        if provider_id:
            conditions.append(ModelConfigORM.provider_id == provider_id)

        # 模型类型过滤
        if model_type:
            conditions.append(ModelConfigORM.model_type == model_type)

        # 活跃状态过滤
        if is_active is not None:
            conditions.append(ModelConfigORM.is_active == is_active)

        stmt = select(ModelConfigORM).where(and_(*conditions)).options(
            joinedload(ModelConfigORM.provider)
        ).order_by(desc(ModelConfigORM.created_at))
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_paginated(self, conditions: dict[str, Any], offset: int, limit: int,
                           sort_by: str = "created_at", sort_order: str = "desc") -> list[ModelConfigEntity]:
        """分页查询模型配置"""
        stmt = select(ModelConfigORM).options(joinedload(ModelConfigORM.provider))

        # 添加查询条件
        for key, value in conditions.items():
            if hasattr(ModelConfigORM, key):
                stmt = stmt.where(getattr(ModelConfigORM, key) == value)

        # 添加排序
        sort_column = getattr(ModelConfigORM, sort_by, ModelConfigORM.created_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        # 添加分页
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count_by_criteria(self, conditions: dict[str, Any]) -> int:
        """根据条件统计数量"""
        from sqlalchemy import func
        stmt = select(func.count(ModelConfigORM.config_id))

        # 添加查询条件
        for key, value in conditions.items():
            if hasattr(ModelConfigORM, key):
                stmt = stmt.where(getattr(ModelConfigORM, key) == value)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_by_provider_and_name(self, provider_id: int, model_name: str) -> ModelConfigEntity | None:
        """根据供应商ID和模型名称获取配置"""
        stmt = select(ModelConfigORM).where(
            ModelConfigORM.provider_id == provider_id,
            ModelConfigORM.model_name == model_name,
            not ModelConfigORM.is_delete
        ).options(joinedload(ModelConfigORM.provider))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model)
