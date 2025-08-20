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
from audit.domain.services import (
    AuditAnalysisService,
    AuditArchiveService,
    AuditRuleService,
)
from config.settings import settings

"""审计日志应用服务"""


class AuditLogService:
    """审计日志应用服务"""

    def __init__(
        self,
        repository: AuditLogRepository,
        rule_service: AuditRuleService | None = None,
        archive_service: AuditArchiveService | None = None,
        analysis_service: AuditAnalysisService | None = None
    ):
        """初始化审计日志服务

        Args:
            repository: 审计日志仓储
            rule_service: 审计规则服务
            archive_service: 审计归档服务 
            analysis_service: 审计分析服务
        """
        self.repository = repository
        self.rule_service = rule_service or AuditRuleService()
        self.archive_service = archive_service or AuditArchiveService(self.rule_service)
        self.analysis_service = analysis_service or AuditAnalysisService()

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
        # 基础验证
        if not request.action:
            raise ValueError("操作类型不能为空")

        if not request.description:
            raise ValueError("描述不能为空")

        # 使用规则服务验证审计数据
        metadata = request.metadata or {}
        validation_errors = self.rule_service.validate_audit_data(request.action, metadata)
        if validation_errors:
            raise ValueError(f"审计数据验证失败: {', '.join(validation_errors)}")

        # 应用审计规则进行数据处理
        processed_metadata = self._process_metadata(request.action, metadata)

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
            metadata=processed_metadata,
            created_at=datetime.utcnow(),
        )

        await self.repository.save(audit_log)

        # 检查是否需要告警
        if self.rule_service.should_alert_on_action(request.action, request.user_id):
            logger.warning(f"高风险操作告警: {audit_log.get_operation_summary()}")
        else:
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
        # 获取时间范围内的审计日志
        start_time = datetime.utcnow() - timedelta(days=days)
        filter_obj = AuditLogFilter(start_time=start_time, end_time=datetime.utcnow())

        # 获取所有相关日志
        logs = await self.repository.find_by_filter(filter_obj, limit=10000)  # 设置合理上限

        # 使用分析服务生成统计报告
        security_summary = self.analysis_service.generate_security_summary(logs, days)

        return AuditLogStatsResponse(
            total_operations=security_summary["overview"]["total_operations"],
            successful_operations=security_summary["overview"]["total_operations"] - security_summary["overview"]["failed_operations"],
            failed_operations=security_summary["overview"]["failed_operations"],
            unique_users=security_summary["overview"]["unique_active_users"],
            recent_logins=security_summary["authentication"]["total_login_attempts"],
            top_actions=security_summary["top_operations"],
        )

    async def cleanup_old_audit_logs(self, days: int | None = None) -> int:
        """清理旧的审计日志"""
        if days is None:
            days = settings.performance.cleanup_retention_days

        if days <= 0:
            raise ValueError("保留天数必须大于0")

        # 获取需要清理的日志
        before_date = datetime.utcnow() - timedelta(days=days)
        filter_obj = AuditLogFilter(end_time=before_date)

        # 获取候选日志列表
        candidate_logs = await self.repository.find_by_filter(filter_obj, limit=10000)

        if not candidate_logs:
            logger.info("没有找到需要清理的审计日志")
            return 0

        # 使用归档服务生成清理计划
        current_time = datetime.utcnow()
        archive_plan = self.archive_service.generate_archive_plan(candidate_logs, current_time)

        # 执行删除操作
        deleted_count = 0
        if archive_plan["delete"] and hasattr(self.repository, "cleanup_old_logs"):
            deleted_count = await self.repository.cleanup_old_logs(before_date)
            logger.info(f"清理了 {deleted_count} 条超过 {days} 天的审计日志")
        else:
            logger.warning("当前仓储不支持批量清理功能或无需清理的日志")

        return deleted_count

    async def get_security_analysis(self, user_id: UUID | None = None, days: int = 30) -> dict:
        """获取安全分析报告
        
        Args:
            user_id: 用户ID，为空时分析所有用户
            days: 分析天数
            
        Returns:
            安全分析报告
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        filter_obj = AuditLogFilter(
            user_id=user_id,
            start_time=start_time,
            end_time=datetime.utcnow()
        )

        logs = await self.repository.find_by_filter(filter_obj, limit=10000)

        if user_id:
            # 用户行为分析
            return self.analysis_service.analyze_user_behavior(logs, user_id)
        else:
            # 整体安全分析
            return self.analysis_service.generate_security_summary(logs, days)

    async def detect_suspicious_activities(self, days: int = 7) -> list:
        """检测可疑活动
        
        Args:
            days: 检测天数
            
        Returns:
            可疑活动列表
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        filter_obj = AuditLogFilter(start_time=start_time, end_time=datetime.utcnow())

        logs = await self.repository.find_by_filter(filter_obj, limit=10000)
        return self.analysis_service.detect_suspicious_activities(logs)

    def _process_metadata(self, action, metadata: dict) -> dict:
        """处理元数据，应用审计规则
        
        Args:
            action: 操作类型
            metadata: 原始元数据
            
        Returns:
            处理后的元数据
        """
        processed = metadata.copy()

        # 应用匿名化规则
        for field_name in list(processed.keys()):
            if self.rule_service.should_anonymize_data(action, field_name):
                # 简单的匿名化处理
                if isinstance(processed[field_name], str):
                    processed[field_name] = "***"
                elif isinstance(processed[field_name], (int, float)):
                    processed[field_name] = 0

        # 添加审计级别信息
        processed["audit_level"] = self.rule_service.get_audit_level(action)
        processed["retention_days"] = self.rule_service.get_retention_days(action)

        return processed

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
