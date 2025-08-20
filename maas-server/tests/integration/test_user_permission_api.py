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

"""用户权限API集成测试"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app


class TestUserPermissionAPI:
    """用户权限API测试"""

    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def admin_headers(self):
        """管理员认证头"""
        # 这里应该返回有效的管理员token
        return {"Authorization": "Bearer admin_token"}

    @pytest.fixture
    def user_headers(self):
        """普通用户认证头"""
        # 这里应该返回有效的普通用户token
        return {"Authorization": "Bearer user_token"}

    def test_get_user_permissions_success(self, client, admin_headers):
        """测试获取用户权限成功"""
        user_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/users/{user_id}/permissions",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证返回数据结构
        permissions_data = data["data"]
        assert "user_id" in permissions_data
        assert "username" in permissions_data
        assert "permissions" in permissions_data
        assert "permissions_by_module" in permissions_data
        assert "roles" in permissions_data
        assert "total_permissions" in permissions_data

    def test_get_user_permissions_unauthorized(self, client, user_headers):
        """测试非管理员获取用户权限被拒绝"""
        user_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/users/{user_id}/permissions",
            headers=user_headers
        )
        
        assert response.status_code == 403

    def test_get_user_permissions_user_not_found(self, client, admin_headers):
        """测试获取不存在用户的权限"""
        non_existent_user_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/users/{non_existent_user_id}/permissions",
            headers=admin_headers
        )
        
        assert response.status_code == 404

    def test_check_user_permission_success(self, client, admin_headers):
        """测试检查用户权限成功"""
        user_id = str(uuid4())
        permission = "user.users.view"
        
        response = client.get(
            f"/api/v1/users/{user_id}/permissions/check",
            params={"permission": permission},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证返回数据结构
        check_result = data["data"]
        assert "user_id" in check_result
        assert "username" in check_result
        assert "permission" in check_result
        assert "has_permission" in check_result
        assert "is_super_admin" in check_result
        assert "granted_by_roles" in check_result
        assert check_result["permission"] == permission

    def test_check_user_permission_missing_parameter(self, client, admin_headers):
        """测试检查用户权限缺少参数"""
        user_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/users/{user_id}/permissions/check",
            headers=admin_headers
        )
        
        assert response.status_code == 422  # Validation error

    def test_check_user_permission_unauthorized(self, client, user_headers):
        """测试非管理员检查用户权限被拒绝"""
        user_id = str(uuid4())
        permission = "user.users.view"
        
        response = client.get(
            f"/api/v1/users/{user_id}/permissions/check",
            params={"permission": permission},
            headers=user_headers
        )
        
        assert response.status_code == 403

    def test_assign_user_roles_success(self, client, admin_headers):
        """测试分配用户角色成功"""
        user_id = str(uuid4())
        role_ids = [str(uuid4()), str(uuid4())]
        
        response = client.post(
            f"/api/v1/users/{user_id}/roles",
            json=role_ids,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证返回的用户数据
        user_data = data["data"]
        assert "id" in user_data
        assert "username" in user_data
        assert "roles" in user_data

    def test_assign_user_roles_empty_list(self, client, admin_headers):
        """测试分配空角色列表"""
        user_id = str(uuid4())
        role_ids = []
        
        response = client.post(
            f"/api/v1/users/{user_id}/roles",
            json=role_ids,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_assign_user_roles_self_modification_forbidden(self, client, admin_headers):
        """测试管理员不能修改自己的角色"""
        # 假设admin_headers对应的用户ID
        admin_user_id = "admin_user_id"  # 这应该从token中提取
        role_ids = [str(uuid4())]
        
        response = client.post(
            f"/api/v1/users/{admin_user_id}/roles",
            json=role_ids,
            headers=admin_headers
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "不能修改自己的角色" in data["detail"]

    def test_assign_user_roles_unauthorized(self, client, user_headers):
        """测试非管理员分配用户角色被拒绝"""
        user_id = str(uuid4())
        role_ids = [str(uuid4())]
        
        response = client.post(
            f"/api/v1/users/{user_id}/roles",
            json=role_ids,
            headers=user_headers
        )
        
        assert response.status_code == 403

    def test_assign_user_roles_invalid_user(self, client, admin_headers):
        """测试为不存在的用户分配角色"""
        non_existent_user_id = str(uuid4())
        role_ids = [str(uuid4())]
        
        response = client.post(
            f"/api/v1/users/{non_existent_user_id}/roles",
            json=role_ids,
            headers=admin_headers
        )
        
        assert response.status_code == 404

    def test_assign_user_roles_invalid_role(self, client, admin_headers):
        """测试分配不存在的角色"""
        user_id = str(uuid4())
        non_existent_role_id = str(uuid4())
        role_ids = [non_existent_role_id]
        
        response = client.post(
            f"/api/v1/users/{user_id}/roles",
            json=role_ids,
            headers=admin_headers
        )
        
        assert response.status_code == 404

    def test_assign_user_roles_invalid_json(self, client, admin_headers):
        """测试分配角色时提供无效JSON"""
        user_id = str(uuid4())
        
        response = client.post(
            f"/api/v1/users/{user_id}/roles",
            json="invalid_json",
            headers=admin_headers
        )
        
        assert response.status_code == 422  # Validation error

    def test_permission_api_without_auth(self, client):
        """测试未认证访问权限API"""
        user_id = str(uuid4())
        
        # 测试获取权限
        response = client.get(f"/api/v1/users/{user_id}/permissions")
        assert response.status_code == 401
        
        # 测试检查权限
        response = client.get(
            f"/api/v1/users/{user_id}/permissions/check",
            params={"permission": "user.users.view"}
        )
        assert response.status_code == 401
        
        # 测试分配角色
        response = client.post(
            f"/api/v1/users/{user_id}/roles",
            json=[str(uuid4())]
        )
        assert response.status_code == 401

    def test_permission_api_with_invalid_uuid(self, client, admin_headers):
        """测试使用无效UUID访问权限API"""
        invalid_user_id = "invalid-uuid"
        
        # 测试获取权限
        response = client.get(
            f"/api/v1/users/{invalid_user_id}/permissions",
            headers=admin_headers
        )
        assert response.status_code == 422  # Validation error
        
        # 测试检查权限
        response = client.get(
            f"/api/v1/users/{invalid_user_id}/permissions/check",
            params={"permission": "user.users.view"},
            headers=admin_headers
        )
        assert response.status_code == 422  # Validation error
        
        # 测试分配角色
        response = client.post(
            f"/api/v1/users/{invalid_user_id}/roles",
            json=[str(uuid4())],
            headers=admin_headers
        )
        assert response.status_code == 422  # Validation error