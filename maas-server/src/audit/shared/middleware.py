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

import time
import uuid

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# 延迟导入避免循环依赖
from audit.domain.models import AuditResult
from audit.shared.config import get_audit_config_manager
from audit.shared.decorators import log_user_action


class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件

    自动为每个请求生成唯一ID，提取客户端信息，并存储在request.state中
    供审计装饰器使用。
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始时间
        start_time = time.time()
        request.state.start_time = start_time

        # 提取客户端信息
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")

        # 存储到request.state
        request.state.client_ip = client_ip
        request.state.user_agent = user_agent

        # 记录请求开始
        logger.info(
            f"请求开始 - ID: {request_id}, Method: {request.method}, "
            f"URL: {request.url}, IP: {client_ip}, UserAgent: {user_agent[:100]}"
        )

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time
            request.state.process_time = process_time

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

            # 记录请求完成
            logger.info(
                f"请求完成 - ID: {request_id}, Status: {response.status_code}, "
                f"Time: {process_time:.3f}s"
            )

            return response

        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求异常
            logger.error(
                f"请求异常 - ID: {request_id}, Error: {e!s}, "
                f"Time: {process_time:.3f}s", exc_info=True
            )

            # 重新抛出异常
            raise

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # 取第一个IP（原始客户端IP）
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # 使用直接连接IP
        if request.client:
            return request.client.host

        return "unknown"


class AutoAuditMiddleware(BaseHTTPMiddleware):
    """自动审计中间件

    根据配置自动为特定路径记录审计日志，适用于不便使用装饰器的场景。
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.config_manager = get_audit_config_manager()

    async def dispatch(self, request: Request, call_next):
        # 检查全局审计开关
        if not self.config_manager.is_audit_enabled():
            return await call_next(request)

        # 检查路径是否被排除
        if self.config_manager.is_path_excluded(request.url.path):
            return await call_next(request)

        # 获取路由审计配置
        route_config = self.config_manager.get_route_config(
            request.url.path,
            request.method
        )

        if not route_config or not route_config.enabled:
            return await call_next(request)

        # 提取请求信息
        client_ip = getattr(request.state, "client_ip", None)
        user_agent = getattr(request.state, "user_agent", None)
        request_id = getattr(request.state, "request_id", None)

        # 获取审计规则
        audit_rule = route_config.rule

        try:
            # 处理请求
            response = await call_next(request)

            # 根据响应状态判断结果
            result = AuditResult.SUCCESS if response.status_code < 400 else AuditResult.FAILURE
            error_message = None if result == AuditResult.SUCCESS else f"HTTP {response.status_code}"

            # 记录审计日志
            await log_user_action(
                action=audit_rule.action,
                description=audit_rule.description,
                resource_type=audit_rule.resource_type,
                result=result,
                error_message=error_message,
                ip_address=client_ip,
                user_agent=user_agent,
                request_id=request_id,
                metadata={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "auto_audit": True,
                    **audit_rule.metadata
                }
            )

            return response

        except Exception as e:
            # 记录失败的审计日志
            await log_user_action(
                action=audit_rule.action,
                description=f"{audit_rule.description} - 请求异常",
                resource_type=audit_rule.resource_type,
                result=AuditResult.FAILURE,
                error_message=str(e),
                ip_address=client_ip,
                user_agent=user_agent,
                request_id=request_id,
                metadata={
                    "method": request.method,
                    "path": str(request.url.path),
                    "auto_audit": True,
                    "exception": type(e).__name__,
                    **audit_rule.metadata
                }
            )

            # 重新抛出异常
            raise

def create_audit_middleware(
    app: ASGIApp,
    enable_request_context: bool = True,
    enable_auto_audit: bool = False,
) -> ASGIApp:
    """创建审计中间件组合

    Args:
        app: ASGI应用
        enable_request_context: 是否启用请求上下文中间件
        enable_auto_audit: 是否启用自动审计中间件

    Returns:
        包装后的ASGI应用
    """
    if enable_request_context:
        app = RequestContextMiddleware(app)

    if enable_auto_audit:
        app = AutoAuditMiddleware(app)

    return app
