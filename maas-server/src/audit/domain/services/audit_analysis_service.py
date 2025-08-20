"""
Copyright 2025 MaaS Team

审计日志分析领域服务

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

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from audit.domain.models import ActionType, AuditLog, AuditResult
from shared.domain.base import DomainService


class AuditAnalysisService(DomainService):
    """审计日志分析领域服务
    
    负责审计日志的统计分析，识别异常模式，生成安全报告。
    为安全团队提供洞察和决策支持。
    """

    def analyze_user_behavior(self, logs: list[AuditLog], user_id: UUID) -> dict[str, Any]:
        """分析用户行为模式
        
        Args:
            logs: 审计日志列表
            user_id: 用户ID
            
        Returns:
            用户行为分析结果
        """
        user_logs = [log for log in logs if log.user_id == user_id]

        if not user_logs:
            return {"error": "未找到用户操作记录"}

        # 时间分析
        login_times = [log.created_at.hour for log in user_logs
                      if log.action == ActionType.LOGIN]
        peak_hours = Counter(login_times).most_common(3)

        # 操作分析
        actions = [log.action for log in user_logs]
        action_counts = Counter(actions)

        # IP地址分析
        ip_addresses = [log.ip_address for log in user_logs if log.ip_address]
        unique_ips = len(set(ip_addresses))
        ip_counts = Counter(ip_addresses)

        # 失败率分析
        total_operations = len(user_logs)
        failed_operations = len([log for log in user_logs
                               if log.result == AuditResult.FAILURE])
        failure_rate = failed_operations / total_operations if total_operations > 0 else 0

        return {
            "user_id": str(user_id),
            "analysis_period": {
                "start": min(log.created_at for log in user_logs).isoformat(),
                "end": max(log.created_at for log in user_logs).isoformat()
            },
            "activity_summary": {
                "total_operations": total_operations,
                "unique_actions": len(action_counts),
                "failure_rate": round(failure_rate, 4)
            },
            "time_patterns": {
                "peak_hours": [(hour, count) for hour, count in peak_hours],
                "total_login_sessions": len(login_times)
            },
            "access_patterns": {
                "unique_ip_count": unique_ips,
                "most_common_ips": ip_counts.most_common(3)
            },
            "operation_patterns": {
                "most_common_actions": action_counts.most_common(5)
            }
        }

    def detect_suspicious_activities(self, logs: list[AuditLog]) -> list[dict[str, Any]]:
        """检测可疑活动
        
        Args:
            logs: 审计日志列表
            
        Returns:
            可疑活动列表
        """
        suspicious_activities = []

        # 检测1: 短时间内大量失败登录
        failed_logins = [log for log in logs
                        if log.action == ActionType.LOGIN_FAILED]

        for user_id in set(log.user_id for log in failed_logins if log.user_id):
            user_failed_logins = [log for log in failed_logins
                                 if log.user_id == user_id]

            # 检查1小时内是否有超过5次失败登录
            for log in user_failed_logins:
                hour_window = timedelta(hours=1)
                window_start = log.created_at - hour_window
                window_end = log.created_at + hour_window

                window_failures = [l for l in user_failed_logins
                                  if window_start <= l.created_at <= window_end]

                if len(window_failures) >= 5:
                    suspicious_activities.append({
                        "type": "BRUTE_FORCE_ATTACK",
                        "severity": "HIGH",
                        "user_id": str(user_id),
                        "description": f"1小时内{len(window_failures)}次登录失败",
                        "time_window": {
                            "start": window_start.isoformat(),
                            "end": window_end.isoformat()
                        },
                        "evidence_count": len(window_failures)
                    })
                    break

        # 检测2: 异常IP访问
        user_ip_map = defaultdict(set)
        for log in logs:
            if log.user_id and log.ip_address:
                user_ip_map[log.user_id].add(log.ip_address)

        for user_id, ip_set in user_ip_map.items():
            if len(ip_set) > 10:  # 用户使用超过10个不同IP
                suspicious_activities.append({
                    "type": "MULTIPLE_IP_ACCESS",
                    "severity": "MEDIUM",
                    "user_id": str(user_id),
                    "description": f"用户使用了{len(ip_set)}个不同IP地址",
                    "unique_ip_count": len(ip_set),
                    "sample_ips": list(ip_set)[:5]
                })

        # 检测3: 异常时间访问
        night_operations = [log for log in logs
                           if log.created_at.hour < 6 or log.created_at.hour > 22]

        night_users = Counter(log.user_id for log in night_operations if log.user_id)
        for user_id, count in night_users.items():
            if count > 20:  # 夜间操作超过20次
                suspicious_activities.append({
                    "type": "OFF_HOURS_ACTIVITY",
                    "severity": "LOW",
                    "user_id": str(user_id),
                    "description": f"夜间(22:00-06:00)进行了{count}次操作",
                    "operation_count": count
                })

        return suspicious_activities

    def generate_security_summary(self, logs: list[AuditLog], period_days: int = 30) -> dict[str, Any]:
        """生成安全摘要报告
        
        Args:
            logs: 审计日志列表
            period_days: 统计周期天数
            
        Returns:
            安全摘要报告
        """
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        recent_logs = [log for log in logs if log.created_at >= cutoff_date]

        # 基础统计
        total_operations = len(recent_logs)
        failed_operations = len([log for log in recent_logs
                               if log.result == AuditResult.FAILURE])
        unique_users = len(set(log.user_id for log in recent_logs if log.user_id))

        # 操作类型分析
        action_stats = Counter(log.action for log in recent_logs)

        # 高风险操作统计
        high_risk_actions = {
            ActionType.USER_DELETE, ActionType.ROLE_DELETE,
            ActionType.PERMISSION_DELETE, ActionType.SYSTEM_SETTING_UPDATE
        }
        high_risk_count = len([log for log in recent_logs
                              if log.action in high_risk_actions])

        # 登录统计
        login_attempts = len([log for log in recent_logs
                            if log.action in [ActionType.LOGIN, ActionType.LOGIN_FAILED]])
        failed_logins = len([log for log in recent_logs
                           if log.action == ActionType.LOGIN_FAILED])

        # 可疑活动检测
        suspicious_activities = self.detect_suspicious_activities(recent_logs)

        return {
            "report_period": {
                "days": period_days,
                "start_date": cutoff_date.isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "overview": {
                "total_operations": total_operations,
                "failed_operations": failed_operations,
                "failure_rate": round(failed_operations / total_operations, 4)
                              if total_operations > 0 else 0,
                "unique_active_users": unique_users,
                "high_risk_operations": high_risk_count
            },
            "authentication": {
                "total_login_attempts": login_attempts,
                "failed_login_attempts": failed_logins,
                "login_success_rate": round((login_attempts - failed_logins) / login_attempts, 4)
                                    if login_attempts > 0 else 0
            },
            "top_operations": action_stats.most_common(10),
            "security_alerts": {
                "suspicious_activities_count": len(suspicious_activities),
                "high_severity_count": len([a for a in suspicious_activities
                                          if a["severity"] == "HIGH"]),
                "activities": suspicious_activities
            }
        }

    def analyze_operation_trends(self, logs: list[AuditLog], days: int = 7) -> dict[str, Any]:
        """分析操作趋势
        
        Args:
            logs: 审计日志列表
            days: 分析天数
            
        Returns:
            操作趋势分析
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # 按天分组统计
        daily_stats = defaultdict(lambda: {
            "total": 0,
            "failed": 0,
            "users": set(),
            "actions": Counter()
        })

        for log in logs:
            if start_date <= log.created_at <= end_date:
                day_key = log.created_at.date().isoformat()
                daily_stats[day_key]["total"] += 1

                if log.result == AuditResult.FAILURE:
                    daily_stats[day_key]["failed"] += 1

                if log.user_id:
                    daily_stats[day_key]["users"].add(log.user_id)

                daily_stats[day_key]["actions"][log.action] += 1

        # 转换为序列化格式
        trends = []
        for day in sorted(daily_stats.keys()):
            stats = daily_stats[day]
            trends.append({
                "date": day,
                "total_operations": stats["total"],
                "failed_operations": stats["failed"],
                "active_users": len(stats["users"]),
                "top_actions": stats["actions"].most_common(3)
            })

        return {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "daily_trends": trends,
            "summary": {
                "avg_daily_operations": sum(t["total_operations"] for t in trends) / len(trends)
                                      if trends else 0,
                "peak_day": max(trends, key=lambda x: x["total_operations"]) if trends else None,
                "most_active_day": max(trends, key=lambda x: x["active_users"]) if trends else None
            }
        }
