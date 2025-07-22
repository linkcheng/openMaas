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
from user.infrastructure.models import ApiKeyORM, RoleORM, UserORM, UserQuotaORM


class SQLAlchemyUserRepository(SQLAlchemyRepository[User, UserORM], UserRepository):
    """SQLAlchemy用户仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserORM)

    async def save(self, user: User) -> User:
        """保存用户"""
        # 查找现有用户
        stmt = select(UserORM).where(UserORM.user_id == user.id)
        result = await self.session.execute(stmt)
        existing_orm = result.scalar_one_or_none()

        if existing_orm:
            # 更新现有用户
            self._update_orm_object(existing_orm, user)
            # 处理角色关联
            await self._sync_user_roles(existing_orm, user)
            # 处理API密钥
            await self._sync_user_api_keys(existing_orm, user)
            # 处理配额
            await self._sync_user_quota(existing_orm, user)
        else:
            # 创建新用户
            new_orm = self._create_orm_object(user)
            self.session.add(new_orm)
            await self.session.flush()  # 获取自增ID

            # 处理角色关联
            await self._sync_user_roles(new_orm, user)
            # 处理API密钥
            await self._sync_user_api_keys(new_orm, user)
            # 处理配额
            await self._sync_user_quota(new_orm, user)

        await self.session.commit()
        return user

    async def _sync_user_roles(self, user_orm: UserORM, user: User):
        """同步用户角色"""
        from uuid_extensions import uuid7

        from user.infrastructure.models import UserRoleORM

        # 获取现有角色关联
        stmt = select(UserRoleORM).where(UserRoleORM.user_id == user.id)
        result = await self.session.execute(stmt)
        existing_roles = result.scalars().all()
        existing_role_ids = {role_rel.role_id for role_rel in existing_roles}

        # 获取当前用户应有的角色ID
        current_role_ids = {role.id for role in user.roles}

        # 如果角色没有变化，直接返回
        if existing_role_ids == current_role_ids:
            return

        # 删除不再需要的角色关联
        roles_to_remove = existing_role_ids - current_role_ids
        if roles_to_remove:
            for role_rel in existing_roles:
                if role_rel.role_id in roles_to_remove:
                    await self.session.delete(role_rel)

        # 添加新的角色关联
        roles_to_add = current_role_ids - existing_role_ids
        for role in user.roles:
            if role.id in roles_to_add:
                role_rel = UserRoleORM(
                    user_role_id=uuid7(),  # 添加必需的user_role_id字段
                    user_id=user.id,
                    role_id=role.id
                )
                self.session.add(role_rel)

    async def _sync_user_api_keys(self, user_orm: UserORM, user: User):
        """同步用户API密钥"""
        # 删除现有API密钥
        stmt = select(ApiKeyORM).where(ApiKeyORM.user_id == user.id)
        result = await self.session.execute(stmt)
        existing_keys = result.scalars().all()
        for key in existing_keys:
            await self.session.delete(key)

        # 添加新的API密钥
        for api_key in user.api_keys:
            key_orm = ApiKeyORM(
                api_key_id=api_key.id,
                user_id=user.id,
                name=api_key.name,
                key_hash=api_key.key_hash,
                permissions=api_key.permissions,
                expires_at=api_key.expires_at,
                last_used_at=api_key.last_used_at,
                status="active" if api_key.is_active else "inactive",
                created_at=api_key.created_at
            )
            self.session.add(key_orm)

    async def _sync_user_quota(self, user_orm: UserORM, user: User):
        """同步用户配额"""
        if user.quota:
            # 查找现有配额
            stmt = select(UserQuotaORM).where(UserQuotaORM.user_id == user.id)
            result = await self.session.execute(stmt)
            existing_quota = result.scalar_one_or_none()

            if existing_quota:
                # 更新现有配额
                existing_quota.api_calls_limit = user.quota.api_calls_limit
                existing_quota.api_calls_used = user.quota.api_calls_used
                existing_quota.storage_limit = user.quota.storage_limit
                existing_quota.storage_used = user.quota.storage_used
                existing_quota.compute_hours_limit = user.quota.compute_hours_limit
                existing_quota.compute_hours_used = user.quota.compute_hours_used
                existing_quota.updated_at = datetime.now(UTC)
            else:
                # 创建新配额
                quota_orm = UserQuotaORM(
                    user_id=user.id,
                    api_calls_limit=user.quota.api_calls_limit,
                    api_calls_used=user.quota.api_calls_used,
                    storage_limit=user.quota.storage_limit,
                    storage_used=user.quota.storage_used,
                    compute_hours_limit=user.quota.compute_hours_limit,
                    compute_hours_used=user.quota.compute_hours_used
                )
                self.session.add(quota_orm)

    async def find_by_id(self, user_id: UUID) -> User | None:
        """根据ID获取用户"""
        stmt = (
            select(UserORM)
            .where(UserORM.user_id == user_id)
            .options(
                selectinload(UserORM.roles),
                selectinload(UserORM.api_keys),
                selectinload(UserORM.quota)
            )
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def find_by_email(self, email: str) -> User | None:
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

    async def find_by_username(self, username: str) -> User | None:
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

    async def find_by_api_key_hash(self, key_hash: str) -> User | None:
        """根据API密钥哈希查找用户"""
        stmt = (
            select(UserORM)
            .join(ApiKeyORM, UserORM.user_id == ApiKeyORM.user_id)
            .where(ApiKeyORM.key_hash == key_hash)
            .options(
                selectinload(UserORM.roles),
                selectinload(UserORM.api_keys),
                selectinload(UserORM.quota)
            )
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def search(self, query) -> list[User]:
        """搜索用户"""
        stmt = select(UserORM).options(
            selectinload(UserORM.roles),
            selectinload(UserORM.api_keys),
            selectinload(UserORM.quota)
        )

        conditions = []
        if query.keyword:
            conditions.append(
                or_(
                    UserORM.username.ilike(f"%{query.keyword}%"),
                    UserORM.email.ilike(f"%{query.keyword}%"),
                    UserORM.first_name.ilike(f"%{query.keyword}%"),
                    UserORM.last_name.ilike(f"%{query.keyword}%")
                )
            )
        if query.status:
            conditions.append(UserORM.status == query.status)
        if query.organization:
            conditions.append(UserORM.organization.ilike(f"%{query.organization}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(query.offset).limit(query.limit)
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

    async def find_users_by_ids(self, user_ids: list[UUID]) -> list[User]:
        """批量根据ID查找用户"""
        if not user_ids:
            return []

        stmt = (
            select(UserORM)
            .where(UserORM.user_id.in_(user_ids))
            .options(
                selectinload(UserORM.roles),
                selectinload(UserORM.api_keys),
                selectinload(UserORM.quota)
            )
        )
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def find_active_users_with_expired_keys(self) -> list[User]:
        """查找有过期API密钥的活跃用户"""
        stmt = (
            select(UserORM)
            .join(ApiKeyORM, UserORM.user_id == ApiKeyORM.user_id)
            .where(
                and_(
                    UserORM.status == "active",
                    ApiKeyORM.expires_at.isnot(None),
                    ApiKeyORM.expires_at < datetime.now(UTC),
                    ApiKeyORM.status == "active"
                )
            )
            .options(
                selectinload(UserORM.roles),
                selectinload(UserORM.api_keys),
                selectinload(UserORM.quota)
            )
            .distinct()
        )
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def get_user_statistics(self) -> dict:
        """获取用户统计信息"""
        # 总用户数
        total_users_stmt = select(func.count(UserORM.id))
        total_users = await self.session.scalar(total_users_stmt)

        # 活跃用户数
        active_users_stmt = select(func.count(UserORM.id)).where(UserORM.status == "active")
        active_users = await self.session.scalar(active_users_stmt)

        # 已验证邮箱用户数
        verified_users_stmt = select(func.count(UserORM.id)).where(UserORM.email_verified == True)
        verified_users = await self.session.scalar(verified_users_stmt)

        # 本月新注册用户数
        current_month = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_stmt = select(func.count(UserORM.id)).where(UserORM.created_at >= current_month)
        new_users = await self.session.scalar(new_users_stmt)

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "new_users_this_month": new_users
        }

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
            id=orm_obj.user_id,  # 使用业务ID作为领域实体ID
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
                # 转换权限
                permissions = []
                for perm_data in role_orm.permissions or []:
                    if isinstance(perm_data, str):
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

                role = Role(
                    id=role_orm.role_id,  # 使用业务ID作为领域实体ID
                    name=role_orm.name,
                    description=role_orm.description,
                    permissions=permissions
                )
                user.add_role(role)

        # 设置API密钥
        if orm_obj.api_keys:
            for key_orm in orm_obj.api_keys:
                api_key = ApiKey(
                    id=key_orm.api_key_id,  # 使用业务ID作为领域实体ID
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
            user_id=user.id,  # 领域实体ID作为业务ID
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
        orm_obj.user_id = user.id  # 更新业务ID
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

    async def find_by_id(self, role_id: UUID) -> Role | None:
        """根据ID获取角色"""
        stmt = select(RoleORM).where(RoleORM.role_id == role_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def find_by_name(self, name: str) -> Role | None:
        """根据名称获取角色"""
        stmt = select(RoleORM).where(RoleORM.name == name)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_default_role(self) -> Role:
        """获取默认角色"""
        return await self.find_by_name("user")

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
            id=orm_obj.role_id,  # 使用业务ID作为领域实体ID
            name=orm_obj.name,
            description=orm_obj.description,
            permissions=permissions
        )

    def _create_orm_object(self, role: Role) -> RoleORM:
        """创建ORM对象"""
        permissions = [str(perm) for perm in role.permissions]
        return RoleORM(
            role_id=role.id,  # 领域实体ID作为业务ID
            name=role.name,
            description=role.description,
            permissions=permissions
        )

    def _update_orm_object(self, orm_obj: RoleORM, role: Role) -> RoleORM:
        """更新ORM对象"""
        permissions = [str(perm) for perm in role.permissions]
        orm_obj.role_id = role.id  # 更新业务ID
        orm_obj.name = role.name
        orm_obj.description = role.description
        orm_obj.permissions = permissions
        return orm_obj


class SQLAlchemyApiKeyRepository(SQLAlchemyRepository[ApiKey, ApiKeyORM], ApiKeyRepository):
    """SQLAlchemy API密钥仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ApiKeyORM)

    async def find_by_id(self, api_key_id: UUID) -> ApiKey | None:
        """根据ID获取API密钥"""
        stmt = select(ApiKeyORM).where(ApiKeyORM.api_key_id == api_key_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def find_by_key_hash(self, key_hash: str) -> ApiKey | None:
        """根据密钥哈希获取API密钥"""
        stmt = select(ApiKeyORM).where(ApiKeyORM.key_hash == key_hash)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def find_by_user_id(self, user_id: UUID) -> list[ApiKey]:
        """根据用户ID查找API密钥"""
        stmt = select(ApiKeyORM).where(ApiKeyORM.user_id == user_id)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def get_active_keys_by_user(self, user_id: UUID) -> list[ApiKey]:
        """获取用户的有效API密钥"""
        stmt = select(ApiKeyORM).where(
            and_(
                ApiKeyORM.user_id == user_id,
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
            id=orm_obj.api_key_id,  # 使用业务ID作为领域实体ID
            name=orm_obj.name,
            key_hash=orm_obj.key_hash,
            permissions=orm_obj.permissions or [],
            expires_at=orm_obj.expires_at,
            last_used_at=orm_obj.last_used_at,
            created_at=orm_obj.created_at
        )
        api_key.is_active = orm_obj.status == "active"
        return api_key

    def _create_orm_object(self, api_key: ApiKey, user_id: UUID = None) -> ApiKeyORM:
        """创建ORM对象"""
        return ApiKeyORM(
            api_key_id=api_key.id,  # 领域实体ID作为业务ID
            user_id=user_id,  # 需要传入用户ID
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
        orm_obj.api_key_id = api_key.id  # 更新业务ID
        orm_obj.name = api_key.name
        orm_obj.permissions = api_key.permissions
        orm_obj.expires_at = api_key.expires_at
        orm_obj.last_used_at = api_key.last_used_at
        orm_obj.status = "active" if api_key.is_active else "inactive"
        return orm_obj


class SQLAlchemyUserQuotaRepository(SQLAlchemyRepository[UserQuota, UserQuotaORM]):
    """SQLAlchemy用户配额仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserQuotaORM)

    async def find_by_user_id(self, user_id: UUID) -> UserQuota | None:
        """根据用户ID获取配额"""
        stmt = select(UserQuotaORM).where(UserQuotaORM.user_id == user_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def update_usage(self, user_id: UUID, api_calls: int = 0, storage: int = 0, compute_hours: int = 0) -> bool:
        """更新用户使用量"""
        stmt = select(UserQuotaORM).where(UserQuotaORM.user_id == user_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()

        if not orm_obj:
            return False

        orm_obj.api_calls_used += api_calls
        orm_obj.storage_used += storage
        orm_obj.compute_hours_used += compute_hours
        orm_obj.updated_at = datetime.now(UTC)

        await self.session.commit()
        return True

    async def reset_monthly_usage(self, user_id: UUID) -> bool:
        """重置月度使用量"""
        stmt = select(UserQuotaORM).where(UserQuotaORM.user_id == user_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()

        if not orm_obj:
            return False

        orm_obj.api_calls_used = 0
        orm_obj.storage_used = 0
        orm_obj.compute_hours_used = 0
        orm_obj.reset_at = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        orm_obj.updated_at = datetime.now(UTC)

        await self.session.commit()
        return True

    def _to_domain_entity(self, orm_obj: UserQuotaORM) -> UserQuota:
        """将ORM对象转换为领域实体"""
        if not orm_obj:
            return None

        return UserQuota(
            api_calls_limit=orm_obj.api_calls_limit,
            api_calls_used=orm_obj.api_calls_used,
            storage_limit=orm_obj.storage_limit,
            storage_used=orm_obj.storage_used,
            compute_hours_limit=orm_obj.compute_hours_limit,
            compute_hours_used=orm_obj.compute_hours_used
        )

    def _create_orm_object(self, quota: UserQuota, user_id: UUID) -> UserQuotaORM:
        """创建ORM对象"""
        return UserQuotaORM(
            user_id=user_id,
            api_calls_limit=quota.api_calls_limit,
            api_calls_used=quota.api_calls_used,
            storage_limit=quota.storage_limit,
            storage_used=quota.storage_used,
            compute_hours_limit=quota.compute_hours_limit,
            compute_hours_used=quota.compute_hours_used
        )

    def _update_orm_object(self, orm_obj: UserQuotaORM, quota: UserQuota) -> UserQuotaORM:
        """更新ORM对象"""
        orm_obj.api_calls_limit = quota.api_calls_limit
        orm_obj.api_calls_used = quota.api_calls_used
        orm_obj.storage_limit = quota.storage_limit
        orm_obj.storage_used = quota.storage_used
        orm_obj.compute_hours_limit = quota.compute_hours_limit
        orm_obj.compute_hours_used = quota.compute_hours_used
        orm_obj.updated_at = datetime.now(UTC)
        return orm_obj
