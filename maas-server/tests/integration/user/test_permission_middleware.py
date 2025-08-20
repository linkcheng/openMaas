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

"""权限中间件集成测试"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from user.application.auth_service import AuthService
from user.application.permission_service import PermissionService
from user.domain.models import User, Role, Permission, PermissionName, RoleType
from user.domain.repositories import IUserRepository
from user.infrastructure.audit_logger import AuditLogger
from user.infrastructure.permission_middleware import PermissionMiddleware


@pytest.fixture
def mock_auth_service():
    """模拟认证服务"""
    service = AsyncMock(spec=AuthService)
    return service


@pytest.fixture
def mock_permission_service():
    """模拟权限服务"""
    service = AsyncMock(spec=PermissionService)
    return service


@pytest.fixture
def mock_user_repository():
    """模拟用户仓储"""
    repository = AsyncMock(spec=IUserRepository)
    return repository


@pytest.fixture
def mock_audit_logger():
    """模拟审计日志服务"""
    logger = AsyncMock(spec=AuditLogger)
    return logger


@pytest.fixture
def test_user():
    """测试用户"""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "testuser"
    user.is_active = True
    user.roles = []
    return user


@pytest.fixture
def test_app(
    mock_auth_service,
    mock_permission_service,
    mock_user_repository,
    mock_audit_logger
):
    """测试应用"""
    app = FastAPI()
    
    # 添加权限中间件
    middleware = PermissionMiddleware(
        app=app,
        auth_service=mock_auth_service,
        permission_service=mock_permission_service,
        user_repository=mock_user_repository,
        audit_logger=mock_audit_logger
    )
    app.add_middleware(PermissionMiddleware, **{
        "auth_service": mock_auth_service,
        "permission_service": mock_permission_service,
        "user_repository": mock_user_repository,
        "audit_logger": mock_audit_logger
    })
    
    # 添加测试路由
    @app.get("/api/v1/users")
    async def get_users():
        return {"users": []}
    
    @app.post("/api/v1/users")
    async def create_user():
        return {"message": "User created"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    @app.get("/api/v1/auth/login")
    async def login():
        return {"token": "test_token"}
    
    return app


class TestPermissionMiddleware:
    """权限中间件测试"""

    def test_excluded_paths_skip_auth(self, test_app):
        """测试排除路径跳过权限验证"""
        client = TestClient(test_app)
        
        # 健康检查不需要权限
        response = client.get("/health")
        assert response.status_code == 200
        
        # 登录接口不需要权限
        response = client.get("/api/v1/auth/login")
        assert response.status_code == 200

    def test_missing_token_returns_401(self, test_app):
        """测试缺少token返回401"""
        client = TestClient(test_app)
        
        response = client.get("/api/v1/users")
        assert response.status_code == 401
        assert "MISSING_TOKEN" in response.json()["error"]["code"]

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(
        self,
        test_app,
        mock_auth_service
    ):
        """测试无效token返回401"""
        # 模拟token验证失败
        mock_auth_service.verify_token.side_effect = Exception("Invalid token")
        
        client = TestClient(test_app)
        
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_user_not_found_returns_401(
        self,
        test_app,
        mock_auth_service,
        mock_user_repository
    ):
        """测试用户不存在返回401"""
        # 模拟token验证成功但用户不存在
        mock_auth_service.verify_token.return_value = {
            "sub": str(uuid4()),
            "permissions": []
        }
        mock_user_repository.find_by_id.return_value = None
        
        client = TestClient(test_app)
        
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 401
        assert "USER_NOT_FOUND" in response.json()["error"]["code"]

    @pytest.mark.asyncio
    async def test_inactive_user_returns_403(
        self,
        test_app,
        mock_auth_service,
        mock_user_repository,
        test_user
    ):
        """测试非活跃用户返回403"""
        # 设置用户为非活跃状态
        test_user.is_active = False
        
        # 模拟token验证成功
        mock_auth_service.verify_token.return_value = {
            "sub": str(test_user.id),
            "permissions": []
        }
        mock_user_repository.find_by_id.return_value = test_user
        
        client = TestClient(test_app)
        
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 403
        assert "USER_INACTIVE" in response.json()["error"]["code"]

    @pytest.mark.asyncio
    async def test_insufficient_permission_returns_403(
        self,
        test_app,
        mock_auth_service,
        mock_permission_service,
        mock_user_repository,
        mock_audit_logger,
        test_user
    ):
        """测试权限不足返回403"""
        # 模拟token验证成功
        mock_auth_service.verify_token.return_value = {
            "sub": str(test_user.id),
            "permissions": []
        }
        mock_user_repository.find_by_id.return_value = test_user
        
        # 模拟权限检查失败
        mock_permission_service.check_user_permission.return_value = False
        
        client = TestClient(test_app)
        
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 403
        assert "INSUFFICIENT_PERMISSION" in response.json()["error"]["code"]
        
        # 验证审计日志被调用
        mock_audit_logger.log_permission_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_successful_request_with_permission(
        self,
        test_app,
        mock_auth_service,
        mock_permission_service,
        mock_user_repository,
        test_user
    ):
        """测试有权限的成功请求"""
        # 模拟token验证成功
        mock_auth_service.verify_token.return_value = {
            "sub": str(test_user.id),
            "permissions": ["user.users.view"]
        }
        mock_user_repository.find_by_id.return_value = test_user
        
        # 模拟权限检查成功
        mock_permission_service.check_user_permission.return_value = True
        
        client = TestClient(test_app)
        
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_permission_inference_from_path_and_method(
        self,
        test_app,
        mock_auth_service,
        mock_permission_service,
        mock_user_repository,
        test_user
    ):
        """测试从路径和方法推断权限"""
        # 模拟token验证成功
        mock_auth_service.verify_token.return_value = {
            "sub": str(test_user.id),
            "permissions": []
        }
        mock_user_repository.find_by_id.return_value = test_user
        
        # 模拟权限检查成功
        mock_permission_service.check_user_permission.return_value = True
        
        client = TestClient(test_app)
        
        # 测试GET请求推断为view权限
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": "Bearer valid_token"}
        )
        mock_permission_service.check_user_permission.assert_called_with(
            user_id=test_user.id,
            permission_name="user.users.view"
        )
        
        # 测试POST请求推断为create权限
        response = client.post(
            "/api/v1/users",
            headers={"Authorization": "Bearer valid_token"}
        )
        mock_permission_service.check_user_permission.assert_called_with(
            user_id=test_user.id,
            permission_name="user.users.create"
        )

    def test_client_ip_extraction(self, test_app):
        """测试客户端IP提取"""
        client = TestClient(test_app)
        
        # 测试X-Forwarded-For头
        response = client.get(
            "/health",
            headers={"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        )
        assert response.status_code == 200
        
        # 测试X-Real-IP头
        response = client.get(
            "/health",
            headers={"X-Real-IP": "192.168.1.2"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sensitive_operation_detection(
        self,
        test_app,
        mock_auth_service,
        mock_permission_service,
        mock_user_repository,
        test_user
    ):
        """测试敏感操作检测"""
        # 模拟token验证成功
        mock_auth_service.verify_token.return_value = {
            "sub": str(test_user.id),
            "permissions": []
        }
        mock_user_repository.find_by_id.return_value = test_user
        mock_permission_service.check_user_permission.return_value = True
        
        client = TestClient(test_app)
        
        # POST请求到用户管理接口应该被标记为敏感操作
        response = client.post(
            "/api/v1/users",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_token_refresh_required_exception(
        self,
        test_app,
        mock_auth_service
    ):
        """测试token刷新异常"""
        from shared.application.exceptions import TokenRefreshRequiredException
        
        # 模拟token过期
        mock_auth_service.verify_token.side_effect = TokenRefreshRequiredException("Token expired")
        
        client = TestClient(test_app)
        
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": "Bearer expired_token"}
        )
        assert response.status_code == 401
        assert "TOKEN_EXPIRED" in response.json()["error"]["code"]

    @pytest.mark.asyncio
    async def test_token_version_mismatch_exception(
        self,
        test_app,
        mock_auth_service
    ):
        """测试token版本不匹配异常"""
        from shared.application.exceptions import TokenVersionMismatchException
        
        # 模拟token版本不匹配
        mock_auth_service.verify_token.side_effect = TokenVersionMismatchException()
        
        client = TestClient(test_app)
        
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": "Bearer old_version_token"}
        )
        assert response.status_code == 401
        assert "TOKEN_VERSION_MISMATCH" in response.json()["error"]["code"]

    def test_request_id_generation(self, test_app):
        """测试请求ID生成"""
        client = TestClient(test_app)
        
        response = client.get("/health")
        assert response.status_code == 200
        
        # 检查响应中是否包含请求ID（如果有错误的话）
        # 正常响应不会包含请求ID，但错误响应会包含

    @pytest.mark.asyncio
    async def test_access_logging(
        self,
        test_app,
        mock_auth_service,
        mock_permission_service,
        mock_user_repository,
        test_user
    ):
        """测试访问日志记录"""
        # 模拟成功的权限验证
        mock_auth_service.verify_token.return_value = {
            "sub": str(test_user.id),
            "permissions": ["user.users.view"]
        }
        mock_user_repository.find_by_id.return_value = test_user
        mock_permission_service.check_user_permission.return_value = True
        
        client = TestClient(test_app)
        
        with patch("user.infrastructure.permission_middleware.logger") as mock_logger:
            response = client.get(
                "/api/v1/users",
                headers={"Authorization": "Bearer valid_token"}
            )
            assert response.status_code == 200
            
            # 验证访问日志被记录
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args[0][0]
            assert "权限访问成功" in log_call
            assert test_user.username in log_call