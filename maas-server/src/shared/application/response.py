"""共享应用层 - 响应模型"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    success: bool = True
    data: T | None = None
    message: str = "操作成功"
    code: int = 200
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None


class ErrorDetail(BaseModel):
    """错误详情"""
    field: str | None = None
    message: str
    code: str | None = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    error: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(ge=1, description="当前页码")
    limit: int = Field(ge=1, le=100, description="每页数量")
    total: int = Field(ge=0, description="总记录数")
    pages: int = Field(ge=0, description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: list[T]
    pagination: PaginationMeta


class SuccessResponse(BaseResponse[None]):
    """成功响应（无数据）"""
    pass


class CreatedResponse(BaseResponse[T]):
    """创建成功响应"""
    code: int = 201
    message: str = "创建成功"


class UpdatedResponse(BaseResponse[T]):
    """更新成功响应"""
    message: str = "更新成功"


class DeletedResponse(BaseResponse[None]):
    """删除成功响应"""
    message: str = "删除成功"


# 常用响应类型
class IdResponse(BaseModel):
    """ID响应"""
    id: UUID


class StatusResponse(BaseModel):
    """状态响应"""
    status: str
    message: str | None = None


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict[str, str] = Field(default_factory=dict)


class MetricsResponse(BaseModel):
    """指标响应"""
    metrics: dict[str, Any]
    collected_at: datetime = Field(default_factory=datetime.utcnow)


# 响应构建器
class ApiResponse(BaseModel, Generic[T]):
    """API响应模型"""
    success: bool = True
    data: T | None = None
    message: str = "操作成功"
    code: int = 200
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None

    @classmethod
    def success_response(
        cls,
        data: T | None = None,
        message: str = "操作成功",
        code: int = 200
    ) -> "ApiResponse[T]":
        """构建成功响应"""
        return cls(
            success=True,
            data=data,
            message=message,
            code=code
        )

    @classmethod
    def error_response(
        cls,
        message: str,
        code: int = 400,
        data: T | None = None
    ) -> "ApiResponse[T]":
        """构建错误响应"""
        return cls(
            success=False,
            data=data,
            message=message,
            code=code
        )


# 响应构建器
def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200
) -> BaseResponse:
    """构建成功响应"""
    return BaseResponse(
        success=True,
        data=data,
        message=message,
        code=code
    )


def error_response(
    message: str,
    code: str,
    details: list[ErrorDetail] | None = None,
    status_code: int = 400
) -> ErrorResponse:
    """构建错误响应"""
    return ErrorResponse(
        error={
            "code": code,
            "message": message,
            "details": details or []
        }
    )


def paginated_response(
    items: list[Any],
    page: int,
    limit: int,
    total: int
) -> BaseResponse[PaginatedResponse]:
    """构建分页响应"""
    pages = (total + limit - 1) // limit

    pagination = PaginationMeta(
        page=page,
        limit=limit,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )

    return BaseResponse(
        data=PaginatedResponse(
            items=items,
            pagination=pagination
        )
    )
