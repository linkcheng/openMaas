"""
Copyright 2025 MaaS Team

审计日志批量操作优化

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

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from audit.domain.models import AuditLog
from audit.infrastructure.models import AuditLogORM
from config.settings import settings
from shared.infrastructure.batch_operations import BaseBatchOperations


class AuditLogBatchOperations(BaseBatchOperations[AuditLog, AuditLogORM]):
    """审计日志批量操作类"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLogORM)

    def _entity_to_dict(self, audit_log: AuditLog) -> dict[str, Any]:
        """将审计日志实体转换为字典格式"""
        return {
            "audit_log_id": audit_log.audit_log_id,
            "user_id": audit_log.user_id,
            "username": audit_log.username,
            "action": audit_log.action.value,
            "resource_type": audit_log.resource_type.value if audit_log.resource_type else None,
            "resource_id": audit_log.resource_id,
            "description": audit_log.description,
            "ip_address": audit_log.ip_address,
            "user_agent": audit_log.user_agent,
            "request_id": audit_log.request_id,
            "result": audit_log.result.value,
            "error_message": audit_log.error_message,
            "extra_data": audit_log.metadata,
            "created_at": audit_log.created_at,
        }

    def _get_conflict_columns(self) -> list[str]:
        """获取冲突检测的列名"""
        return ["audit_log_id"]

    async def batch_delete_old_logs(
        self,
        before_date: datetime,
        batch_size: int | None = None,
        max_batches: int = 100
    ) -> int:
        """批量删除旧的审计日志

        Args:
            before_date: 删除此日期之前的日志
            batch_size: 每批删除的数量，None时使用配置默认值
            max_batches: 最大批次数，防止长时间锁表

        Returns:
            删除的记录数
        """
        if batch_size is None:
            batch_size = settings.performance.cleanup_batch_size

        return await self.batch_delete_by_date(
            date_column="created_at",
            before_date=before_date,
            batch_size=batch_size,
            max_batches=max_batches
        )

    async def vacuum_analyze_audit_table(self) -> None:
        """对审计日志表执行VACUUM ANALYZE优化"""
        await self.vacuum_analyze_table("audit_logs")
