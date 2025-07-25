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
    Permission,
    Role,
    User,
    UserProfile,
    UserStatus,
)
from user.domain.repositories import PermissionRepository, RoleRepository, UserRepository
from user.infrastructure.models import RoleORM, UserORM


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
            for perm_data in role_orm.permissions:
                if isinstance(perm_data, dict):
                    permission = Permission(
                        id=UUID(perm_data.get("id")),
                        name=perm_data.get("name", ""),
                        description=perm_data.get("description", ""),
                        resource=perm_data.get("resource", ""),
                        action=perm_data.get("action", "")
                    )
                    permissions.append(permission)

            role = Role(
                id=role_orm.role_id,
                name=role_orm.name,
                description=role_orm.description or "",
                permissions=permissions
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
        # 默认角色是 'user'
        role = await self.find_by_name("user")
        if not role:
            raise ValueError("默认角色 'user' 不存在")
        return role

    async def find_all(self) -> list[Role]:
        """获取所有角色"""
        stmt = select(RoleORM).order_by(RoleORM.name)
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
        stmt = select(RoleORM)
        
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

    async def find_by_role_id(self, role_id: UUID) -> list[User]:
        """根据角色ID查找用户"""
        # 这个方法应该在UserRepository中，先简单实现
        return []

    def _to_domain_entity(self, orm_obj: RoleORM) -> Role:
        """将ORM对象转换为领域实体"""
        if not orm_obj:
            return None

        permissions = []
        for perm_data in orm_obj.permissions:
            if isinstance(perm_data, dict):
                permission = Permission(
                    id=UUID(perm_data.get("id")),
                    name=perm_data.get("name", ""),
                    description=perm_data.get("description", ""),
                    resource=perm_data.get("resource", ""),
                    action=perm_data.get("action", "")
                )
                permissions.append(permission)

        return Role(
            id=orm_obj.role_id,
            name=orm_obj.name,
            description=orm_obj.description or "",
            permissions=permissions
        )

    def _create_orm_object(self, role: Role) -> RoleORM:
        """创建ORM对象"""
        permissions = []
        for perm in role.permissions:
            permissions.append({
                "id": str(perm.id),
                "name": perm.name,
                "description": perm.description,
                "resource": perm.resource,
                "action": perm.action
            })

        return RoleORM(
            role_id=role.id,
            name=role.name,
            description=role.description,
            permissions=permissions
        )

    def _update_orm_object(self, orm_obj: RoleORM, role: Role) -> RoleORM:
        """更新ORM对象"""
        permissions = []
        for perm in role.permissions:
            permissions.append({
                "id": str(perm.id),
                "name": perm.name,
                "description": perm.description,
                "resource": perm.resource,
                "action": perm.action
            })

        orm_obj.role_id = role.id
        orm_obj.name = role.name
        orm_obj.description = role.description
        orm_obj.permissions = permissions
        return orm_obj


class SQLAlchemyPermissionRepository(PermissionRepository):
    """SQLAlchemy权限仓储实现（基于角色JSON存储）"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, permission_id: UUID) -> Permission | None:
        """根据ID获取权限"""
        # 从所有角色的permissions JSON中查找
        stmt = select(RoleORM)
        result = await self.session.execute(stmt)
        roles = result.scalars().all()
        
        for role in roles:
            for perm_data in role.permissions:
                if isinstance(perm_data, dict) and UUID(perm_data.get("id")) == permission_id:
                    return Permission(
                        id=UUID(perm_data.get("id")),
                        name=perm_data.get("name", ""),
                        description=perm_data.get("description", ""),
                        resource=perm_data.get("resource", ""),
                        action=perm_data.get("action", "")
                    )
        return None

    async def find_by_resource_action(self, resource: str, action: str) -> Permission | None:
        """根据资源和操作查找权限"""
        stmt = select(RoleORM)
        result = await self.session.execute(stmt)
        roles = result.scalars().all()
        
        for role in roles:
            for perm_data in role.permissions:
                if (isinstance(perm_data, dict) and 
                    perm_data.get("resource") == resource and 
                    perm_data.get("action") == action):
                    return Permission(
                        id=UUID(perm_data.get("id")),
                        name=perm_data.get("name", ""),
                        description=perm_data.get("description", ""),
                        resource=perm_data.get("resource", ""),
                        action=perm_data.get("action", "")
                    )
        return None

    async def find_all(self) -> list[Permission]:
        """获取所有权限"""
        stmt = select(RoleORM)
        result = await self.session.execute(stmt)
        roles = result.scalars().all()
        
        permissions = []
        seen_permissions = set()
        
        for role in roles:
            for perm_data in role.permissions:
                if isinstance(perm_data, dict):
                    perm_key = f"{perm_data.get('resource')}:{perm_data.get('action')}"
                    if perm_key not in seen_permissions:
                        permission = Permission(
                            id=UUID(perm_data.get("id")),
                            name=perm_data.get("name", ""),
                            description=perm_data.get("description", ""),
                            resource=perm_data.get("resource", ""),
                            action=perm_data.get("action", "")
                        )
                        permissions.append(permission)
                        seen_permissions.add(perm_key)
        
        return permissions

    async def find_by_resource(self, resource: str) -> list[Permission]:
        """根据资源查找权限"""
        stmt = select(RoleORM)
        result = await self.session.execute(stmt)
        roles = result.scalars().all()
        
        permissions = []
        seen_permissions = set()
        
        for role in roles:
            for perm_data in role.permissions:
                if (isinstance(perm_data, dict) and 
                    perm_data.get("resource") == resource):
                    perm_key = f"{perm_data.get('resource')}:{perm_data.get('action')}"
                    if perm_key not in seen_permissions:
                        permission = Permission(
                            id=UUID(perm_data.get("id")),
                            name=perm_data.get("name", ""),
                            description=perm_data.get("description", ""),
                            resource=perm_data.get("resource", ""),
                            action=perm_data.get("action", "")
                        )
                        permissions.append(permission)
                        seen_permissions.add(perm_key)
        
        return permissions

    async def save(self, permission: Permission) -> Permission:
        """保存权限（注意：这个实现有限制，因为权限嵌入在角色中）"""
        # 由于权限存储在角色的JSON字段中，这个方法比较复杂
        # 在当前架构下，新权限应该通过角色管理来添加
        # 这里提供一个基本实现，但建议通过角色服务来管理权限
        raise NotImplementedError("权限应该通过角色服务进行管理")

    async def delete(self, permission_id: UUID) -> bool:
        """删除权限"""
        # 同样，由于架构限制，删除权限需要从所有包含该权限的角色中移除
        raise NotImplementedError("权限删除应该通过角色服务进行管理")
