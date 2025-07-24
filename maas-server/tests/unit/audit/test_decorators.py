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

"""审计装饰器测试用例"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from fastapi import Request
from fastapi.testclient import TestClient

from src.audit.domain.models import ActionType, AuditResult, ResourceType
from src.audit.shared.decorators import audit_log, audit_user_operation, audit_resource_operation
from src.shared.application.response import ApiResponse


class TestAuditDecorator:
    """审计装饰器测试类"""

    @pytest.fixture
    def mock_request(self):
        """模拟Request对象"""
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        request.state = MagicMock()
        request.state.request_id = "test-request-id"
        return request

    @pytest.fixture
    def mock_log_user_action(self):
        """模拟log_user_action函数"""
        with patch('src.audit.shared.decorators.log_user_action') as mock:
            mock.return_value = AsyncMock()
            yield mock

    @pytest.fixture
    def mock_audit_enabled(self):
        """模拟审计启用检查"""
        with patch('src.audit.shared.decorators.is_audit_enabled_for_action') as mock:
            mock.return_value = True
            yield mock

    @pytest.mark.asyncio
    async def test_audit_log_success(self, mock_request, mock_log_user_action, mock_audit_enabled):
        """测试审计装饰器成功场景"""
        
        @audit_log(
            action=ActionType.LOGIN,
            description="测试登录",
            resource_type=ResourceType.USER
        )
        async def test_function(request: Request, user_id: UUID):
            return ApiResponse.success_response({"id": user_id, "username": "testuser"}, "成功")
        
        user_id = uuid4()
        result = await test_function(mock_request, user_id)
        
        # 验证函数正常执行
        assert result.success is True
        assert result.data["id"] == user_id
        
        # 验证审计日志被记录
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["action"] == ActionType.LOGIN
        assert call_args[1]["description"] == "测试登录"
        assert call_args[1]["resource_type"] == ResourceType.USER
        assert call_args[1]["result"] == AuditResult.SUCCESS
        assert call_args[1]["user_id"] == user_id
        assert call_args[1]["ip_address"] == "127.0.0.1"
        assert call_args[1]["user_agent"] == "test-agent"
        assert call_args[1]["request_id"] == "test-request-id"

    @pytest.mark.asyncio
    async def test_audit_log_failure(self, mock_request, mock_log_user_action, mock_audit_enabled):
        """测试审计装饰器异常场景"""
        
        @audit_log(
            action=ActionType.LOGIN,
            description="测试登录",
            resource_type=ResourceType.USER
        )
        async def test_function(request: Request):
            raise ValueError("测试异常")
        
        # 验证异常被重新抛出
        with pytest.raises(ValueError, match="测试异常"):
            await test_function(mock_request)
        
        # 验证失败的审计日志被记录
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["action"] == ActionType.LOGIN
        assert call_args[1]["result"] == AuditResult.FAILURE
        assert call_args[1]["error_message"] == "测试异常"
        assert "操作失败" in call_args[1]["description"]

    @pytest.mark.asyncio
    async def test_audit_disabled(self, mock_request, mock_log_user_action):
        """测试审计禁用场景"""
        
        with patch('src.audit.shared.decorators.is_audit_enabled_for_action', return_value=False):
            @audit_log(
                action=ActionType.LOGIN,
                description="测试登录"
            )
            async def test_function(request: Request):
                return {"result": "ok"}
            
            result = await test_function(mock_request)
            
            # 验证函数正常执行
            assert result == {"result": "ok"}
            
            # 验证审计日志没有被记录
            mock_log_user_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_user_from_result(self, mock_request, mock_log_user_action, mock_audit_enabled):
        """测试从结果中提取用户信息"""
        
        @audit_log(
            action=ActionType.USER_CREATE,
            description="创建用户",
            extract_user_from_result=True
        )
        async def test_function(request: Request):
            user_id = uuid4()
            return ApiResponse.success_response({
                "id": user_id,
                "username": "newuser"
            }, "创建成功")
        
        result = await test_function(mock_request)
        
        # 验证用户信息被正确提取
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["user_id"] == result.data["id"]
        assert call_args[1]["username"] == "newuser"

    @pytest.mark.asyncio
    async def test_custom_success_condition(self, mock_request, mock_log_user_action, mock_audit_enabled):
        """测试自定义成功条件"""
        
        @audit_log(
            action=ActionType.LOGIN,
            description="测试登录",
            success_condition=lambda result: result.get("status") == "ok"
        )
        async def test_function(request: Request):
            return {"status": "error", "message": "登录失败"}
        
        result = await test_function(mock_request)
        
        # 验证自定义成功条件生效
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["result"] == AuditResult.FAILURE
        assert call_args[1]["error_message"] == "操作未满足成功条件"

    @pytest.mark.asyncio
    async def test_custom_description(self, mock_request, mock_log_user_action, mock_audit_enabled):
        """测试自定义描述生成"""
        
        @audit_log(
            action=ActionType.LOGIN,
            description="默认描述",
            custom_description=lambda request, username, **kwargs: f"用户 {username} 登录系统"
        )
        async def test_function(request: Request, username: str):
            return {"result": "ok"}
        
        await test_function(mock_request, "testuser")
        
        # 验证自定义描述被使用
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["description"] == "用户 testuser 登录系统"

    @pytest.mark.asyncio
    async def test_extract_resource_id(self, mock_request, mock_log_user_action, mock_audit_enabled):
        """测试资源ID提取"""
        
        resource_id = uuid4()
        
        @audit_log(
            action=ActionType.USER_UPDATE,
            description="更新用户",
            resource_type=ResourceType.USER,
            extract_resource_id=lambda request, user_id: user_id
        )
        async def test_function(request: Request, user_id: UUID):
            return {"result": "updated"}
        
        await test_function(mock_request, resource_id)
        
        # 验证资源ID被提取
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["resource_id"] == resource_id


class TestAuditUserOperation:
    """用户操作审计装饰器测试"""

    @pytest.fixture
    def mock_request(self):
        """模拟Request对象"""
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        request.state = MagicMock()
        request.state.request_id = "test-request-id"
        return request

    @pytest.fixture
    def mock_log_user_action(self):
        """模拟log_user_action函数"""
        with patch('src.audit.shared.decorators.log_user_action') as mock:
            mock.return_value = AsyncMock()
            yield mock

    @pytest.fixture
    def mock_audit_enabled(self):
        """模拟审计启用检查"""
        with patch('src.audit.shared.decorators.is_audit_enabled_for_action') as mock:
            mock.return_value = True
            yield mock

    @pytest.mark.asyncio
    async def test_user_operation_decorator(self, mock_request, mock_log_user_action, mock_audit_enabled):
        """测试用户操作装饰器"""
        
        @audit_user_operation(
            action=ActionType.LOGOUT,
            description="用户退出登录"
        )
        async def logout_function(request: Request, user_id: UUID):
            return {"result": "logged_out"}
        
        user_id = uuid4()
        result = await logout_function(mock_request, user_id)
        
        # 验证函数正常执行
        assert result == {"result": "logged_out"}
        
        # 验证审计日志记录
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["action"] == ActionType.LOGOUT
        assert call_args[1]["description"] == "用户退出登录"
        assert call_args[1]["resource_type"] == ResourceType.USER
        assert call_args[1]["user_id"] == user_id


class TestAuditResourceOperation:
    """资源操作审计装饰器测试"""

    @pytest.fixture
    def mock_request(self):
        """模拟Request对象"""
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        request.state = MagicMock()
        request.state.request_id = "test-request-id"
        return request

    @pytest.fixture
    def mock_log_user_action(self):
        """模拟log_user_action函数"""
        with patch('src.audit.shared.decorators.log_user_action') as mock:
            mock.return_value = AsyncMock()
            yield mock

    @pytest.fixture
    def mock_audit_enabled(self):
        """模拟审计启用检查"""
        with patch('src.audit.shared.decorators.is_audit_enabled_for_action') as mock:
            mock.return_value = True
            yield mock

    @pytest.mark.asyncio
    async def test_resource_operation_decorator(self, mock_request, mock_log_user_action, mock_audit_enabled):
        """测试资源操作装饰器"""
        
        @audit_resource_operation(
            action=ActionType.MODEL_CREATE,
            resource_type=ResourceType.MODEL
        )
        async def create_model_function(request: Request, model_id: UUID):
            return {"model_id": model_id, "status": "created"}
        
        model_id = uuid4()
        result = await create_model_function(mock_request, model_id)
        
        # 验证函数正常执行
        assert result["model_id"] == model_id
        assert result["status"] == "created"
        
        # 验证审计日志记录
        mock_log_user_action.assert_called_once()
        call_args = mock_log_user_action.call_args
        assert call_args[1]["action"] == ActionType.MODEL_CREATE
        assert call_args[1]["resource_type"] == ResourceType.MODEL
        assert "model_create" in call_args[1]["description"]
        assert "model" in call_args[1]["description"]