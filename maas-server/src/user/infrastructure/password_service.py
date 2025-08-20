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

"""用户基础设施层 - 密码服务"""

import hashlib
import secrets

from loguru import logger


class PasswordHashService:
    """密码哈希服务
    
    负责密码的哈希和验证，属于技术实现细节。
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )
        return f"{salt}:{password_hash.hex()}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码
        
        Args:
            password: 明文密码
            hashed_password: 已哈希的密码
            
        Returns:
            密码是否匹配
        """
        # 检查输入参数
        if not password or not hashed_password:
            return False

        try:
            salt, stored_hash = hashed_password.split(":")
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                100000
            )
            return password_hash.hex() == stored_hash
        except (ValueError, AttributeError, IndexError) as e:
            logger.error(f"密码验证失败: {e}")
            return False
