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

from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.transaction_manager import transactional

from user.application.schemas import (
    RoleCreateRequest,
    RoleResponse,
    RoleSearchQuery,
    RoleUpdateRequest,
    UserRoleAssignRequest,
)
from user.domain.repositories import IRoleRepository, IPermissionRepository, IUserRepository
from shared.domain.base import DomainException
from user.domain.services.role_domain_service import RoleDomainService


class RoleApplicationService:
    """角色应用服务 - 负责编排和事务管理"""

    def __init__(
        self,
        role_domain_service: RoleDomainService,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository,
        user_repository: IUserRepository,
    ):
        self._role_domain_service = role_domain_service
        self._role_repository = role_repository
        self._permission_repository = permission_repository
        self._user_repository = user_repository

    @transactional()
    async def create_role(
        self, 
        request: RoleCreateRequest,
        session: AsyncSession
    ) -> RoleResponse:
        """创建角色 - 事务操作"""
        # 1. 使用Domain Service验证数据格式
        self._role_domain_service.validate_role_creation_data(request.name, request.description)
        
        # 2. Application Service检查角色名称唯一性
        existing_role = await self._role_repository.find_by_name(request.name)
        self._role_domain_service.validate_role_name_uniqueness(existing_role, request.name)
        
        # 3. Application Service查询权限列表
        permissions = await self._permission_repository.find_by_ids(request.permission_ids)
        
        # 4. 使用Domain Service创建角色实体
        role = self._role_domain_service.create_role_entity(
            name=request.name,
            description=request.description,
            permissions=permissions
        )
        
        # 5. Application Service保存角色
        saved_role = await self._role_repository.save(role)
        # 事务在装饰器中自动提交
        return self._to_role_response(saved_role)

    @transactional()
    async def update_role(
        self, 
        role_id: UUID, 
        request: RoleUpdateRequest,
        session: AsyncSession
    ) -> RoleResponse:
        """更新角色 - 事务操作"""
        # 1. Application Service查询角色
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise DomainException(f"角色 {role_id} 不存在")
        
        # 2. 如果更新名称，检查唯一性
        if request.name is not None:
            existing_role = await self._role_repository.find_by_name(request.name)
            self._role_domain_service.validate_role_name_update_uniqueness(
                existing_role, request.name, role_id
            )

        # 3. 使用Domain Service更新角色基本信息
        updated_role = self._role_domain_service.update_role_entity(
            role=role,
            name=request.name,
            description=request.description
        )

        # 4. 更新权限（如果提供了权限列表）
        if request.permission_ids is not None:
            # 4.1 Domain Service验证权限更新规则
            self._role_domain_service.validate_role_permission_update_rules(updated_role)
            
            # 4.2 Application Service查询权限
            new_permissions = await self._permission_repository.find_by_ids(request.permission_ids)
            
            # 4.3 Domain Service更新权限
            updated_role = self._role_domain_service.update_role_permissions_entity(
                updated_role, new_permissions
            )
            
            # 4.4 使相关用户token失效
            users_with_role = await self._user_repository.find_by_role_id(role_id)
            updated_users = self._role_domain_service.invalidate_users_tokens_for_role_change(
                users_with_role
            )
            # 保存更新后的用户
            await self._user_repository.batch_save(updated_users)
        
        # 5. Application Service保存角色
        saved_role = await self._role_repository.save(updated_role)
        # 事务在装饰器中自动提交
        return self._to_role_response(saved_role)

    @transactional()
    async def delete_role(
        self, 
        role_id: UUID,
        session: AsyncSession
    ) -> bool:
        """删除角色（带安全检查） - 事务操作"""
        # 1. Application Service查询角色
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise DomainException(f"角色 {role_id} 不存在")
        
        # 2. Application Service查询使用此角色的用户
        users_with_role = await self._user_repository.find_by_role_id(role_id)
        
        # 3. 使用Domain Service验证删除规则
        self._role_domain_service.validate_role_deletion_rules(role, users_with_role)

        # 4. Application Service执行删除
        await self._role_repository.delete(role_id)
        # 事务在装饰器中自动提交
        return True

    async def get_role(
        self, 
        role_id: UUID,
    ) -> RoleResponse | None:
        """获取角色 - 只读操作"""
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            return None

        return self._to_role_response(role)

    async def search_roles(
        self, 
        query: RoleSearchQuery,
    ) -> list[RoleResponse]:
        """搜索角色 - 只读操作"""
        roles = await self._role_repository.search_roles(
            name=query.name,
            limit=query.limit,
            offset=query.offset,
        )

        return [self._to_role_response(role) for role in roles]

    @transactional()
    async def update_role_permissions(
        self, 
        role_id: UUID, 
        permission_ids: list[UUID],
        session: AsyncSession
    ) -> RoleResponse:
        """批量更新角色权限 - 事务操作"""
        # 1. Application Service查询角色
        role = await self._role_repository.find_by_id(role_id)
        if not role:
            raise DomainException(f"角色 {role_id} 不存在")
        
        # 2. Domain Service验证权限更新规则
        self._role_domain_service.validate_role_permission_update_rules(role)
        
        # 3. Application Service查询权限
        new_permissions = []
        for permission_id in permission_ids:
            permission = await self._permission_repository.find_by_id(permission_id)
            if permission:
                new_permissions.append(permission)
        
        # 4. Domain Service更新权限
        updated_role = self._role_domain_service.update_role_permissions_entity(
            role, new_permissions
        )
        
        # 5. 使相关用户token失效
        users_with_role = await self._user_repository.find_by_role_id(role_id)
        updated_users = self._role_domain_service.invalidate_users_tokens_for_role_change(
            users_with_role
        )
        # 保存更新后的用户
        await self._user_repository.batch_save(updated_users)
        
        # 6. Application Service保存角色
        saved_role = await self._role_repository.save(updated_role)
        # 事务在装饰器中自动提交
        return self._to_role_response(saved_role)

    @transactional()
    async def assign_user_roles(
        self, 
        request: UserRoleAssignRequest,
        session: AsyncSession
    ) -> bool:
        """为用户分配角色 - 事务操作"""
        # 1. Application Service查询用户
        user = await self._user_repository.find_by_id(request.user_id)
        if not user:
            raise DomainException(f"用户 {request.user_id} 不存在")
        
        # 2. Application Service查询角色列表
        new_roles = []
        for role_id in request.role_ids:
            role = await self._role_repository.find_by_id(role_id)
            if not role:
                raise DomainException(f"角色 {role_id} 不存在")
            new_roles.append(role)
        
        # 3. 使用Domain Service处理角色分配
        self._role_domain_service.assign_user_roles_entity(user, new_roles)
        
        # 4. Application Service保存用户
        await self._user_repository.save(user)
        # 事务在装饰器中自动提交
        return True

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
