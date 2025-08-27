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

from fastapi import Depends, HTTPException, Request, status
from loguru import logger

from user.domain.models import User


async def get_current_user_with_permissions(
    request: Request,
) -> User:
    """获取当前用户并注入权限到request.state
    
    优化后的版本：优先使用 UserContextMiddleware 预先认证的用户信息，
    如果没有则回退到传统的认证流程。
    """
    # 优先检查 UserContextMiddleware 是否已经认证了用户
    if (hasattr(request.state, "is_authenticated") and
            request.state.is_authenticated and
            hasattr(request.state, "current_user") and
            request.state.current_user is not None):
        user = request.state.current_user
        logger.debug(f"从中间件获取已认证用户: {getattr(user, 'username', '<unknown>')}")
        return user

    # 未认证，返回 401
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未认证的请求，请先登录",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    user: Annotated[User, Depends(get_current_user_with_permissions)]
) -> User:
    """获取当前用户(简化版,用于不需要权限检查的接口)"""
    return user


async def get_current_user_id(
    request: Request,
    user: Annotated[User, Depends(get_current_user_with_permissions)]
) -> UUID:
    """获取当前用户ID
    
    优化版本：优先从 request.state 获取，提高性能
    """
    # 优先从 request.state 获取
    if hasattr(request.state, "user_id") and request.state.user_id:
        return request.state.user_id

    # 回退到从用户对象获取（此时 user 一定存在）
    return user.id


async def get_current_permissions(
    request: Request,
    _user: Annotated[User, Depends(get_current_user_with_permissions)]
) -> list[str]:
    """获取当前用户权限
    
    优化版本：优先从 request.state 获取，提高性能
    """
    # 优先从 request.state 获取
    if hasattr(request.state, "permissions") and request.state.permissions:
        return request.state.permissions

    # 回退到空权限列表
    return []


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
    admin_roles = ["admin",]
    user_roles = [role.name.lower() for role in user._roles]
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
