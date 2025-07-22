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

"""共享应用层测试 - 异常测试"""

import pytest
from fastapi import HTTPException

from src.shared.application.exceptions import (
    ApplicationException,
    to_http_exception,
    ValidationException,
    NotFoundException,
    AuthenticationException,
    AuthorizationException
)


class TestApplicationException:
    """应用异常测试"""
    
    def test_application_exception_creation(self):
        """测试应用异常创建"""
        exception = ApplicationException("测试异常", "TEST_ERROR")
        
        assert exception.message == "测试异常"
        assert exception.code == "TEST_ERROR"
        assert str(exception) == "测试异常"
    
    def test_application_exception_default_code(self):
        """测试默认错误码"""
        exception = ApplicationException("测试异常")
        
        assert exception.code == "APPLICATION_ERROR"


class TestValidationException:
    """验证异常测试"""
    
    def test_validation_exception(self):
        """测试验证异常"""
        exception = ValidationException("验证失败", {"field": "error"})
        
        assert exception.message == "验证失败"
        assert exception.code == "VALIDATION_ERROR"
        assert exception.details == {"field": "error"}
    
    def test_validation_exception_without_details(self):
        """测试无详情的验证异常"""
        exception = ValidationException("验证失败")
        
        assert exception.details == {}


class TestNotFoundException:
    """未找到异常测试"""
    
    def test_not_found_exception(self):
        """测试未找到异常"""
        exception = NotFoundException("资源未找到")
        
        assert exception.message == "资源未找到"
        assert exception.code == "NOT_FOUND"


class TestAuthenticationException:
    """认证异常测试"""
    
    def test_authentication_exception(self):
        """测试认证异常"""
        exception = AuthenticationException("认证失败")
        
        assert exception.message == "认证失败"
        assert exception.code == "AUTHENTICATION_ERROR"


class TestAuthorizationException:
    """授权异常测试"""
    
    def test_authorization_exception(self):
        """测试授权异常"""
        exception = AuthorizationException("权限不足")
        
        assert exception.message == "权限不足"
        assert exception.code == "AUTHORIZATION_ERROR"


class TestHttpExceptionConversion:
    """HTTP异常转换测试"""
    
    def test_application_exception_to_http(self):
        """测试应用异常转换为HTTP异常"""
        app_exception = ApplicationException("应用错误", "APP_ERROR")
        http_exception = to_http_exception(app_exception)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == 500
        assert http_exception.detail["success"] == False
        assert http_exception.detail["error"]["code"] == "APP_ERROR"
        assert http_exception.detail["error"]["message"] == "应用错误"
    
    def test_validation_exception_to_http(self):
        """测试验证异常转换为HTTP异常"""
        validation_exception = ValidationException("验证失败", {"field": "error"})
        http_exception = to_http_exception(validation_exception)
        
        assert http_exception.status_code == 400
        assert http_exception.detail["error"]["details"] == {"field": "error"}
    
    def test_not_found_exception_to_http(self):
        """测试未找到异常转换为HTTP异常"""
        not_found_exception = NotFoundException("资源未找到")
        http_exception = to_http_exception(not_found_exception)
        
        assert http_exception.status_code == 404
    
    def test_authentication_exception_to_http(self):
        """测试认证异常转换为HTTP异常"""
        auth_exception = AuthenticationException("认证失败")
        http_exception = to_http_exception(auth_exception)
        
        assert http_exception.status_code == 401
    
    def test_authorization_exception_to_http(self):
        """测试授权异常转换为HTTP异常"""
        authz_exception = AuthorizationException("权限不足")
        http_exception = to_http_exception(authz_exception)
        
        assert http_exception.status_code == 403
    
    def test_unknown_exception_to_http(self):
        """测试未知异常转换为HTTP异常"""
        unknown_exception = ApplicationException("未知错误", "UNKNOWN_ERROR")
        http_exception = to_http_exception(unknown_exception)
        
        assert http_exception.status_code == 500