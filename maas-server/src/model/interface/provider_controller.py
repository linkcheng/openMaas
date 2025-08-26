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

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from model.application import (
    ProviderApplicationService,
    provider_application_service,
)
from model.application.schemas import (
    CreateModelConfigRequest,
    CreateProviderRequest,
    ListModelConfigsParams,
    ListProvidersParams,
    ModelConfigResponse,
    ProviderResponse,
    SearchProvidersParams,
    UpdateModelConfigRequest,
    UpdateProviderRequest,
)
from model.domain.exceptions import (
    ModelConfigAlreadyExistsException,
    ModelConfigNotFoundException,
    ProviderAlreadyExistsException,
    ProviderNotFoundException,
)
from shared.application.response import ApiResponse, PaginatedData
from user.infrastructure.permission import get_current_user_id

router = APIRouter(prefix="/models", tags=["模型管理"])


@router.post("/providers", response_model=ApiResponse[ProviderResponse])
async def create_provider(
    request: CreateProviderRequest,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
):
    """
    创建供应商接口

    创建新的AI模型供应商配置。需要超级管理员权限。

    - **provider_name**: 供应商名称，必须唯一
    - **provider_type**: 供应商类型（如：openai, anthropic等）
    - **display_name**: 显示名称
    - **description**: 描述信息（可选）
    - **base_url**: API基础URL
    - **api_key**: API密钥（可选）
    - **additional_config**: 额外配置参数（可选）
    - **is_active**: 是否启用，默认为True
    """
    try:
        logger.info(f"Creating provider: {request.provider_name} by user: {current_user_id}")

        provider = await provider_service.create_provider(request, str(current_user_id))
        provider_response = ProviderResponse.from_orm(provider)

        return ApiResponse.success_response(
            data=provider_response,
            message=f"供应商 '{request.provider_name}' 创建成功",
            code=201
        )

    except ProviderAlreadyExistsException:
        logger.warning(f"Provider already exists: {request.provider_name}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"供应商 '{request.provider_name}' 已存在"
        )
    except Exception as e:
        logger.error(f"Failed to create provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建供应商失败"
        )


@router.get("/providers", response_model=ApiResponse[PaginatedData[ProviderResponse]])
async def list_providers(
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)],
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页大小，最大100"),
    provider_type: str = Query(None, description="供应商类型过滤"),
    is_active: bool = Query(None, description="是否启用过滤"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="排序方向")
):
    """
    查询供应商列表接口

    获取供应商列表，支持分页和过滤。需要超级管理员权限。

    - **page**: 页码，从1开始
    - **size**: 每页大小，最大100
    - **provider_type**: 按供应商类型过滤（可选）
    - **is_active**: 按启用状态过滤（可选）
    - **sort_by**: 排序字段，默认为created_at
    - **sort_order**: 排序方向，asc或desc，默认为desc
    """
    try:
        logger.debug(f"Listing providers with page={page}, size={size}")

        params = ListProvidersParams(
            page=page,
            size=size,
            provider_type=provider_type,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order
        )

        result = await provider_service.list_providers(params)

        # 转换为响应模型
        provider_responses = [ProviderResponse.from_orm(provider) for provider in result.items]

        return ApiResponse.paginated_response(
            items=provider_responses,
            total=result.total,
            page=result.page,
            size=result.size,
            message="查询供应商列表成功"
        )

    except Exception as e:
        logger.error(f"Failed to list providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询供应商列表失败"
        )


@router.get("/providers/{provider_id}", response_model=ApiResponse[ProviderResponse])
async def get_provider(
    provider_id: int,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)]
):
    """
    获取单个供应商接口

    根据供应商ID获取详细信息。需要超级管理员权限。

    - **provider_id**: 供应商ID
    """
    try:
        logger.debug(f"Getting provider: {provider_id}")

        provider = await provider_service.get_provider(provider_id)
        provider_response = ProviderResponse.from_orm(provider)

        return ApiResponse.success_response(
            data=provider_response,
            message="获取供应商信息成功"
        )

    except ProviderNotFoundException:
        logger.warning(f"Provider not found: {provider_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商 {provider_id} 不存在"
        )
    except Exception as e:
        logger.error(f"Failed to get provider {provider_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取供应商信息失败"
        )


@router.put("/providers/{provider_id}", response_model=ApiResponse[ProviderResponse])
async def update_provider(
    provider_id: int,
    request: UpdateProviderRequest,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
):
    """
    更新供应商接口

    更新指定供应商的配置信息。需要超级管理员权限。

    - **provider_id**: 供应商ID
    - **request**: 更新请求，所有字段都是可选的
    """
    try:
        logger.info(f"Updating provider: {provider_id} by user: {current_user_id}")

        provider = await provider_service.update_provider(provider_id, request, str(current_user_id))
        provider_response = ProviderResponse.from_orm(provider)

        return ApiResponse.success_response(
            data=provider_response,
            message=f"供应商 {provider_id} 更新成功"
        )

    except ProviderNotFoundException:
        logger.warning(f"Provider not found: {provider_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商 {provider_id} 不存在"
        )
    except ProviderAlreadyExistsException as e:
        logger.warning(f"Provider name conflict during update: {provider_id}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update provider {provider_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新供应商失败"
        )


@router.delete("/providers/{provider_id}", response_model=ApiResponse[None])
async def delete_provider(
    provider_id: int,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)]
):
    """
    删除供应商接口

    删除指定的供应商。如果供应商下有活跃的模型配置，将无法删除。需要超级管理员权限。

    - **provider_id**: 供应商ID
    """
    try:
        logger.info(f"Deleting provider: {provider_id}")

        success = await provider_service.delete_provider(provider_id)

        if success:
            return ApiResponse.success_response(
                data=None,
                message=f"供应商 {provider_id} 删除成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除供应商失败"
            )

    except ProviderNotFoundException:
        logger.warning(f"Provider not found: {provider_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商 {provider_id} 不存在"
        )
    except Exception as e:
        logger.error(f"Failed to delete provider {provider_id}: {e}")
        if "活跃的模型配置" in str(e):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除供应商失败"
        )


@router.post("/providers/{provider_id}/activate", response_model=ApiResponse[None])
async def activate_provider(
    provider_id: int,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)]
):
    """
    激活供应商接口

    激活指定的供应商，使其可以被使用。需要超级管理员权限。

    - **provider_id**: 供应商ID
    """
    try:
        logger.info(f"Activating provider: {provider_id}")

        success = await provider_service.activate_provider(provider_id)

        if success:
            return ApiResponse.success_response(
                data=None,
                message=f"供应商 {provider_id} 激活成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="激活供应商失败"
            )

    except ProviderNotFoundException:
        logger.warning(f"Provider not found: {provider_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商 {provider_id} 不存在"
        )
    except Exception as e:
        logger.error(f"Failed to activate provider {provider_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="激活供应商失败"
        )


@router.post("/providers/{provider_id}/deactivate", response_model=ApiResponse[None])
async def deactivate_provider(
    provider_id: int,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)]
):
    """
    停用供应商接口

    停用指定的供应商，使其无法被使用。需要超级管理员权限。

    - **provider_id**: 供应商ID
    """
    try:
        logger.info(f"Deactivating provider: {provider_id}")

        success = await provider_service.deactivate_provider(provider_id)

        if success:
            return ApiResponse.success_response(
                data=None,
                message=f"供应商 {provider_id} 停用成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="停用供应商失败"
            )

    except ProviderNotFoundException:
        logger.warning(f"Provider not found: {provider_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商 {provider_id} 不存在"
        )
    except Exception as e:
        logger.error(f"Failed to deactivate provider {provider_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="停用供应商失败"
        )


@router.get("/providers/search", response_model=ApiResponse[PaginatedData[ProviderResponse]])
async def search_providers(
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)],
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页大小，最大100"),
    keyword: str = Query(None, min_length=1, max_length=100, description="搜索关键词"),
    provider_type: str = Query(None, description="供应商类型过滤"),
    is_active: bool = Query(None, description="是否启用过滤")
):
    """
    搜索供应商接口

    根据关键词搜索供应商，支持按名称和显示名称模糊搜索。需要超级管理员权限。

    - **page**: 页码，从1开始
    - **size**: 每页大小，最大100
    - **keyword**: 搜索关键词，支持供应商名称和显示名称模糊搜索（可选）
    - **provider_type**: 按供应商类型过滤（可选）
    - **is_active**: 按启用状态过滤（可选）
    """
    try:
        logger.debug(f"Searching providers with keyword='{keyword}', page={page}, size={size}")

        params = SearchProvidersParams(
            page=page,
            size=size,
            keyword=keyword,
            provider_type=provider_type,
            is_active=is_active
        )

        result = await provider_service.search_providers(params)

        # 转换为响应模型
        provider_responses = [ProviderResponse.from_orm(provider) for provider in result.items]

        return ApiResponse.paginated_response(
            items=provider_responses,
            total=result.total,
            page=result.page,
            size=result.size,
            message="搜索供应商成功"
        )

    except Exception as e:
        logger.error(f"Failed to search providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索供应商失败"
        )


@router.post("/providers/{provider_id}/models", response_model=ApiResponse[ModelConfigResponse])
async def create_model_config(
    provider_id: int,
    request: CreateModelConfigRequest,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
):
    """
    创建模型配置接口

    为指定供应商创建新的模型配置。需要超级管理员权限。

    - **provider_id**: 供应商ID
    - **model_name**: 模型名称，在同一供应商下必须唯一
    - **model_display_name**: 模型显示名称
    - **model_type**: 模型类型（如：chat, completion等）
    - **model_params**: 模型参数配置（可选）
    - **max_tokens**: 最大token数，默认4096
    - **max_input_tokens**: 最大输入token数，默认3072
    - **temperature**: 温度参数，默认0.7
    - **pricing_config**: 定价配置（可选）
    - **is_active**: 是否启用，默认为True
    """
    try:
        logger.info(f"Creating model config: {request.model_name} for provider: {provider_id} by user: {current_user_id}")

        model_config = await provider_service.create_model_config(provider_id, request, str(current_user_id))
        model_config_response = ModelConfigResponse.from_orm(model_config)

        return ApiResponse.success_response(
            data=model_config_response,
            message=f"模型配置 '{request.model_name}' 创建成功",
            code=201
        )

    except ProviderNotFoundException:
        logger.warning(f"Provider not found: {provider_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"供应商 {provider_id} 不存在"
        )
    except ModelConfigAlreadyExistsException as e:
        logger.warning(f"Model config already exists: {request.model_name} for provider: {provider_id}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create model config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建模型配置失败"
        )


@router.get("/models", response_model=ApiResponse[PaginatedData[ModelConfigResponse]])
async def list_model_configs(
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)],
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页大小，最大100"),
    provider_id: int = Query(None, description="供应商ID过滤"),
    model_type: str = Query(None, description="模型类型过滤"),
    is_active: bool = Query(None, description="是否启用过滤"),
    keyword: str = Query(None, min_length=1, max_length=100, description="搜索关键词"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="排序方向")
):
    """
    查询模型配置列表接口

    获取模型配置列表，支持分页、过滤和搜索。需要超级管理员权限。

    - **page**: 页码，从1开始
    - **size**: 每页大小，最大100
    - **provider_id**: 按供应商ID过滤（可选）
    - **model_type**: 按模型类型过滤（可选）
    - **is_active**: 按启用状态过滤（可选）
    - **keyword**: 搜索关键词，支持模型名称和显示名称模糊搜索（可选）
    - **sort_by**: 排序字段，默认为created_at
    - **sort_order**: 排序方向，asc或desc，默认为desc
    """
    try:
        logger.debug(f"Listing model configs with page={page}, size={size}")

        params = ListModelConfigsParams(
            page=page,
            size=size,
            provider_id=provider_id,
            model_type=model_type,
            is_active=is_active,
            keyword=keyword,
            sort_by=sort_by,
            sort_order=sort_order
        )

        result = await provider_service.list_model_configs(params)

        # 转换为响应模型
        config_responses = [ModelConfigResponse.from_orm(config) for config in result.items]

        return ApiResponse.paginated_response(
            items=config_responses,
            total=result.total,
            page=result.page,
            size=result.size,
            message="查询模型配置列表成功"
        )

    except Exception as e:
        logger.error(f"Failed to list model configs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询模型配置列表失败"
        )


@router.get("/models/{config_id}", response_model=ApiResponse[ModelConfigResponse])
async def get_model_config(
    config_id: int,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)]
):
    """
    获取单个模型配置接口

    根据配置ID获取模型配置详细信息。需要超级管理员权限。

    - **config_id**: 模型配置ID
    """
    try:
        logger.debug(f"Getting model config: {config_id}")

        model_config = await provider_service.get_model_config(config_id)
        model_config_response = ModelConfigResponse.from_orm(model_config)

        return ApiResponse.success_response(
            data=model_config_response,
            message="获取模型配置信息成功"
        )

    except ModelConfigNotFoundException:
        logger.warning(f"Model config not found: {config_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模型配置 {config_id} 不存在"
        )
    except Exception as e:
        logger.error(f"Failed to get model config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取模型配置信息失败"
        )


@router.put("/models/{config_id}", response_model=ApiResponse[ModelConfigResponse])
async def update_model_config(
    config_id: int,
    request: UpdateModelConfigRequest,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
):
    """
    更新模型配置接口

    更新指定模型配置的信息。需要超级管理员权限。

    - **config_id**: 模型配置ID
    - **request**: 更新请求，所有字段都是可选的
    """
    try:
        logger.info(f"Updating model config: {config_id} by user: {current_user_id}")

        model_config = await provider_service.update_model_config(config_id, request, str(current_user_id))
        model_config_response = ModelConfigResponse.from_orm(model_config)

        return ApiResponse.success_response(
            data=model_config_response,
            message=f"模型配置 {config_id} 更新成功"
        )

    except ModelConfigNotFoundException:
        logger.warning(f"Model config not found: {config_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模型配置 {config_id} 不存在"
        )
    except ModelConfigAlreadyExistsException as e:
        logger.warning(f"Model config name conflict during update: {config_id}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update model config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新模型配置失败"
        )


@router.delete("/models/{config_id}", response_model=ApiResponse[None])
async def delete_model_config(
    config_id: int,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)]
):
    """
    删除模型配置接口

    删除指定的模型配置。需要超级管理员权限。

    - **config_id**: 模型配置ID
    """
    try:
        logger.info(f"Deleting model config: {config_id}")

        success = await provider_service.delete_model_config(config_id)

        if success:
            return ApiResponse.success_response(
                data=None,
                message=f"模型配置 {config_id} 删除成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除模型配置失败"
            )

    except ModelConfigNotFoundException:
        logger.warning(f"Model config not found: {config_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模型配置 {config_id} 不存在"
        )
    except Exception as e:
        logger.error(f"Failed to delete model config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除模型配置失败"
        )


@router.post("/models/{config_id}/activate", response_model=ApiResponse[None])
async def activate_model_config(
    config_id: int,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)]
):
    """
    激活模型配置接口

    激活指定的模型配置，使其可以被使用。需要超级管理员权限。
    注意：只有当关联的供应商也处于激活状态时，模型配置才能被激活。

    - **config_id**: 模型配置ID
    """
    try:
        logger.info(f"Activating model config: {config_id}")

        success = await provider_service.activate_model_config(config_id)

        if success:
            return ApiResponse.success_response(
                data=None,
                message=f"模型配置 {config_id} 激活成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="激活模型配置失败"
            )

    except ModelConfigNotFoundException:
        logger.warning(f"Model config not found: {config_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模型配置 {config_id} 不存在"
        )
    except Exception as e:
        logger.error(f"Failed to activate model config {config_id}: {e}")
        # 检查是否是供应商未激活的错误
        if "供应商未激活" in str(e) or "ProviderInactive" in str(e):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="无法激活模型配置：关联的供应商未激活"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="激活模型配置失败"
        )


@router.post("/models/{config_id}/deactivate", response_model=ApiResponse[None])
async def deactivate_model_config(
    config_id: int,
    provider_service: Annotated[ProviderApplicationService, Depends(provider_application_service)]
):
    """
    停用模型配置接口

    停用指定的模型配置，使其无法被使用。需要超级管理员权限。

    - **config_id**: 模型配置ID
    """
    try:
        logger.info(f"Deactivating model config: {config_id}")

        success = await provider_service.deactivate_model_config(config_id)

        if success:
            return ApiResponse.success_response(
                data=None,
                message=f"模型配置 {config_id} 停用成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="停用模型配置失败"
            )

    except ModelConfigNotFoundException:
        logger.warning(f"Model config not found: {config_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模型配置 {config_id} 不存在"
        )
    except Exception as e:
        logger.error(f"Failed to deactivate model config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="停用模型配置失败"
        )
