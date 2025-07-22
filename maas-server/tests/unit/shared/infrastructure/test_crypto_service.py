"""SM2加密服务单元测试"""

import pytest
import tempfile
import pathlib
from unittest.mock import patch, MagicMock

from shared.infrastructure.crypto_service import SM2CryptoService, get_sm2_service


class TestSM2CryptoService:
    """SM2加密服务测试"""

    def test_init_generates_key_pair_if_not_exists(self):
        """测试初始化时如果密钥文件不存在则生成密钥对"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('shared.infrastructure.crypto_service.generate_keypair') as mock_generate:
                mock_generate.return_value = (b'\x01' * 32, b'\x02' * 32)
                
                service = SM2CryptoService(keys_dir=temp_dir)
                
                # 检查密钥文件是否创建
                assert service.private_key_file.exists()
                assert service.public_key_file.exists()
                
                # 检查密钥内容（转换为hex格式）
                expected_private = ('01' * 32)
                expected_public = '04' + ('02' * 32)
                assert service._private_key == expected_private
                assert service._public_key == expected_public

    def test_init_loads_existing_keys(self):
        """测试初始化时如果密钥文件存在则加载密钥"""
        with tempfile.TemporaryDirectory() as temp_dir:
            keys_dir = pathlib.Path(temp_dir)
            
            # 创建测试密钥文件
            private_key_file = keys_dir / "sm2_private_key.pem"
            public_key_file = keys_dir / "sm2_public_key.pem"
            
            private_key_file.write_text("test_private_key")
            public_key_file.write_text("test_public_key")
            
            service = SM2CryptoService(keys_dir=temp_dir)
            
            assert service._private_key == "test_private_key"
            assert service._public_key == "test_public_key"

    def test_public_key_property(self):
        """测试公钥属性"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('shared.infrastructure.crypto_service.generate_keypair') as mock_generate:
                mock_generate.return_value = (b'\x01' * 32, b'\x02' * 32)
                service = SM2CryptoService(keys_dir=temp_dir)
                service._public_key = 'test_public_key'
                
                assert service.public_key == 'test_public_key'

    def test_public_key_property_not_initialized(self):
        """测试公钥未初始化时抛出异常"""
        service = SM2CryptoService.__new__(SM2CryptoService)
        service._public_key = None
        
        with pytest.raises(ValueError, match="公钥未初始化"):
            _ = service.public_key

    def test_encrypt_success(self):
        """测试加密成功"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('shared.infrastructure.crypto_service.generate_keypair') as mock_generate:
                with patch('shared.infrastructure.crypto_service.Encrypt') as mock_encrypt:
                    mock_generate.return_value = (b'\x01' * 32, b'\x02' * 32)
                    mock_encrypt.return_value = 'abcdef123456'  # hex string
                    
                    service = SM2CryptoService(keys_dir=temp_dir)
                    
                    result = service.encrypt("test_password")
                    
                    # 检查返回Base64编码的结果
                    import base64
                    expected = base64.b64encode(bytes.fromhex('abcdef123456')).decode('utf-8')
                    assert result == expected
                    
                    # 检查调用参数
                    mock_encrypt.assert_called_once_with("test_password", bytes.fromhex('02' * 32), 64, Hexstr=0, encoding='utf-8')

    def test_encrypt_not_initialized(self):
        """测试加密器未初始化时抛出异常"""
        service = SM2CryptoService.__new__(SM2CryptoService)
        service._private_key = None
        service._public_key = None
        
        with pytest.raises(ValueError, match="密钥未初始化"):
            service.encrypt("test")

    def test_decrypt_success(self):
        """测试解密成功"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('shared.infrastructure.crypto_service.generate_keypair') as mock_generate:
                with patch('shared.infrastructure.crypto_service.Decrypt') as mock_decrypt:
                    mock_generate.return_value = (b'\x01' * 32, b'\x02' * 32)
                    mock_decrypt.return_value = "test_password"  # 直接返回字符串
                    
                    service = SM2CryptoService(keys_dir=temp_dir)
                    
                    # Base64编码的密文
                    import base64
                    ciphertext = base64.b64encode(b'encrypted_data').decode('utf-8')
                    
                    result = service.decrypt(ciphertext)
                    
                    assert result == "test_password"
                    # 检查调用参数：hex字符串、私钥bytes、len_para=64
                    expected_hex = b'encrypted_data'.hex()
                    mock_decrypt.assert_called_once_with(expected_hex, bytes.fromhex('01' * 32), 64, Hexstr=1, encoding='utf-8')

    def test_decrypt_not_initialized(self):
        """测试解密器未初始化时抛出异常"""
        service = SM2CryptoService.__new__(SM2CryptoService)
        service._private_key = None
        service._public_key = None
        
        with pytest.raises(ValueError, match="密钥未初始化"):
            service.decrypt("test")

    def test_decrypt_invalid_base64(self):
        """测试解密时Base64解码失败的情况"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('shared.infrastructure.crypto_service.generate_keypair') as mock_generate:
                mock_generate.return_value = (b'\x01' * 32, b'\x02' * 32)
                
                service = SM2CryptoService(keys_dir=temp_dir)
                
                # 传入无效的Base64字符串
                invalid_base64 = "不是Base64字符串!!!"
                
                with pytest.raises(ValueError, match="Base64解码失败"):
                    service.decrypt(invalid_base64)

    def test_get_key_info(self):
        """测试获取密钥信息"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('shared.infrastructure.crypto_service.generate_keypair') as mock_generate:
                mock_generate.return_value = (b'\x01' * 32, b'\x02' * 32)
                service = SM2CryptoService(keys_dir=temp_dir)
                service._public_key = "test_public_key_hex"
                
                key_info = service.get_key_info()
                
                expected = {
                    "public_key": "test_public_key_hex",
                    "algorithm": "SM2",
                    "key_length": "256"
                }
                assert key_info == expected

    def test_encrypt_decrypt_round_trip(self):
        """测试加密解密往返"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('shared.infrastructure.crypto_service.generate_keypair') as mock_generate:
                with patch('shared.infrastructure.crypto_service.Encrypt') as mock_encrypt:
                    with patch('shared.infrastructure.crypto_service.Decrypt') as mock_decrypt:
                        mock_generate.return_value = (b'\x01' * 32, b'\x02' * 32)
                        original_text = "test_password_123"
                        encrypted_hex = 'abcdef123456'
                        
                        mock_encrypt.return_value = encrypted_hex
                        mock_decrypt.return_value = original_text
                        
                        service = SM2CryptoService(keys_dir=temp_dir)
                        
                        # 加密
                        ciphertext = service.encrypt(original_text)
                        
                        # 解密
                        decrypted = service.decrypt(ciphertext)
                        
                        assert decrypted == original_text


class TestSM2ServiceSingleton:
    """SM2服务单例测试"""
    
    def test_get_sm2_service_singleton(self):
        """测试获取SM2服务单例"""
        # 清理全局变量
        import shared.infrastructure.crypto_service
        shared.infrastructure.crypto_service._sm2_service = None
        
        with patch('shared.infrastructure.crypto_service.generate_keypair') as mock_generate:
            mock_generate.return_value = (b'\x01' * 32, b'\x02' * 32)
            service1 = get_sm2_service()
            service2 = get_sm2_service()
            
            # 应该是同一个实例
            assert service1 is service2
            assert isinstance(service1, SM2CryptoService)