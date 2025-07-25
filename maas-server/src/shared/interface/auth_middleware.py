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

"""共享接口层 - 认证中间件"""

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
from shared.interface.dependencies import get_user_repository
from audit.application.services import log_user_action
from audit.domain.models import ActionType, AuditResult


class JWTBearer(HTTPBearer):
    """JWT Bearer认证"""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无效的认证方案"
                )
            # 基本的JWT格式验证，不进行key_version检查（在具体的依赖中处理）
            if not self.verify_jwt_format(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无效或过期的令牌"
                )
            return credentials
        return None

    def verify_jwt_format(self, token: str) -> bool:
        """验证JWT令牌格式（不验证key_version）"""
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


class AuthService:
    """认证服务"""

    @staticmethod
    async def decode_token_with_version_check(token: str, user_repository) -> dict[str, Any]:
        """解码JWT令牌并验证key_version"""
        try:
            payload = jwt.decode(
                token,
                settings.get_jwt_secret_key(),
                algorithms=[settings.security.jwt_algorithm]
            )

            # 如果是访问令牌，需要验证key_version
            if payload.get("type") == "access":
                user_id = UUID(payload.get("sub"))
                token_key_version = payload.get("key_version")

                if token_key_version is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="令牌缺少版本信息"
                    )

                # 从数据库获取用户当前的key_version
                user = await user_repository.find_by_id(user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="用户不存在"
                    )

                # 验证key_version是否匹配
                if user.key_version != token_key_version:
                    raise to_http_exception(TokenVersionMismatchException())

            return payload
        except jwt.ExpiredSignatureError:
            raise to_http_exception(TokenRefreshRequiredException())
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效令牌"
            )

    @staticmethod
    def decode_token_basic(token: str) -> dict[str, Any]:
        """基础JWT令牌解码（不验证key_version）"""
        try:
            payload = jwt.decode(
                token,
                settings.get_jwt_secret_key(),
                algorithms=[settings.security.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效令牌"
            )

    @staticmethod
    def get_user_id_from_token(token: str) -> UUID:
        """从令牌获取用户ID"""
        payload = AuthService.decode_token_basic(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌中缺少用户信息"
            )
        try:
            return UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户ID"
            )

    @staticmethod
    def get_permissions_from_token(token: str) -> list[str]:
        """从令牌获取权限列表"""
        payload = AuthService.decode_token_basic(token)
        return payload.get("permissions", [])


# JWT认证依赖
jwt_bearer = JWTBearer()


async def get_current_user_id(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
    user_repository: Annotated[object, Depends(get_user_repository)]
) -> UUID:
    """获取当前用户ID并缓存用户对象"""
    payload = await AuthService.decode_token_with_version_check(credentials.credentials, user_repository)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中缺少用户信息"
        )
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户ID"
        )

    # 将用户ID存储到request.state中，供审计装饰器使用
    request.state.user_id = user_id

    # 获取并缓存完整的用户对象（在token验证过程中已经查询过用户，避免重复查询）
    # 检查是否已经有缓存的用户对象
    if not hasattr(request.state, "current_user") or request.state.current_user is None:
        try:
            user = await user_repository.find_by_id(user_id)
            if user:
                request.state.current_user = user
                request.state.username = user.username
                # 缓存用户权限以避免重复计算
                permissions = []
                for role in user.roles:
                    for perm in role.permissions:
                        permissions.append(f"{perm.resource}:{perm.action}")
                request.state.user_permissions = permissions
            else:
                request.state.current_user = None
                request.state.username = None
                request.state.user_permissions = []
        except Exception:
            # 如果获取用户失败，不影响认证流程
            request.state.current_user = None
            request.state.username = None
            request.state.user_permissions = []

    return user_id


async def get_current_user_permissions(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
    user_repository: Annotated[object, Depends(get_user_repository)]
) -> list[str]:
    """获取当前用户权限"""
    # 如果已经缓存了权限，直接返回
    if hasattr(request.state, "user_permissions") and request.state.user_permissions is not None:
        return request.state.user_permissions

    # 否则从token中获取权限
    payload = await AuthService.decode_token_with_version_check(credentials.credentials, user_repository)
    token_permissions = payload.get("permissions", [])

    # 缓存权限信息
    request.state.user_permissions = token_permissions

    return token_permissions


async def get_current_user(
    request: Request,
    user_id: Annotated[UUID, Depends(get_current_user_id)]
):
    """获取当前用户对象（从缓存中）"""
    # 如果已经缓存了用户对象，直接返回
    if hasattr(request.state, "current_user") and request.state.current_user is not None:
        return request.state.current_user

    # 如果没有缓存，返回None（这种情况一般不会发生，因为get_current_user_id已经缓存了）
    return None


async def get_optional_user_id(
    request: Request
) -> UUID | None:
    """获取可选的用户ID（不强制认证）"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        return AuthService.get_user_id_from_token(token)
    except HTTPException:
        return None


class PermissionChecker:
    """权限检查器"""

    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(self, permissions: Annotated[list[str], Depends(get_current_user_permissions)]):
        """检查权限"""
        required_permission = f"{self.resource}:{self.action}"

        # 检查具体权限
        if required_permission in permissions:
            return True

        # 检查通配符权限
        wildcard_resource = f"{self.resource}:*"
        if wildcard_resource in permissions:
            return True

        # 检查全局权限
        if "*:*" in permissions:
            return True

        # 权限检查失败，记录审计日志
        try:
            # 这里需要从request中获取用户信息，但由于装饰器限制，暂时简化处理
            logger.warning(f"权限检查失败: 用户缺少权限 {required_permission}")
        except Exception as e:
            logger.error(f"记录权限检查失败审计日志时出错: {e}")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"缺少权限: {required_permission}"
        )


def require_permission(resource: str, action: str):
    """权限装饰器"""
    return Depends(PermissionChecker(resource, action))


def require_permission_strict(resource: str, action: str):
    """严格权限检查装饰器 - 实时验证数据库权限"""
    async def check_permission_strict(
        user_id: Annotated[UUID, Depends(get_current_user_id)],
        user_repository: Annotated[object, Depends(get_user_repository)]
    ):
        """严格权限检查 - 从数据库实时获取权限"""
        required_permission = f"{resource}:{action}"

        try:
            user = await user_repository.find_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在"
                )

            # 检查用户是否活跃
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户账户已被禁用"
                )

            # 检查具体权限
            if user.has_permission(resource, action):
                return True

            # 检查角色级别的权限
            for role in user.roles:
                if role.has_permission(resource, action):
                    return True

            # 检查是否是超级管理员
            admin_roles = ["admin", "super_admin", "system_admin"]
            for role in user.roles:
                if role.name.lower() in admin_roles:
                    return True

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"权限验证失败: {e!s}"
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"缺少权限: {required_permission}"
        )

    return Depends(check_permission_strict)


class RoleChecker:
    """角色检查器"""

    def __init__(self, required_roles: list[str], require_all: bool = False):
        """
        初始化角色检查器
        
        Args:
            required_roles: 必需的角色列表
            require_all: 是否需要拥有所有角色（True：AND逻辑，False：OR逻辑）
        """
        self.required_roles = [role.lower() for role in required_roles]
        self.require_all = require_all

    async def __call__(
        self,
        user_id: Annotated[UUID, Depends(get_current_user_id)],
        user_repository: Annotated[object, Depends(get_user_repository)]
    ) -> bool:
        """检查用户是否具有所需角色"""
        try:
            user = await user_repository.find_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在"
                )

            # 检查用户是否活跃
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户账户已被禁用"
                )

            # 获取用户角色名称
            user_roles = [role.name.lower() for role in user.roles]

            # AND逻辑：用户必须拥有所有所需角色
            if self.require_all:
                if all(required_role in user_roles for required_role in self.required_roles):
                    return True
            # OR逻辑：用户只需拥有其中一个角色
            else:
                if any(required_role in user_roles for required_role in self.required_roles):
                    return True

            # 检查是否为超级管理员（拥有所有权限）
            super_admin_roles = ["super_admin", "system_admin"]
            if any(role in user_roles for role in super_admin_roles):
                return True

            # 如果没有匹配的角色，抛出权限不足异常
            role_names = ", ".join(self.required_roles)
            logic_type = "全部" if self.require_all else "任一"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要{logic_type}角色: {role_names}"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"角色验证失败: {e!s}"
            )


class AuthorizationService:
    """权限授权服务"""

    @staticmethod
    async def check_permissions(
        user_id: UUID,
        user_repository,
        required_permissions: list[str],
        require_all: bool = True
    ) -> bool:
        """
        检查用户权限
        
        Args:
            user_id: 用户ID
            user_repository: 用户仓储
            required_permissions: 必需权限列表 (格式: "resource:action")
            require_all: 是否需要所有权限 (True: AND逻辑, False: OR逻辑)
        """
        user = await user_repository.find_by_id(user_id)
        if not user or not user.is_active:
            return False

        user_permissions = []
        for role in user.roles:
            for perm in role.permissions:
                user_permissions.append(f"{perm.resource}:{perm.action}")

        if require_all:
            return all(
                AuthorizationService._has_permission(user_permissions, perm)
                for perm in required_permissions
            )
        else:
            return any(
                AuthorizationService._has_permission(user_permissions, perm)
                for perm in required_permissions
            )

    @staticmethod
    async def check_roles(
        user_id: UUID,
        user_repository,
        required_roles: list[str],
        require_all: bool = False
    ) -> bool:
        """
        检查用户角色
        
        Args:
            user_id: 用户ID
            user_repository: 用户仓储
            required_roles: 必需角色列表
            require_all: 是否需要所有角色 (True: AND逻辑, False: OR逻辑)
        """
        user = await user_repository.find_by_id(user_id)
        if not user or not user.is_active:
            return False

        user_roles = [role.name.lower() for role in user.roles]
        normalized_required_roles = [role.lower() for role in required_roles]

        # 检查超级管理员权限
        super_admin_roles = ["super_admin", "system_admin"]
        if any(role in user_roles for role in super_admin_roles):
            return True

        if require_all:
            return all(role in user_roles for role in normalized_required_roles)
        else:
            return any(role in user_roles for role in normalized_required_roles)

    @staticmethod
    def _has_permission(user_permissions: list[str], required_permission: str) -> bool:
        """检查是否有特定权限（支持通配符）"""
        if required_permission in user_permissions:
            return True

        # 解析权限
        try:
            resource, action = required_permission.split(":")
        except ValueError:
            return False

        # 检查通配符权限
        wildcard_resource = f"{resource}:*"
        if wildcard_resource in user_permissions:
            return True

        # 检查全局权限
        if "*:*" in user_permissions:
            return True

        return False

    @staticmethod
    async def is_admin(user_id: UUID, user_repository) -> bool:
        """检查是否为管理员"""
        return await AuthorizationService.check_roles(
            user_id, user_repository, ["admin", "super_admin", "system_admin"]
        )

    @staticmethod
    async def is_super_admin(user_id: UUID, user_repository) -> bool:
        """检查是否为超级管理员"""
        return await AuthorizationService.check_roles(
            user_id, user_repository, ["super_admin", "system_admin"]
        )


def require_roles(roles: list[str], require_all: bool = False):
    """
    角色装饰器
    
    Args:
        roles: 所需角色列表
        require_all: 是否需要拥有所有角色（True：AND逻辑，False：OR逻辑）
    """
    return Depends(RoleChecker(roles, require_all))


def require_role(role: str):
    """单个角色装饰器"""
    return require_roles([role])


def require_any_admin_role():
    """需要任一管理员角色"""
    return require_roles(["admin", "super_admin", "system_admin"])


def require_developer_or_admin():
    """需要开发者或管理员角色"""
    return require_roles(["developer", "admin", "super_admin", "system_admin"])


class AdvancedPermissionChecker:
    """高级权限检查器 - 支持角色和权限的复合条件"""

    def __init__(
        self,
        required_roles: list[str] | None = None,
        required_permissions: list[str] | None = None,
        role_logic: str = "OR",  # "AND" 或 "OR"
        permission_logic: str = "AND",  # "AND" 或 "OR"
        condition_logic: str = "OR"  # 角色和权限之间的逻辑："AND" 或 "OR"
    ):
        """
        初始化高级权限检查器
        
        Args:
            required_roles: 必需角色列表
            required_permissions: 必需权限列表
            role_logic: 角色之间的逻辑关系
            permission_logic: 权限之间的逻辑关系
            condition_logic: 角色条件和权限条件之间的逻辑关系
        """
        self.required_roles = required_roles or []
        self.required_permissions = required_permissions or []
        self.role_logic = role_logic.upper()
        self.permission_logic = permission_logic.upper()
        self.condition_logic = condition_logic.upper()

    async def __call__(
        self,
        user_id: Annotated[UUID, Depends(get_current_user_id)],
        user_repository: Annotated[object, Depends(get_user_repository)]
    ) -> bool:
        """执行复合权限检查"""
        try:
            role_check_passed = True
            permission_check_passed = True

            # 角色检查
            if self.required_roles:
                role_check_passed = await AuthorizationService.check_roles(
                    user_id,
                    user_repository,
                    self.required_roles,
                    require_all=(self.role_logic == "AND")
                )

            # 权限检查
            if self.required_permissions:
                permission_check_passed = await AuthorizationService.check_permissions(
                    user_id,
                    user_repository,
                    self.required_permissions,
                    require_all=(self.permission_logic == "AND")
                )

            # 应用条件逻辑
            if self.condition_logic == "AND":
                result = role_check_passed and permission_check_passed
            else:  # OR
                result = role_check_passed or permission_check_passed

            if not result:
                # 构建错误消息
                error_parts = []
                if self.required_roles:
                    role_logic_str = "全部" if self.role_logic == "AND" else "任一"
                    error_parts.append(f"{role_logic_str}角色: {', '.join(self.required_roles)}")
                if self.required_permissions:
                    perm_logic_str = "全部" if self.permission_logic == "AND" else "任一"
                    error_parts.append(f"{perm_logic_str}权限: {', '.join(self.required_permissions)}")
                
                condition_str = "且" if self.condition_logic == "AND" else "或"
                error_message = f"需要{condition_str.join(error_parts)}"
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_message
                )

            return True

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"权限验证失败: {e!s}"
            )


def require_complex_permission(
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
    role_logic: str = "OR",
    permission_logic: str = "AND",
    condition_logic: str = "OR"
):
    """复合权限装饰器"""
    return Depends(AdvancedPermissionChecker(
        required_roles=roles,
        required_permissions=permissions,
        role_logic=role_logic,
        permission_logic=permission_logic,
        condition_logic=condition_logic
    ))


async def require_admin(
    permissions: Annotated[list[str], Depends(get_current_user_permissions)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_repository: Annotated[object, Depends(get_user_repository)]
) -> bool:
    """管理员权限检查"""
    # 检查基础管理员权限
    admin_permissions = ["admin:*", "*:*"]
    has_admin_permission = any(perm in permissions for perm in admin_permissions)

    if has_admin_permission:
        return True

    # 检查角色级别的管理员权限
    try:
        user = await user_repository.find_by_id(user_id)
        if user and user.roles:
            # 检查是否有管理员角色
            admin_roles = ["admin", "super_admin", "system_admin"]
            for role in user.roles:
                if role.name.lower() in admin_roles:
                    return True
    except Exception:
        # 如果查询用户失败，继续使用权限检查
        pass

    # 如果没有管理员权限，抛出异常
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="需要管理员权限"
    )

    return True


async def require_super_admin(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_repository: Annotated[object, Depends(get_user_repository)]
) -> bool:
    """超级管理员权限检查 - 用于敏感操作"""
    try:
        user = await user_repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )

        # 检查用户是否活跃
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户账户已被禁用"
            )

        # 检查是否有超级管理员角色或者全局权限
        super_admin_roles = ["super_admin", "system_admin"]
        for role in user.roles:
            if role.name.lower() in super_admin_roles:
                return True

            # 检查是否有全局管理权限
            if role.has_permission("*", "*"):
                return True

        # 如果没有超级管理员权限，抛出异常
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"权限验证失败: {e!s}"
        )

    return True
