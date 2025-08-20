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

"""用户基础设施层 - 权限审计日志服务测试"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID
from uuid_extensions import uuid7

from audit.domain.models import ActionType, AuditResult, ResourceType
from shared.domain.base import EmailAddress
from user.domain.models import (
    Permission, 
    PermissionName, 
    Role, 
    RoleType, 
    User, 
    UserProfile, 
    UserStatus
)
from user.infrastructure.audit_logger import AuditLogger


class TestAuditLogger:
    """AuditLogger测试类"""

    @pytest.fixture
    def audit_logger(self):
        """创建AuditLogger实例"""
        return AuditLogger(enable_async=False)  # 测试时使用同步模式

    @pytest.fixture
    def async_audit_logger(self):
        """创建异步模式的AuditLogger实例"""
        return AuditLogger(enable_async=True)

    @pytest.fixture
    def sample_permission(self):
        """创建示例权限"""
        return Permission(
            id=uuid7(),
            name=PermissionName("user.users.view"),
            display_name="查看用户",
            description="查看用户列表和详情",
            module="user"
        )

    @pytest.fixture
    def sample_role(self, sample_permission):
        """创建示例角色"""
        return Role(
            id=uuid7(),
            name="admin",
            display_name="管理员",
            description="系统管理员角色",
            permissions=[sample_permission],
            is_system_role=True,
            role_type=RoleType.ADMIN
        )

    @pytest.fixture
    def sample_user(self, sample_role):
        """创建示例用户"""
        user = User(
            id=uuid7(),
            username="testuser",
            email=EmailAddress("test@example.com"),
            password_hash="hashed_password",
            profile=UserProfile(
                first_name="Test",
                last_name="User",
                organization="Test Org"
            ),
            status=UserStatus.ACTIVE,
            email_verified=True
        )
        user.add_role(sample_role)
        return user

    @pytest.mark.asyncio
    async def test_log_permission_created(self, audit_logger, sample_permission):
        """测试记录权限创建操作"""
        operator_id = uuid7()
        operator_username = "admin"
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0"
        request_id = "req-123"

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_permission_created(
                permission=sample_permission,
                operator_id=operator_id,
                operator_username=operator_username,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id
            )

            # 验证调用参数
            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.PERMISSION_CREATE
            assert call_args['description'] == f"创建权限: {sample_permission.name.value} ({sample_permission.display_name})"
            assert call_args['resource_type'] == ResourceType.PERMISSION
            assert call_args['resource_id'] == sample_permission.id
            assert call_args['user_id'] == operator_id
            assert call_args['username'] == operator_username
            assert call_args['ip_address'] == ip_address
            assert call_args['user_agent'] == user_agent
            assert call_args['request_id'] == request_id
            assert call_args['result'] == AuditResult.SUCCESS
            
            # 验证元数据
            metadata = call_args['metadata']
            assert metadata['permission_id'] == str(sample_permission.id)
            assert metadata['permission_name'] == sample_permission.name.value
            assert metadata['permission_display_name'] == sample_permission.display_name
            assert metadata['permission_module'] == sample_permission.module
            assert metadata['permission_resource'] == sample_permission.resource
            assert metadata['permission_action'] == sample_permission.action

    @pytest.mark.asyncio
    async def test_log_permission_updated(self, audit_logger, sample_permission):
        """测试记录权限更新操作"""
        old_data = {
            "display_name": "旧显示名称",
            "description": "旧描述"
        }
        new_data = {
            "display_name": "新显示名称",
            "description": "新描述"
        }

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_permission_updated(
                permission=sample_permission,
                old_data=old_data,
                new_data=new_data,
                operator_id=uuid7(),
                operator_username="admin"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.PERMISSION_UPDATE
            assert call_args['description'] == f"更新权限: {sample_permission.name.value} ({sample_permission.display_name})"
            
            # 验证变更对比
            metadata = call_args['metadata']
            assert 'changes' in metadata
            changes = metadata['changes']
            assert 'display_name' in changes
            assert changes['display_name']['old'] == "旧显示名称"
            assert changes['display_name']['new'] == "新显示名称"
            assert 'description' in changes
            assert changes['description']['old'] == "旧描述"
            assert changes['description']['new'] == "新描述"

    @pytest.mark.asyncio
    async def test_log_permission_deleted(self, audit_logger, sample_permission):
        """测试记录权限删除操作"""
        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_permission_deleted(
                permission=sample_permission,
                operator_id=uuid7(),
                operator_username="admin"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.PERMISSION_DELETE
            assert call_args['description'] == f"删除权限: {sample_permission.name.value} ({sample_permission.display_name})"
            assert call_args['resource_type'] == ResourceType.PERMISSION
            assert call_args['resource_id'] == sample_permission.id

    @pytest.mark.asyncio
    async def test_log_role_created(self, audit_logger, sample_role):
        """测试记录角色创建操作"""
        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_role_created(
                role=sample_role,
                operator_id=uuid7(),
                operator_username="admin"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.ROLE_CREATE
            assert call_args['description'] == f"创建角色: {sample_role.name} ({sample_role.display_name})"
            assert call_args['resource_type'] == ResourceType.ROLE
            assert call_args['resource_id'] == sample_role.id
            
            # 验证元数据
            metadata = call_args['metadata']
            assert metadata['role_id'] == str(sample_role.id)
            assert metadata['role_name'] == sample_role.name
            assert metadata['role_display_name'] == sample_role.display_name
            assert metadata['role_type'] == sample_role.role_type.value
            assert metadata['is_system_role'] == sample_role.is_system_role
            assert len(metadata['permissions']) == len(sample_role.permissions)

    @pytest.mark.asyncio
    async def test_log_role_updated(self, audit_logger, sample_role):
        """测试记录角色更新操作"""
        old_data = {"display_name": "旧角色名"}
        new_data = {"display_name": "新角色名"}

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_role_updated(
                role=sample_role,
                old_data=old_data,
                new_data=new_data,
                operator_id=uuid7(),
                operator_username="admin"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.ROLE_UPDATE
            assert call_args['description'] == f"更新角色: {sample_role.name} ({sample_role.display_name})"

    @pytest.mark.asyncio
    async def test_log_role_deleted(self, audit_logger, sample_role):
        """测试记录角色删除操作"""
        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_role_deleted(
                role=sample_role,
                operator_id=uuid7(),
                operator_username="admin"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.ROLE_DELETE
            assert call_args['description'] == f"删除角色: {sample_role.name} ({sample_role.display_name})"
            assert call_args['resource_type'] == ResourceType.ROLE
            assert call_args['resource_id'] == sample_role.id

    @pytest.mark.asyncio
    async def test_log_role_permissions_updated(self, audit_logger, sample_role, sample_permission):
        """测试记录角色权限更新操作"""
        new_permission = Permission(
            id=uuid7(),
            name=PermissionName("user.users.create"),
            display_name="创建用户",
            description="创建新用户",
            module="user"
        )
        
        added_permissions = [new_permission]
        removed_permissions = []

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_role_permissions_updated(
                role=sample_role,
                added_permissions=added_permissions,
                removed_permissions=removed_permissions,
                operator_id=uuid7(),
                operator_username="admin"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.PERMISSION_GRANT
            assert call_args['description'] == f"更新角色权限: {sample_role.name} ({sample_role.display_name})"
            
            # 验证元数据
            metadata = call_args['metadata']
            assert metadata['added_count'] == 1
            assert metadata['removed_count'] == 0
            assert new_permission.name.value in metadata['added_permissions']

    @pytest.mark.asyncio
    async def test_log_user_roles_assigned(self, audit_logger, sample_user, sample_role):
        """测试记录用户角色分配操作"""
        assigned_roles = [sample_role]

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_user_roles_assigned(
                user=sample_user,
                assigned_roles=assigned_roles,
                operator_id=uuid7(),
                operator_username="admin"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.ROLE_ASSIGN
            assert call_args['description'] == f"为用户分配角色: {sample_user.username} ({sample_user.profile.full_name})"
            assert call_args['resource_type'] == ResourceType.USER
            assert call_args['resource_id'] == sample_user.id
            
            # 验证元数据
            metadata = call_args['metadata']
            assert metadata['target_user_id'] == str(sample_user.id)
            assert metadata['target_username'] == sample_user.username
            assert metadata['role_count'] == 1
            assert len(metadata['assigned_roles']) == 1
            assert metadata['assigned_roles'][0]['name'] == sample_role.name

    @pytest.mark.asyncio
    async def test_log_user_roles_revoked(self, audit_logger, sample_user, sample_role):
        """测试记录用户角色撤销操作"""
        revoked_roles = [sample_role]

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_user_roles_revoked(
                user=sample_user,
                revoked_roles=revoked_roles,
                operator_id=uuid7(),
                operator_username="admin"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.ROLE_REVOKE
            assert call_args['description'] == f"撤销用户角色: {sample_user.username} ({sample_user.profile.full_name})"
            assert call_args['resource_type'] == ResourceType.USER
            assert call_args['resource_id'] == sample_user.id

    @pytest.mark.asyncio
    async def test_log_permission_check_success(self, audit_logger, sample_user):
        """测试记录权限检查成功操作"""
        permission_name = "user.users.view"
        granted_by_roles = ["admin"]

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_permission_check(
                user=sample_user,
                permission_name=permission_name,
                has_permission=True,
                granted_by_roles=granted_by_roles
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.ADMIN_OPERATION
            assert call_args['description'] == f"权限检查: {sample_user.username} 检查权限 {permission_name}"
            assert call_args['result'] == AuditResult.SUCCESS
            assert call_args['error_message'] is None
            
            # 验证元数据
            metadata = call_args['metadata']
            assert metadata['permission_name'] == permission_name
            assert metadata['has_permission'] is True
            assert metadata['granted_by_roles'] == granted_by_roles

    @pytest.mark.asyncio
    async def test_log_permission_check_failure(self, audit_logger, sample_user):
        """测试记录权限检查失败操作"""
        permission_name = "user.users.delete"

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_permission_check(
                user=sample_user,
                permission_name=permission_name,
                has_permission=False
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            assert call_args['action'] == ActionType.ADMIN_OPERATION
            assert call_args['result'] == AuditResult.FAILURE
            assert call_args['error_message'] == f"权限不足: {permission_name}"
            
            # 验证元数据
            metadata = call_args['metadata']
            assert metadata['permission_name'] == permission_name
            assert metadata['has_permission'] is False

    @pytest.mark.asyncio
    async def test_async_mode_creates_task(self, async_audit_logger, sample_permission):
        """测试异步模式创建任务"""
        with patch('asyncio.create_task') as mock_create_task:
            mock_create_task.return_value = MagicMock()

            await async_audit_logger.log_permission_created(
                permission=sample_permission,
                operator_id=uuid7(),
                operator_username="admin"
            )

            # 验证创建了异步任务
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_changes_diff(self, audit_logger):
        """测试变更对比生成"""
        old_data = {
            "name": "old_name",
            "description": "old_desc",
            "unchanged": "same_value"
        }
        new_data = {
            "name": "new_name",
            "description": "new_desc",
            "unchanged": "same_value",
            "new_field": "new_value"
        }

        changes = audit_logger._generate_changes_diff(old_data, new_data)

        # 验证变更检测
        assert "name" in changes
        assert changes["name"]["old"] == "old_name"
        assert changes["name"]["new"] == "new_name"
        
        assert "description" in changes
        assert changes["description"]["old"] == "old_desc"
        assert changes["description"]["new"] == "new_desc"
        
        assert "new_field" in changes
        assert changes["new_field"]["old"] is None
        assert changes["new_field"]["new"] == "new_value"
        
        # 未变更的字段不应该在变更中
        assert "unchanged" not in changes

    @pytest.mark.asyncio
    async def test_error_handling_in_async_write(self, async_audit_logger, sample_permission):
        """测试异步写入时的错误处理"""
        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.side_effect = Exception("Database error")
            
            # 异步模式下，错误不应该影响主流程
            with patch('asyncio.create_task') as mock_create_task:
                # 模拟任务执行
                async def mock_task():
                    await async_audit_logger._write_audit_log_async({
                        "action": ActionType.PERMISSION_CREATE,
                        "description": "test"
                    })
                
                mock_create_task.return_value = asyncio.create_task(mock_task())
                
                # 这不应该抛出异常
                await async_audit_logger.log_permission_created(
                    permission=sample_permission,
                    operator_id=uuid7(),
                    operator_username="admin"
                )

    def test_set_async_mode(self, audit_logger):
        """测试设置异步模式"""
        assert audit_logger.enable_async is False
        
        audit_logger.set_async_mode(True)
        assert audit_logger.enable_async is True
        
        audit_logger.set_async_mode(False)
        assert audit_logger.enable_async is False

    @pytest.mark.asyncio
    async def test_flush_pending_logs(self, audit_logger):
        """测试刷新待写入日志"""
        # 当前实现为空方法，测试不抛出异常
        await audit_logger.flush_pending_logs()

    @pytest.mark.asyncio
    async def test_log_with_minimal_parameters(self, audit_logger, sample_permission):
        """测试使用最少参数记录日志"""
        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_permission_created(
                permission=sample_permission
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            # 验证必需参数
            assert call_args['action'] == ActionType.PERMISSION_CREATE
            assert call_args['resource_id'] == sample_permission.id
            
            # 验证可选参数为None
            assert call_args['user_id'] is None
            assert call_args['username'] is None
            assert call_args['ip_address'] is None
            assert call_args['user_agent'] is None
            assert call_args['request_id'] is None

    @pytest.mark.asyncio
    async def test_log_with_all_parameters(self, audit_logger, sample_permission):
        """测试使用所有参数记录日志"""
        operator_id = uuid7()
        operator_username = "admin"
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0"
        request_id = "req-123"

        with patch('user.infrastructure.audit_logger.log_user_action') as mock_log:
            mock_log.return_value = None

            await audit_logger.log_permission_created(
                permission=sample_permission,
                operator_id=operator_id,
                operator_username=operator_username,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            
            # 验证所有参数都被正确传递
            assert call_args['user_id'] == operator_id
            assert call_args['username'] == operator_username
            assert call_args['ip_address'] == ip_address
            assert call_args['user_agent'] == user_agent
            assert call_args['request_id'] == request_id