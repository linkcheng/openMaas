"""
模型供应商管理仓库包

"""

from .model_config_repository import IModelConfigRepository, ModelConfigRepository
from .provider_repository import IProviderRepository, ProviderRepository

__all__ = [
    "IModelConfigRepository",
    "IProviderRepository",
    "ModelConfigRepository",
    "ProviderRepository"
]
