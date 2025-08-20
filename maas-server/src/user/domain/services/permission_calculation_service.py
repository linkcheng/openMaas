"""
Copyright 2025 MaaS Team

权限计算领域服务

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


from shared.domain.base import DomainService
from user.domain.models import Permission, PermissionName, User


class PermissionCalculationService(DomainService):
    """权限计算领域服务
    
    负责计算用户的有效权限，处理权限继承、合并、冲突解决等复杂逻辑。
    这是权限系统的核心计算引擎。
    """

    def calculate_effective_permissions(self, user: User) -> set[Permission]:
        """计算用户有效权限
        
        Args:
            user: 用户实体
            
        Returns:
            用户的有效权限集合
        """
        if user.is_super_admin():
            return self._get_super_admin_permissions()

        effective_permissions = set()

        # 合并所有角色的权限
        for role in user.roles:
            effective_permissions.update(role.permissions)

        # 应用权限规则和过滤
        return self._apply_permission_rules(effective_permissions, user)

    def resolve_permission_hierarchy(self, permissions: set[Permission]) -> set[Permission]:
        """解析权限层次关系
        
        Args:
            permissions: 权限集合
            
        Returns:
            解析后的权限集合（移除被包含的权限）
        """
        resolved_permissions = set()
        permission_list = list(permissions)

        for i, perm in enumerate(permission_list):
            is_covered = False

            # 检查是否被其他权限覆盖
            for j, other_perm in enumerate(permission_list):
                if i != j and self._is_permission_covered_by(perm, other_perm):
                    is_covered = True
                    break

            if not is_covered:
                resolved_permissions.add(perm)

        return resolved_permissions

    def _is_permission_covered_by(self, permission: Permission, covering_permission: Permission) -> bool:
        """检查一个权限是否被另一个权限覆盖
        
        Args:
            permission: 被检查的权限
            covering_permission: 可能覆盖的权限
            
        Returns:
            是否被覆盖
        """
        # 检查模块匹配
        if covering_permission.module != "*" and covering_permission.module != permission.module:
            return False

        # 检查资源匹配
        if covering_permission.resource != "*" and covering_permission.resource != permission.resource:
            return False

        # 检查操作匹配
        if covering_permission.action == "*":
            return True

        # 检查特定的权限层次（例如admin > write > read）
        return self._check_action_hierarchy(permission.action, covering_permission.action)

    def _check_action_hierarchy(self, action: str, covering_action: str) -> bool:
        """检查操作权限层次
        
        Args:
            action: 被检查的操作
            covering_action: 可能覆盖的操作
            
        Returns:
            是否被覆盖
        """
        # 定义权限层次
        hierarchy = {
            "admin": ["create", "read", "update", "delete", "manage"],
            "manage": ["create", "read", "update", "delete"],
            "write": ["create", "update"],
            "read": []
        }

        if covering_action in hierarchy:
            return action in hierarchy[covering_action]

        return action == covering_action

    def _get_super_admin_permissions(self) -> set[Permission]:
        """获取超级管理员权限
        
        Returns:
            超级管理员权限集合
        """
        from uuid_extensions import uuid7

        wildcard_permission = Permission(
            id=uuid7(),
            name=PermissionName("*.*.*"),
            display_name="超级管理员权限",
            description="拥有系统所有权限"
        )

        return {wildcard_permission}

    def _apply_permission_rules(self, permissions: set[Permission], user: User) -> set[Permission]:
        """应用权限规则
        
        Args:
            permissions: 原始权限集合
            user: 用户实体
            
        Returns:
            应用规则后的权限集合
        """
        # 用户状态检查
        if not user.is_active:
            return set()

        # 解析权限层次
        resolved_permissions = self.resolve_permission_hierarchy(permissions)

        # 应用时间限制（如果需要）
        # filtered_permissions = self._apply_time_restrictions(resolved_permissions, user)

        return resolved_permissions

    def get_permission_matrix(self, user: User) -> dict[str, dict[str, list[str]]]:
        """获取权限矩阵
        
        Args:
            user: 用户实体
            
        Returns:
            权限矩阵 {module: {resource: [actions]}}
        """
        effective_permissions = self.calculate_effective_permissions(user)
        matrix = {}

        for permission in effective_permissions:
            module = permission.module or "default"
            resource = permission.resource
            action = permission.action

            if module not in matrix:
                matrix[module] = {}

            if resource not in matrix[module]:
                matrix[module][resource] = []

            if action not in matrix[module][resource]:
                matrix[module][resource].append(action)

        return matrix
