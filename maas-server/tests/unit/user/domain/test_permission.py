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

"""权限实体和值对象的单元测试"""

import pytest
from uuid import UUID
from uuid_extensions import uuid7

from src.user.domain.models import Permission, PermissionName


class TestPermissionName:
    """PermissionName值对象测试"""

    def test_valid_permission_name(self):
        """测试有效的权限名称"""
        permission_name = PermissionName("user.users.view")
        assert permission_name.value == "user.users.view"
        assert permission_name.module == "user"
        assert permission_name.resource == "users"
        assert permission_name.action == "view"

    def test_wildcard_permission_name(self):
        """测试通配符权限名称"""
        permission_name = PermissionName("user.users.*")
        assert permission_name.value == "user.users.*"
        assert permission_name.module == "user"
        assert permission_name.resource == "users"
        assert permission_name.action == "*"

    def test_full_wildcard_permission_name(self):
        """测试完全通配符权限名称"""
        permission_name = PermissionName("*.*.*")
        assert permission_name.value == "*.*.*"
        assert permission_name.module == "*"
        assert permission_name.resource == "*"
        assert permission_name.action == "*"

    def test_invalid_permission_name_format(self):
        """测试无效的权限名称格式"""
        with pytest.raises(ValueError, match="权限名称必须遵循"):
            PermissionName("invalid")
        
        with pytest.raises(ValueError, match="权限名称必须遵循"):
            PermissionName("user.users")
        
        with pytest.raises(ValueError, match="权限名称必须遵循"):
            PermissionName("user.users.view.extra")

    def test_empty_permission_name(self):
        """测试空权限名称"""
        with pytest.raises(ValueError, match="权限名称不能为空"):
            PermissionName("")
        
        with pytest.raises(ValueError, match="权限名称不能为空"):
            PermissionName("   ")

    def test_empty_parts(self):
        """测试空的权限名称部分"""
        with pytest.raises(ValueError, match="权限名称的各部分不能为空"):
            PermissionName("user..view")
        
        with pytest.raises(ValueError, match="权限名称的各部分不能为空"):
            PermissionName(".users.view")
        
        with pytest.raises(ValueError, match="权限名称的各部分不能为空"):
            PermissionName("user.users.")

    def test_invalid_characters(self):
        """测试无效字符"""
        with pytest.raises(ValueError, match="只能包含小写字母、数字和下划线"):
            PermissionName("User.users.view")  # 大写字母
        
        with pytest.raises(ValueError, match="只能包含小写字母、数字和下划线"):
            PermissionName("user.users-admin.view")  # 连字符
        
        with pytest.raises(ValueError, match="只能包含小写字母、数字和下划线"):
            PermissionName("user.users.View")  # 大写字母

    def test_invalid_start_character(self):
        """测试无效的开始字符"""
        with pytest.raises(ValueError, match="只能包含小写字母、数字和下划线，且必须以字母开头"):
            PermissionName("1user.users.view")  # 数字开头
        
        with pytest.raises(ValueError, match="只能包含小写字母、数字和下划线，且必须以字母开头"):
            PermissionName("user._users.view")  # 下划线开头

    def test_permission_name_matching(self):
        """测试权限名称匹配"""
        exact_permission = PermissionName("user.users.view")
        wildcard_action = PermissionName("user.users.*")
        wildcard_all = PermissionName("*.*.*")
        different_permission = PermissionName("model.models.view")

        # 精确匹配
        assert exact_permission.matches(exact_permission)
        
        # 通配符匹配
        assert wildcard_action.matches(exact_permission)
        assert wildcard_all.matches(exact_permission)
        assert wildcard_all.matches(wildcard_action)
        
        # 不匹配
        assert not exact_permission.matches(different_permission)
        assert not wildcard_action.matches(different_permission)

    def test_permission_name_immutability(self):
        """测试权限名称不可变性"""
        permission_name = PermissionName("user.users.view")
        
        # 尝试修改应该失败（frozen dataclass）
        with pytest.raises(AttributeError):
            permission_name.value = "modified"


class TestPermission:
    """Permission实体测试"""

    def test_create_permission(self):
        """测试创建权限"""
        permission_id = uuid7()
        permission_name = PermissionName("user.users.view")
        permission = Permission(
            id=permission_id,
            name=permission_name,
            display_name="查看用户",
            description="查看用户列表和详情"
        )

        assert permission.id == permission_id
        assert permission.name == permission_name
        assert permission.display_name == "查看用户"
        assert permission.description == "查看用户列表和详情"
        assert permission.module == "user"
        assert permission.resource == "users"
        assert permission.action == "view"

    def test_permission_with_custom_module(self):
        """测试带自定义模块的权限"""
        permission_name = PermissionName("user.users.view")
        permission = Permission(
            id=uuid7(),
            name=permission_name,
            display_name="查看用户",
            description="查看用户列表和详情",
            module="custom_module"
        )

        assert permission.module == "custom_module"
        assert permission.name.module == "user"  # name中的模块不变

    def test_permission_matching(self):
        """测试权限匹配"""
        exact_permission = Permission(
            id=uuid7(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户"
        )
        
        wildcard_permission = Permission(
            id=uuid7(),
            name=PermissionName("user.users.*"),
            display_name="用户所有操作",
            description="用户所有操作"
        )
        
        different_permission = Permission(
            id=uuid7(),
            name=PermissionName("model.models.view"),
            display_name="查看模型",
            description="查看模型"
        )

        # 精确匹配
        assert exact_permission.matches(exact_permission)
        
        # 通配符匹配
        assert wildcard_permission.matches(exact_permission)
        
        # 不匹配
        assert not exact_permission.matches(different_permission)

    def test_permission_string_representation(self):
        """测试权限字符串表示"""
        permission = Permission(
            id=uuid7(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户"
        )

        assert str(permission) == "user.users.view"

    def test_permission_equality(self):
        """测试权限相等性"""
        permission1 = Permission(
            id=uuid7(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户"
        )
        
        permission2 = Permission(
            id=uuid7(),
            name=PermissionName("user.users.view"),
            display_name="查看用户列表",  # 不同的显示名称
            description="查看用户列表和详情"  # 不同的描述
        )
        
        permission3 = Permission(
            id=uuid7(),
            name=PermissionName("user.users.create"),
            display_name="创建用户",
            description="创建新用户"
        )

        # 相同权限名称的权限应该相等
        assert permission1 == permission2
        assert hash(permission1) == hash(permission2)
        
        # 不同权限名称的权限不相等
        assert permission1 != permission3
        assert hash(permission1) != hash(permission3)

    def test_permission_hash_consistency(self):
        """测试权限哈希一致性"""
        permission = Permission(
            id=uuid7(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户"
        )

        # 多次调用hash应该返回相同值
        hash1 = hash(permission)
        hash2 = hash(permission)
        assert hash1 == hash2

        # 可以用作字典键和集合元素
        permission_set = {permission}
        permission_dict = {permission: "test"}
        
        assert permission in permission_set
        assert permission in permission_dict