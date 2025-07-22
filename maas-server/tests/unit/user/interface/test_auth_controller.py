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

"""用户接口层 - 认证控制器测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from user.interface.auth_controller import register
from user.application.schemas import UserCreateRequest, UserResponse
from user.domain.models import UserAlreadyExistsException
from shared.application.response import ApiResponse


class TestRegisterController:
    """用户注册控制器测试"""

    @pytest.fixture
    def mock_user_service(self):
        """模拟用户应用服务"""
        return AsyncMock()

    @pytest.fixture
    def mock_email_service(self):
        """模拟邮件服务"""
        return AsyncMock()

    @pytest.fixture
    def mock_background_tasks(self):
        """模拟后台任务"""
        return MagicMock()

    @pytest.fixture
    def valid_register_request(self):
        """有效的注册请求"""
        return UserCreateRequest(
            username="testuser123",
            email="test@example.com",
            password="SecurePass123",
            first_name="Test",
            last_name="User",
            organization="Test Org"
        )

    @pytest.fixture
    def mock_user_response(self):
        """模拟用户响应"""
        from uuid import uuid4
        from datetime import datetime
        from user.domain.models import UserStatus
        from user.application.schemas import UserProfileResponse, UserQuotaResponse

        profile = UserProfileResponse(
            first_name="Test",
            last_name="User",
            full_name="Test User",
            avatar_url=None,
            organization="Test Org",
            bio=None
        )

        quota = UserQuotaResponse(
            api_calls_limit=1000,
            api_calls_used=0,
            api_calls_remaining=1000,
            api_usage_percentage=0.0,
            storage_limit=1073741824,  # 1GB
            storage_used=0,
            storage_remaining=1073741824,
            storage_usage_percentage=0.0,
            compute_hours_limit=10,
            compute_hours_used=0,
            compute_hours_remaining=10
        )

        return UserResponse(
            id=uuid4(),
            username="testuser123",
            email="test@example.com",
            profile=profile,
            status=UserStatus.ACTIVE,
            email_verified=False,
            roles=[],
            quota=quota,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_login_at=None
        )

    @pytest.mark.asyncio
    async def test_register_success(
        self,
        valid_register_request,
        mock_user_response,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试成功注册"""
        # 安排
        mock_user_service.create_user.return_value = mock_user_response

        # 执行
        response = await register(
            valid_register_request,
            mock_background_tasks,
            mock_user_service,
            mock_email_service
        )

        # 验证
        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert response.data == mock_user_response
        assert "注册成功" in response.message

        # 验证服务调用
        mock_user_service.create_user.assert_called_once()
        create_command = mock_user_service.create_user.call_args[0][0]
        assert create_command.username == valid_register_request.username
        assert create_command.email == valid_register_request.email
        assert create_command.first_name == valid_register_request.first_name
        assert create_command.last_name == valid_register_request.last_name
        assert create_command.organization == valid_register_request.organization
        
        # 验证密码已被哈希
        assert create_command.password_hash != valid_register_request.password
        assert len(create_command.password_hash) > 0

        # 验证后台任务
        assert mock_background_tasks.add_task.call_count == 2  # 验证邮件 + 欢迎邮件

    @pytest.mark.asyncio
    async def test_register_username_too_short(
        self,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试用户名过短"""
        # 安排 - 构造一个模拟请求，绕过Pydantic验证
        request = MagicMock()
        request.username = "ab"  # 只有2个字符
        request.email = "test@example.com"
        request.password = "SecurePass123"
        request.first_name = "Test"
        request.last_name = "User"
        request.organization = None

        # 执行与验证
        with pytest.raises(HTTPException) as exc_info:
            await register(request, mock_background_tasks, mock_user_service, mock_email_service)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户名长度必须在3-50个字符之间" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_username_invalid_characters(
        self,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试用户名包含无效字符"""
        # 安排
        request = UserCreateRequest(
            username="test-user!",  # 包含连字符和感叹号
            email="test@example.com",
            password="SecurePass123",
            first_name="Test",
            last_name="User"
        )

        # 执行与验证
        with pytest.raises(HTTPException) as exc_info:
            await register(request, mock_background_tasks, mock_user_service, mock_email_service)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户名只能包含字母、数字和下划线" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_password_too_short(
        self,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试密码过短"""
        # 安排 - 构造一个模拟请求，绕过Pydantic验证
        request = MagicMock()
        request.username = "testuser"
        request.email = "test@example.com"
        request.password = "1234567"  # 只有7个字符
        request.first_name = "Test"
        request.last_name = "User"
        request.organization = None

        # 执行与验证
        with pytest.raises(HTTPException) as exc_info:
            await register(request, mock_background_tasks, mock_user_service, mock_email_service)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "密码至少需要8个字符" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_password_missing_uppercase(
        self,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试密码缺少大写字母"""
        # 安排 - 构造一个模拟请求，绕过Pydantic验证
        request = MagicMock()
        request.username = "testuser"
        request.email = "test@example.com"
        request.password = "lowercase123"  # 缺少大写字母
        request.first_name = "Test"
        request.last_name = "User"
        request.organization = None

        # 执行与验证
        with pytest.raises(HTTPException) as exc_info:
            await register(request, mock_background_tasks, mock_user_service, mock_email_service)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "密码必须包含大写字母、小写字母和数字" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_password_missing_lowercase(
        self,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试密码缺少小写字母"""
        # 安排 - 构造一个模拟请求，绕过Pydantic验证
        request = MagicMock()
        request.username = "testuser"
        request.email = "test@example.com"
        request.password = "UPPERCASE123"  # 缺少小写字母
        request.first_name = "Test"
        request.last_name = "User"
        request.organization = None

        # 执行与验证
        with pytest.raises(HTTPException) as exc_info:
            await register(request, mock_background_tasks, mock_user_service, mock_email_service)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "密码必须包含大写字母、小写字母和数字" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_password_missing_number(
        self,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试密码缺少数字"""
        # 安排 - 构造一个模拟请求，绕过Pydantic验证
        request = MagicMock()
        request.username = "testuser"
        request.email = "test@example.com"
        request.password = "NoNumberPass"  # 缺少数字
        request.first_name = "Test"
        request.last_name = "User"
        request.organization = None

        # 执行与验证
        with pytest.raises(HTTPException) as exc_info:
            await register(request, mock_background_tasks, mock_user_service, mock_email_service)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "密码必须包含大写字母、小写字母和数字" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_user_already_exists(
        self,
        valid_register_request,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试用户已存在的情况"""
        # 安排
        mock_user_service.create_user.side_effect = UserAlreadyExistsException("用户名 testuser123 已被使用")

        # 执行与验证
        with pytest.raises(HTTPException) as exc_info:
            await register(valid_register_request, mock_background_tasks, mock_user_service, mock_email_service)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "用户名 testuser123 已被使用" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_unexpected_error(
        self,
        valid_register_request,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试意外错误的处理"""
        # 安排
        mock_user_service.create_user.side_effect = Exception("数据库连接失败")

        # 执行与验证
        with pytest.raises(HTTPException) as exc_info:
            await register(valid_register_request, mock_background_tasks, mock_user_service, mock_email_service)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "注册失败，请稍后重试" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_with_optional_organization(
        self,
        mock_user_response,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试包含可选组织字段的注册"""
        # 安排
        request = UserCreateRequest(
            username="testuser123",
            email="test@example.com",
            password="SecurePass123",
            first_name="Test",
            last_name="User",
            organization="My Company"
        )
        mock_user_service.create_user.return_value = mock_user_response

        # 执行
        response = await register(request, mock_background_tasks, mock_user_service, mock_email_service)

        # 验证
        assert response.success is True
        create_command = mock_user_service.create_user.call_args[0][0]
        assert create_command.organization == "My Company"

    @pytest.mark.asyncio
    async def test_register_without_organization(
        self,
        mock_user_response,
        mock_user_service,
        mock_email_service,
        mock_background_tasks
    ):
        """测试不包含组织字段的注册"""
        # 安排
        request = UserCreateRequest(
            username="testuser123",
            email="test@example.com",
            password="SecurePass123",
            first_name="Test",
            last_name="User"
        )
        mock_user_service.create_user.return_value = mock_user_response

        # 执行
        response = await register(request, mock_background_tasks, mock_user_service, mock_email_service)

        # 验证
        assert response.success is True
        create_command = mock_user_service.create_user.call_args[0][0]
        assert create_command.organization is None