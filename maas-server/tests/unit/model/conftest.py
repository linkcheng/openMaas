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

"""Test configuration for model module"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator

from model.domain.repository.provider_repository import IProviderRepository, IModelConfigRepository
from model.application.provider_service import ProviderApplicationService
from model.domain.services.provider_service import ProviderDomainService
from model.domain.services.model_config_service import ModelConfigDomainService
from tests.unit.model.factories import (
    create_provider_entity,
    create_model_config_entity,
    create_test_provider_data,
    create_test_model_config_data
)


@pytest.fixture
def mock_provider_repository():
    """Mock provider repository"""
    repository = AsyncMock(spec=IProviderRepository)
    return repository


@pytest.fixture
def mock_model_config_repository():
    """Mock model config repository"""
    repository = AsyncMock(spec=IModelConfigRepository)
    return repository


@pytest.fixture
def mock_provider_domain_service():
    """Mock provider domain service"""
    service = MagicMock(spec=ProviderDomainService)
    return service


@pytest.fixture
def mock_model_config_domain_service():
    """Mock model config domain service"""
    service = MagicMock(spec=ModelConfigDomainService)
    return service


@pytest.fixture
def provider_application_service(
    mock_provider_repository,
    mock_model_config_repository,
    mock_provider_domain_service,
    mock_model_config_domain_service
):
    """Provider application service with mocked dependencies"""
    return ProviderApplicationService(
        provider_repository=mock_provider_repository,
        model_config_repository=mock_model_config_repository,
        provider_domain_service=mock_provider_domain_service,
        model_config_domain_service=mock_model_config_domain_service
    )


@pytest.fixture
def sample_provider_entity():
    """Sample provider entity for testing"""
    return create_provider_entity(
        provider_id=1,
        provider_name="test_provider",
        provider_type="openai",
        display_name="Test Provider"
    )


@pytest.fixture
def sample_model_config_entity():
    """Sample model config entity for testing"""
    return create_model_config_entity(
        config_id=1,
        provider_id=1,
        model_name="test_model",
        model_display_name="Test Model"
    )


@pytest.fixture
def sample_provider_data():
    """Sample provider data for testing"""
    return create_test_provider_data()


@pytest.fixture
def sample_model_config_data():
    """Sample model config data for testing"""
    return create_test_model_config_data()


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_crypto_service():
    """Mock crypto service for API key encryption/decryption"""
    service = MagicMock()
    service.encrypt = MagicMock(return_value="encrypted_key")
    service.decrypt = MagicMock(return_value="decrypted_key")
    return service


@pytest.fixture
async def test_data_cleanup():
    """Fixture to ensure test data cleanup"""
    # Setup
    yield
    # Cleanup - this would be used for integration tests with real database
    pass


# Test data builders
@pytest.fixture
def provider_builder():
    """Builder for creating provider test data"""
    class ProviderBuilder:
        def __init__(self):
            self.data = create_test_provider_data()
        
        def with_name(self, name: str):
            self.data["provider_name"] = name
            return self
        
        def with_type(self, provider_type: str):
            self.data["provider_type"] = provider_type
            return self
        
        def with_display_name(self, display_name: str):
            self.data["display_name"] = display_name
            return self
        
        def inactive(self):
            self.data["is_active"] = False
            return self
        
        def deleted(self):
            self.data["is_delete"] = True
            return self
        
        def build(self):
            return self.data.copy()
        
        def build_entity(self):
            return create_provider_entity(**self.data)
    
    return ProviderBuilder


@pytest.fixture
def model_config_builder():
    """Builder for creating model config test data"""
    class ModelConfigBuilder:
        def __init__(self):
            self.data = create_test_model_config_data()
        
        def with_provider_id(self, provider_id: int):
            self.data["provider_id"] = provider_id
            return self
        
        def with_name(self, name: str):
            self.data["model_name"] = name
            return self
        
        def with_type(self, model_type: str):
            self.data["model_type"] = model_type
            return self
        
        def with_max_tokens(self, max_tokens: int):
            self.data["max_tokens"] = max_tokens
            return self
        
        def inactive(self):
            self.data["is_active"] = False
            return self
        
        def deleted(self):
            self.data["is_delete"] = True
            return self
        
        def build(self):
            return self.data.copy()
        
        def build_entity(self):
            return create_model_config_entity(**self.data)
    
    return ModelConfigBuilder