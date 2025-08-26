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
    """错误码枚举 - 按前缀分类规范"""

    # 系统错误 (SYS_) - 系统级别的基础错误
    SYS_INTERNAL_ERROR = "SYS_INTERNAL_ERROR"
    SYS_DATABASE_ERROR = "SYS_DATABASE_ERROR"
    SYS_CACHE_ERROR = "SYS_CACHE_ERROR"
    SYS_NETWORK_ERROR = "SYS_NETWORK_ERROR"
    SYS_CONFIG_ERROR = "SYS_CONFIG_ERROR"

    # 认证授权错误 (AUTH_) - 身份验证和权限相关
    AUTH_FAILED = "AUTH_FAILED"
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_VERSION_MISMATCH = "AUTH_TOKEN_VERSION_MISMATCH"
    AUTH_TOKEN_REFRESH_REQUIRED = "AUTH_TOKEN_REFRESH_REQUIRED"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS"
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_EMAIL_NOT_VERIFIED = "AUTH_EMAIL_NOT_VERIFIED"

    # 验证错误 (VAL_) - 数据验证和格式错误
    VAL_INVALID_REQUEST = "VAL_INVALID_REQUEST"
    VAL_VALIDATION_ERROR = "VAL_VALIDATION_ERROR"
    VAL_INVALID_FORMAT = "VAL_INVALID_FORMAT"
    VAL_MISSING_REQUIRED_FIELD = "VAL_MISSING_REQUIRED_FIELD"
    VAL_INVALID_PARAMETER = "VAL_INVALID_PARAMETER"
    VAL_INVALID_EMAIL = "VAL_INVALID_EMAIL"
    VAL_INVALID_PHONE = "VAL_INVALID_PHONE"

    # 资源错误 (RES_) - 资源访问和管理相关
    RES_NOT_FOUND = "RES_NOT_FOUND"
    RES_ALREADY_EXISTS = "RES_ALREADY_EXISTS"
    RES_ACCESS_DENIED = "RES_ACCESS_DENIED"
    RES_CONFLICT = "RES_CONFLICT"
    RES_LOCKED = "RES_LOCKED"
    RES_EXPIRED = "RES_EXPIRED"

    # 业务错误 (BIZ_) - 具体业务逻辑错误
    BIZ_USER_NOT_FOUND = "BIZ_USER_NOT_FOUND"
    BIZ_USER_ALREADY_EXISTS = "BIZ_USER_ALREADY_EXISTS"
    BIZ_USER_SUSPENDED = "BIZ_USER_SUSPENDED"
    BIZ_MODEL_NOT_FOUND = "BIZ_MODEL_NOT_FOUND"
    BIZ_MODEL_ALREADY_EXISTS = "BIZ_MODEL_ALREADY_EXISTS"
    BIZ_MODEL_UPLOAD_FAILED = "BIZ_MODEL_UPLOAD_FAILED"
    BIZ_FINETUNE_JOB_NOT_FOUND = "BIZ_FINETUNE_JOB_NOT_FOUND"
    BIZ_FINETUNE_JOB_FAILED = "BIZ_FINETUNE_JOB_FAILED"
    BIZ_INFERENCE_FAILED = "BIZ_INFERENCE_FAILED"
    BIZ_DEPLOYMENT_NOT_FOUND = "BIZ_DEPLOYMENT_NOT_FOUND"
    BIZ_DEPLOYMENT_FAILED = "BIZ_DEPLOYMENT_FAILED"
    BIZ_KNOWLEDGE_BASE_NOT_FOUND = "BIZ_KNOWLEDGE_BASE_NOT_FOUND"
    BIZ_DOCUMENT_NOT_FOUND = "BIZ_DOCUMENT_NOT_FOUND"
    BIZ_DOCUMENT_PROCESSING_FAILED = "BIZ_DOCUMENT_PROCESSING_FAILED"

    # 限制错误 (LIM_) - 速率限制、配额等限制相关
    LIM_RATE_LIMIT_EXCEEDED = "LIM_RATE_LIMIT_EXCEEDED"
    LIM_STORAGE_LIMIT_EXCEEDED = "LIM_STORAGE_LIMIT_EXCEEDED"
    LIM_QUOTA_EXCEEDED = "LIM_QUOTA_EXCEEDED"
    LIM_CONCURRENT_LIMIT_EXCEEDED = "LIM_CONCURRENT_LIMIT_EXCEEDED"


class ApplicationException(Exception):
    """应用层异常基类"""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.SYS_INTERNAL_ERROR,
        details: dict[str, Any] | None = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ValidationException(ApplicationException):
    """验证异常"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, ErrorCode.VAL_VALIDATION_ERROR, details)


class AuthenticationException(ApplicationException):
    """认证异常"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(message, ErrorCode.AUTH_FAILED)


class AuthorizationException(ApplicationException):
    """授权异常"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS)


class TokenVersionMismatchException(ApplicationException):
    """Token版本不匹配异常"""

    def __init__(self, message: str = "Token版本已过期，请重新登录"):
        super().__init__(message, ErrorCode.AUTH_TOKEN_VERSION_MISMATCH)


class TokenRefreshRequiredException(ApplicationException):
    """Token需要刷新异常"""

    def __init__(self, message: str = "Token已过期，需要刷新"):
        super().__init__(message, ErrorCode.AUTH_TOKEN_REFRESH_REQUIRED)


class ResourceNotFoundException(ApplicationException):
    """资源未找到异常"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} {resource_id} 未找到"
        super().__init__(message, ErrorCode.RES_NOT_FOUND)


class BusinessRuleException(ApplicationException):
    """业务规则异常"""

    def __init__(self, message: str, code: ErrorCode = ErrorCode.VAL_INVALID_REQUEST):
        super().__init__(message, code)


class RateLimitExceededException(ApplicationException):
    """限流异常"""

    def __init__(self, message: str = "请求频率过高，请稍后再试"):
        super().__init__(message, ErrorCode.LIM_RATE_LIMIT_EXCEEDED)


def to_http_exception(exc: ApplicationException) -> HTTPException:
    """将应用异常转换为HTTP异常"""

    status_code_map = {
        # 系统错误 -> 500
        ErrorCode.SYS_INTERNAL_ERROR: 500,
        ErrorCode.SYS_DATABASE_ERROR: 500,
        ErrorCode.SYS_CACHE_ERROR: 500,
        ErrorCode.SYS_NETWORK_ERROR: 500,
        ErrorCode.SYS_CONFIG_ERROR: 500,

        # 认证授权错误 -> 401/403
        ErrorCode.AUTH_FAILED: 401,
        ErrorCode.AUTH_INVALID_TOKEN: 401,
        ErrorCode.AUTH_TOKEN_EXPIRED: 401,
        ErrorCode.AUTH_TOKEN_VERSION_MISMATCH: 401,
        ErrorCode.AUTH_TOKEN_REFRESH_REQUIRED: 401,
        ErrorCode.AUTH_INVALID_CREDENTIALS: 401,
        ErrorCode.AUTH_EMAIL_NOT_VERIFIED: 401,
        ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS: 403,

        # 验证错误 -> 400/422
        ErrorCode.VAL_INVALID_REQUEST: 400,
        ErrorCode.VAL_VALIDATION_ERROR: 422,
        ErrorCode.VAL_INVALID_FORMAT: 400,
        ErrorCode.VAL_MISSING_REQUIRED_FIELD: 400,
        ErrorCode.VAL_INVALID_PARAMETER: 400,
        ErrorCode.VAL_INVALID_EMAIL: 400,
        ErrorCode.VAL_INVALID_PHONE: 400,

        # 资源错误 -> 404/409/403
        ErrorCode.RES_NOT_FOUND: 404,
        ErrorCode.RES_ALREADY_EXISTS: 409,
        ErrorCode.RES_ACCESS_DENIED: 403,
        ErrorCode.RES_CONFLICT: 409,
        ErrorCode.RES_LOCKED: 423,
        ErrorCode.RES_EXPIRED: 410,

        # 业务错误 -> 400/404/409
        ErrorCode.BIZ_USER_NOT_FOUND: 404,
        ErrorCode.BIZ_USER_ALREADY_EXISTS: 409,
        ErrorCode.BIZ_USER_SUSPENDED: 403,
        ErrorCode.BIZ_MODEL_NOT_FOUND: 404,
        ErrorCode.BIZ_MODEL_ALREADY_EXISTS: 409,
        ErrorCode.BIZ_MODEL_UPLOAD_FAILED: 400,
        ErrorCode.BIZ_FINETUNE_JOB_NOT_FOUND: 404,
        ErrorCode.BIZ_FINETUNE_JOB_FAILED: 400,
        ErrorCode.BIZ_INFERENCE_FAILED: 400,
        ErrorCode.BIZ_DEPLOYMENT_NOT_FOUND: 404,
        ErrorCode.BIZ_DEPLOYMENT_FAILED: 400,
        ErrorCode.BIZ_KNOWLEDGE_BASE_NOT_FOUND: 404,
        ErrorCode.BIZ_DOCUMENT_NOT_FOUND: 404,
        ErrorCode.BIZ_DOCUMENT_PROCESSING_FAILED: 400,

        # 限制错误 -> 429
        ErrorCode.LIM_RATE_LIMIT_EXCEEDED: 429,
        ErrorCode.LIM_STORAGE_LIMIT_EXCEEDED: 429,
        ErrorCode.LIM_QUOTA_EXCEEDED: 429,
        ErrorCode.LIM_CONCURRENT_LIMIT_EXCEEDED: 429,
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
