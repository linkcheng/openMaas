"""
Copyright 2025 MaaS Team

用户生命周期领域服务

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

from datetime import datetime
from typing import Any
from uuid import UUID

from shared.domain.base import BusinessRuleViolationException, DomainService
from user.domain.models import Role, User, UserStatus


class UserLifecycleService(DomainService):
    """用户生命周期领域服务
    
    负责管理用户的完整生命周期，包括创建、激活、暂停、重置、删除等状态变更，
    以及相关的业务规则验证和状态转换逻辑。
    """

    # 用户状态转换规则
    STATE_TRANSITIONS = {
        UserStatus.ACTIVE: [UserStatus.INACTIVE, UserStatus.SUSPENDED],
        UserStatus.INACTIVE: [UserStatus.ACTIVE, UserStatus.SUSPENDED],
        UserStatus.SUSPENDED: [UserStatus.ACTIVE, UserStatus.INACTIVE]
    }

    def can_transition_to(self, current_status: UserStatus, target_status: UserStatus) -> bool:
        """检查用户状态是否可以转换
        
        Args:
            current_status: 当前状态
            target_status: 目标状态
            
        Returns:
            是否可以转换
        """
        if current_status == target_status:
            return False

        return target_status in self.STATE_TRANSITIONS.get(current_status, [])

    def validate_user_activation(self, user: User) -> list[str]:
        """验证用户激活条件
        
        Args:
            user: 用户实体
            
        Returns:
            验证错误列表
        """
        errors = []

        # 检查当前状态
        if user.status == UserStatus.ACTIVE:
            errors.append("用户已处于激活状态")
            return errors

        # 检查邮箱验证
        if not user.email_verified:
            errors.append("用户邮箱尚未验证")

        # 检查用户角色
        if not user.roles:
            errors.append("用户未分配角色")

        return errors

    def validate_user_suspension(self, user: User, reason: str) -> list[str]:
        """验证用户暂停条件
        
        Args:
            user: 用户实体
            reason: 暂停原因
            
        Returns:
            验证错误列表
        """
        errors = []

        # 检查当前状态
        if user.status == UserStatus.SUSPENDED:
            errors.append("用户已处于暂停状态")
            return errors

        # 检查暂停原因
        if not reason or len(reason.strip()) < 5:
            errors.append("暂停原因不能为空且至少5个字符")

        # 检查是否为系统管理员（特殊保护）
        if user.is_super_admin():
            errors.append("超级管理员不能被暂停")

        return errors

    def validate_user_deletion(self, user: User) -> list[str]:
        """验证用户删除条件
        
        Args:
            user: 用户实体
            
        Returns:
            验证错误列表
        """
        errors = []

        # 超级管理员不能删除
        if user.is_super_admin():
            errors.append("超级管理员不能删除")

        # 活跃用户需要先暂停
        if user.status == UserStatus.ACTIVE:
            errors.append("活跃用户需要先暂停才能删除")

        # 检查关联数据（这里简化处理，实际应该检查业务关联）
        # if self.has_active_sessions(user.id):
        #     errors.append("用户存在活跃会话，无法删除")

        return errors

    def execute_user_activation(self, user: User) -> dict[str, Any]:
        """执行用户激活
        
        Args:
            user: 用户实体
            
        Returns:
            操作结果
        """
        errors = self.validate_user_activation(user)
        if errors:
            raise BusinessRuleViolationException(f"用户激活失败: {', '.join(errors)}")

        old_status = user.status
        user.activate()

        return {
            "operation": "user_activation",
            "user_id": str(user.id),
            "old_status": old_status.value,
            "new_status": user.status.value,
            "timestamp": datetime.utcnow().isoformat()
        }

    def execute_user_suspension(self, user: User, reason: str, suspended_by: UUID) -> dict[str, Any]:
        """执行用户暂停
        
        Args:
            user: 用户实体
            reason: 暂停原因
            suspended_by: 操作者ID
            
        Returns:
            操作结果
        """
        errors = self.validate_user_suspension(user, reason)
        if errors:
            raise BusinessRuleViolationException(f"用户暂停失败: {', '.join(errors)}")

        old_status = user.status
        user.suspend(reason)

        # 使所有现有token失效
        user.increment_key_version()

        return {
            "operation": "user_suspension",
            "user_id": str(user.id),
            "old_status": old_status.value,
            "new_status": user.status.value,
            "reason": reason,
            "suspended_by": str(suspended_by),
            "timestamp": datetime.utcnow().isoformat()
        }

    def execute_role_assignment(self, user: User, new_roles: list[Role], assigned_by: UUID) -> dict[str, Any]:
        """执行角色分配
        
        Args:
            user: 用户实体
            new_roles: 新角色列表
            assigned_by: 操作者ID
            
        Returns:
            操作结果
        """
        errors = self.validate_role_assignment(user, new_roles)
        if errors:
            raise BusinessRuleViolationException(f"角色分配失败: {', '.join(errors)}")

        old_roles = [role.name for role in user.roles]
        user.set_roles(new_roles)
        new_role_names = [role.name for role in new_roles]

        # 权限变更时使token失效
        user.increment_key_version()

        return {
            "operation": "role_assignment",
            "user_id": str(user.id),
            "old_roles": old_roles,
            "new_roles": new_role_names,
            "assigned_by": str(assigned_by),
            "timestamp": datetime.utcnow().isoformat()
        }

    def validate_role_assignment(self, user: User, new_roles: list[Role]) -> list[str]:
        """验证角色分配
        
        Args:
            user: 用户实体
            new_roles: 新角色列表
            
        Returns:
            验证错误列表
        """
        errors = []

        # 用户必须至少有一个角色
        if not new_roles:
            errors.append("用户必须至少分配一个角色")

        # 检查角色冲突
        role_types = [role.role_type for role in new_roles]
        if len(set(role_types)) != len(role_types):
            errors.append("不能分配相同类型的多个角色")

        # 检查系统角色分配权限（简化处理）
        system_roles = [role for role in new_roles if role.is_system_role]
        if len(system_roles) > 1:
            errors.append("不能分配多个系统角色")

        return errors

    def calculate_user_risk_score(self, user: User) -> dict[str, Any]:
        """计算用户风险评分
        
        Args:
            user: 用户实体
            
        Returns:
            风险评分结果
        """
        risk_score = 0
        risk_factors = []

        # 账户状态风险
        if user.status == UserStatus.SUSPENDED:
            risk_score += 50
            risk_factors.append("账户被暂停")
        elif user.status == UserStatus.INACTIVE:
            risk_score += 20
            risk_factors.append("账户不活跃")

        # 邮箱验证风险
        if not user.email_verified:
            risk_score += 30
            risk_factors.append("邮箱未验证")

        # 权限风险
        if user.is_super_admin():
            risk_score += 100
            risk_factors.append("拥有超级管理员权限")
        elif len(user.roles) > 3:
            risk_score += 25
            risk_factors.append("拥有多个角色")

        # 最后登录时间风险
        if user.last_login_at:
            days_since_login = (datetime.utcnow() - user.last_login_at).days
            if days_since_login > 90:
                risk_score += 40
                risk_factors.append("长时间未登录")
            elif days_since_login > 30:
                risk_score += 15
                risk_factors.append("较长时间未登录")
        else:
            risk_score += 20
            risk_factors.append("从未登录")

        # 确定风险级别
        if risk_score >= 150:
            risk_level = "CRITICAL"
        elif risk_score >= 100:
            risk_level = "HIGH"
        elif risk_score >= 50:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "user_id": str(user.id),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "assessment_time": datetime.utcnow().isoformat()
        }

    def get_user_lifecycle_summary(self, user: User) -> dict[str, Any]:
        """获取用户生命周期摘要
        
        Args:
            user: 用户实体
            
        Returns:
            生命周期摘要
        """
        account_age_days = (datetime.utcnow() - user.created_at).days if user.created_at else 0
        days_since_update = (datetime.utcnow() - user.updated_at).days if user.updated_at else 0
        days_since_login = None

        if user.last_login_at:
            days_since_login = (datetime.utcnow() - user.last_login_at).days

        return {
            "user_id": str(user.id),
            "current_status": user.status.value,
            "account_age_days": account_age_days,
            "email_verified": user.email_verified,
            "roles_count": len(user.roles),
            "is_super_admin": user.is_super_admin(),
            "days_since_last_update": days_since_update,
            "days_since_last_login": days_since_login,
            "key_version": user.key_version,
            "possible_transitions": [
                status.value for status in self.STATE_TRANSITIONS.get(user.status, [])
            ]
        }

    def suggest_lifecycle_actions(self, user: User) -> list[dict[str, Any]]:
        """建议生命周期操作
        
        Args:
            user: 用户实体
            
        Returns:
            建议操作列表
        """
        suggestions = []

        # 邮箱验证建议
        if not user.email_verified:
            suggestions.append({
                "action": "verify_email",
                "priority": "HIGH",
                "description": "用户邮箱未验证，建议发送验证邮件"
            })

        # 长期不活跃用户建议
        if user.last_login_at:
            days_since_login = (datetime.utcnow() - user.last_login_at).days
            if days_since_login > 180:
                suggestions.append({
                    "action": "deactivate_inactive_user",
                    "priority": "MEDIUM",
                    "description": f"用户{days_since_login}天未登录，建议暂停账户"
                })

        # 权限审查建议
        if len(user.roles) > 5:
            suggestions.append({
                "action": "review_permissions",
                "priority": "MEDIUM",
                "description": "用户拥有过多角色，建议进行权限审查"
            })

        # 密码重置建议
        if user.key_version == 1:
            suggestions.append({
                "action": "password_reset",
                "priority": "LOW",
                "description": "用户从未更改密码，建议提醒修改"
            })

        return suggestions
