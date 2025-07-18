"""测试配置文件"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

# 异步测试设置
@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# 测试数据库设置
@pytest.fixture
async def test_db_session() -> AsyncGenerator:
    """测试数据库会话"""
    # 这里可以创建测试数据库会话
    # 为了单元测试，我们使用Mock
    session = AsyncMock()
    yield session


# 仓储Mock
@pytest.fixture
def mock_user_repository():
    """用户仓储Mock"""
    return AsyncMock()


@pytest.fixture
def mock_role_repository():
    """角色仓储Mock"""
    return AsyncMock()


@pytest.fixture
def mock_api_key_repository():
    """API密钥仓储Mock"""
    return AsyncMock()


# 服务Mock
@pytest.fixture
def mock_email_service():
    """邮件服务Mock"""
    return MagicMock()


@pytest.fixture
def mock_password_service():
    """密码服务Mock"""
    return MagicMock()


# 测试数据
@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "organization": "Test Org"
    }


@pytest.fixture
def sample_role_data():
    """示例角色数据"""
    return {
        "name": "test_role",
        "description": "Test Role",
        "permissions": ["user:read", "user:write"]
    }


@pytest.fixture
def sample_api_key_data():
    """示例API密钥数据"""
    return {
        "name": "Test API Key",
        "permissions": ["user:read"]
    }


# 测试环境设置
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """设置测试环境"""
    # 设置测试环境变量
    monkeypatch.setenv("MAAS_ENVIRONMENT", "testing")
    monkeypatch.setenv("MAAS_DEBUG", "true")
    monkeypatch.setenv("MAAS_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("MAAS_JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("MAAS_LOG_LEVEL", "DEBUG")