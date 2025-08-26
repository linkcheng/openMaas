"""
Copyright 2025 MaaS Team

请求上下文中间件 - 统一使用trace_id

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
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from shared.infrastructure.logging_service import get_logger_with_trace, set_trace_id

logger = get_logger_with_trace()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件 - 统一使用trace_id"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 生成trace_id（统一标识，短格式便于查看）
        trace_id = str(uuid.uuid4())[:8]

        # 设置到contextvar（业务代码可用）
        set_trace_id(trace_id)

        # 设置到request.state（保持向后兼容）
        request.state.trace_id = trace_id
        request.state.request_id = trace_id  # 保持向后兼容

        # 记录请求开始时间
        start_time = time.time()
        request.state.start_time = start_time

        # 提取客户端信息
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")

        # 存储到request.state
        request.state.client_ip = client_ip
        request.state.user_agent = user_agent

        logger.info(f"请求开始 - {request.method} {request.url.path}")

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time
            request.state.process_time = process_time

            # 添加响应头（保持兼容性）
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Request-ID"] = trace_id  # 保持兼容性
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

            logger.info(
                f"请求完成 - Status: {response.status_code}, "
                f"Time: {process_time:.3f}s"
            )

            return response

        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time

            logger.error(f"请求异常 - {e}", exc_info=True)

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
