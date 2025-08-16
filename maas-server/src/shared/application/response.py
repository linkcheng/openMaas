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

"""共享应用层 - 响应模型"""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """分页元数据"""
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")

    @classmethod
    def create(cls, total: int, page: int, size: int) -> "PaginationMeta":
        """创建分页元数据"""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(total=total, page=page, size=size, pages=pages)


class PaginatedData(BaseModel, Generic[T]):
    """分页数据模型"""
    items: list[T] = Field(..., description="数据列表")
    pagination: PaginationMeta = Field(..., description="分页信息")


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
        page: int,
        size: int,
        message: str = "操作成功",
        code: int = 200
    ) -> "ApiResponse[PaginatedData[T]]":
        """构建分页响应"""
        pagination_meta = PaginationMeta.create(total=total, page=page, size=size)
        paginated_data = PaginatedData(items=items, pagination=pagination_meta)

        return cls(
            success=True,
            data=paginated_data,
            message=message,
            code=code
        )

