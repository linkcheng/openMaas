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

"""用户领域服务 - 审计日志核心业务逻辑"""

import math
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from loguru import logger

from shared.domain.base import DomainService
from user.domain.models import AuditLog
from user.domain.repositories import IAuditLogRepository


class AuditDomainService(DomainService):
    """审计日志领域服务
    
    负责审计日志的核心业务逻辑，包括：
    - 日志记录的业务规则验证
    - Repository 操作管理
    - 数据完整性保证
    """

    def __init__(self, audit_repository: IAuditLogRepository):
        self._audit_repository = audit_repository

    async def record_audit_log(self, audit_log: AuditLog) -> None:
        """记录审计日志
        
        Args:
            audit_log: 审计日志领域实体
        """
        try:
            # 业务规则验证
            self._validate_audit_log(audit_log)
            
            # 数据存储
            await self._audit_repository.save(audit_log)
            
            # 记录到应用日志
            if audit_log.success:
                logger.info(f"审计日志: {audit_log.get_operation_summary()}")
            else:
                logger.warning(f"审计日志 (失败): {audit_log.get_operation_summary()} - {audit_log.error_message}")
                
        except Exception as e:
            logger.error(f"保存审计日志失败: {e}", exc_info=True)
            # 不抛出异常，避免影响主业务流程

    async def query_audit_logs(
        self,
        user_id: UUID | None = None,
        action: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        success: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[AuditLog], int]:
        """查询审计日志
        
        Args:
            user_id: 用户ID筛选
            action: 操作类型筛选
            start_time: 开始时间
            end_time: 结束时间
            success: 操作结果筛选
            limit: 查询数量限制
            offset: 查询偏移量
            
        Returns:
            (日志列表, 总数)
        """
        # 业务规则验证
        self._validate_query_parameters(limit, offset, start_time, end_time)
        
        # Repository 操作
        return await self._audit_repository.find_with_count(
            user_id=user_id,
            action=action,
            start_time=start_time,
            end_time=end_time,
            success=success,
            limit=limit,
            offset=offset,
        )

    async def get_audit_statistics(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        """获取审计统计信息
        
        Args:
            start_time: 统计开始时间
            end_time: 统计结束时间
            
        Returns:
            统计信息字典
        """
        # 业务规则验证
        if start_time and end_time and start_time >= end_time:
            raise ValueError("开始时间必须早于结束时间")
        
        # Repository 操作
        return await self._audit_repository.get_stats(
            start_time=start_time,
            end_time=end_time,
        )

    async def cleanup_expired_logs(self, retention_days: int) -> int:
        """清理过期的审计日志
        
        Args:
            retention_days: 保留天数
            
        Returns:
            删除的记录数
        """
        # 业务规则验证
        if retention_days <= 0:
            raise ValueError("保留天数必须大于0")
        
        if retention_days < 30:
            raise ValueError("为保证合规性，审计日志保留天数不能少于30天")
        
        # 计算删除截止时间
        before_date = datetime.now(UTC) - timedelta(days=retention_days)
        
        # Repository 操作
        deleted_count = await self._audit_repository.cleanup_old_logs(before_date)
        
        logger.info(f"清理了 {deleted_count} 条超过 {retention_days} 天的审计日志")
        return deleted_count

    def _validate_audit_log(self, audit_log: AuditLog) -> None:
        """验证审计日志的业务规则
        
        Args:
            audit_log: 审计日志实体
        """
        # 基本字段验证
        if not audit_log.description or len(audit_log.description.strip()) == 0:
            raise ValueError("操作描述不能为空")
        
        if not audit_log.success and not audit_log.error_message:
            raise ValueError("操作失败时必须提供错误信息")
        
        # 用户信息一致性验证
        if audit_log.user_id and not audit_log.username:
            logger.warning(f"用户ID {audit_log.user_id} 缺少用户名信息")

    def _validate_query_parameters(
        self,
        limit: int,
        offset: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> None:
        """验证查询参数的业务规则
        
        Args:
            limit: 查询数量限制
            offset: 查询偏移量
            start_time: 开始时间
            end_time: 结束时间
        """
        if limit <= 0 or limit > 100:
            raise ValueError("查询数量必须在1-100之间")
        
        if offset < 0:
            raise ValueError("查询偏移量不能为负数")
        
        if start_time and end_time and start_time >= end_time:
            raise ValueError("开始时间必须早于结束时间")
        
        # 防止查询时间范围过大
        if start_time and end_time:
            time_diff = end_time - start_time
            if time_diff.days > 365:
                raise ValueError("查询时间范围不能超过365天")

    def calculate_pagination(self, total: int, page: int, page_size: int) -> dict[str, Any]:
        """计算分页信息
        
        Args:
            total: 总记录数
            page: 当前页码
            page_size: 每页数量
            
        Returns:
            分页信息字典
        """
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages,
        }