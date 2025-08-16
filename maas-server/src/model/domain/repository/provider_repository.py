"""
模型供应商数据访问仓库

"""
from abc import abstractmethod
from typing import Any

from model.domain.models.provider_model import ModelConfigEntity, ProviderEntity
from shared.domain.base import Repository


class IProviderRepository(Repository[ProviderEntity]):
    """供应商仓库接口"""

    @abstractmethod
    async def create(self, provider: ProviderEntity) -> ProviderEntity:
        """创建供应商"""
        pass

    @abstractmethod
    async def get_by_id(self, provider_id: int) -> ProviderEntity | None:
        """根据ID获取供应商"""
        pass

    @abstractmethod
    async def get_by_name(self, provider_name: str) -> ProviderEntity | None:
        """根据名称获取供应商"""
        pass

    @abstractmethod
    async def get_all(self, include_deleted: bool = False) -> list[ProviderEntity]:
        """获取所有供应商"""
        pass

    @abstractmethod
    async def get_by_type(self, provider_type: str) -> list[ProviderEntity]:
        """根据类型获取供应商列表"""
        pass

    @abstractmethod
    async def get_active_providers(self) -> list[ProviderEntity]:
        """获取所有活跃的供应商"""
        pass

    @abstractmethod
    async def update(self, provider_id: int, update_data: dict[str, Any]) -> bool:
        """更新供应商信息"""
        pass

    @abstractmethod
    async def delete(self, provider_id: int) -> bool:
        """软删除供应商"""
        pass

    @abstractmethod
    async def activate(self, provider_id: int) -> bool:
        """激活供应商"""
        pass

    @abstractmethod
    async def deactivate(self, provider_id: int) -> bool:
        """停用供应商"""
        pass

    @abstractmethod
    async def search(self, keyword: str, provider_type: str | None = None,
                    is_active: bool | None = None) -> list[ProviderEntity]:
        """搜索供应商"""
        pass

    @abstractmethod
    async def find_paginated(self, conditions: dict[str, Any], offset: int, limit: int,
                           sort_by: str = "created_at", sort_order: str = "desc") -> list[ProviderEntity]:
        """分页查询供应商"""
        pass

    @abstractmethod
    async def count_by_criteria(self, conditions: dict[str, Any]) -> int:
        """根据条件统计数量"""
        pass


class IModelConfigRepository(Repository[ModelConfigEntity]):
    """供应商模型配置仓库接口"""

    @abstractmethod
    async def create(self, config: ModelConfigEntity) -> ModelConfigEntity:
        """创建模型配置"""
        pass

    @abstractmethod
    async def get_by_id(self, config_id: int) -> ModelConfigEntity | None:
        """根据ID获取模型配置"""
        pass

    @abstractmethod
    async def update(self, config_id: int, update_data: dict[str, Any]) -> bool:
        """更新模型配置"""
        pass

    @abstractmethod
    async def delete(self, config_id: int) -> bool:
        """软删除模型配置"""
        pass

    @abstractmethod
    async def activate(self, config_id: int) -> bool:
        """激活模型配置"""
        pass

    @abstractmethod
    async def deactivate(self, config_id: int) -> bool:
        """停用模型配置"""
        pass

    @abstractmethod
    async def search(self, keyword: str, provider_id: int | None = None,
                    model_type: str | None = None, is_active: bool | None = None) -> list[ModelConfigEntity]:
        """搜索模型配置"""
        pass

    @abstractmethod
    async def find_paginated(self, conditions: dict[str, Any], offset: int, limit: int,
                           sort_by: str = "created_at", sort_order: str = "desc") -> list[ModelConfigEntity]:
        """分页查询模型配置"""
        pass

    @abstractmethod
    async def count_by_criteria(self, conditions: dict[str, Any]) -> int:
        """根据条件统计数量"""
        pass

    @abstractmethod
    async def get_by_provider_and_name(self, provider_id: int, model_name: str) -> ModelConfigEntity | None:
        """根据供应商ID和模型名称获取配置"""
        pass



