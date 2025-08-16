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

"""模型配置领域服务实现"""

import re
from decimal import Decimal
from typing import Any

from model.domain.exceptions import (
    BusinessRuleViolationException,
    InvalidModelParametersException,
    ModelConfigAlreadyExistsException,
    ModelConfigNotFoundException,
    ModelConfigValidationException,
    ProviderInactiveException,
    ProviderNotFoundException,
)
from model.domain.models.provider_model import ModelConfigEntity
from model.domain.repository.provider_repository import (
    IModelConfigRepository,
    IProviderRepository,
)


class ModelConfigDomainService:
    """模型配置领域服务，实现核心业务逻辑和业务规则验证"""

    def __init__(
        self,
        provider_repo: IProviderRepository,
        model_config_repo: IModelConfigRepository
    ):
        self.provider_repo = provider_repo
        self.model_config_repo = model_config_repo

    async def validate_model_config_creation(self, config: ModelConfigEntity) -> None:
        """验证模型配置创建的业务规则"""
        # 验证供应商存在且激活
        provider = await self.provider_repo.get_by_id(config.provider_id)
        if not provider or provider.is_delete:
            raise ProviderNotFoundException(config.provider_id)

        if not provider.is_active:
            raise ProviderInactiveException(config.provider_id)

        # 验证模型配置唯一性
        existing_config = await self.model_config_repo.get_by_provider_and_name(
            config.provider_id, config.model_name
        )
        if existing_config and not existing_config.is_delete:
            raise ModelConfigAlreadyExistsException(config.provider_id, config.model_name)

        # 验证模型配置基本信息
        self._validate_model_config_basic_info(config)

        # 验证模型参数
        self._validate_model_parameters(config)

        # 验证定价配置
        self._validate_pricing_config(config)

    async def validate_model_config_update(self, config_id: int, update_data: dict[str, Any],
                                         current_config: ModelConfigEntity | None = None) -> ModelConfigEntity:
        """验证模型配置更新的业务规则"""
        if not current_config:
            current_config = await self.model_config_repo.get_by_id(config_id)
            if not current_config:
                raise ModelConfigNotFoundException(config_id)

        # 检查模型配置是否已被删除
        if current_config.is_delete:
            raise ModelConfigNotFoundException(config_id)

        # 如果更新模型名称，检查唯一性
        if "model_name" in update_data and update_data["model_name"] != current_config.model_name:
            existing_config = await self.model_config_repo.get_by_provider_and_name(
                current_config.provider_id, update_data["model_name"]
            )
            if existing_config and not existing_config.is_delete and existing_config.config_id != config_id:
                raise ModelConfigAlreadyExistsException(current_config.provider_id, update_data["model_name"])

        # 创建更新后的实体进行验证
        updated_config = self._create_updated_model_config(current_config, update_data)
        self._validate_model_config_basic_info(updated_config)
        self._validate_model_parameters(updated_config)
        self._validate_pricing_config(updated_config)

        return updated_config

    async def validate_model_config_deletion(self, config_id: int) -> None:
        """验证模型配置删除的业务规则"""
        config = await self.model_config_repo.get_by_id(config_id)
        if not config or config.is_delete:
            raise ModelConfigNotFoundException(config_id)

        # 这里可以添加更多业务规则，比如检查是否有正在使用的任务等
        # 目前允许删除任何模型配置

    async def validate_model_config_activation(self, config_id: int) -> None:
        """验证模型配置激活的业务规则"""
        config = await self.model_config_repo.get_by_id(config_id)
        if not config or config.is_delete:
            raise ModelConfigNotFoundException(config_id)

        if config.is_active:
            raise BusinessRuleViolationException(
                "model_config_already_active",
                f"模型配置 {config_id} 已经是激活状态"
            )

        # 验证供应商是否激活
        provider = await self.provider_repo.get_by_id(config.provider_id)
        if not provider or provider.is_delete:
            raise ProviderNotFoundException(config.provider_id)

        if not provider.is_active:
            raise ProviderInactiveException(config.provider_id)

        # 验证模型配置完整性
        self._validate_model_parameters(config)

    async def validate_model_config_deactivation(self, config_id: int) -> None:
        """验证模型配置停用的业务规则"""
        config = await self.model_config_repo.get_by_id(config_id)
        if not config or config.is_delete:
            raise ModelConfigNotFoundException(config_id)

        if not config.is_active:
            raise BusinessRuleViolationException(
                "model_config_already_inactive",
                f"模型配置 {config_id} 已经是停用状态"
            )

    def validate_model_parameters(self, model_type: str, model_params: dict[str, Any]) -> dict[str, str]:
        """验证模型参数并返回优化建议"""
        suggestions = {}

        # 根据模型类型验证参数
        if model_type == "chat":
            suggestions.update(self._validate_chat_model_params(model_params))
        elif model_type == "completion":
            suggestions.update(self._validate_completion_model_params(model_params))
        elif model_type == "embedding":
            suggestions.update(self._validate_embedding_model_params(model_params))
        elif model_type == "image":
            suggestions.update(self._validate_image_model_params(model_params))
        else:
            suggestions["model_type"] = f"未知的模型类型 '{model_type}'，建议使用标准类型"

        return suggestions

    def generate_config_optimization_suggestions(self, config: ModelConfigEntity) -> dict[str, Any]:
        """生成模型配置优化建议"""
        suggestions = {
            "performance_suggestions": [],
            "cost_suggestions": [],
            "parameter_suggestions": [],
            "security_suggestions": []
        }

        # 性能优化建议
        if config.max_tokens and config.max_tokens > 8192:
            suggestions["performance_suggestions"].append(
                "考虑降低max_tokens以提高响应速度和降低成本"
            )

        if config.temperature and config.temperature > Decimal("1.0"):
            suggestions["performance_suggestions"].append(
                "高temperature值可能导致输出不稳定，建议调整到0.7-1.0之间"
            )

        # 成本优化建议
        if config.max_input_tokens and config.max_input_tokens > 4096:
            suggestions["cost_suggestions"].append(
                "考虑优化输入长度以降低token使用成本"
            )

        # 参数优化建议
        if config.model_params:
            param_suggestions = self.validate_model_parameters(config.model_type, config.model_params)
            suggestions["parameter_suggestions"].extend(param_suggestions.values())

        # 安全建议
        if config.model_params and config.model_params.get("allow_unsafe_content"):
            suggestions["security_suggestions"].append(
                "启用了不安全内容，请确保有适当的内容过滤机制"
            )

        return suggestions

    async def manage_model_config_versions(self, config_id: int) -> dict[str, Any]:
        """管理模型配置版本和历史记录"""
        config = await self.model_config_repo.get_by_id(config_id)
        if not config or config.is_delete:
            raise ModelConfigNotFoundException(config_id)

        # 这里可以实现版本管理逻辑
        # 目前返回基本的版本信息
        return {
            "config_id": config_id,
            "current_version": "1.0",  # 简化版本管理
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "created_by": config.created_by,
            "updated_by": config.updated_by,
            "change_history": [
                {
                    "version": "1.0",
                    "timestamp": config.created_at,
                    "user": config.created_by,
                    "action": "created",
                    "changes": "初始创建"
                }
            ]
        }

    def _validate_model_config_basic_info(self, config: ModelConfigEntity) -> None:
        """验证模型配置基本信息"""
        # 验证模型名称
        if not config.model_name or not config.model_name.strip():
            raise ModelConfigValidationException("model_name", config.model_name, "模型名称不能为空")

        if len(config.model_name) > 128:
            raise ModelConfigValidationException("model_name", config.model_name, "模型名称长度不能超过128个字符")

        # 验证模型名称格式
        if not re.match(r"^[a-zA-Z0-9_.-]+$", config.model_name):
            raise ModelConfigValidationException(
                "model_name",
                config.model_name,
                "模型名称只能包含字母、数字、下划线、点和连字符"
            )

        # 验证显示名称
        if not config.model_display_name or not config.model_display_name.strip():
            raise ModelConfigValidationException("model_display_name", config.model_display_name, "模型显示名称不能为空")

        if len(config.model_display_name) > 128:
            raise ModelConfigValidationException("model_display_name", config.model_display_name, "模型显示名称长度不能超过128个字符")

        # 验证模型类型
        valid_model_types = ["chat", "completion", "embedding", "image", "audio", "video"]
        if config.model_type not in valid_model_types:
            raise ModelConfigValidationException(
                "model_type",
                config.model_type,
                f"模型类型必须是以下之一: {', '.join(valid_model_types)}"
            )

    def _validate_model_parameters(self, config: ModelConfigEntity) -> None:
        """验证模型参数"""
        # 验证token限制
        if config.max_tokens is not None:
            if config.max_tokens < 1 or config.max_tokens > 100000:
                raise InvalidModelParametersException(
                    "max_tokens",
                    config.max_tokens,
                    "最大输出token数必须在1-100000之间"
                )

        if config.max_input_tokens is not None:
            if config.max_input_tokens < 1 or config.max_input_tokens > 100000:
                raise InvalidModelParametersException(
                    "max_input_tokens",
                    config.max_input_tokens,
                    "最大输入token数必须在1-100000之间"
                )

        # 验证temperature
        if config.temperature is not None:
            if config.temperature < 0 or config.temperature > 2:
                raise InvalidModelParametersException(
                    "temperature",
                    config.temperature,
                    "temperature必须在0-2之间"
                )

        # 验证自定义参数
        if config.model_params:
            self._validate_custom_model_params(config.model_params)

    def _validate_custom_model_params(self, params: dict[str, Any]) -> None:
        """验证自定义模型参数"""
        # 检查参数数量限制
        if len(params) > 20:
            raise InvalidModelParametersException(
                "model_params",
                params,
                "自定义参数数量不能超过20个"
            )

        # 验证参数键名和值
        for key, value in params.items():
            if not isinstance(key, str) or len(key) > 50:
                raise InvalidModelParametersException(
                    key,
                    value,
                    "参数键名必须是字符串且长度不能超过50个字符"
                )

            if not re.match(r"^[a-zA-Z0-9_]+$", key):
                raise InvalidModelParametersException(
                    key,
                    value,
                    "参数键名只能包含字母、数字和下划线"
                )

            # 验证参数值类型
            if not isinstance(value, str | int | float | bool | type(None)):
                raise InvalidModelParametersException(
                    key,
                    value,
                    "参数值必须是字符串、数字、布尔值或null"
                )

    def _validate_pricing_config(self, config: ModelConfigEntity) -> None:
        """验证定价配置"""
        if not config.pricing_config:
            return

        required_fields = ["input_price", "output_price", "currency"]
        for field in required_fields:
            if field not in config.pricing_config:
                raise ModelConfigValidationException(
                    "pricing_config",
                    config.pricing_config,
                    f"定价配置缺少必需字段: {field}"
                )

        # 验证价格为非负数
        for price_field in ["input_price", "output_price"]:
            price = config.pricing_config.get(price_field)
            if price is not None and (not isinstance(price, int | float) or price < 0):
                raise ModelConfigValidationException(
                    "pricing_config",
                    price,
                    f"{price_field}必须是非负数"
                )

        # 验证货币代码
        currency = config.pricing_config.get("currency")
        valid_currencies = ["USD", "EUR", "CNY", "JPY", "GBP"]
        if currency not in valid_currencies:
            raise ModelConfigValidationException(
                "pricing_config",
                currency,
                f"货币代码必须是以下之一: {', '.join(valid_currencies)}"
            )

    def _validate_chat_model_params(self, params: dict[str, Any]) -> dict[str, str]:
        """验证聊天模型参数"""
        suggestions = {}

        if "top_p" in params:
            top_p = params["top_p"]
            if not isinstance(top_p, int | float) or top_p < 0 or top_p > 1:
                raise InvalidModelParametersException("top_p", top_p, "top_p必须在0-1之间")
            if top_p > 0.95:
                suggestions["top_p"] = "top_p值过高可能导致输出质量下降"

        if "frequency_penalty" in params:
            penalty = params["frequency_penalty"]
            if not isinstance(penalty, int | float) or penalty < -2 or penalty > 2:
                raise InvalidModelParametersException("frequency_penalty", penalty, "frequency_penalty必须在-2到2之间")

        if "presence_penalty" in params:
            penalty = params["presence_penalty"]
            if not isinstance(penalty, int | float) or penalty < -2 or penalty > 2:
                raise InvalidModelParametersException("presence_penalty", penalty, "presence_penalty必须在-2到2之间")

        return suggestions

    def _validate_completion_model_params(self, params: dict[str, Any]) -> dict[str, str]:
        """验证文本补全模型参数"""
        suggestions = {}

        if "best_of" in params:
            best_of = params["best_of"]
            if not isinstance(best_of, int) or best_of < 1 or best_of > 20:
                raise InvalidModelParametersException("best_of", best_of, "best_of必须在1-20之间")
            if best_of > 5:
                suggestions["best_of"] = "best_of值过高会显著增加成本"

        return suggestions

    def _validate_embedding_model_params(self, params: dict[str, Any]) -> dict[str, str]:
        """验证嵌入模型参数"""
        suggestions = {}

        if "dimensions" in params:
            dimensions = params["dimensions"]
            if not isinstance(dimensions, int) or dimensions < 1 or dimensions > 3072:
                raise InvalidModelParametersException("dimensions", dimensions, "dimensions必须在1-3072之间")

        return suggestions

    def _validate_image_model_params(self, params: dict[str, Any]) -> dict[str, str]:
        """验证图像模型参数"""
        suggestions = {}

        if "size" in params:
            size = params["size"]
            valid_sizes = ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
            if size not in valid_sizes:
                raise InvalidModelParametersException("size", size, f"size必须是以下之一: {', '.join(valid_sizes)}")

        if "quality" in params:
            quality = params["quality"]
            if quality not in ["standard", "hd"]:
                raise InvalidModelParametersException("quality", quality, "quality必须是'standard'或'hd'")

        return suggestions

    def _create_updated_model_config(self, current_config: ModelConfigEntity,
                                   update_data: dict[str, Any]) -> ModelConfigEntity:
        """创建更新后的模型配置实体"""
        updated_config = ModelConfigEntity(
            config_id=current_config.config_id,
            provider_id=current_config.provider_id,
            model_name=update_data.get("model_name", current_config.model_name),
            model_display_name=update_data.get("model_display_name", current_config.model_display_name),
            model_type=update_data.get("model_type", current_config.model_type),
            model_params=update_data.get("model_params", current_config.model_params),
            max_tokens=update_data.get("max_tokens", current_config.max_tokens),
            max_input_tokens=update_data.get("max_input_tokens", current_config.max_input_tokens),
            temperature=update_data.get("temperature", current_config.temperature),
            pricing_config=update_data.get("pricing_config", current_config.pricing_config),
            is_active=update_data.get("is_active", current_config.is_active),
            created_by=current_config.created_by,
            created_at=current_config.created_at,
            updated_by=update_data.get("updated_by", current_config.updated_by),
            updated_at=current_config.updated_at,
            is_delete=current_config.is_delete
        )
        return updated_config
