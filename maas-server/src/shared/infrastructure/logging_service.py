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

"""日志服务 - 统一的日志配置和管理"""

import sys
from pathlib import Path
from typing import Any

from loguru import logger

from config.schemas import Settings


class LoggingService:
    """日志服务类 - 管理系统日志配置"""

    def __init__(self, settings: Settings):
        """初始化日志服务
        
        Args:
            settings: 系统配置
        """
        self.settings = settings
        self._configured = False

    def configure(self) -> None:
        """配置日志系统"""
        if self._configured:
            return

        # 移除默认handler
        logger.remove()

        # 确保日志目录存在
        log_dir = Path(self.settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # 配置控制台日志
        if self.settings.log_console_enabled:
            self._configure_console_logger()

        # 配置文件日志
        if self.settings.log_file_enabled:
            self._configure_file_logger()

        self._configured = True
        logger.info("日志系统配置完成")

    def _configure_console_logger(self) -> None:
        """配置控制台日志"""
        console_format = self._get_console_format()

        logger.add(
            sys.stdout,
            level=self.settings.log_level,
            format=console_format,
            colorize=True,
            enqueue=True,
        )

    def _configure_file_logger(self) -> None:
        """配置文件日志"""
        log_path = self._get_log_file_path()

        # 配置主日志文件
        logger.add(
            log_path,
            level=self.settings.log_level,
            format=self.settings.log_format,
            rotation=self.settings.log_rotation,
            retention=self.settings.log_retention,
            compression="gz",
            enqueue=True,
            serialize=self.settings.log_json_format,
        )

        # 配置错误日志文件
        error_log_path = log_path.parent / "error.log"
        logger.add(
            error_log_path,
            level="ERROR",
            format=self.settings.log_format,
            rotation=self.settings.log_rotation,
            retention=self.settings.log_retention,
            compression="gz",
            enqueue=True,
            serialize=self.settings.log_json_format,
        )

    def _get_console_format(self) -> str:
        """获取控制台日志格式"""
        if self.settings.log_json_format:
            return self.settings.log_format
        else:
            return (
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )

    def _get_log_file_path(self) -> Path:
        """获取日志文件路径"""
        log_dir = Path(self.settings.log_dir)

        if self.settings.log_file:
            return log_dir / self.settings.log_file
        else:
            return log_dir / "app.log"

    def create_structured_logger(self, context: dict[str, Any] | None = None) -> Any:
        """创建结构化日志记录器
        
        Args:
            context: 上下文信息
            
        Returns:
            配置了上下文的logger实例
        """
        if context is None:
            context = {}

        return logger.bind(**context)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        request_id: str | None = None,
        user_id: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        """记录HTTP请求日志
        
        Args:
            method: HTTP方法
            path: 请求路径  
            status_code: 状态码
            duration: 处理时间(秒)
            request_id: 请求ID
            user_id: 用户ID
            ip_address: 客户端IP
        """
        context = {
            "request_id": request_id,
            "user_id": user_id,
            "ip_address": ip_address,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
        }

        structured_logger = self.create_structured_logger(context)

        if status_code >= 500:
            structured_logger.error(f"请求处理失败: {method} {path}")
        elif status_code >= 400:
            structured_logger.warning(f"请求错误: {method} {path}")
        else:
            structured_logger.info(f"请求完成: {method} {path}")

    def log_business_event(
        self,
        event_type: str,
        message: str,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """记录业务事件日志
        
        Args:
            event_type: 事件类型
            message: 事件消息
            user_id: 用户ID
            resource_type: 资源类型
            resource_id: 资源ID
            metadata: 额外元数据
        """
        context = {
            "event_type": event_type,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "metadata": metadata or {},
        }

        structured_logger = self.create_structured_logger(context)
        structured_logger.info(message)


# 全局日志服务实例
_logging_service: LoggingService | None = None


def get_logging_service() -> LoggingService:
    """获取日志服务实例(单例模式)"""
    global _logging_service
    if _logging_service is None:
        from config.settings import settings
        _logging_service = LoggingService(settings)
        _logging_service.configure()
    return _logging_service


def get_logger(name: str | None = None, **context: Any) -> Any:
    """获取配置好的logger实例
    
    Args:
        name: logger名称
        **context: 上下文信息
        
    Returns:
        logger实例
    """
    service = get_logging_service()

    if context:
        return service.create_structured_logger(context)
    else:
        return logger.bind(name=name) if name else logger
