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

"""用户领域 - 仓储接口"""

from abc import abstractmethod
from uuid import UUID
from datetime import datetime

from shared.domain.base import Repository
from user.domain.models import Permission, Role, User, AuditLog


class IUserRepository(Repository[User]):
    """用户仓储接口"""

    @abstractmethod
    async def save(self, user: User) -> User:
        """保存用户"""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> User:
        """删除用户"""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        pass

    @abstractmethod
    async def find_by_status(self, status: str) -> list[User]:
        """根据状态查找用户"""
        pass

    @abstractmethod
    async def search_users(
        self,
        keyword: str | None = None,
        status: str | None = None,
        organization: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[User]:
        """搜索用户"""
        pass

    @abstractmethod
    async def find_by_role_id(self, role_id: UUID) -> list[User]:
        """根据角色ID查找用户"""
        pass

    @abstractmethod
    async def count_users(
        self,
        keyword: str | None = None,
        status: str | None = None,
        organization: str | None = None
    ) -> int:
        """统计用户数量"""
        pass

    @abstractmethod
    async def find_users_with_permissions(self, permission_names: list[str]) -> list[User]:
        """查找拥有指定权限的用户"""
        pass

    @abstractmethod
    async def batch_update_user_roles(self, user_role_updates: list[dict]) -> bool:
        """批量更新用户角色"""
        pass

    @abstractmethod
    async def find_by_ids(self, user_ids: list[UUID]) -> list[User]:
        """批量根据ID查找用户"""
        pass


class IRoleRepository(Repository[Role]):
    """角色仓储接口"""

    @abstractmethod
    async def save(self, role: Role) -> Role:
        """保存角色"""
        pass

    @abstractmethod
    async def delete(self, role_id: UUID) -> Role:
        """删除角色"""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Role | None:
        """根据名称获取角色"""
        pass

    @abstractmethod
    async def get_default_role(self) -> Role:
        """获取默认角色"""
        pass

    @abstractmethod
    async def find_all(self) -> list[Role]:
        """获取所有角色"""
        pass

    @abstractmethod
    async def search_roles(
        self,
        name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Role]:
        """搜索角色"""
        pass

    @abstractmethod
    async def delete(self, role_id: UUID) -> bool:
        """删除角色"""
        pass

    @abstractmethod
    async def find_roles_with_permissions(self, permission_ids: list[UUID] | None = None) -> list[Role]:
        """查找包含指定权限的角色"""
        pass

    @abstractmethod
    async def find_by_ids(self, role_ids: list[UUID]) -> list[Role]:
        """批量根据ID查找角色"""
        pass

    @abstractmethod
    async def count_roles(
        self,
        name: str | None = None,
    ) -> int:
        """统计角色数量"""
        pass


class IPermissionRepository(Repository[Permission]):
    """权限仓储接口"""

    @abstractmethod
    async def save(self, permission: Permission) -> Permission:
        """保存权限"""
        pass

    @abstractmethod
    async def delete(self, permission_id: UUID) -> Permission:
        """删除权限"""
        pass

    @abstractmethod
    async def find_by_resource_action(self, resource: str, action: str) -> Permission | None:
        """根据资源和操作查找权限"""
        pass

    @abstractmethod
    async def find_all(self) -> list[Permission]:
        """获取所有权限"""
        pass

    @abstractmethod
    async def find_by_resource(self, resource: str) -> list[Permission]:
        """根据资源查找权限"""
        pass

    @abstractmethod
    async def find_by_module(self, module: str) -> list[Permission]:
        """根据模块查找权限"""
        pass

    @abstractmethod
    async def find_by_ids(self, permission_ids: list[UUID]) -> list[Permission]:
        """批量根据ID查找权限"""
        pass

    @abstractmethod
    async def find_by_names(self, permission_names: list[str]) -> list[Permission]:
        """批量根据名称查找权限"""
        pass

    @abstractmethod
    async def search_permissions(
        self,
        keyword: str | None = None,
        module: str | None = None,
        resource: str | None = None,
        action: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Permission]:
        """搜索权限"""
        pass

    @abstractmethod
    async def count_permissions(
        self,
        keyword: str | None = None,
        module: str | None = None,
        resource: str | None = None,
    ) -> int:
        """统计权限数量"""
        pass



class IAuditLogRepository(Repository[AuditLog]):
    """审计日志仓储接口"""

    @abstractmethod
    async def save(self, audit_log: AuditLog) -> AuditLog:
        """保存审计日志"""
        pass

    @abstractmethod
    async def find_with_count(self, 
        user_id: UUID | None = None, 
        action = None, start_time: datetime | None = None, 
        end_time: datetime | None = None, 
        success: bool | None = None, 
        limit: int = 20,
         offset: int = 0
    ) -> tuple[list, int]:
        """查找审计日志"""
        pass
    
    @abstractmethod
    async def get_stats(self, start_time: datetime | None = None, end_time: datetime | None = None) -> dict:
        """获取统计数据"""
        pass
    
    @abstractmethod
    async def cleanup_old_logs(self, before_date: datetime) -> int:
        """清理旧的审计日志"""
        pass