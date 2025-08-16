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

"""Tests for ProviderApplicationService"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from decimal import Decimal

from model.application.provider_service import ProviderApplicationService
from model.application.schemas import (
    CreateProviderRequest,
    UpdateProviderRequest,
    CreateModelConfigRequest,
    UpdateModelConfigRequest,
    ListProvidersParams,
    SearchProvidersParams,
    ListModelConfigsParams,
    PaginatedResponse
)
from model.domain.models.provider_model import ProviderEntity, ModelConfigEntity
from model.domain.exceptions import (
    ProviderNotFoundException,
    ProviderAlreadyExistsException,
    ModelConfigNotFoundException,
    ModelConfigAlreadyExistsException,
    ProviderHasActiveModelsException,
    ConcurrentUpdateException
)
from tests.unit.model.factories import create_provider_entity, create_model_config_entity


class TestProviderApplicationService:
    """Test cases for ProviderApplicationService"""
    
    @pytest.fixture
    def mock_provider_repository(self):
        """Mock provider repository"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_model_config_repository(self):
        """Mock model config repository"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_provider_domain_service(self):
        """Mock provider domain service"""
        return MagicMock()
    
    @pytest.fixture
    def mock_validation_service(self):
        """Mock validation service"""
        service = MagicMock()
        # Setup default validation methods to not raise exceptions
        service.validate_provider_name = MagicMock()
        service.validate_provider_type = MagicMock()
        service.validate_base_url = MagicMock()
        service.validate_display_name = MagicMock()
        service.validate_description = MagicMock()
        service.validate_api_key = MagicMock()
        service.validate_additional_config = MagicMock()
        service.validate_model_name = MagicMock()
        service.validate_model_display_name = MagicMock()
        service.validate_model_type = MagicMock()
        service.validate_token_limits = MagicMock()
        service.validate_temperature = MagicMock()
        service.validate_model_params = MagicMock()
        service.validate_pricing_config = MagicMock()
        return service
    
    @pytest.fixture
    def provider_service(
        self,
        mock_provider_repository,
        mock_model_config_repository,
        mock_provider_domain_service,
        mock_validation_service
    ):
        """Provider application service with mocked dependencies"""
        return ProviderApplicationService(
            provider_repo=mock_provider_repository,
            model_config_repo=mock_model_config_repository,
            provider_domain_service=mock_provider_domain_service,
            validation_service=mock_validation_service
        )
    
    @pytest.fixture
    def sample_create_provider_request(self):
        """Sample create provider request"""
        return CreateProviderRequest(
            provider_name="test_provider",
            provider_type="openai",
            display_name="Test Provider",
            description="Test provider description",
            base_url="https://api.test.com/v1",
            api_key="test-api-key",
            additional_config={"timeout": 30},
            is_active=True
        )
    
    @pytest.fixture
    def sample_provider_entity(self):
        """Sample provider entity"""
        return create_provider_entity(
            provider_id=1,
            provider_name="test_provider",
            provider_type="openai",
            display_name="Test Provider"
        )
    
    async def test_create_provider_success(
        self,
        provider_service,
        mock_provider_repository,
        mock_validation_service,
        sample_create_provider_request,
        sample_provider_entity
    ):
        """Test successful provider creation"""
        # Setup
        mock_provider_repository.get_by_name.return_value = None
        mock_provider_repository.create.return_value = sample_provider_entity
        
        # Execute
        result = await provider_service.create_provider(sample_create_provider_request, "test_user")
        
        # Verify
        mock_validation_service.validate_provider_name.assert_called_once()
        mock_validation_service.validate_provider_type.assert_called_once()
        mock_validation_service.validate_base_url.assert_called_once()
        mock_provider_repository.get_by_name.assert_called_once_with("test_provider")
        mock_provider_repository.create.assert_called_once()
        assert isinstance(result, ProviderEntity)
        assert result.provider_id == sample_provider_entity.provider_id
    
    async def test_create_provider_already_exists(
        self,
        provider_service,
        mock_provider_repository,
        sample_create_provider_request,
        sample_provider_entity
    ):
        """Test provider creation when provider already exists"""
        # Setup
        mock_provider_repository.get_by_name.return_value = sample_provider_entity
        
        # Execute & Verify
        with pytest.raises(ProviderAlreadyExistsException):
            await provider_service.create_provider(sample_create_provider_request, "test_user")
        
        mock_provider_repository.get_by_name.assert_called_once_with("test_provider")
        mock_provider_repository.create.assert_not_called()
    
    async def test_get_provider_success(
        self,
        provider_service,
        mock_provider_repository,
        sample_provider_entity
    ):
        """Test successful provider retrieval"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        
        # Execute
        result = await provider_service.get_provider(1)
        
        # Verify
        mock_provider_repository.get_by_id.assert_called_once_with(1)
        assert result == sample_provider_entity
    
    async def test_get_provider_not_found(
        self,
        provider_service,
        mock_provider_repository
    ):
        """Test provider retrieval when not found"""
        # Setup
        mock_provider_repository.get_by_id.return_value = None
        
        # Execute & Verify
        with pytest.raises(ProviderNotFoundException):
            await provider_service.get_provider(999)
        
        mock_provider_repository.get_by_id.assert_called_once_with(999)
    
    async def test_list_providers_success(
        self,
        provider_service,
        mock_provider_repository
    ):
        """Test successful provider listing"""
        # Setup
        providers = [create_provider_entity(provider_id=i) for i in range(1, 4)]
        mock_provider_repository.count_by_criteria.return_value = 3
        mock_provider_repository.find_paginated.return_value = providers
        
        params = ListProvidersParams(page=1, size=20)
        
        # Execute
        result = await provider_service.list_providers(params)
        
        # Verify
        mock_provider_repository.count_by_criteria.assert_called_once()
        mock_provider_repository.find_paginated.assert_called_once()
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 3
        assert result.total == 3
        assert result.page == 1
        assert result.size == 20
    
    async def test_search_providers_success(
        self,
        provider_service,
        mock_provider_repository
    ):
        """Test successful provider search"""
        # Setup
        providers = [create_provider_entity(provider_id=i) for i in range(1, 3)]
        mock_provider_repository.search.return_value = providers
        
        params = SearchProvidersParams(page=1, size=20, keyword="test")
        
        # Execute
        result = await provider_service.search_providers(params)
        
        # Verify
        mock_provider_repository.search.assert_called_once_with(
            keyword="test",
            provider_type=None,
            is_active=None
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2
    
    async def test_update_provider_success(
        self,
        provider_service,
        mock_provider_repository,
        mock_validation_service,
        sample_provider_entity
    ):
        """Test successful provider update"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        mock_provider_repository.get_by_name.return_value = None
        mock_provider_repository.update.return_value = True
        
        updated_entity = create_provider_entity(
            provider_id=1,
            provider_name="updated_provider",
            display_name="Updated Provider"
        )
        mock_provider_repository.get_by_id.side_effect = [sample_provider_entity, updated_entity]
        
        request = UpdateProviderRequest(
            provider_name="updated_provider",
            display_name="Updated Provider"
        )
        
        # Execute
        result = await provider_service.update_provider(1, request, "test_user")
        
        # Verify
        mock_validation_service.validate_provider_name.assert_called_once()
        mock_validation_service.validate_display_name.assert_called_once()
        mock_provider_repository.update.assert_called_once()
        assert result == updated_entity
    
    async def test_update_provider_not_found(
        self,
        provider_service,
        mock_provider_repository
    ):
        """Test provider update when provider not found"""
        # Setup
        mock_provider_repository.get_by_id.return_value = None
        
        request = UpdateProviderRequest(display_name="Updated Provider")
        
        # Execute & Verify
        with pytest.raises(ProviderNotFoundException):
            await provider_service.update_provider(999, request, "test_user")
        
        mock_provider_repository.get_by_id.assert_called_once_with(999)
        mock_provider_repository.update.assert_not_called()
    
    async def test_update_provider_name_conflict(
        self,
        provider_service,
        mock_provider_repository,
        sample_provider_entity
    ):
        """Test provider update with name conflict"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        
        conflicting_provider = create_provider_entity(provider_id=2, provider_name="existing_provider")
        mock_provider_repository.get_by_name.return_value = conflicting_provider
        
        request = UpdateProviderRequest(provider_name="existing_provider")
        
        # Execute & Verify
        with pytest.raises(ProviderAlreadyExistsException):
            await provider_service.update_provider(1, request, "test_user")
        
        mock_provider_repository.update.assert_not_called()
    
    async def test_delete_provider_success(
        self,
        provider_service,
        mock_provider_repository,
        mock_model_config_repository,
        sample_provider_entity
    ):
        """Test successful provider deletion"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        mock_model_config_repository.search.return_value = []  # No active models
        mock_provider_repository.delete.return_value = True
        
        # Execute
        result = await provider_service.delete_provider(1)
        
        # Verify
        mock_provider_repository.get_by_id.assert_called_once_with(1)
        mock_model_config_repository.search.assert_called_once()
        mock_provider_repository.delete.assert_called_once_with(1)
        assert result is True
    
    async def test_delete_provider_with_active_models(
        self,
        provider_service,
        mock_provider_repository,
        mock_model_config_repository,
        sample_provider_entity
    ):
        """Test provider deletion when has active models"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        active_models = [create_model_config_entity(config_id=i) for i in range(1, 3)]
        mock_model_config_repository.search.return_value = active_models
        
        # Execute & Verify
        with pytest.raises(ProviderHasActiveModelsException):
            await provider_service.delete_provider(1)
        
        mock_provider_repository.delete.assert_not_called()
    
    async def test_activate_provider_success(
        self,
        provider_service,
        mock_provider_repository,
        sample_provider_entity
    ):
        """Test successful provider activation"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        mock_provider_repository.activate.return_value = True
        
        # Execute
        result = await provider_service.activate_provider(1)
        
        # Verify
        mock_provider_repository.get_by_id.assert_called_once_with(1)
        mock_provider_repository.activate.assert_called_once_with(1)
        assert result is True
    
    async def test_deactivate_provider_success(
        self,
        provider_service,
        mock_provider_repository,
        sample_provider_entity
    ):
        """Test successful provider deactivation"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        mock_provider_repository.deactivate.return_value = True
        
        # Execute
        result = await provider_service.deactivate_provider(1)
        
        # Verify
        mock_provider_repository.get_by_id.assert_called_once_with(1)
        mock_provider_repository.deactivate.assert_called_once_with(1)
        assert result is True
    
    async def test_create_model_config_success(
        self,
        provider_service,
        mock_provider_repository,
        mock_model_config_repository,
        mock_validation_service,
        sample_provider_entity
    ):
        """Test successful model config creation"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        mock_model_config_repository.get_by_provider_and_name.return_value = None
        
        created_config = create_model_config_entity(config_id=1, provider_id=1)
        mock_model_config_repository.create.return_value = created_config
        
        request = CreateModelConfigRequest(
            model_name="test_model",
            model_display_name="Test Model",
            model_type="chat",
            max_tokens=4096,
            max_input_tokens=3072,
            temperature=Decimal("0.70"),
            is_active=True
        )
        
        # Execute
        result = await provider_service.create_model_config(1, request, "test_user")
        
        # Verify
        mock_provider_repository.get_by_id.assert_called_once_with(1)
        mock_validation_service.validate_model_name.assert_called_once()
        mock_validation_service.validate_model_type.assert_called_once()
        mock_model_config_repository.get_by_provider_and_name.assert_called_once()
        mock_model_config_repository.create.assert_called_once()
        assert isinstance(result, ModelConfigEntity)
        assert result.config_id == created_config.config_id
    
    async def test_create_model_config_provider_not_found(
        self,
        provider_service,
        mock_provider_repository
    ):
        """Test model config creation when provider not found"""
        # Setup
        mock_provider_repository.get_by_id.return_value = None
        
        request = CreateModelConfigRequest(
            model_name="test_model",
            model_display_name="Test Model",
            model_type="chat"
        )
        
        # Execute & Verify
        with pytest.raises(ProviderNotFoundException):
            await provider_service.create_model_config(999, request, "test_user")
        
        mock_provider_repository.get_by_id.assert_called_once_with(999)
    
    async def test_create_model_config_already_exists(
        self,
        provider_service,
        mock_provider_repository,
        mock_model_config_repository,
        sample_provider_entity
    ):
        """Test model config creation when config already exists"""
        # Setup
        mock_provider_repository.get_by_id.return_value = sample_provider_entity
        existing_config = create_model_config_entity(config_id=1, provider_id=1, model_name="test_model")
        mock_model_config_repository.get_by_provider_and_name.return_value = existing_config
        
        request = CreateModelConfigRequest(
            model_name="test_model",
            model_display_name="Test Model",
            model_type="chat"
        )
        
        # Execute & Verify
        with pytest.raises(ModelConfigAlreadyExistsException):
            await provider_service.create_model_config(1, request, "test_user")
        
        mock_model_config_repository.create.assert_not_called()
    
    async def test_get_model_config_success(
        self,
        provider_service,
        mock_model_config_repository
    ):
        """Test successful model config retrieval"""
        # Setup
        config = create_model_config_entity(config_id=1)
        mock_model_config_repository.get_by_id.return_value = config
        
        # Execute
        result = await provider_service.get_model_config(1)
        
        # Verify
        mock_model_config_repository.get_by_id.assert_called_once_with(1)
        assert result == config
    
    async def test_get_model_config_not_found(
        self,
        provider_service,
        mock_model_config_repository
    ):
        """Test model config retrieval when not found"""
        # Setup
        mock_model_config_repository.get_by_id.return_value = None
        
        # Execute & Verify
        with pytest.raises(ModelConfigNotFoundException):
            await provider_service.get_model_config(999)
        
        mock_model_config_repository.get_by_id.assert_called_once_with(999)
    
    async def test_list_model_configs_success(
        self,
        provider_service,
        mock_model_config_repository
    ):
        """Test successful model config listing"""
        # Setup
        configs = [create_model_config_entity(config_id=i) for i in range(1, 4)]
        mock_model_config_repository.count_by_criteria.return_value = 3
        mock_model_config_repository.find_paginated.return_value = configs
        
        params = ListModelConfigsParams(page=1, size=20)
        
        # Execute
        result = await provider_service.list_model_configs(params)
        
        # Verify
        mock_model_config_repository.count_by_criteria.assert_called_once()
        mock_model_config_repository.find_paginated.assert_called_once()
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 3
        assert result.total == 3
    
    async def test_list_model_configs_with_search(
        self,
        provider_service,
        mock_model_config_repository
    ):
        """Test model config listing with search keyword"""
        # Setup
        configs = [create_model_config_entity(config_id=i) for i in range(1, 3)]
        mock_model_config_repository.search.return_value = configs
        
        params = ListModelConfigsParams(page=1, size=20, keyword="test")
        
        # Execute
        result = await provider_service.list_model_configs(params)
        
        # Verify
        mock_model_config_repository.search.assert_called_once()
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2
    
    async def test_update_model_config_success(
        self,
        provider_service,
        mock_model_config_repository,
        mock_validation_service
    ):
        """Test successful model config update"""
        # Setup
        existing_config = create_model_config_entity(config_id=1, model_name="old_model")
        mock_model_config_repository.get_by_id.return_value = existing_config
        mock_model_config_repository.get_by_provider_and_name.return_value = None
        mock_model_config_repository.update.return_value = True
        
        updated_config = create_model_config_entity(config_id=1, model_name="new_model")
        mock_model_config_repository.get_by_id.side_effect = [existing_config, updated_config]
        
        request = UpdateModelConfigRequest(model_name="new_model")
        
        # Execute
        result = await provider_service.update_model_config(1, request, "test_user")
        
        # Verify
        mock_validation_service.validate_model_name.assert_called_once()
        mock_model_config_repository.update.assert_called_once()
        assert result == updated_config
    
    async def test_delete_model_config_success(
        self,
        provider_service,
        mock_model_config_repository
    ):
        """Test successful model config deletion"""
        # Setup
        config = create_model_config_entity(config_id=1)
        mock_model_config_repository.get_by_id.return_value = config
        mock_model_config_repository.delete.return_value = True
        
        # Execute
        result = await provider_service.delete_model_config(1)
        
        # Verify
        mock_model_config_repository.get_by_id.assert_called_once_with(1)
        mock_model_config_repository.delete.assert_called_once_with(1)
        assert result is True
    
    async def test_activate_model_config_success(
        self,
        provider_service,
        mock_model_config_repository,
        mock_provider_repository
    ):
        """Test successful model config activation"""
        # Setup
        config = create_model_config_entity(config_id=1, provider_id=1)
        mock_model_config_repository.get_by_id.return_value = config
        
        provider = create_provider_entity(provider_id=1, is_active=True)
        mock_provider_repository.get_by_id.return_value = provider
        
        mock_model_config_repository.activate.return_value = True
        
        # Execute
        result = await provider_service.activate_model_config(1)
        
        # Verify
        mock_model_config_repository.get_by_id.assert_called_once_with(1)
        mock_provider_repository.get_by_id.assert_called_once_with(1)
        mock_model_config_repository.activate.assert_called_once_with(1)
        assert result is True
    
    async def test_deactivate_model_config_success(
        self,
        provider_service,
        mock_model_config_repository
    ):
        """Test successful model config deactivation"""
        # Setup
        config = create_model_config_entity(config_id=1)
        mock_model_config_repository.get_by_id.return_value = config
        mock_model_config_repository.deactivate.return_value = True
        
        # Execute
        result = await provider_service.deactivate_model_config(1)
        
        # Verify
        mock_model_config_repository.get_by_id.assert_called_once_with(1)
        mock_model_config_repository.deactivate.assert_called_once_with(1)
        assert result is True