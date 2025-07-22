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

# pylint: disable=import-outside-toplevel
"""配置工具类 - 提供配置加密、验证、健康检查等功能"""

import os
import secrets
from base64 import b64decode, b64encode
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.schemas import Settings
from config.settings import get_settings


class ConfigSecurity:
    """配置安全管理类"""

    def __init__(self, master_key: str | None = None):
        """初始化配置安全管理器

        Args:
            master_key: 主密钥, 如果为None则从环境变量获取
        """
        self.master_key = master_key or os.getenv("MAAS_MASTER_KEY")
        if not self.master_key:
            self.master_key = self._generate_master_key()

    def _generate_master_key(self) -> str:
        """生成主密钥"""
        return secrets.token_urlsafe(32)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    def encrypt_value(self, value: str) -> str:
        """加密配置值"""
        if not value:
            return value

        salt = os.urandom(16)
        key = self._derive_key(self.master_key, salt)
        f = Fernet(b64encode(key))
        encrypted = f.encrypt(value.encode())

        # 返回格式: salt + encrypted_data (base64编码)
        return b64encode(salt + encrypted).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        """解密配置值"""
        if not encrypted_value:
            return encrypted_value

        try:
            data = b64decode(encrypted_value.encode())
            salt = data[:16]
            encrypted_data = data[16:]

            key = self._derive_key(self.master_key, salt)
            f = Fernet(b64encode(key))
            decrypted = f.decrypt(encrypted_data)

            return decrypted.decode()
        except Exception:
            # 如果解密失败, 返回原值(可能是明文)
            return encrypted_value

    def is_encrypted(self, value: str) -> bool:
        """判断值是否已加密"""
        if not value:
            return False

        try:
            b64decode(value.encode())
            return True
        except Exception:
            return False

    def mask_sensitive_value(self, value: str, mask_char: str = "*") -> str:
        """遮蔽敏感信息"""
        if not value or len(value) < 4:
            return mask_char * 8

        # 显示前2位和后2位
        return value[:2] + mask_char * (len(value) - 4) + value[-2:]


class ConfigValidator:
    """配置验证器"""

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_production_config(self) -> list[str]:
        """验证生产环境配置"""
        errors = []

        if not self.settings.is_production():
            return errors

        # 检查JWT密钥
        if len(self.settings.security.jwt_secret_key) < 32:
            errors.append("生产环境JWT密钥长度必须至少32个字符")

        if self.settings.security.jwt_secret_key == "your-secret-key-change-in-production":
            errors.append("生产环境必须更改默认JWT密钥")

        # 检查调试模式
        if self.settings.server.debug:
            errors.append("生产环境不能启用调试模式")

        # 检查CORS配置
        if "localhost" in str(self.settings.security.cors_origins):
            errors.append("生产环境CORS配置不应包含localhost")

        return errors

    def validate_database_config(self) -> list[str]:
        """验证数据库配置"""
        errors = []

        # 检查数据库URL格式
        db_url = self.settings.database.url
        if not db_url.startswith(("postgresql://", "postgresql+asyncpg://")):
            errors.append("数据库URL格式不正确")

        # 检查同步和异步URL一致性
        async_url = self.settings.database.url
        sync_url = self.settings.database.url_sync

        if "postgresql+asyncpg" in async_url and "postgresql://" not in sync_url:
            errors.append("同步数据库URL应该对应异步URL")

        return errors

    def validate_redis_config(self) -> list[str]:
        """验证Redis配置"""
        errors = []

        redis_url = self.settings.redis.url
        if not redis_url.startswith("redis://"):
            errors.append("Redis URL格式不正确")

        return errors

    def validate_all(self) -> dict[str, list[str]]:
        """验证所有配置"""
        results = {
            "production": self.validate_production_config(),
            "database": self.validate_database_config(),
            "redis": self.validate_redis_config(),
        }

        return {k: v for k, v in results.items() if v}


class ConfigHealthChecker:
    """配置健康检查器"""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def check_database_connection(self) -> bool:
        """检查数据库连接"""
        try:
            import asyncpg

            # 解析数据库URL
            url = self.settings.database.url
            url = url.replace("postgresql+asyncpg://", "postgresql://")

            conn = await asyncpg.connect(url)
            await conn.execute("SELECT 1")
            await conn.close()
            return True
        except Exception:
            return False

    async def check_redis_connection(self) -> bool:
        """检查Redis连接"""
        try:
            import redis.asyncio as redis

            r = redis.from_url(self.settings.redis.url)
            await r.ping()
            await r.close()
            return True
        except Exception:
            return False

    async def check_all_connections(self) -> dict[str, bool]:
        """检查所有连接"""
        results = {
            "database": await self.check_database_connection(),
            "redis": await self.check_redis_connection(),
        }

        return results


def get_config_summary(settings: Settings, mask_secrets: bool = True) -> dict[str, Any]:
    """获取配置摘要"""
    security = ConfigSecurity()

    summary = {
        "environment": settings.environment,
        "debug": settings.server.debug,
        "app_name": settings.app.name,
        "app_version": settings.app.version,
        "database": {
            "url": security.mask_sensitive_value(settings.database.url) if mask_secrets else settings.database.url,
        },
        "redis": {
            "url": security.mask_sensitive_value(settings.redis.url) if mask_secrets else settings.redis.url,
        },
        "security": {
            "jwt_secret_key": security.mask_sensitive_value(settings.security.jwt_secret_key) if mask_secrets else settings.security.jwt_secret_key,
            "cors_origins": settings.security.cors_origins,
        },
    }

    return summary


def validate_config() -> dict[str, Any]:
    """验证当前配置"""
    settings = get_settings()
    validator = ConfigValidator(settings)

    return {
        "environment": settings.environment,
        "validation_results": validator.validate_all(),
        "config_summary": get_config_summary(settings, mask_secrets=True)
    }
