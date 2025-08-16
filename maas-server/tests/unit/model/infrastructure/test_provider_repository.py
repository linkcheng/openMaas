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

"""Tests for ProviderRepository"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from decimal import Decimal

from model.infrastructure.repositorise import ProviderRepository
from model.infrastructure.models import ProviderORM
from model.domain.models.provider_model import ProviderEntity
from tests.unit.model.factories import create_provider_entity, create_provider_orm


class TestProviderRepository:
    """Test cases for ProviderRepository"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session
    
    @pytest.fixture
    def provider_repository(self, mock_session):
        """Provider repository with mocked session"""
        return ProviderRepository(mock_session)
    
    @pytest.fixture
    def sample_provider_entity(self):
        """Sample provider entity"""
        return create_provider_entity(
            provider_id=1,
            provider_name="test_provider",
            provider_type="openai",
            display_name="Test Provider",
            description="Test provider description",
            base_url="https://api.test.com/v1",
            api_key="test-api-key",
            is_active=True,
            created_by="test_user",
            updated_by="test_user"
        )
    
    @pytest.fixture
    def sample_provider_orm(self):
        """Sample provider ORM"""
        return create_provider_orm(
            provider_id=1,
            provider_name="test_provider",
            provider_type="openai",
            display_name="Test Provider",
            description="Test provider description",
            base_url="https://api.test.com/v1",
            api_key="test-api-key",
            is_active=True,
            created_by="test_user",
            updated_by="test_user"
        )
    
    def test_to_entity_conversion(self, provider_repository, sample_provider_orm):
        """Test ORM to entity conversion"""
        entity = provider_repository._to_entity(sample_provider_orm)
        
        assert entity is not None
        assert isinstance(entity, ProviderEntity)
        assert entity.provider_id == sample_provider_orm.provider_id
        assert entity.provider_name == sample_provider_orm.provider_name
        assert entity.provider_type == sample_provider_orm.provider_type
        assert entity.display_name == sample_provider_orm.display_name
        assert entity.description == sample_provider_orm.description
        assert entity.base_url == sample_provider_orm.base_url
        assert entity.api_key == sample_provider_orm.api_key
        assert entity.is_active == sample_provider_orm.is_active
        assert entity.created_by == sample_provider_orm.created_by
        assert entity.updated_by == sample_provider_orm.updated_by
    
    def test_to_entity_with_none(self, provider_repository):
        """Test ORM to entity conversion with None input"""
        entity = provider_repository._to_entity(None)
        assert entity is None
    
    def test_to_model_conversion(self, provider_repository, sample_provider_entity):
        """Test entity to ORM conversion"""
        orm = provider_repository._to_model(sample_provider_entity)
        
        assert orm is not None
        assert isinstance(orm, ProviderORM)
        assert orm.provider_id == sample_provider_entity.provider_id
        assert orm.provider_name == sample_provider_entity.provider_name
        assert orm.provider_type == sample_provider_entity.provider_type
        assert orm.display_name == sample_provider_entity.display_name
        assert orm.description == sample_provider_entity.description
        assert orm.base_url == sample_provider_entity.base_url
        assert orm.api_key == sample_provider_entity.api_key
        assert orm.is_active == sample_provider_entity.is_active
        assert orm.created_by == sample_provider_entity.created_by
        assert orm.updated_by == sample_provider_entity.updated_by
    
    def test_to_model_with_none(self, provider_repository):
        """Test entity to ORM conversion with None input"""
        orm = provider_repository._to_model(None)
        assert orm is None
    
    async def test_create_provider(self, provider_repository, mock_session, sample_provider_entity):
        """Test creating a provider"""
        # Setup
        created_orm = create_provider_orm(**sample_provider_entity.__dict__)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Execute
        result = await provider_repository.create(sample_provider_entity)
        
        # Verify
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert isinstance(result, ProviderEntity)
    
    async def test_get_by_id_found(self, provider_repository, mock_session, sample_provider_orm):
        """Test getting provider by ID when found"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_provider_orm
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.get_by_id(1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert isinstance(result, ProviderEntity)
        assert result.provider_id == sample_provider_orm.provider_id
    
    async def test_get_by_id_not_found(self, provider_repository, mock_session):
        """Test getting provider by ID when not found"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.get_by_id(999)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is None
    
    async def test_get_by_name_found(self, provider_repository, mock_session, sample_provider_orm):
        """Test getting provider by name when found"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_provider_orm
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.get_by_name("test_provider")
        
        # Verify
        mock_session.execute.assert_called_once()
        assert isinstance(result, ProviderEntity)
        assert result.provider_name == sample_provider_orm.provider_name
    
    async def test_get_by_name_not_found(self, provider_repository, mock_session):
        """Test getting provider by name when not found"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.get_by_name("nonexistent")
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is None
    
    async def test_get_all_providers(self, provider_repository, mock_session):
        """Test getting all providers"""
        # Setup
        providers = [create_provider_orm(provider_id=i) for i in range(1, 4)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = providers
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.get_all()
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 3
        assert all(isinstance(p, ProviderEntity) for p in result)
    
    async def test_get_by_type(self, provider_repository, mock_session):
        """Test getting providers by type"""
        # Setup
        providers = [create_provider_orm(provider_id=i, provider_type="openai") for i in range(1, 3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = providers
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.get_by_type("openai")
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert all(p.provider_type == "openai" for p in result)
    
    async def test_get_active_providers(self, provider_repository, mock_session):
        """Test getting active providers"""
        # Setup
        providers = [create_provider_orm(provider_id=i, is_active=True) for i in range(1, 3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = providers
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.get_active_providers()
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert all(p.is_active for p in result)
    
    async def test_update_provider(self, provider_repository, mock_session):
        """Test updating provider"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        update_data = {"display_name": "Updated Provider"}
        
        # Execute
        result = await provider_repository.update(1, update_data)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is True
    
    async def test_update_provider_not_found(self, provider_repository, mock_session):
        """Test updating non-existent provider"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        
        update_data = {"display_name": "Updated Provider"}
        
        # Execute
        result = await provider_repository.update(999, update_data)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is False
    
    async def test_delete_provider(self, provider_repository, mock_session):
        """Test soft deleting provider"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.delete(1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is True
    
    async def test_activate_provider(self, provider_repository, mock_session):
        """Test activating provider"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.activate(1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is True
    
    async def test_deactivate_provider(self, provider_repository, mock_session):
        """Test deactivating provider"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.deactivate(1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is True
    
    async def test_search_providers(self, provider_repository, mock_session):
        """Test searching providers"""
        # Setup
        providers = [create_provider_orm(provider_id=i) for i in range(1, 3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = providers
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await provider_repository.search("test", provider_type="openai", is_active=True)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert all(isinstance(p, ProviderEntity) for p in result)
    
    async def test_find_paginated(self, provider_repository, mock_session):
        """Test paginated provider search"""
        # Setup
        providers = [create_provider_orm(provider_id=i) for i in range(1, 3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = providers
        mock_session.execute.return_value = mock_result
        
        conditions = {"is_active": True, "is_delete": False}
        
        # Execute
        result = await provider_repository.find_paginated(conditions, 0, 10)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert all(isinstance(p, ProviderEntity) for p in result)
    
    async def test_count_by_criteria(self, provider_repository, mock_session):
        """Test counting providers by criteria"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result
        
        conditions = {"is_active": True, "is_delete": False}
        
        # Execute
        result = await provider_repository.count_by_criteria(conditions)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result == 5
    
    async def test_count_by_criteria_none_result(self, provider_repository, mock_session):
        """Test counting providers when result is None"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result
        
        conditions = {"is_active": True}
        
        # Execute
        result = await provider_repository.count_by_criteria(conditions)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result == 0