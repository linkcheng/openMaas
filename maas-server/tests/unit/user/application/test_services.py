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

"""用户应用层测试 - 应用服务测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.user.application.user_service import (
    UserApplicationService,
    PasswordHashService,
    EmailVerificationService,
    ApiKeyService
)
from src.user.application.schemas import (
    UserCreateCommand,
    UserUpdateCommand,
    PasswordChangeCommand,
    UserSearchQuery
)
from src.user.domain.models import (
    User,
    UserProfile,
    UserStatus,
    Role,
    Permission,
    PermissionName,
    UserAlreadyExistsException,
    InvalidCredentialsException
)
from src.shared.domain.base import EmailAddress
from src.shared.application.exceptions import ApplicationException


class TestPasswordHashService:
    """密码哈希服务测试"""
    
    def test_hash_password(self):
        """测试密码哈希"""
        password = "TestPassword123!"
        hashed = PasswordHashService.hash_password(password)
        
        assert hashed != password
        assert ":" in hashed  # 格式：salt:hash
        assert len(hashed) > 64  # 哈希结果应该很长
    
    def test_verify_password(self):
        """测试密码验证"""
        password = "TestPassword123!"
        hashed = PasswordHashService.hash_password(password)
        
        # 正确密码
        assert PasswordHashService.verify_password(password, hashed) == True
        
        # 错误密码
        assert PasswordHashService.verify_password("WrongPassword", hashed) == False
        
        # 格式错误的哈希
        assert PasswordHashService.verify_password(password, "invalid_hash") == False
    
    def test_hash_password_different_salts(self):
        """测试相同密码生成不同哈希"""
        password = "TestPassword123!"
        hash1 = PasswordHashService.hash_password(password)
        hash2 = PasswordHashService.hash_password(password)
        
        assert hash1 != hash2  # 不同的salt应该产生不同的哈希
        assert PasswordHashService.verify_password(password, hash1) == True
        assert PasswordHashService.verify_password(password, hash2) == True


class TestEmailVerificationService:
    """邮箱验证服务测试"""
    
    def test_generate_verification_token(self):
        """测试生成验证令牌"""
        token = EmailVerificationService.generate_verification_token()
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_reset_token(self):
        """测试生成重置令牌"""
        token = EmailVerificationService.generate_reset_token()
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_tokens_are_unique(self):
        """测试令牌唯一性"""
        token1 = EmailVerificationService.generate_verification_token()
        token2 = EmailVerificationService.generate_verification_token()
        
        assert token1 != token2
        
        reset_token1 = EmailVerificationService.generate_reset_token()
        reset_token2 = EmailVerificationService.generate_reset_token()
        
        assert reset_token1 != reset_token2


class TestApiKeyService:
    """API密钥服务测试"""
    
    def test_generate_api_key(self):
        """测试生成API密钥"""
        api_key = ApiKeyService.generate_api_key()
        
        assert isinstance(api_key, str)
        assert api_key.startswith("mk-")
        assert len(api_key) > 10
    
    def test_hash_api_key(self):
        """测试API密钥哈希"""
        api_key = "mk-test-key"
        hashed = ApiKeyService.hash_api_key(api_key)
        
        assert isinstance(hashed, str)
        assert hashed != api_key
        assert len(hashed) == 64  # SHA256哈希长度
    
    def test_api_keys_are_unique(self):
        """测试API密钥唯一性"""
        key1 = ApiKeyService.generate_api_key()
        key2 = ApiKeyService.generate_api_key()
        
        assert key1 != key2
    
    def test_same_key_same_hash(self):
        """测试相同密钥产生相同哈希"""
        api_key = "mk-test-key"
        hash1 = ApiKeyService.hash_api_key(api_key)
        hash2 = ApiKeyService.hash_api_key(api_key)
        
        assert hash1 == hash2


class TestUserApplicationService:
    """用户应用服务测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.user_repository = AsyncMock()
        self.role_repository = AsyncMock()
        self.password_service = PasswordHashService()
        self.email_service = EmailVerificationService()
        self.api_key_service = ApiKeyService()
        
        self.service = UserApplicationService(
            user_repository=self.user_repository,
            role_repository=self.role_repository,
            password_service=self.password_service,
            email_service=self.email_service,
            api_key_service=self.api_key_service
        )
    
    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """测试成功创建用户"""
        # 准备测试数据
        command = UserCreateCommand(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            organization="Test Org"
        )
        
        # 模拟仓储返回
        self.user_repository.find_by_email.return_value = None
        self.user_repository.find_by_username.return_value = None
        self.role_repository.find_by_name.return_value = Role(
            id=uuid4(),
            name="user",
            description="普通用户",
            permissions=[]
        )
        
        # 执行测试
        result = await self.service.create_user(command)
        
        # 验证结果
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.profile.first_name == "Test"
        assert result.profile.last_name == "User"
        assert result.profile.organization == "Test Org"
        
        # 验证仓储调用
        self.user_repository.find_by_email.assert_called_once_with("test@example.com")
        self.user_repository.find_by_username.assert_called_once_with("testuser")
        self.user_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_email_exists(self):
        """测试邮箱已存在的情况"""
        command = UserCreateCommand(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        # 模拟邮箱已存在
        existing_user = User.create(
            username="existing",
            email="test@example.com",
            password_hash="hash",
            first_name="Existing",
            last_name="User"
        )
        self.user_repository.find_by_email.return_value = existing_user
        
        # 执行测试并验证异常
        with pytest.raises(UserAlreadyExistsException, match="邮箱 test@example.com 已被使用"):
            await self.service.create_user(command)
    
    @pytest.mark.asyncio
    async def test_create_user_username_exists(self):
        """测试用户名已存在的情况"""
        command = UserCreateCommand(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        # 模拟用户名已存在
        existing_user = User.create(
            username="testuser",
            email="existing@example.com",
            password_hash="hash",
            first_name="Existing",
            last_name="User"
        )
        self.user_repository.find_by_email.return_value = None
        self.user_repository.find_by_username.return_value = existing_user
        
        # 执行测试并验证异常
        with pytest.raises(UserAlreadyExistsException, match="用户名 testuser 已被使用"):
            await self.service.create_user(command)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """测试成功认证用户"""
        # 创建测试用户
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash=self.password_service.hash_password("password123"),
            first_name="Test",
            last_name="User"
        )
        user.verify_email()  # 验证邮箱
        
        self.user_repository.find_by_email.return_value = user
        
        # 执行测试
        result = await self.service.authenticate_user("test@example.com", "password123")
        
        # 验证结果
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        
        # 验证仓储调用
        self.user_repository.find_by_email.assert_called_once_with("test@example.com")
        self.user_repository.save.assert_called_once()  # 记录登录时间
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        """测试用户不存在的情况"""
        self.user_repository.find_by_email.return_value = None
        
        # 执行测试并验证异常
        with pytest.raises(InvalidCredentialsException, match="邮箱或密码错误"):
            await self.service.authenticate_user("nonexistent@example.com", "password123")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self):
        """测试密码错误的情况"""
        # 创建测试用户
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash=self.password_service.hash_password("password123"),
            first_name="Test",
            last_name="User"
        )
        user.verify_email()
        
        self.user_repository.find_by_email.return_value = user
        
        # 执行测试并验证异常
        with pytest.raises(InvalidCredentialsException, match="邮箱或密码错误"):
            await self.service.authenticate_user("test@example.com", "wrongpassword")
    
    @pytest.mark.asyncio
    async def test_create_user_with_organization(
        self,
        mock_user_repository,
        mock_role_repository,
        mock_api_key_repository,
        sample_user_data
    ):
        """测试创建包含组织信息的用户"""
        # 安排
        mock_user_repository.find_by_email.return_value = None
        mock_user_repository.find_by_username.return_value = None
        mock_role_repository.find_by_name.return_value = MagicMock(name="user")
        
        service = UserApplicationService(
            mock_user_repository,
            mock_role_repository,
            mock_api_key_repository
        )
        
        command = UserCreateCommand(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            organization="TechCorp"
        )

        # 执行
        result = await service.create_user(command)

        # 验证
        assert result.profile.organization == "TechCorp"
        mock_user_repository.save.assert_called_once()

    async def test_create_user_without_organization(
        self,
        mock_user_repository,
        mock_role_repository,
        mock_api_key_repository,
        sample_user_data
    ):
        """测试创建不包含组织信息的用户"""
        # 安排
        mock_user_repository.find_by_email.return_value = None
        mock_user_repository.find_by_username.return_value = None
        mock_role_repository.find_by_name.return_value = MagicMock(name="user")
        
        service = UserApplicationService(
            mock_user_repository,
            mock_role_repository,
            mock_api_key_repository
        )
        
        command = UserCreateCommand(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            organization=None
        )

        # 执行
        result = await service.create_user(command)

        # 验证
        assert result.profile.organization is None
        mock_user_repository.save.assert_called_once()

    async def test_create_user_email_already_exists(
        self,
        mock_user_repository,
        mock_role_repository,
        mock_api_key_repository
    ):
        """测试邮箱已存在的情况"""
        # 安排
        existing_user = MagicMock()
        mock_user_repository.find_by_email.return_value = existing_user
        
        service = UserApplicationService(
            mock_user_repository,
            mock_role_repository,
            mock_api_key_repository
        )
        
        command = UserCreateCommand(
            username="testuser",
            email="existing@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe"
        )

        # 执行与验证
        with pytest.raises(UserAlreadyExistsException) as exc_info:
            await service.create_user(command)
        
        assert "邮箱 existing@example.com 已被使用" in str(exc_info.value)

    async def test_create_user_username_already_exists(
        self,
        mock_user_repository,
        mock_role_repository,
        mock_api_key_repository
    ):
        """测试用户名已存在的情况"""
        # 安排
        mock_user_repository.find_by_email.return_value = None
        existing_user = MagicMock()
        mock_user_repository.find_by_username.return_value = existing_user
        
        service = UserApplicationService(
            mock_user_repository,
            mock_role_repository,
            mock_api_key_repository
        )
        
        command = UserCreateCommand(
            username="existinguser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe"
        )

        # 执行与验证
        with pytest.raises(UserAlreadyExistsException) as exc_info:
            await service.create_user(command)
        
        assert "用户名 existinguser 已被使用" in str(exc_info.value)

    async def test_create_user_assigns_default_role(
        self,
        mock_user_repository,
        mock_role_repository,
        mock_api_key_repository
    ):
        """测试创建用户时分配默认角色"""
        # 安排
        default_role = MagicMock()
        default_role.name = "user"
        
        mock_user_repository.find_by_email.return_value = None
        mock_user_repository.find_by_username.return_value = None
        mock_role_repository.find_by_name.return_value = default_role
        
        service = UserApplicationService(
            mock_user_repository,
            mock_role_repository,
            mock_api_key_repository
        )
        
        command = UserCreateCommand(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe"
        )

        # 执行
        result = await service.create_user(command)

        # 验证
        mock_role_repository.find_by_name.assert_called_once_with("user")
        # 验证用户被保存（间接验证角色被添加）
        mock_user_repository.save.assert_called_once()

    async def test_create_user_no_default_role_available(
        self,
        mock_user_repository,
        mock_role_repository,
        mock_api_key_repository
    ):
        """测试没有默认角色可用的情况"""
        # 安排
        mock_user_repository.find_by_email.return_value = None
        mock_user_repository.find_by_username.return_value = None
        mock_role_repository.find_by_name.return_value = None  # 没有找到默认角色
        
        service = UserApplicationService(
            mock_user_repository,
            mock_role_repository,
            mock_api_key_repository
        )
        
        command = UserCreateCommand(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe"
        )

        # 执行
        result = await service.create_user(command)

        # 验证 - 用户仍然应该被创建，即使没有默认角色
        assert result.username == "testuser"
        mock_user_repository.save.assert_called_once()
        mock_role_repository.find_by_name.assert_called_once_with("user")

    async def test_authenticate_user_email_not_verified(self):
        user = User.create(
            username="testuser", 
            email="test@example.com",
            password_hash=self.password_service.hash_password("password123"),
            first_name="Test",
            last_name="User"
        )
        
        self.user_repository.find_by_email.return_value = user
        
        # 执行测试并验证异常
        with pytest.raises(EmailNotVerifiedException, match="邮箱未验证"):
            await self.service.authenticate_user("test@example.com", "password123")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_suspended(self):
        """测试用户被暂停的情况"""
        # 创建测试用户
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash=self.password_service.hash_password("password123"),
            first_name="Test",
            last_name="User"
        )
        user.verify_email()
        user.suspend("测试暂停")
        
        self.user_repository.find_by_email.return_value = user
        
        # 执行测试并验证异常
        with pytest.raises(ApplicationException, match="账户已被暂停"):
            await self.service.authenticate_user("test@example.com", "password123")
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self):
        """测试成功获取用户"""
        user_id = uuid4()
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        user.id = user_id
        
        self.user_repository.find_by_id.return_value = user
        
        # 执行测试
        result = await self.service.get_user_by_id(user_id)
        
        # 验证结果
        assert result is not None
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        
        # 验证仓储调用
        self.user_repository.find_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """测试用户不存在的情况"""
        user_id = uuid4()
        self.user_repository.find_by_id.return_value = None
        
        # 执行测试
        result = await self.service.get_user_by_id(user_id)
        
        # 验证结果
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self):
        """测试成功更新用户档案"""
        user_id = uuid4()
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        user.id = user_id
        
        self.user_repository.find_by_id.return_value = user
        
        command = UserUpdateCommand(
            user_id=user_id,
            first_name="Updated",
            last_name="Name",
            bio="Updated bio"
        )
        
        # 执行测试
        result = await self.service.update_user_profile(command)
        
        # 验证结果
        assert result.profile.first_name == "Updated"
        assert result.profile.last_name == "Name"
        assert result.profile.bio == "Updated bio"
        
        # 验证仓储调用
        self.user_repository.find_by_id.assert_called_once_with(user_id)
        self.user_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_user_profile_not_found(self):
        """测试更新不存在用户的档案"""
        user_id = uuid4()
        self.user_repository.find_by_id.return_value = None
        
        command = UserUpdateCommand(
            user_id=user_id,
            first_name="Updated",
            last_name="Name"
        )
        
        # 执行测试并验证异常
        with pytest.raises(ApplicationException, match="用户不存在"):
            await self.service.update_user_profile(command)
    
    @pytest.mark.asyncio
    async def test_change_password_success(self):
        """测试成功修改密码"""
        user_id = uuid4()
        old_password = "oldpassword123"
        new_password = "newpassword123"
        
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash=self.password_service.hash_password(old_password),
            first_name="Test",
            last_name="User"
        )
        user.id = user_id
        
        self.user_repository.find_by_id.return_value = user
        
        command = PasswordChangeCommand(
            user_id=user_id,
            current_password=old_password,
            new_password_hash=self.password_service.hash_password(new_password)
        )
        
        # 执行测试
        result = await self.service.change_password(command)
        
        # 验证结果
        assert result == True
        
        # 验证密码已更新
        assert self.password_service.verify_password(new_password, user.password_hash)
        
        # 验证仓储调用
        self.user_repository.find_by_id.assert_called_once_with(user_id)
        self.user_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_current_password(self):
        """测试当前密码错误的情况"""
        user_id = uuid4()
        old_password = "oldpassword123"
        
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash=self.password_service.hash_password(old_password),
            first_name="Test",
            last_name="User"
        )
        user.id = user_id
        
        self.user_repository.find_by_id.return_value = user
        
        command = PasswordChangeCommand(
            user_id=user_id,
            current_password="wrongpassword",
            new_password_hash=self.password_service.hash_password("newpassword123")
        )
        
        # 执行测试并验证异常
        with pytest.raises(InvalidCredentialsException, match="当前密码错误"):
            await self.service.change_password(command)
    
    @pytest.mark.asyncio
    async def test_create_api_key_success(self):
        """测试成功创建API密钥"""
        user_id = uuid4()
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        user.id = user_id
        
        self.user_repository.find_by_id.return_value = user
        
        # 执行测试
        result = await self.service.create_api_key(
            user_id=user_id,
            name="Test Key",
            permissions=["user:read"]
        )
        
        # 验证结果
        assert result.name == "Test Key"
        assert result.permissions == ["user:read"]
        assert result.api_key.startswith("mk-")
        
        # 验证仓储调用
        self.user_repository.find_by_id.assert_called_once_with(user_id)
        self.user_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_revoke_api_key_success(self):
        """测试成功撤销API密钥"""
        user_id = uuid4()
        user = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        user.id = user_id
        
        # 创建API密钥
        api_key = user.create_api_key(
            name="Test Key",
            key_hash="hashed_key",
            permissions=["user:read"]
        )
        
        self.user_repository.find_by_id.return_value = user
        
        # 执行测试
        result = await self.service.revoke_api_key(user_id, api_key.id)
        
        # 验证结果
        assert result == True
        assert api_key.is_active == False
        
        # 验证仓储调用
        self.user_repository.find_by_id.assert_called_once_with(user_id)
        self.user_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_users_success(self):
        """测试成功搜索用户"""
        query = UserSearchQuery(
            keyword="test",
            status="active",
            limit=10,
            offset=0
        )
        
        users = [
            User.create(
                username="testuser1",
                email="test1@example.com",
                password_hash="hash",
                first_name="Test1",
                last_name="User1"
            ),
            User.create(
                username="testuser2",
                email="test2@example.com",
                password_hash="hash",
                first_name="Test2",
                last_name="User2"
            )
        ]
        
        self.user_repository.search.return_value = users
        
        # 执行测试
        result = await self.service.search_users(query)
        
        # 验证结果
        assert len(result) == 2
        assert result[0].username == "testuser1"
        assert result[1].username == "testuser2"
        
        # 验证仓储调用
        self.user_repository.search.assert_called_once_with(query)
    async d
ef test_assign_user_roles_success(
        self, user_service, mock_user_repository, mock_role_repository
    ):
        """测试成功分配用户角色"""
        # 准备
        user_id = uuid4()
        role_ids = [uuid4(), uuid4()]
        
        user = User(
            id=user_id,
            username="testuser",
            email=EmailAddress("test@example.com"),
            password_hash="hashed_password",
            profile=UserProfile(first_name="Test", last_name="User")
        )
        
        roles = [
            Role(
                id=role_ids[0],
                name="role1",
                display_name="角色1",
                description="测试角色1"
            ),
            Role(
                id=role_ids[1],
                name="role2",
                display_name="角色2",
                description="测试角色2"
            )
        ]
        
        mock_user_repository.find_by_id.return_value = user
        mock_role_repository.find_by_id.side_effect = roles
        mock_user_repository.save.return_value = user

        # 执行
        result = await user_service.assign_user_roles(user_id, role_ids)

        # 验证
        assert result.id == user_id
        mock_user_repository.save.assert_called_once()

    async def test_assign_user_roles_user_not_found(
        self, user_service, mock_user_repository
    ):
        """测试分配角色给不存在的用户"""
        # 准备
        user_id = uuid4()
        role_ids = [uuid4()]
        mock_user_repository.find_by_id.return_value = None

        # 执行和验证
        with pytest.raises(ApplicationException, match="用户 .* 不存在"):
            await user_service.assign_user_roles(user_id, role_ids)

    async def test_assign_user_roles_role_not_found(
        self, user_service, mock_user_repository, mock_role_repository
    ):
        """测试分配不存在的角色"""
        # 准备
        user_id = uuid4()
        role_ids = [uuid4()]
        
        user = User(
            id=user_id,
            username="testuser",
            email=EmailAddress("test@example.com"),
            password_hash="hashed_password",
            profile=UserProfile(first_name="Test", last_name="User")
        )
        
        mock_user_repository.find_by_id.return_value = user
        mock_role_repository.find_by_id.return_value = None

        # 执行和验证
        with pytest.raises(ApplicationException, match="角色 .* 不存在"):
            await user_service.assign_user_roles(user_id, role_ids)

    async def test_get_user_permissions_success(
        self, user_service, mock_user_repository
    ):
        """测试成功获取用户权限"""
        # 准备
        user_id = uuid4()
        permission = Permission(
            id=uuid4(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户列表"
        )
        role = Role(
            id=uuid4(),
            name="test_role",
            display_name="测试角色",
            description="测试角色",
            permissions=[permission]
        )
        user = User(
            id=user_id,
            username="testuser",
            email=EmailAddress("test@example.com"),
            password_hash="hashed_password",
            profile=UserProfile(first_name="Test", last_name="User")
        )
        user.add_role(role)
        
        mock_user_repository.find_by_id.return_value = user

        # 执行
        result = await user_service.get_user_permissions(user_id)

        # 验证
        assert result["user_id"] == str(user_id)
        assert result["username"] == user.username
        assert len(result["permissions"]) == 1
        assert permission.name.value in result["permissions"]
        assert len(result["roles"]) == 1

    async def test_get_user_permissions_user_not_found(
        self, user_service, mock_user_repository
    ):
        """测试获取不存在用户的权限"""
        # 准备
        user_id = uuid4()
        mock_user_repository.find_by_id.return_value = None

        # 执行和验证
        with pytest.raises(ApplicationException, match="用户 .* 不存在"):
            await user_service.get_user_permissions(user_id)

    async def test_check_user_permission_success(
        self, user_service, mock_user_repository
    ):
        """测试成功检查用户权限"""
        # 准备
        user_id = uuid4()
        permission_name = "user.users.view"
        
        user = User(
            id=user_id,
            username="testuser",
            email=EmailAddress("test@example.com"),
            password_hash="hashed_password",
            profile=UserProfile(first_name="Test", last_name="User")
        )
        user.has_permission = MagicMock(return_value=True)
        user.is_super_admin = MagicMock(return_value=False)
        
        mock_user_repository.find_by_id.return_value = user

        # 执行
        result = await user_service.check_user_permission(user_id, permission_name)

        # 验证
        assert result["user_id"] == str(user_id)
        assert result["permission"] == permission_name
        assert result["has_permission"] is True
        assert result["is_super_admin"] is False

    async def test_check_user_permission_user_not_found(
        self, user_service, mock_user_repository
    ):
        """测试检查不存在用户的权限"""
        # 准备
        user_id = uuid4()
        permission_name = "user.users.view"
        mock_user_repository.find_by_id.return_value = None

        # 执行和验证
        with pytest.raises(ApplicationException, match="用户 .* 不存在"):
            await user_service.check_user_permission(user_id, permission_name)

    async def test_check_user_permission_by_parts_success(
        self, user_service, mock_user_repository
    ):
        """测试通过资源和操作检查用户权限成功"""
        # 准备
        user_id = uuid4()
        resource = "users"
        action = "view"
        module = "user"
        
        user = User(
            id=user_id,
            username="testuser",
            email=EmailAddress("test@example.com"),
            password_hash="hashed_password",
            profile=UserProfile(first_name="Test", last_name="User")
        )
        user.has_permission_by_parts = MagicMock(return_value=True)
        user.is_super_admin = MagicMock(return_value=False)
        
        mock_user_repository.find_by_id.return_value = user

        # 执行
        result = await user_service.check_user_permission_by_parts(
            user_id, resource, action, module
        )

        # 验证
        assert result["user_id"] == str(user_id)
        assert result["resource"] == resource
        assert result["action"] == action
        assert result["module"] == module
        assert result["has_permission"] is True
        assert result["is_super_admin"] is False