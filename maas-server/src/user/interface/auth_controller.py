"""用户接口层 - 认证控制器"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from loguru import logger
from pydantic import ValidationError

from shared.application.response import ApiResponse
from shared.interface.auth_middleware import get_current_user_id, jwt_bearer
from shared.interface.dependencies import (
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
from user.application.services import (
    PasswordHashService,
    UserApplicationService,
)
from user.domain.models import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse[UserResponse], summary="用户注册")
async def register(
    request: UserCreateRequest,
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """
    用户注册
    
    - **username**: 用户名（3-50字符，字母、数字、下划线）
    - **email**: 邮箱地址
    - **password**: 密码（至少8字符，包含大小写字母和数字）
    - **first_name**: 名字
    - **last_name**: 姓氏
    - **organization**: 组织（可选）
    """
    try:
        # 哈希密码
        password_hash = PasswordHashService.hash_password(request.password)

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

    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        # 处理 Pydantic 验证错误
        error_messages = []
        for error in e.errors():
            field = error.get("loc", ["unknown"])[-1]
            message = error.get("msg", "验证失败")
            error_messages.append(f"{field}: {message}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(error_messages)
        )
    except Exception as e:
        # 记录详细错误信息
        logging.error(f"用户注册失败: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=ApiResponse[AuthTokenResponse], summary="用户登录")
async def login(
    request: UserLoginRequest,
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    用户登录
    
    - **login_id**: 邮箱地址或用户名
    - **password**: 密码
    """
    try:
        # 认证用户
        user = await user_service.authenticate_user(request.login_id, request.password)
        logger.info(user)
        # 创建令牌
        token_response = await auth_service._create_token_response(user)

        return ApiResponse.success_response(token_response, "登录成功")

    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱或密码错误"
        )

    except Exception as e:
        logger.error(f"登录失败: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post("/refresh", response_model=ApiResponse[AuthTokenResponse], summary="刷新令牌")
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    刷新访问令牌
    
    使用刷新令牌获取新的访问令牌
    """
    try:
        token_response = await auth_service.refresh_access_token(credentials.credentials)
        return ApiResponse.success_response(token_response, "令牌刷新成功")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )





@router.post("/logout", response_model=ApiResponse[bool], summary="退出登录")
async def logout(
    user_id: Annotated[str, Depends(get_current_user_id)],
):
    """
    退出登录
    
    将令牌加入黑名单（可选实现）
    """
    try:
        # TODO: 可以实现令牌黑名单功能
        # 这里简化处理，客户端删除令牌即可

        return ApiResponse.success_response(True, "退出登录成功")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="退出登录失败"
        )


@router.get("/me", response_model=ApiResponse[UserResponse], summary="获取当前用户信息")
async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """
    获取当前用户信息
    """
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
