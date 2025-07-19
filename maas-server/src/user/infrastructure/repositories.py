"""用户基础设施层 - 仓储实现"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.domain.base import EmailAddress
from shared.infrastructure.repository import SQLAlchemyRepository
from user.domain.models import (
    ApiKey,
    Permission,
    Role,
    User,
    UserProfile,
    UserQuota,
    UserStatus,
)
from user.domain.repositories import ApiKeyRepository, RoleRepository, UserRepository
from user.infrastructure.models import ApiKeyORM, RoleORM, UserORM, UserRoleORM


class SQLAlchemyUserRepository(SQLAlchemyRepository[User, UserORM], UserRepository):
    """SQLAlchemy用户仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserORM)

    async def get_by_uuid(self, user_uuid: UUID) -> User | None:
        """根据UUID获取用户"""
        stmt = (
            select(UserORM)
            .where(UserORM.uuid == user_uuid)
            .options(
                selectinload(UserORM.roles),
                selectinload(UserORM.api_keys),
                selectinload(UserORM.quota)
            )
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        stmt = (
            select(UserORM)
            .where(UserORM.email == email)
            .options(
                selectinload(UserORM.roles),
                selectinload(UserORM.api_keys),
                selectinload(UserORM.quota)
            )
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        stmt = (
            select(UserORM)
            .where(UserORM.username == username)
            .options(
                selectinload(UserORM.roles),
                selectinload(UserORM.api_keys),
                selectinload(UserORM.quota)
            )
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        stmt = select(func.count(UserORM.id)).where(UserORM.email == email)
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        stmt = select(func.count(UserORM.id)).where(UserORM.username == username)
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def find_by_status(self, status: str) -> list[User]:
        """根据状态查找用户"""
        stmt = (
            select(UserORM)
            .where(UserORM.status == status)
            .options(
                selectinload(UserORM.roles),
                selectinload(UserORM.api_keys),
                selectinload(UserORM.quota)
            )
        )
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def search_users(
        self,
        keyword: str | None = None,
        status: str | None = None,
        organization: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[User]:
        """搜索用户"""
        stmt = select(UserORM).options(
            selectinload(UserORM.roles),
            selectinload(UserORM.api_keys),
            selectinload(UserORM.quota)
        )

        conditions = []
        if keyword:
            conditions.append(
                or_(
                    UserORM.username.ilike(f"%{keyword}%"),
                    UserORM.email.ilike(f"%{keyword}%"),
                    UserORM.first_name.ilike(f"%{keyword}%"),
                    UserORM.last_name.ilike(f"%{keyword}%")
                )
            )
        if status:
            conditions.append(UserORM.status == status)
        if organization:
            conditions.append(UserORM.organization.ilike(f"%{organization}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def count_users(
        self,
        keyword: str | None = None,
        status: str | None = None,
        organization: str | None = None
    ) -> int:
        """统计用户数量"""
        stmt = select(func.count(UserORM.id))

        conditions = []
        if keyword:
            conditions.append(
                or_(
                    UserORM.username.ilike(f"%{keyword}%"),
                    UserORM.email.ilike(f"%{keyword}%"),
                    UserORM.first_name.ilike(f"%{keyword}%"),
                    UserORM.last_name.ilike(f"%{keyword}%")
                )
            )
        if status:
            conditions.append(UserORM.status == status)
        if organization:
            conditions.append(UserORM.organization.ilike(f"%{organization}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self.session.execute(stmt)
        return result.scalar()

    def _to_domain_entity(self, orm_obj: UserORM) -> User:
        """将ORM对象转换为领域实体"""
        if not orm_obj:
            return None

        # 构建用户档案
        profile = UserProfile(
            first_name=orm_obj.first_name or "",
            last_name=orm_obj.last_name or "",
            avatar_url=orm_obj.avatar_url,
            organization=orm_obj.organization,
            bio=orm_obj.bio
        )

        # 构建用户实体
        user = User(
            id=orm_obj.uuid,  # 使用UUID作为领域实体ID
            username=orm_obj.username,
            email=EmailAddress(orm_obj.email),
            password_hash=orm_obj.password_hash,
            profile=profile,
            status=UserStatus(orm_obj.status),
            email_verified=orm_obj.email_verified,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            last_login_at=orm_obj.last_login_at
        )

        # 设置角色
        if orm_obj.roles:
            for role_orm in orm_obj.roles:
                role = Role(
                    id=role_orm.uuid,  # 使用UUID作为领域实体ID
                    name=role_orm.name,
                    description=role_orm.description,
                    permissions=[]  # 权限需要单独加载
                )
                user.add_role(role)

        # 设置API密钥
        if orm_obj.api_keys:
            for key_orm in orm_obj.api_keys:
                api_key = ApiKey(
                    id=key_orm.uuid,  # 使用UUID作为领域实体ID
                    name=key_orm.name,
                    key_hash=key_orm.key_hash,
                    permissions=key_orm.permissions or [],
                    expires_at=key_orm.expires_at,
                    last_used_at=key_orm.last_used_at,
                    created_at=key_orm.created_at
                )
                api_key.is_active = key_orm.status == "active"
                user._api_keys.append(api_key)

        # 设置配额
        if orm_obj.quota:
            quota = UserQuota(
                api_calls_limit=orm_obj.quota.api_calls_limit,
                api_calls_used=orm_obj.quota.api_calls_used,
                storage_limit=orm_obj.quota.storage_limit,
                storage_used=orm_obj.quota.storage_used,
                compute_hours_limit=orm_obj.quota.compute_hours_limit,
                compute_hours_used=orm_obj.quota.compute_hours_used
            )
            user.set_quota(quota)

        return user

    def _create_orm_object(self, user: User) -> UserORM:
        """创建ORM对象"""
        return UserORM(
            uuid=user.id,  # 领域实体ID作为UUID
            username=user.username,
            email=user.email.value,
            password_hash=user.password_hash,
            first_name=user.profile.first_name,
            last_name=user.profile.last_name,
            avatar_url=user.profile.avatar_url,
            organization=user.profile.organization,
            bio=user.profile.bio,
            status=user.status.value,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )

    def _update_orm_object(self, orm_obj: UserORM, user: User) -> UserORM:
        """更新ORM对象"""
        orm_obj.uuid = user.id  # 更新UUID
        orm_obj.username = user.username
        orm_obj.email = user.email.value
        orm_obj.password_hash = user.password_hash
        orm_obj.first_name = user.profile.first_name
        orm_obj.last_name = user.profile.last_name
        orm_obj.avatar_url = user.profile.avatar_url
        orm_obj.organization = user.profile.organization
        orm_obj.bio = user.profile.bio
        orm_obj.status = user.status.value
        orm_obj.email_verified = user.email_verified
        orm_obj.updated_at = user.updated_at
        orm_obj.last_login_at = user.last_login_at
        return orm_obj


class SQLAlchemyRoleRepository(SQLAlchemyRepository[Role, RoleORM], RoleRepository):
    """SQLAlchemy角色仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RoleORM)

    async def get_by_uuid(self, role_uuid: UUID) -> Role | None:
        """根据UUID获取角色"""
        stmt = select(RoleORM).where(RoleORM.uuid == role_uuid)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_by_name(self, name: str) -> Role | None:
        """根据名称获取角色"""
        stmt = select(RoleORM).where(RoleORM.name == name)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_default_role(self) -> Role:
        """获取默认角色"""
        return await self.get_by_name("user")

    async def find_all(self) -> list[Role]:
        """获取所有角色"""
        stmt = select(RoleORM)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    def _to_domain_entity(self, orm_obj: RoleORM) -> Role:
        """将ORM对象转换为领域实体"""
        if not orm_obj:
            return None

        # 转换权限
        permissions = []
        for perm_data in orm_obj.permissions or []:
            if isinstance(perm_data, str):
                # 简单字符串格式 "resource:action"
                parts = perm_data.split(":")
                if len(parts) == 2:
                    permission = Permission(
                        id=UUID(int=0),  # 临时ID
                        name=perm_data,
                        description=f"Permission for {perm_data}",
                        resource=parts[0],
                        action=parts[1]
                    )
                    permissions.append(permission)

        return Role(
            id=orm_obj.uuid,  # 使用UUID作为领域实体ID
            name=orm_obj.name,
            description=orm_obj.description,
            permissions=permissions
        )

    def _create_orm_object(self, role: Role) -> RoleORM:
        """创建ORM对象"""
        permissions = [str(perm) for perm in role.permissions]
        return RoleORM(
            uuid=role.id,  # 领域实体ID作为UUID
            name=role.name,
            description=role.description,
            permissions=permissions
        )

    def _update_orm_object(self, orm_obj: RoleORM, role: Role) -> RoleORM:
        """更新ORM对象"""
        permissions = [str(perm) for perm in role.permissions]
        orm_obj.uuid = role.id  # 更新UUID
        orm_obj.name = role.name
        orm_obj.description = role.description
        orm_obj.permissions = permissions
        return orm_obj


class SQLAlchemyApiKeyRepository(SQLAlchemyRepository[ApiKey, ApiKeyORM], ApiKeyRepository):
    """SQLAlchemy API密钥仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ApiKeyORM)

    async def get_by_uuid(self, api_key_uuid: UUID) -> ApiKey | None:
        """根据UUID获取API密钥"""
        stmt = select(ApiKeyORM).where(ApiKeyORM.uuid == api_key_uuid)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_by_key_hash(self, key_hash: str) -> ApiKey | None:
        """根据密钥哈希获取API密钥"""
        stmt = select(ApiKeyORM).where(ApiKeyORM.key_hash == key_hash)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def find_by_user_uuid(self, user_uuid: UUID) -> list[ApiKey]:
        """根据用户UUID查找API密钥"""
        stmt = select(ApiKeyORM).where(ApiKeyORM.user_uuid == user_uuid)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def get_active_keys_by_user(self, user_uuid: UUID) -> list[ApiKey]:
        """获取用户的有效API密钥"""
        stmt = select(ApiKeyORM).where(
            and_(
                ApiKeyORM.user_uuid == user_uuid,
                ApiKeyORM.status == "active"
            )
        )
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def delete_expired_keys(self) -> int:
        """删除过期的API密钥"""
        from sqlalchemy import update

        # 使用update而不是delete，将状态设置为过期
        stmt = update(ApiKeyORM).where(
            and_(
                ApiKeyORM.expires_at.isnot(None),
                ApiKeyORM.expires_at < datetime.now(UTC)
            )
        ).values(status="expired")

        result = await self.session.execute(stmt)
        return result.rowcount

    def _to_domain_entity(self, orm_obj: ApiKeyORM) -> ApiKey:
        """将ORM对象转换为领域实体"""
        if not orm_obj:
            return None

        api_key = ApiKey(
            id=orm_obj.uuid,  # 使用UUID作为领域实体ID
            name=orm_obj.name,
            key_hash=orm_obj.key_hash,
            permissions=orm_obj.permissions or [],
            expires_at=orm_obj.expires_at,
            last_used_at=orm_obj.last_used_at,
            created_at=orm_obj.created_at
        )
        api_key.is_active = orm_obj.status == "active"
        return api_key

    def _create_orm_object(self, api_key: ApiKey) -> ApiKeyORM:
        """创建ORM对象"""
        return ApiKeyORM(
            uuid=api_key.id,  # 领域实体ID作为UUID
            name=api_key.name,
            key_hash=api_key.key_hash,
            permissions=api_key.permissions,
            expires_at=api_key.expires_at,
            last_used_at=api_key.last_used_at,
            status="active" if api_key.is_active else "inactive",
            created_at=api_key.created_at
        )

    def _update_orm_object(self, orm_obj: ApiKeyORM, api_key: ApiKey) -> ApiKeyORM:
        """更新ORM对象"""
        orm_obj.uuid = api_key.id  # 更新UUID
        orm_obj.name = api_key.name
        orm_obj.permissions = api_key.permissions
        orm_obj.expires_at = api_key.expires_at
        orm_obj.last_used_at = api_key.last_used_at
        orm_obj.status = "active" if api_key.is_active else "inactive"
        return orm_obj
