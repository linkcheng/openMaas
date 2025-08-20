"""
Copyright 2025 MaaS Team

审计日志归档领域服务

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

from datetime import datetime, timedelta
from uuid import UUID

from audit.domain.models import ActionType, AuditLog
from audit.domain.services.audit_rule_service import AuditRuleService
from shared.domain.base import DomainService


class AuditArchiveService(DomainService):
    """审计日志归档领域服务
    
    负责管理审计日志的生命周期，包括归档、压缩、清理等操作。
    确保合规性要求的同时优化存储性能。
    """

    def __init__(self, rule_service: AuditRuleService):
        """初始化归档服务
        
        Args:
            rule_service: 审计规则服务
        """
        self.rule_service = rule_service

    def should_archive(self, audit_log: AuditLog, current_time: datetime) -> bool:
        """判断审计日志是否应该归档
        
        Args:
            audit_log: 审计日志
            current_time: 当前时间
            
        Returns:
            是否应该归档
        """
        # 30天以上的日志考虑归档
        archive_threshold = current_time - timedelta(days=30)
        return audit_log.created_at < archive_threshold

    def should_compress(self, audit_log: AuditLog, current_time: datetime) -> bool:
        """判断审计日志是否应该压缩
        
        Args:
            audit_log: 审计日志
            current_time: 当前时间
            
        Returns:
            是否应该压缩
        """
        # 90天以上的日志考虑压缩
        compress_threshold = current_time - timedelta(days=90)
        return audit_log.created_at < compress_threshold

    def should_delete(self, audit_log: AuditLog, current_time: datetime) -> bool:
        """判断审计日志是否应该删除
        
        Args:
            audit_log: 审计日志
            current_time: 当前时间
            
        Returns:
            是否应该删除
        """
        retention_days = self.rule_service.get_retention_days(audit_log.action)
        delete_threshold = current_time - timedelta(days=retention_days)
        return audit_log.created_at < delete_threshold

    def get_archive_strategy(self, action: ActionType) -> dict[str, int]:
        """获取归档策略
        
        Args:
            action: 操作类型
            
        Returns:
            归档策略配置
        """
        if action in self.rule_service.HIGH_RISK_ACTIONS:
            return {
                "hot_days": 90,      # 热存储天数
                "warm_days": 365,    # 温存储天数
                "cold_days": 1095,   # 冷存储天数
                "retention_days": 2555  # 总保留天数
            }
        elif action in self.rule_service.AUTH_ACTIONS:
            return {
                "hot_days": 30,
                "warm_days": 180,
                "cold_days": 730,
                "retention_days": 1095
            }
        else:
            return {
                "hot_days": 7,
                "warm_days": 30,
                "cold_days": 180,
                "retention_days": 365
            }

    def get_storage_tier(self, audit_log: AuditLog, current_time: datetime) -> str:
        """获取存储层级
        
        Args:
            audit_log: 审计日志
            current_time: 当前时间
            
        Returns:
            存储层级: HOT, WARM, COLD
        """
        strategy = self.get_archive_strategy(audit_log.action)
        age_days = (current_time - audit_log.created_at).days

        if age_days <= strategy["hot_days"]:
            return "HOT"
        elif age_days <= strategy["warm_days"]:
            return "WARM"
        elif age_days <= strategy["cold_days"]:
            return "COLD"
        else:
            return "ARCHIVE"

    def calculate_storage_cost(self, logs: list[AuditLog], current_time: datetime) -> dict[str, float]:
        """计算存储成本
        
        Args:
            logs: 审计日志列表
            current_time: 当前时间
            
        Returns:
            各存储层级的成本统计
        """
        costs = {"HOT": 0.0, "WARM": 0.0, "COLD": 0.0, "ARCHIVE": 0.0}

        # 存储成本（每GB每月）
        cost_per_gb = {
            "HOT": 0.1,
            "WARM": 0.05,
            "COLD": 0.02,
            "ARCHIVE": 0.005
        }

        for log in logs:
            tier = self.get_storage_tier(log, current_time)
            # 假设每条日志平均1KB
            size_gb = 0.001
            costs[tier] += cost_per_gb[tier] * size_gb

        return costs

    def generate_archive_plan(self, logs: list[AuditLog], current_time: datetime) -> dict[str, list[UUID]]:
        """生成归档计划
        
        Args:
            logs: 审计日志列表
            current_time: 当前时间
            
        Returns:
            归档计划（操作类型 -> 日志ID列表）
        """
        plan = {
            "archive": [],
            "compress": [],
            "delete": []
        }

        for log in logs:
            if self.should_delete(log, current_time):
                plan["delete"].append(log.audit_log_id)
            elif self.should_compress(log, current_time):
                plan["compress"].append(log.audit_log_id)
            elif self.should_archive(log, current_time):
                plan["archive"].append(log.audit_log_id)

        return plan

    def validate_archive_integrity(self, archived_logs: list[AuditLog]) -> list[str]:
        """验证归档完整性
        
        Args:
            archived_logs: 已归档的日志列表
            
        Returns:
            完整性检查错误列表
        """
        errors = []

        # 检查必要字段
        required_fields = ["audit_log_id", "user_id", "action", "created_at"]

        for log in archived_logs:
            for field in required_fields:
                if not hasattr(log, field) or getattr(log, field) is None:
                    errors.append(f"日志 {log.audit_log_id} 缺少必要字段: {field}")

        # 检查时间顺序
        sorted_logs = sorted(archived_logs, key=lambda x: x.created_at)
        if sorted_logs != archived_logs:
            errors.append("归档日志时间顺序不正确")

        return errors

    def get_compliance_report(self, action: ActionType, start_date: datetime, end_date: datetime) -> dict:
        """生成合规性报告
        
        Args:
            action: 操作类型
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            合规性报告
        """
        retention_days = self.rule_service.get_retention_days(action)
        strategy = self.get_archive_strategy(action)

        return {
            "action": action.value,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "retention_policy": {
                "days": retention_days,
                "reason": "监管合规要求" if retention_days >= 1095 else "业务需求"
            },
            "archive_strategy": strategy,
            "compliance_status": "COMPLIANT"
        }
