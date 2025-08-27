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

from fastapi import APIRouter, Depends, Query, status
from loguru import logger

from shared.application.response import ApiResponse
from user.application import get_role_application_service
from user.application.decorators import audit_admin_operation
from user.application.role_service import RoleApplicationService
from user.application.schemas import (
    RoleCreateRequest,
    RoleListData,
    RoleResponse,
    RoleSearchQuery,
    RoleUpdateRequest,
    UserRoleAssignRequest,
)
from user.infrastructure.permission import (
    get_current_user_id,
)

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("", response_model=ApiResponse[RoleResponse])
@audit_admin_operation("创建角色")
async def create_role(
    request: RoleCreateRequest,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """创建角色（仅超级管理员）"""

    role = await role_service.create_role(request)
    logger.info(f"角色创建成功: {role.name}")
    return ApiResponse.success_response(data=role, message="角色创建成功")


@router.get("", response_model=ApiResponse[RoleListData])
async def search_roles(
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
    name: str | None = Query(None, description="角色名称关键词"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """获取角色列表（支持分页和搜索）"""

    offset = (page - 1) * limit
    query = RoleSearchQuery(name=name, limit=limit, offset=offset)
    roles = await role_service.search_roles(query)

    # 构建分页响应
    response_data = RoleListData(
        roles=roles,
        pagination={
            "page": page,
            "limit": limit,
            "total": len(roles),  # 这里应该从repository获取总数，暂时使用当前页数量
            "has_more": len(roles) == limit  # 简单判断是否有更多数据
        }
    )

    return ApiResponse.success_response(data=response_data, message="获取角色列表成功")


@router.get("/{role_id}", response_model=ApiResponse[RoleResponse])
async def get_role(
    role_id: UUID,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """获取角色详情"""

    role = await role_service.get_role(role_id)
    if not role:
        return ApiResponse.error_response(message="角色不存在", status_code=status.HTTP_404_NOT_FOUND)
    return ApiResponse.success_response(data=role, message="获取角色详情成功")


@router.put("/{role_id}", response_model=ApiResponse[RoleResponse])
@audit_admin_operation("更新角色")
async def update_role(
    role_id: UUID,
    request: RoleUpdateRequest,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """更新角色（仅超级管理员）"""

    role = await role_service.update_role(role_id, request)
    logger.info(f"角色更新成功: {role.name}")
    return ApiResponse.success_response(data=role, message="角色更新成功")


@router.put("/{role_id}/permissions", response_model=ApiResponse[RoleResponse])
@audit_admin_operation("更新角色权限")
async def update_role_permissions(
    role_id: UUID,
    permission_ids: list[UUID],
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """更新角色权限（仅超级管理员）"""

    role = await role_service.update_role_permissions(role_id, permission_ids)
    logger.info(f"角色权限更新成功: {role.name}")
    return ApiResponse.success_response(data=role, message="角色权限更新成功")


@router.delete("/{role_id}", response_model=ApiResponse[None])
@audit_admin_operation("删除角色")
async def delete_role(
    role_id: UUID,
    role_service: Annotated[RoleApplicationService, Depends(get_role_application_service)],
):
    """删除角色（带安全检查）（仅超级管理员）"""

    success = await role_service.delete_role(role_id)
    if success:
        logger.info(f"角色删除成功: {role_id}")
        return ApiResponse.success_response(message="角色删除成功")

    return ApiResponse.error_response(message="角色删除失败")


@router.post("/users/assign", response_model=ApiResponse[None])
@audit_admin_operation("为用户分配角色")
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
