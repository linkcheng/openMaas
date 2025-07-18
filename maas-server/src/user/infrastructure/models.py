"""用户基础设施层 - ORM模型"""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...shared.infrastructure.database import Base

# 用户角色关联表
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column("granted_by", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("granted_at", DateTime(timezone=True), server_default=func.now())
)


class UserORM(Base):
    """用户ORM模型"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # 用户档案
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(Text)
    organization = Column(String(255))
    bio = Column(Text)

    # 状态和验证
    status = Column(String(20), default="active", nullable=False, index=True)
    email_verified = Column(Boolean, default=False, nullable=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # 关系
    roles = relationship("RoleORM", secondary=user_roles, back_populates="users")
    api_keys = relationship("ApiKeyORM", back_populates="user", cascade="all, delete-orphan")
    quota = relationship("UserQuotaORM", back_populates="user", uselist=False, cascade="all, delete-orphan")


class RoleORM(Base):
    """角色ORM模型"""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    users = relationship("UserORM", secondary=user_roles, back_populates="roles")


class ApiKeyORM(Base):
    """API密钥ORM模型"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    permissions = Column(JSON, default=list)

    expires_at = Column(DateTime(timezone=True))
    last_used_at = Column(DateTime(timezone=True))
    status = Column(String(20), default="active", nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("UserORM", back_populates="api_keys")


class UserQuotaORM(Base):
    """用户配额ORM模型"""
    __tablename__ = "user_quotas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    api_calls_limit = Column(Integer, default=1000)
    api_calls_used = Column(Integer, default=0)
    storage_limit = Column(Integer, default=1073741824)  # 1GB
    storage_used = Column(Integer, default=0)
    compute_hours_limit = Column(Integer, default=10)
    compute_hours_used = Column(Integer, default=0)

    reset_at = Column(DateTime(timezone=True), default=lambda: datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("UserORM", back_populates="quota")
