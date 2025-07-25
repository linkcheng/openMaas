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

"""角色应用服务"""

from uuid import UUID
from uuid_extensions import uuid7
from loguru import logger

from shared.application.exceptions import ApplicationException
from user.application.schemas import (
    PermissionRequest,
    PermissionResponse,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    RoleSearchQuery,
    UserRoleAssignRequest,
)
from user.domain.models import Permission, Role
from user.domain.repositories import PermissionRepository, RoleRepository, UserRepository


class RoleApplicationService:
    """角色应用服务"""

    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
        user_repository: UserRepository,
    ):
        self._role_repository = role_repository
        self._permission_repository = permission_repository
        self._user_repository = user_repository

    async def create_permission(self, request: PermissionRequest) -> PermissionResponse:
        """创建权限（当前架构下权限通过角色管理）"""
        # 检查权限是否已存在
        existing = await self._permission_repository.find_by_resource_action(
            request.resource, request.action
        )
        if existing:
            raise ApplicationException(f"权限 {request.resource}:{request.action} 已存在")

        # 在当前架构下，权限需要添加到角色中
        # 这里我们返回一个虚拟的Permission对象，实际权限管理通过角色进行
        permission_id = uuid7()
        logger.info(f"权限定义创建: {request.name} ({request.resource}:{request.action})")

        return PermissionResponse(
            id=permission_id,
            name=request.name,
            description=request.description,
            resource=request.resource,
            action=request.action,
        )

    async def create_role(self, request: RoleCreateRequest) -> RoleResponse:
        """创建角色"""
        # 检查角色是否已存在
        existing_role = await self._role_repository.find_by_name(request.name)
        if existing_role:
            raise ApplicationException(f"角色 {request.name} 已存在")

        # 获取权限列表（基于ID查找）
        permissions = []
        for permission_id in request.permission_ids:
            permission = await self._permission_repository.find_by_id(permission_id)
            if not permission:
                # 如果找不到权限，我们可以允许创建空权限角色
                logger.warning(f"权限 {permission_id} 不存在，跳过")
                continue
            permissions.append(permission)

        # 创建角色
        role = Role(
            id=uuid7(),
            name=request.name,
            description=request.description,
            permissions=permissions,
        )

        saved_role = await self._role_repository.save(role)
        logger.info(f"角色创建成功: {saved_role.name}")

        return self._to_role_response(saved_role)

    async def update_role(self, role_id: UUID, request: RoleUpdateRequest) -> RoleResponse:
        """更新角色"""
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise ApplicationException(f"角色 {role_id} 不存在")

        # 更新角色信息
        if request.name is not None:
            # 检查新名称是否已被使用
            existing_role = await self._role_repository.find_by_name(request.name)
            if existing_role and existing_role.id != role_id:
                raise ApplicationException(f"角色名称 {request.name} 已被使用")
            role.name = request.name

        if request.description is not None:
            role.description = request.description

        # 更新权限
        if request.permission_ids is not None:
            # 清空现有权限
            for existing_permission in role.permissions:
                role.remove_permission(existing_permission)

            # 添加新权限
            for permission_id in request.permission_ids:
                permission = await self._permission_repository.find_by_id(permission_id)
                if not permission:
                    logger.warning(f"权限 {permission_id} 不存在，跳过")
                    continue
                role.add_permission(permission)

        saved_role = await self._role_repository.save(role)
        logger.info(f"角色更新成功: {saved_role.name}")

        return self._to_role_response(saved_role)

    async def delete_role(self, role_id: UUID) -> bool:
        """删除角色"""
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise ApplicationException(f"角色 {role_id} 不存在")

        # 检查是否有用户使用此角色
        users_with_role = await self._user_repository.find_by_role_id(role_id)
        if users_with_role:
            user_names = [user.username for user in users_with_role]
            raise ApplicationException(f"无法删除角色，以下用户正在使用: {', '.join(user_names)}")

        # 检查是否为系统默认角色
        system_roles = ["admin", "super_admin", "system_admin", "user"]
        if role.name.lower() in system_roles:
            raise ApplicationException(f"无法删除系统角色: {role.name}")

        await self._role_repository.delete(role_id)
        logger.info(f"角色删除成功: {role.name}")

        return True

    async def get_role(self, role_id: UUID) -> RoleResponse | None:
        """获取角色"""
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            return None

        return self._to_role_response(role)

    async def search_roles(self, query: RoleSearchQuery) -> list[RoleResponse]:
        """搜索角色"""
        roles = await self._role_repository.search_roles(
            name=query.name,
            limit=query.limit,
            offset=query.offset,
        )

        return [self._to_role_response(role) for role in roles]

    async def get_all_permissions(self) -> list[PermissionResponse]:
        """获取所有权限"""
        permissions = await self._permission_repository.find_all()
        return [
            PermissionResponse(
                id=perm.id,
                name=perm.name,
                description=perm.description,
                resource=perm.resource,
                action=perm.action,
            )
            for perm in permissions
        ]

    async def assign_user_roles(self, request: UserRoleAssignRequest) -> bool:
        """为用户分配角色"""
        user = await self._user_repository.find_by_id(request.user_id)
        if not user:
            raise ApplicationException(f"用户 {request.user_id} 不存在")

        # 获取角色列表
        new_roles = []
        for role_id in request.role_ids:
            role = await self._role_repository.find_by_id(role_id)
            if not role:
                raise ApplicationException(f"角色 {role_id} 不存在")
            new_roles.append(role)

        # 清空现有角色
        for existing_role in user.roles:
            user.remove_role(existing_role)

        # 添加新角色
        for new_role in new_roles:
            user.add_role(new_role)

        # 使用户token失效
        user.increment_key_version()

        await self._user_repository.save(user)
        logger.info(f"用户 {user.username} 角色分配成功")

        return True

    def _to_role_response(self, role: Role) -> RoleResponse:
        """转换为角色响应DTO"""
        permissions = []
        for perm in role.permissions:
            permissions.append(f"{perm.resource}:{perm.action}")

        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=permissions,
        )