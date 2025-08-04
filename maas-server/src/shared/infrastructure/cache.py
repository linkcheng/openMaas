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

"""共享基础设施层 - 缓存配置"""

import contextlib

import redis
from loguru import logger

from config.settings import settings

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
    socket_keepalive=True,
)

def get_redis():
    """获取Redis客户端"""
    return redis_client


async def check_redis_connection() -> bool:
    """检查Redis连接状态"""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"ping err {e}", exc_info=True)
        return False

async def init_redis():
    """初始化Redis连接"""
    try:
        # 检查Redis连接
        return bool(await check_redis_connection())
    except Exception as e:
        logger.error(f"{e}", exc_info=True)
        return False


async def close_redis():
    """关闭Redis连接"""
    with contextlib.suppress(Exception):
        redis_client.close()



# from circuitbreaker import circuit

# @circuit(failure_threshold=3, recovery_timeout=60)
# async def safe_redis_operation():
#     return redis_client.ping()


# from tenacity import retry, stop_after_attempt, wait_exponential

# @retry(
#     stop=stop_after_attempt(3),
#     wait=wait_exponential(multiplier=1, max=10),
#     retry=retry_if_exception_type(
#         (redis.TimeoutError, redis.ConnectionError)
# )
# def reliable_redis_operation():
#     return redis_client.ping()
