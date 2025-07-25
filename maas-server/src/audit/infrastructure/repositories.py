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

"""审计日志仓储实现"""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from audit.domain.models import ActionType, AuditLog, AuditResult, ResourceType
from audit.domain.repositories import AuditLogFilter, AuditLogRepository
from audit.infrastructure.batch_operations import AuditLogBatchOperations
from audit.infrastructure.models import AuditLogORM


class SQLAlchemyAuditLogRepository(AuditLogRepository):
    """基于SQLAlchemy的审计日志仓储实现"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_ops = AuditLogBatchOperations(session)

    async def save(self, audit_log: AuditLog) -> None:
        """保存审计日志"""
        try:
            audit_log_orm = AuditLogORM(
                audit_log_id=audit_log.audit_log_id,
                user_id=audit_log.user_id,
                username=audit_log.username,
                action=audit_log.action.value,
                resource_type=audit_log.resource_type.value if audit_log.resource_type else None,
                resource_id=audit_log.resource_id,
                description=audit_log.description,
                ip_address=audit_log.ip_address,
                user_agent=audit_log.user_agent,
                request_id=audit_log.request_id,
                result=audit_log.result.value,
                error_message=audit_log.error_message,
                extra_data=audit_log.metadata,
                created_at=audit_log.created_at,
            )

            self.session.add(audit_log_orm)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def find_by_id(self, audit_log_id: UUID) -> AuditLog | None:
        """根据ID查找审计日志"""
        result = await self.session.execute(
            select(AuditLogORM).where(AuditLogORM.audit_log_id == audit_log_id)
        )
        audit_log_orm = result.scalar_one_or_none()

        if audit_log_orm is None:
            return None

        return self._orm_to_domain(audit_log_orm)

    async def find_by_filter(
        self,
        filter_obj: AuditLogFilter,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[AuditLog]:
        """根据过滤条件查找审计日志"""
        query = select(AuditLogORM)

        # 应用过滤条件
        query = self._apply_filter(query, filter_obj)

        # 应用排序
        if order_desc:
            query = query.order_by(desc(getattr(AuditLogORM, order_by)))
        else:
            query = query.order_by(getattr(AuditLogORM, order_by))

        # 应用分页
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        audit_log_orms = result.scalars().all()

        return [self._orm_to_domain(orm) for orm in audit_log_orms]

    async def count_by_filter(self, filter_obj: AuditLogFilter) -> int:
        """统计符合条件的审计日志数量"""
        query = select(func.count(AuditLogORM.id))
        query = self._apply_filter(query, filter_obj)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def find_by_user_id(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        """根据用户ID查找审计日志"""
        filter_obj = AuditLogFilter(user_id=user_id)
        return await self.find_by_filter(filter_obj, limit, offset)

    async def find_by_resource(
        self,
        resource_type: ResourceType,
        resource_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        """根据资源查找审计日志"""
        filter_obj = AuditLogFilter(
            resource_type=resource_type,
            resource_id=resource_id
        )
        return await self.find_by_filter(filter_obj, limit, offset)

    async def find_recent_logins(
        self,
        user_id: UUID | None = None,
        hours: int = 24,
        limit: int = 50,
    ) -> list[AuditLog]:
        """查找最近的登录记录"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        filter_obj = AuditLogFilter(
            user_id=user_id,
            action=ActionType.LOGIN,
            start_time=start_time
        )
        return await self.find_by_filter(filter_obj, limit, 0)

    async def find_failed_operations(
        self,
        hours: int = 1,
        limit: int = 50,
    ) -> list[AuditLog]:
        """查找失败的操作记录"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        filter_obj = AuditLogFilter(
            result=AuditResult.FAILURE,
            start_time=start_time
        )
        return await self.find_by_filter(filter_obj, limit, 0)

    async def find_with_count_by_filter(
        self,
        filter_obj: AuditLogFilter,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[AuditLog], int]:
        """根据过滤条件查找审计日志并返回总数"""
        try:
            # 构建查询
            data_query = select(AuditLogORM)
            count_query = select(func.count(AuditLogORM.id))

            # 应用过滤条件
            data_query = self._apply_filter(data_query, filter_obj)
            count_query = self._apply_filter(count_query, filter_obj)

            # 先执行count查询
            count_result = await self.session.execute(count_query)
            total = count_result.scalar() or 0

            # 如果没有数据，直接返回
            if total == 0:
                return [], 0

            # 应用排序和分页
            if order_desc:
                data_query = data_query.order_by(desc(getattr(AuditLogORM, order_by)))
            else:
                data_query = data_query.order_by(getattr(AuditLogORM, order_by))

            data_query = data_query.limit(limit).offset(offset)

            # 执行数据查询
            data_result = await self.session.execute(data_query)
            audit_log_orms = data_result.scalars().all()

            return [self._orm_to_domain(orm) for orm in audit_log_orms], total
        except Exception:
            await self.session.rollback()
            raise

    async def find_by_ids(self, log_ids: list[UUID]) -> list[AuditLog]:
        """根据ID列表批量查找审计日志"""
        if not log_ids:
            return []

        query = select(AuditLogORM).where(AuditLogORM.audit_log_id.in_(log_ids))
        result = await self.session.execute(query)
        audit_log_orms = result.scalars().all()

        return [self._orm_to_domain(orm) for orm in audit_log_orms]

    async def get_statistics(
        self,
        start_time: datetime | None = None,
        include_user_stats: bool = False,
        include_action_stats: bool = False,
    ) -> dict:
        """获取审计日志统计信息"""
        try:
            # 使用单个查询获取基本统计信息
            base_conditions = []
            if start_time:
                base_conditions.append(AuditLogORM.created_at >= start_time)

            # 构建统计查询 - 使用条件聚合
            stats_query = select(
                func.count(AuditLogORM.id).label("total"),
                func.sum(
                    case((AuditLogORM.result == AuditResult.SUCCESS.value, 1), else_=0)
                ).label("successful"),
                func.sum(
                    case((AuditLogORM.result == AuditResult.FAILURE.value, 1), else_=0)
                ).label("failed")
            )

            if base_conditions:
                stats_query = stats_query.where(and_(*base_conditions))

            # 执行基本统计查询
            stats_result = await self.session.execute(stats_query)
            stats_row = stats_result.first()

            total = stats_row.total or 0
            successful = stats_row.successful or 0
            failed = stats_row.failed or 0

            # 最近登录统计
            recent_login_time = datetime.utcnow() - timedelta(hours=24)
            login_conditions = [
                AuditLogORM.action == ActionType.LOGIN.value,
                AuditLogORM.created_at >= recent_login_time
            ]

            login_stats_query = select(
                func.count(AuditLogORM.id).label("login_count"),
                func.count(func.distinct(AuditLogORM.user_id)).label("unique_users")
            ).where(and_(*login_conditions))

            login_result = await self.session.execute(login_stats_query)
            login_row = login_result.first()

            recent_logins = login_row.login_count or 0
            unique_users = login_row.unique_users or 0

            # 热门操作统计（如果需要）
            top_actions = []
            if include_action_stats:
                action_stats_query = select(
                    AuditLogORM.action,
                    func.count(AuditLogORM.id).label("count")
                ).group_by(AuditLogORM.action).order_by(desc("count")).limit(10)

                if base_conditions:
                    action_stats_query = action_stats_query.where(and_(*base_conditions))

                action_result = await self.session.execute(action_stats_query)
                top_actions = [
                    {"action": row.action, "count": row.count}
                    for row in action_result.fetchall()
                ]
            else:
                # 简化实现
                top_actions = [
                    {"action": "login", "count": recent_logins},
                    {"action": "profile_update", "count": 0},
                    {"action": "password_change", "count": 0},
                ]

            return {
                "total": total,
                "successful": successful,
                "failed": failed,
                "unique_users": unique_users,
                "recent_logins": recent_logins,
                "top_actions": top_actions,
            }
        except Exception:
            await self.session.rollback()
            raise

    def _apply_filter(self, query, filter_obj: AuditLogFilter):
        """应用过滤条件"""
        conditions = []

        if filter_obj.user_id is not None:
            conditions.append(AuditLogORM.user_id == filter_obj.user_id)

        if filter_obj.username is not None:
            conditions.append(AuditLogORM.username.ilike(f"%{filter_obj.username}%"))

        if filter_obj.action is not None:
            conditions.append(AuditLogORM.action == filter_obj.action.value)

        if filter_obj.resource_type is not None:
            conditions.append(AuditLogORM.resource_type == filter_obj.resource_type.value)

        if filter_obj.resource_id is not None:
            conditions.append(AuditLogORM.resource_id == filter_obj.resource_id)

        if filter_obj.result is not None:
            conditions.append(AuditLogORM.result == filter_obj.result.value)

        if filter_obj.ip_address is not None:
            conditions.append(AuditLogORM.ip_address == filter_obj.ip_address)

        if filter_obj.start_time is not None:
            conditions.append(AuditLogORM.created_at >= filter_obj.start_time)

        if filter_obj.end_time is not None:
            conditions.append(AuditLogORM.created_at <= filter_obj.end_time)

        if filter_obj.search_keyword is not None:
            keyword = f"%{filter_obj.search_keyword}%"
            conditions.append(
                or_(
                    AuditLogORM.description.ilike(keyword),
                    AuditLogORM.username.ilike(keyword),
                    AuditLogORM.action.ilike(keyword),
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        return query

    def _orm_to_domain(self, orm: AuditLogORM) -> AuditLog:
        """将ORM模型转换为领域模型"""
        return AuditLog(
            audit_log_id=orm.audit_log_id,
            user_id=orm.user_id,
            username=orm.username,
            action=ActionType(orm.action),
            resource_type=ResourceType(orm.resource_type) if orm.resource_type else None,
            resource_id=orm.resource_id,
            description=orm.description,
            ip_address=orm.ip_address,
            user_agent=orm.user_agent,
            request_id=orm.request_id,
            result=AuditResult(orm.result),
            error_message=orm.error_message,
            metadata=orm.extra_data,
            created_at=orm.created_at,
        )

    async def batch_save(self, audit_logs: list[AuditLog]) -> None:
        """批量保存审计日志"""
        await self.batch_ops.batch_save(audit_logs)

    async def cleanup_old_logs(self, before_date: datetime, batch_size: int = 1000) -> int:
        """清理旧的审计日志"""
        return await self.batch_ops.batch_delete_old_logs(before_date, batch_size)

    async def optimize_table(self) -> None:
        """优化审计日志表"""
        await self.batch_ops.vacuum_analyze_audit_table()


async def get_audit_log_repository() -> AuditLogRepository:
    """获取审计日志仓储实例
    
    注意：返回的仓储实例需要在适当的会话上下文中使用
    建议在调用方使用 async with async_session_factory() as session 管理会话
    """
    from shared.infrastructure.database import async_session_factory
    # 注意：这里不应该直接创建会话，应该由调用方管理
    # 这个函数保持向后兼容，但建议使用依赖注入
    session = async_session_factory()
    return SQLAlchemyAuditLogRepository(session)
