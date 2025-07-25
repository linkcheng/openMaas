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

from config.settings import settings
from shared.application.exceptions import (
    TokenRefreshRequiredException,
    TokenVersionMismatchException,
    to_http_exception,
)
from shared.interface.dependencies import get_user_repository


class JWTBearer(HTTPBearer):
    """JWT Bearer认证"""

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
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
    """获取当前用户ID"""
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

    return user_id


async def get_current_user_permissions(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
    user_repository: Annotated[object, Depends(get_user_repository)]
) -> list[str]:
    """获取当前用户权限"""
    payload = await AuthService.decode_token_with_version_check(credentials.credentials, user_repository)
    return payload.get("permissions", [])


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

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"缺少权限: {required_permission}"
        )


def require_permission(resource: str, action: str):
    """权限装饰器"""
    return Depends(PermissionChecker(resource, action))


class RoleChecker:
    """角色检查器"""

    def __init__(self, required_roles: list[str]):
        self.required_roles = required_roles

    async def __call__(self, user_id: Annotated[UUID, Depends(get_current_user_id)]):
        """检查角色"""
        # 这里需要从数据库获取用户角色
        # 暂时简化处理，实际需要注入用户仓储
        # TODO: 实现完整的角色检查逻辑
        return True


def require_roles(roles: list[str]):
    """角色装饰器"""
    return Depends(RoleChecker(roles))


def require_admin(
    permissions: Annotated[list[str], Depends(get_current_user_permissions)]
) -> bool:
    """管理员权限检查 - 暂时禁用权限验证"""
    # 暂时返回True，允许所有用户访问管理功能
    return True

    # 原权限检查逻辑（已注释）
    # admin_permissions = ["admin:*", "*:*"]
    # if not any(perm in permissions for perm in admin_permissions):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="需要管理员权限"
    #     )
    # return True
