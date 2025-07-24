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

"""共享基础设施层 - 通用健康检查基类"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Type

from sqlalchemy import text, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from shared.infrastructure.database import async_session_factory, Base


class BaseDatabaseHealthCheck(ABC):
    """数据库健康检查基类"""
    
    def __init__(self, model_class: Optional[Type[Base]] = None):
        self.model_class = model_class
    
    @staticmethod
    async def check_connection() -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            async with async_session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                return {
                    "status": "healthy",
                    "message": "数据库连接正常",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            return {
                "status": "unhealthy",
                "message": f"数据库连接失败: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_table_status(self, table_name: str) -> Dict[str, Any]:
        """检查表状态"""
        if not self.model_class:
            return {
                "status": "skipped",
                "message": "未指定模型类",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            async with async_session_factory() as session:
                # 检查表是否存在并可访问
                count_query = select(func.count(self.model_class.id))
                result = await session.execute(count_query)
                total_records = result.scalar()
                
                # 检查最近的记录（如果有created_at字段）
                recent_records = 0
                if hasattr(self.model_class, 'created_at'):
                    recent_query = select(func.count(self.model_class.id)).where(
                        self.model_class.created_at >= datetime.utcnow() - timedelta(hours=24)
                    )
                    result = await session.execute(recent_query)
                    recent_records = result.scalar()
                
                return {
                    "status": "healthy",
                    "total_records": total_records,
                    "recent_24h_records": recent_records,
                    "message": f"{table_name}表状态正常",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"{table_name}表检查失败: {e}")
            return {
                "status": "unhealthy",
                "message": f"{table_name}表检查失败: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_performance(self) -> Dict[str, Any]:
        """检查数据库性能"""
        if not self.model_class:
            return {
                "status": "skipped",
                "message": "未指定模型类",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            async with async_session_factory() as session:
                start_time = datetime.utcnow()
                
                # 执行一个简单的查询来测试响应时间
                query = select(self.model_class).limit(1)
                await session.execute(query)
                
                end_time = datetime.utcnow()
                response_time_ms = (end_time - start_time).total_seconds() * 1000
                
                status = "healthy" if response_time_ms < 1000 else "warning"
                if response_time_ms > 5000:
                    status = "unhealthy"
                
                return {
                    "status": status,
                    "response_time_ms": round(response_time_ms, 2),
                    "message": f"查询响应时间: {response_time_ms:.2f}ms",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"性能检查失败: {e}")
            return {
                "status": "unhealthy",
                "message": f"性能检查失败: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def get_connection_pool_stats() -> Dict[str, Any]:
        """获取连接池统计信息"""
        try:
            async with async_session_factory() as session:
                # 获取当前活跃连接数
                result = await session.execute(text(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                ))
                active_connections = result.scalar()
                
                # 获取总连接数
                result = await session.execute(text(
                    "SELECT count(*) FROM pg_stat_activity"
                ))
                total_connections = result.scalar()
                
                return {
                    "status": "healthy",
                    "active_connections": active_connections,
                    "total_connections": total_connections,
                    "message": "连接池状态正常",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"连接池统计获取失败: {e}")
            return {
                "status": "unknown",
                "message": f"连接池统计获取失败: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def comprehensive_health_check(self, table_name: str) -> Dict[str, Any]:
        """综合健康检查"""
        checks = {
            "connection": await self.check_connection(),
            "table_status": await self.check_table_status(table_name),
            "performance": await self.check_performance(),
            "connection_pool": await self.get_connection_pool_stats(),
        }
        
        # 确定整体状态
        overall_status = "healthy"
        unhealthy_checks = []
        
        for check_name, check_result in checks.items():
            if check_result.get("status") == "unhealthy":
                overall_status = "unhealthy"
                unhealthy_checks.append(check_name)
            elif check_result.get("status") == "warning" and overall_status == "healthy":
                overall_status = "warning"
        
        return {
            "overall_status": overall_status,
            "checks": checks,
            "unhealthy_checks": unhealthy_checks,
            "timestamp": datetime.utcnow().isoformat()
        }


async def quick_health_check() -> bool:
    """快速健康检查，返回布尔值"""
    try:
        result = await BaseDatabaseHealthCheck.check_connection()
        return result.get("status") == "healthy"
    except Exception:
        return False