"""
Copyright 2025 MaaS Team

审计日志中间件 - 请求上下文管理

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

from typing import Any
from uuid import UUID

import jwt
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.settings import settings

from shared.infrastructure.database import async_session_factory

from user.infrastructure.repositories import UserRepository



class UserContextMiddleware(BaseHTTPMiddleware):
    """用户上下文中间件
    
    提前进行用户认证，将用户信息注入到 request.state 中，
    供后续的依赖注入和审计装饰器使用。
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 尝试从请求头获取认证信息
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, credentials = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer" and credentials:
                # 尝试进行用户认证
                user_context = await self._authenticate_user(credentials)
                if user_context:
                    # 将用户信息注入到 request.state
                    request.state.current_user = user_context["user"]
                    request.state.user_id = user_context["user_id"]
                    request.state.username = user_context["username"]
                    request.state.permissions = user_context["permissions"]
                    request.state.is_authenticated = True

                    logger.debug(f"用户上下文中间件: 用户 {user_context['username']} 认证成功")
                else:
                    # 认证失败，设置未认证状态
                    request.state.is_authenticated = False
            else:
                request.state.is_authenticated = False
        else:
            # 没有认证信息，设置未认证状态
            request.state.is_authenticated = False
            request.state.username = None
            # 避免对无请求体或非 JSON 请求（如 CORS 预检 OPTIONS）进行 JSON 解析
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                content_length = request.headers.get("content-length")
                content_type = request.headers.get("content-type", "")
                if content_length and content_type.startswith("application/json"):
                    try:
                        body = await request.json()
                        request.state.username = (body or {}).get("login_id")
                    except Exception as e:
                        logger.debug(f"Skip parsing body in middleware: {e}")

        response = await call_next(request)
        
        return response

    async def _authenticate_user(self, token: str) -> dict[str, Any] | None:
        """认证用户并返回用户上下文信息"""
        try:
            # 解析JWT token
            payload = jwt.decode(
                token,
                settings.get_jwt_secret_key(),
                algorithms=[settings.security.jwt_algorithm]
            )

            # 验证token类型
            if payload.get("type") != "access":
                return None

            user_id = UUID(payload.get("sub"))
            token_key_version = payload.get("key_version")

            if token_key_version is None:
                return None

            user = None
            async with async_session_factory() as session:
            # 获取用户仓储（动态导入避免循环依赖）
                user_repository = UserRepository(session)
                # 获取用户信息
                user = await user_repository.find_by_id(user_id)
        
            if not user:
                return None

            # 验证key_version和用户状态
            if user.key_version != token_key_version or not user.is_active:
                return None

            # 提取用户权限
            permissions = []
            for role in user.roles:
                for permission in role.permissions:
                    perm_str = f"{permission.resource}:{permission.action}"
                    if perm_str not in permissions:
                        permissions.append(perm_str)

            return {
                "user": user,
                "user_id": user.id,
                "username": user.username,
                "permissions": permissions,
            }

        except Exception as e:
            logger.error(f"用户认证失败: {e}", exc_info=True)
            return None
