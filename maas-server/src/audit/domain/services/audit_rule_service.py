"""
Copyright 2025 MaaS Team

审计规则领域服务

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

from uuid import UUID

from audit.domain.models import ActionType, AuditResult
from shared.domain.base import DomainService


class AuditRuleService(DomainService):
    """审计规则领域服务
    
    负责定义和管理审计规则，判断哪些操作需要记录审计日志，
    以及审计日志的详细程度。
    """

    # 高风险操作，需要详细审计
    HIGH_RISK_ACTIONS = {
        ActionType.USER_DELETE,
        ActionType.ROLE_DELETE,
        ActionType.PERMISSION_DELETE,
        ActionType.API_KEY_DELETE,
        ActionType.SYSTEM_SETTING_UPDATE,
        ActionType.ADMIN_OPERATION,
        ActionType.PASSWORD_RESET,
        ActionType.USER_DEACTIVATE,
        ActionType.MODEL_DELETE,
        ActionType.APPLICATION_DELETE
    }

    # 认证相关操作，需要安全审计
    AUTH_ACTIONS = {
        ActionType.LOGIN,
        ActionType.LOGOUT,
        ActionType.LOGIN_FAILED,
        ActionType.TOKEN_REFRESH,
        ActionType.PASSWORD_CHANGE
    }

    # 权限相关操作，需要授权审计
    PERMISSION_ACTIONS = {
        ActionType.ROLE_CREATE,
        ActionType.ROLE_UPDATE,
        ActionType.ROLE_ASSIGN,
        ActionType.ROLE_REVOKE,
        ActionType.PERMISSION_CREATE,
        ActionType.PERMISSION_UPDATE,
        ActionType.PERMISSION_GRANT,
        ActionType.PERMISSION_REVOKE
    }

    def should_audit_action(self, action: ActionType) -> bool:
        """判断操作是否需要审计
        
        Args:
            action: 操作类型
            
        Returns:
            是否需要审计
        """
        # 所有操作都需要审计，但审计详细程度不同
        return True

    def get_audit_level(self, action: ActionType) -> str:
        """获取审计级别
        
        Args:
            action: 操作类型
            
        Returns:
            审计级别: BASIC, DETAILED, SECURITY
        """
        if action in self.HIGH_RISK_ACTIONS:
            return "DETAILED"
        elif action in self.AUTH_ACTIONS:
            return "SECURITY"
        elif action in self.PERMISSION_ACTIONS:
            return "DETAILED"
        else:
            return "BASIC"

    def should_include_request_body(self, action: ActionType) -> bool:
        """判断是否需要记录请求体
        
        Args:
            action: 操作类型
            
        Returns:
            是否记录请求体
        """
        # 高风险操作和权限操作需要记录请求体
        return action in self.HIGH_RISK_ACTIONS or action in self.PERMISSION_ACTIONS

    def should_include_response_body(self, action: ActionType, result: AuditResult) -> bool:
        """判断是否需要记录响应体
        
        Args:
            action: 操作类型
            result: 操作结果
            
        Returns:
            是否记录响应体
        """
        # 失败的操作总是记录响应，便于排查问题
        if result == AuditResult.FAILURE:
            return True

        # 查询类操作通常不记录响应体（避免敏感信息泄露）
        return action in self.HIGH_RISK_ACTIONS

    def get_retention_days(self, action: ActionType) -> int:
        """获取审计日志保留天数
        
        Args:
            action: 操作类型
            
        Returns:
            保留天数
        """
        if action in self.HIGH_RISK_ACTIONS:
            return 2555  # 7年（合规要求）
        elif action in self.AUTH_ACTIONS or action in self.PERMISSION_ACTIONS:
            return 1095  # 3年
        else:
            return 365   # 1年

    def should_alert_on_action(self, action: ActionType, user_id: UUID | None = None) -> bool:
        """判断操作是否需要告警
        
        Args:
            action: 操作类型
            user_id: 用户ID
            
        Returns:
            是否需要告警
        """
        # 系统操作（user_id为None）如果是高风险操作需要告警
        if user_id is None and action in self.HIGH_RISK_ACTIONS:
            return True

        # 连续登录失败需要告警（这里简化处理，实际需要检查频率）
        if action == ActionType.LOGIN_FAILED:
            return True

        return False

    def get_required_metadata_fields(self, action: ActionType) -> list[str]:
        """获取操作需要记录的元数据字段
        
        Args:
            action: 操作类型
            
        Returns:
            需要记录的元数据字段列表
        """
        base_fields = ["user_agent", "ip_address"]

        if action in self.AUTH_ACTIONS:
            base_fields.extend(["login_method", "session_id"])

        if action in self.PERMISSION_ACTIONS:
            base_fields.extend(["affected_users", "permission_changes"])

        if action in self.HIGH_RISK_ACTIONS:
            base_fields.extend(["reason", "approval_id"])

        return base_fields

    def validate_audit_data(self, action: ActionType, metadata: dict) -> list[str]:
        """验证审计数据完整性
        
        Args:
            action: 操作类型
            metadata: 元数据
            
        Returns:
            验证错误列表
        """
        errors = []
        required_fields = self.get_required_metadata_fields(action)

        for field in required_fields:
            if field not in metadata:
                errors.append(f"缺少必需的元数据字段: {field}")

        return errors

    def should_anonymize_data(self, action: ActionType, field_name: str) -> bool:
        """判断字段是否需要匿名化
        
        Args:
            action: 操作类型
            field_name: 字段名称
            
        Returns:
            是否需要匿名化
        """
        # 敏感字段列表
        sensitive_fields = {"password", "token", "api_key", "secret"}

        # 敏感字段总是匿名化
        if any(sensitive in field_name.lower() for sensitive in sensitive_fields):
            return True

        # 非高风险操作的个人信息字段需要匿名化
        if action not in self.HIGH_RISK_ACTIONS:
            personal_fields = {"email", "phone", "address", "id_card"}
            if any(personal in field_name.lower() for personal in personal_fields):
                return True

        return False
