"""
Copyright 2025 MaaS Team

审计日志仓储接口定义

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

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from audit.domain.models import ActionType, AuditLog, AuditResult, ResourceType


class AuditLogFilter:
    """审计日志查询过滤器"""

    def __init__(
        self,
        user_id: UUID | None = None,
        username: str | None = None,
        action: ActionType | None = None,
        resource_type: ResourceType | None = None,
        resource_id: UUID | None = None,
        result: AuditResult | None = None,
        ip_address: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        search_keyword: str | None = None,
    ):
        self.user_id = user_id
        self.username = username
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.result = result
        self.ip_address = ip_address
        self.start_time = start_time
        self.end_time = end_time
        self.search_keyword = search_keyword


class AuditLogRepository(ABC):
    """审计日志仓储接口"""

    @abstractmethod
    async def save(self, audit_log: AuditLog) -> None:
        """保存审计日志

        Args:
            audit_log: 审计日志实体
        """
        pass
    
    @abstractmethod
    async def delete(self, audit_log_id: UUID) -> None:
        """删除审计日志"""
        pass

    @abstractmethod
    async def find_by_id(self, audit_log_id: UUID) -> AuditLog | None:
        """根据ID查找审计日志

        Args:
            audit_log_id: 审计日志ID

        Returns:
            审计日志实体，如果不存在则返回None
        """
        pass

    @abstractmethod
    async def find_by_filter(
        self,
        filter_obj: AuditLogFilter,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[AuditLog]:
        """根据过滤条件查找审计日志

        Args:
            filter_obj: 过滤条件
            limit: 返回数量限制
            offset: 偏移量
            order_by: 排序字段
            order_desc: 是否降序

        Returns:
            审计日志列表
        """
        pass

    @abstractmethod
    async def count_by_filter(self, filter_obj: AuditLogFilter) -> int:
        """统计符合条件的审计日志数量

        Args:
            filter_obj: 过滤条件

        Returns:
            数量
        """
        pass

    @abstractmethod
    async def find_by_user_id(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        """根据用户ID查找审计日志

        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            审计日志列表
        """
        pass

    @abstractmethod
    async def find_by_resource(
        self,
        resource_type: ResourceType,
        resource_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        """根据资源查找审计日志

        Args:
            resource_type: 资源类型
            resource_id: 资源ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            审计日志列表
        """
        pass

    @abstractmethod
    async def find_recent_logins(
        self,
        user_id: UUID | None = None,
        hours: int = 24,
        limit: int = 50,
    ) -> list[AuditLog]:
        """查找最近的登录记录

        Args:
            user_id: 用户ID，为空时查找所有用户
            hours: 最近多少小时
            limit: 返回数量限制

        Returns:
            审计日志列表
        """
        pass

    @abstractmethod
    async def find_failed_operations(
        self,
        hours: int = 1,
        limit: int = 50,
    ) -> list[AuditLog]:
        """查找失败的操作记录

        Args:
            hours: 最近多少小时
            limit: 返回数量限制

        Returns:
            审计日志列表
        """
        pass

    @abstractmethod
    async def find_with_count_by_filter(
        self,
        filter_obj: AuditLogFilter,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[AuditLog], int]:
        """根据过滤条件查找审计日志并返回总数

        Args:
            filter_obj: 过滤条件
            limit: 返回数量限制
            offset: 偏移量
            order_by: 排序字段
            order_desc: 是否降序

        Returns:
            审计日志列表和总数的元组
        """
        pass

    @abstractmethod
    async def find_by_ids(self, log_ids: list[UUID]) -> list[AuditLog]:
        """根据ID列表批量查找审计日志

        Args:
            log_ids: 审计日志ID列表

        Returns:
            审计日志列表
        """
        pass

    @abstractmethod
    async def get_statistics(
        self,
        start_time: datetime | None = None,
        include_user_stats: bool = False,
        include_action_stats: bool = False,
    ) -> dict:
        """获取审计日志统计信息

        Args:
            start_time: 统计开始时间
            include_user_stats: 是否包含用户统计
            include_action_stats: 是否包含操作统计

        Returns:
            统计信息字典
        """
        pass
