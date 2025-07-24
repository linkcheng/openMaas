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

"""审计中间件测试用例"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from src.audit.domain.models import ActionType, AuditResult, ResourceType
from src.audit.shared.middleware import RequestContextMiddleware, AutoAuditMiddleware
from src.audit.shared.config import AuditRuleConfig, RouteAuditConfig


class TestRequestContextMiddleware:
    """请求上下文中间件测试"""

    @pytest.fixture
    def app_with_middleware(self):
        """创建带中间件的测试应用"""
        app = FastAPI()
        app.add_middleware(RequestContextMiddleware)
        
        @app.get("/test")
        async def test_endpoint(request: Request):
            return {
                "request_id": getattr(request.state, "request_id", None),
                "client_ip": getattr(request.state, "client_ip", None),
                "user_agent": getattr(request.state, "user_agent", None),
                "start_time": getattr(request.state, "start_time", None),
            }
        
        return app

    def test_request_context_middleware(self, app_with_middleware):
        """测试请求上下文中间件功能"""
        client = TestClient(app_with_middleware)
        
        response = client.get("/test", headers={"user-agent": "test-client"})
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证请求ID生成
        assert data["request_id"] is not None
        assert len(data["request_id"]) > 0
        
        # 验证客户端IP提取
        assert data["client_ip"] is not None
        
        # 验证User-Agent提取
        assert data["user_agent"] == "test-client"
        
        # 验证开始时间记录
        assert data["start_time"] is not None
        
        # 验证响应头
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers
        assert response.headers["X-Request-ID"] == data["request_id"]

    def test_client_ip_extraction(self, app_with_middleware):
        """测试客户端IP提取"""
        client = TestClient(app_with_middleware)
        
        # 测试X-Forwarded-For头
        response = client.get("/test", headers={
            "x-forwarded-for": "192.168.1.100, 10.0.0.1",
            "x-real-ip": "172.16.0.1"
        })
        
        data = response.json()
        # 应该使用X-Forwarded-For的第一个IP
        assert data["client_ip"] == "192.168.1.100"
        
        # 测试X-Real-IP头（当没有X-Forwarded-For时）
        response = client.get("/test", headers={
            "x-real-ip": "172.16.0.1"
        })
        
        data = response.json()
        assert data["client_ip"] == "172.16.0.1"

    def test_middleware_exception_handling(self, app_with_middleware):
        """测试中间件异常处理"""
        app = app_with_middleware
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("测试异常")
        
        client = TestClient(app)
        
        with pytest.raises(ValueError):
            client.get("/error")


class TestAutoAuditMiddleware:
    """自动审计中间件测试"""

    @pytest.fixture
    def mock_config_manager(self):
        """模拟配置管理器"""
        with patch('src.audit.shared.middleware.get_audit_config_manager') as mock:
            manager = MagicMock()
            manager.is_audit_enabled.return_value = True
            manager.is_path_excluded.return_value = False
            mock.return_value = manager
            yield manager

    @pytest.fixture
    def mock_log_user_action(self):
        """模拟审计日志记录函数"""
        with patch('src.audit.shared.middleware.log_user_action') as mock:
            mock.return_value = AsyncMock()
            yield mock

    @pytest.fixture
    def app_with_audit_middleware(self, mock_config_manager):
        """创建带审计中间件的测试应用"""
        app = FastAPI()
        app.add_middleware(RequestContextMiddleware)
        app.add_middleware(AutoAuditMiddleware)
        
        @app.get("/api/v1/test")
        async def test_endpoint():
            return {"message": "success"}
        
        @app.get("/api/v1/error")
        async def error_endpoint():
            raise ValueError("测试异常")
        
        return app

    def test_auto_audit_middleware_success(self, app_with_audit_middleware, mock_config_manager, mock_log_user_action):
        """测试自动审计中间件成功场景"""
        # 设置路由配置
        rule = AuditRuleConfig(
            action=ActionType.LOGIN,
            description="测试API访问",
            resource_type=ResourceType.SYSTEM,
            metadata={"category": "test"}
        )
        route_config = RouteAuditConfig(
            path="/api/v1/test",
            method="GET",
            rule=rule,
            enabled=True
        )
        mock_config_manager.get_route_config.return_value = route_config
        
        client = TestClient(app_with_audit_middleware)
        response = client.get("/api/v1/test")
        
        assert response.status_code == 200
        
        # 验证审计日志被记录
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["action"] == ActionType.LOGIN
        assert call_args[1]["description"] == "测试API访问"
        assert call_args[1]["resource_type"] == ResourceType.SYSTEM
        assert call_args[1]["result"] == AuditResult.SUCCESS
        assert call_args[1]["metadata"]["auto_audit"] is True
        assert call_args[1]["metadata"]["category"] == "test"
        assert call_args[1]["metadata"]["method"] == "GET"
        assert call_args[1]["metadata"]["path"] == "/api/v1/test"
        assert call_args[1]["metadata"]["status_code"] == 200

    def test_auto_audit_middleware_failure(self, app_with_audit_middleware, mock_config_manager, mock_log_user_action):
        """测试自动审计中间件异常场景"""
        # 设置路由配置
        rule = AuditRuleConfig(
            action=ActionType.ADMIN_OPERATION,
            description="错误API访问",
            resource_type=ResourceType.SYSTEM
        )
        route_config = RouteAuditConfig(
            path="/api/v1/error",
            method="GET",
            rule=rule,
            enabled=True
        )
        mock_config_manager.get_route_config.return_value = route_config
        
        client = TestClient(app_with_audit_middleware)
        
        with pytest.raises(ValueError):
            client.get("/api/v1/error")
        
        # 验证失败的审计日志被记录
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["action"] == ActionType.ADMIN_OPERATION
        assert call_args[1]["description"] == "错误API访问 - 请求异常"
        assert call_args[1]["result"] == AuditResult.FAILURE
        assert call_args[1]["error_message"] == "测试异常"
        assert call_args[1]["metadata"]["auto_audit"] is True
        assert call_args[1]["metadata"]["exception"] == "ValueError"

    def test_auto_audit_middleware_disabled_globally(self, app_with_audit_middleware, mock_config_manager, mock_log_user_action):
        """测试全局审计禁用"""
        mock_config_manager.is_audit_enabled.return_value = False
        
        client = TestClient(app_with_audit_middleware)
        response = client.get("/api/v1/test")
        
        assert response.status_code == 200
        
        # 验证审计日志没有被记录
        mock_log_user_action.assert_not_called()

    def test_auto_audit_middleware_excluded_path(self, app_with_audit_middleware, mock_config_manager, mock_log_user_action):
        """测试排除路径"""
        mock_config_manager.is_path_excluded.return_value = True
        
        client = TestClient(app_with_audit_middleware)
        response = client.get("/api/v1/test")
        
        assert response.status_code == 200
        
        # 验证审计日志没有被记录
        mock_log_user_action.assert_not_called()

    def test_auto_audit_middleware_no_route_config(self, app_with_audit_middleware, mock_config_manager, mock_log_user_action):
        """测试无路由配置"""
        mock_config_manager.get_route_config.return_value = None
        
        client = TestClient(app_with_audit_middleware)
        response = client.get("/api/v1/test")
        
        assert response.status_code == 200
        
        # 验证审计日志没有被记录
        mock_log_user_action.assert_not_called()

    def test_auto_audit_middleware_disabled_route(self, app_with_audit_middleware, mock_config_manager, mock_log_user_action):
        """测试禁用的路由"""
        rule = AuditRuleConfig(
            action=ActionType.LOGIN,
            description="测试API访问"
        )
        route_config = RouteAuditConfig(
            path="/api/v1/test",
            method="GET",
            rule=rule,
            enabled=False  # 路由配置禁用
        )
        mock_config_manager.get_route_config.return_value = route_config
        
        client = TestClient(app_with_audit_middleware)
        response = client.get("/api/v1/test")
        
        assert response.status_code == 200
        
        # 验证审计日志没有被记录
        mock_log_user_action.assert_not_called()

    def test_auto_audit_middleware_http_error_status(self, mock_config_manager, mock_log_user_action):
        """测试HTTP错误状态码"""
        app = FastAPI()
        app.add_middleware(RequestContextMiddleware)
        app.add_middleware(AutoAuditMiddleware)
        
        @app.get("/api/v1/not-found")
        async def not_found_endpoint():
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # 设置路由配置
        rule = AuditRuleConfig(
            action=ActionType.ADMIN_OPERATION,
            description="API访问"
        )
        route_config = RouteAuditConfig(
            path="/api/v1/not-found",
            method="GET",
            rule=rule,
            enabled=True
        )
        mock_config_manager.get_route_config.return_value = route_config
        
        client = TestClient(app)
        response = client.get("/api/v1/not-found")
        
        assert response.status_code == 404
        
        # 验证失败的审计日志被记录
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["result"] == AuditResult.FAILURE
        assert call_args[1]["error_message"] == "HTTP 404"
        assert call_args[1]["metadata"]["status_code"] == 404