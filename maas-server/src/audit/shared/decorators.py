"""
Copyright 2025 MaaS Team

审计日志装饰器 - AOP实现

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

import contextlib
import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar
from uuid import UUID

from fastapi import Request
from loguru import logger

# 延迟导入避免循环依赖
from audit.application.services import log_user_action
from audit.domain.models import ActionType, AuditResult, ResourceType
from audit.shared.config import is_audit_enabled_for_action
from shared.application.response import ApiResponse

F = TypeVar("F", bound=Callable[..., Any])


class AuditContext:
    """审计上下文信息"""

    def __init__(self):
        self.request: Request | None = None
        self.user_id: UUID | None = None
        self.username: str | None = None
        self.ip_address: str | None = None
        self.user_agent: str | None = None
        self.request_id: str | None = None


def audit_log(
    action: ActionType,
    description: str,
    resource_type: ResourceType | None = None,
    extract_user_from_params: bool = True,
    extract_user_from_result: bool = False,
    success_condition: Callable[[Any], bool] | None = None,
    failure_condition: Callable[[Exception], bool] | None = None,
    extract_resource_id: Callable[..., UUID | None] | None = None,
    custom_description: Callable[..., str] | None = None,
) -> Callable[[F], F]:
    """
    审计日志装饰器

    Args:
        action: 操作类型
        description: 操作描述模板
        resource_type: 资源类型
        extract_user_from_params: 是否从参数中提取用户信息
        extract_user_from_result: 是否从返回结果中提取用户信息
        success_condition: 自定义成功条件判断函数
        failure_condition: 自定义失败条件判断函数
        extract_resource_id: 资源ID提取函数
        custom_description: 自定义描述生成函数
    """

    def decorator(func: F) -> F:

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 检查是否启用审计
            if not is_audit_enabled_for_action(action):
                logger.debug(f"操作 {action.value} 的审计已禁用，跳过记录")
                return await func(*args, **kwargs)

            # 提取审计上下文
            context = _extract_context(func, args, kwargs)

            # 提取资源ID
            resource_id = None
            if extract_resource_id:
                try:
                    resource_id = extract_resource_id(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"提取资源ID失败: {e}")

            # 生成描述
            final_description = description
            if custom_description:
                try:
                    final_description = custom_description(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"生成自定义描述失败: {e}")
                    final_description = description

            try:
                # 执行原函数
                result = await func(*args, **kwargs)

                # 从结果中提取用户信息
                if extract_user_from_result and not context.user_id:
                    _extract_user_from_result(context, result)

                # 丰富用户信息（获取用户名）
                if context.user_id and not context.username:
                    await _enrich_context_with_user_info(context, args, kwargs)

                # 判断操作结果
                audit_result = AuditResult.SUCCESS
                error_message = None

                if success_condition and not success_condition(result):
                    audit_result = AuditResult.FAILURE
                    error_message = "操作未满足成功条件"

                # 记录审计日志
                await log_user_action(
                    action=action,
                    description=final_description,
                    user_id=context.user_id,
                    username=context.username,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    result=audit_result,
                    error_message=error_message,
                    ip_address=context.ip_address,
                    user_agent=context.user_agent,
                    request_id=context.request_id,
                )

                return result

            except Exception as e:
                # 判断是否为预期的失败
                is_expected_failure = False
                if failure_condition:
                    with contextlib.suppress(Exception):
                        is_expected_failure = failure_condition(e)

                # 丰富用户信息（获取用户名）
                if context.user_id and not context.username:
                    await _enrich_context_with_user_info(context, args, kwargs)

                # 记录失败的审计日志
                await log_user_action(
                    action=action,
                    description=f"{final_description} - 操作失败",
                    user_id=context.user_id,
                    username=context.username,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    result=AuditResult.FAILURE,
                    error_message=str(e),
                    ip_address=context.ip_address,
                    user_agent=context.user_agent,
                    request_id=context.request_id,
                    metadata={"expected_failure": is_expected_failure}
                )

                # 重新抛出异常
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数的包装器（当前项目主要是异步，暂时简化处理）
            logger.warning(f"同步函数 {func.__name__} 使用审计装饰器，建议使用异步版本")
            return func(*args, **kwargs)

        # 根据函数类型选择包装器
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _extract_context(func: Callable, args: tuple, kwargs: dict) -> AuditContext:
    """从函数参数中提取审计上下文"""
    context = AuditContext()

    # 获取函数签名
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    # 查找Request对象
    request_obj = None
    for param_name, param_value in bound_args.arguments.items():
        if isinstance(param_value, Request):
            request_obj = param_value
            context.request = param_value
            context.ip_address = param_value.client.host if param_value.client else None
            context.user_agent = param_value.headers.get("user-agent")
            context.request_id = getattr(param_value.state, "request_id", None)
            break

    # 首先尝试从 request.state 获取用户信息
    if request_obj:
        # 检查 request.state 中是否有用户对象
        current_user = getattr(request_obj.state, "current_user", None)
        if current_user:
            context.user_id = getattr(current_user, "id", None)
            context.username = getattr(current_user, "username", None)

        # 如果没有完整用户对象，尝试从 state 中获取用户 ID 和用户名
        if not context.user_id:
            context.user_id = getattr(request_obj.state, "user_id", None)
        if not context.username:
            context.username = getattr(request_obj.state, "username", None)

    # 查找用户信息参数（作为备选方案）
    for param_name, param_value in bound_args.arguments.items():
        if param_name in ["user_id", "current_user_id"] and isinstance(param_value, UUID):
            if not context.user_id:  # 只有在没有从 request.state 获取到时才使用
                context.user_id = param_value
        elif param_name in ["username", "current_username"] and isinstance(param_value, str):
            if not context.username:
                context.username = param_value
        elif param_name in ["user", "current_user"] and hasattr(param_value, "id"):
            if not context.user_id:
                context.user_id = param_value.id
            if not context.username:
                context.username = getattr(param_value, "username", None)

    return context


async def _enrich_context_with_user_info(context: AuditContext, args: tuple, kwargs: dict) -> None:
    """异步丰富上下文中的用户信息"""
    if context.user_id and not context.username:
        try:
            # 尝试从函数参数中找到 user_service
            user_service = None
            for param_name, param_value in kwargs.items():
                if param_name == "user_service" or (hasattr(param_value, "get_user_by_id")):
                    user_service = param_value
                    break

            if user_service:
                # 尝试获取用户信息
                user = await user_service.get_user_by_id(context.user_id)
                if user:
                    context.username = user.username
            else:
                # 如果没有找到user_service，尝试直接从数据库获取
                try:

                    # 这是一个备选方案，但可能会有性能影响
                    # 在生产环境中建议优化这个逻辑
                    pass
                except Exception:
                    pass

        except Exception as e:
            logger.warning(f"获取用户信息失败: {e}")
            # 失败时不影响主流程，只是无法获取用户名


def _extract_user_from_result(context: AuditContext, result: Any) -> None:
    """从返回结果中提取用户信息"""
    try:
        # 处理ApiResponse包装的结果
        data = result.data if isinstance(result, ApiResponse) else result

        # 尝试从不同的数据结构中提取用户信息
        if hasattr(data, "user") and hasattr(data.user, "id"):
            context.user_id = data.user.id
            context.username = getattr(data.user, "username", None)
        elif hasattr(data, "id") and hasattr(data, "username"):
            context.user_id = data.id
            context.username = data.username
        elif isinstance(data, dict):
            if "user" in data and isinstance(data["user"], dict):
                context.user_id = data["user"].get("id")
                context.username = data["user"].get("username")
            elif "id" in data and "username" in data:
                context.user_id = data.get("id")
                context.username = data.get("username")

    except Exception as e:
        logger.warning(f"从结果中提取用户信息失败: {e}")


def audit_resource_operation(
    action: ActionType,
    resource_type: ResourceType,
    description_template: str = "{action}:{resource_type}",
) -> Callable[[F], F]:
    """
    资源操作审计装饰器的便捷方法

    Args:
        action: 操作类型
        resource_type: 资源类型
        description_template: 描述模板
    """

    def extract_resource_id_from_params(*args, **kwargs) -> UUID | None:
        """从参数中提取资源ID"""
        # 查找常见的资源ID参数名
        for key in ["resource_id", "id", f"{resource_type.value}_id"]:
            if key in kwargs and isinstance(kwargs[key], UUID | str):
                try:
                    return UUID(str(kwargs[key]))
                except (ValueError, TypeError):
                    pass
        return None

    def generate_description(*args, **kwargs) -> str:
        """生成描述"""
        return description_template.format(
            action=action.value,
            resource_type=resource_type.value
        )

    return audit_log(
        action=action,
        description=generate_description(),
        resource_type=resource_type,
        extract_resource_id=extract_resource_id_from_params,
        custom_description=generate_description,
    )


def audit_user_operation(
    action: ActionType,
    description: str,
    extract_target_user: bool = False,
) -> Callable[[F], F]:
    """
    用户操作审计装饰器的便捷方法

    Args:
        action: 操作类型
        description: 操作描述
        extract_target_user: 是否提取目标用户信息（用于管理员操作其他用户的场景）
    """

    def extract_target_user_id(*args, **kwargs) -> UUID | None:
        """提取目标用户ID"""
        if not extract_target_user:
            return None

        for key in ["target_user_id", "user_id", "id"]:
            if key in kwargs and isinstance(kwargs[key], UUID | str):
                try:
                    return UUID(str(kwargs[key]))
                except (ValueError, TypeError):
                    pass
        return None

    return audit_log(
        action=action,
        description=description,
        resource_type=ResourceType.USER,
        extract_resource_id=extract_target_user_id if extract_target_user else None,
    )
