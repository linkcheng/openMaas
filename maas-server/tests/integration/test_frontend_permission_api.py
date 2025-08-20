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

"""前端权限API集成测试"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from uuid import UUID

from main import app
from tests.conftest import TestUser


class TestFrontendPermissionAPI:
    """前端权限API集成测试"""

    @pytest.mark.asyncio
    async def test_get_current_user_permissions_success(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试获取当前用户权限成功"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get("/api/v1/auth/permissions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        permission_data = data["data"]
        assert "user_id" in permission_data
        assert "username" in permission_data
        assert "permissions" in permission_data
        assert "modules" in permission_data
        assert "roles" in permission_data
        assert "is_super_admin" in permission_data
        
        # 验证数据类型
        assert isinstance(permission_data["permissions"], list)
        assert isinstance(permission_data["modules"], dict)
        assert isinstance(permission_data["roles"], list)
        assert isinstance(permission_data["is_super_admin"], bool)

    @pytest.mark.asyncio
    async def test_get_current_user_permissions_with_refresh(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试强制刷新用户权限"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get(
            "/api/v1/auth/permissions?refresh=true", 
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    @pytest.mark.asyncio
    async def test_get_user_menus_success(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试获取用户菜单成功"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get("/api/v1/auth/menus", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        menu_data = data["data"]
        assert "menus" in menu_data
        assert "permissions" in menu_data
        assert "user_id" in menu_data
        assert "username" in menu_data
        
        # 验证菜单数据结构
        assert isinstance(menu_data["menus"], list)
        if menu_data["menus"]:
            menu = menu_data["menus"][0]
            assert "menu_id" in menu
            assert "menu_name" in menu
            assert "menu_path" in menu
            assert "required_permissions" in menu

    @pytest.mark.asyncio
    async def test_check_user_permission_success(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试检查用户权限成功"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        # 测试检查一个基本权限
        response = await async_client.get(
            "/api/v1/auth/permissions/check?permission=user.users.view",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], bool)

    @pytest.mark.asyncio
    async def test_check_user_permission_wildcard(
        self, 
        async_client: AsyncClient, 
        test_super_admin: TestUser
    ):
        """测试超级管理员通配符权限检查"""
        headers = {"Authorization": f"Bearer {test_super_admin.access_token}"}
        
        response = await async_client.get(
            "/api/v1/auth/permissions/check?permission=any.permission.here",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is True  # 超级管理员应该有所有权限

    @pytest.mark.asyncio
    async def test_check_menu_permission_success(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试检查菜单权限成功"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get(
            "/api/v1/auth/menus/user_management/check",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], bool)

    @pytest.mark.asyncio
    async def test_get_permission_modules_success(
        self, 
        async_client: AsyncClient, 
        test_admin: TestUser
    ):
        """测试获取权限模块信息成功"""
        headers = {"Authorization": f"Bearer {test_admin.access_token}"}
        
        response = await async_client.get("/api/v1/auth/permissions/modules", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        modules = data["data"]
        assert isinstance(modules, dict)
        
        # 验证模块结构
        if modules:
            module_name = next(iter(modules))
            module = modules[module_name]
            assert "name" in module
            assert "display_name" in module
            assert "permissions" in module
            assert isinstance(module["permissions"], list)

    @pytest.mark.asyncio
    async def test_get_permission_modules_insufficient_permission(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试权限不足时获取权限模块信息失败"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get("/api/v1/auth/permissions/modules", headers=headers)
        
        # 应该返回403权限不足
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_refresh_user_permissions_success(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试刷新用户权限缓存成功"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.post("/api/v1/auth/permissions/refresh", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证返回的权限数据结构
        permission_data = data["data"]
        assert "user_id" in permission_data
        assert "permissions" in permission_data
        assert "modules" in permission_data

    @pytest.mark.asyncio
    async def test_batch_refresh_user_permissions_success(
        self, 
        async_client: AsyncClient, 
        test_admin: TestUser,
        test_user: TestUser
    ):
        """测试批量刷新用户权限缓存成功"""
        headers = {"Authorization": f"Bearer {test_admin.access_token}"}
        
        user_ids = [str(test_user.user_id), str(test_admin.user_id)]
        
        response = await async_client.post(
            "/api/v1/auth/permissions/batch-refresh",
            headers=headers,
            json=user_ids
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        result = data["data"]
        assert "total_count" in result
        assert "success_count" in result
        assert "failed_count" in result
        assert result["total_count"] == len(user_ids)

    @pytest.mark.asyncio
    async def test_batch_refresh_user_permissions_insufficient_permission(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试权限不足时批量刷新用户权限失败"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        user_ids = [str(test_user.user_id)]
        
        response = await async_client.post(
            "/api/v1/auth/permissions/batch-refresh",
            headers=headers,
            json=user_ids
        )
        
        # 应该返回403权限不足
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_batch_refresh_empty_user_list(
        self, 
        async_client: AsyncClient, 
        test_admin: TestUser
    ):
        """测试空用户列表时批量刷新失败"""
        headers = {"Authorization": f"Bearer {test_admin.access_token}"}
        
        response = await async_client.post(
            "/api/v1/auth/permissions/batch-refresh",
            headers=headers,
            json=[]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "INVALID_REQUEST" in data["error"]["code"]

    @pytest.mark.asyncio
    async def test_batch_refresh_too_many_users(
        self, 
        async_client: AsyncClient, 
        test_admin: TestUser
    ):
        """测试用户数量过多时批量刷新失败"""
        headers = {"Authorization": f"Bearer {test_admin.access_token}"}
        
        # 创建超过100个用户ID
        user_ids = [str(UUID(int=i)) for i in range(101)]
        
        response = await async_client.post(
            "/api/v1/auth/permissions/batch-refresh",
            headers=headers,
            json=user_ids
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "TOO_MANY_USERS" in data["error"]["code"]

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """测试未授权访问"""
        # 不提供Authorization头
        response = await async_client.get("/api/v1/auth/permissions")
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_token_access(self, async_client: AsyncClient):
        """测试无效token访问"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = await async_client.get("/api/v1/auth/permissions", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_permission_check_missing_parameter(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试权限检查缺少参数"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get(
            "/api/v1/auth/permissions/check",  # 缺少permission参数
            headers=headers
        )
        
        assert response.status_code == 422  # 参数验证错误

    @pytest.mark.asyncio
    async def test_menu_permission_check_nonexistent_menu(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试检查不存在菜单的权限"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get(
            "/api/v1/auth/menus/nonexistent_menu/check",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is False  # 不存在的菜单应该返回False

    @pytest.mark.asyncio
    async def test_permission_data_structure_validation(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试权限数据结构验证"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get("/api/v1/auth/permissions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        permission_data = data["data"]
        
        # 验证必需字段存在
        required_fields = ["user_id", "username", "permissions", "modules", "roles", "is_super_admin"]
        for field in required_fields:
            assert field in permission_data, f"Missing required field: {field}"
        
        # 验证数据类型
        assert isinstance(permission_data["user_id"], str)
        assert isinstance(permission_data["username"], str)
        assert isinstance(permission_data["permissions"], list)
        assert isinstance(permission_data["modules"], dict)
        assert isinstance(permission_data["roles"], list)
        assert isinstance(permission_data["is_super_admin"], bool)
        
        # 验证模块结构
        for module_name, module in permission_data["modules"].items():
            assert isinstance(module, dict)
            assert "name" in module
            assert "display_name" in module
            assert "permissions" in module
            assert isinstance(module["permissions"], list)

    @pytest.mark.asyncio
    async def test_menu_data_structure_validation(
        self, 
        async_client: AsyncClient, 
        test_user: TestUser
    ):
        """测试菜单数据结构验证"""
        headers = {"Authorization": f"Bearer {test_user.access_token}"}
        
        response = await async_client.get("/api/v1/auth/menus", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        menu_data = data["data"]
        
        # 验证必需字段存在
        required_fields = ["menus", "permissions", "user_id", "username"]
        for field in required_fields:
            assert field in menu_data, f"Missing required field: {field}"
        
        # 验证菜单结构
        assert isinstance(menu_data["menus"], list)
        for menu in menu_data["menus"]:
            menu_required_fields = ["menu_id", "menu_name", "menu_path", "required_permissions"]
            for field in menu_required_fields:
                assert field in menu, f"Missing menu field: {field}"
            
            assert isinstance(menu["required_permissions"], list)
            assert isinstance(menu["sort_order"], int)
            assert isinstance(menu["is_visible"], bool)