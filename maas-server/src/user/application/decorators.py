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

"""用户应用层 - 审计装饰器"""

import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar
from uuid import UUID

from fastapi import Request
from loguru import logger
from uuid_extensions import uuid7

from shared.infrastructure.database import async_session_factory
from user.infrastructure.models import AuditLogORM

F = TypeVar("F", bound=Callable[..., Any])


def audit_log(
    action: str,
    description: str,
    **kwargs
) -> Callable[[F], F]:
    """
    简化的审计日志装饰器
    
    Args:
        action: 操作类型
        description: 操作描述
        extract_user_from_result: 是否从返回结果中提取用户信息
    """

    def decorator(func: F) -> F:

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 提取审计上下文
            context = _extract_context(func, args, kwargs)

            try:
                # 执行原函数
                result = await func(*args, **kwargs)

                context = _extract_context(func, args, kwargs)

                # 记录成功的审计日志
                await _log_audit_action(
                    action=action,
                    description=description,
                    user_id=context.get("user_id"),
                    username=context.get("username"),
                    ip_address=context.get("ip_address"),
                    user_agent=context.get("user_agent"),
                    success=True,
                )

                return result

            except Exception as e:
                # 记录失败的审计日志
                await _log_audit_action(
                    action=action,
                    description=f"{description} - 操作失败",
                    user_id=context.get("user_id"),
                    username=context.get("username"),
                    ip_address=context.get("ip_address"),
                    user_agent=context.get("user_agent"),
                    success=False,
                    error_message=str(e),
                )

                # 重新抛出异常
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数的包装器（简化处理）
            logger.warning(f"同步函数 {func.__name__} 使用审计装饰器，建议使用异步版本")
            return func(*args, **kwargs)

        # 根据函数类型选择包装器
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _extract_context(func: Callable, args: tuple, kwargs: dict) -> dict[str, Any]:
    """从函数参数中提取审计上下文"""
    context = {}

    # 获取函数签名
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    # 查找Request对象
    request_obj = None
    for param_name, param_value in bound_args.arguments.items():
        if isinstance(param_value, Request):
            request_obj = param_value
            break

    if request_obj:
        # 优先使用RequestContextMiddleware设置的客户端信息
        context["ip_address"] = getattr(request_obj.state, "client_ip", None)
        context["user_agent"] = getattr(request_obj.state, "user_agent", None)

        # 从 request.state 获取用户信息（已认证接口）
        context["user_id"] = getattr(request_obj.state, "user_id", None)
        context["username"] = getattr(request_obj.state, "username", None)

        # 如果state中没有用户信息，尝试从current_user获取
        current_user = getattr(request_obj.state, "current_user", None)
        if current_user and not context["user_id"]:
            context["user_id"] = getattr(current_user, "id", None)
            context["username"] = getattr(current_user, "username", None)

    return context


async def _log_audit_action(
    action: str,
    description: str,
    user_id: UUID | None = None,
    username: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    success: bool = True,
    error_message: str | None = None,
) -> None:
    """记录审计日志到数据库"""
    try:
        async with async_session_factory() as session:
            # 直接创建 ORM 对象并保存
            audit_log_orm = AuditLogORM(
                log_id=uuid7(),
                user_id=user_id,
                username=username,
                action=action,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message,
            )

            session.add(audit_log_orm)
            await session.commit()

            # 记录到应用日志
            if success:
                logger.info(f"审计日志: 用户 {username or 'system'} 执行 {action} - {description}")
            else:
                logger.warning(f"审计日志 (失败): 用户 {username or 'system'} 执行 {action} - {description} - {error_message}")

    except Exception as e:
        logger.error(f"记录审计日志失败: {e}", exc_info=True)
        # 审计日志失败不应该影响主业务流程
        pass


# 便捷的预定义装饰器
def audit_login(description: str = "用户登录"):
    """用户登录审计装饰器"""
    return audit_log("LOGIN", description)


def audit_logout(description: str = "用户登出"):
    """用户登出审计装饰器"""
    return audit_log("LOGOUT", description)


def audit_user_create(description: str = "创建用户"):
    """用户创建审计装饰器"""
    return audit_log("USER_CREATE", description)


def audit_admin_operation(description: str = "管理员操作"):
    """管理员操作审计装饰器"""
    return audit_log("ADMIN_OPERATION", description)

def audit_user_operation(description: str = "用户操作"):
    """用户操作审计装饰器"""
    return audit_log("USER_OPERATION", description)
