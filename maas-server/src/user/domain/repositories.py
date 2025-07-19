"""用户领域 - 仓储接口"""

from abc import abstractmethod
from uuid import UUID

from shared.domain.base import Repository
from user.domain.models import ApiKey, Role, User


class UserRepository(Repository[User]):
    """用户仓储接口"""

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        pass

    @abstractmethod
    async def find_by_api_key_hash(self, key_hash: str) -> User | None:
        """根据API密钥哈希查找用户"""
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
    async def search(self, query) -> list[User]:
        """搜索用户"""
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


class RoleRepository(Repository[Role]):
    """角色仓储接口"""

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


class ApiKeyRepository(Repository[ApiKey]):
    """API密钥仓储接口"""

    @abstractmethod
    async def find_by_key_hash(self, key_hash: str) -> ApiKey | None:
        """根据密钥哈希获取API密钥"""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> list[ApiKey]:
        """根据用户ID查找API密钥"""
        pass

    @abstractmethod
    async def get_active_keys_by_user(self, user_id: UUID) -> list[ApiKey]:
        """获取用户的有效API密钥"""
        pass

    @abstractmethod
    async def delete_expired_keys(self) -> int:
        """删除过期的API密钥"""
        pass
