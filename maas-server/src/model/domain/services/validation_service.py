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

"""业务规则验证服务"""

import re
from decimal import Decimal
from typing import Any
from urllib.parse import urlparse

from model.domain.exceptions import (
    BusinessRuleViolationException,
    InvalidModelParametersException,
    ModelConfigValidationException,
    ProviderValidationException,
)


class ValidationService:
    """业务规则验证服务"""

    @staticmethod
    def validate_provider_name(provider_name: str) -> None:
        """验证供应商名称"""
        if not provider_name or not provider_name.strip():
            raise ProviderValidationException("provider_name", provider_name, "供应商名称不能为空")

        if len(provider_name.strip()) > 64:
            raise ProviderValidationException("provider_name", provider_name, "供应商名称长度不能超过64个字符")

        # 供应商名称只能包含字母、数字、下划线和连字符
        if not re.match(r"^[a-zA-Z0-9_-]+$", provider_name.strip()):
            raise ProviderValidationException(
                "provider_name",
                provider_name,
                "供应商名称只能包含字母、数字、下划线和连字符"
            )

    @staticmethod
    def validate_provider_type(provider_type: str) -> None:
        """验证供应商类型"""
        if not provider_type or not provider_type.strip():
            raise ProviderValidationException("provider_type", provider_type, "供应商类型不能为空")

        if len(provider_type.strip()) > 64:
            raise ProviderValidationException("provider_type", provider_type, "供应商类型长度不能超过64个字符")

        # 定义支持的供应商类型
        valid_types = {
            "openai", "anthropic", "google", "azure", "aws", "huggingface",
            "cohere", "ai21", "replicate", "custom"
        }

        if provider_type.strip().lower() not in valid_types:
            raise ProviderValidationException(
                "provider_type",
                provider_type,
                f"不支持的供应商类型，支持的类型: {', '.join(valid_types)}"
            )

    @staticmethod
    def validate_base_url(base_url: str) -> None:
        """验证基础URL"""
        if not base_url or not base_url.strip():
            raise ProviderValidationException("base_url", base_url, "基础URL不能为空")

        if len(base_url.strip()) > 512:
            raise ProviderValidationException("base_url", base_url, "基础URL长度不能超过512个字符")

        try:
            parsed = urlparse(base_url.strip())
            if not parsed.scheme or not parsed.netloc:
                raise ProviderValidationException("base_url", base_url, "基础URL格式无效")

            if parsed.scheme not in ["http", "https"]:
                raise ProviderValidationException("base_url", base_url, "基础URL必须使用http或https协议")
        except Exception as e:
            raise ProviderValidationException("base_url", base_url, f"基础URL格式无效: {e!s}")

    @staticmethod
    def validate_display_name(display_name: str) -> None:
        """验证显示名称"""
        if not display_name or not display_name.strip():
            raise ProviderValidationException("display_name", display_name, "显示名称不能为空")

        if len(display_name.strip()) > 128:
            raise ProviderValidationException("display_name", display_name, "显示名称长度不能超过128个字符")

    @staticmethod
    def validate_description(description: str | None) -> None:
        """验证描述信息"""
        if description is not None and len(description) > 1000:
            raise ProviderValidationException("description", description, "描述信息长度不能超过1000个字符")

    @staticmethod
    def validate_api_key(api_key: str | None) -> None:
        """验证API密钥"""
        if api_key is not None:
            if len(api_key) > 512:
                raise ProviderValidationException("api_key", api_key, "API密钥长度不能超过512个字符")

            # API密钥不能包含明显的无效字符
            if any(char in api_key for char in ["\n", "\r", "\t"]):
                raise ProviderValidationException("api_key", api_key, "API密钥包含无效字符")

    @staticmethod
    def validate_additional_config(additional_config: dict[str, Any] | None) -> None:
        """验证额外配置"""
        if additional_config is not None:
            if not isinstance(additional_config, dict):
                raise ProviderValidationException(
                    "additional_config",
                    additional_config,
                    "额外配置必须是字典类型"
                )

            # 检查配置大小（序列化后不超过10KB）
            import json
            try:
                config_str = json.dumps(additional_config)
                if len(config_str.encode("utf-8")) > 10240:  # 10KB
                    raise ProviderValidationException(
                        "additional_config",
                        additional_config,
                        "额外配置大小不能超过10KB"
                    )
            except (TypeError, ValueError) as e:
                raise ProviderValidationException(
                    "additional_config",
                    additional_config,
                    f"额外配置序列化失败: {e!s}"
                )

    @staticmethod
    def validate_model_name(model_name: str) -> None:
        """验证模型名称"""
        if not model_name or not model_name.strip():
            raise ModelConfigValidationException("model_name", model_name, "模型名称不能为空")

        if len(model_name.strip()) > 128:
            raise ModelConfigValidationException("model_name", model_name, "模型名称长度不能超过128个字符")

        # 模型名称只能包含字母、数字、下划线、连字符和点号
        if not re.match(r"^[a-zA-Z0-9_.-]+$", model_name.strip()):
            raise ModelConfigValidationException(
                "model_name",
                model_name,
                "模型名称只能包含字母、数字、下划线、连字符和点号"
            )

    @staticmethod
    def validate_model_display_name(model_display_name: str) -> None:
        """验证模型显示名称"""
        if not model_display_name or not model_display_name.strip():
            raise ModelConfigValidationException("model_display_name", model_display_name, "模型显示名称不能为空")

        if len(model_display_name.strip()) > 128:
            raise ModelConfigValidationException(
                "model_display_name",
                model_display_name,
                "模型显示名称长度不能超过128个字符"
            )

    @staticmethod
    def validate_model_type(model_type: str) -> None:
        """验证模型类型"""
        if not model_type or not model_type.strip():
            raise ModelConfigValidationException("model_type", model_type, "模型类型不能为空")

        if len(model_type.strip()) > 64:
            raise ModelConfigValidationException("model_type", model_type, "模型类型长度不能超过64个字符")

        # 定义支持的模型类型
        valid_types = {
            "chat", "completion", "embedding", "image", "audio", "video",
            "multimodal", "code", "fine-tuning", "custom"
        }

        if model_type.strip().lower() not in valid_types:
            raise ModelConfigValidationException(
                "model_type",
                model_type,
                f"不支持的模型类型，支持的类型: {', '.join(valid_types)}"
            )

    @staticmethod
    def validate_token_limits(max_tokens: int | None, max_input_tokens: int | None) -> None:
        """验证token限制"""
        if max_tokens is not None:
            if max_tokens <= 0:
                raise InvalidModelParametersException("max_tokens", max_tokens, "最大token数必须大于0")

            if max_tokens > 100000:
                raise InvalidModelParametersException("max_tokens", max_tokens, "最大token数不能超过100000")

        if max_input_tokens is not None:
            if max_input_tokens <= 0:
                raise InvalidModelParametersException("max_input_tokens", max_input_tokens, "最大输入token数必须大于0")

            if max_input_tokens > 100000:
                raise InvalidModelParametersException("max_input_tokens", max_input_tokens, "最大输入token数不能超过100000")

        # 验证输入token不能大于最大token
        if max_tokens is not None and max_input_tokens is not None:
            if max_input_tokens > max_tokens:
                raise InvalidModelParametersException(
                    "max_input_tokens",
                    max_input_tokens,
                    "最大输入token数不能大于最大token数"
                )

    @staticmethod
    def validate_temperature(temperature: Decimal | None) -> None:
        """验证温度参数"""
        if temperature is not None:
            if temperature < 0 or temperature > 2:
                raise InvalidModelParametersException("temperature", temperature, "温度参数必须在0-2之间")

    @staticmethod
    def validate_model_params(model_params: dict[str, Any] | None) -> None:
        """验证模型参数"""
        if model_params is not None:
            if not isinstance(model_params, dict):
                raise InvalidModelParametersException(
                    "model_params",
                    model_params,
                    "模型参数必须是字典类型"
                )

            # 检查参数大小（序列化后不超过50KB）
            import json
            try:
                params_str = json.dumps(model_params)
                if len(params_str.encode("utf-8")) > 51200:  # 50KB
                    raise InvalidModelParametersException(
                        "model_params",
                        model_params,
                        "模型参数大小不能超过50KB"
                    )
            except (TypeError, ValueError) as e:
                raise InvalidModelParametersException(
                    "model_params",
                    model_params,
                    f"模型参数序列化失败: {e!s}"
                )

    @staticmethod
    def validate_pricing_config(pricing_config: dict[str, Any] | None) -> None:
        """验证定价配置"""
        if pricing_config is not None:
            if not isinstance(pricing_config, dict):
                raise InvalidModelParametersException(
                    "pricing_config",
                    pricing_config,
                    "定价配置必须是字典类型"
                )

            # 验证必要的定价字段
            if "input_price_per_1k" in pricing_config:
                price = pricing_config["input_price_per_1k"]
                if not isinstance(price, int | float | Decimal) or price < 0:
                    raise InvalidModelParametersException(
                        "pricing_config.input_price_per_1k",
                        price,
                        "输入价格必须是非负数"
                    )

            if "output_price_per_1k" in pricing_config:
                price = pricing_config["output_price_per_1k"]
                if not isinstance(price, int | float | Decimal) or price < 0:
                    raise InvalidModelParametersException(
                        "pricing_config.output_price_per_1k",
                        price,
                        "输出价格必须是非负数"
                    )

            # 检查配置大小
            import json
            try:
                config_str = json.dumps(pricing_config, default=str)
                if len(config_str.encode("utf-8")) > 10240:  # 10KB
                    raise InvalidModelParametersException(
                        "pricing_config",
                        pricing_config,
                        "定价配置大小不能超过10KB"
                    )
            except (TypeError, ValueError) as e:
                raise InvalidModelParametersException(
                    "pricing_config",
                    pricing_config,
                    f"定价配置序列化失败: {e!s}"
                )

    @staticmethod
    def validate_business_rules(provider_id: int, model_name: str, existing_configs: list) -> None:
        """验证业务规则"""
        # 检查同一供应商下模型名称的唯一性
        for config in existing_configs:
            if config.model_name == model_name and not config.is_delete:
                raise BusinessRuleViolationException(
                    "unique_model_name_per_provider",
                    f"供应商 {provider_id} 下已存在名为 '{model_name}' 的模型配置"
                )
