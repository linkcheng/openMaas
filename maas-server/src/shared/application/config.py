"""共享应用层 - 配置管理"""


from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = "MAAS Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # 数据库配置
    database_url: str = Field(
        default="postgresql+asyncpg://maas:maas@localhost:5432/maas",
        description="异步数据库连接URL"
    )
    database_url_sync: str = Field(
        default="postgresql://maas:maas@localhost:5432/maas",
        description="同步数据库连接URL（用于Alembic）"
    )

    # Redis配置
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis连接URL"
    )

    # Milvus配置
    milvus_host: str = "localhost"
    milvus_port: int = 19530

    # JWT配置
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT密钥"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # 安全配置
    bcrypt_rounds: int = 12
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    frontend_url: str = "http://localhost:3000"

    # 文件存储配置
    upload_max_size: int = 1024 * 1024 * 1024  # 1GB
    upload_dir: str = "uploads"

    # 外部服务配置
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"

    # 邮件配置
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True

    # 监控配置
    enable_metrics: bool = True
    metrics_port: int = 9090

    # 日志配置
    log_level: str = "INFO"
    log_file: str | None = None

    class Config:
        env_file = ".env"
        env_prefix = "MAAS_"
        case_sensitive = False


# 全局配置实例
settings = Settings()
