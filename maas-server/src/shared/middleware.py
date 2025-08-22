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
