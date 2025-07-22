"""共享应用层 - 响应模型"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


# 响应构建器
class ApiResponse(BaseModel, Generic[T]):
    """API响应模型"""
    success: bool = True
    data: T | None = None
    message: str = "操作成功"
    code: int = 200
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # request_id: str | None = None

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
                  
    @classmethod
    def paginated_response(
        cls,
        items: list[T],
        total: int,
        message: str = "操作成功",
        code: int = 200
    ) -> "ApiResponse[T]":
        """构建分页响应"""
        
        return cls(
            success=False,
            data=items,
            total=total,
            message=message,
            code=code
        )

