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

"""角色管理API集成测试"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app


class TestRoleManagementAPI:
    """角色管理API测试"""

    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def super_admin_headers(self):
        """超级管理员认证头"""
        return {"Authorization": "Bearer super_admin_token"}

    @pytest.fixture
    def admin_headers(self):
        """管理员认证头"""
        return {"Authorization": "Bearer admin_token"}

    @pytest.fixture
    def user_headers(self):
        """普通用户认证头"""
        return {"Authorization": "Bearer user_token"}

    def test_get_roles_with_pagination_success(self, client, admin_headers):
        """测试获取角色列表（支持分页）成功"""
        response = client.get(
            "/api/v1/roles",
            params={"page": 1, "limit": 10},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证分页响应结构
        response_data = data["data"]
        assert "roles" in response_data
        assert "pagination" in response_data
        
        pagination = response_data["pagination"]
        assert "page" in pagination
        assert "limit" in pagination
        assert "total" in pagination
        assert "has_more" in pagination
        assert pagination["page"] == 1
        assert pagination["limit"] == 10

    def test_get_roles_with_search_success(self, client, admin_headers):
        """测试搜索角色成功"""
        response = client.get(
            "/api/v1/roles",
            params={"name": "admin", "page": 1, "limit": 20},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_roles_default_pagination(self, client, admin_headers):
        """测试默认分页参数"""
        response = client.get(
            "/api/v1/roles",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        pagination = data["data"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 20

    def test_get_roles_invalid_pagination(self, client, admin_headers):
        """测试无效分页参数"""
        # 测试页码小于1
        response = client.get(
            "/api/v1/roles",
            params={"page": 0, "limit": 10},
            headers=admin_headers
        )
        assert response.status_code == 422
        
        # 测试限制超过最大值
        response = client.get(
            "/api/v1/roles",
            params={"page": 1, "limit": 101},
            headers=admin_headers
        )
        assert response.status_code == 422

    def test_get_roles_unauthorized(self, client, user_headers):
        """测试非管理员获取角色列表被拒绝"""
        response = client.get(
            "/api/v1/roles",
            headers=user_headers
        )
        
        assert response.status_code == 403

    def test_update_role_permissions_success(self, client, super_admin_headers):
        """测试更新角色权限成功"""
        role_id = str(uuid4())
        permission_ids = [str(uuid4()), str(uuid4())]
        
        response = client.put(
            f"/api/v1/roles/{role_id}/permissions",
            json=permission_ids,
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证返回的角色数据
        role_data = data["data"]
        assert "id" in role_data
        assert "name" in role_data
        assert "permissions" in role_data

    def test_update_role_permissions_empty_list(self, client, super_admin_headers):
        """测试清空角色权限"""
        role_id = str(uuid4())
        permission_ids = []
        
        response = client.put(
            f"/api/v1/roles/{role_id}/permissions",
            json=permission_ids,
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_update_role_permissions_role_not_found(self, client, super_admin_headers):
        """测试更新不存在角色的权限"""
        non_existent_role_id = str(uuid4())
        permission_ids = [str(uuid4())]
        
        response = client.put(
            f"/api/v1/roles/{non_existent_role_id}/permissions",
            json=permission_ids,
            headers=super_admin_headers
        )
        
        assert response.status_code == 404

    def test_update_role_permissions_system_role_forbidden(self, client, super_admin_headers):
        """测试更新系统角色权限被禁止"""
        # 假设这是一个系统角色ID
        system_role_id = "system_role_id"
        permission_ids = [str(uuid4())]
        
        response = client.put(
            f"/api/v1/roles/{system_role_id}/permissions",
            json=permission_ids,
            headers=super_admin_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "系统角色" in data["detail"]

    def test_update_role_permissions_invalid_permission(self, client, super_admin_headers):
        """测试使用不存在的权限更新角色"""
        role_id = str(uuid4())
        non_existent_permission_id = str(uuid4())
        permission_ids = [non_existent_permission_id]
        
        response = client.put(
            f"/api/v1/roles/{role_id}/permissions",
            json=permission_ids,
            headers=super_admin_headers
        )
        
        # 应该成功，但会跳过不存在的权限
        assert response.status_code == 200

    def test_update_role_permissions_unauthorized(self, client, admin_headers):
        """测试非超级管理员更新角色权限被拒绝"""
        role_id = str(uuid4())
        permission_ids = [str(uuid4())]
        
        response = client.put(
            f"/api/v1/roles/{role_id}/permissions",
            json=permission_ids,
            headers=admin_headers
        )
        
        assert response.status_code == 403

    def test_delete_role_success(self, client, super_admin_headers):
        """测试删除角色成功"""
        role_id = str(uuid4())
        
        response = client.delete(
            f"/api/v1/roles/{role_id}",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "角色删除成功" in data["message"]

    def test_delete_role_not_found(self, client, super_admin_headers):
        """测试删除不存在的角色"""
        non_existent_role_id = str(uuid4())
        
        response = client.delete(
            f"/api/v1/roles/{non_existent_role_id}",
            headers=super_admin_headers
        )
        
        assert response.status_code == 404

    def test_delete_system_role_forbidden(self, client, super_admin_headers):
        """测试删除系统角色被禁止"""
        # 假设这是一个系统角色ID
        system_role_id = "system_role_id"
        
        response = client.delete(
            f"/api/v1/roles/{system_role_id}",
            headers=super_admin_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "系统角色" in data["detail"]

    def test_delete_role_with_users_forbidden(self, client, super_admin_headers):
        """测试删除有用户使用的角色被禁止"""
        # 假设这个角色有用户在使用
        role_with_users_id = "role_with_users_id"
        
        response = client.delete(
            f"/api/v1/roles/{role_with_users_id}",
            headers=super_admin_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "正在使用" in data["detail"]

    def test_delete_role_unauthorized(self, client, admin_headers):
        """测试非超级管理员删除角色被拒绝"""
        role_id = str(uuid4())
        
        response = client.delete(
            f"/api/v1/roles/{role_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 403

    def test_role_management_without_auth(self, client):
        """测试未认证访问角色管理API"""
        role_id = str(uuid4())
        
        # 测试获取角色列表
        response = client.get("/api/v1/roles")
        assert response.status_code == 401
        
        # 测试更新角色权限
        response = client.put(
            f"/api/v1/roles/{role_id}/permissions",
            json=[str(uuid4())]
        )
        assert response.status_code == 401
        
        # 测试删除角色
        response = client.delete(f"/api/v1/roles/{role_id}")
        assert response.status_code == 401

    def test_role_management_with_invalid_uuid(self, client, super_admin_headers):
        """测试使用无效UUID访问角色管理API"""
        invalid_role_id = "invalid-uuid"
        
        # 测试更新角色权限
        response = client.put(
            f"/api/v1/roles/{invalid_role_id}/permissions",
            json=[str(uuid4())],
            headers=super_admin_headers
        )
        assert response.status_code == 422
        
        # 测试删除角色
        response = client.delete(
            f"/api/v1/roles/{invalid_role_id}",
            headers=super_admin_headers
        )
        assert response.status_code == 422

    def test_update_role_permissions_invalid_json(self, client, super_admin_headers):
        """测试更新角色权限时提供无效JSON"""
        role_id = str(uuid4())
        
        response = client.put(
            f"/api/v1/roles/{role_id}/permissions",
            json="invalid_json",
            headers=super_admin_headers
        )
        
        assert response.status_code == 422

    def test_role_api_comprehensive_flow(self, client, super_admin_headers, admin_headers):
        """测试角色API的完整流程"""
        # 1. 获取角色列表
        response = client.get("/api/v1/roles", headers=admin_headers)
        assert response.status_code == 200
        
        # 2. 创建新角色
        create_data = {
            "name": "test_role",
            "description": "测试角色",
            "permission_ids": []
        }
        response = client.post("/api/v1/roles", json=create_data, headers=super_admin_headers)
        assert response.status_code == 200
        role_id = response.json()["data"]["id"]
        
        # 3. 更新角色权限
        permission_ids = [str(uuid4())]
        response = client.put(
            f"/api/v1/roles/{role_id}/permissions",
            json=permission_ids,
            headers=super_admin_headers
        )
        assert response.status_code == 200
        
        # 4. 获取角色详情
        response = client.get(f"/api/v1/roles/{role_id}", headers=admin_headers)
        assert response.status_code == 200
        
        # 5. 删除角色
        response = client.delete(f"/api/v1/roles/{role_id}", headers=super_admin_headers)
        assert response.status_code == 200