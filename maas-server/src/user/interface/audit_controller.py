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

"""用户接口层 - 审计日志控制器（简化版）"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from shared.application.response import ApiResponse
from user.application import get_audit_application_service
from user.application.audit_service import AuditApplicationService
from user.application.schemas import (
    AuditCleanupCommand,
    AuditCleanupResponse,
    AuditLogListResponse,
    AuditLogQuery,
    AuditStatsQuery,
    AuditStatsResponse,
)
from user.infrastructure.permission import require_admin_permission

router = APIRouter(prefix="/audit", tags=["审计日志"])


@router.get(
    "/logs",
    response_model=ApiResponse[AuditLogListResponse],
    summary="获取审计日志列表",
    description="管理员查看系统审计日志列表，支持分页和筛选",
    dependencies=[require_admin_permission()],
)
async def get_audit_logs(
    audit_service: Annotated[AuditApplicationService, Depends(get_audit_application_service)],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: UUID | None = Query(None, description="用户ID筛选"),
    action: str | None = Query(None, description="操作类型筛选"),
    start_time: datetime | None = Query(None, description="开始时间"),
    end_time: datetime | None = Query(None, description="结束时间"),
    success: bool | None = Query(None, description="操作结果筛选"),
):
    """获取审计日志列表"""

    # 构建查询对象
    query = AuditLogQuery(
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=action,
        start_time=start_time,
        end_time=end_time,
        success=success,
    )

    # 调用应用服务
    result = await audit_service.get_logs(query)

    # 转换响应格式
    response_data = AuditLogListResponse(
        items= result["logs"],
        pagination=result["pagination"],
    )

    return ApiResponse.success_response(response_data, "获取审计日志成功")


@router.get(
    "/stats",
    response_model=ApiResponse[AuditStatsResponse],
    summary="获取审计日志统计",
    description="获取审计日志的统计信息，包括总数、成功率等",
    dependencies=[require_admin_permission()],
)
async def get_audit_stats(
    audit_service: Annotated[AuditApplicationService, Depends(get_audit_application_service)],
    days: int = Query(7, ge=1, le=365, description="统计天数"),
):
    """获取审计日志统计"""

    query = AuditStatsQuery(days=days)
    stats = await audit_service.get_stats(query)

    return ApiResponse.success_response(stats, "获取统计信息成功")


@router.get(
    "/users/{user_id}/logs",
    response_model=ApiResponse[AuditLogListResponse],
    summary="获取指定用户的审计日志",
    description="管理员查看指定用户的操作日志",
    dependencies=[require_admin_permission()],
)
async def get_user_audit_logs(
    user_id: UUID,
    audit_service: Annotated[AuditApplicationService, Depends(get_audit_application_service)],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """获取指定用户的审计日志"""

    result = await audit_service.get_user_logs(
        user_id=user_id,
        page=page,
        page_size=page_size,
    )

    # 转换返回格式
    response_data = AuditLogListResponse(
        items= result["logs"],
        pagination=result["pagination"],
    )

    return ApiResponse.success_response(response_data, "获取用户审计日志成功")


@router.post(
    "/cleanup",
    response_model=ApiResponse[AuditCleanupResponse],
    summary="清理旧的审计日志",
    description="清理指定天数之前的审计日志（谨慎操作）",
    dependencies=[require_admin_permission()],
)
async def cleanup_audit_logs(
    audit_service: Annotated[AuditApplicationService, Depends(get_audit_application_service)],
    days: int = Query(90, ge=30, le=365, description="保留天数，30-365天"),
):
    """清理旧的审计日志"""

    command = AuditCleanupCommand(days=days)
    response_data = await audit_service.cleanup_old_logs(command)

    return ApiResponse.success_response(response_data, f"清理完成，删除了 {response_data.deleted_count} 条记录")
