"""
Copyright 2025 MaaS Team

审计日志领域模型

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

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class AuditResult(str, Enum):
    """审计结果枚举"""
    SUCCESS = "success"
    FAILURE = "failure"


class ActionType(str, Enum):
    """操作类型枚举"""
    # 认证相关
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    TOKEN_REFRESH = "token_refresh"

    # 用户管理
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_ACTIVATE = "user_activate"
    USER_DEACTIVATE = "user_deactivate"
    PROFILE_UPDATE = "profile_update"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"

    # 角色权限
    ROLE_CREATE = "role_create"
    ROLE_UPDATE = "role_update"
    ROLE_DELETE = "role_delete"
    ROLE_ASSIGN = "role_assign"
    ROLE_REVOKE = "role_revoke"
    PERMISSION_CREATE = "permission_create"
    PERMISSION_UPDATE = "permission_update"
    PERMISSION_DELETE = "permission_delete"
    PERMISSION_GRANT = "permission_grant"
    PERMISSION_REVOKE = "permission_revoke"

    # API密钥
    API_KEY_CREATE = "api_key_create"
    API_KEY_DELETE = "api_key_delete"
    API_KEY_REVOKE = "api_key_revoke"

    # 系统管理
    SYSTEM_SETTING_UPDATE = "system_setting_update"
    ADMIN_OPERATION = "admin_operation"
    USER_MANAGEMENT = "user_management"

    # 业务操作 - 数据管理
    DATASET_CREATE = "dataset_create"
    DATASET_UPDATE = "dataset_update"
    DATASET_DELETE = "dataset_delete"

    # 业务操作 - 模型管理
    MODEL_CREATE = "model_create"
    MODEL_UPDATE = "model_update"
    MODEL_DELETE = "model_delete"
    MODEL_DEPLOY = "model_deploy"
    MODEL_UNDEPLOY = "model_undeploy"

    # 业务操作 - 应用管理
    APPLICATION_CREATE = "application_create"
    APPLICATION_UPDATE = "application_update"
    APPLICATION_DELETE = "application_delete"


class ResourceType(str, Enum):
    """资源类型枚举"""
    USER = "user"
    ROLE = "role"
    API_KEY = "api_key"
    DATASET = "dataset"
    MODEL = "model"
    APPLICATION = "application"
    SYSTEM = "system"


@dataclass(frozen=True)
class AuditLog:
    """审计日志领域实体"""

    audit_log_id: UUID
    user_id: UUID | None
    username: str | None
    action: ActionType
    resource_type: ResourceType | None
    resource_id: UUID | None
    description: str
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    result: AuditResult
    error_message: str | None
    metadata: dict[str, Any]
    created_at: datetime

    def __post_init__(self) -> None:
        """验证领域规则"""
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("操作描述不能为空")

        if self.result == AuditResult.FAILURE and not self.error_message:
            raise ValueError("操作失败时必须提供错误信息")

    @property
    def is_successful(self) -> bool:
        """判断操作是否成功"""
        return self.result == AuditResult.SUCCESS

    @property
    def is_system_operation(self) -> bool:
        """判断是否为系统操作"""
        return self.user_id is None

    @property
    def has_resource(self) -> bool:
        """判断是否关联资源"""
        return self.resource_type is not None and self.resource_id is not None

    def get_operation_summary(self) -> str:
        """获取操作摘要"""
        actor = self.username if self.username else "系统"
        action_desc = self._get_action_description()

        if self.has_resource:
            return f"{actor} {action_desc} {self.resource_type}:{self.resource_id}"
        else:
            return f"{actor} {action_desc}"

    def _get_action_description(self) -> str:
        """获取操作描述"""
        action_map = {
            ActionType.LOGIN: "登录",
            ActionType.LOGOUT: "登出",
            ActionType.LOGIN_FAILED: "登录失败",
            ActionType.USER_CREATE: "创建用户",
            ActionType.USER_UPDATE: "更新用户",
            ActionType.USER_DELETE: "删除用户",
            ActionType.PROFILE_UPDATE: "更新个人资料",
            ActionType.PASSWORD_CHANGE: "修改密码",
            ActionType.MODEL_CREATE: "创建模型",
            ActionType.MODEL_DEPLOY: "部署模型",
            # 可以根据需要扩展更多操作类型
        }
        return action_map.get(self.action, str(self.action))
