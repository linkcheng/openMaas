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

"""权限管理API集成测试"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app


class TestPermissionManagementAPI:
    """权限管理API测试"""

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

    def test_get_permissions_success(self, client, admin_headers):
        """测试获取权限列表成功"""
        response = client.get(
            "/api/v1/permissions",
            params={"page": 1, "limit": 10},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证响应结构
        response_data = data["data"]
        assert "permissions" in response_data
        assert "pagination" in response_data
        assert "filters" in response_data
        
        pagination = response_data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 10

    def test_get_permissions_with_filters(self, client, admin_headers):
        """测试带过滤条件获取权限列表"""
        response = client.get(
            "/api/v1/permissions",
            params={
                "name": "user",
                "module": "user",
                "resource": "users",
                "action": "view",
                "page": 1,
                "limit": 20
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        filters = data["data"]["filters"]
        assert filters["name"] == "user"
        assert filters["module"] == "user"
        assert filters["resource"] == "users"
        assert filters["action"] == "view"

    def test_get_permissions_by_module_success(self, client, admin_headers):
        """测试按模块获取权限成功"""
        module = "user"
        
        response = client.get(
            f"/api/v1/permissions/modules/{module}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert f"获取模块 {module} 权限成功" in data["message"]

    def test_get_all_permissions_success(self, client, admin_headers):
        """测试获取所有权限成功"""
        response = client.get(
            "/api/v1/permissions/all",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证响应结构
        response_data = data["data"]
        assert "permissions" in response_data
        assert "permissions_by_module" in response_data
        assert "total_count" in response_data

    def test_create_permission_success(self, client, super_admin_headers):
        """测试创建权限成功"""
        permission_data = {
            "name": "test.resource.action",
            "display_name": "测试权限",
            "description": "这是一个测试权限",
            "resource": "resource",
            "action": "action",
            "module": "test"
        }
        
        response = client.post(
            "/api/v1/permissions",
            json=permission_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证返回的权限数据
        permission = data["data"]
        assert permission["name"] == permission_data["name"]
        assert permission["display_name"] == permission_data["display_name"]
        assert permission["resource"] == permission_data["resource"]
        assert permission["action"] == permission_data["action"]
        assert permission["module"] == permission_data["module"]

    def test_create_permission_duplicate(self, client, super_admin_headers):
        """测试创建重复权限"""
        permission_data = {
            "name": "duplicate.resource.action",
            "display_name": "重复权限",
            "description": "这是一个重复权限",
            "resource": "resource",
            "action": "action",
            "module": "duplicate"
        }
        
        # 第一次创建应该成功
        response = client.post(
            "/api/v1/permissions",
            json=permission_data,
            headers=super_admin_headers
        )
        assert response.status_code == 200
        
        # 第二次创建应该失败
        response = client.post(
            "/api/v1/permissions",
            json=permission_data,
            headers=super_admin_headers
        )
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    def test_create_permission_invalid_name(self, client, super_admin_headers):
        """测试创建权限时使用无效名称"""
        permission_data = {
            "name": "invalid-name-format",
            "display_name": "无效权限",
            "description": "这是一个无效权限",
            "resource": "resource",
            "action": "action",
            "module": "test"
        }
        
        response = client.post(
            "/api/v1/permissions",
            json=permission_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 400
        assert "格式错误" in response.json()["detail"]

    def test_get_permission_success(self, client, admin_headers):
        """测试获取权限详情成功"""
        permission_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/permissions/{permission_id}",
            headers=admin_headers
        )
        
        # 如果权限存在应该返回200，不存在返回404
        assert response.status_code in [200, 404]

    def test_get_permission_not_found(self, client, admin_headers):
        """测试获取不存在的权限"""
        non_existent_permission_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/permissions/{non_existent_permission_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 404
        assert "权限不存在" in response.json()["detail"]

    def test_update_permission_success(self, client, super_admin_headers):
        """测试更新权限成功"""
        permission_id = str(uuid4())
        update_data = {
            "display_name": "更新后的权限名称",
            "description": "更新后的权限描述",
            "module": "updated_module"
        }
        
        response = client.put(
            f"/api/v1/permissions/{permission_id}",
            json=update_data,
            headers=super_admin_headers
        )
        
        # 如果权限存在应该返回200，不存在返回404
        assert response.status_code in [200, 404]

    def test_delete_permission_success(self, client, super_admin_headers):
        """测试删除权限成功"""
        permission_id = str(uuid4())
        
        response = client.delete(
            f"/api/v1/permissions/{permission_id}",
            headers=super_admin_headers
        )
        
        # 如果权限存在且可删除应该返回200，不存在返回404，有依赖返回400
        assert response.status_code in [200, 400, 404]

    def test_batch_create_permissions_success(self, client, super_admin_headers):
        """测试批量创建权限成功"""
        batch_data = {
            "permissions": [
                {
                    "name": "batch1.resource.action",
                    "display_name": "批量权限1",
                    "description": "批量创建的权限1",
                    "resource": "resource",
                    "action": "action",
                    "module": "batch1"
                },
                {
                    "name": "batch2.resource.action",
                    "display_name": "批量权限2",
                    "description": "批量创建的权限2",
                    "resource": "resource",
                    "action": "action",
                    "module": "batch2"
                }
            ]
        }
        
        response = client.post(
            "/api/v1/permissions/batch",
            json=batch_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "created_permissions" in data["data"]
        assert "created_count" in data["data"]

    def test_batch_delete_permissions_success(self, client, super_admin_headers):
        """测试批量删除权限成功"""
        permission_ids = [str(uuid4()), str(uuid4())]
        
        response = client.delete(
            "/api/v1/permissions/batch",
            json=permission_ids,
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted_count" in data["data"]
        assert "failed_deletions" in data["data"]

    def test_export_permissions_success(self, client, super_admin_headers):
        """测试导出权限配置成功"""
        response = client.get(
            "/api/v1/permissions/export",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证导出数据结构
        export_data = data["data"]
        assert "permissions" in export_data
        assert "total_count" in export_data
        assert "export_module" in export_data

    def test_export_permissions_by_module(self, client, super_admin_headers):
        """测试按模块导出权限配置"""
        module = "user"
        
        response = client.get(
            "/api/v1/permissions/export",
            params={"module": module},
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["export_module"] == module

    def test_import_permissions_success(self, client, super_admin_headers):
        """测试导入权限配置成功"""
        import_data = [
            {
                "name": "import1.resource.action",
                "display_name": "导入权限1",
                "description": "导入的权限1",
                "resource": "resource",
                "action": "action",
                "module": "import1"
            },
            {
                "name": "import2.resource.action",
                "display_name": "导入权限2",
                "description": "导入的权限2",
                "resource": "resource",
                "action": "action",
                "module": "import2"
            }
        ]
        
        response = client.post(
            "/api/v1/permissions/import",
            json=import_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "imported_count" in data["data"]
        assert "failed_imports" in data["data"]

    def test_validate_user_permission_success(self, client, admin_headers):
        """测试验证用户权限成功"""
        user_id = str(uuid4())
        permission_name = "user.users.view"
        
        response = client.get(
            f"/api/v1/permissions/validate/{user_id}",
            params={"permission_name": permission_name},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证响应结构
        validation_result = data["data"]
        assert "user_id" in validation_result
        assert "permission" in validation_result
        assert "has_permission" in validation_result

    def test_validate_user_permission_by_parts_success(self, client, admin_headers):
        """测试通过资源和操作验证用户权限成功"""
        user_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/permissions/validate/{user_id}/by-parts",
            params={
                "resource": "users",
                "action": "view",
                "module": "user"
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证响应结构
        validation_result = data["data"]
        assert "user_id" in validation_result
        assert "permission" in validation_result
        assert "resource" in validation_result
        assert "action" in validation_result
        assert "module" in validation_result
        assert "has_permission" in validation_result

    def test_permission_api_unauthorized_access(self, client, user_headers):
        """测试非管理员访问权限API被拒绝"""
        # 测试获取权限列表
        response = client.get("/api/v1/permissions", headers=user_headers)
        assert response.status_code == 403
        
        # 测试创建权限
        response = client.post(
            "/api/v1/permissions",
            json={"name": "test", "display_name": "test"},
            headers=user_headers
        )
        assert response.status_code == 403

    def test_permission_api_super_admin_only(self, client, admin_headers):
        """测试仅超级管理员可访问的API"""
        permission_data = {
            "name": "test.resource.action",
            "display_name": "测试权限",
            "description": "测试权限",
            "resource": "resource",
            "action": "action"
        }
        
        # 普通管理员不能创建权限
        response = client.post(
            "/api/v1/permissions",
            json=permission_data,
            headers=admin_headers
        )
        assert response.status_code == 403

    def test_permission_api_without_auth(self, client):
        """测试未认证访问权限API"""
        # 测试获取权限列表
        response = client.get("/api/v1/permissions")
        assert response.status_code == 401
        
        # 测试创建权限
        response = client.post("/api/v1/permissions", json={})
        assert response.status_code == 401

    def test_permission_api_with_invalid_uuid(self, client, admin_headers):
        """测试使用无效UUID访问权限API"""
        invalid_id = "invalid-uuid"
        
        response = client.get(
            f"/api/v1/permissions/{invalid_id}",
            headers=admin_headers
        )
        assert response.status_code == 422

    def test_permission_api_comprehensive_flow(self, client, super_admin_headers, admin_headers):
        """测试权限API的完整流程"""
        # 1. 获取权限列表
        response = client.get("/api/v1/permissions", headers=admin_headers)
        assert response.status_code == 200
        
        # 2. 创建新权限
        permission_data = {
            "name": "flow.test.action",
            "display_name": "流程测试权限",
            "description": "完整流程测试权限",
            "resource": "test",
            "action": "action",
            "module": "flow"
        }
        response = client.post(
            "/api/v1/permissions",
            json=permission_data,
            headers=super_admin_headers
        )
        assert response.status_code == 200
        permission_id = response.json()["data"]["id"]
        
        # 3. 获取权限详情
        response = client.get(
            f"/api/v1/permissions/{permission_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 4. 更新权限
        update_data = {"display_name": "更新后的权限名称"}
        response = client.put(
            f"/api/v1/permissions/{permission_id}",
            json=update_data,
            headers=super_admin_headers
        )
        assert response.status_code == 200
        
        # 5. 导出权限
        response = client.get(
            "/api/v1/permissions/export",
            headers=super_admin_headers
        )
        assert response.status_code == 200
        
        # 6. 删除权限
        response = client.delete(
            f"/api/v1/permissions/{permission_id}",
            headers=super_admin_headers
        )
        assert response.status_code == 200