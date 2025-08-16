"""
模型供应商数据模型

"""
import datetime
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from shared.domain.base import (
    Entity,
)


@dataclass
class ProviderEntity(Entity):
    """模型供应商实体类，用于业务逻辑处理"""
    provider_id: int | None = None
    provider_name: str = ""
    provider_type: str = ""
    display_name: str = ""
    description: str | None = None
    base_url: str = ""
    api_key: str | None = None
    additional_config: dict[str, Any] | None = None
    is_active: bool = True
    created_by: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_by: str = ""
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    is_delete: bool = False


@dataclass
class ModelConfigEntity(Entity):
    """模型配置实体类，用于业务逻辑处理"""
    config_id: int | None = None
    provider_id: int = 0
    model_name: str = ""
    model_display_name: str = ""
    model_type: str = ""
    model_params: dict[str, Any] | None = None
    max_tokens: int | None = 4096
    max_input_tokens: int | None = 3072
    temperature: Decimal | None = Decimal("0.70")
    pricing_config: dict[str, Any] | None = None
    is_active: bool = True
    created_by: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_by: str = ""
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    is_delete: bool = False
