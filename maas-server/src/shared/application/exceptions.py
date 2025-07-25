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

"""共享应用层 - 通用异常处理"""

from enum import Enum
from typing import Any

from fastapi import HTTPException


class ErrorCode(str, Enum):
    """错误码枚举"""

    # 通用错误
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # 认证相关
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_VERSION_MISMATCH = "TOKEN_VERSION_MISMATCH"
    TOKEN_REFRESH_REQUIRED = "TOKEN_REFRESH_REQUIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # 用户相关
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"

    # 模型相关
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    MODEL_ALREADY_EXISTS = "MODEL_ALREADY_EXISTS"
    MODEL_UPLOAD_FAILED = "MODEL_UPLOAD_FAILED"
    INVALID_MODEL_FORMAT = "INVALID_MODEL_FORMAT"

    # 微调相关
    FINETUNE_JOB_NOT_FOUND = "FINETUNE_JOB_NOT_FOUND"
    FINETUNE_JOB_FAILED = "FINETUNE_JOB_FAILED"
    INVALID_TRAINING_DATA = "INVALID_TRAINING_DATA"

    # 推理相关
    INFERENCE_FAILED = "INFERENCE_FAILED"
    DEPLOYMENT_NOT_FOUND = "DEPLOYMENT_NOT_FOUND"
    DEPLOYMENT_FAILED = "DEPLOYMENT_FAILED"

    # 知识库相关
    KNOWLEDGE_BASE_NOT_FOUND = "KNOWLEDGE_BASE_NOT_FOUND"
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    DOCUMENT_PROCESSING_FAILED = "DOCUMENT_PROCESSING_FAILED"

    # 资源限制
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    STORAGE_LIMIT_EXCEEDED = "STORAGE_LIMIT_EXCEEDED"


class ApplicationException(Exception):
    """应用层异常基类"""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ValidationException(ApplicationException):
    """验证异常"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)


class AuthenticationException(ApplicationException):
    """认证异常"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(message, ErrorCode.AUTHENTICATION_FAILED)


class AuthorizationException(ApplicationException):
    """授权异常"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, ErrorCode.INSUFFICIENT_PERMISSIONS)


class TokenVersionMismatchException(ApplicationException):
    """Token版本不匹配异常"""

    def __init__(self, message: str = "Token版本已过期，请重新登录"):
        super().__init__(message, ErrorCode.TOKEN_VERSION_MISMATCH)


class TokenRefreshRequiredException(ApplicationException):
    """Token需要刷新异常"""

    def __init__(self, message: str = "Token已过期，需要刷新"):
        super().__init__(message, ErrorCode.TOKEN_REFRESH_REQUIRED)


class ResourceNotFoundException(ApplicationException):
    """资源未找到异常"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} {resource_id} 未找到"
        super().__init__(message, ErrorCode.RESOURCE_NOT_FOUND)


class BusinessRuleException(ApplicationException):
    """业务规则异常"""

    def __init__(self, message: str, code: ErrorCode = ErrorCode.INVALID_REQUEST):
        super().__init__(message, code)


class QuotaExceededException(ApplicationException):
    """配额超限异常"""

    def __init__(self, resource_type: str, limit: int):
        message = f"{resource_type} 配额已达上限 {limit}"
        super().__init__(message, ErrorCode.QUOTA_EXCEEDED)


class RateLimitExceededException(ApplicationException):
    """限流异常"""

    def __init__(self, message: str = "请求频率过高，请稍后再试"):
        super().__init__(message, ErrorCode.RATE_LIMIT_EXCEEDED)


def to_http_exception(exc: ApplicationException) -> HTTPException:
    """将应用异常转换为HTTP异常"""

    status_code_map = {
        ErrorCode.VALIDATION_ERROR: 422,
        ErrorCode.AUTHENTICATION_FAILED: 401,
        ErrorCode.INVALID_TOKEN: 401,
        ErrorCode.TOKEN_EXPIRED: 401,
        ErrorCode.TOKEN_VERSION_MISMATCH: 401,
        ErrorCode.TOKEN_REFRESH_REQUIRED: 401,
        ErrorCode.INSUFFICIENT_PERMISSIONS: 403,
        ErrorCode.RESOURCE_NOT_FOUND: 404,
        ErrorCode.USER_ALREADY_EXISTS: 409,
        ErrorCode.MODEL_ALREADY_EXISTS: 409,
        ErrorCode.RATE_LIMIT_EXCEEDED: 429,
        ErrorCode.QUOTA_EXCEEDED: 429,
        ErrorCode.INTERNAL_SERVER_ERROR: 500,
    }

    status_code = status_code_map.get(exc.code, 500)

    return HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )
