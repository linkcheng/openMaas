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

"""角色实体的单元测试"""

import pytest
from uuid_extensions import uuid7

from src.shared.domain.base import BusinessRuleViolationException
from src.user.domain.models import Role, Permission, PermissionName, RoleType


class TestRole:
    """Role实体测试"""

    def create_test_permission(self, name: str, display_name: str = None) -> Permission:
        """创建测试权限"""
        return Permission(
            id=uuid7(),
            name=PermissionName(name),
            display_name=display_name or name,
            description=f"Test permission: {name}"
        )

    def test_create_role(self):
        """测试创建角色"""
        role_id = uuid7()
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create")
        ]
        
        role = Role(
            id=role_id,
            name="test_role",
            display_name="测试角色",
            description="测试角色描述",
            permissions=permissions,
            is_system_role=False,
            role_type=RoleType.USER
        )

        assert role.id == role_id
        assert role.name == "test_role"
        assert role.display_name == "测试角色"
        assert role.description == "测试角色描述"
        assert len(role.permissions) == 2
        assert not role.is_system_role
        assert role.role_type == RoleType.USER

    def test_create_role_with_defaults(self):
        """测试使用默认值创建角色"""
        role = Role(
            id=uuid7(),
            name="default_role",
            display_name="默认角色",
            description="默认角色描述"
        )

        assert len(role.permissions) == 0
        assert not role.is_system_role
        assert role.role_type == RoleType.USER

    def test_create_system_role(self):
        """测试创建系统角色"""
        role = Role(
            id=uuid7(),
            name="admin",
            display_name="管理员",
            description="系统管理员角色",
            is_system_role=True,
            role_type=RoleType.ADMIN
        )

        assert role.is_system_role
        assert role.role_type == RoleType.ADMIN

    def test_add_permission(self):
        """测试添加权限"""
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色"
        )
        
        permission = self.create_test_permission("user.users.view")
        role.add_permission(permission)

        assert len(role.permissions) == 1
        assert permission in role.permissions

    def test_add_duplicate_permission(self):
        """测试添加重复权限"""
        permission = self.create_test_permission("user.users.view")
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=[permission]
        )
        
        # 添加相同权限不应该重复
        role.add_permission(permission)
        assert len(role.permissions) == 1

    def test_add_permission_to_system_role(self):
        """测试向系统角色添加权限"""
        role = Role(
            id=uuid7(),
            name="admin",
            display_name="管理员",
            description="系统管理员",
            is_system_role=True
        )
        
        permission = self.create_test_permission("user.users.view")
        
        with pytest.raises(BusinessRuleViolationException):
            role.add_permission(permission)

    def test_remove_permission(self):
        """测试移除权限"""
        permission = self.create_test_permission("user.users.view")
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=[permission]
        )
        
        role.remove_permission(permission)
        assert len(role.permissions) == 0
        assert permission not in role.permissions

    def test_remove_nonexistent_permission(self):
        """测试移除不存在的权限"""
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色"
        )
        
        permission = self.create_test_permission("user.users.view")
        
        # 移除不存在的权限不应该报错
        role.remove_permission(permission)
        assert len(role.permissions) == 0

    def test_remove_permission_from_system_role(self):
        """测试从系统角色移除权限"""
        permission = self.create_test_permission("user.users.view")
        role = Role(
            id=uuid7(),
            name="admin",
            display_name="管理员",
            description="系统管理员",
            permissions=[permission],
            is_system_role=True
        )
        
        with pytest.raises(BusinessRuleViolationException):
            role.remove_permission(permission)

    def test_add_permissions_batch(self):
        """测试批量添加权限"""
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色"
        )
        
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create"),
            self.create_test_permission("user.roles.view")
        ]
        
        role.add_permissions(permissions)
        assert len(role.permissions) == 3
        for permission in permissions:
            assert permission in role.permissions

    def test_add_permissions_batch_to_system_role(self):
        """测试向系统角色批量添加权限"""
        role = Role(
            id=uuid7(),
            name="admin",
            display_name="管理员",
            description="系统管理员",
            is_system_role=True
        )
        
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create")
        ]
        
        with pytest.raises(BusinessRuleViolationException):
            role.add_permissions(permissions)

    def test_remove_permissions_batch(self):
        """测试批量移除权限"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create"),
            self.create_test_permission("user.roles.view")
        ]
        
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=permissions
        )
        
        permissions_to_remove = permissions[:2]  # 移除前两个权限
        role.remove_permissions(permissions_to_remove)
        
        assert len(role.permissions) == 1
        assert permissions[2] in role.permissions
        for permission in permissions_to_remove:
            assert permission not in role.permissions

    def test_set_permissions(self):
        """测试设置权限列表"""
        initial_permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create")
        ]
        
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=initial_permissions
        )
        
        new_permissions = [
            self.create_test_permission("model.models.view"),
            self.create_test_permission("model.models.create")
        ]
        
        role.set_permissions(new_permissions)
        
        assert len(role.permissions) == 2
        for permission in new_permissions:
            assert permission in role.permissions
        for permission in initial_permissions:
            assert permission not in role.permissions

    def test_set_permissions_on_system_role(self):
        """测试设置系统角色权限"""
        role = Role(
            id=uuid7(),
            name="admin",
            display_name="管理员",
            description="系统管理员",
            is_system_role=True
        )
        
        permissions = [self.create_test_permission("user.users.view")]
        
        with pytest.raises(BusinessRuleViolationException):
            role.set_permissions(permissions)

    def test_has_permission(self):
        """测试权限检查"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.*"),
            self.create_test_permission("model.models.view")
        ]
        
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=permissions
        )

        # 精确匹配
        assert role.has_permission("user.users.view")
        assert role.has_permission("model.models.view")
        
        # 通配符匹配
        assert role.has_permission("user.users.create")  # 匹配 user.users.*
        assert role.has_permission("user.users.delete")  # 匹配 user.users.*
        
        # 不匹配
        assert not role.has_permission("model.models.create")
        assert not role.has_permission("admin.system.view")

    def test_has_permission_invalid_format(self):
        """测试无效格式的权限检查"""
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色"
        )

        # 无效格式的权限名称应该返回False
        assert not role.has_permission("invalid")
        assert not role.has_permission("user.users")
        assert not role.has_permission("")

    def test_has_permission_by_parts(self):
        """测试通过资源和操作检查权限"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("model.models.*")
        ]
        
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=permissions
        )

        # 精确匹配
        assert role.has_permission_by_parts("users", "view", "user")
        
        # 通配符匹配
        assert role.has_permission_by_parts("models", "create", "model")
        assert role.has_permission_by_parts("models", "delete", "model")
        
        # 不匹配
        assert not role.has_permission_by_parts("users", "create", "user")
        assert not role.has_permission_by_parts("models", "view", "admin")

    def test_has_permission_by_parts_without_module(self):
        """测试不指定模块的权限检查"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("model.users.*")  # 不同模块的users资源
        ]
        
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=permissions
        )

        # 不指定模块时，应该匹配任何模块的相同资源和操作
        assert role.has_permission_by_parts("users", "view")
        assert role.has_permission_by_parts("users", "create")  # 匹配 model.users.*

    def test_merge_permissions(self):
        """测试合并权限"""
        permissions1 = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create")
        ]
        
        permissions2 = [
            self.create_test_permission("user.users.create"),  # 重复权限
            self.create_test_permission("model.models.view"),
            self.create_test_permission("model.models.create")
        ]
        
        role1 = Role(
            id=uuid7(),
            name="role1",
            display_name="角色1",
            description="角色1",
            permissions=permissions1
        )
        
        role2 = Role(
            id=uuid7(),
            name="role2",
            display_name="角色2",
            description="角色2",
            permissions=permissions2
        )
        
        merged_permissions = role1.merge_permissions(role2)
        
        # 应该包含所有不重复的权限
        assert len(merged_permissions) == 4
        
        # 原角色权限不应该被修改
        assert len(role1.permissions) == 2
        assert len(role2.permissions) == 3

    def test_can_be_deleted(self):
        """测试角色是否可以删除"""
        regular_role = Role(
            id=uuid7(),
            name="regular_role",
            display_name="普通角色",
            description="普通角色",
            is_system_role=False
        )
        
        system_role = Role(
            id=uuid7(),
            name="admin",
            display_name="管理员",
            description="系统管理员",
            is_system_role=True
        )

        assert regular_role.can_be_deleted()
        assert not system_role.can_be_deleted()

    def test_role_equality(self):
        """测试角色相等性"""
        role1 = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色"
        )
        
        role2 = Role(
            id=uuid7(),
            name="test_role",
            display_name="不同的显示名称",  # 不同的显示名称
            description="不同的描述"  # 不同的描述
        )
        
        role3 = Role(
            id=uuid7(),
            name="different_role",
            display_name="不同角色",
            description="不同角色"
        )

        # 相同名称的角色应该相等
        assert role1 == role2
        assert hash(role1) == hash(role2)
        
        # 不同名称的角色不相等
        assert role1 != role3
        assert hash(role1) != hash(role3)

    def test_permissions_immutability(self):
        """测试权限列表的不可变性"""
        permissions = [
            self.create_test_permission("user.users.view"),
            self.create_test_permission("user.users.create")
        ]
        
        role = Role(
            id=uuid7(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=permissions
        )
        
        # 获取权限列表应该返回副本
        role_permissions = role.permissions
        role_permissions.append(self.create_test_permission("user.users.delete"))
        
        # 原角色的权限列表不应该被修改
        assert len(role.permissions) == 2
        assert len(role_permissions) == 3