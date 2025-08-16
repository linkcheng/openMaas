from datetime import datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, validator

T = TypeVar("T")

class CreateProviderRequest(BaseModel):
    """创建供应商请求模型"""
    provider_name: str = Field(
        min_length=1,
        max_length=64,
        description="供应商名称，必须唯一",
        example="openai"
    )
    provider_type: str = Field(
        min_length=1,
        max_length=64,
        description="供应商类型",
        example="openai"
    )
    display_name: str = Field(
        min_length=1,
        max_length=128,
        description="显示名称",
        example="OpenAI"
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="描述信息",
        example="OpenAI GPT模型供应商"
    )
    base_url: str = Field(
        min_length=1,
        max_length=512,
        description="基础URL",
        example="https://api.openai.com/v1"
    )
    api_key: str | None = Field(
        None,
        max_length=512,
        description="API密钥"
    )
    additional_config: dict[str, Any] | None = Field(
        None,
        description="额外配置参数"
    )
    is_active: bool = Field(
        True,
        description="是否启用"
    )

    @validator("provider_name")
    def validate_provider_name(cls, v):
        if not v or not v.strip():
            raise ValueError("供应商名称不能为空")
        
        # 安全性检查
        from model.infrastructure.security import SecurityValidator
        if not SecurityValidator.validate_input_safety(v):
            raise ValueError("供应商名称包含不安全字符")
        if not SecurityValidator.validate_sql_injection(v):
            raise ValueError("供应商名称包含潜在的注入攻击字符")
        
        return SecurityValidator.sanitize_string(v.strip())

    @validator("base_url")
    def validate_base_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("基础URL必须以http://或https://开头")
        
        # 安全性检查
        from model.infrastructure.security import SecurityValidator
        if not SecurityValidator.validate_url(v):
            raise ValueError("URL格式不安全或无效")
        
        return v

    @validator("api_key")
    def validate_api_key(cls, v):
        if v is None:
            return v
        
        # 安全性检查
        from model.infrastructure.security import SecurityValidator
        if not SecurityValidator.validate_api_key_format(v):
            raise ValueError("API密钥格式不安全或无效")
        
        return v

    @validator("additional_config")
    def validate_additional_config(cls, v):
        if v is None:
            return v
        
        # 安全性检查
        from model.infrastructure.security import SecurityValidator
        if not SecurityValidator.validate_json_config(v):
            raise ValueError("额外配置包含不安全内容")
        
        return v

    @validator("description")
    def validate_description(cls, v):
        if v is None:
            return v
        
        # 安全性检查
        from model.infrastructure.security import SecurityValidator
        if not SecurityValidator.validate_input_safety(v):
            raise ValueError("描述包含不安全字符")
        
        return SecurityValidator.sanitize_string(v)

    class Config:
        json_schema_extra = {
            "example": {
                "provider_name": "openai",
                "provider_type": "openai",
                "display_name": "OpenAI",
                "description": "OpenAI GPT模型供应商",
                "base_url": "https://api.openai.com/v1",
                "api_key": "sk-xxx",
                "additional_config": {
                    "organization": "org-xxx"
                },
                "is_active": True
            }
        }


class UpdateProviderRequest(BaseModel):
    """更新供应商请求模型"""
    provider_name: str | None = Field(
        None,
        min_length=1,
        max_length=64,
        description="供应商名称"
    )
    provider_type: str | None = Field(
        None,
        min_length=1,
        max_length=64,
        description="供应商类型"
    )
    display_name: str | None = Field(
        None,
        min_length=1,
        max_length=128,
        description="显示名称"
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="描述信息"
    )
    base_url: str | None = Field(
        None,
        min_length=1,
        max_length=512,
        description="基础URL"
    )
    api_key: str | None = Field(
        None,
        max_length=512,
        description="API密钥"
    )
    additional_config: dict[str, Any] | None = Field(
        None,
        description="额外配置参数"
    )
    is_active: bool | None = Field(
        None,
        description="是否启用"
    )

    @validator("provider_name")
    def validate_provider_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("供应商名称不能为空")
        return v.strip() if v else v

    @validator("base_url")
    def validate_base_url(cls, v):
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("基础URL必须以http://或https://开头")
        return v


class ProviderResponse(BaseModel):
    """供应商响应模型"""
    provider_id: int = Field( description="供应商ID")
    provider_name: str = Field( description="供应商名称")
    provider_type: str = Field( description="供应商类型")
    display_name: str = Field( description="显示名称")
    description: str | None = Field(None, description="描述信息")
    base_url: str = Field( description="基础URL")
    additional_config: dict[str, Any] | None = Field(None, description="额外配置参数")
    is_active: bool = Field( description="是否启用")
    created_by: str = Field( description="创建人")
    created_at: datetime = Field( description="创建时间")
    updated_by: str = Field( description="更新人")
    updated_at: datetime = Field( description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "provider_id": 1,
                "provider_name": "openai",
                "provider_type": "openai",
                "display_name": "OpenAI",
                "description": "OpenAI GPT模型供应商",
                "base_url": "https://api.openai.com/v1",
                "additional_config": {
                    "organization": "org-xxx"
                },
                "is_active": True,
                "created_by": "admin",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_by": "admin",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class ListProvidersParams(BaseModel):
    """查询供应商列表参数模型"""
    page: int = Field(
        1,
        ge=1,
        description="页码，从1开始"
    )
    size: int = Field(
        20,
        ge=1,
        le=100,
        description="每页大小，最大100"
    )
    provider_type: str | None = Field(
        None,
        description="供应商类型过滤"
    )
    is_active: bool | None = Field(
        None,
        description="是否启用过滤"
    )
    sort_by: str | None = Field(
        "created_at",
        description="排序字段"
    )
    sort_order: str | None = Field(
        "desc",
        pattern="^(asc|desc)$",
        description="排序方向：asc或desc"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20,
                "provider_type": "openai",
                "is_active": True,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


class SearchProvidersParams(BaseModel):
    """搜索供应商参数模型"""
    page: int = Field(
        1,
        ge=1,
        description="页码，从1开始"
    )
    size: int = Field(
        20,
        ge=1,
        le=100,
        description="每页大小，最大100"
    )
    keyword: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="搜索关键词，支持供应商名称和显示名称模糊搜索"
    )
    provider_type: str | None = Field(
        None,
        description="供应商类型过滤"
    )
    is_active: bool | None = Field(
        None,
        description="是否启用过滤"
    )

    @validator("keyword")
    def validate_keyword(cls, v):
        if v is not None and not v.strip():
            raise ValueError("搜索关键词不能为空字符串")
        return v.strip() if v else v

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20,
                "keyword": "openai",
                "provider_type": "openai",
                "is_active": True
            }
        }


class PaginatedProviderResponse(BaseModel):
    """分页供应商响应模型"""
    items: list[ProviderResponse] = Field( description="供应商列表")
    total: int = Field( description="总数量")
    page: int = Field( description="当前页码")
    size: int = Field( description="每页大小")
    pages: int = Field( description="总页数")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "provider_id": 1,
                        "provider_name": "openai",
                        "provider_type": "openai",
                        "display_name": "OpenAI",
                        "description": "OpenAI GPT模型供应商",
                        "base_url": "https://api.openai.com/v1",
                        "additional_config": {},
                        "is_active": True,
                        "created_by": "admin",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_by": "admin",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 20,
                "pages": 1
            }
        }

class CreateModelConfigRequest(BaseModel):
    """创建模型配置请求模型"""
    model_name: str = Field(
        min_length=1,
        max_length=128,
        description="模型名称，在同一供应商下必须唯一",
        example="gpt-4"
    )
    model_display_name: str = Field(
        min_length=1,
        max_length=128,
        description="模型显示名称",
        example="GPT-4"
    )
    model_type: str = Field(
        min_length=1,
        max_length=64,
        description="模型类型",
        example="chat"
    )
    model_params: dict[str, Any] | None = Field(
        None,
        description="模型参数配置"
    )
    max_tokens: int | None = Field(
        4096,
        ge=1,
        le=100000,
        description="最大token数"
    )
    max_input_tokens: int | None = Field(
        3072,
        ge=1,
        le=100000,
        description="最大输入token数"
    )
    temperature: Decimal | None = Field(
        Decimal("0.70"),
        ge=0,
        le=2,
        description="温度参数，控制输出随机性"
    )
    pricing_config: dict[str, Any] | None = Field(
        None,
        description="定价配置"
    )
    is_active: bool = Field(
        True,
        description="是否启用"
    )

    @validator("model_name")
    def validate_model_name(cls, v):
        if not v or not v.strip():
            raise ValueError("模型名称不能为空")
        return v.strip()

    @validator("max_input_tokens", "max_tokens")
    def validate_token_limits(cls, v, values):
        if v is not None and v <= 0:
            raise ValueError("token数量必须大于0")
        # 验证输入token不能大于最大token
        if "max_tokens" in values and values["max_tokens"] is not None:
            if v is not None and v > values["max_tokens"]:
                raise ValueError("最大输入token数不能大于最大token数")
        return v

    @validator("temperature")
    def validate_temperature(cls, v):
        if v is not None and (v < 0 or v > 2):
            raise ValueError("温度参数必须在0-2之间")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "gpt-4",
                "model_display_name": "GPT-4",
                "model_type": "chat",
                "model_params": {
                    "supports_functions": True,
                    "supports_vision": False
                },
                "max_tokens": 4096,
                "max_input_tokens": 3072,
                "temperature": 0.7,
                "pricing_config": {
                    "input_price_per_1k": 0.03,
                    "output_price_per_1k": 0.06,
                    "currency": "USD"
                },
                "is_active": True
            }
        }


class UpdateModelConfigRequest(BaseModel):
    """更新模型配置请求模型"""
    model_name: str | None = Field(
        None,
        min_length=1,
        max_length=128,
        description="模型名称"
    )
    model_display_name: str | None = Field(
        None,
        min_length=1,
        max_length=128,
        description="模型显示名称"
    )
    model_type: str | None = Field(
        None,
        min_length=1,
        max_length=64,
        description="模型类型"
    )
    model_params: dict[str, Any] | None = Field(
        None,
        description="模型参数配置"
    )
    max_tokens: int | None = Field(
        None,
        ge=1,
        le=100000,
        description="最大token数"
    )
    max_input_tokens: int | None = Field(
        None,
        ge=1,
        le=100000,
        description="最大输入token数"
    )
    temperature: Decimal | None = Field(
        None,
        ge=0,
        le=2,
        description="温度参数"
    )
    pricing_config: dict[str, Any] | None = Field(
        None,
        description="定价配置"
    )
    is_active: bool | None = Field(
        None,
        description="是否启用"
    )

    @validator("model_name")
    def validate_model_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("模型名称不能为空")
        return v.strip() if v else v

    @validator("max_input_tokens", "max_tokens")
    def validate_token_limits(cls, v):
        if v is not None and v <= 0:
            raise ValueError("token数量必须大于0")
        return v

    @validator("temperature")
    def validate_temperature(cls, v):
        if v is not None and (v < 0 or v > 2):
            raise ValueError("温度参数必须在0-2之间")
        return v


class ModelConfigResponse(BaseModel):
    """模型配置响应模型"""
    config_id: int = Field( description="配置ID")
    provider_id: int = Field( description="供应商ID")
    model_name: str = Field( description="模型名称")
    model_display_name: str = Field( description="模型显示名称")
    model_type: str = Field( description="模型类型")
    model_params: dict[str, Any] | None = Field(None, description="模型参数配置")
    max_tokens: int | None = Field(None, description="最大token数")
    max_input_tokens: int | None = Field(None, description="最大输入token数")
    temperature: Decimal | None = Field(None, description="温度参数")
    pricing_config: dict[str, Any] | None = Field(None, description="定价配置")
    is_active: bool = Field( description="是否启用")
    created_by: str = Field( description="创建人")
    created_at: datetime = Field( description="创建时间")
    updated_by: str = Field( description="更新人")
    updated_at: datetime = Field( description="更新时间")
    provider: ProviderResponse | None = Field(None, description="关联的供应商信息")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "config_id": 1,
                "provider_id": 1,
                "model_name": "gpt-4",
                "model_display_name": "GPT-4",
                "model_type": "chat",
                "model_params": {
                    "supports_functions": True,
                    "supports_vision": False
                },
                "max_tokens": 4096,
                "max_input_tokens": 3072,
                "temperature": 0.7,
                "pricing_config": {
                    "input_price_per_1k": 0.03,
                    "output_price_per_1k": 0.06,
                    "currency": "USD"
                },
                "is_active": True,
                "created_by": "admin",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_by": "admin",
                "updated_at": "2024-01-01T00:00:00Z",
                "provider": {
                    "provider_id": 1,
                    "provider_name": "openai",
                    "display_name": "OpenAI"
                }
            }
        }


class ListModelConfigsParams(BaseModel):
    """查询模型配置列表参数模型"""
    page: int = Field(
        1,
        ge=1,
        description="页码，从1开始"
    )
    size: int = Field(
        20,
        ge=1,
        le=100,
        description="每页大小，最大100"
    )
    provider_id: int | None = Field(
        None,
        description="供应商ID过滤"
    )
    model_type: str | None = Field(
        None,
        description="模型类型过滤"
    )
    is_active: bool | None = Field(
        None,
        description="是否启用过滤"
    )
    keyword: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="搜索关键词，支持模型名称和显示名称模糊搜索"
    )
    sort_by: str | None = Field(
        "created_at",
        description="排序字段"
    )
    sort_order: str | None = Field(
        "desc",
        pattern="^(asc|desc)$",
        description="排序方向：asc或desc"
    )

    @validator("keyword")
    def validate_keyword(cls, v):
        if v is not None and not v.strip():
            raise ValueError("搜索关键词不能为空字符串")
        return v.strip() if v else v

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20,
                "provider_id": 1,
                "model_type": "chat",
                "is_active": True,
                "keyword": "gpt",
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


class PaginatedModelConfigResponse(BaseModel):
    """分页模型配置响应模型"""
    items: list[ModelConfigResponse] = Field( description="模型配置列表")
    total: int = Field( description="总数量")
    page: int = Field( description="当前页码")
    size: int = Field( description="每页大小")
    pages: int = Field( description="总页数")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "config_id": 1,
                        "provider_id": 1,
                        "model_name": "gpt-4",
                        "model_display_name": "GPT-4",
                        "model_type": "chat",
                        "model_params": {},
                        "max_tokens": 4096,
                        "max_input_tokens": 3072,
                        "temperature": 0.7,
                        "pricing_config": {},
                        "is_active": True,
                        "created_by": "admin",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_by": "admin",
                        "updated_at": "2024-01-01T00:00:00Z",
                        "provider": None
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 20,
                "pages": 1
            }
        }

class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应模型"""
    items: list[T] = Field( description="数据列表")
    total: int = Field( ge=0, description="总数量")
    page: int = Field( ge=1, description="当前页码")
    size: int = Field( ge=1, le=100, description="每页大小")
    pages: int = Field( ge=0, description="总页数")

    @validator("pages", pre=False, always=True)
    def calculate_pages(cls, v, values):
        """计算总页数"""
        if "total" in values and "size" in values:
            total = values["total"]
            size = values["size"]
            if size > 0:
                return (total + size - 1) // size  # 向上取整
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            }
        }

    @classmethod
    def create(cls, items: list[T], total: int, page: int, size: int) -> "PaginatedResponse[T]":
        """创建分页响应的便捷方法"""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class MessageResponse(BaseModel):
    """操作结果消息响应模型"""
    message: str = Field( description="操作结果消息")
    success: bool = Field(True, description="操作是否成功")
    data: dict[str, Any] | None = Field(None, description="附加数据")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "操作成功",
                "success": True,
                "data": {
                    "affected_rows": 1
                }
            }
        }

    @classmethod
    def success_message(cls, message: str = "操作成功", data: dict[str, Any] | None = None) -> "MessageResponse":
        """创建成功消息的便捷方法"""
        return cls(message=message, success=True, data=data)

    @classmethod
    def error_message(cls, message: str = "操作失败", data: dict[str, Any] | None = None) -> "MessageResponse":
        """创建错误消息的便捷方法"""
        return cls(message=message, success=False, data=data)


class PaginationMeta(BaseModel):
    """分页元数据模型"""
    total: int = Field( ge=0, description="总数量")
    page: int = Field( ge=1, description="当前页码")
    size: int = Field( ge=1, le=100, description="每页大小")
    pages: int = Field( ge=0, description="总页数")
    has_prev: bool = Field( description="是否有上一页")
    has_next: bool = Field( description="是否有下一页")
    prev_page: int | None = Field(None, description="上一页页码")
    next_page: int | None = Field(None, description="下一页页码")

    @validator("pages", pre=False, always=True)
    def calculate_pages(cls, v, values):
        """计算总页数"""
        if "total" in values and "size" in values:
            total = values["total"]
            size = values["size"]
            if size > 0:
                return (total + size - 1) // size
        return v

    @validator("has_prev", pre=False, always=True)
    def calculate_has_prev(cls, v, values):
        """计算是否有上一页"""
        if "page" in values:
            return values["page"] > 1
        return False

    @validator("has_next", pre=False, always=True)
    def calculate_has_next(cls, v, values):
        """计算是否有下一页"""
        if "page" in values and "pages" in values:
            return values["page"] < values["pages"]
        return False

    @validator("prev_page", pre=False, always=True)
    def calculate_prev_page(cls, v, values):
        """计算上一页页码"""
        if "page" in values and values["page"] > 1:
            return values["page"] - 1
        return None

    @validator("next_page", pre=False, always=True)
    def calculate_next_page(cls, v, values):
        """计算下一页页码"""
        if "page" in values and "pages" in values and values["page"] < values["pages"]:
            return values["page"] + 1
        return None

    @classmethod
    def create(cls, total: int, page: int, size: int) -> "PaginationMeta":
        """创建分页元数据的便捷方法"""
        pages = (total + size - 1) // size if size > 0 else 0
        has_prev = page > 1
        has_next = page < pages
        prev_page = page - 1 if has_prev else None
        next_page = page + 1 if has_next else None

        return cls(
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_prev=has_prev,
            has_next=has_next,
            prev_page=prev_page,
            next_page=next_page
        )

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 2,
                "size": 20,
                "pages": 5,
                "has_prev": True,
                "has_next": True,
                "prev_page": 1,
                "next_page": 3
            }
        }


class BaseListParams(BaseModel):
    """基础列表查询参数模型"""
    page: int = Field(
        1,
        ge=1,
        description="页码，从1开始"
    )
    size: int = Field(
        20,
        ge=1,
        le=100,
        description="每页大小，最大100"
    )
    sort_by: str | None = Field(
        "created_at",
        description="排序字段"
    )
    sort_order: str | None = Field(
        "desc",
        pattern="^(asc|desc)$",
        description="排序方向：asc或desc"
    )

    def get_offset(self) -> int:
        """获取数据库查询偏移量"""
        return (self.page - 1) * self.size

    def get_limit(self) -> int:
        """获取数据库查询限制数量"""
        return self.size

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


# 为了向后兼容，保留原有的类型别名
PaginatedProviderResponse = PaginatedResponse[ProviderResponse]
PaginatedModelConfigResponse = PaginatedResponse[ModelConfigResponse]
