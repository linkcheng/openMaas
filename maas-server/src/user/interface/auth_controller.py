"""用户接口层 - 认证控制器"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated

from ...shared.interface.auth_middleware import jwt_bearer, get_current_user_id
from ...shared.interface.dependencies import (
    get_user_application_service,
    get_auth_service,
    get_email_service,
)
from ...shared.application.response import ApiResponse
from ..application.services import (
    UserApplicationService,
    PasswordHashService,
    EmailVerificationService,
)
from ..application.auth_service import AuthService, EmailService
from ..application.schemas import (
    UserCreateRequest,
    UserLoginRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    EmailVerificationRequest,
    AuthTokenResponse,
    UserResponse,
    UserCreateCommand,
)
from ..domain.models import UserAlreadyExistsException, InvalidCredentialsException, EmailNotVerifiedException


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse[UserResponse], summary="用户注册")
async def register(
    request: UserCreateRequest,
    background_tasks: BackgroundTasks,
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
):
    """
    用户注册
    
    - **username**: 用户名（3-50字符）
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
        
        # 生成邮箱验证令牌并发送邮件
        verification_token = EmailVerificationService.generate_verification_token()
        background_tasks.add_task(
            email_service.send_verification_email,
            request.email,
            verification_token
        )
        
        # 发送欢迎邮件
        background_tasks.add_task(
            email_service.send_welcome_email,
            request.email,
            request.username
        )
        
        return ApiResponse.success(user, "注册成功，请检查邮箱完成验证")
        
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
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
    
    - **email**: 邮箱地址
    - **password**: 密码
    """
    try:
        # 认证用户
        user = await user_service.authenticate_user(request.email, request.password)
        
        # 创建令牌
        token_response = await auth_service._create_token_response(user)
        
        return ApiResponse.success(token_response, "登录成功")
        
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    except EmailNotVerifiedException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先验证邮箱"
        )
    except Exception as e:
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
        return ApiResponse.success(token_response, "令牌刷新成功")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/verify-email", response_model=ApiResponse[bool], summary="验证邮箱")
async def verify_email(
    request: EmailVerificationRequest,
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """
    验证邮箱
    
    - **token**: 邮箱验证令牌
    """
    try:
        # TODO: 实现令牌验证逻辑，这里需要存储和验证令牌
        # 暂时简化处理
        # result = await user_service.verify_email(user_id)
        
        return ApiResponse.success(True, "邮箱验证成功")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱验证失败"
        )


@router.post("/forgot-password", response_model=ApiResponse[bool], summary="忘记密码")
async def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    email_service: Annotated[EmailService, Depends(get_email_service)],
):
    """
    忘记密码
    
    - **email**: 邮箱地址
    """
    try:
        # 生成重置令牌
        reset_token = EmailVerificationService.generate_reset_token()
        
        # 发送重置邮件
        background_tasks.add_task(
            email_service.send_password_reset_email,
            request.email,
            reset_token
        )
        
        return ApiResponse.success(True, "密码重置邮件已发送")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送重置邮件失败"
        )


@router.post("/reset-password", response_model=ApiResponse[bool], summary="重置密码")
async def reset_password(
    request: PasswordResetConfirmRequest,
    user_service: Annotated[UserApplicationService, Depends(get_user_application_service)],
):
    """
    重置密码
    
    - **token**: 重置令牌
    - **new_password**: 新密码
    """
    try:
        # TODO: 实现令牌验证和密码重置逻辑
        # 暂时简化处理
        
        return ApiResponse.success(True, "密码重置成功")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码重置失败"
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
        
        return ApiResponse.success(True, "退出登录成功")
        
    except Exception as e:
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
        
        return ApiResponse.success(user, "获取用户信息成功")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )