"""用户模块数据初始化器"""

from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_extensions import uuid7

from shared.domain.initializer import DataInitializer
from user.domain.models import RoleType
from user.infrastructure.models import RoleORM, UserORM, UserQuotaORM, UserRoleORM


class UserDataInitializer(DataInitializer):
    """用户模块数据初始化器"""

    def __init__(self) -> None:
        self._roles_data = self._get_initial_roles_data()
        self._admin_data = self._get_initial_admin_data()

    def get_module_name(self) -> str:
        """获取模块名称"""
        return "user"

    def get_dependencies(self) -> list[str]:
        """获取依赖的模块列表"""
        return []  # 用户模块无依赖

    def _get_initial_roles_data(self) -> list[dict[str, Any]]:
        """获取初始角色数据"""
        return [
            {
                "role_id": uuid7(),
                "name": RoleType.ADMIN.value,
                "description": "系统管理员，拥有所有权限",
                "permissions": [
                    "user:create", "user:read", "user:update", "user:delete",
                    "role:create", "role:read", "role:update", "role:delete",
                    "model:create", "model:read", "model:update", "model:delete",
                    "service:create", "service:read", "service:update", "service:delete",
                    "system:read", "system:update", "system:monitor"
                ]
            },
            {
                "role_id": uuid7(),
                "name": RoleType.DEVELOPER.value,
                "description": "开发人员，拥有模型和服务的管理权限",
                "permissions": [
                    "user:read", "user:update",
                    "model:create", "model:read", "model:update", "model:delete",
                    "service:create", "service:read", "service:update", "service:delete",
                    "system:read"
                ]
            },
            {
                "role_id": uuid7(),
                "name": RoleType.USER.value,
                "description": "普通用户，只能使用已部署的服务",
                "permissions": [
                    "user:read", "user:update",
                    "model:read",
                    "service:read", "service:use"
                ]
            }
        ]

    def _get_initial_admin_data(self) -> dict[str, Any]:
        """获取初始管理员用户数据"""
        from user.application.services import PasswordHashService

        # 动态生成密码哈希
        admin_password = "admin123"  # 默认管理员密码
        password_hash = PasswordHashService.hash_password(admin_password)

        return {
            "user_id": uuid7(),
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": password_hash,
            "first_name": "系统",
            "last_name": "管理员",
            "organization": "MaaS平台",
            "bio": "系统默认管理员账户",
            "status": "active",
            "email_verified": True,
        }

    async def initialize(self, session: AsyncSession) -> bool:
        """初始化用户模块数据"""
        try:
            # 初始化角色
            await self._initialize_roles(session)

            # 初始化管理员用户
            admin_user = await self._initialize_admin_user(session)

            # 刷新session以确保角色已保存
            await session.flush()

            # 为管理员分配角色
            if admin_user:
                await self._assign_admin_role(session, admin_user)

            # 为管理员创建配额
            if admin_user:
                await self._create_admin_quota(session, admin_user)

            return True

        except Exception as e:
            logger.error(f"用户模块数据初始化失败: {e}")
            return False

    async def _initialize_roles(self, session: AsyncSession) -> None:
        """初始化角色数据"""
        logger.info("初始化角色数据...")

        for role_data in self._roles_data:
            # 检查角色是否已存在
            result = await session.execute(
                select(RoleORM).where(RoleORM.name == role_data["name"])
            )
            existing_role = result.scalar_one_or_none()

            if existing_role:
                # 更新现有角色的权限
                existing_role.description = role_data["description"]
                existing_role.permissions = role_data["permissions"]
                existing_role.updated_at = datetime.utcnow()
                logger.info(f"更新角色: {role_data['name']}")
            else:
                # 创建新角色
                role = RoleORM(**role_data)
                session.add(role)
                logger.info(f"创建角色: {role_data['name']}")

    async def _initialize_admin_user(self, session: AsyncSession) -> UserORM | None:
        """初始化管理员用户"""
        logger.info("初始化管理员用户...")

        admin_data = self._admin_data

        # 检查管理员用户是否已存在
        result = await session.execute(
            select(UserORM).where(UserORM.username == admin_data["username"])
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.info(f"管理员用户已存在: {admin_data['username']}")
            return existing_user

        # 创建新的管理员用户
        admin_user = UserORM(**admin_data)
        session.add(admin_user)
        logger.info(f"创建管理员用户: {admin_data['username']}")

        return admin_user

    async def _assign_admin_role(self, session: AsyncSession, admin_user: UserORM) -> None:
        """为管理员分配角色"""
        logger.info("为管理员分配角色...")

        # 获取管理员角色
        result = await session.execute(
            select(RoleORM).where(RoleORM.name == RoleType.ADMIN.value)
        )
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            logger.error("管理员角色不存在，无法分配")
            return

        # 检查是否已经分配了角色（使用更严格的检查）
        result = await session.execute(
            select(UserRoleORM).where(
                (UserRoleORM.user_id == admin_user.user_id) &
                (UserRoleORM.role_id == admin_role.role_id)
            )
        )
        existing_user_role = result.scalar_one_or_none()

        if existing_user_role:
            logger.info("管理员角色已分配，跳过")
            return

        try:
            # 创建用户角色关联
            user_role = UserRoleORM(
                user_role_id=uuid7(),
                user_id=admin_user.user_id,
                role_id=admin_role.role_id,
                granted_by_id=admin_user.user_id  # 自己分配给自己
            )
            session.add(user_role)
            await session.flush()  # 立即刷新以检测约束冲突
            logger.info("为管理员用户分配管理员角色")
        except Exception as e:
            logger.warning(f"管理员角色分配失败，可能已存在: {e}")
            # 如果是唯一约束错误，说明角色已分配，可以忽略
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                logger.info("管理员角色已存在，忽略重复分配")
            else:
                raise

    async def _create_admin_quota(self, session: AsyncSession, admin_user: UserORM) -> None:
        """为管理员创建配额"""
        logger.info("为管理员创建配额...")

        # 检查配额是否已存在
        result = await session.execute(
            select(UserQuotaORM).where(UserQuotaORM.user_id == admin_user.user_id)
        )
        existing_quota = result.scalar_one_or_none()

        if existing_quota:
            logger.info("管理员配额已存在")
            return

        # 创建管理员配额（高配额）
        quota = UserQuotaORM(
            user_quota_id=uuid7(),
            user_id=admin_user.user_id,
            api_calls_limit=100000,  # 高API调用限制
            api_calls_used=0,
            storage_limit=1073741824,  # 1GB存储
            storage_used=0,
            compute_hours_limit=1000,  # 1000小时计算时间
            compute_hours_used=0
        )

        session.add(quota)
        logger.info("为管理员用户创建高配额")
