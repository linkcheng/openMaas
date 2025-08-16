import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.infrastructure.database import Base


class ProviderORM(Base):
    """模型供应商配置表"""

    __tablename__ = "providers"
    __table_args__ = (
        PrimaryKeyConstraint("provider_id", name="providers_pkey"),
        Index("idx_provider_type", "provider_type"),
        Index("idx_provider_name", "provider_name"),
    )

    provider_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="供应商ID")
    provider_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="供应商名称")
    provider_type: Mapped[str] = mapped_column(String(64), nullable=False, comment="供应商类型")
    display_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="显示名称")
    description: Mapped[str] = mapped_column(Text, nullable=True, comment="描述信息")
    base_url: Mapped[str] = mapped_column(String(512), nullable=False, comment="基础URL")
    api_key: Mapped[str] = mapped_column(String(512), nullable=True, comment="API密钥(加密存储)")
    additional_config: Mapped[dict] = mapped_column(JSON, nullable=True, comment="额外配置参数")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1", comment="是否启用")
    created_by: Mapped[str] = mapped_column(String(64), nullable=False, comment="创建人")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False,
                                                         server_default=func.current_timestamp(), comment="创建时间")
    updated_by: Mapped[str] = mapped_column(String(64), nullable=False, comment="更新人")
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False,
                                                         server_default=func.current_timestamp(), comment="更新时间")
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0", comment="是否删除")

    # 关联关系 - 一对多关联到供应商模型配置表
    model_configs: Mapped[list["ModelConfigORM"]] = relationship(
        "ModelConfigORM",
        back_populates="provider",
        cascade="all, delete-orphan"
    )


class ModelConfigORM(Base):
    """供应商模型配置表"""

    __tablename__ = "model_configs"
    __table_args__ = (
        PrimaryKeyConstraint("config_id", name="provider_model_configs_pkey"),
        Index("idx_provider_id", "provider_id"),
        Index("idx_model_type", "model_type"),
        Index("idx_model_name", "model_name"),
        Index("uk_provider_model", "provider_id", "model_name", "is_delete", unique=True),
    )

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="配置ID")
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("providers.provider_id"),
                                           nullable=False, comment="供应商ID")
    model_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="模型名称")
    model_display_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="模型显示名称")
    model_type: Mapped[str] = mapped_column(String(64), nullable=False, comment="模型类型")
    model_params: Mapped[dict] = mapped_column(JSON, nullable=True, comment="模型参数配置")
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=True, server_default="4096", comment="最大token数")
    max_input_tokens: Mapped[int] = mapped_column(Integer, nullable=True, server_default="3072", comment="最大输入token数")
    temperature: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=True, server_default="0.70", comment="温度参数")
    pricing_config: Mapped[dict] = mapped_column(JSON, nullable=True, comment="定价配置")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1", comment="是否启用")
    created_by: Mapped[str] = mapped_column(String(64), nullable=False, comment="创建人")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False,
                                                         server_default=func.current_timestamp(), comment="创建时间")
    updated_by: Mapped[str] = mapped_column(String(64), nullable=False, comment="更新人")
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False,
                                                         server_default=func.current_timestamp(), comment="更新时间")
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0", comment="是否删除")

    # 关联关系 - 多对一关联到供应商表
    provider: Mapped["ProviderORM"] = relationship(
        "ProviderORM",
        back_populates="model_configs"
    )
