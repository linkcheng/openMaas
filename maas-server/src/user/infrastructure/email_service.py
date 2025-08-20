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

"""用户基础设施层 - 邮箱服务"""

import secrets


class EmailVerificationService:
    """邮箱验证服务
    
    负责邮箱验证相关的技术实现，如验证码生成等。
    """

    @staticmethod
    def generate_verification_code() -> str:
        """生成验证码
        
        Returns:
            6位数字验证码
        """
        return str(secrets.randbelow(900000) + 100000)

    @staticmethod
    def generate_verification_token() -> str:
        """生成验证令牌
        
        Returns:
            URL安全的随机令牌
        """
        return secrets.token_urlsafe(32)
