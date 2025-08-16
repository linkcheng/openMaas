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

"""Tests for ModelConfigRepository"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from decimal import Decimal

from model.infrastructure.repositorise import ModelConfigRepository
from model.infrastructure.models import ModelConfigORM
from model.domain.models.provider_model import ModelConfigEntity
from tests.unit.model.factories import create_model_config_entity, create_model_config_orm


class TestModelConfigRepository:
    """Test cases for ModelConfigRepository"""
    
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
    def model_config_repository(self, mock_session):
        """Model config repository with mocked session"""
        return ModelConfigRepository(mock_session)
    
    @pytest.fixture
    def sample_model_config_entity(self):
        """Sample model config entity"""
        return create_model_config_entity(
            config_id=1,
            provider_id=1,
            model_name="test_model",
            model_display_name="Test Model",
            model_type="chat",
            max_tokens=4096,
            max_input_tokens=3072,
            temperature=Decimal("0.70"),
            is_active=True,
            created_by="test_user",
            updated_by="test_user"
        )
    
    @pytest.fixture
    def sample_model_config_orm(self):
        """Sample model config ORM"""
        return create_model_config_orm(
            config_id=1,
            provider_id=1,
            model_name="test_model",
            model_display_name="Test Model",
            model_type="chat",
            max_tokens=4096,
            max_input_tokens=3072,
            temperature=Decimal("0.70"),
            is_active=True,
            created_by="test_user",
            updated_by="test_user"
        )
    
    def test_to_entity_conversion(self, model_config_repository, sample_model_config_orm):
        """Test ORM to entity conversion"""
        entity = model_config_repository._to_entity(sample_model_config_orm)
        
        assert entity is not None
        assert isinstance(entity, ModelConfigEntity)
        assert entity.config_id == sample_model_config_orm.config_id
        assert entity.provider_id == sample_model_config_orm.provider_id
        assert entity.model_name == sample_model_config_orm.model_name
        assert entity.model_display_name == sample_model_config_orm.model_display_name
        assert entity.model_type == sample_model_config_orm.model_type
        assert entity.max_tokens == sample_model_config_orm.max_tokens
        assert entity.max_input_tokens == sample_model_config_orm.max_input_tokens
        assert entity.temperature == sample_model_config_orm.temperature
        assert entity.is_active == sample_model_config_orm.is_active
        assert entity.created_by == sample_model_config_orm.created_by
        assert entity.updated_by == sample_model_config_orm.updated_by
    
    def test_to_entity_with_none(self, model_config_repository):
        """Test ORM to entity conversion with None input"""
        entity = model_config_repository._to_entity(None)
        assert entity is None
    
    def test_to_model_conversion(self, model_config_repository, sample_model_config_entity):
        """Test entity to ORM conversion"""
        orm = model_config_repository._to_model(sample_model_config_entity)
        
        assert orm is not None
        assert isinstance(orm, ModelConfigORM)
        assert orm.config_id == sample_model_config_entity.config_id
        assert orm.provider_id == sample_model_config_entity.provider_id
        assert orm.model_name == sample_model_config_entity.model_name
        assert orm.model_display_name == sample_model_config_entity.model_display_name
        assert orm.model_type == sample_model_config_entity.model_type
        assert orm.max_tokens == sample_model_config_entity.max_tokens
        assert orm.max_input_tokens == sample_model_config_entity.max_input_tokens
        assert orm.temperature == sample_model_config_entity.temperature
        assert orm.is_active == sample_model_config_entity.is_active
        assert orm.created_by == sample_model_config_entity.created_by
        assert orm.updated_by == sample_model_config_entity.updated_by
    
    def test_to_model_with_none(self, model_config_repository):
        """Test entity to ORM conversion with None input"""
        orm = model_config_repository._to_model(None)
        assert orm is None
    
    async def test_create_model_config(self, model_config_repository, mock_session, sample_model_config_entity):
        """Test creating a model config"""
        # Setup
        created_orm = create_model_config_orm(**sample_model_config_entity.__dict__)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Execute
        result = await model_config_repository.create(sample_model_config_entity)
        
        # Verify
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert isinstance(result, ModelConfigEntity)
    
    async def test_get_by_id_found(self, model_config_repository, mock_session, sample_model_config_orm):
        """Test getting model config by ID when found"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_model_config_orm
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.get_by_id(1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert isinstance(result, ModelConfigEntity)
        assert result.config_id == sample_model_config_orm.config_id
    
    async def test_get_by_id_not_found(self, model_config_repository, mock_session):
        """Test getting model config by ID when not found"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.get_by_id(999)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is None
    
    async def test_update_model_config(self, model_config_repository, mock_session):
        """Test updating model config"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        update_data = {"model_display_name": "Updated Model"}
        
        # Execute
        result = await model_config_repository.update(1, update_data)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is True
    
    async def test_update_model_config_not_found(self, model_config_repository, mock_session):
        """Test updating non-existent model config"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        
        update_data = {"model_display_name": "Updated Model"}
        
        # Execute
        result = await model_config_repository.update(999, update_data)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is False
    
    async def test_delete_model_config(self, model_config_repository, mock_session):
        """Test soft deleting model config"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.delete(1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is True
    
    async def test_activate_model_config(self, model_config_repository, mock_session):
        """Test activating model config"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.activate(1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is True
    
    async def test_deactivate_model_config(self, model_config_repository, mock_session):
        """Test deactivating model config"""
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.deactivate(1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is True
    
    async def test_search_model_configs(self, model_config_repository, mock_session):
        """Test searching model configs"""
        # Setup
        configs = [create_model_config_orm(config_id=i) for i in range(1, 3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = configs
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.search("test", provider_id=1, model_type="chat", is_active=True)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert all(isinstance(c, ModelConfigEntity) for c in result)
    
    async def test_find_paginated(self, model_config_repository, mock_session):
        """Test paginated model config search"""
        # Setup
        configs = [create_model_config_orm(config_id=i) for i in range(1, 3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = configs
        mock_session.execute.return_value = mock_result
        
        conditions = {"is_active": True, "is_delete": False}
        
        # Execute
        result = await model_config_repository.find_paginated(conditions, 0, 10)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert all(isinstance(c, ModelConfigEntity) for c in result)
    
    async def test_count_by_criteria(self, model_config_repository, mock_session):
        """Test counting model configs by criteria"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar.return_value = 3
        mock_session.execute.return_value = mock_result
        
        conditions = {"is_active": True, "is_delete": False}
        
        # Execute
        result = await model_config_repository.count_by_criteria(conditions)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result == 3
    
    async def test_count_by_criteria_none_result(self, model_config_repository, mock_session):
        """Test counting model configs when result is None"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result
        
        conditions = {"is_active": True}
        
        # Execute
        result = await model_config_repository.count_by_criteria(conditions)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result == 0
    
    async def test_get_by_provider_and_name_found(self, model_config_repository, mock_session, sample_model_config_orm):
        """Test getting model config by provider and name when found"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_model_config_orm
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.get_by_provider_and_name(1, "test_model")
        
        # Verify
        mock_session.execute.assert_called_once()
        assert isinstance(result, ModelConfigEntity)
        assert result.provider_id == 1
        assert result.model_name == "test_model"
    
    async def test_get_by_provider_and_name_not_found(self, model_config_repository, mock_session):
        """Test getting model config by provider and name when not found"""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.get_by_provider_and_name(1, "nonexistent")
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is None
    
    async def test_search_with_keyword_only(self, model_config_repository, mock_session):
        """Test searching model configs with keyword only"""
        # Setup
        configs = [create_model_config_orm(config_id=i) for i in range(1, 2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = configs
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.search("test")
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 1
        assert all(isinstance(c, ModelConfigEntity) for c in result)
    
    async def test_search_with_provider_filter(self, model_config_repository, mock_session):
        """Test searching model configs with provider filter"""
        # Setup
        configs = [create_model_config_orm(config_id=i, provider_id=1) for i in range(1, 2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = configs
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.search("", provider_id=1)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 1
        assert all(c.provider_id == 1 for c in result)
    
    async def test_search_with_model_type_filter(self, model_config_repository, mock_session):
        """Test searching model configs with model type filter"""
        # Setup
        configs = [create_model_config_orm(config_id=i, model_type="chat") for i in range(1, 2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = configs
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.search("", model_type="chat")
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 1
        assert all(c.model_type == "chat" for c in result)
    
    async def test_search_with_active_filter(self, model_config_repository, mock_session):
        """Test searching model configs with active filter"""
        # Setup
        configs = [create_model_config_orm(config_id=i, is_active=True) for i in range(1, 2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = configs
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await model_config_repository.search("", is_active=True)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert len(result) == 1
        assert all(c.is_active for c in result)