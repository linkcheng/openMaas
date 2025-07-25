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

"""共享基础设施层 - 通用批量操作基类"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar

from loguru import logger
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from shared.infrastructure.database import Base

T = TypeVar("T")  # 领域模型类型
M = TypeVar("M", bound=Base)  # ORM模型类型


class BaseBatchOperations(ABC, Generic[T, M]):
    """通用批量操作基类"""

    def __init__(self, session: AsyncSession, model_class: type[M]):
        self.session = session
        self.model_class = model_class

    async def batch_save(self, entities: list[T], batch_size: int | None = None) -> None:
        """批量保存实体
        
        Args:
            entities: 实体列表
            batch_size: 批次大小，None时使用配置默认值
        """
        if not entities:
            return

        if batch_size is None:
            batch_size = settings.performance.batch_size

        try:
            # 转换为ORM数据
            orm_data = []
            for entity in entities:
                orm_data.append(self._entity_to_dict(entity))

            # 分批插入
            for i in range(0, len(orm_data), batch_size):
                batch = orm_data[i:i + batch_size]

                # 使用PostgreSQL的ON CONFLICT处理重复
                stmt = insert(self.model_class).values(batch)
                conflict_columns = self._get_conflict_columns()
                if conflict_columns:
                    stmt = stmt.on_conflict_do_nothing(index_elements=conflict_columns)

                await self.session.execute(stmt)

            await self.session.commit()
            logger.info(f"批量保存{self.model_class.__name__}成功，共 {len(entities)} 条记录")

        except Exception as e:
            await self.session.rollback()
            logger.error(f"批量保存{self.model_class.__name__}失败: {e}", exc_info=True)
            raise

    async def batch_delete_by_date(
        self,
        date_column: str,
        before_date: datetime,
        batch_size: int | None = None,
        max_batches: int = 100
    ) -> int:
        """批量删除指定日期之前的记录
        
        Args:
            date_column: 日期字段名
            before_date: 删除此日期之前的记录
            batch_size: 每批删除的数量，None时使用配置默认值
            max_batches: 最大批次数，防止长时间锁表
            
        Returns:
            删除的记录数
        """
        if batch_size is None:
            batch_size = settings.performance.cleanup_batch_size

        total_deleted = 0

        try:
            date_field = getattr(self.model_class, date_column)

            for batch_num in range(max_batches):
                # 查找要删除的ID
                ids_query = select(self.model_class.id).where(
                    date_field < before_date
                ).limit(batch_size)

                result = await self.session.execute(ids_query)
                ids_to_delete = [row[0] for row in result.fetchall()]

                if not ids_to_delete:
                    break

                # 删除这批记录
                delete_query = self.model_class.__table__.delete().where(
                    self.model_class.id.in_(ids_to_delete)
                )

                result = await self.session.execute(delete_query)
                deleted_count = result.rowcount
                total_deleted += deleted_count

                await self.session.commit()

                logger.info(f"批次 {batch_num + 1}: 删除了 {deleted_count} 条{self.model_class.__name__}记录")

                # 如果删除的记录数少于批次大小，说明已经删除完毕
                if deleted_count < batch_size:
                    break

            logger.info(f"批量删除{self.model_class.__name__}完成，总共删除 {total_deleted} 条记录")
            return total_deleted

        except Exception as e:
            await self.session.rollback()
            logger.error(f"批量删除{self.model_class.__name__}失败: {e}", exc_info=True)
            raise

    async def vacuum_analyze_table(self, table_name: str) -> None:
        """对指定表执行VACUUM ANALYZE优化
        
        Args:
            table_name: 表名
            
        注意：这个操作需要适当的数据库权限
        """
        try:
            # 注意：VACUUM不能在事务中执行
            await self.session.execute(text(f"VACUUM ANALYZE {table_name}"))
            logger.info(f"表 {table_name} VACUUM ANALYZE完成")
        except Exception as e:
            logger.warning(f"表 {table_name} VACUUM ANALYZE失败: {e}")
            # 这个操作失败不应该影响主流程

    @abstractmethod
    def _entity_to_dict(self, entity: T) -> dict[str, Any]:
        """将领域实体转换为字典格式
        
        Args:
            entity: 领域实体
            
        Returns:
            字典格式的数据
        """
        pass

    def _get_conflict_columns(self) -> list[str]:
        """获取冲突检测的列名
        
        Returns:
            用于冲突检测的列名列表，默认为空（不处理冲突）
        """
        return []


class BatchOperationsMixin:
    """批量操作混入类，为仓储类提供批量操作能力"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._batch_ops = None

    @property
    def batch_ops(self):
        """获取批量操作实例"""
        if self._batch_ops is None:
            self._batch_ops = self._create_batch_operations()
        return self._batch_ops

    @abstractmethod
    def _create_batch_operations(self):
        """创建批量操作实例"""
        pass
