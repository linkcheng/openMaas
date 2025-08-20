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

"""角色应用服务 - 负责编排和事务管理"""

from uuid import UUID

from user.application.schemas import (
    RoleCreateRequest,
    RoleResponse,
    RoleSearchQuery,
    RoleUpdateRequest,
    UserRoleAssignRequest,
)
from user.domain.repositories import IRoleRepository
from user.domain.services.role_domain_service import RoleDomainService


class RoleApplicationService:
    """角色应用服务 - 负责编排和事务管理"""

    def __init__(
        self,
        role_repository: IRoleRepository,
        role_domain_service: RoleDomainService,
    ):
        self._role_repository = role_repository
        self._role_domain_service = role_domain_service

    async def create_role(self, request: RoleCreateRequest) -> RoleResponse:
        """创建角色"""
        # 使用 Domain Service 创建角色
        role = await self._role_domain_service.create_role_with_permissions(
            name=request.name,
            description=request.description,
            permission_ids=request.permission_ids
        )

        return self._to_role_response(role)

    async def update_role(self, role_id: UUID, request: RoleUpdateRequest) -> RoleResponse:
        """更新角色"""
        # 使用 Domain Service 更新角色基本信息
        role = await self._role_domain_service.update_role_information(
            role_id=role_id,
            name=request.name,
            description=request.description
        )

        # 更新权限（如果提供了权限列表）
        if request.permission_ids is not None:
            role = await self._role_domain_service.update_role_permissions(
                role_id=role_id,
                permission_ids=request.permission_ids
            )

        # 保存角色
        saved_role = await self._role_repository.save(role)
        return self._to_role_response(saved_role)

    async def delete_role(self, role_id: UUID) -> bool:
        """删除角色（带安全检查）"""
        # 使用 Domain Service 验证删除规则
        role = await self._role_domain_service.validate_role_deletion(role_id)

        # 执行删除
        await self._role_repository.delete(role_id)
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

    async def update_role_permissions(self, role_id: UUID, permission_ids: list[UUID]) -> RoleResponse:
        """批量更新角色权限"""
        # 使用 Domain Service 更新权限
        role = await self._role_domain_service.update_role_permissions(
            role_id=role_id,
            permission_ids=permission_ids
        )

        # 保存角色
        saved_role = await self._role_repository.save(role)
        return self._to_role_response(saved_role)

    async def assign_user_roles(self, request: UserRoleAssignRequest) -> bool:
        """为用户分配角色"""
        # 使用 Domain Service 处理角色分配
        await self._role_domain_service.assign_user_roles(
            user_id=request.user_id,
            role_ids=request.role_ids
        )

        return True

    async def validate_role_assignment(self, user_id: UUID, role_ids: list[UUID], assigner_id: UUID) -> dict:
        """验证角色分配权限"""
        # 使用 Domain Service 验证权限
        return await self._role_domain_service.validate_role_assignment_authority(
            user_id=user_id,
            role_ids=role_ids,
            assigner_id=assigner_id
        )

    async def get_role_usage_statistics(self, role_id: UUID) -> dict:
        """获取角色使用统计"""
        # 使用 Domain Service 获取统计信息
        return await self._role_domain_service.get_role_usage_statistics(role_id)

    def _to_role_response(self, role) -> RoleResponse:
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
