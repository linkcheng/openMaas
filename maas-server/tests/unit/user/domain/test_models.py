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

"""用户领域测试 - 用户模型测试"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.user.domain.models import (
    User,
    UserProfile,
    UserQuota,
    UserStatus,
    RoleType,
    Role,
    Permission,
    ApiKey,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    EmailNotVerifiedException,
    UserRegisteredEvent,
    UserEmailVerifiedEvent,
    UserProfileUpdatedEvent,
    ApiKeyCreatedEvent
)
from src.shared.domain.base import EmailAddress, BusinessRuleViolationException


class TestUserProfile:
    """用户档案测试"""
    
    def test_user_profile_creation(self):
        """测试用户档案创建"""
        profile = UserProfile(
            first_name="张",
            last_name="三",
            avatar_url="https://example.com/avatar.png",
            organization="测试公司",
            bio="测试简介"
        )
        
        assert profile.first_name == "张"
        assert profile.last_name == "三"
        assert profile.full_name == "张 三"
        assert profile.avatar_url == "https://example.com/avatar.png"
        assert profile.organization == "测试公司"
        assert profile.bio == "测试简介"
    
    def test_user_profile_validation(self):
        """测试用户档案验证"""
        # 正常创建
        profile = UserProfile(first_name="张", last_name="三")
        assert profile.full_name == "张 三"
        
        # 名字为空
        with pytest.raises(ValueError, match="名字不能为空"):
            UserProfile(first_name="", last_name="三")
        
        # 姓氏为空
        with pytest.raises(ValueError, match="姓氏不能为空"):
            UserProfile(first_name="张", last_name="")
        
        # 名字过长
        with pytest.raises(ValueError, match="名字长度不能超过50个字符"):
            UserProfile(first_name="a" * 51, last_name="三")
        
        # 姓氏过长
        with pytest.raises(ValueError, match="姓氏长度不能超过50个字符"):
            UserProfile(first_name="张", last_name="a" * 51)


class TestUserQuota:
    """用户配额测试"""
    
    def test_user_quota_creation(self):
        """测试用户配额创建"""
        quota = UserQuota(
            api_calls_limit=1000,
            api_calls_used=100,
            storage_limit=1024 * 1024 * 1024,  # 1GB
            storage_used=1024 * 1024 * 100,    # 100MB
            compute_hours_limit=10,
            compute_hours_used=2
        )
        
        assert quota.api_calls_limit == 1000
        assert quota.api_calls_used == 100
        assert quota.storage_limit == 1024 * 1024 * 1024
        assert quota.storage_used == 1024 * 1024 * 100
        assert quota.compute_hours_limit == 10
        assert quota.compute_hours_used == 2
    
    def test_user_quota_validation(self):
        """测试用户配额验证"""
        # 正常创建
        quota = UserQuota(
            api_calls_limit=1000,
            api_calls_used=0,
            storage_limit=1024,
            storage_used=0,
            compute_hours_limit=10,
            compute_hours_used=0
        )
        
        # API调用限制为负数
        with pytest.raises(ValueError, match="API调用限制不能为负数"):
            UserQuota(
                api_calls_limit=-1,
                api_calls_used=0,
                storage_limit=1024,
                storage_used=0,
                compute_hours_limit=10,
                compute_hours_used=0
            )
        
        # 存储限制为负数
        with pytest.raises(ValueError, match="存储限制不能为负数"):
            UserQuota(
                api_calls_limit=1000,
                api_calls_used=0,
                storage_limit=-1,
                storage_used=0,
                compute_hours_limit=10,
                compute_hours_used=0
            )
        
        # 计算时间限制为负数
        with pytest.raises(ValueError, match="计算时间限制不能为负数"):
            UserQuota(
                api_calls_limit=1000,
                api_calls_used=0,
                storage_limit=1024,
                storage_used=0,
                compute_hours_limit=-1,
                compute_hours_used=0
            )
    
    def test_quota_usage_checks(self):
        """测试配额使用检查"""
        quota = UserQuota(
            api_calls_limit=1000,
            api_calls_used=900,
            storage_limit=1024,
            storage_used=512,
            compute_hours_limit=10,
            compute_hours_used=8
        )
        
        # API调用检查
        assert quota.can_make_api_call(100) == True
        assert quota.can_make_api_call(101) == False
        
        # 存储检查
        assert quota.can_use_storage(512) == True
        assert quota.can_use_storage(513) == False
        
        # 计算时间检查
        assert quota.can_use_compute_hours(2) == True
        assert quota.can_use_compute_hours(3) == False
    
    def test_quota_usage_percentage(self):
        """测试配额使用百分比"""
        quota = UserQuota(
            api_calls_limit=1000,
            api_calls_used=500,
            storage_limit=1000,
            storage_used=250,
            compute_hours_limit=10,
            compute_hours_used=3
        )
        
        assert quota.get_api_usage_percentage() == 50.0
        assert quota.get_storage_usage_percentage() == 25.0
        
        # 限制为0的情况
        quota_zero = UserQuota(
            api_calls_limit=0,
            api_calls_used=0,
            storage_limit=0,
            storage_used=0,
            compute_hours_limit=0,
            compute_hours_used=0
        )
        
        assert quota_zero.get_api_usage_percentage() == 0
        assert quota_zero.get_storage_usage_percentage() == 0


class TestPermission:
    """权限测试"""
    
    def test_permission_creation(self):
        """测试权限创建"""
        permission = Permission(
            id=uuid4(),
            name="读取用户",
            description="允许读取用户信息",
            resource="user",
            action="read"
        )
        
        assert permission.name == "读取用户"
        assert permission.description == "允许读取用户信息"
        assert permission.resource == "user"
        assert permission.action == "read"
        assert str(permission) == "user:read"


class TestRole:
    """角色测试"""
    
    def test_role_creation(self):
        """测试角色创建"""
        permission1 = Permission(
            id=uuid4(),
            name="读取用户",
            description="允许读取用户信息",
            resource="user",
            action="read"
        )
        
        permission2 = Permission(
            id=uuid4(),
            name="写入用户",
            description="允许写入用户信息",
            resource="user",
            action="write"
        )
        
        role = Role(
            id=uuid4(),
            name="用户管理员",
            description="用户管理员角色",
            permissions=[permission1, permission2]
        )
        
        assert role.name == "用户管理员"
        assert role.description == "用户管理员角色"
        assert len(role.permissions) == 2
        assert permission1 in role.permissions
        assert permission2 in role.permissions
    
    def test_role_permission_management(self):
        """测试角色权限管理"""
        permission1 = Permission(
            id=uuid4(),
            name="读取用户",
            description="允许读取用户信息",
            resource="user",
            action="read"
        )
        
        permission2 = Permission(
            id=uuid4(),
            name="写入用户",
            description="允许写入用户信息",
            resource="user",
            action="write"
        )
        
        role = Role(
            id=uuid4(),
            name="用户管理员",
            description="用户管理员角色",
            permissions=[permission1]
        )
        
        # 添加权限
        role.add_permission(permission2)
        assert len(role.permissions) == 2
        assert permission2 in role.permissions
        
        # 重复添加不会增加
        role.add_permission(permission2)
        assert len(role.permissions) == 2
        
        # 移除权限
        role.remove_permission(permission1)
        assert len(role.permissions) == 1
        assert permission1 not in role.permissions
        assert permission2 in role.permissions
    
    def test_role_has_permission(self):
        """测试角色权限检查"""
        permission1 = Permission(
            id=uuid4(),
            name="读取用户",
            description="允许读取用户信息",
            resource="user",
            action="read"
        )
        
        permission2 = Permission(
            id=uuid4(),
            name="所有用户权限",
            description="允许所有用户操作",
            resource="user",
            action="*"
        )
        
        permission3 = Permission(
            id=uuid4(),
            name="管理员权限",
            description="允许所有操作",
            resource="*",
            action="*"
        )
        
        role = Role(
            id=uuid4(),
            name="测试角色",
            description="测试角色",
            permissions=[permission1, permission2, permission3]
        )
        
        # 精确权限
        assert role.has_permission("user", "read") == True
        assert role.has_permission("user", "write") == False
        
        # 通配符权限
        assert role.has_permission("user", "write") == True  # user:* 权限
        assert role.has_permission("model", "read") == True  # *:* 权限
        
        # 不存在的权限
        role_limited = Role(
            id=uuid4(),
            name="受限角色",
            description="受限角色",
            permissions=[permission1]
        )
        
        assert role_limited.has_permission("user", "read") == True
        assert role_limited.has_permission("user", "write") == False
        assert role_limited.has_permission("model", "read") == False


class TestApiKey:
    """API密钥测试"""
    
    def test_api_key_creation(self):
        """测试API密钥创建"""
        api_key = ApiKey(
            id=uuid4(),
            name="测试密钥",
            key_hash="hashed_key",
            permissions=["user:read", "model:read"],
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        assert api_key.name == "测试密钥"
        assert api_key.key_hash == "hashed_key"
        assert api_key.permissions == ["user:read", "model:read"]
        assert api_key.is_active == True
        assert api_key.expires_at is not None
    
    def test_api_key_expiration(self):
        """测试API密钥过期检查"""
        # 未过期的密钥
        api_key = ApiKey(
            id=uuid4(),
            name="测试密钥",
            key_hash="hashed_key",
            permissions=[],
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        
        assert api_key.is_expired() == False
        assert api_key.is_valid() == True
        
        # 已过期的密钥
        expired_key = ApiKey(
            id=uuid4(),
            name="过期密钥",
            key_hash="hashed_key",
            permissions=[],
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        
        assert expired_key.is_expired() == True
        assert expired_key.is_valid() == False
        
        # 永不过期的密钥
        never_expire_key = ApiKey(
            id=uuid4(),
            name="永不过期密钥",
            key_hash="hashed_key",
            permissions=[],
            expires_at=None
        )
        
        assert never_expire_key.is_expired() == False
        assert never_expire_key.is_valid() == True
    
    def test_api_key_use(self):
        """测试API密钥使用"""
        api_key = ApiKey(
            id=uuid4(),
            name="测试密钥",
            key_hash="hashed_key",
            permissions=[]
        )
        
        assert api_key.last_used_at is None
        
        # 使用密钥
        api_key.use()
        assert api_key.last_used_at is not None
        
        # 使用已过期的密钥
        expired_key = ApiKey(
            id=uuid4(),
            name="过期密钥",
            key_hash="hashed_key",
            permissions=[],
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        
        with pytest.raises(BusinessRuleViolationException, match="API密钥无效或已过期"):
            expired_key.use()
    
    def test_api_key_revoke(self):
        """测试API密钥撤销"""
        api_key = ApiKey(
            id=uuid4(),
            name="测试密钥",
            key_hash="hashed_key",
            permissions=[]
        )
        
        assert api_key.is_active == True
        assert api_key.is_valid() == True
        
        # 撤销密钥
        api_key.revoke()
        assert api_key.is_active == False
        assert api_key.is_valid() == False


class TestUser:
    """用户测试"""
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            organization="Test Org"
        )
        
        assert user.username == "testuser"
        assert user.email.value == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.profile.first_name == "Test"
        assert user.profile.last_name == "User"
        assert user.profile.organization == "Test Org"
        assert user.status == UserStatus.ACTIVE
        assert user.email_verified == False
        assert len(user.domain_events) == 1
        assert isinstance(user.domain_events[0], UserRegisteredEvent)
    
    def test_user_creation_validation(self):
        """测试用户创建验证"""
        # 用户名太短
        with pytest.raises(BusinessRuleViolationException, match="用户名至少需要3个字符"):
            User.create(
                username="ab",
                email="test@example.com",
                password_hash="hashed_password",
                first_name="Test",
                last_name="User"
            )
        
        # 用户名太长
        with pytest.raises(BusinessRuleViolationException, match="用户名不能超过50个字符"):
            User.create(
                username="a" * 51,
                email="test@example.com",
                password_hash="hashed_password",
                first_name="Test",
                last_name="User"
            )
    
    def test_user_email_verification(self):
        """测试用户邮箱验证"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        assert user.email_verified == False
        
        # 验证邮箱
        user.verify_email()
        assert user.email_verified == True
        
        # 检查事件
        email_verified_events = [e for e in user.domain_events if isinstance(e, UserEmailVerifiedEvent)]
        assert len(email_verified_events) == 1
        
        # 重复验证
        with pytest.raises(BusinessRuleViolationException, match="邮箱已经验证过了"):
            user.verify_email()
    
    def test_user_profile_update(self):
        """测试用户档案更新"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        new_profile = UserProfile(
            first_name="New",
            last_name="Name",
            bio="New bio"
        )
        
        user.update_profile(new_profile)
        
        assert user.profile.first_name == "New"
        assert user.profile.last_name == "Name"
        assert user.profile.bio == "New bio"
        
        # 检查事件
        profile_updated_events = [e for e in user.domain_events if isinstance(e, UserProfileUpdatedEvent)]
        assert len(profile_updated_events) == 1
    
    def test_user_role_management(self):
        """测试用户角色管理"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        role = Role(
            id=uuid4(),
            name="测试角色",
            description="测试角色",
            permissions=[]
        )
        
        # 添加角色
        user.add_role(role)
        assert len(user.roles) == 1
        assert role in user.roles
        
        # 重复添加不会增加
        user.add_role(role)
        assert len(user.roles) == 1
        
        # 移除角色
        user.remove_role(role)
        assert len(user.roles) == 0
        assert role not in user.roles
    
    def test_user_api_key_management(self):
        """测试用户API密钥管理"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        # 创建API密钥
        api_key = user.create_api_key(
            name="测试密钥",
            key_hash="hashed_key",
            permissions=["user:read"]
        )
        
        assert api_key.name == "测试密钥"
        assert api_key.key_hash == "hashed_key"
        assert api_key.permissions == ["user:read"]
        assert len(user.api_keys) == 1
        assert api_key in user.api_keys
        
        # 检查事件
        api_key_created_events = [e for e in user.domain_events if isinstance(e, ApiKeyCreatedEvent)]
        assert len(api_key_created_events) == 1
        
        # 撤销API密钥
        user.revoke_api_key(api_key.id)
        assert api_key.is_active == False
        
        # 撤销不存在的密钥
        with pytest.raises(BusinessRuleViolationException, match="API密钥不存在"):
            user.revoke_api_key(uuid4())
    
    def test_user_api_key_limit(self):
        """测试用户API密钥数量限制"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        # 创建10个API密钥
        for i in range(10):
            user.create_api_key(
                name=f"密钥{i}",
                key_hash=f"hashed_key_{i}",
                permissions=[]
            )
        
        # 尝试创建第11个密钥
        with pytest.raises(BusinessRuleViolationException, match="API密钥数量已达上限"):
            user.create_api_key(
                name="超限密钥",
                key_hash="hashed_key_11",
                permissions=[]
            )
    
    def test_user_status_management(self):
        """测试用户状态管理"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        assert user.status == UserStatus.ACTIVE
        
        # 暂停用户
        user.suspend("违规行为")
        assert user.status == UserStatus.SUSPENDED
        
        # 重复暂停
        with pytest.raises(BusinessRuleViolationException, match="用户已被暂停"):
            user.suspend("重复暂停")
        
        # 激活用户
        user.activate()
        assert user.status == UserStatus.ACTIVE
        
        # 重复激活
        with pytest.raises(BusinessRuleViolationException, match="用户已处于激活状态"):
            user.activate()
    
    def test_user_is_active(self):
        """测试用户是否活跃"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        # 未验证邮箱
        assert user.is_active == False
        
        # 验证邮箱
        user.verify_email()
        assert user.is_active == True
        
        # 暂停用户
        user.suspend("测试暂停")
        assert user.is_active == False