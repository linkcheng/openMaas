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

"""用户接口层 - 用户管理控制器"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from shared.application.exceptions import (
    AuthorizationException,
    ResourceNotFoundException,
)
from shared.application.response import ApiResponse
from shared.infrastructure.crypto_service import get_sm2_service
from user.application import get_user_application_service
from user.application.decorators import audit_user_operation
from user.application.schemas import (
    PasswordChangeCommand,
    PasswordChangeRequest,
    UserCreateRequest,
    UserResponse,
    UserSearchQuery,
    UserStatsResponse,
    UserSummaryResponse,
    UserCreateCommand,
    UserUpdateCommand,
    UserUpdateRequest,
)
from user.application.user_service import (
    UserApplicationService,
)
from user.infrastructure.password_service import PasswordHashService
from user.domain.models import User
from user.infrastructure.permission import get_current_user, get_current_user_id

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/me", response_model=ApiResponse[UserResponse], summary="获取当前用户信息")
async def get_current_user(
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """获取当前用户信息"""

    user = None
    if hasattr(request.state, "current_user") and request.state.current_user is not None:
        user = request.state.current_user

    if not user:
        raise ResourceNotFoundException("用户", "当前用户")
    user_response = await user_service._to_user_response(user)
    return ApiResponse.success_response(user_response, "获取用户信息成功")


@router.put("/me", response_model=ApiResponse[UserResponse], summary="更新当前用户信息")
async def update_current_user(
    request: UserUpdateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """更新当前用户信息"""

    command = UserUpdateCommand(
        user_id=user_id,
        first_name=request.first_name,
        last_name=request.last_name,
        avatar_url=request.avatar_url,
        organization=request.organization,
        bio=request.bio,
    )

    user = await user_service.update_user_profile(command)
    return ApiResponse.success_response(user, "用户信息更新成功")


@router.post("/me/change-password", response_model=ApiResponse[bool], summary="修改密码")
@audit_user_operation("修改密码")
async def change_password(
    request: PasswordChangeRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """修改密码"""

    sm2_service = get_sm2_service()
    current_password = sm2_service.decrypt(request.current_password)
    new_password = sm2_service.decrypt(request.new_password)

    # 哈希新密码
    new_password_hash = PasswordHashService.hash_password(new_password)

    command = PasswordChangeCommand(
        user_id=user_id,
        current_password=current_password,
        new_password_hash=new_password_hash,
    )

    success = await user_service.change_password(command)
    return ApiResponse.success_response(success, "密码修改成功")


# 管理员API
@router.get("/", response_model=ApiResponse[list[UserSummaryResponse]], summary="搜索用户")
async def search_users(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    keyword: str = Query(None, description="搜索关键词"),
    status: str = Query(None, description="用户状态"),
    organization: str = Query(None, description="组织"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """搜索用户（管理员）"""

    query = UserSearchQuery(
        keyword=keyword,
        status=status,
        organization=organization,
        limit=limit,
        offset=(page - 1) * limit,
    )

    users = await user_service.search_users(query)
    return ApiResponse.success_response(users, "搜索用户成功")



@router.get("/{user_id}", response_model=ApiResponse[UserResponse], summary="获取用户详情")
async def get_user_by_id(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
):
    """获取用户详情（管理员）"""

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise ResourceNotFoundException("用户", str(user_id))

    return ApiResponse.success_response(user, "获取用户详情成功")


@router.post("/{user_id}/suspend", response_model=ApiResponse[bool], summary="暂停用户")
async def suspend_user(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
    reason: str = Query(..., description="暂停原因"),
):
    """暂停用户（管理员）"""

    success = await user_service.suspend_user(user_id, reason)
    return ApiResponse.success_response(success, "用户已暂停")


@router.post("/{user_id}/activate", response_model=ApiResponse[bool], summary="激活用户")
async def activate_user(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
):
    """激活用户（管理员）"""

    success = await user_service.activate_user(user_id)
    return ApiResponse.success_response(success, "用户已激活")


# 权限相关API
@router.get("/{user_id}/permissions", response_model=ApiResponse[dict], summary="获取用户权限")
async def get_user_permissions(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
):
    """获取用户完整权限（管理员）"""

    permissions = await user_service.get_user_permissions(user_id)
    return ApiResponse.success_response(permissions, "获取用户权限成功")


@router.get("/{user_id}/permissions/check", response_model=ApiResponse[dict], summary="检查用户权限")
async def check_user_permission(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
    permission: str = Query(..., description="权限名称，格式：module.resource.action"),
):
    """检查用户是否拥有指定权限（管理员）"""

    result = await user_service.check_user_permission(user_id, permission)
    return ApiResponse.success_response(result, "权限检查完成")


@router.post("/{user_id}/roles", response_model=ApiResponse[UserResponse], summary="分配用户角色")
async def assign_user_roles(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
    role_ids: list[UUID],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """为用户分配角色（管理员）"""

    # 防止用户修改自己的角色
    if user_id == current_user_id:
        raise AuthorizationException("不能修改自己的角色")

    user = await user_service.assign_user_roles(user_id, role_ids)
    return ApiResponse.success_response(user, "用户角色分配成功")


@router.post("/", response_model=ApiResponse[UserResponse], summary="创建用户（管理员）")
async def create_user(
    req: UserCreateRequest,
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """创建用户（管理员）"""

    sm2 = get_sm2_service()
    raw_password = sm2.decrypt(req.password)
    password_hash = PasswordHashService.hash_password(raw_password)

    command = UserCreateCommand(
        username=req.username,
        email=str(req.email),
        password_hash=password_hash,
        first_name=req.first_name,
        last_name=req.last_name,
        organization=req.organization,
        roletype=req.role_type,
    )

    user = await user_service.create_user(command)
    return ApiResponse.success_response(user, "用户创建成功")

