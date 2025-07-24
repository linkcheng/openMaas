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

"""审计日志基础设施层 - ORM模型"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid_extensions import uuid7

from shared.infrastructure.database import Base


class AuditLogORM(Base):
    """审计日志ORM模型"""
    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint(
            "result IN ('success', 'failure')",
            name="ck_audit_log_result"
        ),
        CheckConstraint(
            "length(action) >= 1",
            name="ck_audit_log_action_not_empty"
        ),
        CheckConstraint(
            "length(description) >= 1",
            name="ck_audit_log_description_not_empty"
        ),
        UniqueConstraint("audit_log_id", name="uq_audit_log_id"),
        # 单列索引
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_resource_type", "resource_type"),
        Index("ix_audit_logs_resource_id", "resource_id"),
        Index("ix_audit_logs_result", "result"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_ip_address", "ip_address"),
        # 复合索引 - 优化常见查询
        Index("ix_audit_logs_user_created", "user_id", "created_at"),
        Index("ix_audit_logs_action_created", "action", "created_at"),
        Index("ix_audit_logs_resource_created", "resource_type", "resource_id", "created_at"),
        Index("ix_audit_logs_result_created", "result", "created_at"),
        # 覆盖索引 - 优化统计查询
        Index("ix_audit_logs_stats", "created_at", "result", "action", "user_id"),
    )

    # 自增主键
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # 业务ID
    audit_log_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid7
    )

    # 操作用户信息
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,  # 系统操作可以为空
        comment="操作用户ID，系统操作时为空"
    )
    username: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="操作用户名快照"
    )

    # 操作信息
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="操作类型，如login、logout、create_user等"
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="资源类型，如user、model、dataset等"
    )
    resource_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="资源ID"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="操作描述"
    )

    # 请求信息
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # IPv6最大长度
        nullable=True,
        comment="客户端IP地址"
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="用户代理字符串"
    )
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="请求追踪ID"
    )

    # 操作结果
    result: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="操作结果：success或failure"
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="错误信息，操作失败时记录"
    )

    # 扩展信息
    extra_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="额外的元数据信息"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="记录创建时间"
    )
