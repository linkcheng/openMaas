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

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from shared.application.response import ApiResponse
from shared.interface.auth_middleware import (
    get_current_user_id,
    require_admin,
)

from shared.infrastructure.crypto_service import get_sm2_service
from shared.interface.dependencies import get_user_application_service
from user.application.schemas import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyResponse,
    PasswordChangeCommand,
    PasswordChangeRequest,
    UserResponse,
    UserStatsResponse,
    UserSummaryResponse,
    UserUpdateCommand,
    UserUpdateRequest,
)
from user.application.services import (
    PasswordHashService,
    UserApplicationService,
)
from user.domain.models import InvalidCredentialsException

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/me", response_model=ApiResponse[UserResponse], summary="获取当前用户信息")
async def get_current_user(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """获取当前用户信息"""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        return ApiResponse.success_response(user, "获取用户信息成功")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )


@router.put("/me", response_model=ApiResponse[UserResponse], summary="更新当前用户信息")
async def update_current_user(
    request: UserUpdateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """更新当前用户信息"""
    try:
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

    except ValueError as e:
        logger.warning(f"用户信息更新数据验证失败: {e!s} - 用户ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"数据验证失败: {e!s}"
        )
    except Exception as e:
        logger.error(f"更新用户信息失败: {e!s} - 用户ID: {user_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息失败"
        )


@router.post("/me/change-password", response_model=ApiResponse[bool], summary="修改密码")
async def change_password(
    request: PasswordChangeRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """修改密码"""
    try:
        
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

    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    except Exception as e:
        logger.error(f"密码修改失败: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败"
        )


@router.get("/me/stats", response_model=ApiResponse[UserStatsResponse], summary="获取用户统计信息")
async def get_user_stats(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """获取用户统计信息"""
    try:
        stats = await user_service.get_user_stats(user_id)
        return ApiResponse.success_response(stats, "获取统计信息成功")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )


@router.post("/me/api-keys", response_model=ApiResponse[ApiKeyCreateResponse], summary="创建API密钥")
async def create_api_key(
    request: ApiKeyCreateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """创建API密钥"""
    try:
        api_key = await user_service.create_api_key(
            user_id=user_id,
            name=request.name,
            permissions=request.permissions,
            expires_at=request.expires_at,
        )

        return ApiResponse.success_response(api_key, "API密钥创建成功")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建API密钥失败"
        )


@router.get("/me/api-keys", response_model=ApiResponse[list[ApiKeyResponse]], summary="获取API密钥列表")
async def get_api_keys(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """获取API密钥列表"""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        api_keys = [
            ApiKeyResponse(
                id=key.id,
                name=key.name,
                permissions=key.permissions,
                expires_at=key.expires_at,
                last_used_at=key.last_used_at,
                is_active=key.is_active,
                created_at=key.created_at,
            )
            for key in user.api_keys
        ]

        return ApiResponse.success_response(api_keys, "获取API密钥列表成功")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取API密钥列表失败"
        )


@router.delete("/me/api-keys/{key_id}", response_model=ApiResponse[bool], summary="撤销API密钥")
async def revoke_api_key(
    key_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """撤销API密钥"""
    try:
        success = await user_service.revoke_api_key(user_id, key_id)
        return ApiResponse.success_response(success, "API密钥撤销成功")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="撤销API密钥失败"
        )


# 管理员API
@router.get("/", response_model=ApiResponse[list[UserSummaryResponse]], summary="搜索用户")
async def search_users(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    keyword: str = Query(None, description="搜索关键词"),
    status: str = Query(None, description="用户状态"),
    organization: str = Query(None, description="组织"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    _: bool = Depends(require_admin),
):
    """搜索用户（管理员）"""
    try:
        from user.application.schemas import UserSearchQuery

        query = UserSearchQuery(
            keyword=keyword,
            status=status,
            organization=organization,
            limit=limit,
            offset=(page - 1) * limit,
        )

        users = await user_service.search_users(query)
        return ApiResponse.success_response(users, "搜索用户成功")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索用户失败"
        )


@router.get("/{user_id}", response_model=ApiResponse[UserResponse], summary="获取用户详情")
async def get_user_by_id(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
    _: bool = Depends(require_admin),
):
    """获取用户详情（管理员）"""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        return ApiResponse.success_response(user, "获取用户详情成功")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户详情失败"
        )


@router.post("/{user_id}/suspend", response_model=ApiResponse[bool], summary="暂停用户")
async def suspend_user(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
    reason: str = Query(..., description="暂停原因"),
    _: bool = Depends(require_admin),
):
    """暂停用户（管理员）"""
    try:
        success = await user_service.suspend_user(user_id, reason)
        return ApiResponse.success_response(success, "用户已暂停")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="暂停用户失败"
        )


@router.post("/{user_id}/activate", response_model=ApiResponse[bool], summary="激活用户")
async def activate_user(
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    user_id: UUID,
    _: bool = Depends(require_admin),
):
    """激活用户（管理员）"""
    try:
        success = await user_service.activate_user(user_id)
        return ApiResponse.success_response(success, "用户已激活")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="激活用户失败"
        )
