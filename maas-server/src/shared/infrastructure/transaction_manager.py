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

"""共享基础设施层 - 事务管理器"""

import contextvars
from collections.abc import AsyncGenerator, Callable
from functools import wraps
from typing import TypeVar

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session_factory

# 事务会话上下文变量
_transaction_session: contextvars.ContextVar[AsyncSession | None] = contextvars.ContextVar(
    "transaction_session", default=None
)

T = TypeVar("T")


class TransactionManager:
    """统一事务管理器"""

    @staticmethod
    def get_current_session() -> AsyncSession | None:
        """获取当前事务会话"""
        return _transaction_session.get(None)

    @staticmethod
    def set_current_session(session: AsyncSession) -> None:
        """设置当前事务会话"""
        _transaction_session.set(session)

    @staticmethod
    def clear_current_session() -> None:
        """清除当前事务会话"""
        _transaction_session.set(None)


async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
    """获取写操作会话（不自动管理事务）"""
    # 检查是否存在事务上下文
    current_session = TransactionManager.get_current_session()
    if current_session:
        yield current_session
        return

    # 创建新会话
    async with async_session_factory() as session:
        try:
            TransactionManager.set_current_session(session)
            yield session
        except Exception as exc:
            await session.rollback()
            logger.error(f"Write session error: {exc}")
            raise
        finally:
            await session.close()
            TransactionManager.clear_current_session()


async def get_readonly_session() -> AsyncGenerator[AsyncSession, None]:
    """获取只读会话（优化读操作）"""
    async with async_session_factory() as session:
        try:
            # 设置为只读模式（优化数据库性能）
            await session.execute(text("SET TRANSACTION READ ONLY"))
            yield session
        except Exception as exc:
            logger.error(f"Readonly session error: {exc}")
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话，不自动管理事务（已重构）
    
    注意：此函数已重构为不自动管理事务，事务管理交由上层控制。
    推荐使用 get_readonly_session()
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database session error: {exc}")
            raise
        finally:
            await session.close()
            logger.debug("Session closed")


def transactional():
    """声明式事务管理装饰器 - 仅用于写操作"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            
            # 检查是否已在事务中
            current_session = TransactionManager.get_current_session()
            if current_session:
                return await func(*args, **kwargs)

            async with async_session_factory() as session:
                # 设置事务上下文
                TransactionManager.set_current_session(session)
                
                try:
                    result = await func(*args, **kwargs)
                    await session.commit()
                    logger.debug("Transaction committed successfully")
                    return result
                except Exception as exc:
                    await session.rollback()
                    logger.error(f"Transaction failed, rolled back: {exc}")
                    raise
                finally:
                    await session.close()
                    TransactionManager.clear_current_session()
           

        return wrapper
    return decorator


class TransactionContext:
    """事务上下文管理器（手动使用）"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.previous_session: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        # 保存之前的会话
        self.previous_session = TransactionManager.get_current_session()
        # 设置当前事务会话
        TransactionManager.set_current_session(self.session)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.session.commit()
                logger.debug("Transaction context committed")
            else:
                await self.session.rollback()
                logger.error(f"Transaction context rolled back due to: {exc_val}")
        finally:
            # 恢复之前的会话
            TransactionManager.set_current_session(self.previous_session)

