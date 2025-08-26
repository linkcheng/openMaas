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

"""异常映射器 - 将Domain异常转换为Application异常"""

from shared.application.exceptions import ApplicationException, ErrorCode
from shared.domain.base import (
    AccessDeniedException,
    BusinessRuleViolationException,
    DomainException,
    InvalidOperationException,
)
from shared.domain.base import (
    ResourceNotFoundException as DomainResourceNotFoundException,
)


def map_domain_to_application_exception(domain_exc: DomainException) -> ApplicationException:
    """将Domain异常转换为Application异常"""

    # 根据Domain异常类型映射到相应的错误码
    error_code_map = {
        BusinessRuleViolationException: ErrorCode.VAL_VALIDATION_ERROR,
        DomainResourceNotFoundException: ErrorCode.RES_NOT_FOUND,
        AccessDeniedException: ErrorCode.RES_ACCESS_DENIED,
        InvalidOperationException: ErrorCode.VAL_INVALID_REQUEST,
    }

    # 获取对应的错误码
    domain_exc_type = type(domain_exc)
    error_code = error_code_map.get(domain_exc_type, ErrorCode.SYS_INTERNAL_ERROR)

    # 如果Domain异常有自定义错误码，优先使用
    if hasattr(domain_exc, "code") and domain_exc.code:
        # Domain异常的code可能需要映射为相应的Application错误码
        custom_code = _map_domain_code_to_application_code(domain_exc.code)
        if custom_code:
            error_code = custom_code

    return ApplicationException(
        message=domain_exc.message,
        code=error_code,
        details={"domain_error": str(domain_exc)}
    )


def _map_domain_code_to_application_code(domain_code: str) -> ErrorCode | None:
    """将Domain层的错误码映射为Application层的错误码"""

    # Domain层的错误码通常是业务相关的，映射到BIZ_前缀的错误码
    domain_to_application_map = {
        "USER_NOT_FOUND": ErrorCode.BIZ_USER_NOT_FOUND,
        "USER_ALREADY_EXISTS": ErrorCode.BIZ_USER_ALREADY_EXISTS,
        "USER_SUSPENDED": ErrorCode.BIZ_USER_SUSPENDED,
        "PERMISSION_DENIED": ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
        "INVALID_CREDENTIALS": ErrorCode.AUTH_INVALID_CREDENTIALS,
        "ROLE_NOT_FOUND": ErrorCode.RES_NOT_FOUND,
        "PERMISSION_NOT_FOUND": ErrorCode.RES_NOT_FOUND,
        "ROLE_ALREADY_EXISTS": ErrorCode.RES_ALREADY_EXISTS,
        "PERMISSION_ALREADY_EXISTS": ErrorCode.RES_ALREADY_EXISTS,
        "INVALID_OPERATION": ErrorCode.VAL_INVALID_REQUEST,
        "BUSINESS_RULE_VIOLATION": ErrorCode.VAL_VALIDATION_ERROR,
    }

    return domain_to_application_map.get(domain_code)


# 装饰器：自动捕获Domain异常并转换为Application异常
def handle_domain_exceptions(func):
    """装饰器：自动处理Domain异常转换"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DomainException as domain_exc:
            app_exc = map_domain_to_application_exception(domain_exc)
            raise app_exc

    return wrapper
