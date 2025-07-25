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

"""共享基础设施层 - 数据库配置"""

from collections.abc import AsyncGenerator

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
    # 优化后的连接池配置
    pool_size=10,          # 常规连接数
    max_overflow=5,        # 临时超额连接
    pool_timeout=30,       # 获取连接超时时间
    pool_recycle=300,      # 更短的连接回收周期
    pool_pre_ping=True,    # 执行前健康检查
    connect_args={
        "server_settings": {
            "application_name": "maas_backend"
        }
    }
)

# 异步会话工厂
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=True,  # 确保数据一致性
    autoflush=False,
    future=True,           # 启用2.0特性
)

# async_session_factory = async_sessionmaker(
#     bind=async_engine,
#     twophase=True,  # 启用两阶段提交
#     info={"require_new_connection": True}  # 强制新连接
# )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database operation failed: {exc}")
            raise
        finally:
            await session.close()
            logger.debug("Session closed")


# 别名，用于依赖注入
get_db_session = get_async_session



async def check_database_health():
    """深度健康检查"""
    try:
        async with async_engine.connect() as conn:
            await conn.scalar("SELECT 1")
            return True
    except Exception as e:
        logger.critical(f"Database health check failed: {e}")
        return False


async def init_database() -> bool:
    """初始化数据库"""
    logger.info("创建数据库表...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        logger.info("数据库表创建完成")

        # 初始化数据
        from .database_initializer import init_initial_data
        init_success = await init_initial_data()
        if init_success:
            logger.info("数据库初始数据创建完成")
        else:
            logger.warning("数据库初始数据创建失败")

        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False



async def close_database():
    """关闭数据库连接"""
    try:
        await async_engine.dispose()
        sync_engine.dispose()
    except Exception:
        pass



# 同步数据库引擎（用于Alembic迁移）
sync_engine = create_engine(
    settings.database.url_sync,
    echo=settings.server.debug,
    # 优化后的连接池配置
    pool_size=10,                # 常规连接数（根据服务器核心数调整）
    max_overflow=5,              # 临时超额连接数
    pool_timeout=30,             # 连接获取超时时间（秒）
    pool_recycle=300,            # 连接回收周期（秒），建议小于数据库的wait_timeout
    pool_pre_ping=True,          # 执行前健康检查
    connect_args={
        "connect_timeout": 5,    # 连接建立超时
        "application_name": "maas_alembic"  # 标识连接来源
    }
)

# 同步会话工厂（线程安全配置）
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=True,      # 避免脏数据
    future=True,                # 启用SQLAlchemy 2.0特性
    twophase=False,             # 根据分布式事务需求调整
    info={"purpose": "alembic"} # 标记会话用途
)

def get_sync_session():
    """线程安全的同步会话生成器（改进版）

    特点：
    1. 明确会话生命周期
    2. 自动清理资源
    3. 异常安全处理
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()  # 自动提交成功操作
    except Exception as e:
        session.rollback()  # 异常时回滚
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        session.close()
        logger.debug("Sync session closed")



from sqlalchemy import event


@event.listens_for(async_engine.sync_engine, "connect")
def on_connect(dbapi_conn, connection_record):
    logger.debug(f"New connection established: {id(dbapi_conn)}")


@event.listens_for(async_engine.sync_engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    logger.debug(f"Connection checked out: {id(dbapi_conn)}")

