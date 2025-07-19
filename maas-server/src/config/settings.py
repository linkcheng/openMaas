"""配置设置 - 提供配置实例管理"""


from config.schemas import Settings

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
