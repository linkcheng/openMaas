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

"""安全工具和验证"""

import re
from typing import Any
from urllib.parse import urlparse

from loguru import logger


class SecurityValidator:
    """安全验证器"""

    # 危险字符模式
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS script标签
        r"javascript:",  # JavaScript协议
        r"on\w+\s*=",  # 事件处理器
        r"expression\s*\(",  # CSS表达式
        r"@import",  # CSS导入
        r"<iframe[^>]*>",  # iframe标签
        r"<object[^>]*>",  # object标签
        r"<embed[^>]*>",  # embed标签
    ]

    # SQL注入模式
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r'(\b(OR|AND)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?)',
        r"(--|#|/\*|\*/)",
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDROP\b.*\bTABLE\b)",
    ]

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """验证URL安全性"""
        try:
            parsed = urlparse(url)

            # 检查协议
            if parsed.scheme not in ["http", "https"]:
                logger.warning(f"Invalid URL scheme: {parsed.scheme}")
                return False

            # 检查主机名
            if not parsed.netloc:
                logger.warning("URL missing hostname")
                return False

            # 检查是否为本地地址（可选，根据需求调整）
            local_hosts = ["localhost", "127.0.0.1", "0.0.0.0"]
            if parsed.hostname in local_hosts:
                logger.warning(f"Local hostname detected: {parsed.hostname}")
                # 在生产环境中可能需要禁止本地地址
                # return False

            return True
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False

    @classmethod
    def validate_input_safety(cls, input_value: str) -> bool:
        """验证输入安全性，防止XSS和注入攻击"""
        if not input_value:
            return True

        # 检查危险模式
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, input_value, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected in input: {pattern}")
                return False

        return True

    @classmethod
    def validate_sql_injection(cls, input_value: str) -> bool:
        """验证SQL注入"""
        if not input_value:
            return True

        # 检查SQL注入模式
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_value, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return False

        return True

    @classmethod
    def sanitize_string(cls, input_value: str) -> str:
        """清理字符串，移除危险字符"""
        if not input_value:
            return input_value

        # 移除HTML标签
        sanitized = re.sub(r"<[^>]+>", "", input_value)

        # 移除JavaScript协议
        sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)

        # 移除事件处理器
        sanitized = re.sub(r'on\w+\s*=\s*[\'"][^\'"]*[\'"]', "", sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    @classmethod
    def validate_api_key_format(cls, api_key: str) -> bool:
        """验证API密钥格式"""
        if not api_key:
            return True  # 可选字段

        # 检查长度（一般API密钥都有最小长度要求）
        if len(api_key) < 10:
            logger.warning("API key too short")
            return False

        # 检查是否包含危险字符
        if not cls.validate_input_safety(api_key):
            return False

        # 检查是否为明显的测试/示例密钥
        test_patterns = [
            r"^(test|demo|example|sample)",
            r"(xxx|yyy|zzz)",
            r"^(sk-)?[0-9a-f]{32}$",  # 简单的十六进制模式
        ]

        for pattern in test_patterns:
            if re.match(pattern, api_key, re.IGNORECASE):
                logger.info("Test/example API key detected")
                # 在开发环境中可能允许，生产环境中需要更严格
                break

        return True

    @classmethod
    def validate_json_config(cls, config: dict[str, Any]) -> bool:
        """验证JSON配置安全性"""
        if not config:
            return True

        # 检查配置键和值
        for key, value in config.items():
            if isinstance(value, str):
                if not cls.validate_input_safety(value):
                    logger.warning(f"Unsafe value in config key: {key}")
                    return False
            elif isinstance(value, dict):
                if not cls.validate_json_config(value):
                    return False

        return True

    @classmethod
    def mask_sensitive_data(cls, data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """遮蔽敏感数据"""
        if not data or len(data) <= visible_chars:
            return mask_char * len(data) if data else ""

        return data[:visible_chars] + mask_char * (len(data) - visible_chars)
