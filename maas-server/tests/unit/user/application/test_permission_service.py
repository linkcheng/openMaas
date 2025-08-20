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

"""权限应用服务测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.user.application.permission_service import PermissionApplicationService
from src.user.application.schemas import (
    PermissionRequest,
    PermissionUpdateRequest,
    PermissionSearchQuery,
    PermissionBatchRequest,
)
from src.user.domain.models import (
    Permission,
    PermissionName,
    Role,
    User,
    UserProfile,
)
from src.shared.domain.base import EmailAddress
from src.shared.application.exceptions import ApplicationException


class TestPermissionApplicationService:
    """权限应用服务测试"""

    @pytest.fixture
    def mock_permission_repository(self):
        """模拟权限仓储"""
        return AsyncMock()

    @pytest.fixture
    def mock_role_repository(self):
        """模拟角色仓储"""
        return AsyncMock()

    @pytest.fixture
    def mock_user_repository(self):
        """模拟用户仓储"""
        return AsyncMock()

    @pytest.fixture
    def permission_service(
        self, mock_permission_repository, mock_role_repository, mock_user_repository
    ):
        """权限应用服务实例"""
        return PermissionApplicationService(
            permission_repository=mock_permission_repository,
            role_repository=mock_role_repository,
            user_repository=mock_user_repository,
        )

    @pytest.fixture
    def sample_permission(self):
        """示例权限"""
        return Permission(
            id=uuid4(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户列表和详情",
            module="user"
        )

    @pytest.fixture
    def sample_role(self, sample_permission):
        """示例角色"""
        return Role(
            id=uuid4(),
            name="test_role",
            display_name="测试角色",
            description="测试用角色",
            permissions=[sample_permission]
        )

    @pytest.fixture
    def sample_user(self):
        """示例用户"""
        return User(
            id=uuid4(),
            username="testuser",
            email=EmailAddress("test@example.com"),
            password_hash="hashed_password",
            profile=UserProfile(first_name="Test", last_name="User")
        )

    async def test_create_permission_success(
        self, permission_service, mock_permission_repository
    ):
        """测试成功创建权限"""
        # 准备
        request = PermissionRequest(
            name="user.users.create",
            display_name="创建用户",
            description="创建新用户",
            resource="users",
            action="create",
            module="user"
        )
        mock_permission_repository.find_by_resource_action.return_value = None
        
        created_permission = Permission(
            id=uuid4(),
            name=PermissionName(request.name),
            display_name=request.display_name,
            description=request.description,
            module=request.module
        )
        mock_permission_repository.save.return_value = created_permission

        # 执行
        result = await permission_service.create_permission(request)

        # 验证
        assert result.name == request.name
        assert result.display_name == request.display_name
        assert result.description == request.description
        assert result.resource == request.resource
        assert result.action == request.action
        assert result.module == request.module

    async def test_create_permission_already_exists(
        self, permission_service, mock_permission_repository, sample_permission
    ):
        """测试创建已存在的权限"""
        # 准备
        request = PermissionRequest(
            name="user.users.view",
            display_name="查看用户",
            description="查看用户列表",
            resource="users",
            action="view",
            module="user"
        )
        mock_permission_repository.find_by_resource_action.return_value = sample_permission

        # 执行和验证
        with pytest.raises(ApplicationException, match="权限 users:view 已存在"):
            await permission_service.create_permission(request)

    async def test_create_permission_invalid_name(
        self, permission_service, mock_permission_repository
    ):
        """测试创建权限名称格式错误"""
        # 准备
        request = PermissionRequest(
            name="invalid_name",  # 不符合 {module}.{resource}.{action} 格式
            display_name="无效权限",
            description="无效的权限名称",
            resource="users",
            action="view",
            module="user"
        )
        mock_permission_repository.find_by_resource_action.return_value = None

        # 执行和验证
        with pytest.raises(ApplicationException, match="权限名称格式错误"):
            await permission_service.create_permission(request)

    async def test_get_permission_success(
        self, permission_service, mock_permission_repository, sample_permission
    ):
        """测试成功获取权限"""
        # 准备
        mock_permission_repository.find_by_id.return_value = sample_permission

        # 执行
        result = await permission_service.get_permission(sample_permission.id)

        # 验证
        assert result is not None
        assert result.id == sample_permission.id
        assert result.name == sample_permission.name.value

    async def test_get_permission_not_found(
        self, permission_service, mock_permission_repository
    ):
        """测试获取不存在的权限"""
        # 准备
        mock_permission_repository.find_by_id.return_value = None

        # 执行
        result = await permission_service.get_permission(uuid4())

        # 验证
        assert result is None

    async def test_update_permission_success(
        self, permission_service, mock_permission_repository, sample_permission
    ):
        """测试成功更新权限"""
        # 准备
        request = PermissionUpdateRequest(
            display_name="更新的显示名称",
            description="更新的描述",
            module="updated_module"
        )
        mock_permission_repository.find_by_id.return_value = sample_permission
        mock_permission_repository.save.return_value = sample_permission

        # 执行
        result = await permission_service.update_permission(sample_permission.id, request)

        # 验证
        assert result.id == sample_permission.id
        mock_permission_repository.save.assert_called_once()

    async def test_update_permission_not_found(
        self, permission_service, mock_permission_repository
    ):
        """测试更新不存在的权限"""
        # 准备
        request = PermissionUpdateRequest(display_name="新名称")
        mock_permission_repository.find_by_id.return_value = None

        # 执行和验证
        with pytest.raises(ApplicationException, match="权限 .* 不存在"):
            await permission_service.update_permission(uuid4(), request)

    async def test_delete_permission_success(
        self, permission_service, mock_permission_repository, mock_role_repository,
        sample_permission
    ):
        """测试成功删除权限"""
        # 准备
        mock_permission_repository.find_by_id.return_value = sample_permission
        mock_role_repository.find_roles_with_permission.return_value = []

        # 执行
        result = await permission_service.delete_permission(sample_permission.id)

        # 验证
        assert result is True
        mock_permission_repository.delete.assert_called_once_with(sample_permission.id)

    async def test_delete_permission_in_use(
        self, permission_service, mock_permission_repository, mock_role_repository,
        sample_permission, sample_role
    ):
        """测试删除正在使用的权限失败"""
        # 准备
        mock_permission_repository.find_by_id.return_value = sample_permission
        mock_role_repository.find_roles_with_permission.return_value = [sample_role]

        # 执行和验证
        with pytest.raises(ApplicationException, match="无法删除权限，以下角色正在使用"):
            await permission_service.delete_permission(sample_permission.id)

    async def test_search_permissions(
        self, permission_service, mock_permission_repository, sample_permission
    ):
        """测试搜索权限"""
        # 准备
        query = PermissionSearchQuery(
            name="user",
            module="user",
            resource="users",
            action="view",
            limit=10,
            offset=0
        )
        mock_permission_repository.search_permissions.return_value = [sample_permission]

        # 执行
        result = await permission_service.search_permissions(query)

        # 验证
        assert len(result) == 1
        assert result[0].id == sample_permission.id
        mock_permission_repository.search_permissions.assert_called_once_with(
            name=query.name,
            module=query.module,
            resource=query.resource,
            action=query.action,
            limit=query.limit,
            offset=query.offset,
        )

    async def test_get_permissions_by_module(
        self, permission_service, mock_permission_repository, sample_permission
    ):
        """测试按模块获取权限"""
        # 准备
        module = "user"
        mock_permission_repository.find_by_module.return_value = [sample_permission]

        # 执行
        result = await permission_service.get_permissions_by_module(module)

        # 验证
        assert len(result) == 1
        assert result[0].id == sample_permission.id
        mock_permission_repository.find_by_module.assert_called_once_with(module)

    async def test_get_all_permissions(
        self, permission_service, mock_permission_repository, sample_permission
    ):
        """测试获取所有权限"""
        # 准备
        mock_permission_repository.find_all.return_value = [sample_permission]

        # 执行
        result = await permission_service.get_all_permissions()

        # 验证
        assert len(result) == 1
        assert result[0].id == sample_permission.id

    async def test_batch_create_permissions_success(
        self, permission_service, mock_permission_repository
    ):
        """测试批量创建权限成功"""
        # 准备
        perm_requests = [
            PermissionRequest(
                name="user.users.create",
                display_name="创建用户",
                description="创建新用户",
                resource="users",
                action="create",
                module="user"
            ),
            PermissionRequest(
                name="user.users.edit",
                display_name="编辑用户",
                description="编辑用户信息",
                resource="users",
                action="edit",
                module="user"
            )
        ]
        request = PermissionBatchRequest(permissions=perm_requests)
        
        mock_permission_repository.find_by_resource_action.return_value = None
        
        # 模拟保存成功
        def mock_save(permission):
            return permission
        mock_permission_repository.save.side_effect = mock_save

        # 执行
        result = await permission_service.batch_create_permissions(request)

        # 验证
        assert len(result) == 2
        assert mock_permission_repository.save.call_count == 2

    async def test_batch_delete_permissions_success(
        self, permission_service, mock_permission_repository, mock_role_repository
    ):
        """测试批量删除权限成功"""
        # 准备
        permission_ids = [uuid4(), uuid4()]
        
        # 模拟权限存在且没有被使用
        mock_permission_repository.find_by_id.return_value = Permission(
            id=uuid4(),
            name=PermissionName("test.test.test"),
            display_name="测试权限",
            description="测试用权限"
        )
        mock_role_repository.find_roles_with_permission.return_value = []

        # 执行
        result = await permission_service.batch_delete_permissions(permission_ids)

        # 验证
        assert result["deleted_count"] == 2
        assert len(result["failed_deletions"]) == 0
        assert mock_permission_repository.delete.call_count == 2

    async def test_validate_permission_success(
        self, permission_service, mock_user_repository, sample_user
    ):
        """测试权限验证成功"""
        # 准备
        permission_name = "user.users.view"
        sample_user.has_permission = MagicMock(return_value=True)
        mock_user_repository.find_by_id.return_value = sample_user

        # 执行
        result = await permission_service.validate_permission(sample_user.id, permission_name)

        # 验证
        assert result is True
        sample_user.has_permission.assert_called_once_with(permission_name)

    async def test_validate_permission_user_not_found(
        self, permission_service, mock_user_repository
    ):
        """测试权限验证用户不存在"""
        # 准备
        mock_user_repository.find_by_id.return_value = None

        # 执行
        result = await permission_service.validate_permission(uuid4(), "test.permission")

        # 验证
        assert result is False

    async def test_validate_permission_by_parts_success(
        self, permission_service, mock_user_repository, sample_user
    ):
        """测试通过资源和操作验证权限成功"""
        # 准备
        resource = "users"
        action = "view"
        module = "user"
        sample_user.has_permission_by_parts = MagicMock(return_value=True)
        mock_user_repository.find_by_id.return_value = sample_user

        # 执行
        result = await permission_service.validate_permission_by_parts(
            sample_user.id, resource, action, module
        )

        # 验证
        assert result is True
        sample_user.has_permission_by_parts.assert_called_once_with(resource, action, module)

    async def test_export_permissions(
        self, permission_service, mock_permission_repository, sample_permission
    ):
        """测试导出权限配置"""
        # 准备
        mock_permission_repository.find_all.return_value = [sample_permission]

        # 执行
        result = await permission_service.export_permissions()

        # 验证
        assert result.total_count == 1
        assert len(result.permissions) == 1
        assert result.permissions[0]["name"] == sample_permission.name.value
        assert result.export_module is None

    async def test_export_permissions_by_module(
        self, permission_service, mock_permission_repository, sample_permission
    ):
        """测试按模块导出权限配置"""
        # 准备
        module = "user"
        mock_permission_repository.find_by_module.return_value = [sample_permission]

        # 执行
        result = await permission_service.export_permissions(module)

        # 验证
        assert result.total_count == 1
        assert result.export_module == module
        mock_permission_repository.find_by_module.assert_called_once_with(module)

    async def test_import_permissions_success(
        self, permission_service, mock_permission_repository
    ):
        """测试导入权限配置成功"""
        # 准备
        import_data = [
            {
                "name": "user.users.create",
                "display_name": "创建用户",
                "description": "创建新用户",
                "resource": "users",
                "action": "create",
                "module": "user"
            }
        ]
        mock_permission_repository.find_by_resource_action.return_value = None
        
        def mock_save(permission):
            return permission
        mock_permission_repository.save.side_effect = mock_save

        # 执行
        result = await permission_service.import_permissions(import_data)

        # 验证
        assert result["imported_count"] == 1
        assert len(result["failed_imports"]) == 0
        mock_permission_repository.save.assert_called_once()

    async def test_import_permissions_missing_fields(
        self, permission_service, mock_permission_repository
    ):
        """测试导入权限配置缺少必需字段"""
        # 准备
        import_data = [
            {
                "name": "user.users.create",
                # 缺少其他必需字段
            }
        ]

        # 执行
        result = await permission_service.import_permissions(import_data)

        # 验证
        assert result["imported_count"] == 0
        assert len(result["failed_imports"]) == 1
        assert "缺少必需字段" in result["failed_imports"][0]["reason"]