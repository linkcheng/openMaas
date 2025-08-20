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

"""简化的认证中间件 - 实现最小化RBAC"""

from collections.abc import Callable
from enum import Enum
from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from config.settings import settings
from shared.application.exceptions import (
    TokenRefreshRequiredException,
    TokenVersionMismatchException,
    to_http_exception,
)
from user.application import get_user_repository
from user.domain.models import User


class JWTBearer(HTTPBearer):
    """JWT Bearer认证"""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无效的认证方案"
                )
            if not self.verify_jwt_format(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无效或过期的令牌"
                )
            return credentials
        return None

    def verify_jwt_format(self, token: str) -> bool:
        """验证JWT令牌格式"""
        try:
            payload = jwt.decode(
                token,
                settings.get_jwt_secret_key(),
                algorithms=[settings.security.jwt_algorithm]
            )
            return payload is not None
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False


jwt_bearer = JWTBearer()


async def get_current_user_with_permissions(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
    user_repository: Annotated[Any, Depends(get_user_repository)]
) -> User:
    """获取当前用户并注入权限到request.state"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.get_jwt_secret_key(),
            algorithms=[settings.security.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as e:
        raise to_http_exception(TokenRefreshRequiredException()) from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效令牌"
        ) from e

    # 验证access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请使用access token访问"
        )

    user_id = UUID(payload.get("sub"))
    token_key_version = payload.get("key_version")

    if token_key_version is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌缺少版本信息"
        )

    # 获取用户并验证key_version
    user = await user_repository.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    if user.key_version != token_key_version:
        raise to_http_exception(TokenVersionMismatchException())

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )

    # 注入用户信息到request.state
    request.state.current_user = user
    request.state.user_id = user.id
    request.state.username = user.username

    # 获取并注入用户权限
    permissions = []
    for role in user.roles:
        for permission in role.permissions:
            perm_str = f"{permission.resource}:{permission.action}"
            if perm_str not in permissions:
                permissions.append(perm_str)

    request.state.permissions = permissions

    logger.debug(f"用户认证成功: {user.username}, 权限数量: {len(permissions)}")
    return user


async def get_current_user(
    user: Annotated[User, Depends(get_current_user_with_permissions)]
) -> User:
    """获取当前用户(简化版,用于不需要权限检查的接口)"""
    return user


async def get_current_user_id(
    user: Annotated[User, Depends(get_current_user_with_permissions)]
) -> UUID:
    """获取当前用户ID"""
    return user.id


async def get_current_permissions(
    request: Request,
    _user: Annotated[User, Depends(get_current_user_with_permissions)]
) -> list[str]:
    """获取当前用户权限"""
    return getattr(request.state, "permissions", [])


class PermissionLogic(str, Enum):
    """权限验证逻辑"""
    AND = "AND"  # 需要所有权限
    OR = "OR"    # 需要任一权限


class PermissionChecker:
    """权限检查器"""

    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(
        self,
        request: Request,
        permissions: Annotated[list[str], Depends(get_current_permissions)]
    ) -> bool:
        """检查权限"""
        required_permission = f"{self.resource}:{self.action}"

        if self._has_permission(permissions, required_permission):
            return True

        # 权限检查失败
        user = getattr(request.state, "current_user", None)
        username = user.username if user else "未知用户"
        logger.warning(f"权限检查失败: 用户 {username} 缺少权限 {required_permission}")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"缺少权限: {required_permission}"
        )

    def _has_permission(self, permissions: list[str], required_permission: str) -> bool:
        """检查是否有权限"""
        # 检查具体权限
        if required_permission in permissions:
            return True

        # 检查通配符权限
        resource, action = required_permission.split(":")
        wildcard_resource = f"{resource}:*"
        if wildcard_resource in permissions:
            return True

        # 检查全局权限
        if "*:*" in permissions:
            return True

        return False


class MultiPermissionChecker:
    """多权限检查器"""

    def __init__(self, required_permissions: list[str], logic: PermissionLogic = PermissionLogic.AND):
        """
        初始化多权限检查器
        
        Args:
            required_permissions: 必需权限列表，格式为 ["resource:action", ...]
            logic: 权限验证逻辑 (AND: 需要所有权限, OR: 需要任一权限)
        """
        self.required_permissions = required_permissions
        self.logic = logic

    def __call__(
        self,
        request: Request,
        permissions: Annotated[list[str], Depends(get_current_permissions)]
    ) -> bool:
        """检查多个权限"""
        checker = PermissionChecker("", "")  # 创建辅助检查器实例

        validation_results = {}
        for perm in self.required_permissions:
            validation_results[perm] = checker._has_permission(permissions, perm)

        # 应用逻辑判断
        if self.logic == PermissionLogic.AND:
            # AND逻辑：需要所有权限
            has_all_permissions = all(validation_results.values())
            missing_permissions = [
                perm for perm, result in validation_results.items() if not result
            ]

            if not has_all_permissions:
                user = getattr(request.state, "current_user", None)
                username = user.username if user else "未知用户"
                logger.warning(
                    f"多权限检查失败(AND): 用户 {username}, "
                    f"缺少权限: {missing_permissions}"
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要所有权限: {', '.join(missing_permissions)}"
                )

        else:  # OR逻辑
            # OR逻辑：需要任一权限
            has_any_permission = any(validation_results.values())

            if not has_any_permission:
                user = getattr(request.state, "current_user", None)
                username = user.username if user else "未知用户"
                logger.warning(
                    f"多权限检查失败(OR): 用户 {username}, "
                    f"需要任一权限: {self.required_permissions}"
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要任一权限: {', '.join(self.required_permissions)}"
                )

        return True


def require_permission(resource: str, action: str) -> Callable[..., Any]:
    """单权限装饰器"""
    return Depends(PermissionChecker(resource, action))


def require_permissions(permissions: list[str], logic: PermissionLogic = PermissionLogic.AND) -> Callable[..., Any]:
    """
    多权限装饰器
    
    Args:
        permissions: 必需权限列表，格式为 ["resource:action", ...]
        logic: 权限验证逻辑 (AND: 需要所有权限, OR: 需要任一权限)
    
    Returns:
        FastAPI依赖装饰器
    
    Examples:
        # 需要所有权限 (AND逻辑)
        @require_permissions(["user:read", "user:update"])
        async def update_user_profile(): pass
        
        # 需要任一权限 (OR逻辑)  
        @require_permissions(["admin:manage", "user:admin"], logic=PermissionLogic.OR)
        async def admin_or_user_admin(): pass
    """
    return Depends(MultiPermissionChecker(permissions, logic))


def require_all_permissions(*permissions: str) -> Callable[..., Any]:
    """
    需要所有权限的装饰器 (AND逻辑的简化版本)
    
    Args:
        *permissions: 权限列表，格式为 "resource:action"
    
    Returns:
        FastAPI依赖装饰器
        
    Example:
        @require_all_permissions("user:read", "user:update", "role:read")
        async def complex_user_operation(): pass
    """
    return require_permissions(list(permissions), PermissionLogic.AND)


def require_any_permission(*permissions: str) -> Callable[..., Any]:
    """
    需要任一权限的装饰器 (OR逻辑的简化版本)
    
    Args:
        *permissions: 权限列表，格式为 "resource:action"
    
    Returns:
        FastAPI依赖装饰器
        
    Example:
        @require_any_permission("admin:manage", "user:admin")  
        async def admin_operation(): pass
    """
    return require_permissions(list(permissions), PermissionLogic.OR)


async def require_admin(
    permissions: Annotated[list[str], Depends(get_current_permissions)],
    user: Annotated[User, Depends(get_current_user)]
) -> bool:
    """管理员权限检查"""
    # 检查权限级别的管理员权限
    admin_permissions = ["admin:*", "*:*"]
    if any(perm in permissions for perm in admin_permissions):
        return True

    # 检查角色级别的管理员权限
    admin_roles = ["admin", "super_admin", "system_admin"]
    user_roles = [role.name.lower() for role in user.roles]
    if any(role in user_roles for role in admin_roles):
        return True

    logger.warning(f"管理员权限检查失败: 用户 {user.username}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="需要管理员权限"
    )


def require_admin_permission() -> Callable[..., Any]:
    """管理员权限装饰器"""
    return Depends(require_admin)
