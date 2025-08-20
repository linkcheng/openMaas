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

"""用户接口层 - 认证控制器"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from loguru import logger

from audit.domain.models import ActionType, ResourceType
from audit.shared.decorators import audit_log, audit_user_operation
from shared.application.response import ApiResponse
from shared.infrastructure.crypto_service import get_sm2_service
from user.application import (
    get_auth_service,
    get_user_application_service,
)
from user.application.auth_service import AuthService
from user.application.schemas import (
    AuthTokenResponse,
    UserCreateCommand,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
)
from user.application.user_service import (
    PasswordHashService,
    UserApplicationService,
)
from user.infrastructure.auth_middleware import get_current_user_id, jwt_bearer

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/crypto/public-key", response_model=ApiResponse[dict], summary="获取SM2公钥")
async def get_public_key():
    """
    获取SM2公钥用于前端密码加密

    返回SM2公钥信息，前端使用此公钥加密密码后传输
    """

    sm2_service = get_sm2_service()
    key_info = sm2_service.get_key_info()

    return ApiResponse.success_response(key_info, "获取公钥成功")



@router.post("/register", response_model=ApiResponse[UserResponse], summary="用户注册")
@audit_log(
    action=ActionType.USER_CREATE,
    description="用户注册",
    resource_type=ResourceType.USER,
    extract_user_from_result=True,
    success_condition=lambda result: isinstance(result, ApiResponse) and result.success,
    custom_description=lambda request, **kwargs: f"用户 {request.username} 尝试注册"
)
async def register(
    request: UserCreateRequest,
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """
    用户注册

    - **username**: 用户名（3-50字符，字母、数字、下划线）
    - **email**: 邮箱地址
    - **password**: SM2加密后的密码
    - **first_name**: 名字
    - **last_name**: 姓氏
    - **organization**: 组织（可选）
    """
    # 解密密码
    sm2_service = get_sm2_service()
    decrypted_password = sm2_service.decrypt(request.password)

    # 哈希密码
    password_hash = PasswordHashService.hash_password(decrypted_password)

    # 创建用户命令
    command = UserCreateCommand(
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        first_name=request.first_name,
        last_name=request.last_name,
        organization=request.organization,
    )

    # 创建用户
    user = await user_service.create_user(command)

    return ApiResponse.success_response(user, "注册成功")


@router.post("/login", response_model=ApiResponse[AuthTokenResponse], summary="用户登录")
@audit_log(
    action=ActionType.LOGIN,
    description="用户登录",
    resource_type=ResourceType.USER,
    extract_user_from_result=True,
    success_condition=lambda result: isinstance(result, ApiResponse) and result.success,
    custom_description=lambda request, **kwargs: f"用户 {request.login_id} 尝试登录"
)
async def login(
    request: UserLoginRequest,
    http_request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    用户登录

    - **login_id**: 邮箱地址或用户名
    - **password**: SM2加密后的密码
    """
    # 解密密码
    sm2_service = get_sm2_service()
    decrypted_password = sm2_service.decrypt(request.password)

    # 检查解密结果
    if not decrypted_password:
        raise ValueError("密码解密后为空")

    # 创建令牌
    token_response = await auth_service.create_token_response(request.login_id, decrypted_password)

    return ApiResponse.success_response(token_response, "登录成功")


@router.post("/refresh", response_model=ApiResponse[AuthTokenResponse], summary="刷新令牌")
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    刷新访问令牌

    使用刷新令牌获取新的访问令牌
    """

    token_response = await auth_service.refresh_access_token(credentials.credentials)
    return ApiResponse.success_response(token_response, "令牌刷新成功")


@router.post("/logout", response_model=ApiResponse[bool], summary="退出登录")
@audit_user_operation(
    action=ActionType.LOGOUT,
    description="用户退出登录"
)
async def logout(
    http_request: Request,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """
    退出登录

    递增用户的key_version，使所有现有token失效
    """
    # 获取用户信息并存储到request.state中，供审计装饰器使用
    try:
        user = await user_service.get_user_by_id(user_id)
        if user:
            http_request.state.username = user.username
            http_request.state.current_user = user

            # 递增用户的key_version，使所有token失效
            await user_service.logout_user(user_id)

    except Exception as e:
        logger.warning(f"用户登出处理失败: {e}")
        http_request.state.username = None
        http_request.state.current_user = None

    return ApiResponse.success_response(True, "退出登录成功")


