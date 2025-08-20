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

"""角色仓储集成测试"""

import pytest
from uuid import UUID
from uuid_extensions import uuid7

from user.domain.models import Role, Permission, PermissionName, RoleType
from user.infrastructure.repositories import RoleRepository
from user.infrastructure.models import RoleORM, PermissionORM, RolePermissionORM


@pytest.mark.asyncio
class TestRoleRepository:
    """角色仓储测试"""

    async def test_find_roles_with_permissions(self, db_session):
        """测试查找包含指定权限的角色"""
        repo = RoleRepository(db_session)
        
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
        
        # 创建测试角色
        role1_id = uuid7()
        role2_id = uuid7()
        role1 = RoleORM(
            role_id=role1_id,
            name="admin",
            display_name="管理员",
            description="系统管理员",
            role_type="admin",
            is_system_role=True
        )
        role2 = RoleORM(
            role_id=role2_id,
            name="user",
            display_name="普通用户",
            description="普通用户",
            role_type="user",
            is_system_role=False
        )
        
        # 创建角色权限关联
        role_perm1 = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role1_id,
            permission_id=perm1_id
        )
        role_perm2 = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role1_id,
            permission_id=perm2_id
        )
        role_perm3 = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role2_id,
            permission_id=perm1_id
        )
        
        db_session.add_all([perm1, perm2, role1, role2, role_perm1, role_perm2, role_perm3])
        await db_session.commit()
        
        # 测试查找包含指定权限的角色
        roles = await repo.find_roles_with_permissions([perm1_id])
        assert len(roles) == 2  # admin 和 user 都有 perm1
        
        roles = await repo.find_roles_with_permissions([perm2_id])
        assert len(roles) == 1  # 只有 admin 有 perm2
        
        # 测试查找所有角色（不指定权限）
        all_roles = await repo.find_roles_with_permissions(None)
        assert len(all_roles) == 2

    async def test_find_by_ids(self, db_session):
        """测试批量根据ID查找角色"""
        repo = RoleRepository(db_session)
        
        # 创建测试角色
        role1_id = uuid7()
        role2_id = uuid7()
        role1 = RoleORM(
            role_id=role1_id,
            name="admin",
            display_name="管理员",
            description="系统管理员",
            role_type="admin",
            is_system_role=True
        )
        role2 = RoleORM(
            role_id=role2_id,
            name="user",
            display_name="普通用户",
            description="普通用户",
            role_type="user",
            is_system_role=False
        )
        
        db_session.add_all([role1, role2])
        await db_session.commit()
        
        # 测试批量查找
        roles = await repo.find_by_ids([role1_id, role2_id])
        assert len(roles) == 2
        
        found_ids = {role.id for role in roles}
        assert role1_id in found_ids
        assert role2_id in found_ids

    async def test_count_roles(self, db_session):
        """测试统计角色数量"""
        repo = RoleRepository(db_session)
        
        # 创建测试角色
        roles_data = [
            ("admin", "管理员", "系统管理员", "admin", True),
            ("user", "普通用户", "普通用户", "user", False),
            ("developer", "开发者", "开发者角色", "developer", False),
        ]
        
        for name, display_name, description, role_type, is_system in roles_data:
            role = RoleORM(
                role_id=uuid7(),
                name=name,
                display_name=display_name,
                description=description,
                role_type=role_type,
                is_system_role=is_system
            )
            db_session.add(role)
        
        await db_session.commit()
        
        # 测试总数统计
        total = await repo.count_roles()
        assert total == 3
        
        # 测试名称过滤统计
        count = await repo.count_roles(name="admin")
        assert count == 1

    async def test_search_roles_with_permissions(self, db_session):
        """测试搜索角色（包含权限预加载）"""
        repo = RoleRepository(db_session)
        
        # 创建测试权限
        perm1_id = uuid7()
        perm1 = PermissionORM(
            permission_id=perm1_id,
            name="user.users.view",
            display_name="查看用户",
            description="查看用户列表",
            module="user",
            resource="users",
            action="view"
        )
        
        # 创建测试角色
        role1_id = uuid7()
        role1 = RoleORM(
            role_id=role1_id,
            name="admin",
            display_name="管理员",
            description="系统管理员",
            role_type="admin",
            is_system_role=True
        )
        
        # 创建角色权限关联
        role_perm1 = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role1_id,
            permission_id=perm1_id
        )
        
        db_session.add_all([perm1, role1, role_perm1])
        await db_session.commit()
        
        # 测试搜索角色
        roles = await repo.search_roles(name="admin")
        assert len(roles) == 1
        
        role = roles[0]
        assert role.name == "admin"
        assert len(role.permissions) == 1
        assert role.permissions[0].name.value == "user.users.view"

    async def test_save_role_with_permissions(self, db_session):
        """测试保存角色及其权限"""
        repo = RoleRepository(db_session)
        
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
        
        # 创建权限实体
        permission1 = Permission(
            id=perm1_id,
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户列表",
            module="user"
        )
        permission2 = Permission(
            id=perm2_id,
            name=PermissionName("user.roles.create"),
            display_name="创建角色",
            description="创建新角色",
            module="user"
        )
        
        # 创建角色实体
        role = Role(
            id=uuid7(),
            name="test_admin",
            display_name="测试管理员",
            description="测试管理员角色",
            permissions=[permission1, permission2],
            is_system_role=False,
            role_type=RoleType.ADMIN
        )
        
        # 保存角色
        saved_role = await repo.save(role)
        assert saved_role.id == role.id
        
        # 查找角色验证权限
        found_role = await repo.find_by_id(role.id)
        assert found_role is not None
        assert found_role.name == "test_admin"
        assert len(found_role.permissions) == 2
        
        permission_names = {perm.name.value for perm in found_role.permissions}
        assert "user.users.view" in permission_names
        assert "user.roles.create" in permission_names

    async def test_update_role_permissions(self, db_session):
        """测试更新角色权限"""
        repo = RoleRepository(db_session)
        
        # 创建测试权限
        perm1_id = uuid7()
        perm2_id = uuid7()
        perm3_id = uuid7()
        
        permissions_data = [
            (perm1_id, "user.users.view", "查看用户", "查看用户列表", "user", "users", "view"),
            (perm2_id, "user.roles.create", "创建角色", "创建新角色", "user", "roles", "create"),
            (perm3_id, "user.permissions.manage", "管理权限", "管理系统权限", "user", "permissions", "manage"),
        ]
        
        for perm_id, name, display_name, description, module, resource, action in permissions_data:
            perm = PermissionORM(
                permission_id=perm_id,
                name=name,
                display_name=display_name,
                description=description,
                module=module,
                resource=resource,
                action=action
            )
            db_session.add(perm)
        
        await db_session.commit()
        
        # 创建角色实体（初始只有一个权限）
        permission1 = Permission(
            id=perm1_id,
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户列表",
            module="user"
        )
        
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=[permission1],
            is_system_role=False,
            role_type=RoleType.USER
        )
        
        # 保存角色
        await repo.save(role)
        
        # 更新角色权限（添加更多权限）
        permission2 = Permission(
            id=perm2_id,
            name=PermissionName("user.roles.create"),
            display_name="创建角色",
            description="创建新角色",
            module="user"
        )
        permission3 = Permission(
            id=perm3_id,
            name=PermissionName("user.permissions.manage"),
            display_name="管理权限",
            description="管理系统权限",
            module="user"
        )
        
        role.add_permissions([permission2, permission3])
        
        # 保存更新后的角色
        await repo.save(role)
        
        # 验证权限更新
        found_role = await repo.find_by_id(role.id)
        assert len(found_role.permissions) == 3
        
        permission_names = {perm.name.value for perm in found_role.permissions}
        assert "user.users.view" in permission_names
        assert "user.roles.create" in permission_names
        assert "user.permissions.manage" in permission_names