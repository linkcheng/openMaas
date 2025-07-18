"""共享应用层测试 - 配置测试"""

import pytest
import os
from unittest.mock import patch

from src.shared.application.config import Settings


class TestSettings:
    """配置测试"""
    
    def test_default_settings(self):
        """测试默认配置"""
        settings = Settings()
        
        assert settings.app_name == "MAAS Platform"
        assert settings.app_version == "1.0.0"
        assert settings.debug == False
        assert settings.environment == "development"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.reload == False
    
    def test_env_prefix(self):
        """测试环境变量前缀"""
        with patch.dict(os.environ, {
            "MAAS_APP_NAME": "Test App",
            "MAAS_DEBUG": "true",
            "MAAS_PORT": "9000"
        }):
            settings = Settings()
            
            assert settings.app_name == "Test App"
            assert settings.debug == True
            assert settings.port == 9000
    
    def test_database_urls(self):
        """测试数据库URL配置"""
        settings = Settings()
        
        assert "postgresql+asyncpg://" in settings.database_url
        assert "postgresql://" in settings.database_url_sync
    
    def test_jwt_config(self):
        """测试JWT配置"""
        settings = Settings()
        
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_access_token_expire_minutes == 30
        assert settings.jwt_refresh_token_expire_days == 7
        assert len(settings.jwt_secret_key) > 0
    
    def test_cors_origins(self):
        """测试CORS配置"""
        settings = Settings()
        
        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) > 0
    
    def test_file_upload_config(self):
        """测试文件上传配置"""
        settings = Settings()
        
        assert settings.upload_max_size > 0
        assert settings.upload_dir == "uploads"
    
    def test_environment_specific_config(self):
        """测试环境特定配置"""
        # 测试开发环境
        with patch.dict(os.environ, {"MAAS_ENVIRONMENT": "development"}):
            settings = Settings()
            assert settings.environment == "development"
        
        # 测试生产环境
        with patch.dict(os.environ, {"MAAS_ENVIRONMENT": "production"}):
            settings = Settings()
            assert settings.environment == "production"
        
        # 测试测试环境
        with patch.dict(os.environ, {"MAAS_ENVIRONMENT": "testing"}):
            settings = Settings()
            assert settings.environment == "testing"