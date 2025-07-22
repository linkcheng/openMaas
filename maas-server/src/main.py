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

"""FastAPI应用入口点"""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config.settings import settings
from shared.application.exceptions import ApplicationException, to_http_exception
from shared.infrastructure.database import (
    close_database,
    close_redis,
    init_database,
    init_redis,
)
from user.interface import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动MAAS平台...")

    # 初始化数据库连接
    db_status = await init_database()
    if db_status:
        logger.info("数据库连接初始化成功")
    else:
        logger.warning("数据库连接初始化失败，请检查配置")

    # 初始化Redis连接
    redis_status = await init_redis()
    if redis_status:
        logger.info("Redis连接初始化成功")
    else:
        logger.warning("Redis连接初始化失败，请检查配置")

    logger.info("MAAS平台启动完成")

    yield

    # 关闭时执行
    logger.info("正在关闭MAAS平台...")

    # 关闭数据库连接
    await close_database()
    logger.info("数据库连接已关闭")

    # 关闭Redis连接
    await close_redis()
    logger.info("Redis连接已关闭")

    logger.info("MAAS平台已关闭")

# 创建FastAPI应用
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description=settings.app.description,
    docs_url="/docs" if settings.server.debug else None,
    redoc_url="/redoc" if settings.server.debug else None,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加可信主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.server.debug else ["localhost", "127.0.0.1"]
)


# 请求ID中间件
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """为每个请求添加唯一ID"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # 添加请求ID到响应头
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()

    # 记录请求开始
    logger.info(
        f"请求开始: {request.method} {request.url.path} - "
        f"客户端: {request.client.host if request.client else 'unknown'} - "
        f"请求ID: {getattr(request.state, 'request_id', 'unknown')}"
    )

    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 记录请求完成
    logger.info(
        f"请求完成: {request.method} {request.url.path} - "
        f"状态码: {response.status_code} - "
        f"耗时: {process_time:.4f}s - "
        f"请求ID: {getattr(request.state, 'request_id', 'unknown')}"
    )

    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(process_time)

    return response


# 全局异常处理器
@app.exception_handler(ApplicationException)
async def application_exception_handler(request: Request, exc: ApplicationException):
    """应用异常处理器"""
    logger.error(
        f"应用异常: {exc.message} - "
        f"错误码: {exc.code} - "
        f"请求: {request.method} {request.url.path} - "
        f"请求ID: {getattr(request.state, 'request_id', 'unknown')}"
    )

    http_exc = to_http_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content={
            **http_exc.detail,
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": time.time()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.warning(
        f"HTTP异常: {exc.detail} - "
        f"状态码: {exc.status_code} - "
        f"请求: {request.method} {request.url.path} - "
        f"请求ID: {getattr(request.state, 'request_id', 'unknown')}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": {}
            },
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(
        f"未处理异常: {exc!s} - "
        f"类型: {type(exc).__name__} - "
        f"请求: {request.method} {request.url.path} - "
        f"请求ID: {getattr(request.state, 'request_id', 'unknown')}",
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误" if not settings.server.debug else str(exc),
                "details": {}
            },
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": time.time()
        }
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.app.version,
        "timestamp": time.time()
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 {settings.app.name}",
        "version": settings.app.version,
        "docs": "/docs" if settings.server.debug else None
    }


# 注册路由
app.include_router(user_router)


if __name__ == "__main__":
    import uvicorn

    # 配置日志
    logger.remove()
    logger.add(
        "logs/app.log",
        rotation="1 day",
        retention="30 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        lambda msg: print(msg, end=""),
        level=settings.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )

    # 启动服务器
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        log_level=settings.log_level.lower()
    )
