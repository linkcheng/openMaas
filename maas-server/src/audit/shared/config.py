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

"""审计日志配置管理"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from audit.domain.models import ActionType, ResourceType


@dataclass
class AuditRuleConfig:
    """审计规则配置"""
    action: ActionType
    description: str
    resource_type: ResourceType | None = None
    enabled: bool = True
    extract_user_from_result: bool = False
    extract_user_from_params: bool = True
    custom_success_condition: str | None = None  # Python表达式字符串
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class RouteAuditConfig:
    """路由审计配置"""
    path: str
    method: str = "*"  # * 表示所有方法
    rule: AuditRuleConfig = None
    enabled: bool = True


@dataclass
class AuditConfig:
    """完整的审计配置"""
    enabled: bool = True
    # 全局排除路径
    excluded_paths: list[str] = field(default_factory=lambda: [
        "/docs", "/redoc", "/openapi.json", "/health", "/metrics"
    ])
    # 路由级别的配置
    routes: dict[str, RouteAuditConfig] = field(default_factory=dict)
    # 默认规则
    default_rules: dict[str, AuditRuleConfig] = field(default_factory=dict)
    # 敏感操作（总是记录，即使全局禁用）
    critical_actions: set[ActionType] = field(default_factory=lambda: {
        ActionType.LOGIN, ActionType.LOGOUT, ActionType.USER_DELETE,
        ActionType.ADMIN_OPERATION
    })


class AuditConfigManager:
    """审计配置管理器"""

    def __init__(self, config_path: str | None = None):
        self.config_path = Path(config_path) if config_path else Path("config/audit.json")
        self._config: AuditConfig | None = None
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, encoding="utf-8") as f:
                    config_data = json.load(f)
                self._config = self._parse_config(config_data)
                logger.info(f"审计配置已从 {self.config_path} 加载")
            else:
                self._config = self._get_default_config()
                logger.info("使用默认审计配置")
        except Exception as e:
            logger.error(f"加载审计配置失败: {e}")
            self._config = self._get_default_config()

    def _parse_config(self, config_data: dict) -> AuditConfig:
        """解析配置数据"""
        config = AuditConfig()

        # 基本配置
        config.enabled = config_data.get("enabled", True)
        config.excluded_paths = config_data.get("excluded_paths", config.excluded_paths)

        # 关键操作
        critical_actions = config_data.get("critical_actions", [])
        config.critical_actions = {ActionType(action) for action in critical_actions}

        # 默认规则
        default_rules = config_data.get("default_rules", {})
        for rule_name, rule_data in default_rules.items():
            config.default_rules[rule_name] = AuditRuleConfig(
                action=ActionType(rule_data["action"]),
                description=rule_data["description"],
                resource_type=ResourceType(rule_data["resource_type"]) if rule_data.get("resource_type") else None,
                enabled=rule_data.get("enabled", True),
                extract_user_from_result=rule_data.get("extract_user_from_result", False),
                extract_user_from_params=rule_data.get("extract_user_from_params", True),
                custom_success_condition=rule_data.get("custom_success_condition"),
                metadata=rule_data.get("metadata", {}),
            )

        # 路由配置
        routes = config_data.get("routes", {})
        for route_key, route_data in routes.items():
            rule_data = route_data.get("rule", {})
            rule = AuditRuleConfig(
                action=ActionType(rule_data["action"]),
                description=rule_data["description"],
                resource_type=ResourceType(rule_data["resource_type"]) if rule_data.get("resource_type") else None,
                enabled=rule_data.get("enabled", True),
                extract_user_from_result=rule_data.get("extract_user_from_result", False),
                extract_user_from_params=rule_data.get("extract_user_from_params", True),
                custom_success_condition=rule_data.get("custom_success_condition"),
                metadata=rule_data.get("metadata", {}),
            )

            config.routes[route_key] = RouteAuditConfig(
                path=route_data["path"],
                method=route_data.get("method", "*"),
                rule=rule,
                enabled=route_data.get("enabled", True),
            )

        return config

    def _get_default_config(self) -> AuditConfig:
        """获取默认配置"""
        config = AuditConfig()

        # 默认规则
        config.default_rules = {
            "user_auth": AuditRuleConfig(
                action=ActionType.LOGIN,
                description="用户认证操作",
                resource_type=ResourceType.USER,
                extract_user_from_result=True,
            ),
            "user_management": AuditRuleConfig(
                action=ActionType.USER_MANAGEMENT,
                description="用户管理操作",
                resource_type=ResourceType.USER,
            ),
            "admin_operation": AuditRuleConfig(
                action=ActionType.ADMIN_OPERATION,
                description="管理员操作",
                resource_type=ResourceType.SYSTEM,
            ),
        }

        # 路由配置
        config.routes = {
            "auth_login": RouteAuditConfig(
                path="/api/v1/auth/login",
                method="POST",
                rule=config.default_rules["user_auth"],
            ),
            "auth_logout": RouteAuditConfig(
                path="/api/v1/auth/logout",
                method="POST",
                rule=AuditRuleConfig(
                    action=ActionType.LOGOUT,
                    description="用户退出登录",
                    resource_type=ResourceType.USER,
                ),
            ),
            "auth_register": RouteAuditConfig(
                path="/api/v1/auth/register",
                method="POST",
                rule=AuditRuleConfig(
                    action=ActionType.USER_CREATE,
                    description="用户注册",
                    resource_type=ResourceType.USER,
                    extract_user_from_result=True,
                ),
            ),
        }

        return config

    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # 转换为可序列化的格式
            config_data = self._serialize_config(self._config)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"审计配置已保存到 {self.config_path}")
        except Exception as e:
            logger.error(f"保存审计配置失败: {e}")

    def _serialize_config(self, config: AuditConfig) -> dict:
        """序列化配置对象"""
        return {
            "enabled": config.enabled,
            "excluded_paths": config.excluded_paths,
            "critical_actions": [action.value for action in config.critical_actions],
            "default_rules": {
                name: {
                    "action": rule.action.value,
                    "description": rule.description,
                    "resource_type": rule.resource_type.value if rule.resource_type else None,
                    "enabled": rule.enabled,
                    "extract_user_from_result": rule.extract_user_from_result,
                    "extract_user_from_params": rule.extract_user_from_params,
                    "custom_success_condition": rule.custom_success_condition,
                    "metadata": rule.metadata,
                }
                for name, rule in config.default_rules.items()
            },
            "routes": {
                name: {
                    "path": route.path,
                    "method": route.method,
                    "enabled": route.enabled,
                    "rule": {
                        "action": route.rule.action.value,
                        "description": route.rule.description,
                        "resource_type": route.rule.resource_type.value if route.rule.resource_type else None,
                        "enabled": route.rule.enabled,
                        "extract_user_from_result": route.rule.extract_user_from_result,
                        "extract_user_from_params": route.rule.extract_user_from_params,
                        "custom_success_condition": route.rule.custom_success_condition,
                        "metadata": route.rule.metadata,
                    }
                }
                for name, route in config.routes.items()
            }
        }

    @property
    def config(self) -> AuditConfig:
        """获取当前配置"""
        return self._config

    def is_audit_enabled(self) -> bool:
        """检查审计是否全局启用"""
        return self._config.enabled

    def is_path_excluded(self, path: str) -> bool:
        """检查路径是否被排除"""
        for excluded in self._config.excluded_paths:
            if path.startswith(excluded):
                return True
        return False

    def get_route_config(self, path: str, method: str = "GET") -> RouteAuditConfig | None:
        """获取路由的审计配置"""
        # 精确匹配
        for route_config in self._config.routes.values():
            if (route_config.path == path and
                (route_config.method == "*" or route_config.method.upper() == method.upper())):
                return route_config

        # 前缀匹配
        for route_config in self._config.routes.values():
            if (path.startswith(route_config.path.rstrip("*")) and
                (route_config.method == "*" or route_config.method.upper() == method.upper())):
                return route_config

        return None

    def is_critical_action(self, action: ActionType) -> bool:
        """检查是否为关键操作"""
        return action in self._config.critical_actions

    def get_default_rule(self, rule_name: str) -> AuditRuleConfig | None:
        """获取默认规则"""
        return self._config.default_rules.get(rule_name)

    def add_route_config(self, name: str, config: RouteAuditConfig) -> None:
        """添加路由配置"""
        self._config.routes[name] = config

    def remove_route_config(self, name: str) -> None:
        """移除路由配置"""
        if name in self._config.routes:
            del self._config.routes[name]

    def reload_config(self) -> None:
        """重新加载配置"""
        self._load_config()


# 全局配置管理器实例
_audit_config_manager: AuditConfigManager | None = None


def get_audit_config_manager() -> AuditConfigManager:
    """获取审计配置管理器实例"""
    global _audit_config_manager
    if _audit_config_manager is None:
        _audit_config_manager = AuditConfigManager()
    return _audit_config_manager


def is_audit_enabled_for_action(action: ActionType) -> bool:
    """检查指定操作是否启用审计"""
    manager = get_audit_config_manager()
    if not manager.is_audit_enabled():
        # 即使全局禁用，关键操作也要记录
        return manager.is_critical_action(action)
    return True


def get_audit_rule_for_route(path: str, method: str = "GET") -> AuditRuleConfig | None:
    """获取路由的审计规则"""
    manager = get_audit_config_manager()
    route_config = manager.get_route_config(path, method)
    return route_config.rule if route_config and route_config.enabled else None
