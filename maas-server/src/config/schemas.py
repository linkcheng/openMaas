"""配置数据模型 - 定义配置的结构和验证规则"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.env_utils import get_env_file_path


class DatabaseConfig(BaseSettings):
    """数据库配置"""

    url: str = Field(
        default="postgresql+asyncpg://maas:maas@localhost:5432/maas",
        description="异步数据库连接URL"
    )
    url_sync: str = Field(
        default="postgresql://maas:maas@localhost:5432/maas",
        description="同步数据库连接URL(用于Alembic)"
    )

    model_config = SettingsConfigDict(
        env_file=get_env_file_path(),
        env_file_encoding="utf-8",
        env_prefix="MAAS_DATABASE_",
        case_sensitive=False,
        extra="ignore",
    )


class RedisConfig(BaseSettings):
    """Redis配置"""

    url: str = Field(
        default="redis://:password@localhost:6379/0",
        description="Redis连接URL"
    )

    model_config = SettingsConfigDict(
        env_file=get_env_file_path(),
        env_file_encoding="utf-8",
        env_prefix="MAAS_REDIS_",
        case_sensitive=False,
        extra="ignore",
    )


class SecurityConfig(BaseSettings):
    """安全配置"""

    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT密钥"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    frontend_url: str = "http://localhost:3000"

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        """验证JWT密钥强度"""
        if len(v) < 32:
            raise ValueError("JWT密钥长度至少需要32个字符")
        return v

    model_config = SettingsConfigDict(
        env_file=get_env_file_path(),
        env_file_encoding="utf-8",
        env_prefix="MAAS_SECURITY_",
        case_sensitive=False,
        extra="ignore",
    )


class AppConfig(BaseSettings):
    """应用配置"""

    name: str = "MaaS Platform"
    version: str = "1.0.0"
    description: str = "Model-as-a-Service Platform"

    model_config = SettingsConfigDict(
        env_file=get_env_file_path(),
        env_file_encoding="utf-8",
        env_prefix="MAAS_APP_",
        case_sensitive=False,
        extra="ignore",
    )


class ServerConfig(BaseSettings):
    """服务器配置"""

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=get_env_file_path(),
        env_file_encoding="utf-8",
        env_prefix="MAAS_SERVER_",
        case_sensitive=False,
        extra="ignore",
    )


class Settings(BaseSettings):
    """主配置类 - 整合所有配置模块"""

    # 环境配置
    environment: str = Field(
        default="development",
        description="运行环境(development/testing/production)"
    )

    # 文件存储配置
    upload_max_size: int = 1024 * 1024 * 1024  # 1GB
    upload_dir: str = "uploads"

    # 监控配置
    enable_metrics: bool = True
    metrics_port: int = 9090

    # 日志配置
    log_level: str = "INFO"
    log_file: str | None = None

    # 配置模块
    app: AppConfig = Field(default_factory=AppConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # 校验器
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """校验环境配置"""
        allowed_envs = ["development", "testing", "production"]
        if v not in allowed_envs:
            raise ValueError(f"environment必须是{allowed_envs}中的一个")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """校验日志级别"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"log_level必须是{allowed_levels}中的一个")
        return v.upper()

    # Pydantic v2 配置
    model_config = SettingsConfigDict(
        env_file=get_env_file_path(),
        env_file_encoding="utf-8",
        env_prefix="MAAS_",
        case_sensitive=False,
        extra="ignore",
    )

    # 便捷方法
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.environment == "development"

    def is_testing(self) -> bool:
        """判断是否为测试环境"""
        return self.environment == "testing"

    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return self.database.url

    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        return self.redis.url

    def get_jwt_secret_key(self) -> str:
        """获取JWT密钥"""
        return self.security.jwt_secret_key

