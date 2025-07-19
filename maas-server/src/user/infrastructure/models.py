"""用户基础设施层 - ORM模型"""

from datetime import UTC, datetime
from typing import Optional
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

    # 关系
    roles: Mapped[list["RoleORM"]] = relationship(
        "RoleORM",
        secondary="user_roles",
        primaryjoin="UserORM.user_id == UserRoleORM.user_id",
        secondaryjoin="RoleORM.role_id == UserRoleORM.role_id",
        back_populates="users",
        lazy="selectin"
    )
    api_keys: Mapped[list["ApiKeyORM"]] = relationship(
        "ApiKeyORM",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    quota: Mapped[Optional["UserQuotaORM"]] = relationship(
        "UserQuotaORM",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
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


class ApiKeyORM(Base):
    """API密钥ORM模型"""
    __tablename__ = "api_keys"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'revoked')",
            name="ck_api_key_status"
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at > created_at",
            name="ck_api_key_expiry"
        ),
        UniqueConstraint("api_key_id", name="uq_api_key_id"),
        Index("ix_api_keys_user_id", "user_id"),
        Index("ix_api_keys_key_hash", "key_hash"),
        Index("ix_api_keys_status", "status"),
        Index("ix_api_keys_expires_at", "expires_at"),
    )

    # 自增主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    # 业务ID
    api_key_id: Mapped[UUID] = mapped_column(
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
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    key_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    permissions: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # 关系
    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="api_keys"
    )


class UserQuotaORM(Base):
    """用户配额ORM模型"""
    __tablename__ = "user_quotas"
    __table_args__ = (
        CheckConstraint("api_calls_limit >= 0", name="ck_api_calls_limit_positive"),
        CheckConstraint("api_calls_used >= 0", name="ck_api_calls_used_positive"),
        CheckConstraint("storage_limit >= 0", name="ck_storage_limit_positive"),
        CheckConstraint("storage_used >= 0", name="ck_storage_used_positive"),
        CheckConstraint("compute_hours_limit >= 0", name="ck_compute_hours_limit_positive"),
        CheckConstraint("compute_hours_used >= 0", name="ck_compute_hours_used_positive"),
        CheckConstraint("api_calls_used <= api_calls_limit", name="ck_api_calls_within_limit"),
        CheckConstraint("storage_used <= storage_limit", name="ck_storage_within_limit"),
        CheckConstraint("compute_hours_used <= compute_hours_limit", name="ck_compute_hours_within_limit"),
        UniqueConstraint("user_quota_id", name="uq_user_quota_id"),
        UniqueConstraint("user_id", name="uq_user_quota_user_id"),
        Index("ix_user_quotas_reset_at", "reset_at"),
    )

    # 自增主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    # 业务ID
    user_quota_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid7
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    api_calls_limit: Mapped[int] = mapped_column(
        Integer,
        default=1000,
        nullable=False
    )
    api_calls_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    storage_limit: Mapped[int] = mapped_column(
        Integer,
        default=1073741824,  # 1GB
        nullable=False
    )
    storage_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    compute_hours_limit: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False
    )
    compute_hours_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        ),
        nullable=False
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
    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="quota"
    )
