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

"""供应商领域服务实现"""

import re
from typing import Any
from urllib.parse import urlparse

from model.domain.exceptions import (
    BusinessRuleViolationException,
    ProviderAlreadyExistsException,
    ProviderHasActiveModelsException,
    ProviderNotFoundException,
    ProviderValidationException,
)
from model.domain.models.provider_model import ProviderEntity
from model.domain.repository.provider_repository import (
    IModelConfigRepository,
    IProviderRepository,
)


class ProviderDomainService:
    """供应商领域服务，实现核心业务逻辑和业务规则验证"""

    def __init__(
        self,
        provider_repo: IProviderRepository,
        model_config_repo: IModelConfigRepository
    ):
        self.provider_repo = provider_repo
        self.model_config_repo = model_config_repo

    async def validate_provider_creation(self, provider: ProviderEntity) -> None:
        """验证供应商创建的业务规则"""
        # 验证供应商名称唯一性
        existing_provider = await self.provider_repo.get_by_name(provider.provider_name)
        if existing_provider and not existing_provider.is_delete:
            raise ProviderAlreadyExistsException(provider.provider_name)

        # 验证供应商基本信息
        self._validate_provider_basic_info(provider)

        # 验证供应商配置
        self._validate_provider_config(provider)

    async def validate_provider_update(self, provider_id: int, update_data: dict[str, Any],
                                     current_provider: ProviderEntity | None = None) -> ProviderEntity:
        """验证供应商更新的业务规则"""
        if not current_provider:
            current_provider = await self.provider_repo.get_by_id(provider_id)
            if not current_provider:
                raise ProviderNotFoundException(provider_id)

        # 检查供应商是否已被删除
        if current_provider.is_delete:
            raise ProviderNotFoundException(provider_id)

        # 如果更新供应商名称，检查唯一性
        if "provider_name" in update_data and update_data["provider_name"] != current_provider.provider_name:
            existing_provider = await self.provider_repo.get_by_name(update_data["provider_name"])
            if existing_provider and not existing_provider.is_delete and existing_provider.provider_id != provider_id:
                raise ProviderAlreadyExistsException(update_data["provider_name"])

        # 创建更新后的实体进行验证
        updated_provider = self._create_updated_provider(current_provider, update_data)
        self._validate_provider_basic_info(updated_provider)
        self._validate_provider_config(updated_provider)

        return updated_provider

    async def validate_provider_deletion(self, provider_id: int) -> None:
        """验证供应商删除的业务规则"""
        provider = await self.provider_repo.get_by_id(provider_id)
        if not provider or provider.is_delete:
            raise ProviderNotFoundException(provider_id)

        # 检查是否有活跃的模型配置
        active_models = await self.model_config_repo.search(
            keyword="",
            provider_id=provider_id,
            is_active=True
        )

        if active_models:
            raise ProviderHasActiveModelsException(provider_id, len(active_models))

    async def validate_provider_activation(self, provider_id: int) -> None:
        """验证供应商激活的业务规则"""
        provider = await self.provider_repo.get_by_id(provider_id)
        if not provider or provider.is_delete:
            raise ProviderNotFoundException(provider_id)

        if provider.is_active:
            raise BusinessRuleViolationException(
                "provider_already_active",
                f"供应商 {provider_id} 已经是激活状态"
            )

        # 验证供应商配置完整性
        self._validate_provider_config(provider)

    async def validate_provider_deactivation(self, provider_id: int) -> None:
        """验证供应商停用的业务规则"""
        provider = await self.provider_repo.get_by_id(provider_id)
        if not provider or provider.is_delete:
            raise ProviderNotFoundException(provider_id)

        if not provider.is_active:
            raise BusinessRuleViolationException(
                "provider_already_inactive",
                f"供应商 {provider_id} 已经是停用状态"
            )

    async def manage_provider_lifecycle(self, provider_id: int, action: str, user_id: str) -> bool:
        """管理供应商生命周期状态"""
        if action == "activate":
            await self.validate_provider_activation(provider_id)
            return await self.provider_repo.activate(provider_id)
        elif action == "deactivate":
            await self.validate_provider_deactivation(provider_id)
            # 停用供应商时，同时停用其所有模型配置
            await self._deactivate_provider_models(provider_id)
            return await self.provider_repo.deactivate(provider_id)
        else:
            raise BusinessRuleViolationException(
                "invalid_lifecycle_action",
                f"无效的生命周期操作: {action}"
            )

    async def manage_provider_model_associations(self, provider_id: int) -> dict[str, Any]:
        """管理供应商与模型配置的关联关系"""
        provider = await self.provider_repo.get_by_id(provider_id)
        if not provider or provider.is_delete:
            raise ProviderNotFoundException(provider_id)

        # 获取供应商的所有模型配置
        all_models = await self.model_config_repo.search(
            keyword="",
            provider_id=provider_id
        )

        active_models = [model for model in all_models if model.is_active and not model.is_delete]
        inactive_models = [model for model in all_models if not model.is_active and not model.is_delete]

        return {
            "provider_id": provider_id,
            "provider_name": provider.provider_name,
            "provider_active": provider.is_active,
            "total_models": len(all_models),
            "active_models": len(active_models),
            "inactive_models": len(inactive_models),
            "active_model_list": [
                {
                    "config_id": model.config_id,
                    "model_name": model.model_name,
                    "model_type": model.model_type
                }
                for model in active_models
            ],
            "inactive_model_list": [
                {
                    "config_id": model.config_id,
                    "model_name": model.model_name,
                    "model_type": model.model_type
                }
                for model in inactive_models
            ]
        }

    def _validate_provider_basic_info(self, provider: ProviderEntity) -> None:
        """验证供应商基本信息"""
        # 验证供应商名称
        if not provider.provider_name or not provider.provider_name.strip():
            raise ProviderValidationException("provider_name", provider.provider_name, "供应商名称不能为空")

        if len(provider.provider_name) > 64:
            raise ProviderValidationException("provider_name", provider.provider_name, "供应商名称长度不能超过64个字符")

        # 验证供应商名称格式（只允许字母、数字、下划线、连字符）
        if not re.match(r"^[a-zA-Z0-9_-]+$", provider.provider_name):
            raise ProviderValidationException(
                "provider_name",
                provider.provider_name,
                "供应商名称只能包含字母、数字、下划线和连字符"
            )

        # 验证供应商类型
        if not provider.provider_type or not provider.provider_type.strip():
            raise ProviderValidationException("provider_type", provider.provider_type, "供应商类型不能为空")

        valid_provider_types = ["openai", "anthropic", "google", "azure", "aws", "huggingface", "custom"]
        if provider.provider_type not in valid_provider_types:
            raise ProviderValidationException(
                "provider_type",
                provider.provider_type,
                f"供应商类型必须是以下之一: {', '.join(valid_provider_types)}"
            )

        # 验证显示名称
        if not provider.display_name or not provider.display_name.strip():
            raise ProviderValidationException("display_name", provider.display_name, "显示名称不能为空")

        if len(provider.display_name) > 128:
            raise ProviderValidationException("display_name", provider.display_name, "显示名称长度不能超过128个字符")

        # 验证描述长度
        if provider.description and len(provider.description) > 1000:
            raise ProviderValidationException("description", provider.description, "描述长度不能超过1000个字符")

    def _validate_provider_config(self, provider: ProviderEntity) -> None:
        """验证供应商配置信息"""
        # 验证基础URL
        if not provider.base_url or not provider.base_url.strip():
            raise ProviderValidationException("base_url", provider.base_url, "基础URL不能为空")

        # 验证URL格式
        try:
            parsed_url = urlparse(provider.base_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ProviderValidationException("base_url", provider.base_url, "基础URL格式无效")

            if parsed_url.scheme not in ["http", "https"]:
                raise ProviderValidationException("base_url", provider.base_url, "基础URL必须使用HTTP或HTTPS协议")
        except Exception:
            raise ProviderValidationException("base_url", provider.base_url, "基础URL格式无效")

        # 验证API密钥长度
        if provider.api_key and len(provider.api_key) > 512:
            raise ProviderValidationException("api_key", provider.api_key, "API密钥长度不能超过512个字符")

        # 验证额外配置
        if provider.additional_config:
            self._validate_additional_config(provider.additional_config)

    def _validate_additional_config(self, config: dict[str, Any]) -> None:
        """验证额外配置信息"""
        # 检查配置项数量限制
        if len(config) > 50:
            raise ProviderValidationException(
                "additional_config",
                config,
                "额外配置项数量不能超过50个"
            )

        # 检查配置键名格式
        for key in config:
            if not isinstance(key, str) or len(key) > 100:
                raise ProviderValidationException(
                    "additional_config",
                    key,
                    "配置键名必须是字符串且长度不能超过100个字符"
                )

            if not re.match(r"^[a-zA-Z0-9_.-]+$", key):
                raise ProviderValidationException(
                    "additional_config",
                    key,
                    "配置键名只能包含字母、数字、下划线、点和连字符"
                )

    def _create_updated_provider(self, current_provider: ProviderEntity, update_data: dict[str, Any]) -> ProviderEntity:
        """创建更新后的供应商实体"""
        updated_provider = ProviderEntity(
            provider_id=current_provider.provider_id,
            provider_name=update_data.get("provider_name", current_provider.provider_name),
            provider_type=update_data.get("provider_type", current_provider.provider_type),
            display_name=update_data.get("display_name", current_provider.display_name),
            description=update_data.get("description", current_provider.description),
            base_url=update_data.get("base_url", current_provider.base_url),
            is_active=update_data.get("is_active", current_provider.is_active),
            created_by=current_provider.created_by,
            created_at=current_provider.created_at,
            updated_by=update_data.get("updated_by", current_provider.updated_by),
            updated_at=current_provider.updated_at,
            is_delete=current_provider.is_delete
        )
        return updated_provider

    async def _deactivate_provider_models(self, provider_id: int) -> None:
        """停用供应商的所有模型配置"""
        active_models = await self.model_config_repo.search(
            keyword="",
            provider_id=provider_id,
            is_active=True
        )

        for model in active_models:
            await self.model_config_repo.deactivate(model.config_id)
