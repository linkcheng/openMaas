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

"""用户聚合权限功能的单元测试"""

import pytest
from datetime import datetime
from uuid_extensions import uuid7

from src.shared.domain.base import EmailAddress
from src.user.domain.models import (
    User, Role, Permission, PermissionName, UserProfile, UserStatus, RoleType
)


class TestUserPermissions:
    """User聚合权限功能测试"""

    def create_test_user(self, username: str = "testuser") -> User:
        """创建测试用户"""
        return User.create(
            username=username,
            email=f"{username}@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )

    def create_test_permission(self, name: str, display_name: str = None) -> Permission:
        """创建测试权限"""
        return Permission(
            id=uuid7(),
            name=PermissionName(name),
            display_name=display_name or name,
            description=f"Test permission: {name}"
        )

    def create_test_role(self, name: str, permissions: list[Permission] = None) -> Role:
        """创建测试角色"""
        return Role(
            id=uuid7(),
            name=name,
            display_name=f"测试角色 {name}",
            description=f"测试角色 {name} 描述",
            permissions=permissions or [],
            role_type=RoleType.USER
        )

    def test_add_role_to_user(self):
        """测试为用户添加角色"""
        user = self.create_test_user()
        role = self.create_test_role("test_role")
        
        initial_key_version = user.key_version
        user.add_role(role)

        assert len(user.roles) == 1
        assert role in user.roles
        assert user.key_version == initial_key_version + 1  # 权限变更应该增加key版本

    def test_remove_role_from_user(self):
        """测试从用户移除角色"""
        role = self.create_test_role("test_role")
        user = self.create_test_user()
        user.add_role(role)
        
        initial_key_version = user.key_version
        user.remove_role(role)

        assert len(user.roles) == 0
        assert role not in user.roles
        assert user.key_version == initial_key_version + 1  # 权限变更应该增加key版本

    def test_set_roles_for_user(self):
        """测试设置用户角色列表"""
        role1 = self.create_test_role("role1")
        role2 = self.create_test_role("role2")
        role3 = self.create_test_role("role3")
        
        user = self.create_test_user()
        user.add_role(role1)
        user.add_role(role2)
        
        initial_key_version = user.key_version
        user.set_roles([role2, role3])  # 替换为新的角色列表

        assert len(user.roles) == 2
        assert role1 not in user.roles
        assert role2 in user.roles
        assert role3 in user.roles
        assert user.key_version == initial_key_version + 1

    def test_user_has_permission(self):
        """测试用户权限检查"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create"),
            self.create_test_permission("model.models.*")
        ]
        
        role = self.create_test_role("test_role", permissions)
        user = self.create_test_user()
        user.add_role(role)

        # 精确匹配
        assert user.has_permission("user.users.view")
        assert user.has_permission("user.users.create")
        
        # 通配符匹配
        assert user.has_permission("model.models.view")
        assert user.has_permission("model.models.create")
        assert user.has_permission("model.models.delete")
        
        # 不匹配
        assert not user.has_permission("admin.system.view")
        assert not user.has_permission("user.users.delete")

    def test_user_has_permission_by_parts(self):
        """测试通过资源和操作检查用户权限"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("model.models.*")
        ]
        
        role = self.create_test_role("test_role", permissions)
        user = self.create_test_user()
        user.add_role(role)

        # 精确匹配
        assert user.has_permission_by_parts("users", "view", "user")
        
        # 通配符匹配
        assert user.has_permission_by_parts("models", "create", "model")
        
        # 不匹配
        assert not user.has_permission_by_parts("users", "create", "user")
        assert not user.has_permission_by_parts("models", "view", "admin")

    def test_user_has_permission_by_parts_without_module(self):
        """测试不指定模块的用户权限检查"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("model.users.*")  # 不同模块的users资源
        ]
        
        role = self.create_test_role("test_role", permissions)
        user = self.create_test_user()
        user.add_role(role)

        # 不指定模块时，应该匹配任何模块的相同资源和操作
        assert user.has_permission_by_parts("users", "view")
        assert user.has_permission_by_parts("users", "create")  # 匹配 model.users.*

    def test_user_multiple_roles_permission_merge(self):
        """测试用户多角色权限合并"""
        permissions1 = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create")
        ]
        
        permissions2 = [
            self.create_test_permission("model.models.view"),
            self.create_test_permission("model.models.create")
        ]
        
        role1 = self.create_test_role("role1", permissions1)
        role2 = self.create_test_role("role2", permissions2)
        
        user = self.create_test_user()
        user.add_role(role1)
        user.add_role(role2)

        # 应该拥有两个角色的所有权限
        assert user.has_permission("user.users.view")
        assert user.has_permission("user.users.create")
        assert user.has_permission("model.models.view")
        assert user.has_permission("model.models.create")
        
        # 不应该拥有未分配的权限
        assert not user.has_permission("admin.system.view")

    def test_user_is_super_admin(self):
        """测试超级管理员检查"""
        # 普通用户
        regular_user = self.create_test_user("regular")
        regular_role = self.create_test_role("user", [
            self.create_test_permission("user.users.view")
        ])
        regular_user.add_role(regular_role)
        
        assert not regular_user.is_super_admin()

        # 超级管理员（通配符权限）
        super_admin = self.create_test_user("admin")
        super_admin_role = self.create_test_role("super_admin", [
            self.create_test_permission("*.*.*")
        ])
        super_admin.add_role(super_admin_role)
        
        assert super_admin.is_super_admin()



    def test_super_admin_has_all_permissions(self):
        """测试超级管理员拥有所有权限"""
        super_admin = self.create_test_user("admin")
        super_admin_role = self.create_test_role("super_admin", [
            self.create_test_permission("*.*.*")
        ])
        super_admin.add_role(super_admin_role)

        # 超级管理员应该拥有任何权限
        assert super_admin.has_permission("user.users.view")
        assert super_admin.has_permission("user.users.create")
        assert super_admin.has_permission("model.models.delete")
        assert super_admin.has_permission("admin.system.manage")
        assert super_admin.has_permission("any.resource.action")

        # 通过资源和操作检查也应该通过
        assert super_admin.has_permission_by_parts("users", "view", "user")
        assert super_admin.has_permission_by_parts("models", "create", "model")
        assert super_admin.has_permission_by_parts("system", "manage", "admin")

    def test_user_get_all_permissions(self):
        """测试获取用户所有权限"""
        permissions1 = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create")
        ]
        
        permissions2 = [
            self.create_test_permission("user.users.create"),  # 重复权限
            self.create_test_permission("model.models.view")
        ]
        
        role1 = self.create_test_role("role1", permissions1)
        role2 = self.create_test_role("role2", permissions2)
        
        user = self.create_test_user()
        user.add_role(role1)
        user.add_role(role2)

        all_permissions = user.get_all_permissions()
        
        # 应该包含所有不重复的权限
        assert len(all_permissions) == 3
        permission_names = [perm.name.value for perm in all_permissions]
        assert "user.users.view" in permission_names
        assert "user.users.create" in permission_names
        assert "model.models.view" in permission_names

    def test_super_admin_get_all_permissions(self):
        """测试超级管理员获取所有权限"""
        super_admin = self.create_test_user("admin")
        super_admin_role = self.create_test_role("super_admin", [
            self.create_test_permission("*.*.*")
        ])
        super_admin.add_role(super_admin_role)

        all_permissions = super_admin.get_all_permissions()
        
        # 超级管理员应该返回通配符权限
        assert len(all_permissions) == 1
        assert all_permissions[0].name.value == "*.*.*"
        assert all_permissions[0].display_name == "所有权限"

    def test_user_get_permissions_by_module(self):
        """测试获取指定模块的权限"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.roles.view"),
            self.create_test_permission("model.models.view"),
            self.create_test_permission("model.datasets.view")
        ]
        
        role = self.create_test_role("test_role", permissions)
        user = self.create_test_user()
        user.add_role(role)

        user_permissions = user.get_permissions_by_module("user")
        model_permissions = user.get_permissions_by_module("model")
        admin_permissions = user.get_permissions_by_module("admin")

        # user模块权限
        assert len(user_permissions) == 2
        user_permission_names = [perm.name.value for perm in user_permissions]
        assert "user.users.view" in user_permission_names
        assert "user.roles.view" in user_permission_names

        # model模块权限
        assert len(model_permissions) == 2
        model_permission_names = [perm.name.value for perm in model_permissions]
        assert "model.models.view" in model_permission_names
        assert "model.datasets.view" in model_permission_names

        # admin模块权限（无权限）
        assert len(admin_permissions) == 0

    def test_super_admin_get_permissions_by_module(self):
        """测试超级管理员获取指定模块权限"""
        super_admin = self.create_test_user("admin")
        super_admin_role = self.create_test_role("super_admin", [
            self.create_test_permission("*.*.*")
        ])
        super_admin.add_role(super_admin_role)

        user_permissions = super_admin.get_permissions_by_module("user")
        model_permissions = super_admin.get_permissions_by_module("model")

        # 超级管理员对任何模块都应该返回通配符权限
        assert len(user_permissions) == 1
        assert user_permissions[0].name.value == "*.*.*"
        
        assert len(model_permissions) == 1
        assert model_permissions[0].name.value == "*.*.*"

    def test_user_invalidate_permission_cache(self):
        """测试用户权限缓存失效"""
        user = self.create_test_user()
        initial_key_version = user.key_version
        
        user.invalidate_permission_cache()
        
        assert user.key_version == initial_key_version + 1

    def test_user_permission_cache_invalidation_on_role_changes(self):
        """测试角色变更时权限缓存自动失效"""
        user = self.create_test_user()
        role = self.create_test_role("test_role")
        
        initial_key_version = user.key_version
        
        # 添加角色应该使缓存失效
        user.add_role(role)
        assert user.key_version == initial_key_version + 1
        
        # 移除角色应该使缓存失效
        current_key_version = user.key_version
        user.remove_role(role)
        assert user.key_version == current_key_version + 1
        
        # 设置角色列表应该使缓存失效
        current_key_version = user.key_version
        user.set_roles([role])
        assert user.key_version == current_key_version + 1

    def test_user_roles_immutability(self):
        """测试用户角色列表的不可变性"""
        role1 = self.create_test_role("role1")
        role2 = self.create_test_role("role2")
        
        user = self.create_test_user()
        user.add_role(role1)
        
        # 获取角色列表应该返回副本
        user_roles = user.roles
        user_roles.append(role2)
        
        # 原用户的角色列表不应该被修改
        assert len(user.roles) == 1
        assert len(user_roles) == 2
        assert role2 not in user.roles

    def test_user_without_roles_has_no_permissions(self):
        """测试没有角色的用户没有权限"""
        user = self.create_test_user()
        
        assert not user.has_permission("user.users.view")
        assert not user.has_permission_by_parts("users", "view", "user")
        assert not user.is_super_admin()
        assert len(user.get_all_permissions()) == 0
        assert len(user.get_permissions_by_module("user")) == 0

    def test_user_with_empty_role_has_no_permissions(self):
        """测试拥有空权限角色的用户没有权限"""
        empty_role = self.create_test_role("empty_role", [])
        user = self.create_test_user()
        user.add_role(empty_role)
        
        assert not user.has_permission("user.users.view")
        assert not user.has_permission_by_parts("users", "view", "user")
        assert not user.is_super_admin()
        assert len(user.get_all_permissions()) == 0
        assert len(user.get_permissions_by_module("user")) == 0