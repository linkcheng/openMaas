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
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# 角色和权限相关DTO
class PermissionRequest(BaseModel):
    """权限创建请求"""
    name: str = Field(..., min_length=1, max_length=100, description="权限名称")
    display_name: str = Field(..., min_length=1, max_length=100, description="权限显示名称")
    description: str = Field(..., min_length=1, max_length=255, description="权限描述")
    resource: str = Field(..., min_length=1, max_length=100, description="资源")
    action: str = Field(..., min_length=1, max_length=100, description="操作")
    module: str | None = Field(None, max_length=100, description="模块")


class PermissionResponse(BaseModel):
    """权限响应"""
    id: UUID
    name: str
    display_name: str
    description: str
    resource: str
    action: str
    module: str | None = None

    class Config:
        from_attributes = True


class RoleCreateRequest(BaseModel):
    """角色创建请求"""
    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    description: str = Field(..., min_length=1, max_length=255, description="角色描述")
    permission_ids: list[UUID] = Field(default_factory=list, description="权限ID列表")

    @validator("name")
    def validate_role_name(cls, v):
        import re
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("角色名称只能包含字母、数字和下划线")
        return v.lower()


class RoleUpdateRequest(BaseModel):
    """角色更新请求"""
    name: str | None = Field(None, min_length=1, max_length=100, description="角色名称")
    description: str | None = Field(None, min_length=1, max_length=255, description="角色描述")
    permission_ids: list[UUID] | None = Field(None, description="权限ID列表")

    @validator("name")
    def validate_role_name(cls, v):
        if v is not None:
            import re
            if not re.match(r"^[a-zA-Z0-9_]+$", v):
                raise ValueError("角色名称只能包含字母、数字和下划线")
            return v.lower()
        return v


class RoleResponse(BaseModel):
    """角色响应"""
    id: UUID
    name: str
    description: str
    permissions: list[str]  # 权限字符串列表 "resource:action"

    class Config:
        from_attributes = True


class UserRoleAssignRequest(BaseModel):
    """用户角色分配请求"""
    user_id: UUID
    role_ids: list[UUID] = Field(..., min_items=1, description="角色ID列表")


class RoleSearchQuery(BaseModel):
    """角色搜索查询"""
    name: str | None = Field(None, description="角色名称关键词")
    limit: int = Field(20, ge=1, le=100, description="返回数量限制")
    offset: int = Field(0, ge=0, description="偏移量")


class PermissionUpdateRequest(BaseModel):
    """权限更新请求"""
    name: str | None = Field(None, min_length=1, max_length=100, description="权限名称")
    display_name: str | None = Field(None, min_length=1, max_length=100, description="权限显示名称")
    description: str | None = Field(None, min_length=1, max_length=255, description="权限描述")
    module: str | None = Field(None, max_length=100, description="模块")


class PermissionSearchQuery(BaseModel):
    """权限搜索查询"""
    name: str | None = Field(None, description="权限名称关键词")
    module: str | None = Field(None, description="模块")
    resource: str | None = Field(None, description="资源")
    action: str | None = Field(None, description="操作")
    limit: int = Field(20, ge=1, le=100, description="返回数量限制")
    offset: int = Field(0, ge=0, description="偏移量")


class PermissionBatchRequest(BaseModel):
    """权限批量操作请求"""
    permissions: list[PermissionRequest] = Field(..., min_items=1, description="权限列表")


class PermissionExportResponse(BaseModel):
    """权限导出响应"""
    permissions: list[dict[str, Any]]
    total_count: int
    export_module: str | None = None


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
    expires_in: int
    token_type: str = "Bearer"


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_api_calls: int
    total_storage_used: int
    total_compute_hours: int
    models_created: int
    applications_created: int
    last_30_days_activity: dict[str, int]


# 前端权限相关DTO
class FrontendPermissionModule(BaseModel):
    """前端权限模块"""
    name: str = Field(..., description="模块名称")
    display_name: str = Field(..., description="模块显示名称")
    permissions: list[str] = Field(default_factory=list, description="权限列表")


class FrontendPermissionData(BaseModel):
    """前端权限数据"""
    user_id: UUID
    username: str
    permissions: list[str] = Field(default_factory=list, description="用户所有权限")
    modules: dict[str, FrontendPermissionModule] = Field(default_factory=dict, description="按模块分组的权限")
    roles: list[str] = Field(default_factory=list, description="用户角色列表")
    is_super_admin: bool = Field(default=False, description="是否为超级管理员")
    cached_at: datetime | None = Field(None, description="缓存时间")


class MenuPermissionMapping(BaseModel):
    """菜单权限映射"""
    menu_id: str = Field(..., description="菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    menu_path: str = Field(..., description="菜单路径")
    required_permissions: list[str] = Field(default_factory=list, description="所需权限")
    parent_menu_id: str | None = Field(None, description="父菜单ID")
    sort_order: int = Field(default=0, description="排序顺序")
    icon: str | None = Field(None, description="菜单图标")
    is_visible: bool = Field(default=True, description="是否可见")


class FrontendMenuData(BaseModel):
    """前端菜单数据"""
    menus: list[MenuPermissionMapping] = Field(default_factory=list, description="可访问的菜单列表")
    permissions: list[str] = Field(default_factory=list, description="用户权限")
    user_id: UUID
    username: str




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
