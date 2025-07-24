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

"""审计配置管理器测试用例"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.audit.domain.models import ActionType, ResourceType
from src.audit.shared.config import (
    AuditConfig,
    AuditConfigManager,
    AuditRuleConfig,
    RouteAuditConfig,
    get_audit_config_manager,
    is_audit_enabled_for_action,
    get_audit_rule_for_route
)


class TestAuditRuleConfig:
    """审计规则配置测试"""

    def test_audit_rule_config_creation(self):
        """测试审计规则配置创建"""
        rule = AuditRuleConfig(
            action=ActionType.LOGIN,
            description="用户登录",
            resource_type=ResourceType.USER,
            enabled=True,
            extract_user_from_result=True,
            metadata={"category": "auth"}
        )
        
        assert rule.action == ActionType.LOGIN
        assert rule.description == "用户登录"
        assert rule.resource_type == ResourceType.USER
        assert rule.enabled is True
        assert rule.extract_user_from_result is True
        assert rule.metadata == {"category": "auth"}

    def test_audit_rule_config_defaults(self):
        """测试审计规则配置默认值"""
        rule = AuditRuleConfig(
            action=ActionType.LOGOUT,
            description="用户退出"
        )
        
        assert rule.resource_type is None
        assert rule.enabled is True
        assert rule.extract_user_from_result is False
        assert rule.extract_user_from_params is True
        assert rule.custom_success_condition is None
        assert rule.metadata == {}


class TestRouteAuditConfig:
    """路由审计配置测试"""

    def test_route_audit_config_creation(self):
        """测试路由审计配置创建"""
        rule = AuditRuleConfig(
            action=ActionType.LOGIN,
            description="用户登录"
        )
        
        route_config = RouteAuditConfig(
            path="/api/v1/auth/login",
            method="POST",
            rule=rule,
            enabled=True
        )
        
        assert route_config.path == "/api/v1/auth/login"
        assert route_config.method == "POST"
        assert route_config.rule == rule
        assert route_config.enabled is True


class TestAuditConfig:
    """审计配置测试"""

    def test_audit_config_creation(self):
        """测试审计配置创建"""
        config = AuditConfig(
            enabled=True,
            excluded_paths=["/health", "/metrics"],
            critical_actions={ActionType.LOGIN, ActionType.USER_DELETE}
        )
        
        assert config.enabled is True
        assert "/health" in config.excluded_paths
        assert ActionType.LOGIN in config.critical_actions

    def test_audit_config_defaults(self):
        """测试审计配置默认值"""
        config = AuditConfig()
        
        assert config.enabled is True
        assert "/docs" in config.excluded_paths
        assert "/health" in config.excluded_paths
        assert ActionType.LOGIN in config.critical_actions
        assert ActionType.LOGOUT in config.critical_actions
        assert config.routes == {}
        assert config.default_rules == {}


class TestAuditConfigManager:
    """审计配置管理器测试"""

    def test_config_manager_with_no_file(self):
        """测试无配置文件时的行为"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent_audit.json"
            manager = AuditConfigManager(str(config_path))
            
            # 应该使用默认配置
            assert manager.is_audit_enabled() is True
            assert manager.is_path_excluded("/docs") is True
            assert manager.is_critical_action(ActionType.LOGIN) is True

    def test_config_manager_with_valid_file(self):
        """测试有效配置文件的加载"""
        config_data = {
            "enabled": False,
            "excluded_paths": ["/custom", "/test"],
            "critical_actions": ["login", "user_delete"],
            "default_rules": {
                "test_rule": {
                    "action": "login",
                    "description": "测试登录",
                    "resource_type": "user",
                    "enabled": True,
                    "extract_user_from_result": False,
                    "extract_user_from_params": True,
                    "custom_success_condition": None,
                    "metadata": {"test": "value"}
                }
            },
            "routes": {
                "test_route": {
                    "path": "/test/path",
                    "method": "GET",
                    "enabled": True,
                    "rule": {
                        "action": "login",
                        "description": "测试路由",
                        "resource_type": "user",
                        "enabled": True,
                        "extract_user_from_result": False,
                        "extract_user_from_params": True,
                        "custom_success_condition": None,
                        "metadata": {}
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            manager = AuditConfigManager(config_path)
            
            # 验证配置加载
            assert manager.is_audit_enabled() is False
            assert manager.is_path_excluded("/custom") is True
            assert manager.is_path_excluded("/docs") is False  # 不在自定义排除列表中
            assert manager.is_critical_action(ActionType.LOGIN) is True
            assert manager.is_critical_action(ActionType.LOGOUT) is False  # 不在自定义关键操作列表中
            
            # 验证默认规则
            rule = manager.get_default_rule("test_rule")
            assert rule is not None
            assert rule.action == ActionType.LOGIN
            assert rule.description == "测试登录"
            assert rule.metadata == {"test": "value"}
            
            # 验证路由配置
            route_config = manager.get_route_config("/test/path", "GET")
            assert route_config is not None
            assert route_config.path == "/test/path"
            assert route_config.method == "GET"
            assert route_config.rule.description == "测试路由"
            
        finally:
            Path(config_path).unlink()

    def test_config_manager_with_invalid_file(self):
        """测试无效配置文件的处理"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_path = f.name
        
        try:
            manager = AuditConfigManager(config_path)
            
            # 应该回退到默认配置
            assert manager.is_audit_enabled() is True
            assert manager.is_path_excluded("/docs") is True
            
        finally:
            Path(config_path).unlink()

    def test_save_config(self):
        """测试配置保存"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_audit.json"
            manager = AuditConfigManager(str(config_path))
            
            # 修改配置
            manager.config.enabled = False
            manager.config.excluded_paths.append("/custom")
            
            # 保存配置
            manager.save_config()
            
            # 验证文件存在
            assert config_path.exists()
            
            # 验证保存的内容
            with open(config_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert saved_data["enabled"] is False
            assert "/custom" in saved_data["excluded_paths"]

    def test_route_config_matching(self):
        """测试路由配置匹配"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent_audit.json"
            manager = AuditConfigManager(str(config_path))
            
            # 清除默认路由配置以避免冲突
            manager._config.routes.clear()
            
            # 添加测试路由配置
            rule = AuditRuleConfig(
                action=ActionType.LOGIN,
                description="登录API"
            )
            route_config = RouteAuditConfig(
                path="/api/v1/auth/login",
                method="POST",
                rule=rule
            )
            manager.add_route_config("login_route", route_config)
            
            # 测试精确匹配
            matched = manager.get_route_config("/api/v1/auth/login", "POST")
            assert matched is not None
            assert matched.rule.description == "登录API"
            
            # 测试方法不匹配
            matched = manager.get_route_config("/api/v1/auth/login", "GET")
            assert matched is None
            
            # 测试路径不匹配
            matched = manager.get_route_config("/api/v1/auth/logout", "POST")
            assert matched is None

    def test_wildcard_route_matching(self):
        """测试通配符路由匹配"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent_audit.json"  
            manager = AuditConfigManager(str(config_path))
            
            # 添加通配符路由配置
            rule = AuditRuleConfig(
                action=ActionType.ADMIN_OPERATION,
                description="管理员操作"
            )
            route_config = RouteAuditConfig(
                path="/api/v1/admin/*",
                method="*",
                rule=rule
            )
            manager.add_route_config("admin_routes", route_config)
            
            # 测试前缀匹配
            matched = manager.get_route_config("/api/v1/admin/users", "GET")
            assert matched is not None
            assert matched.rule.description == "管理员操作"
            
            matched = manager.get_route_config("/api/v1/admin/settings/update", "POST")
            assert matched is not None
            
            # 测试不匹配的路径
            matched = manager.get_route_config("/api/v1/public/data", "GET")
            assert matched is None

    def test_add_remove_route_config(self):
        """测试添加和删除路由配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent_audit.json"
            manager = AuditConfigManager(str(config_path))
            
            rule = AuditRuleConfig(
                action=ActionType.USER_CREATE,
                description="创建用户"
            )
            route_config = RouteAuditConfig(
                path="/api/v1/users",
                method="POST",
                rule=rule
            )
            
            # 添加配置
            manager.add_route_config("create_user", route_config)
            assert manager.get_route_config("/api/v1/users", "POST") is not None
            
            # 删除配置
            manager.remove_route_config("create_user")
            assert manager.get_route_config("/api/v1/users", "POST") is None


class TestGlobalFunctions:
    """全局函数测试"""

    def test_get_audit_config_manager_singleton(self):
        """测试配置管理器单例"""
        with patch('src.audit.shared.config._audit_config_manager', None):
            manager1 = get_audit_config_manager()
            manager2 = get_audit_config_manager()
            
            assert manager1 is manager2

    def test_is_audit_enabled_for_action(self):
        """测试操作审计启用检查"""
        with patch('src.audit.shared.config.get_audit_config_manager') as mock_get_manager:
            mock_manager = mock_get_manager.return_value
            
            # 测试全局启用且非关键操作
            mock_manager.is_audit_enabled.return_value = True
            mock_manager.is_critical_action.return_value = False
            
            result = is_audit_enabled_for_action(ActionType.PROFILE_UPDATE)
            assert result is True
            
            # 测试全局禁用但关键操作
            mock_manager.is_audit_enabled.return_value = False
            mock_manager.is_critical_action.return_value = True
            
            result = is_audit_enabled_for_action(ActionType.LOGIN)
            assert result is True
            
            # 测试全局禁用且非关键操作
            mock_manager.is_audit_enabled.return_value = False
            mock_manager.is_critical_action.return_value = False
            
            result = is_audit_enabled_for_action(ActionType.PROFILE_UPDATE)
            assert result is False

    def test_get_audit_rule_for_route(self):
        """测试获取路由审计规则"""
        with patch('src.audit.shared.config.get_audit_config_manager') as mock_get_manager:
            mock_manager = mock_get_manager.return_value
            mock_route_config = RouteAuditConfig(
                path="/test",
                method="GET",
                rule=AuditRuleConfig(
                    action=ActionType.LOGIN,
                    description="测试"
                ),
                enabled=True
            )
            
            # 测试启用的路由
            mock_manager.get_route_config.return_value = mock_route_config
            
            rule = get_audit_rule_for_route("/test", "GET")
            assert rule is not None
            assert rule.description == "测试"
            
            # 测试禁用的路由
            mock_route_config.enabled = False
            
            rule = get_audit_rule_for_route("/test", "GET")
            assert rule is None
            
            # 测试不存在的路由
            mock_manager.get_route_config.return_value = None
            
            rule = get_audit_rule_for_route("/nonexistent", "GET")
            assert rule is None