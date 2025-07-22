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

"""配置设置 - 提供配置实例管理"""


from src.config.schemas import Settings

# 全局配置实例
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """获取配置实例(单例模式)"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def reload_settings() -> Settings:
    """重新加载配置"""
    global _settings_instance
    _settings_instance = None
    return get_settings()


# 全局配置实例
settings = get_settings()


# 兼容性函数
def get_database_url() -> str:
    """获取数据库连接URL"""
    return settings.get_database_url()


def get_redis_url() -> str:
    """获取Redis连接URL"""
    return settings.get_redis_url()


def get_jwt_secret_key() -> str:
    """获取JWT密钥"""
    return settings.get_jwt_secret_key()
