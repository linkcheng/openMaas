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

"""用户基础设施层 - ORM模型"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_extensions import uuid7

from shared.infrastructure.database import Base


class UserRoleORM(Base):
    """用户角色关联ORM模型"""
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        UniqueConstraint("user_role_id", name="uq_user_role_id"),
        Index("ix_user_roles_user_id", "user_id"),
        Index("ix_user_roles_role_id", "role_id"),
    )

    # 自增主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    # 业务ID
    user_role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid7
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.role_id", ondelete="CASCADE"),
        nullable=False
    )
    granted_by_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class UserORM(Base):
    """用户ORM模型"""
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended')",
            name="ck_user_status"
        ),
        CheckConstraint("length(username) >= 3", name="ck_username_min_length"),
        CheckConstraint("length(first_name) >= 1", name="ck_first_name_not_empty"),
        CheckConstraint("length(last_name) >= 1", name="ck_last_name_not_empty"),
        UniqueConstraint("user_id", name="uq_user_id"),
        Index("ix_users_username", "username"),
        Index("ix_users_email", "email"),
        Index("ix_users_status", "status"),
        Index("ix_users_created_at", "created_at"),
    )

    # 自增主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    # 业务ID
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid7
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # 用户档案
    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    organization: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # 状态和验证
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Token版本控制
    key_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        index=True
    )

    # 关系
    roles: Mapped[list["RoleORM"]] = relationship(
        "RoleORM",
        secondary="user_roles",
        primaryjoin="UserORM.user_id == UserRoleORM.user_id",
        secondaryjoin="RoleORM.role_id == UserRoleORM.role_id",
        back_populates="users",
        lazy="selectin"
    )


class RoleORM(Base):
    """角色ORM模型"""
    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint(
            "name IN ('admin', 'developer', 'user')",
            name="ck_role_name"
        ),
        UniqueConstraint("role_id", name="uq_role_id"),
        Index("ix_roles_name", "name"),
    )

    # 自增主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    # 业务ID
    role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid7
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    permissions: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # 关系
    users: Mapped[list["UserORM"]] = relationship(
        "UserORM",
        secondary="user_roles",
        primaryjoin="RoleORM.role_id == UserRoleORM.role_id",
        secondaryjoin="UserORM.user_id == UserRoleORM.user_id",
        back_populates="roles",
        lazy="selectin"
    )
