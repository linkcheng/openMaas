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

from sqlalchemy import and_, case, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_extensions import uuid7

from shared.domain.base import EmailAddress
from shared.infrastructure.repository import SQLAlchemyRepository
from user.infrastructure.models import AuditLogORM

from user.domain.models import (
    Permission,
    PermissionName,
    Role,
    RoleType,
    User,
    UserProfile,
    UserStatus,
    AuditLog,
)
from user.domain.repositories import (
    IPermissionRepository,
    IRoleRepository,
    IUserRepository,
    IAuditLogRepository,
)
from user.infrastructure.models import (
    PermissionORM,
    RoleORM,
    RolePermissionORM,
    UserORM,
    UserRoleORM,
)



class UserRepository(SQLAlchemyRepository[User, UserORM], IUserRepository):
    """SQLAlchemy用户仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User, UserORM)

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
        else:
            # 创建新用户
            new_orm = self._create_orm_object(user)
            self.session.add(new_orm)
            await self.session.flush()  # 获取自增ID

            # 处理角色关联
            await self._sync_user_roles(new_orm, user)

        await self.session.commit()
        return user

    async def _sync_user_roles(self, user_orm: UserORM, user: User):
        """同步用户角色"""

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

    async def find_by_id(self, user_id: UUID) -> User | None:
        """根据ID获取用户"""
        stmt = (
            select(UserORM)
            .where(UserORM.user_id == user_id)
            .options(
                selectinload(UserORM.roles)
            )
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_by_id(self, user_id: UUID) -> User | None:
        """根据ID获取用户（重写基类方法）"""
        return await self.find_by_id(user_id)

    async def find_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        stmt = (
            select(UserORM)
            .where(UserORM.email == email)
            .options(
                selectinload(UserORM.roles)
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
                selectinload(UserORM.roles)
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
                selectinload(UserORM.roles)
            )
        )
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def search(self, query) -> list[User]:
        """搜索用户"""
        stmt = select(UserORM).options(
            selectinload(UserORM.roles)
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
            selectinload(UserORM.roles)
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

    async def find_by_role_id(self, role_id: UUID) -> list[User]:
        """根据角色ID查找用户"""
        stmt = select(UserORM).options(
            selectinload(UserORM.roles)
        ).join(UserRoleORM).where(UserRoleORM.role_id == role_id)

        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def find_users_with_permissions(self, permission_names: list[str]) -> list[User]:
        """查找拥有指定权限的用户"""
        if not permission_names:
            return []

        # 查找拥有指定权限的用户，使用预加载优化查询性能
        stmt = (
            select(UserORM)
            .options(
                selectinload(UserORM.roles).selectinload(RoleORM.permissions)
            )
            .join(UserRoleORM)
            .join(RoleORM, RoleORM.role_id == UserRoleORM.role_id)
            .join(RolePermissionORM, RolePermissionORM.role_id == RoleORM.role_id)
            .join(PermissionORM, PermissionORM.permission_id == RolePermissionORM.permission_id)
            .where(PermissionORM.name.in_(permission_names))
            .distinct()
        )

        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def batch_update_user_roles(self, user_role_updates: list[dict]) -> bool:
        """批量更新用户角色"""
        try:

            # 批量处理用户角色更新
            user_ids = [update.get("user_id") for update in user_role_updates if update.get("user_id")]

            if not user_ids:
                return True

            # 批量删除现有角色关联
            delete_stmt = delete(UserRoleORM).where(UserRoleORM.user_id.in_(user_ids))
            await self.session.execute(delete_stmt)

            # 批量添加新的角色关联
            new_role_relations = []
            for update in user_role_updates:
                user_id = update.get("user_id")
                role_ids = update.get("role_ids", [])

                if not user_id:
                    continue

                for role_id in role_ids:
                    role_rel = UserRoleORM(
                        user_role_id=uuid7(),
                        user_id=user_id,
                        role_id=role_id,
                    )
                    new_role_relations.append(role_rel)

            # 批量插入新关联
            if new_role_relations:
                self.session.add_all(new_role_relations)

            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            # 可以记录错误日志
            return False

    async def find_by_ids(self, user_ids: list[UUID]) -> list[User]:
        """批量根据ID查找用户"""
        if not user_ids:
            return []

        stmt = select(UserORM).where(UserORM.user_id.in_(user_ids)).options(
            selectinload(UserORM.roles).selectinload(RoleORM.permissions)
        )
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def load_user_permissions_with_cache(self, user_id: UUID) -> list[Permission]:
        """加载用户权限（支持缓存策略）"""

        # 查询用户的所有权限（通过角色关联）
        stmt = (
            select(PermissionORM)
            .join(RolePermissionORM, RolePermissionORM.permission_id == PermissionORM.permission_id)
            .join(RoleORM, RoleORM.role_id == RolePermissionORM.role_id)
            .join(UserRoleORM, UserRoleORM.role_id == RoleORM.role_id)
            .where(UserRoleORM.user_id == user_id)
            .distinct()
        )

        result = await self.session.execute(stmt)
        permission_orms = result.scalars().all()

        # 转换为领域实体
        permissions = []
        for perm_orm in permission_orms:
            permission = Permission(
                id=perm_orm.permission_id,
                name=PermissionName(perm_orm.name),
                display_name=perm_orm.display_name,
                description=perm_orm.description or "",
                module=perm_orm.module
            )
            permissions.append(permission)

        return permissions

    async def find_users_by_permission_and_module(self, module: str, permission_name: str) -> list[User]:
        """根据模块和权限名称查找用户"""

        stmt = (
            select(UserORM)
            .options(
                selectinload(UserORM.roles).selectinload(RoleORM.permissions)
            )
            .join(UserRoleORM)
            .join(RoleORM, RoleORM.role_id == UserRoleORM.role_id)
            .join(RolePermissionORM, RolePermissionORM.role_id == RoleORM.role_id)
            .join(PermissionORM, PermissionORM.permission_id == RolePermissionORM.permission_id)
            .where(
                and_(
                    PermissionORM.module == module,
                    PermissionORM.name == permission_name
                )
            )
            .distinct()
        )

        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    def _to_domain_entity(self, orm_obj: UserORM) -> User:
        """将ORM对象转换为领域实体"""
        if not orm_obj:
            return None

        # 转换用户档案
        profile = UserProfile(
            first_name=orm_obj.first_name or "",
            last_name=orm_obj.last_name or "",
            avatar_url=orm_obj.avatar_url,
            organization=orm_obj.organization,
            bio=orm_obj.bio
        )

        # 创建用户实体
        user = User(
            id=orm_obj.user_id,  # 使用业务ID作为领域实体ID
            username=orm_obj.username,
            email=EmailAddress(orm_obj.email),
            password_hash=orm_obj.password_hash,
            profile=profile,
            status=UserStatus(orm_obj.status),
            email_verified=orm_obj.email_verified,
            key_version=orm_obj.key_version,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            last_login_at=orm_obj.last_login_at
        )

        # 添加角色
        for role_orm in orm_obj.roles:
            permissions = []
            for perm_orm in role_orm.permissions:
                permission = Permission(
                    id=perm_orm.permission_id,
                    name=PermissionName(perm_orm.name),
                    display_name=perm_orm.display_name,
                    description=perm_orm.description or "",
                    module=perm_orm.module
                )
                permissions.append(permission)

            role = Role(
                id=role_orm.role_id,
                name=role_orm.name,
                display_name=role_orm.display_name,
                description=role_orm.description or "",
                permissions=permissions,
                is_system_role=role_orm.is_system_role,
                role_type=RoleType(role_orm.role_type)
            )
            user.add_role(role)

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
            key_version=user.key_version,
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
        orm_obj.key_version = user.key_version
        orm_obj.last_login_at = user.last_login_at
        orm_obj.updated_at = datetime.now(UTC)
        return orm_obj


class RoleRepository(SQLAlchemyRepository[Role, RoleORM], IRoleRepository):
    """SQLAlchemy角色仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Role, RoleORM)

    async def find_by_id(self, role_id: UUID) -> Role | None:
        """根据ID获取角色"""
        stmt = select(RoleORM).where(RoleORM.role_id == role_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_by_id(self, role_id: UUID) -> Role | None:
        """根据ID获取角色（重写基类方法）"""
        return await self.find_by_id(role_id)

    async def find_by_name(self, name: str) -> Role | None:
        """根据名称获取角色"""
        stmt = select(RoleORM).where(RoleORM.name == name)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_default_role(self) -> Role:
        """获取默认角色"""
        # 默认角色是 'user'
        role = await self.find_by_name("user")
        if not role:
            raise ValueError("默认角色 'user' 不存在")
        return role

    async def find_all(self) -> list[Role]:
        """获取所有角色"""
        stmt = select(RoleORM).options(selectinload(RoleORM.permissions)).order_by(RoleORM.name)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def search_roles(
        self,
        name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Role]:
        """搜索角色"""
        stmt = select(RoleORM).options(selectinload(RoleORM.permissions))

        if name:
            stmt = stmt.where(RoleORM.name.ilike(f"%{name}%"))

        stmt = stmt.order_by(RoleORM.name).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def delete(self, role_id: UUID) -> bool:
        """删除角色"""
        stmt = select(RoleORM).where(RoleORM.role_id == role_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()

        if orm_obj:
            await self.session.delete(orm_obj)
            await self.session.commit()
            return True
        return False

    async def find_roles_with_permissions(self, permission_ids: list[UUID] | None = None) -> list[Role]:
        """查找包含指定权限的角色"""

        stmt = select(RoleORM).options(selectinload(RoleORM.permissions))

        if permission_ids:
            stmt = stmt.join(RolePermissionORM).where(RolePermissionORM.permission_id.in_(permission_ids)).distinct()

        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def find_by_ids(self, role_ids: list[UUID]) -> list[Role]:
        """批量根据ID查找角色"""
        if not role_ids:
            return []

        stmt = select(RoleORM).where(RoleORM.role_id.in_(role_ids)).options(selectinload(RoleORM.permissions))
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def count_roles(self, name: str | None = None) -> int:
        """统计角色数量"""
        stmt = select(func.count(RoleORM.id))

        if name:
            stmt = stmt.where(RoleORM.name.ilike(f"%{name}%"))

        result = await self.session.execute(stmt)
        return result.scalar()

    def _to_domain_entity(self, orm_obj: RoleORM) -> Role:
        """将ORM对象转换为领域实体"""
        if not orm_obj:
            return None

        permissions = []
        for perm_orm in orm_obj.permissions:
            permission = Permission(
                id=perm_orm.permission_id,
                name=PermissionName(perm_orm.name),
                display_name=perm_orm.display_name,
                description=perm_orm.description or "",
                module=perm_orm.module
            )
            permissions.append(permission)

        return Role(
            id=orm_obj.role_id,
            name=orm_obj.name,
            display_name=orm_obj.display_name,
            description=orm_obj.description or "",
            permissions=permissions,
            is_system_role=orm_obj.is_system_role,
            role_type=RoleType(orm_obj.role_type)
        )

    def _create_orm_object(self, role: Role) -> RoleORM:
        """创建ORM对象"""
        return RoleORM(
            role_id=role.id,
            name=role.name,
            display_name=role.display_name,
            description=role.description,
            role_type=role.role_type.value,
            is_system_role=role.is_system_role
        )

    def _update_orm_object(self, orm_obj: RoleORM, role: Role) -> RoleORM:
        """更新ORM对象"""
        orm_obj.role_id = role.id
        orm_obj.name = role.name
        orm_obj.display_name = role.display_name
        orm_obj.description = role.description
        orm_obj.role_type = role.role_type.value
        orm_obj.is_system_role = role.is_system_role
        return orm_obj

    async def save(self, role: Role) -> Role:
        """保存角色"""

        # 查找现有角色
        stmt = select(RoleORM).where(RoleORM.role_id == role.id)
        result = await self.session.execute(stmt)
        existing_orm = result.scalar_one_or_none()

        if existing_orm:
            # 更新现有角色
            self._update_orm_object(existing_orm, role)
            # 处理权限关联
            await self._sync_role_permissions(existing_orm, role)
        else:
            # 创建新角色
            new_orm = self._create_orm_object(role)
            self.session.add(new_orm)
            await self.session.flush()  # 获取自增ID

            # 处理权限关联
            await self._sync_role_permissions(new_orm, role)

        await self.session.commit()
        return role

    async def _sync_role_permissions(self, role_orm: RoleORM, role: Role):
        """同步角色权限"""

        # 获取现有权限关联
        stmt = select(RolePermissionORM).where(RolePermissionORM.role_id == role.id)
        result = await self.session.execute(stmt)
        existing_perms = result.scalars().all()
        existing_perm_ids = {perm_rel.permission_id for perm_rel in existing_perms}

        # 获取当前角色应有的权限ID
        current_perm_ids = {perm.id for perm in role.permissions}

        # 如果权限没有变化，直接返回
        if existing_perm_ids == current_perm_ids:
            return

        # 删除不再需要的权限关联
        perms_to_remove = existing_perm_ids - current_perm_ids
        if perms_to_remove:
            for perm_rel in existing_perms:
                if perm_rel.permission_id in perms_to_remove:
                    await self.session.delete(perm_rel)

        # 添加新的权限关联
        perms_to_add = current_perm_ids - existing_perm_ids
        for perm in role.permissions:
            if perm.id in perms_to_add:
                perm_rel = RolePermissionORM(
                    role_permission_id=uuid7(),
                    role_id=role.id,
                    permission_id=perm.id
                )
                self.session.add(perm_rel)


class PermissionRepository(SQLAlchemyRepository[Permission, PermissionORM], IPermissionRepository):
    """SQLAlchemy权限仓储实现"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Permission, PermissionORM)

    async def find_by_id(self, permission_id: UUID) -> Permission | None:
        """根据ID获取权限"""
        stmt = select(PermissionORM).where(PermissionORM.permission_id == permission_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def get_by_id(self, permission_id: UUID) -> Permission | None:
        """根据ID获取权限（重写基类方法）"""
        return await self.find_by_id(permission_id)

    async def find_by_resource_action(self, resource: str, action: str) -> Permission | None:
        """根据资源和操作查找权限"""
        stmt = select(PermissionORM).where(
            and_(PermissionORM.resource == resource, PermissionORM.action == action)
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._to_domain_entity(orm_obj) if orm_obj else None

    async def find_all(self) -> list[Permission]:
        """获取所有权限"""
        stmt = select(PermissionORM).order_by(PermissionORM.module, PermissionORM.resource, PermissionORM.action)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def find_by_resource(self, resource: str) -> list[Permission]:
        """根据资源查找权限"""
        stmt = select(PermissionORM).where(PermissionORM.resource == resource).order_by(PermissionORM.action)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def find_by_module(self, module: str) -> list[Permission]:
        """根据模块查找权限"""
        stmt = select(PermissionORM).where(PermissionORM.module == module).order_by(PermissionORM.resource, PermissionORM.action)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def find_by_ids(self, permission_ids: list[UUID]) -> list[Permission]:
        """批量根据ID查找权限"""
        if not permission_ids:
            return []

        stmt = select(PermissionORM).where(PermissionORM.permission_id.in_(permission_ids))
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def find_by_names(self, permission_names: list[str]) -> list[Permission]:
        """批量根据名称查找权限"""
        if not permission_names:
            return []

        stmt = select(PermissionORM).where(PermissionORM.name.in_(permission_names))
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def save(self, permission: Permission) -> Permission:
        """保存权限（重写基类方法）"""
        # 查找现有权限
        stmt = select(PermissionORM).where(PermissionORM.permission_id == permission.id)
        result = await self.session.execute(stmt)
        existing_orm = result.scalar_one_or_none()

        if existing_orm:
            # 更新现有权限
            self._update_orm_object(existing_orm, permission)
        else:
            # 创建新权限
            new_orm = self._create_orm_object(permission)
            self.session.add(new_orm)

        await self.session.commit()
        return permission

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
        stmt = select(PermissionORM)

        conditions = []
        if keyword:
            conditions.append(
                or_(
                    PermissionORM.name.ilike(f"%{keyword}%"),
                    PermissionORM.display_name.ilike(f"%{keyword}%"),
                    PermissionORM.description.ilike(f"%{keyword}%")
                )
            )
        if module:
            conditions.append(PermissionORM.module == module)
        if resource:
            conditions.append(PermissionORM.resource == resource)
        if action:
            conditions.append(PermissionORM.action == action)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(PermissionORM.module, PermissionORM.resource, PermissionORM.action).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        orm_objects = result.scalars().all()
        return [self._to_domain_entity(obj) for obj in orm_objects]

    async def count_permissions(
        self,
        keyword: str | None = None,
        module: str | None = None,
        resource: str | None = None,
    ) -> int:
        """统计权限数量"""
        stmt = select(func.count(PermissionORM.id))

        conditions = []
        if keyword:
            conditions.append(
                or_(
                    PermissionORM.name.ilike(f"%{keyword}%"),
                    PermissionORM.display_name.ilike(f"%{keyword}%"),
                    PermissionORM.description.ilike(f"%{keyword}%")
                )
            )
        if module:
            conditions.append(PermissionORM.module == module)
        if resource:
            conditions.append(PermissionORM.resource == resource)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self.session.execute(stmt)
        return result.scalar()

    def _to_domain_entity(self, orm_obj) -> Permission:
        """将ORM对象转换为领域实体"""
        if not orm_obj:
            return None

        return Permission(
            id=orm_obj.permission_id,
            name=PermissionName(orm_obj.name),
            display_name=orm_obj.display_name,
            description=orm_obj.description or "",
            module=orm_obj.module
        )

    def _create_orm_object(self, permission: Permission):
        """创建ORM对象"""
        return PermissionORM(
            permission_id=permission.id,
            name=permission.name.value,
            display_name=permission.display_name,
            description=permission.description,
            module=permission.module,
            resource=permission.resource,
            action=permission.action
        )

    def _update_orm_object(self, orm_obj, permission: Permission):
        """更新ORM对象"""
        orm_obj.permission_id = permission.id
        orm_obj.name = permission.name.value
        orm_obj.display_name = permission.display_name
        orm_obj.description = permission.description
        orm_obj.module = permission.module
        orm_obj.resource = permission.resource
        orm_obj.action = permission.action
        return orm_obj


class AuditLogRepository(SQLAlchemyRepository[AuditLog, AuditLogORM], IAuditLogRepository):
    """审计日志仓储（简化版）"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLog, AuditLogORM)
    
    async def find_with_count(
        self,
        user_id: UUID | None = None,
        action = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        success: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list, int]:
        """查询审计日志并返回总数"""
        
        try:
            # 构建查询条件
            conditions = []
            if user_id is not None:
                conditions.append(AuditLogORM.user_id == user_id)
            if action is not None:
                conditions.append(AuditLogORM.action == action)
            if start_time is not None:
                conditions.append(AuditLogORM.created_at >= start_time)
            if end_time is not None:
                conditions.append(AuditLogORM.created_at <= end_time)
            if success is not None:
                conditions.append(AuditLogORM.success == success)
            
            # 构建查询
            data_query = select(AuditLogORM)
            count_query = select(func.count(AuditLogORM.id))
            
            if conditions:
                data_query = data_query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))
            
            # 执行计数查询
            count_result = await self.session.execute(count_query)
            total = count_result.scalar() or 0
            
            if total == 0:
                return [], 0
            
            # 执行数据查询
            data_query = data_query.order_by(AuditLogORM.created_at.desc()).offset(offset).limit(limit)
            data_result = await self.session.execute(data_query)
            orm_objects = data_result.scalars().all()
            
            # 转换为领域对象
            logs = []
            for orm_obj in orm_objects:
                log = AuditLog(
                    id=orm_obj.id,
                    user_id=orm_obj.user_id,
                    username=orm_obj.username,
                    action=orm_obj.action,
                    description=orm_obj.description,
                    ip_address=orm_obj.ip_address,
                    user_agent=orm_obj.user_agent,
                    success=orm_obj.success,
                    error_message=orm_obj.error_message,
                    created_at=orm_obj.created_at,
                )
                logs.append(log)
            
            return logs, total
            
        except Exception:
            await self.session.rollback()
            raise
    
    async def get_stats(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict:
        """获取审计统计信息"""
        
        try:
            # 基本统计
            conditions = []
            if start_time is not None:
                conditions.append(AuditLogORM.created_at >= start_time)
            if end_time is not None:
                conditions.append(AuditLogORM.created_at <= end_time)
            
            # 总数和成功失败统计
            stats_query = select(
                func.count(AuditLogORM.id).label("total"),
                func.sum(case((AuditLogORM.success == True, 1), else_=0)).label("successful"),
                func.sum(case((AuditLogORM.success == False, 1), else_=0)).label("failed"),
                func.count(func.distinct(AuditLogORM.user_id)).label("unique_users")
            )
            
            if conditions:
                stats_query = stats_query.where(and_(*conditions))
            
            stats_result = await self.session.execute(stats_query)
            stats_row = stats_result.first()
            
            # 热门操作统计
            action_query = select(
                AuditLogORM.action,
                func.count(AuditLogORM.id).label("count")
            ).group_by(AuditLogORM.action).order_by(func.count(AuditLogORM.id).desc()).limit(5)
            
            if conditions:
                action_query = action_query.where(and_(*conditions))
            
            action_result = await self.session.execute(action_query)
            top_actions = [
                {"action": row.action, "count": row.count}
                for row in action_result.fetchall()
            ]
            
            return {
                "total": stats_row.total or 0,
                "successful": stats_row.successful or 0,
                "failed": stats_row.failed or 0,
                "unique_users": stats_row.unique_users or 0,
                "top_actions": top_actions,
            }
            
        except Exception:
            await self.session.rollback()
            raise
    
    async def cleanup_old_logs(self, before_date: datetime) -> int:
        """清理旧的审计日志"""        
        try:
            # 先统计要删除的数量
            count_query = select(func.count(AuditLogORM.id)).where(AuditLogORM.created_at < before_date)
            count_result = await self.session.execute(count_query)
            count = count_result.scalar() or 0
            
            if count > 0:
                # 执行删除
                delete_query = delete(AuditLogORM).where(AuditLogORM.created_at < before_date)
                await self.session.execute(delete_query)
                await self.session.commit()
            
            return count
            
        except Exception:
            await self.session.rollback()
            raise

    def _to_domain_entity(self, orm_obj: AuditLogORM) -> AuditLog:
        """将ORM对象转换为领域实体"""
        return AuditLog(
            id=orm_obj.log_id,
            user_id=orm_obj.user_id,
            username=orm_obj.username,
            action=orm_obj.action,
            description=orm_obj.description,
            ip_address=orm_obj.ip_address,
            user_agent=orm_obj.user_agent,
            success=orm_obj.success,
            error_message=orm_obj.error_message,
            created_at=orm_obj.created_at,
        )

    def _create_orm_object(self, audit_log: AuditLog) -> AuditLogORM:
        """创建ORM对象"""
        return AuditLogORM(
            log_id=audit_log.id,
            user_id=audit_log.user_id,
            username=audit_log.username,
            action=audit_log.action,
            description=audit_log.description,
            ip_address=audit_log.ip_address,
            user_agent=audit_log.user_agent,
            success=audit_log.success,
            error_message=audit_log.error_message,
            created_at=audit_log.created_at,
        )

    def _update_orm_object(self, orm_obj: AuditLogORM, audit_log: AuditLog) -> AuditLogORM:
        """更新ORM对象"""
        orm_obj.log_id = audit_log.id
        orm_obj.user_id = audit_log.user_id
        orm_obj.username = audit_log.username
        orm_obj.action = audit_log.action
        orm_obj.description = audit_log.description
        orm_obj.ip_address = audit_log.ip_address
        orm_obj.user_agent = audit_log.user_agent
        orm_obj.success = audit_log.success
        orm_obj.error_message = audit_log.error_message
        orm_obj.created_at = audit_log.created_at
        return orm_obj
