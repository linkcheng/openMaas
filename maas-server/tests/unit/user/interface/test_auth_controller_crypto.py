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

"""认证控制器公钥接口单元测试"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from user.interface.auth_controller import get_public_key
from shared.infrastructure.crypto_service import SM2CryptoService


class TestAuthControllerCrypto:
    """认证控制器加密相关测试"""

    @pytest.mark.asyncio
    async def test_get_public_key_success(self):
        """测试获取公钥成功"""
        mock_service = Mock(spec=SM2CryptoService)
        mock_key_info = {
            "public_key": "test_public_key_hex",
            "algorithm": "SM2",
            "key_length": "256"
        }
        mock_service.get_key_info.return_value = mock_key_info
        
        with patch('user.interface.auth_controller.get_sm2_service', return_value=mock_service):
            response = await get_public_key()
            
            assert response.success is True
            assert response.data == mock_key_info
            assert response.message == "获取公钥成功"
            mock_service.get_key_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_public_key_service_error(self):
        """测试获取公钥时服务异常"""
        mock_service = Mock(spec=SM2CryptoService)
        mock_service.get_key_info.side_effect = Exception("Service error")
        
        with patch('user.interface.auth_controller.get_sm2_service', return_value=mock_service):
            with pytest.raises(HTTPException) as exc_info:
                await get_public_key()
            
            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "获取公钥失败"