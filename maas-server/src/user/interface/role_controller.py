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

"""角色管理控制器"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger

from shared.application.response import ApiResponse
from shared.interface.auth_middleware import (
    require_super_admin,
    require_any_admin_role,
    get_current_user_id,
)
from shared.interface.dependencies import get_role_application_service
from audit.shared.decorators import audit_resource_operation, audit_user_operation
from audit.domain.models import ActionType, ResourceType
from user.application.role_service import RoleApplicationService
from user.application.schemas import (
    PermissionRequest,
    PermissionResponse,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    RoleSearchQuery,
    UserRoleAssignRequest,
)

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("/permissions", response_model=dict, dependencies=[Depends(require_super_admin)])
@audit_resource_operation(
    action=ActionType.PERMISSION_CREATE,
    resource_type=ResourceType.ROLE,
    description_template="创建权限"
)
async def create_permission(
    request: PermissionRequest,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """创建权限（仅超级管理员）"""

    permission = await role_service.create_permission(request)
    logger.info(f"权限创建成功: {permission.name}")
    return ApiResponse.success_response(data=permission, message="权限创建成功")


@router.get("/permissions", response_model=dict, dependencies=[Depends(require_any_admin_role)])
async def get_all_permissions(
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """获取所有权限"""

    permissions = await role_service.get_all_permissions()
    return ApiResponse.success_response(data=permissions, message="获取权限列表成功")


@router.post("", response_model=dict, dependencies=[Depends(require_super_admin)])
@audit_resource_operation(
    action=ActionType.ROLE_CREATE,
    resource_type=ResourceType.ROLE,
    description_template="创建角色"
)
async def create_role(
    request: RoleCreateRequest,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """创建角色（仅超级管理员）"""

    role = await role_service.create_role(request)
    logger.info(f"角色创建成功: {role.name}")
    return ApiResponse.success_response(data=role, message="角色创建成功")


@router.get("", response_model=dict, dependencies=[Depends(require_any_admin_role)])
async def search_roles(
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
    name: str | None = Query(None, description="角色名称关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
):
    """搜索角色"""

    query = RoleSearchQuery(name=name, limit=limit, offset=offset)
    roles = await role_service.search_roles(query)
    return ApiResponse.success_response(data=roles, message="获取角色列表成功")


@router.get("/{role_id}", response_model=dict, dependencies=[Depends(require_any_admin_role)])
async def get_role(
    role_id: UUID,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """获取角色详情"""

    role = await role_service.get_role(role_id)
    if not role:
        return ApiResponse.error_response(message="角色不存在", status_code=status.HTTP_404_NOT_FOUND)
    return ApiResponse.success_response(data=role, message="获取角色详情成功")


@router.put("/{role_id}", response_model=dict, dependencies=[Depends(require_super_admin)])
@audit_resource_operation(
    action=ActionType.ROLE_UPDATE,
    resource_type=ResourceType.ROLE,
    description_template="更新角色"
)
async def update_role(
    role_id: UUID,
    request: RoleUpdateRequest,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """更新角色（仅超级管理员）"""

    role = await role_service.update_role(role_id, request)
    logger.info(f"角色更新成功: {role.name}")
    return ApiResponse.success_response(data=role, message="角色更新成功")


@router.delete("/{role_id}", response_model=dict, dependencies=[Depends(require_super_admin)])
@audit_resource_operation(
    action=ActionType.ROLE_DELETE,
    resource_type=ResourceType.ROLE,
    description_template="删除角色"
)
async def delete_role(
    role_id: UUID,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """删除角色（仅超级管理员）"""

    success = await role_service.delete_role(role_id)
    if success:
        logger.info(f"角色删除成功: {role_id}")
        return ApiResponse.success_response(message="角色删除成功")

    return ApiResponse.error_response(message="角色删除失败")



@router.post("/users/assign", response_model=dict, dependencies=[Depends(require_super_admin)])
@audit_user_operation(
    action=ActionType.ROLE_ASSIGN,
    description="为用户分配角色",
    extract_target_user=True
)
async def assign_user_roles(
    request: UserRoleAssignRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """为用户分配角色（仅超级管理员）"""

    # 防止用户修改自己的角色
    if request.user_id == current_user_id:
        return ApiResponse.error_response(
            message="不能修改自己的角色",
            status_code=status.HTTP_403_FORBIDDEN
        )

    success = await role_service.assign_user_roles(request)
    if success:
        logger.info(f"用户角色分配成功: user_id={request.user_id}")
        return ApiResponse.success_response(message="用户角色分配成功")
    
    return ApiResponse.error_response(message="用户角色分配失败")
