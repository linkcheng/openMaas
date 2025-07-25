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

"""审计日志REST API接口"""


from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger

from audit.application.schemas import (
    AuditLogListResponse,
    AuditLogQueryRequest,
    AuditLogResponse,
    AuditLogStatsResponse,
)
from audit.application.services import AuditLogService
from shared.application.response import ApiResponse
from shared.interface.auth_middleware import require_admin
from shared.interface.dependencies import get_audit_log_service

# 创建路由器
router = APIRouter(prefix="/audit", tags=["审计日志"])


@router.get(
    "/logs",
    response_model=ApiResponse[AuditLogListResponse],
    summary="获取审计日志列表",
    description="获取系统审计日志列表，支持分页和筛选",
)
async def get_audit_logs(
    request: Request,
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    username: str | None = Query(None, description="用户名筛选"),
    action: str | None = Query(None, description="操作类型筛选"),
    result: str | None = Query(None, description="操作结果筛选"),
    start_time: str | None = Query(None, description="开始时间"),
    end_time: str | None = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    _: bool = Depends(require_admin),
) -> ApiResponse[AuditLogListResponse]:
    """获取审计日志列表"""

    query = AuditLogQueryRequest(
        username=username,
        action=action,
        result=result,
        start_time=start_time,
        end_time=end_time,
        page=page,
        size=size,
    )

    result = await audit_service.query_audit_logs(query)
    return ApiResponse.success_response(result, "获取审计日志成功")


@router.get(
    "/stats",
    response_model=ApiResponse[AuditLogStatsResponse],
    summary="获取审计日志统计",
    description="获取审计日志的统计信息",
)
async def get_audit_stats(
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    _: bool = Depends(require_admin),
) -> ApiResponse[AuditLogStatsResponse]:
    """获取审计日志统计"""
    logger.info("get_audit_stats")
    stats = await audit_service.get_audit_stats()
    return ApiResponse.success_response(stats, "获取统计信息成功")


@router.post(
    "/logs/export",
    response_model=ApiResponse[list[AuditLogResponse]],
    summary="导出审计日志",
    description="根据指定的日志ID列表导出审计日志",
)
async def export_audit_logs(
    request: dict,
    audit_service: Annotated[AuditLogService, Depends(get_audit_log_service)],
    _: bool = Depends(require_admin),
) -> ApiResponse[list[AuditLogResponse]]:
    """导出审计日志"""

    log_ids = request.get("log_ids", [])

    if not log_ids:
        raise HTTPException(status_code=400, detail="请选择要导出的日志")

    logs = await audit_service.export_audit_logs(log_ids)
    return ApiResponse.success_response(logs, "导出日志成功")

