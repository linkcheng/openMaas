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

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from model.application.provider_service import ProviderApplicationService
from model.domain.repository.provider_repository import (
    IModelConfigRepository,
    IProviderRepository,
)
from model.domain.services.provider_service import ProviderDomainService
from model.domain.services.validation_service import ValidationService
from model.infrastructure.repositorise import ModelConfigRepository, ProviderRepository
from shared.infrastructure.database import get_db_session


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
