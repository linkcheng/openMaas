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

"""用户模块业务规则验证服务"""

import re

from shared.domain.base import DomainException


class UserValidationService:
    """用户业务规则验证服务"""

    @staticmethod
    def validate_username(username: str) -> None:
        """验证用户名"""
        if not username or not username.strip():
            raise DomainException("用户名不能为空")

        username = username.strip()
        if len(username) < 3:
            raise DomainException("用户名长度不能少于3个字符")

        if len(username) > 64:
            raise DomainException("用户名长度不能超过64个字符")

        # 用户名只能包含字母、数字、下划线
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise DomainException("用户名只能包含字母、数字和下划线")

    @staticmethod
    def validate_email(email: str) -> None:
        """验证邮箱"""
        if not email or not email.strip():
            raise DomainException("邮箱不能为空")

        email = email.strip()
        if len(email) > 254:
            raise DomainException("邮箱长度不能超过254个字符")

        # 简单的邮箱格式验证
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise DomainException("邮箱格式无效")

    @staticmethod
    def validate_password(password: str) -> None:
        """验证密码"""
        if not password:
            raise DomainException("密码不能为空")

        if len(password) < 8:
            raise DomainException("密码长度不能少于8个字符")

        if len(password) > 128:
            raise DomainException("密码长度不能超过128个字符")

        # 密码必须包含至少一个字母和一个数字
        if not re.search(r"[a-zA-Z]", password):
            raise DomainException("密码必须包含至少一个字母")

        if not re.search(r"\d", password):
            raise DomainException("密码必须包含至少一个数字")

    @staticmethod
    def validate_user_profile(first_name: str | None, last_name: str | None,
                             organization: str | None, bio: str | None) -> None:
        """验证用户档案信息"""
        if first_name and len(first_name.strip()) > 50:
            raise DomainException("名字长度不能超过50个字符")

        if last_name and len(last_name.strip()) > 50:
            raise DomainException("姓氏长度不能超过50个字符")

        if organization and len(organization.strip()) > 100:
            raise DomainException("组织名称长度不能超过100个字符")

        if bio and len(bio.strip()) > 500:
            raise DomainException("个人简介长度不能超过500个字符")

    @staticmethod
    def validate_role_name(role_name: str) -> None:
        """验证角色名称"""
        if not role_name or not role_name.strip():
            raise DomainException("角色名称不能为空")

        role_name = role_name.strip()
        if len(role_name) > 64:
            raise DomainException("角色名称长度不能超过64个字符")

        # 角色名称只能包含字母、数字、下划线、连字符和空格
        if not re.match(r"^[a-zA-Z0-9_\-\s]+$", role_name):
            raise DomainException("角色名称只能包含字母、数字、下划线、连字符和空格")

    @staticmethod
    def validate_role_description(description: str | None) -> None:
        """验证角色描述"""
        if description and len(description.strip()) > 500:
            raise DomainException("角色描述长度不能超过500个字符")

    @staticmethod
    def validate_permission_name(permission_name: str) -> None:
        """验证权限名称"""
        if not permission_name or not permission_name.strip():
            raise DomainException("权限名称不能为空")

        permission_name = permission_name.strip()
        if len(permission_name) > 100:
            raise DomainException("权限名称长度不能超过100个字符")

        # 权限名称格式: module.resource.action 或 *.resource.action
        if not re.match(r"^(\*|[a-zA-Z0-9_]+)\.[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$", permission_name):
            raise DomainException("权限名称格式无效，应为: module.resource.action")

    @staticmethod
    def validate_permission_display_name(display_name: str) -> None:
        """验证权限显示名称"""
        if not display_name or not display_name.strip():
            raise DomainException("权限显示名称不能为空")

        if len(display_name.strip()) > 100:
            raise DomainException("权限显示名称长度不能超过100个字符")

    @staticmethod
    def validate_permission_description(description: str | None) -> None:
        """验证权限描述"""
        if description and len(description.strip()) > 500:
            raise DomainException("权限描述长度不能超过500个字符")

    @staticmethod
    def validate_permission_module(module: str | None) -> None:
        """验证权限模块名称"""
        if module:
            module = module.strip()
            if len(module) > 50:
                raise DomainException("权限模块名称长度不能超过50个字符")

            if not re.match(r"^[a-zA-Z0-9_]+$", module):
                raise DomainException("权限模块名称只能包含字母、数字和下划线")
