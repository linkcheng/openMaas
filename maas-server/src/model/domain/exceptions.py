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

"""模型供应商领域异常定义"""

from typing import Any

from shared.domain.base import DomainException


class ProviderDomainException(DomainException):
    """供应商领域异常基类"""
    pass


class ProviderNotFoundException(ProviderDomainException):
    """供应商未找到异常"""

    def __init__(self, provider_id: int):
        super().__init__(f"供应商 {provider_id} 未找到", "PROVIDER_NOT_FOUND")
        self.provider_id = provider_id


class ProviderAlreadyExistsException(ProviderDomainException):
    """供应商已存在异常"""

    def __init__(self, provider_name: str):
        super().__init__(f"供应商 '{provider_name}' 已存在", "PROVIDER_ALREADY_EXISTS")
        self.provider_name = provider_name


class ProviderInactiveException(ProviderDomainException):
    """供应商未激活异常"""

    def __init__(self, provider_id: int):
        super().__init__(f"供应商 {provider_id} 未激活", "PROVIDER_INACTIVE")
        self.provider_id = provider_id


class ProviderHasActiveModelsException(ProviderDomainException):
    """供应商有活跃模型配置异常"""

    def __init__(self, provider_id: int, active_model_count: int):
        super().__init__(
            f"供应商 {provider_id} 有 {active_model_count} 个活跃的模型配置，无法删除",
            "PROVIDER_HAS_ACTIVE_MODELS"
        )
        self.provider_id = provider_id
        self.active_model_count = active_model_count


class ModelConfigDomainException(DomainException):
    """模型配置领域异常基类"""
    pass


class ModelConfigNotFoundException(ModelConfigDomainException):
    """模型配置未找到异常"""

    def __init__(self, config_id: int):
        super().__init__(f"模型配置 {config_id} 未找到", "MODEL_CONFIG_NOT_FOUND")
        self.config_id = config_id


class ModelConfigAlreadyExistsException(ModelConfigDomainException):
    """模型配置已存在异常"""

    def __init__(self, provider_id: int, model_name: str):
        super().__init__(
            f"供应商 {provider_id} 的模型 '{model_name}' 配置已存在",
            "MODEL_CONFIG_ALREADY_EXISTS"
        )
        self.provider_id = provider_id
        self.model_name = model_name


class ModelConfigInactiveException(ModelConfigDomainException):
    """模型配置未激活异常"""

    def __init__(self, config_id: int):
        super().__init__(f"模型配置 {config_id} 未激活", "MODEL_CONFIG_INACTIVE")
        self.config_id = config_id


class InvalidModelParametersException(ModelConfigDomainException):
    """无效模型参数异常"""

    def __init__(self, parameter_name: str, parameter_value: Any, reason: str):
        super().__init__(
            f"模型参数 '{parameter_name}' 值 '{parameter_value}' 无效: {reason}",
            "INVALID_MODEL_PARAMETERS"
        )
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value
        self.reason = reason


class ProviderValidationException(ProviderDomainException):
    """供应商验证异常"""

    def __init__(self, field_name: str, field_value: Any, reason: str):
        super().__init__(
            f"供应商字段 '{field_name}' 值 '{field_value}' 验证失败: {reason}",
            "PROVIDER_VALIDATION_ERROR"
        )
        self.field_name = field_name
        self.field_value = field_value
        self.reason = reason


class ModelConfigValidationException(ModelConfigDomainException):
    """模型配置验证异常"""

    def __init__(self, field_name: str, field_value: Any, reason: str):
        super().__init__(
            f"模型配置字段 '{field_name}' 值 '{field_value}' 验证失败: {reason}",
            "MODEL_CONFIG_VALIDATION_ERROR"
        )
        self.field_name = field_name
        self.field_value = field_value
        self.reason = reason


class ConcurrentUpdateException(DomainException):
    """并发更新异常"""

    def __init__(self, resource_type: str, resource_id: int):
        super().__init__(
            f"{resource_type} {resource_id} 已被其他用户修改，请刷新后重试",
            "CONCURRENT_UPDATE_CONFLICT"
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class BusinessRuleViolationException(DomainException):
    """业务规则违反异常"""

    def __init__(self, rule_name: str, description: str):
        super().__init__(f"业务规则 '{rule_name}' 违反: {description}", "BUSINESS_RULE_VIOLATION")
        self.rule_name = rule_name
        self.description = description
