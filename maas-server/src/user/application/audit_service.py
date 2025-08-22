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

"""用户应用层 - 审计应用服务"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID
from loguru import logger

from user.application.schemas import (
    AuditCleanupCommand,
    AuditCleanupResponse,
    AuditLogQuery,
    AuditLogResponse,
    AuditStatsQuery,
    AuditStatsResponse,
)
from user.domain.services.audit_domain_service import AuditDomainService


class AuditApplicationService:
    """审计应用服务 - 负责协调和编排，DTO转换"""
    
    def __init__(self, audit_domain_service: AuditDomainService):
        self._audit_domain_service = audit_domain_service
    
    async def get_logs(self, query: AuditLogQuery) -> dict[str, Any]:
        """分页查询审计日志"""
        offset = (query.page - 1) * query.page_size
        
        # 调用领域服务
        logs, total = await self._audit_domain_service.query_audit_logs(
            user_id=query.user_id,
            action=query.action,
            start_time=query.start_time,
            end_time=query.end_time,
            success=query.success,
            limit=query.page_size,
            offset=offset,
        )
        
        # 转换为响应DTO
        log_responses = [
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                username=log.username,
                action=log.action,
                description=log.description,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                success=log.success,
                error_message=log.error_message,
                created_at=log.created_at,
                operation_summary=log.get_operation_summary(),
                is_system_operation=log.is_system_operation,
            )
            for log in logs
        ]
        
        # 计算分页信息
        pagination = self._audit_domain_service.calculate_pagination(
            total, query.page, query.page_size
        )
        
        return {
            "logs": log_responses,
            "pagination": pagination,
        }
    
    async def get_user_logs(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """获取指定用户的审计日志"""
        query = AuditLogQuery(
            page=page,
            page_size=page_size,
            user_id=user_id,
        )
        return await self.get_logs(query)
    
    async def get_stats(self, query: AuditStatsQuery) -> AuditStatsResponse:
        """获取审计统计信息"""
        start_time = datetime.utcnow() - timedelta(days=query.days)
        end_time = datetime.utcnow()
        
        # 调用领域服务
        stats = await self._audit_domain_service.get_audit_statistics(
            start_time=start_time,
            end_time=end_time,
        )
        
        # 转换为响应DTO
        return AuditStatsResponse(
            period=f"最近 {query.days} 天",
            total_operations=stats.get("total", 0),
            successful_operations=stats.get("successful", 0),
            failed_operations=stats.get("failed", 0),
            unique_users=stats.get("unique_users", 0),
            top_actions=stats.get("top_actions", []),
            generated_at=datetime.utcnow().isoformat(),
        )
    
    async def cleanup_old_logs(self, command: AuditCleanupCommand) -> AuditCleanupResponse:
        """清理旧的审计日志"""
        # 调用领域服务
        deleted_count = await self._audit_domain_service.cleanup_expired_logs(
            retention_days=command.days
        )
        
        # 转换为响应DTO
        return AuditCleanupResponse(
            deleted_count=deleted_count,
            retention_days=command.days,
            cleanup_time=datetime.utcnow().isoformat(),
        )
