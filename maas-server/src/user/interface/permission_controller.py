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

"""权限管理控制器"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from loguru import logger

from shared.application.response import ApiResponse
from user.application import get_permission_application_service
from user.application.decorators import audit_admin_operation
from user.application.permission_service import PermissionApplicationService
from user.application.schemas import (
    PermissionBatchRequest,
    PermissionRequest,
    PermissionSearchQuery,
    PermissionUpdateRequest,
    PermissionResponse,
    PermissionExportResponse,
    PermissionListData,
    BatchPermissionData,
    PermissionValidationData
)

router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.get("", response_model=ApiResponse[PermissionListData])
async def get_permissions(
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
    name: str | None = Query(None, description="权限名称关键词"),
    module: str | None = Query(None, description="模块"),
    resource: str | None = Query(None, description="资源"),
    action: str | None = Query(None, description="操作"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """获取权限列表（支持搜索和分页）"""

    offset = (page - 1) * limit
    query = PermissionSearchQuery(
        name=name,
        module=module,
        resource=resource,
        action=action,
        limit=limit,
        offset=offset,
    )

    permissions = await permission_service.search_permissions(query)

    # 构建分页响应
    response_data = PermissionListData(
        permissions=permissions,
        pagination={
            "page": page,
            "limit": limit,
            "total": len(permissions),
            "has_more": len(permissions) == limit
        },
        filters=PermissionSearchQuery(
            name=name,
            module=module,
            resource=resource,
            action=action
        ),
    )

    return ApiResponse.success_response(data=response_data, message="获取权限列表成功")


@router.get("/modules/{module}", response_model=ApiResponse[list[PermissionResponse]])
async def get_permissions_by_module(
    module: str,
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
):
    """按模块获取权限"""

    permissions = await permission_service.get_permissions_by_module(module)
    return ApiResponse.success_response(data=permissions, message=f"获取模块 {module} 权限成功")


@router.post("", response_model=ApiResponse[PermissionResponse])
@audit_admin_operation("管理员操作")
async def create_permission(
    request: PermissionRequest,
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
):
    """创建新权限（仅超级管理员）"""

    permission = await permission_service.create_permission(request)
    logger.info(f"权限创建成功: {permission.name}")
    return ApiResponse.success_response(data=permission, message="权限创建成功")


@router.get("/{permission_id}", response_model=ApiResponse[PermissionResponse])
async def get_permission(
    permission_id: UUID,
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
):
    """获取权限详情"""

    permission = await permission_service.get_permission(permission_id)
    if not permission:
        return ApiResponse.error_response(
            message="权限不存在",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return ApiResponse.success_response(data=permission, message="获取权限详情成功")


@router.put("/{permission_id}", response_model=ApiResponse[PermissionResponse])
@audit_admin_operation("管理员操作")
async def update_permission(
    permission_id: UUID,
    request: PermissionUpdateRequest,
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
):
    """更新权限（仅超级管理员）"""

    permission = await permission_service.update_permission(permission_id, request)
    logger.info(f"权限更新成功: {permission.name}")
    return ApiResponse.success_response(data=permission, message="权限更新成功")


@router.delete("/{permission_id}", response_model=ApiResponse[None])
@audit_admin_operation("管理员操作")
async def delete_permission(
    permission_id: UUID,
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
):
    """删除权限（仅超级管理员）"""

    success = await permission_service.delete_permission(permission_id)
    if success:
        logger.info(f"权限删除成功: {permission_id}")
        return ApiResponse.success_response(message="权限删除成功")

    return ApiResponse.error_response(message="权限删除失败")


# 批量操作接口
@router.post("/batch", response_model=ApiResponse[BatchPermissionData])
@audit_admin_operation("管理员操作")
async def batch_create_permissions(
    request: PermissionBatchRequest,
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
):
    """批量创建权限（仅超级管理员）"""

    permissions = await permission_service.batch_create_permissions(request)
    logger.info(f"批量创建权限成功，共创建 {len(permissions)} 个权限")
    response_data = BatchPermissionData(    
        created_permissions=permissions,
        created_count=len(permissions)
    )
    return ApiResponse.success_response(
        data=response_data,
        message=f"批量创建权限成功，共创建 {len(permissions)} 个权限"
    )


@router.delete("/batch", response_model=ApiResponse[BatchPermissionData])
@audit_admin_operation("管理员操作")
async def batch_delete_permissions(
    permission_ids: list[UUID],
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
):
    """批量删除权限（仅超级管理员）"""

    result = await permission_service.batch_delete_permissions(permission_ids)
    logger.info(f"批量删除权限完成，成功删除 {result['deleted_count']} 个权限")

    return ApiResponse.success_response(
        data=result,
        message=f"批量删除权限完成，成功删除 {result['deleted_count']} 个权限"
    )


# 导入导出接口
@router.get("/export", response_model=ApiResponse[PermissionExportResponse])
async def export_permissions(
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
    module: str | None = Query(None, description="导出指定模块的权限"),
):
    """导出权限配置（仅超级管理员）"""

    export_data = await permission_service.export_permissions(module)
    logger.info(f"权限配置导出成功，共 {export_data.total_count} 个权限")

    return ApiResponse.success_response(
        data=export_data,
        message=f"权限配置导出成功，共 {export_data.total_count} 个权限"
    )


@router.post("/import", response_model=ApiResponse[BatchPermissionData])
@audit_admin_operation("管理员操作")
async def import_permissions(
    import_data: list[dict[str, Any]],
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
):
    """导入权限配置（仅超级管理员）"""

    result = await permission_service.import_permissions(import_data)
    logger.info(f"权限配置导入完成，成功导入 {result['imported_count']} 个权限")

    return ApiResponse.success_response(
        data=result,
        message=f"权限配置导入完成，成功导入 {result['imported_count']} 个权限"
    )


# 权限验证接口
@router.get("/validate/{user_id}", response_model=ApiResponse[PermissionValidationData])
async def validate_user_permission(
    user_id: UUID,
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
    permission_name: str = Query(..., description="权限名称"),
):
    """验证用户权限"""

    has_permission = await permission_service.validate_permission(user_id, permission_name)
    response_data = PermissionValidationData(
        user_id=str(user_id),
        permission=permission_name,
        has_permission=has_permission
    )
    return ApiResponse.success_response(
        data=response_data,
        message="权限验证完成"
    )


@router.get("/validate/{user_id}/by-parts", response_model=ApiResponse[PermissionValidationData])
async def validate_user_permission_by_parts(
    user_id: UUID,
    permission_service: Annotated[PermissionApplicationService, Depends(get_permission_application_service)],
    resource: str = Query(..., description="资源"),
    action: str = Query(..., description="操作"),
    module: str = Query(None, description="模块"),
):
    """通过资源和操作验证用户权限"""

    has_permission = await permission_service.validate_permission_by_parts(
        user_id, resource, action, module
    )

    permission_name = f"{module}.{resource}.{action}"
    response_data = PermissionValidationData(
        user_id=str(user_id),
        permission=permission_name,
        has_permission=has_permission,
        resource=resource,
        action=action,
        module=module
    )
    return ApiResponse.success_response(
        data=response_data,
        message="权限验证完成"
    )
