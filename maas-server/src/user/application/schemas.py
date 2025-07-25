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

"""用户应用层 - DTO模型"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# 请求DTO
class UserCreateRequest(BaseModel):
    """用户创建请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="SM2加密后的密码")
    first_name: str = Field(..., min_length=1, max_length=50, description="名字")
    last_name: str = Field(..., min_length=1, max_length=50, description="姓氏")
    organization: str | None = Field(None, max_length=255, description="组织")

    @validator("username")
    def validate_username(cls, v):
        import re
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    login_id: str = Field(..., description="邮箱地址或用户名")
    password: str = Field(..., description="SM2加密后的密码")


class UserUpdateRequest(BaseModel):
    """用户更新请求"""
    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    avatar_url: str | None = Field(None, description="头像URL")
    organization: str | None = Field(None, max_length=255)
    bio: str | None = Field(None, max_length=500)


class PasswordChangeRequest(BaseModel):
    """密码修改请求"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., description="新密码")


class EmailVerificationRequest(BaseModel):
    """邮箱验证请求"""
    token: str = Field(..., description="验证令牌")


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirmRequest(BaseModel):
    """密码重置确认请求"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")


class UserSearchRequest(BaseModel):
    """用户搜索请求"""
    keyword: str | None = Field(None, description="搜索关键词")
    status: UserStatus | None = Field(None, description="用户状态")
    organization: str | None = Field(None, description="组织")
    page: int = Field(1, ge=1, description="页码")
    limit: int = Field(20, ge=1, le=100, description="每页数量")


# 响应DTO
class UserProfileResponse(BaseModel):
    """用户档案响应"""
    first_name: str
    last_name: str
    full_name: str
    avatar_url: str | None
    organization: str | None
    bio: str | None


class RoleResponse(BaseModel):
    """角色响应"""
    id: UUID
    name: str
    description: str
    permissions: list[str]


class UserResponse(BaseModel):
    """用户响应"""
    id: UUID
    username: str
    email: str
    profile: UserProfileResponse
    status: UserStatus
    email_verified: bool
    roles: list[RoleResponse]
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None

    class Config:
        from_attributes = True


class UserSummaryResponse(BaseModel):
    """用户摘要响应（用于列表）"""
    id: UUID
    username: str
    email: str
    full_name: str
    organization: str | None
    status: UserStatus
    email_verified: bool
    created_at: datetime
    last_login_at: datetime | None


class AuthTokenResponse(BaseModel):
    """认证令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_api_calls: int
    total_storage_used: int
    total_compute_hours: int
    models_created: int
    applications_created: int
    last_30_days_activity: dict[str, int]


# 内部DTO（应用层内部使用）
class UserCreateCommand(BaseModel):
    """用户创建命令"""
    username: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    organization: str | None = None


class UserUpdateCommand(BaseModel):
    """用户更新命令"""
    user_id: UUID
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    organization: str | None = None
    bio: str | None = None


class PasswordChangeCommand(BaseModel):
    """密码修改命令"""
    user_id: UUID
    current_password: str
    new_password_hash: str


class UserSearchQuery(BaseModel):
    """用户搜索查询"""
    keyword: str | None = None
    status: str | None = None
    organization: str | None = None
    limit: int = 20
    offset: int = 0
