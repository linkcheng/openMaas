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

"""国密SM2加密服务"""

import base64
import pathlib

from loguru import logger
from pysmx.SM2 import generate_keypair, Encrypt, Decrypt


class SM2CryptoService:
    """SM2加密解密服务"""

    def __init__(self, keys_dir: str = "keys"):
        """
        初始化SM2密钥对
        
        Args:
            keys_dir: 密钥文件存储目录
        """
        self.len_para = 64
        self.keys_dir = pathlib.Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True)

        self.private_key_file = self.keys_dir / "sm2_private_key.pem"
        self.public_key_file = self.keys_dir / "sm2_public_key.pem"

        self._private_key: bytes | None = None
        self._public_key: bytes | None = None

        self._load_or_generate_keys()

    def _load_or_generate_keys(self) -> None:
        """加载或生成SM2密钥对"""
        try:
            if self.private_key_file.exists() and self.public_key_file.exists():
                # 从文件加载密钥
                self._load_keys_from_files()
                logger.info("SM2密钥对从文件加载成功")
            else:
                # 生成新的密钥对
                self._generate_and_save_keys()
                logger.info("SM2密钥对生成并保存成功")

        except Exception as e:
            logger.error(f"SM2密钥对初始化失败: {e}", exc_info=True)
            raise

    def _load_keys_from_files(self) -> None:
        """从文件加载密钥"""
        try:
            # 读取私钥"
            with open(self.private_key_file, "rb") as f:
                self._private_key = f.read()

            # 读取公钥
            with open(self.public_key_file, "rb") as f:
                self._public_key = f.read()
            logger.info("密钥从文件加载完成")

        except Exception as e:
            logger.error(f"从文件加载密钥失败: {e}")
            raise

    def _generate_and_save_keys(self) -> None:
        """生成并保存SM2密钥对到文件"""
        try:
            # 生成SM2密钥对
            self._public_key, self._private_key = generate_keypair()
            
            # 保存私钥到文件
            with open(self.private_key_file, "wb") as f:
                f.write(self._private_key)

            # 保存公钥到文件
            with open(self.public_key_file, "wb") as f:
                f.write(self._public_key)

            logger.info("SM2密钥对生成并保存到文件")

        except Exception as e:
            logger.error(f"生成并保存密钥失败: {e}")
            raise

    @property
    def public_key(self) -> str:
        """获取公钥"""
        if not self._public_key:
            raise ValueError("公钥未初始化")
        return self._public_key.hex()

    def encrypt(self, plaintext: str) -> str:
        """
        使用SM2公钥加密
        
        Args:
            plaintext: 明文字符串
            
        Returns:
            Base64编码的密文
        """
        if not plaintext:
            return plaintext
    
        if not self._private_key or not self._public_key:
            raise ValueError("密钥未初始化")
        
        try:

            ciphertext = Encrypt(plaintext, self._public_key, self.len_para, 0)

            return ciphertext.hex()

        except Exception as e:
            logger.error(f"SM2加密失败: {e}")
            raise ValueError(f"加密失败: {e}")

    def decrypt(self, ciphertext: str) -> str:
        """
        使用SM2私钥解密
        
        Args:
            ciphertext: Base64编码的密文
            
        Returns:
            解密后的明文字符串
        """
        if not ciphertext:
            return ciphertext
        
        if not self._private_key or not self._public_key:
            raise ValueError("密钥未初始化")
    
        try:
            
            # SM2解密，len_para固定为64
            decrypted_text = Decrypt(ciphertext, self._private_key, 64, 0)
            
            return decrypted_text.decode()

        except Exception as e:
            logger.error(f"SM2解密失败: {e}", exc_info=True)
            raise ValueError(f"解密失败: {e}")

    def get_key_info(self) -> dict[str, str]:
        """获取密钥信息（不包含私钥）"""
        return {
            "public_key": self.public_key,
            "algorithm": "SM2",
            "key_length": "256"
        }


# 全局SM2服务实例
_sm2_service: SM2CryptoService | None = None


def get_sm2_service() -> SM2CryptoService:
    """获取SM2加密服务实例（单例模式）"""
    global _sm2_service
    if _sm2_service is None:
        _sm2_service = SM2CryptoService()
    return _sm2_service


if __name__ == '__main__':    
    sm2_svc = get_sm2_service()
    s = sm2_svc.encrypt('hello')
    print(s)
 
    c = sm2_svc.decrypt(s)
    print(c)
