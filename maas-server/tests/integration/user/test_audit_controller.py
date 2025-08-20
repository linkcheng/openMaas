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

"""权限审计API控制器集成测试"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from audit.application.services import AuditLogService
from audit.application.schemas import AuditLogListResponse, AuditLogResponse
from audit.domain.models import ActionType, AuditResult, ResourceType
from user.interface.audit_controller import router
from user.application import get_audit_log_service


@pytest.fixture
def mock_audit_service():
    """模拟审计服务"""
    service = AsyncMock(spec=AuditLogService)
    return service


@pytest.fixture
def test_audit_logs():
    """测试审计日志数据"""
    logs = []
    for i in range(5):
        log = MagicMock(spec=AuditLogResponse)
        log.audit_log_id = uuid4()
        log.user_id = uuid4()
        log.username = f"testuser{i}"
        log.action = ActionType.PERMISSION_CREATE
        log.resource_type = ResourceType.PERMISSION
        log.resource_id = uuid4()
        log.description = f"创建权限 test.permission.{i}"
        log.ip_address = "192.168.1.1"
        log.user_agent = "TestAgent/1.0"
        log.request_id = f"req-{i}"
        log.result = AuditResult.SUCCESS
        log.error_message = None
        log.metadata = {
            "permission_name": f"test.permission.{i}",
            "has_permission": True,
            "granted_by_roles": ["admin"]
        }
        log.created_at = datetime.utcnow() - timedelta(hours=i)
        logs.append(log)
    return logs


@pytest.fixture
def test_client(mock_audit_service):
    """测试客户端"""
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    
    # 模拟依赖注入
    app.dependency_overrides[get_audit_log_service] = lambda: mock_audit_service
    
    return TestClient(app)


class TestPermissionAuditController:
    """权限审计控制器测试"""

    @patch("user.interface.audit_controller.require_permission")
    def test_get_permission_audit_logs_success(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service,
        test_audit_logs
    ):
        """测试获取权限审计日志成功"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟审计服务返回数据
        mock_audit_service.query_audit_logs.return_value = AuditLogListResponse(
            items=test_audit_logs,
            total=len(test_audit_logs),
            page=1,
            page_size=20,
            total_pages=1
        )
        
        # 发送请求
        response = test_client.get("/api/v1/audit/permissions/logs")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) == len(test_audit_logs)

    @patch("user.interface.audit_controller.require_permission")
    def test_get_permission_audit_logs_with_filters(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service,
        test_audit_logs
    ):
        """测试带筛选条件的权限审计日志查询"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟审计服务返回数据
        mock_audit_service.query_audit_logs.return_value = AuditLogListResponse(
            items=test_audit_logs[:2],
            total=2,
            page=1,
            page_size=20,
            total_pages=1
        )
        
        # 发送带筛选条件的请求
        response = test_client.get(
            "/api/v1/audit/permissions/logs",
            params={
                "username": "testuser1",
                "permission_name": "test.permission.1",
                "result": "SUCCESS",
                "page": 1,
                "size": 10
            }
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) == 2

    @patch("user.interface.audit_controller.require_permission")
    def test_get_permission_audit_stats_success(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service,
        test_audit_logs
    ):
        """测试获取权限审计统计成功"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟查询审计日志
        mock_audit_service.query_audit_logs.return_value = AuditLogListResponse(
            items=test_audit_logs,
            total=len(test_audit_logs),
            page=1,
            page_size=10000,
            total_pages=1
        )
        
        # 发送请求
        response = test_client.get("/api/v1/audit/permissions/stats")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_checks" in data["data"]
        assert "successful_checks" in data["data"]
        assert "failed_checks" in data["data"]
        assert "unique_users" in data["data"]
        assert "unique_permissions" in data["data"]
        assert "top_permissions" in data["data"]
        assert "top_users" in data["data"]

    @patch("user.interface.audit_controller.require_permission")
    def test_export_permission_audit_logs_csv(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service,
        test_audit_logs
    ):
        """测试导出权限审计日志为CSV"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟审计服务返回数据
        mock_audit_service.query_audit_logs.return_value = AuditLogListResponse(
            items=test_audit_logs,
            total=len(test_audit_logs),
            page=1,
            page_size=10000,
            total_pages=1
        )
        
        # 发送导出请求
        export_request = {
            "username": "testuser",
            "start_time": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "page": 1,
            "size": 10000
        }
        
        response = test_client.post(
            "/api/v1/audit/permissions/export",
            json=export_request,
            params={"format": "csv"}
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

    @patch("user.interface.audit_controller.require_permission")
    def test_analyze_permission_usage_success(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service,
        test_audit_logs
    ):
        """测试权限使用分析成功"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟审计服务返回数据
        mock_audit_service.query_audit_logs.return_value = AuditLogListResponse(
            items=test_audit_logs,
            total=len(test_audit_logs),
            page=1,
            page_size=10000,
            total_pages=1
        )
        
        # 发送分析请求
        response = test_client.get("/api/v1/audit/permissions/analysis")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis_period" in data["data"]
        assert "summary" in data["data"]
        assert "anomalies" in data["data"]
        assert "trends" in data["data"]
        assert "user_behavior" in data["data"]
        assert "recommendations" in data["data"]

    @patch("user.interface.audit_controller.require_permission")
    def test_permission_required_decorator(
        self,
        mock_require_permission,
        test_client
    ):
        """测试权限验证装饰器"""
        # 模拟权限验证失败
        def mock_permission_check(permission):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    raise HTTPException(status_code=403, detail="权限不足")
                return wrapper
            return decorator
        
        mock_require_permission.side_effect = mock_permission_check
        
        # 发送请求
        response = test_client.get("/api/v1/audit/permissions/logs")
        
        # 验证权限验证被调用
        assert response.status_code == 403

    @patch("user.interface.audit_controller.require_permission")
    def test_query_with_time_range(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service,
        test_audit_logs
    ):
        """测试带时间范围的查询"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟审计服务返回数据
        mock_audit_service.query_audit_logs.return_value = AuditLogListResponse(
            items=test_audit_logs,
            total=len(test_audit_logs),
            page=1,
            page_size=20,
            total_pages=1
        )
        
        # 发送带时间范围的请求
        start_time = (datetime.utcnow() - timedelta(days=7)).isoformat()
        end_time = datetime.utcnow().isoformat()
        
        response = test_client.get(
            "/api/v1/audit/permissions/logs",
            params={
                "start_time": start_time,
                "end_time": end_time
            }
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("user.interface.audit_controller.require_permission")
    def test_stats_with_custom_time_range(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service,
        test_audit_logs
    ):
        """测试自定义时间范围的统计"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟审计服务返回数据
        mock_audit_service.query_audit_logs.return_value = AuditLogListResponse(
            items=test_audit_logs,
            total=len(test_audit_logs),
            page=1,
            page_size=10000,
            total_pages=1
        )
        
        # 发送带时间范围的统计请求
        start_time = (datetime.utcnow() - timedelta(days=30)).isoformat()
        end_time = datetime.utcnow().isoformat()
        
        response = test_client.get(
            "/api/v1/audit/permissions/stats",
            params={
                "start_time": start_time,
                "end_time": end_time
            }
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("user.interface.audit_controller.require_permission")
    def test_analysis_with_specific_user(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service,
        test_audit_logs
    ):
        """测试特定用户的权限使用分析"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟审计服务返回数据
        mock_audit_service.query_audit_logs.return_value = AuditLogListResponse(
            items=test_audit_logs[:2],  # 只返回特定用户的日志
            total=2,
            page=1,
            page_size=10000,
            total_pages=1
        )
        
        # 发送特定用户的分析请求
        user_id = str(uuid4())
        response = test_client.get(
            "/api/v1/audit/permissions/analysis",
            params={"user_id": user_id}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("user.interface.audit_controller.require_permission")
    def test_error_handling(
        self,
        mock_require_permission,
        test_client,
        mock_audit_service
    ):
        """测试错误处理"""
        # 模拟权限验证通过
        mock_require_permission.return_value = lambda func: func
        
        # 模拟审计服务抛出异常
        mock_audit_service.query_audit_logs.side_effect = Exception("Database error")
        
        # 发送请求
        response = test_client.get("/api/v1/audit/permissions/logs")
        
        # 验证错误响应
        assert response.status_code == 500

    def test_csv_generation(self):
        """测试CSV生成功能"""
        from user.interface.audit_controller import _generate_csv_export, PermissionAuditResponse
        
        # 创建测试数据
        test_items = [
            PermissionAuditResponse(
                id=uuid4(),
                user_id=uuid4(),
                username="testuser",
                action="PERMISSION_CREATE",
                permission_name="test.permission",
                resource_type="PERMISSION",
                resource_id=uuid4(),
                description="创建权限",
                ip_address="192.168.1.1",
                user_agent="TestAgent/1.0",
                request_id="req-123",
                result="SUCCESS",
                error_message=None,
                metadata={},
                created_at=datetime.utcnow(),
                has_permission=True,
                granted_by_roles=["admin"],
                is_sensitive_operation=True
            )
        ]
        
        # 生成CSV
        csv_content = _generate_csv_export(test_items)
        
        # 验证CSV内容
        assert "ID" in csv_content
        assert "用户名" in csv_content
        assert "testuser" in csv_content
        assert "PERMISSION_CREATE" in csv_content

    def test_sensitive_operation_detection(self):
        """测试敏感操作检测"""
        from user.interface.audit_controller import _is_sensitive_operation
        from audit.domain.models import ActionType
        
        # 测试敏感操作
        assert _is_sensitive_operation(ActionType.PERMISSION_CREATE, {}) is True
        assert _is_sensitive_operation(ActionType.ROLE_DELETE, {}) is True
        
        # 测试非敏感操作
        assert _is_sensitive_operation(ActionType.USER_LOGIN, {}) is False
        
        # 测试元数据标记
        assert _is_sensitive_operation(ActionType.USER_LOGIN, {"is_sensitive": True}) is True

    def test_hourly_stats_calculation(self):
        """测试按小时统计计算"""
        from user.interface.audit_controller import _calculate_hourly_stats, PermissionAuditResponse
        
        # 创建测试数据
        items = []
        for hour in [9, 10, 10, 11]:
            item = MagicMock(spec=PermissionAuditResponse)
            item.created_at = datetime.utcnow().replace(hour=hour)
            items.append(item)
        
        # 计算统计
        stats = _calculate_hourly_stats(items)
        
        # 验证结果
        assert len(stats) == 3  # 9, 10, 11点
        hour_10_stat = next(s for s in stats if s["hour"] == 10)
        assert hour_10_stat["count"] == 2

    def test_daily_stats_calculation(self):
        """测试按天统计计算"""
        from user.interface.audit_controller import _calculate_daily_stats, PermissionAuditResponse
        
        # 创建测试数据
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        items = []
        for date in [today, today, yesterday]:
            item = MagicMock(spec=PermissionAuditResponse)
            item.created_at = datetime.combine(date, datetime.min.time())
            items.append(item)
        
        # 计算统计
        stats = _calculate_daily_stats(items)
        
        # 验证结果
        assert len(stats) == 2  # 今天和昨天
        today_stat = next(s for s in stats if s["date"] == today.isoformat())
        assert today_stat["count"] == 2