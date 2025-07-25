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

审计日志应用层数据模型
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from audit.domain.models import ActionType, AuditResult, ResourceType


class CreateAuditLogRequest(BaseModel):
    """创建审计日志请求"""

    user_id: UUID | None = Field(None, description="操作用户ID")
    username: str | None = Field(None, description="操作用户名")
    action: ActionType = Field(..., description="操作类型")
    resource_type: ResourceType | None = Field(None, description="资源类型")
    resource_id: UUID | None = Field(None, description="资源ID")
    description: str = Field(..., description="操作描述")
    ip_address: str | None = Field(None, description="客户端IP地址")
    user_agent: str | None = Field(None, description="用户代理")
    request_id: str | None = Field(None, description="请求ID")
    result: AuditResult = Field(AuditResult.SUCCESS, description="操作结果")
    error_message: str | None = Field(None, description="错误信息")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class AuditLogQueryRequest(BaseModel):
    """查询审计日志请求"""

    user_id: UUID | None = Field(None, description="用户ID")
    username: str | None = Field(None, description="用户名")
    action: ActionType | None = Field(None, description="操作类型")
    resource_type: ResourceType | None = Field(None, description="资源类型")
    resource_id: UUID | None = Field(None, description="资源ID")
    result: AuditResult | None = Field(None, description="操作结果")
    ip_address: str | None = Field(None, description="IP地址")
    start_time: datetime | None = Field(None, description="开始时间")
    end_time: datetime | None = Field(None, description="结束时间")
    search_keyword: str | None = Field(None, description="搜索关键词")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小")
    order_by: str = Field("created_at", description="排序字段")
    order_desc: bool = Field(True, description="是否降序")


class AuditLogResponse(BaseModel):
    """审计日志响应"""

    audit_log_id: UUID = Field(..., description="审计日志ID")
    user_id: UUID | None = Field(None, description="用户ID")
    username: str | None = Field(None, description="用户名")
    action: ActionType = Field(..., description="操作类型")
    resource_type: ResourceType | None = Field(None, description="资源类型")
    resource_id: UUID | None = Field(None, description="资源ID")
    description: str = Field(..., description="操作描述")
    ip_address: str | None = Field(None, description="IP地址")
    user_agent: str | None = Field(None, description="用户代理")
    request_id: str | None = Field(None, description="请求ID")
    result: AuditResult = Field(..., description="操作结果")
    error_message: str | None = Field(None, description="错误信息")
    metadata: dict[str, Any] = Field(..., description="元数据")
    created_at: datetime = Field(..., description="创建时间")

    # 计算属性
    operation_summary: str = Field(..., description="操作摘要")
    is_successful: bool = Field(..., description="是否成功")
    is_system_operation: bool = Field(..., description="是否系统操作")


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""

    items: list[AuditLogResponse] = Field(..., description="审计日志列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")


class AuditLogStatsResponse(BaseModel):
    """审计日志统计响应"""

    total_operations: int = Field(..., description="总操作数")
    successful_operations: int = Field(..., description="成功操作数")
    failed_operations: int = Field(..., description="失败操作数")
    unique_users: int = Field(..., description="不同用户数")
    recent_logins: int = Field(..., description="最近登录数")
    top_actions: list[dict[str, Any]] = Field(..., description="热门操作统计")
