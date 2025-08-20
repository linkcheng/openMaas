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

"""权限仓储集成测试"""

import pytest
from uuid import UUID
from uuid_extensions import uuid7

from user.domain.models import Permission, PermissionName
from user.infrastructure.repositories import PermissionRepository
from user.infrastructure.models import PermissionORM


@pytest.mark.asyncio
class TestPermissionRepository:
    """权限仓储测试"""

    async def test_find_by_module(self, db_session):
        """测试按模块查找权限"""
        repo = PermissionRepository(db_session)
        
        # 创建测试权限
        perm1 = PermissionORM(
            permission_id=uuid7(),
            name="user.users.view",
            display_name="查看用户",
            description="查看用户列表",
            module="user",
            resource="users",
            action="view"
        )
        perm2 = PermissionORM(
            permission_id=uuid7(),
            name="user.roles.create",
            display_name="创建角色",
            description="创建新角色",
            module="user",
            resource="roles",
            action="create"
        )
        perm3 = PermissionORM(
            permission_id=uuid7(),
            name="model.models.view",
            display_name="查看模型",
            description="查看模型列表",
            module="model",
            resource="models",
            action="view"
        )
        
        db_session.add_all([perm1, perm2, perm3])
        await db_session.commit()
        
        # 测试按模块查找
        user_permissions = await repo.find_by_module("user")
        assert len(user_permissions) == 2
        assert all(perm.module == "user" for perm in user_permissions)
        
        model_permissions = await repo.find_by_module("model")
        assert len(model_permissions) == 1
        assert model_permissions[0].module == "model"

    async def test_find_by_resource_action(self, db_session):
        """测试根据资源和操作查找权限"""
        repo = PermissionRepository(db_session)
        
        # 创建测试权限
        perm = PermissionORM(
            permission_id=uuid7(),
            name="user.users.view",
            display_name="查看用户",
            description="查看用户列表",
            module="user",
            resource="users",
            action="view"
        )
        
        db_session.add(perm)
        await db_session.commit()
        
        # 测试查找
        found_perm = await repo.find_by_resource_action("users", "view")
        assert found_perm is not None
        assert found_perm.resource == "users"
        assert found_perm.action == "view"
        
        # 测试不存在的权限
        not_found = await repo.find_by_resource_action("users", "delete")
        assert not_found is None

    async def test_find_by_ids(self, db_session):
        """测试批量根据ID查找权限"""
        repo = PermissionRepository(db_session)
        
        # 创建测试权限
        perm1_id = uuid7()
        perm2_id = uuid7()
        perm1 = PermissionORM(
            permission_id=perm1_id,
            name="user.users.view",
            display_name="查看用户",
            description="查看用户列表",
            module="user",
            resource="users",
            action="view"
        )
        perm2 = PermissionORM(
            permission_id=perm2_id,
            name="user.roles.create",
            display_name="创建角色",
            description="创建新角色",
            module="user",
            resource="roles",
            action="create"
        )
        
        db_session.add_all([perm1, perm2])
        await db_session.commit()
        
        # 测试批量查找
        permissions = await repo.find_by_ids([perm1_id, perm2_id])
        assert len(permissions) == 2
        
        found_ids = {perm.id for perm in permissions}
        assert perm1_id in found_ids
        assert perm2_id in found_ids

    async def test_find_by_names(self, db_session):
        """测试批量根据名称查找权限"""
        repo = PermissionRepository(db_session)
        
        # 创建测试权限
        perm1 = PermissionORM(
            permission_id=uuid7(),
            name="user.users.view",
            display_name="查看用户",
            description="查看用户列表",
            module="user",
            resource="users",
            action="view"
        )
        perm2 = PermissionORM(
            permission_id=uuid7(),
            name="user.roles.create",
            display_name="创建角色",
            description="创建新角色",
            module="user",
            resource="roles",
            action="create"
        )
        
        db_session.add_all([perm1, perm2])
        await db_session.commit()
        
        # 测试批量查找
        permissions = await repo.find_by_names(["user.users.view", "user.roles.create"])
        assert len(permissions) == 2
        
        found_names = {perm.name.value for perm in permissions}
        assert "user.users.view" in found_names
        assert "user.roles.create" in found_names

    async def test_search_permissions(self, db_session):
        """测试搜索权限"""
        repo = PermissionRepository(db_session)
        
        # 创建测试权限
        permissions_data = [
            ("user.users.view", "查看用户", "查看用户列表", "user", "users", "view"),
            ("user.users.create", "创建用户", "创建新用户", "user", "users", "create"),
            ("user.roles.view", "查看角色", "查看角色列表", "user", "roles", "view"),
            ("model.models.view", "查看模型", "查看模型列表", "model", "models", "view"),
        ]
        
        for name, display_name, description, module, resource, action in permissions_data:
            perm = PermissionORM(
                permission_id=uuid7(),
                name=name,
                display_name=display_name,
                description=description,
                module=module,
                resource=resource,
                action=action
            )
            db_session.add(perm)
        
        await db_session.commit()
        
        # 测试关键词搜索
        results = await repo.search_permissions(keyword="用户")
        assert len(results) == 2
        
        # 测试模块过滤
        results = await repo.search_permissions(module="user")
        assert len(results) == 3
        
        # 测试资源过滤
        results = await repo.search_permissions(resource="users")
        assert len(results) == 2
        
        # 测试分页
        results = await repo.search_permissions(limit=2, offset=0)
        assert len(results) == 2
        
        results = await repo.search_permissions(limit=2, offset=2)
        assert len(results) == 2

    async def test_count_permissions(self, db_session):
        """测试统计权限数量"""
        repo = PermissionRepository(db_session)
        
        # 创建测试权限
        permissions_data = [
            ("user.users.view", "查看用户", "查看用户列表", "user", "users", "view"),
            ("user.users.create", "创建用户", "创建新用户", "user", "users", "create"),
            ("model.models.view", "查看模型", "查看模型列表", "model", "models", "view"),
        ]
        
        for name, display_name, description, module, resource, action in permissions_data:
            perm = PermissionORM(
                permission_id=uuid7(),
                name=name,
                display_name=display_name,
                description=description,
                module=module,
                resource=resource,
                action=action
            )
            db_session.add(perm)
        
        await db_session.commit()
        
        # 测试总数统计
        total = await repo.count_permissions()
        assert total == 3
        
        # 测试关键词过滤统计
        count = await repo.count_permissions(keyword="用户")
        assert count == 2
        
        # 测试模块过滤统计
        count = await repo.count_permissions(module="user")
        assert count == 2
        
        # 测试资源过滤统计
        count = await repo.count_permissions(resource="users")
        assert count == 2

    async def test_save_and_find_permission(self, db_session):
        """测试保存和查找权限"""
        repo = PermissionRepository(db_session)
        
        # 创建权限实体
        permission = Permission(
            id=uuid7(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户列表",
            module="user"
        )
        
        # 保存权限
        saved_permission = await repo.save(permission)
        assert saved_permission.id == permission.id
        
        # 查找权限
        found_permission = await repo.find_by_id(permission.id)
        assert found_permission is not None
        assert found_permission.id == permission.id
        assert found_permission.name.value == "user.users.view"
        assert found_permission.display_name == "查看用户"
        assert found_permission.module == "user"
        assert found_permission.resource == "users"
        assert found_permission.action == "view"