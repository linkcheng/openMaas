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

"""用户仓储集成测试"""

import pytest
from uuid import UUID
from uuid_extensions import uuid7

from shared.domain.base import EmailAddress
from user.domain.models import User, UserProfile, UserStatus, Role, Permission, PermissionName, RoleType
from user.infrastructure.repositories import UserRepository
from user.infrastructure.models import (
    UserORM, RoleORM, PermissionORM, UserRoleORM, RolePermissionORM
)


@pytest.mark.asyncio
class TestUserRepository:
    """用户仓储测试"""

    async def test_find_users_with_permissions(self, db_session):
        """测试查找拥有指定权限的用户"""
        repo = UserRepository(db_session)
        
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
        
        # 创建测试用户
        user1_id = uuid7()
        user2_id = uuid7()
        user1 = UserORM(
            user_id=user1_id,
            username="admin_user",
            email="admin@example.com",
            password_hash="hashed_password",
            first_name="Admin",
            last_name="User",
            status="active",
            email_verified=True
        )
        user2 = UserORM(
            user_id=user2_id,
            username="normal_user",
            email="user@example.com",
            password_hash="hashed_password",
            first_name="Normal",
            last_name="User",
            status="active",
            email_verified=True
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
        
        # 创建用户角色关联
        user_role1 = UserRoleORM(
            user_role_id=uuid7(),
            user_id=user1_id,
            role_id=role1_id
        )
        user_role2 = UserRoleORM(
            user_role_id=uuid7(),
            user_id=user2_id,
            role_id=role2_id
        )
        
        db_session.add_all([
            perm1, perm2, role1, role2, user1, user2,
            role_perm1, role_perm2, role_perm3, user_role1, user_role2
        ])
        await db_session.commit()
        
        # 测试查找拥有指定权限的用户
        users = await repo.find_users_with_permissions(["user.users.view"])
        assert len(users) == 2  # admin_user 和 normal_user 都有查看用户权限
        
        users = await repo.find_users_with_permissions(["user.roles.create"])
        assert len(users) == 1  # 只有 admin_user 有创建角色权限
        assert users[0].username == "admin_user"

    async def test_batch_update_user_roles(self, db_session):
        """测试批量更新用户角色"""
        repo = UserRepository(db_session)
        
        # 创建测试角色
        role1_id = uuid7()
        role2_id = uuid7()
        role3_id = uuid7()
        
        roles_data = [
            (role1_id, "admin", "管理员", "系统管理员", "admin", True),
            (role2_id, "user", "普通用户", "普通用户", "user", False),
            (role3_id, "developer", "开发者", "开发者角色", "developer", False),
        ]
        
        for role_id, name, display_name, description, role_type, is_system in roles_data:
            role = RoleORM(
                role_id=role_id,
                name=name,
                display_name=display_name,
                description=description,
                role_type=role_type,
                is_system_role=is_system
            )
            db_session.add(role)
        
        # 创建测试用户
        user1_id = uuid7()
        user2_id = uuid7()
        
        users_data = [
            (user1_id, "user1", "user1@example.com", "User", "One"),
            (user2_id, "user2", "user2@example.com", "User", "Two"),
        ]
        
        for user_id, username, email, first_name, last_name in users_data:
            user = UserORM(
                user_id=user_id,
                username=username,
                email=email,
                password_hash="hashed_password",
                first_name=first_name,
                last_name=last_name,
                status="active",
                email_verified=True
            )
            db_session.add(user)
        
        await db_session.commit()
        
        # 批量更新用户角色
        updates = [
            {
                'user_id': user1_id,
                'role_ids': [role1_id, role3_id],  # admin + developer
                'granted_by_id': None
            },
            {
                'user_id': user2_id,
                'role_ids': [role2_id],  # user only
                'granted_by_id': None
            }
        ]
        
        result = await repo.batch_update_user_roles(updates)
        assert result is True
        
        # 验证角色更新
        user1 = await repo.find_by_id(user1_id)
        assert len(user1.roles) == 2
        role_names = {role.name for role in user1.roles}
        assert "admin" in role_names
        assert "developer" in role_names
        
        user2 = await repo.find_by_id(user2_id)
        assert len(user2.roles) == 1
        assert user2.roles[0].name == "user"

    async def test_find_by_ids(self, db_session):
        """测试批量根据ID查找用户"""
        repo = UserRepository(db_session)
        
        # 创建测试用户
        user1_id = uuid7()
        user2_id = uuid7()
        
        users_data = [
            (user1_id, "user1", "user1@example.com", "User", "One"),
            (user2_id, "user2", "user2@example.com", "User", "Two"),
        ]
        
        for user_id, username, email, first_name, last_name in users_data:
            user = UserORM(
                user_id=user_id,
                username=username,
                email=email,
                password_hash="hashed_password",
                first_name=first_name,
                last_name=last_name,
                status="active",
                email_verified=True
            )
            db_session.add(user)
        
        await db_session.commit()
        
        # 测试批量查找
        users = await repo.find_by_ids([user1_id, user2_id])
        assert len(users) == 2
        
        found_ids = {user.id for user in users}
        assert user1_id in found_ids
        assert user2_id in found_ids

    async def test_load_user_permissions_with_cache(self, db_session):
        """测试加载用户权限（支持缓存策略）"""
        repo = UserRepository(db_session)
        
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
        role_id = uuid7()
        role = RoleORM(
            role_id=role_id,
            name="admin",
            display_name="管理员",
            description="系统管理员",
            role_type="admin",
            is_system_role=True
        )
        
        # 创建测试用户
        user_id = uuid7()
        user = UserORM(
            user_id=user_id,
            username="test_user",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            status="active",
            email_verified=True
        )
        
        # 创建关联
        role_perm1 = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role_id,
            permission_id=perm1_id
        )
        role_perm2 = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role_id,
            permission_id=perm2_id
        )
        user_role = UserRoleORM(
            user_role_id=uuid7(),
            user_id=user_id,
            role_id=role_id
        )
        
        db_session.add_all([
            perm1, perm2, role, user, role_perm1, role_perm2, user_role
        ])
        await db_session.commit()
        
        # 测试加载用户权限
        permissions = await repo.load_user_permissions_with_cache(user_id)
        assert len(permissions) == 2
        
        permission_names = {perm.name.value for perm in permissions}
        assert "user.users.view" in permission_names
        assert "user.roles.create" in permission_names

    async def test_find_users_by_permission_and_module(self, db_session):
        """测试根据模块和权限名称查找用户"""
        repo = UserRepository(db_session)
        
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
            name="model.models.view",
            display_name="查看模型",
            description="查看模型列表",
            module="model",
            resource="models",
            action="view"
        )
        
        # 创建测试角色
        role1_id = uuid7()
        role2_id = uuid7()
        role1 = RoleORM(
            role_id=role1_id,
            name="user_admin",
            display_name="用户管理员",
            description="用户模块管理员",
            role_type="admin",
            is_system_role=False
        )
        role2 = RoleORM(
            role_id=role2_id,
            name="model_admin",
            display_name="模型管理员",
            description="模型模块管理员",
            role_type="admin",
            is_system_role=False
        )
        
        # 创建测试用户
        user1_id = uuid7()
        user2_id = uuid7()
        user1 = UserORM(
            user_id=user1_id,
            username="user_admin",
            email="user_admin@example.com",
            password_hash="hashed_password",
            first_name="User",
            last_name="Admin",
            status="active",
            email_verified=True
        )
        user2 = UserORM(
            user_id=user2_id,
            username="model_admin",
            email="model_admin@example.com",
            password_hash="hashed_password",
            first_name="Model",
            last_name="Admin",
            status="active",
            email_verified=True
        )
        
        # 创建关联
        role_perm1 = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role1_id,
            permission_id=perm1_id
        )
        role_perm2 = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role2_id,
            permission_id=perm2_id
        )
        user_role1 = UserRoleORM(
            user_role_id=uuid7(),
            user_id=user1_id,
            role_id=role1_id
        )
        user_role2 = UserRoleORM(
            user_role_id=uuid7(),
            user_id=user2_id,
            role_id=role2_id
        )
        
        db_session.add_all([
            perm1, perm2, role1, role2, user1, user2,
            role_perm1, role_perm2, user_role1, user_role2
        ])
        await db_session.commit()
        
        # 测试根据模块和权限查找用户
        users = await repo.find_users_by_permission_and_module("user", "user.users.view")
        assert len(users) == 1
        assert users[0].username == "user_admin"
        
        users = await repo.find_users_by_permission_and_module("model", "model.models.view")
        assert len(users) == 1
        assert users[0].username == "model_admin"
        
        # 测试不存在的权限
        users = await repo.find_users_by_permission_and_module("user", "nonexistent.permission")
        assert len(users) == 0

    async def test_find_by_role_id_with_permissions(self, db_session):
        """测试根据角色ID查找用户（包含权限预加载）"""
        repo = UserRepository(db_session)
        
        # 创建测试权限
        perm_id = uuid7()
        perm = PermissionORM(
            permission_id=perm_id,
            name="user.users.view",
            display_name="查看用户",
            description="查看用户列表",
            module="user",
            resource="users",
            action="view"
        )
        
        # 创建测试角色
        role_id = uuid7()
        role = RoleORM(
            role_id=role_id,
            name="admin",
            display_name="管理员",
            description="系统管理员",
            role_type="admin",
            is_system_role=True
        )
        
        # 创建测试用户
        user1_id = uuid7()
        user2_id = uuid7()
        user1 = UserORM(
            user_id=user1_id,
            username="admin1",
            email="admin1@example.com",
            password_hash="hashed_password",
            first_name="Admin",
            last_name="One",
            status="active",
            email_verified=True
        )
        user2 = UserORM(
            user_id=user2_id,
            username="admin2",
            email="admin2@example.com",
            password_hash="hashed_password",
            first_name="Admin",
            last_name="Two",
            status="active",
            email_verified=True
        )
        
        # 创建关联
        role_perm = RolePermissionORM(
            role_permission_id=uuid7(),
            role_id=role_id,
            permission_id=perm_id
        )
        user_role1 = UserRoleORM(
            user_role_id=uuid7(),
            user_id=user1_id,
            role_id=role_id
        )
        user_role2 = UserRoleORM(
            user_role_id=uuid7(),
            user_id=user2_id,
            role_id=role_id
        )
        
        db_session.add_all([
            perm, role, user1, user2, role_perm, user_role1, user_role2
        ])
        await db_session.commit()
        
        # 测试根据角色ID查找用户
        users = await repo.find_by_role_id(role_id)
        assert len(users) == 2
        
        # 验证用户包含角色和权限信息
        for user in users:
            assert len(user.roles) == 1
            assert user.roles[0].name == "admin"
            assert len(user.roles[0].permissions) == 1
            assert user.roles[0].permissions[0].name.value == "user.users.view"