"""共享基础设施层 - 数据库配置"""

from collections.abc import AsyncGenerator

import redis
from loguru import logger
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config.settings import settings

# 创建元数据
metadata = MetaData()

# 创建基类
class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    metadata = metadata


# 异步数据库引擎
async_engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.server.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
)

# 异步会话工厂
async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 同步数据库引擎（用于Alembic迁移）
sync_engine = create_engine(
    settings.database.url_sync,
    echo=settings.server.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
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
    settings.get_redis_url(),
    decode_responses=True,
    retry_on_timeout=True,
    retry_on_error=[redis.BusyLoadingError, redis.ConnectionError],
    health_check_interval=30,
    max_connections=50,
    socket_connect_timeout=5,
    socket_timeout=5,
)


def get_redis():
    """获取Redis客户端"""
    return redis_client


async def check_redis_connection() -> bool:
    """检查Redis连接状态"""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False


async def init_database() -> None:
    """初始化数据库"""
    logger.info("创建数据库表...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        logger.info("数据库表创建完成")
        return True
    except Exception:
        return False
    logger.info("数据库表创建失败")


async def init_redis():
    """初始化Redis连接"""
    try:
        # 检查Redis连接
        if await check_redis_connection():
            return True
        return False
    except Exception:
        return False


async def close_database():
    """关闭数据库连接"""
    try:
        await async_engine.dispose()
        sync_engine.dispose()
    except Exception:
        pass


async def close_redis():
    """关闭Redis连接"""
    try:
        redis_client.close()
    except Exception:
        pass
