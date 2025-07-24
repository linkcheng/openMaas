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

"""SM2加密服务测试"""

import pytest
from src.shared.infrastructure.crypto_service import SM2CryptoService, get_sm2_service


class TestSM2CryptoService:
    """SM2加密服务测试类"""

    def test_encrypt_decrypt(self):
        """测试基本加密解密功能"""
        sm2_service = get_sm2_service()
        
        # 测试数据
        test_texts = [
            "hello world",
            "中文测试",
            "123456",
            "special@#$%^&*()chars",
            "",  # 空字符串
        ]
        
        for text in test_texts:
            # 加密
            encrypted = sm2_service.encrypt(text)
            assert isinstance(encrypted, str)
            
            # 空字符串应该直接返回空字符串，不进行加密
            if text == "":
                assert encrypted == ""
            else:
                assert len(encrypted) > 0
            
            # 解密
            decrypted = sm2_service.decrypt(encrypted)
            assert decrypted == text

    def test_decrypt_invalid_input(self):
        """测试解密无效输入"""
        sm2_service = get_sm2_service()
        
        # 测试无效的十六进制字符串
        with pytest.raises(ValueError, match="密文不是有效的十六进制格式"):
            sm2_service.decrypt("invalid_hex")
        
        # 测试非字符串输入
        with pytest.raises(ValueError, match="密文必须是字符串格式"):
            sm2_service.decrypt(123)  # type: ignore
        
        # 测试无效的密文长度（太短）
        with pytest.raises(ValueError, match="解密失败"):
            sm2_service.decrypt("abcd")

    def test_encrypt_invalid_input(self):
        """测试加密无效输入"""
        sm2_service = get_sm2_service()
        
        # 测试非字符串输入
        with pytest.raises(ValueError, match="明文必须是字符串格式"):
            sm2_service.encrypt(123)  # type: ignore

    def test_get_key_info(self):
        """测试获取密钥信息"""
        sm2_service = get_sm2_service()
        key_info = sm2_service.get_key_info()
        
        assert "public_key" in key_info
        assert "algorithm" in key_info
        assert "key_length" in key_info
        assert key_info["algorithm"] == "SM2"
        assert key_info["key_length"] == "256"
        assert isinstance(key_info["public_key"], str)
        assert len(key_info["public_key"]) > 0

    def test_singleton_pattern(self):
        """测试单例模式"""
        service1 = get_sm2_service()
        service2 = get_sm2_service()
        
        assert service1 is service2