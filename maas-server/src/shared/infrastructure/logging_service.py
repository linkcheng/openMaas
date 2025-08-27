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

"""日志服务 - 简化版基础配置 + trace_id支持"""

import contextvars
import sys
from pathlib import Path

import loguru as _loguru
from loguru import logger

from config.schemas import Settings
from config.settings import settings

# trace_id上下文变量（业务代码友好）
trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id")


def _ensure_trace_id(record):
    """在日志记录中确保存在trace_id，缺省为'-'"""
    record["extra"].setdefault("trace_id", "-")
    return record


# 全局替换 loguru.logger，确保任意位置 `from loguru import logger` 均带默认 trace_id
_loguru.logger = _loguru.logger.patch(_ensure_trace_id).bind(trace_id="-")

# 本模块内使用与全局一致的 logger 引用
logger = _loguru.logger


class LoggingService:
    """简化版日志服务 - 基础配置 + trace_id支持"""

    def __init__(self, settings: Settings):
        """初始化日志服务"""
        self.settings = settings
        self._configured = False

    def configure(self) -> None:
        """配置日志系统 - 仅做基础配置"""
        if self._configured:
            return

        # 清除默认handler
        logger.remove()

        # 配置文件日志
        if self.settings.log_file_enabled:
            log_dir = Path(self.settings.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)

            log_path = log_dir / (self.settings.log_file or "app.log")
            logger.add(
                log_path,
                level=self.settings.log_level,
                format=self.settings.log_format,
                rotation=self.settings.log_rotation,
                retention=self.settings.log_retention,
                compression="gz"
            )

        # 配置控制台日志
        if self.settings.log_console_enabled:
            console_format = self._get_console_format()
            logger.add(
                sys.stdout,
                level=self.settings.log_level,
                format=console_format,
                colorize=True
            )

        self._configured = True
        logger.info("日志系统配置完成")

    def _get_console_format(self) -> str:
        """获取控制台日志格式"""
        if self.settings.log_json_format:
            return self.settings.log_format
        else:
            return (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level}</level> | "
                "trace:{extra[trace_id]} | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )


# 全局日志服务实例
_logging_service: LoggingService | None = None


def get_logging_service() -> LoggingService:
    """获取日志服务实例(单例模式)"""
    global _logging_service
    if _logging_service is None:
        _logging_service = LoggingService(settings)
        _logging_service.configure()
    return _logging_service


# 自动初始化日志服务
get_logging_service()


# trace_id便捷功能（保留业务代码友好性）
def get_trace_id() -> str | None:
    """获取当前上下文的trace_id"""
    try:
        return trace_id_var.get()
    except LookupError:
        return None


def set_trace_id(trace_id: str) -> None:
    """设置trace_id到上下文"""
    trace_id_var.set(trace_id)


def get_logger_with_trace():
    """获取自动包含trace_id的logger（业务代码友好）"""
    trace_id = get_trace_id()
    return logger.bind(trace_id=trace_id or "-")


# 保持向后兼容性
def get_logger(**context) -> logger:
    """获取logger实例（保持兼容性）"""
    if context:
        return logger.bind(**context)
    return  logger
