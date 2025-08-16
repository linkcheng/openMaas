from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

# 类型变量，用于泛型
T = TypeVar("T")
M = TypeVar("M")


class BaseRepository(Generic[T, M]):
    """基础仓储，提供基础的CRUD操作"""

    def __init__(self, session: AsyncSession, entity_class: type[T], model_class: type[M]):
        self.session = session
        self.entity_class = entity_class
        self.model_class = model_class

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
