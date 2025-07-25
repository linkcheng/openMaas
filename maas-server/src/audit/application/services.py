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

import math
from datetime import datetime, timedelta
from uuid import UUID

from loguru import logger
from uuid_extensions import uuid7

from audit.application.schemas import (
    AuditLogListResponse,
    AuditLogQueryRequest,
    AuditLogResponse,
    AuditLogStatsResponse,
    CreateAuditLogRequest,
)
from audit.domain.models import AuditLog
from audit.domain.repositories import AuditLogFilter, AuditLogRepository
from config.settings import settings

"""审计日志应用服务"""


class AuditLogService:
    """审计日志应用服务"""

    def __init__(self, repository: AuditLogRepository):
        """初始化审计日志服务
        
        Args:
            repository: 审计日志仓储
        """
        self.repository = repository

    async def create_audit_log(
        self, request: CreateAuditLogRequest
    ) -> AuditLogResponse:
        """创建审计日志

        Args:
            request: 创建请求

        Returns:
            审计日志响应
        
        Raises:
            ValueError: 当必要参数缺失时
        """
        if not request.action:
            raise ValueError("操作类型不能为空")

        if not request.description:
            raise ValueError("描述不能为空")

        audit_log = AuditLog(
            audit_log_id=uuid7(),
            user_id=request.user_id,
            username=request.username,
            action=request.action,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            description=request.description,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            request_id=request.request_id,
            result=request.result,
            error_message=request.error_message,
            metadata=request.metadata,
            created_at=datetime.utcnow(),
        )


        await self.repository.save(audit_log)
        logger.info(f"审计日志已创建: {audit_log.get_operation_summary()}")
        return self._domain_to_response(audit_log)

    async def query_audit_logs(
        self, request: AuditLogQueryRequest
    ) -> AuditLogListResponse:
        """查询审计日志列表

        Args:
            request: 查询请求

        Returns:
            审计日志列表响应
            
        Raises:
            ValueError: 当分页参数无效时
        """
        if request.page < 1:
            raise ValueError("页码必须大于0")
        if request.page_size < 1:
            raise ValueError("页面大小必须大于0")

        filter_obj = AuditLogFilter(
            user_id=request.user_id,
            username=request.username,
            action=request.action,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            result=request.result,
            ip_address=request.ip_address,
            start_time=request.start_time,
            end_time=request.end_time,
            search_keyword=request.search_keyword,
        )

        offset = (request.page - 1) * request.page_size

        audit_logs, total = await self.repository.find_with_count_by_filter(
            filter_obj=filter_obj,
            limit=request.page_size,
            offset=offset,
            order_by=request.order_by,
            order_desc=request.order_desc,
        )

        items = [self._domain_to_response(log) for log in audit_logs]
        total_pages = math.ceil(total / request.page_size) if total > 0 else 1

        return AuditLogListResponse(
            items=items,
            total=total,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
        )

    async def get_recent_logins(
        self,
        user_id: UUID | None = None,
        hours: int = 24,
        limit: int = 50,
    ) -> list[AuditLogResponse]:
        """获取最近的登录记录

        Args:
            user_id: 用户ID, 为空时查找所有用户
            hours: 最近多少小时
            limit: 返回数量限制

        Returns:
            审计日志列表
        """
        audit_logs = await self.repository.find_recent_logins(
            user_id=user_id,
            hours=hours,
            limit=limit,
        )

        return [self._domain_to_response(log) for log in audit_logs]

    async def export_audit_logs(self, log_ids: list[UUID]) -> list[AuditLogResponse]:
        """导出指定ID的审计日志

        Args:
            log_ids: 审计日志ID列表

        Returns:
            审计日志列表
        """
        if not log_ids:
            return []

        logs = await self.repository.find_by_ids(log_ids)
        return [self._domain_to_response(log) for log in logs]

    async def get_audit_stats(self, days: int = 7) -> AuditLogStatsResponse:
        """获取审计日志统计信息

        Args:
            days: 统计最近多少天的数据

        Returns:
            统计信息
        """
        start_time = datetime.utcnow() - timedelta(days=days)

        stats = await self.repository.get_statistics(
            start_time=start_time,
            include_user_stats=True,
            include_action_stats=True
        )

        return AuditLogStatsResponse(
            total_operations=stats["total"],
            successful_operations=stats["successful"],
            failed_operations=stats["failed"],
            unique_users=stats["unique_users"],
            recent_logins=stats["recent_logins"],
            top_actions=stats["top_actions"],
        )

    async def cleanup_old_audit_logs(self, days: int | None = None) -> int:
        """清理旧的审计日志"""
        if days is None:
            days = settings.performance.cleanup_retention_days

        if days <= 0:
            raise ValueError("保留天数必须大于0")

        before_date = datetime.utcnow() - timedelta(days=days)


        if hasattr(self.repository, "cleanup_old_logs"):
            deleted_count = await self.repository.cleanup_old_logs(before_date)
            logger.info(f"清理了 {deleted_count} 条超过 {days} 天的审计日志")
            return deleted_count
        else:
            logger.warning("当前仓储不支持批量清理功能")
            return 0


    def _domain_to_response(self, audit_log: AuditLog) -> AuditLogResponse:
        """将领域模型转换为响应格式"""
        return AuditLogResponse(
            audit_log_id=audit_log.audit_log_id,
            user_id=audit_log.user_id,
            username=audit_log.username,
            action=audit_log.action,
            resource_type=audit_log.resource_type,
            resource_id=audit_log.resource_id,
            description=audit_log.description,
            ip_address=audit_log.ip_address,
            user_agent=audit_log.user_agent,
            request_id=audit_log.request_id,
            result=audit_log.result,
            error_message=audit_log.error_message,
            metadata=audit_log.metadata,
            created_at=audit_log.created_at,
            operation_summary=audit_log.get_operation_summary(),
            is_successful=audit_log.is_successful,
            is_system_operation=audit_log.is_system_operation,
        )

# 辅助函数: 快速创建审计日志
async def log_user_action(
    action,
    description: str,
    user_id = None,
    username: str | None = None,
    resource_type = None,
    resource_id = None,
    result = None,
    error_message: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    """快速记录用户操作

    这是一个便捷方法, 用于在业务代码中快速记录审计日志
    使用独立的会话确保事务完整性
    """

    try:
        from audit.domain.models import AuditResult
        from audit.infrastructure.repositories import SQLAlchemyAuditLogRepository
        from shared.infrastructure.database import async_session_factory

        # 设置默认值
        if result is None:
            result = AuditResult.SUCCESS

        async with async_session_factory() as session:
            repository = SQLAlchemyAuditLogRepository(session)
            service = AuditLogService(repository)

            request = CreateAuditLogRequest(
                user_id=user_id,
                username=username,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                result=result,
                error_message=error_message,
                metadata=metadata or {},
            )

            await service.create_audit_log(request)
    except Exception as e:
        logger.error(f"记录审计日志失败: {e}", exc_info=True)
        # 审计日志失败不应该影响主业务流程
        pass

