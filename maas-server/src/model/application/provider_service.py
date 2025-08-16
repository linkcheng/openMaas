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

import datetime
from collections.abc import AsyncGenerator

from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from model.application.schemas import (
    CreateModelConfigRequest,
    CreateProviderRequest,
    ListModelConfigsParams,
    ListProvidersParams,
    PaginatedResponse,
    SearchProvidersParams,
    UpdateModelConfigRequest,
    UpdateProviderRequest,
)
from model.domain.exceptions import (
    ConcurrentUpdateException,
    ModelConfigAlreadyExistsException,
    ModelConfigNotFoundException,
    ProviderAlreadyExistsException,
    ProviderHasActiveModelsException,
    ProviderNotFoundException,
)
from model.domain.models.provider_model import ModelConfigEntity, ProviderEntity
from model.domain.repository.provider_repository import (
    IModelConfigRepository,
    IProviderRepository,
)
from model.domain.services.provider_service import ProviderDomainService
from model.domain.services.validation_service import ValidationService
from model.infrastructure.repositorise import ModelConfigRepository, ProviderRepository
from shared.infrastructure.database import get_db_session


class ProviderApplicationService:
    """供应商应用服务，处理业务流程编排和事务管理"""

    def __init__(
        self,
        provider_repo: IProviderRepository,
        model_config_repo: IModelConfigRepository,
        provider_domain_service: ProviderDomainService,
        validation_service: ValidationService
    ):
        self.provider_repo = provider_repo
        self.model_config_repo = model_config_repo
        self.provider_domain_service = provider_domain_service
        self.validation_service = validation_service

    async def create_provider(self, request: CreateProviderRequest, user_id: str) -> ProviderEntity:
        """创建供应商，包含唯一性检查和数据验证"""
        logger.info(f"Creating provider: {request.provider_name} by user: {user_id}")

        # 数据验证
        self.validation_service.validate_provider_name(request.provider_name)
        self.validation_service.validate_provider_type(request.provider_type)
        self.validation_service.validate_base_url(request.base_url)
        self.validation_service.validate_display_name(request.display_name)
        self.validation_service.validate_description(request.description)
        self.validation_service.validate_api_key(request.api_key)
        self.validation_service.validate_additional_config(request.additional_config)

        # 唯一性检查
        existing_provider = await self.provider_repo.get_by_name(request.provider_name)
        if existing_provider:
            raise ProviderAlreadyExistsException(request.provider_name)

        # 创建实体
        now = datetime.datetime.utcnow()
        provider = ProviderEntity(
            provider_name=request.provider_name.strip(),
            provider_type=request.provider_type.strip(),
            display_name=request.display_name.strip(),
            description=request.description.strip() if request.description else None,
            base_url=request.base_url.strip(),
            api_key=request.api_key,
            additional_config=request.additional_config,
            is_active=request.is_active,
            created_by=user_id,
            created_at=now,
            updated_by=user_id,
            updated_at=now,
            is_delete=False
        )

        # 保存到数据库
        created_provider = await self.provider_repo.create(provider)
        
        # 安全审计日志
        from model.infrastructure.security import AuditLogger
        AuditLogger.log_data_modification(
            user_id=user_id,
            resource_type="provider",
            resource_id=str(created_provider.provider_id),
            action="create",
            changes={
                "provider_name": request.provider_name,
                "provider_type": request.provider_type,
                "display_name": request.display_name,
                "base_url": request.base_url,
                "is_active": request.is_active
            }
        )
        
        logger.info(f"Provider created successfully: {created_provider.provider_id}")

        return created_provider

    async def get_provider(self, provider_id: int) -> ProviderEntity | None:
        """获取单个供应商"""
        logger.debug(f"Getting provider: {provider_id}")

        provider = await self.provider_repo.get_by_id(provider_id)
        if not provider:
            raise ProviderNotFoundException(provider_id)

        return provider

    async def list_providers(self, params: ListProvidersParams) -> PaginatedResponse[ProviderEntity]:
        """查询供应商列表"""
        logger.debug(f"Listing providers with params: {params}")

        # 构建查询条件
        conditions = {"is_delete": False}
        if params.provider_type:
            conditions["provider_type"] = params.provider_type
        if params.is_active is not None:
            conditions["is_active"] = params.is_active

        # 获取总数
        total = await self.provider_repo.count_by_criteria(conditions)

        # 获取分页数据
        offset = (params.page - 1) * params.size
        providers = await self.provider_repo.find_paginated(
            conditions=conditions,
            offset=offset,
            limit=params.size,
            sort_by=params.sort_by,
            sort_order=params.sort_order
        )

        return PaginatedResponse.create(
            items=providers,
            total=total,
            page=params.page,
            size=params.size
        )

    async def search_providers(self, params: SearchProvidersParams) -> PaginatedResponse[ProviderEntity]:
        """搜索供应商"""
        logger.debug(f"Searching providers with params: {params}")

        # 使用仓储的搜索方法
        providers = await self.provider_repo.search(
            keyword=params.keyword,
            provider_type=params.provider_type,
            is_active=params.is_active
        )

        # 手动分页（实际项目中应该在数据库层面分页）
        total = len(providers)
        start = (params.page - 1) * params.size
        end = start + params.size
        paginated_providers = providers[start:end]

        return PaginatedResponse.create(
            items=paginated_providers,
            total=total,
            page=params.page,
            size=params.size
        )

    async def update_provider(self, provider_id: int, request: UpdateProviderRequest, user_id: str) -> ProviderEntity:
        """更新供应商，包含并发控制和数据验证"""
        logger.info(f"Updating provider: {provider_id} by user: {user_id}")

        # 检查供应商是否存在
        existing_provider = await self.provider_repo.get_by_id(provider_id)
        if not existing_provider:
            raise ProviderNotFoundException(provider_id)

        # 构建更新数据
        update_data = {}

        # 验证并设置更新字段
        if request.provider_name is not None:
            self.validation_service.validate_provider_name(request.provider_name)
            # 检查名称唯一性（排除当前供应商）
            existing_by_name = await self.provider_repo.get_by_name(request.provider_name)
            if existing_by_name and existing_by_name.provider_id != provider_id:
                raise ProviderAlreadyExistsException(request.provider_name)
            update_data["provider_name"] = request.provider_name.strip()

        if request.provider_type is not None:
            self.validation_service.validate_provider_type(request.provider_type)
            update_data["provider_type"] = request.provider_type.strip()

        if request.display_name is not None:
            self.validation_service.validate_display_name(request.display_name)
            update_data["display_name"] = request.display_name.strip()

        if request.description is not None:
            self.validation_service.validate_description(request.description)
            update_data["description"] = request.description.strip() if request.description else None

        if request.base_url is not None:
            self.validation_service.validate_base_url(request.base_url)
            update_data["base_url"] = request.base_url.strip()

        if request.api_key is not None:
            self.validation_service.validate_api_key(request.api_key)
            update_data["api_key"] = request.api_key

        if request.additional_config is not None:
            self.validation_service.validate_additional_config(request.additional_config)
            update_data["additional_config"] = request.additional_config

        if request.is_active is not None:
            update_data["is_active"] = request.is_active

        # 设置更新元数据
        update_data["updated_by"] = user_id
        update_data["updated_at"] = datetime.datetime.utcnow()

        # 执行更新
        success = await self.provider_repo.update(provider_id, update_data)
        if not success:
            raise ConcurrentUpdateException("供应商", provider_id)

        # 返回更新后的供应商
        updated_provider = await self.provider_repo.get_by_id(provider_id)
        logger.info(f"Provider updated successfully: {provider_id}")

        return updated_provider

    async def delete_provider(self, provider_id: int) -> bool:
        """删除供应商"""
        logger.info(f"Deleting provider: {provider_id}")

        # 检查供应商是否存在
        existing_provider = await self.provider_repo.get_by_id(provider_id)
        if not existing_provider:
            raise ProviderNotFoundException(provider_id)

        # 检查是否有活跃的模型配置
        active_models = await self.model_config_repo.search(
            keyword="",
            provider_id=provider_id,
            is_active=True
        )

        if active_models:
            raise ProviderHasActiveModelsException(provider_id, len(active_models))

        # 执行软删除
        success = await self.provider_repo.delete(provider_id)
        if success:
            logger.info(f"Provider deleted successfully: {provider_id}")

        return success

    async def activate_provider(self, provider_id: int) -> bool:
        """激活供应商"""
        logger.info(f"Activating provider: {provider_id}")

        # 检查供应商是否存在
        existing_provider = await self.provider_repo.get_by_id(provider_id)
        if not existing_provider:
            raise ProviderNotFoundException(provider_id)

        # 执行激活
        success = await self.provider_repo.activate(provider_id)
        if success:
            logger.info(f"Provider activated successfully: {provider_id}")

        return success

    async def deactivate_provider(self, provider_id: int) -> bool:
        """停用供应商"""
        logger.info(f"Deactivating provider: {provider_id}")

        # 检查供应商是否存在
        existing_provider = await self.provider_repo.get_by_id(provider_id)
        if not existing_provider:
            raise ProviderNotFoundException(provider_id)

        # 执行停用
        success = await self.provider_repo.deactivate(provider_id)
        if success:
            logger.info(f"Provider deactivated successfully: {provider_id}")

        return success

    async def create_model_config(self, provider_id: int, request: CreateModelConfigRequest, user_id: str) -> ModelConfigEntity:
        """创建模型配置，包含供应商关联验证"""
        logger.info(f"Creating model config: {request.model_name} for provider: {provider_id} by user: {user_id}")

        # 验证供应商是否存在且激活
        provider = await self.provider_repo.get_by_id(provider_id)
        if not provider:
            raise ProviderNotFoundException(provider_id)

        # 数据验证
        self.validation_service.validate_model_name(request.model_name)
        self.validation_service.validate_model_display_name(request.model_display_name)
        self.validation_service.validate_model_type(request.model_type)
        self.validation_service.validate_token_limits(request.max_tokens, request.max_input_tokens)
        self.validation_service.validate_temperature(request.temperature)
        self.validation_service.validate_model_params(request.model_params)
        self.validation_service.validate_pricing_config(request.pricing_config)

        # 检查同一供应商下模型名称的唯一性
        existing_config = await self.model_config_repo.get_by_provider_and_name(provider_id, request.model_name)
        if existing_config:
            raise ModelConfigAlreadyExistsException(provider_id, request.model_name)

        # 创建实体
        now = datetime.datetime.utcnow()
        model_config = ModelConfigEntity(
            provider_id=provider_id,
            model_name=request.model_name.strip(),
            model_display_name=request.model_display_name.strip(),
            model_type=request.model_type.strip(),
            model_params=request.model_params,
            max_tokens=request.max_tokens,
            max_input_tokens=request.max_input_tokens,
            temperature=request.temperature,
            pricing_config=request.pricing_config,
            is_active=request.is_active,
            created_by=user_id,
            created_at=now,
            updated_by=user_id,
            updated_at=now,
            is_delete=False
        )

        # 保存到数据库
        created_config = await self.model_config_repo.create(model_config)
        logger.info(f"Model config created successfully: {created_config.config_id}")

        return created_config

    async def get_model_config(self, config_id: int) -> ModelConfigEntity | None:
        """获取单个模型配置"""
        logger.debug(f"Getting model config: {config_id}")

        config = await self.model_config_repo.get_by_id(config_id)
        if not config:
            raise ModelConfigNotFoundException(config_id)

        return config

    async def list_model_configs(self, params: ListModelConfigsParams) -> PaginatedResponse[ModelConfigEntity]:
        """查询模型配置列表"""
        logger.debug(f"Listing model configs with params: {params}")

        # 构建查询条件
        conditions = {"is_delete": False}
        if params.provider_id:
            conditions["provider_id"] = params.provider_id
        if params.model_type:
            conditions["model_type"] = params.model_type
        if params.is_active is not None:
            conditions["is_active"] = params.is_active

        # 如果有关键词搜索，使用搜索方法
        if params.keyword:
            configs = await self.model_config_repo.search(
                keyword=params.keyword,
                provider_id=params.provider_id,
                model_type=params.model_type,
                is_active=params.is_active
            )

            # 手动分页
            total = len(configs)
            start = (params.page - 1) * params.size
            end = start + params.size
            paginated_configs = configs[start:end]

            return PaginatedResponse.create(
                items=paginated_configs,
                total=total,
                page=params.page,
                size=params.size
            )

        # 获取总数
        total = await self.model_config_repo.count_by_criteria(conditions)

        # 获取分页数据
        offset = (params.page - 1) * params.size
        configs = await self.model_config_repo.find_paginated(
            conditions=conditions,
            offset=offset,
            limit=params.size,
            sort_by=params.sort_by,
            sort_order=params.sort_order
        )

        return PaginatedResponse.create(
            items=configs,
            total=total,
            page=params.page,
            size=params.size
        )

    async def update_model_config(self, config_id: int, request: UpdateModelConfigRequest, user_id: str) -> ModelConfigEntity:
        """更新模型配置"""
        logger.info(f"Updating model config: {config_id} by user: {user_id}")

        # 检查模型配置是否存在
        existing_config = await self.model_config_repo.get_by_id(config_id)
        if not existing_config:
            raise ModelConfigNotFoundException(config_id)

        # 构建更新数据
        update_data = {}

        # 验证并设置更新字段
        if request.model_name is not None:
            self.validation_service.validate_model_name(request.model_name)
            # 检查名称唯一性（排除当前配置）
            existing_by_name = await self.model_config_repo.get_by_provider_and_name(
                existing_config.provider_id, request.model_name
            )
            if existing_by_name and existing_by_name.config_id != config_id:
                raise ModelConfigAlreadyExistsException(existing_config.provider_id, request.model_name)
            update_data["model_name"] = request.model_name.strip()

        if request.model_display_name is not None:
            self.validation_service.validate_model_display_name(request.model_display_name)
            update_data["model_display_name"] = request.model_display_name.strip()

        if request.model_type is not None:
            self.validation_service.validate_model_type(request.model_type)
            update_data["model_type"] = request.model_type.strip()

        if request.model_params is not None:
            self.validation_service.validate_model_params(request.model_params)
            update_data["model_params"] = request.model_params

        if request.max_tokens is not None or request.max_input_tokens is not None:
            # 获取当前值用于验证
            current_max_tokens = request.max_tokens if request.max_tokens is not None else existing_config.max_tokens
            current_max_input_tokens = request.max_input_tokens if request.max_input_tokens is not None else existing_config.max_input_tokens
            self.validation_service.validate_token_limits(current_max_tokens, current_max_input_tokens)

            if request.max_tokens is not None:
                update_data["max_tokens"] = request.max_tokens
            if request.max_input_tokens is not None:
                update_data["max_input_tokens"] = request.max_input_tokens

        if request.temperature is not None:
            self.validation_service.validate_temperature(request.temperature)
            update_data["temperature"] = request.temperature

        if request.pricing_config is not None:
            self.validation_service.validate_pricing_config(request.pricing_config)
            update_data["pricing_config"] = request.pricing_config

        if request.is_active is not None:
            update_data["is_active"] = request.is_active

        # 设置更新元数据
        update_data["updated_by"] = user_id
        update_data["updated_at"] = datetime.datetime.utcnow()

        # 执行更新
        success = await self.model_config_repo.update(config_id, update_data)
        if not success:
            raise ConcurrentUpdateException("模型配置", config_id)

        # 返回更新后的配置
        updated_config = await self.model_config_repo.get_by_id(config_id)
        logger.info(f"Model config updated successfully: {config_id}")

        return updated_config

    async def delete_model_config(self, config_id: int) -> bool:
        """删除模型配置"""
        logger.info(f"Deleting model config: {config_id}")

        # 检查模型配置是否存在
        existing_config = await self.model_config_repo.get_by_id(config_id)
        if not existing_config:
            raise ModelConfigNotFoundException(config_id)

        # 执行软删除
        success = await self.model_config_repo.delete(config_id)
        if success:
            logger.info(f"Model config deleted successfully: {config_id}")

        return success

    async def activate_model_config(self, config_id: int) -> bool:
        """激活模型配置"""
        logger.info(f"Activating model config: {config_id}")

        # 检查模型配置是否存在
        existing_config = await self.model_config_repo.get_by_id(config_id)
        if not existing_config:
            raise ModelConfigNotFoundException(config_id)

        # 检查供应商是否激活
        provider = await self.provider_repo.get_by_id(existing_config.provider_id)
        if not provider or not provider.is_active:
            from model.domain.exceptions import ProviderInactiveException
            raise ProviderInactiveException(existing_config.provider_id)

        # 执行激活
        success = await self.model_config_repo.activate(config_id)
        if success:
            logger.info(f"Model config activated successfully: {config_id}")

        return success

    async def deactivate_model_config(self, config_id: int) -> bool:
        """停用模型配置"""
        logger.info(f"Deactivating model config: {config_id}")

        # 检查模型配置是否存在
        existing_config = await self.model_config_repo.get_by_id(config_id)
        if not existing_config:
            raise ModelConfigNotFoundException(config_id)

        # 执行停用
        success = await self.model_config_repo.deactivate(config_id)
        if success:
            logger.info(f"Model config deactivated successfully: {config_id}")

        return success


async def provider_repo(
    db: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[ProviderRepository, None]:
    yield ProviderRepository(session=db)


async def model_config_repo(
    db: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[ModelConfigRepository, None]:
    yield ModelConfigRepository(session=db)


async def provider_domain_service(
    provider_repo: IProviderRepository = Depends(provider_repo),
    model_config_repo: IModelConfigRepository = Depends(model_config_repo)
) -> AsyncGenerator[ProviderDomainService, None]:
    yield ProviderDomainService(
        provider_repo=provider_repo,
        model_config_repo=model_config_repo
    )


async def validation_service() -> AsyncGenerator[ValidationService, None]:
    yield ValidationService()


async def provider_application_service(
    provider_repo: IProviderRepository = Depends(provider_repo),
    model_config_repo: IModelConfigRepository = Depends(model_config_repo),
    provider_domain_service: ProviderDomainService = Depends(provider_domain_service),
    validation_service: ValidationService = Depends(validation_service)
) -> AsyncGenerator[ProviderApplicationService, None]:
    yield ProviderApplicationService(
        provider_repo=provider_repo,
        model_config_repo=model_config_repo,
        provider_domain_service=provider_domain_service,
        validation_service=validation_service
    )

