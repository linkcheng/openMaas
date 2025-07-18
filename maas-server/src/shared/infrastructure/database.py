"""共享基础设施层 - 数据库配置"""

from collections.abc import AsyncGenerator

import redis
from pymilvus import connections
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..application.config import settings

# SQLAlchemy 基础模型
Base = declarative_base()

# 异步数据库引擎
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 异步会话工厂
async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 同步数据库引擎（用于Alembic迁移）
sync_engine = create_engine(
    settings.database_url_sync,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 同步会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 别名，用于依赖注入
get_db_session = get_async_session


def get_sync_session():
    """获取同步数据库会话（用于依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis连接
redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    retry_on_timeout=True,
    retry_on_error=[redis.BusyLoadingError, redis.ConnectionError],
    health_check_interval=30,
)


def get_redis():
    """获取Redis客户端"""
    return redis_client


# Milvus连接
def init_milvus():
    """初始化Milvus连接"""
    connections.connect(
        alias="default",
        host=settings.milvus_host,
        port=settings.milvus_port,
    )


def get_milvus():
    """获取Milvus连接"""
    return connections.get_connection(alias="default")
