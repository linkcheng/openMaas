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

"""角色应用服务测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.user.application.role_service import RoleApplicationService
from src.user.application.schemas import (
    PermissionRequest,
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleSearchQuery,
    UserRoleAssignRequest,
)
from src.user.domain.models import (
    Role,
    Permission,
    PermissionName,
    User,
    UserProfile,
    RoleType,
)
from src.shared.domain.base import EmailAddress
from src.shared.application.exceptions import ApplicationException


class TestRoleApplicationService:
    """角色应用服务测试"""

    @pytest.fixture
    def mock_role_repository(self):
        """模拟角色仓储"""
        return AsyncMock()

    @pytest.fixture
    def mock_permission_repository(self):
        """模拟权限仓储"""
        return AsyncMock()

    @pytest.fixture
    def mock_user_repository(self):
        """模拟用户仓储"""
        return AsyncMock()

    @pytest.fixture
    def role_service(self, mock_role_repository, mock_permission_repository, mock_user_repository):
        """角色应用服务实例"""
        return RoleApplicationService(
            role_repository=mock_role_repository,
            permission_repository=mock_permission_repository,
            user_repository=mock_user_repository,
        )

    @pytest.fixture
    def sample_permission(self):
        """示例权限"""
        return Permission(
            id=uuid4(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户列表和详情"
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
        self, role_service, mock_permission_repository
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

        # 执行
        result = await role_service.create_permission(request)

        # 验证
        assert result.name == request.name
        assert result.description == request.description
        assert result.resource == request.resource
        assert result.action == request.action

    async def test_create_permission_already_exists(
        self, role_service, mock_permission_repository, sample_permission
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
            await role_service.create_permission(request)

    async def test_create_role_success(
        self, role_service, mock_role_repository, mock_permission_repository, sample_permission
    ):
        """测试成功创建角色"""
        # 准备
        request = RoleCreateRequest(
            name="new_role",
            description="新角色",
            permission_ids=[sample_permission.id]
        )
        mock_role_repository.find_by_name.return_value = None
        mock_permission_repository.find_by_id.return_value = sample_permission
        mock_role_repository.save.return_value = Role(
            id=uuid4(),
            name=request.name,
            display_name=request.name,
            description=request.description,
            permissions=[sample_permission]
        )

        # 执行
        result = await role_service.create_role(request)

        # 验证
        assert result.name == request.name
        assert result.description == request.description
        assert len(result.permissions) == 1

    async def test_create_role_already_exists(
        self, role_service, mock_role_repository, sample_role
    ):
        """测试创建已存在的角色"""
        # 准备
        request = RoleCreateRequest(
            name="test_role",
            description="测试角色",
            permission_ids=[]
        )
        mock_role_repository.find_by_name.return_value = sample_role

        # 执行和验证
        with pytest.raises(ApplicationException, match="角色 test_role 已存在"):
            await role_service.create_role(request)

    async def test_update_role_permissions_success(
        self, role_service, mock_role_repository, mock_permission_repository, 
        mock_user_repository, sample_role, sample_permission
    ):
        """测试成功更新角色权限"""
        # 准备
        new_permission = Permission(
            id=uuid4(),
            name=PermissionName("user.users.edit"),
            display_name="编辑用户",
            description="编辑用户信息"
        )
        
        mock_role_repository.find_by_id.return_value = sample_role
        mock_permission_repository.find_by_id.return_value = new_permission
        mock_role_repository.save.return_value = sample_role
        mock_user_repository.find_by_role_id.return_value = []

        # 执行
        result = await role_service.update_role_permissions(
            sample_role.id, [new_permission.id]
        )

        # 验证
        assert result.id == sample_role.id
        mock_role_repository.save.assert_called_once()

    async def test_update_role_permissions_system_role(
        self, role_service, mock_role_repository
    ):
        """测试更新系统角色权限失败"""
        # 准备
        system_role = Role(
            id=uuid4(),
            name="admin",
            display_name="管理员",
            description="系统管理员",
            is_system_role=True
        )
        mock_role_repository.find_by_id.return_value = system_role

        # 执行和验证
        with pytest.raises(ApplicationException, match="无法修改系统角色"):
            await role_service.update_role_permissions(system_role.id, [])

    async def test_delete_role_success(
        self, role_service, mock_role_repository, mock_user_repository, sample_role
    ):
        """测试成功删除角色"""
        # 准备
        mock_role_repository.find_by_id.return_value = sample_role
        mock_user_repository.find_by_role_id.return_value = []

        # 执行
        result = await role_service.delete_role(sample_role.id)

        # 验证
        assert result is True
        mock_role_repository.delete.assert_called_once_with(sample_role.id)

    async def test_delete_role_with_users(
        self, role_service, mock_role_repository, mock_user_repository, 
        sample_role, sample_user
    ):
        """测试删除有用户使用的角色失败"""
        # 准备
        mock_role_repository.find_by_id.return_value = sample_role
        mock_user_repository.find_by_role_id.return_value = [sample_user]

        # 执行和验证
        with pytest.raises(ApplicationException, match="无法删除角色，以下用户正在使用"):
            await role_service.delete_role(sample_role.id)

    async def test_delete_system_role(
        self, role_service, mock_role_repository, mock_user_repository
    ):
        """测试删除系统角色失败"""
        # 准备
        system_role = Role(
            id=uuid4(),
            name="admin",
            display_name="管理员",
            description="系统管理员",
            is_system_role=True
        )
        mock_role_repository.find_by_id.return_value = system_role
        mock_user_repository.find_by_role_id.return_value = []

        # 执行和验证
        with pytest.raises(ApplicationException, match="无法删除系统角色"):
            await role_service.delete_role(system_role.id)

    async def test_get_role_success(
        self, role_service, mock_role_repository, sample_role
    ):
        """测试成功获取角色"""
        # 准备
        mock_role_repository.find_by_id.return_value = sample_role

        # 执行
        result = await role_service.get_role(sample_role.id)

        # 验证
        assert result is not None
        assert result.id == sample_role.id
        assert result.name == sample_role.name

    async def test_get_role_not_found(
        self, role_service, mock_role_repository
    ):
        """测试获取不存在的角色"""
        # 准备
        mock_role_repository.find_by_id.return_value = None

        # 执行
        result = await role_service.get_role(uuid4())

        # 验证
        assert result is None

    async def test_search_roles(
        self, role_service, mock_role_repository, sample_role
    ):
        """测试搜索角色"""
        # 准备
        query = RoleSearchQuery(name="test", limit=10, offset=0)
        mock_role_repository.search_roles.return_value = [sample_role]

        # 执行
        result = await role_service.search_roles(query)

        # 验证
        assert len(result) == 1
        assert result[0].id == sample_role.id
        mock_role_repository.search_roles.assert_called_once_with(
            name=query.name, limit=query.limit, offset=query.offset
        )

    async def test_get_all_permissions(
        self, role_service, mock_permission_repository, sample_permission
    ):
        """测试获取所有权限"""
        # 准备
        mock_permission_repository.find_all.return_value = [sample_permission]

        # 执行
        result = await role_service.get_all_permissions()

        # 验证
        assert len(result) == 1
        assert result[0].id == sample_permission.id
        assert result[0].name == sample_permission.name.value

    async def test_assign_user_roles_success(
        self, role_service, mock_user_repository, mock_role_repository,
        sample_user, sample_role
    ):
        """测试成功分配用户角色"""
        # 准备
        request = UserRoleAssignRequest(
            user_id=sample_user.id,
            role_ids=[sample_role.id]
        )
        mock_user_repository.find_by_id.return_value = sample_user
        mock_role_repository.find_by_id.return_value = sample_role
        mock_user_repository.save.return_value = sample_user

        # 执行
        result = await role_service.assign_user_roles(request)

        # 验证
        assert result is True
        mock_user_repository.save.assert_called_once()

    async def test_assign_user_roles_user_not_found(
        self, role_service, mock_user_repository
    ):
        """测试分配角色给不存在的用户"""
        # 准备
        request = UserRoleAssignRequest(
            user_id=uuid4(),
            role_ids=[uuid4()]
        )
        mock_user_repository.find_by_id.return_value = None

        # 执行和验证
        with pytest.raises(ApplicationException, match="用户 .* 不存在"):
            await role_service.assign_user_roles(request)

    async def test_assign_user_roles_role_not_found(
        self, role_service, mock_user_repository, mock_role_repository, sample_user
    ):
        """测试分配不存在的角色给用户"""
        # 准备
        request = UserRoleAssignRequest(
            user_id=sample_user.id,
            role_ids=[uuid4()]
        )
        mock_user_repository.find_by_id.return_value = sample_user
        mock_role_repository.find_by_id.return_value = None

        # 执行和验证
        with pytest.raises(ApplicationException, match="角色 .* 不存在"):
            await role_service.assign_user_roles(request)