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

"""Tests for ProviderController"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from decimal import Decimal
from fastapi import HTTPException
from fastapi.testclient import TestClient

from model.interface.provider_controller import router
from model.application.schemas import (
    CreateProviderRequest,
    UpdateProviderRequest,
    CreateModelConfigRequest,
    UpdateModelConfigRequest,
    PaginatedResponse
)
from model.domain.models.provider_model import ProviderEntity, ModelConfigEntity
from model.domain.exceptions import (
    ProviderNotFoundException,
    ProviderAlreadyExistsException,
    ModelConfigNotFoundException,
    ModelConfigAlreadyExistsException,
    ProviderHasActiveModelsException
)
from tests.unit.model.factories import create_provider_entity, create_model_config_entity


# Mock FastAPI app for testing
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestProviderController:
    """Test cases for ProviderController"""
    
    @pytest.fixture
    def mock_provider_service(self):
        """Mock provider application service"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_user_id(self):
        """Mock user ID"""
        return str(uuid4())
    
    @pytest.fixture
    def sample_provider_entity(self):
        """Sample provider entity"""
        return create_provider_entity(
            provider_id=1,
            provider_name="test_provider",
            provider_type="openai",
            display_name="Test Provider"
        )
    
    @pytest.fixture
    def sample_model_config_entity(self):
        """Sample model config entity"""
        return create_model_config_entity(
            config_id=1,
            provider_id=1,
            model_name="test_model",
            model_display_name="Test Model"
        )
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.get_current_user_id')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_create_provider_success(
        self,
        mock_require_super_admin,
        mock_get_current_user_id,
        mock_provider_service_dep,
        mock_provider_service,
        mock_user_id,
        sample_provider_entity
    ):
        """Test successful provider creation"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_get_current_user_id.return_value = mock_user_id
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.create_provider.return_value = sample_provider_entity
        
        # Test data
        request_data = {
            "provider_name": "test_provider",
            "provider_type": "openai",
            "display_name": "Test Provider",
            "base_url": "https://api.test.com/v1",
            "is_active": True
        }
        
        # Execute
        response = client.post("/models/providers", json=request_data)
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "供应商 'test_provider' 创建成功"
        assert data["data"]["provider_id"] == 1
        assert data["data"]["provider_name"] == "test_provider"
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.get_current_user_id')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_create_provider_already_exists(
        self,
        mock_require_super_admin,
        mock_get_current_user_id,
        mock_provider_service_dep,
        mock_provider_service,
        mock_user_id
    ):
        """Test provider creation when provider already exists"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_get_current_user_id.return_value = mock_user_id
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.create_provider.side_effect = ProviderAlreadyExistsException("test_provider")
        
        # Test data
        request_data = {
            "provider_name": "test_provider",
            "provider_type": "openai",
            "display_name": "Test Provider",
            "base_url": "https://api.test.com/v1"
        }
        
        # Execute
        response = client.post("/models/providers", json=request_data)
        
        # Verify
        assert response.status_code == 422
        data = response.json()
        assert "已存在" in data["detail"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_list_providers_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful provider listing"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        
        providers = [create_provider_entity(provider_id=i) for i in range(1, 4)]
        paginated_result = PaginatedResponse.create(
            items=providers,
            total=3,
            page=1,
            size=20
        )
        mock_provider_service.list_providers.return_value = paginated_result
        
        # Execute
        response = client.get("/models/providers?page=1&size=20")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "查询供应商列表成功"
        assert len(data["data"]["items"]) == 3
        assert data["data"]["total"] == 3
        assert data["data"]["page"] == 1
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_get_provider_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service,
        sample_provider_entity
    ):
        """Test successful provider retrieval"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.get_provider.return_value = sample_provider_entity
        
        # Execute
        response = client.get("/models/providers/1")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "获取供应商信息成功"
        assert data["data"]["provider_id"] == 1
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_get_provider_not_found(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test provider retrieval when not found"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.get_provider.side_effect = ProviderNotFoundException(999)
        
        # Execute
        response = client.get("/models/providers/999")
        
        # Verify
        assert response.status_code == 404
        data = response.json()
        assert "不存在" in data["detail"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.get_current_user_id')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_update_provider_success(
        self,
        mock_require_super_admin,
        mock_get_current_user_id,
        mock_provider_service_dep,
        mock_provider_service,
        mock_user_id,
        sample_provider_entity
    ):
        """Test successful provider update"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_get_current_user_id.return_value = mock_user_id
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.update_provider.return_value = sample_provider_entity
        
        # Test data
        request_data = {
            "display_name": "Updated Provider"
        }
        
        # Execute
        response = client.put("/models/providers/1", json=request_data)
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "更新成功" in data["message"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_delete_provider_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful provider deletion"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.delete_provider.return_value = True
        
        # Execute
        response = client.delete("/models/providers/1")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_delete_provider_with_active_models(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test provider deletion when has active models"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.delete_provider.side_effect = ProviderHasActiveModelsException(1, 2)
        
        # Execute
        response = client.delete("/models/providers/1")
        
        # Verify
        assert response.status_code == 422
        data = response.json()
        assert "活跃的模型配置" in data["detail"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_activate_provider_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful provider activation"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.activate_provider.return_value = True
        
        # Execute
        response = client.post("/models/providers/1/activate")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "激活成功" in data["message"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_deactivate_provider_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful provider deactivation"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.deactivate_provider.return_value = True
        
        # Execute
        response = client.post("/models/providers/1/deactivate")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "停用成功" in data["message"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_search_providers_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful provider search"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        
        providers = [create_provider_entity(provider_id=i) for i in range(1, 3)]
        paginated_result = PaginatedResponse.create(
            items=providers,
            total=2,
            page=1,
            size=20
        )
        mock_provider_service.search_providers.return_value = paginated_result
        
        # Execute
        response = client.get("/models/providers/search?keyword=test&page=1&size=20")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "搜索供应商成功"
        assert len(data["data"]["items"]) == 2
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.get_current_user_id')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_create_model_config_success(
        self,
        mock_require_super_admin,
        mock_get_current_user_id,
        mock_provider_service_dep,
        mock_provider_service,
        mock_user_id,
        sample_model_config_entity
    ):
        """Test successful model config creation"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_get_current_user_id.return_value = mock_user_id
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.create_model_config.return_value = sample_model_config_entity
        
        # Test data
        request_data = {
            "model_name": "test_model",
            "model_display_name": "Test Model",
            "model_type": "chat",
            "max_tokens": 4096,
            "max_input_tokens": 3072,
            "temperature": 0.7,
            "is_active": True
        }
        
        # Execute
        response = client.post("/models/providers/1/models", json=request_data)
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "模型配置 'test_model' 创建成功"
        assert data["data"]["config_id"] == 1
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.get_current_user_id')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_create_model_config_provider_not_found(
        self,
        mock_require_super_admin,
        mock_get_current_user_id,
        mock_provider_service_dep,
        mock_provider_service,
        mock_user_id
    ):
        """Test model config creation when provider not found"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_get_current_user_id.return_value = mock_user_id
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.create_model_config.side_effect = ProviderNotFoundException(999)
        
        # Test data
        request_data = {
            "model_name": "test_model",
            "model_display_name": "Test Model",
            "model_type": "chat"
        }
        
        # Execute
        response = client.post("/models/providers/999/models", json=request_data)
        
        # Verify
        assert response.status_code == 404
        data = response.json()
        assert "不存在" in data["detail"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_list_model_configs_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful model config listing"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        
        configs = [create_model_config_entity(config_id=i) for i in range(1, 4)]
        paginated_result = PaginatedResponse.create(
            items=configs,
            total=3,
            page=1,
            size=20
        )
        mock_provider_service.list_model_configs.return_value = paginated_result
        
        # Execute
        response = client.get("/models/models?page=1&size=20")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "查询模型配置列表成功"
        assert len(data["data"]["items"]) == 3
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_get_model_config_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service,
        sample_model_config_entity
    ):
        """Test successful model config retrieval"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.get_model_config.return_value = sample_model_config_entity
        
        # Execute
        response = client.get("/models/models/1")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "获取模型配置信息成功"
        assert data["data"]["config_id"] == 1
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_get_model_config_not_found(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test model config retrieval when not found"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.get_model_config.side_effect = ModelConfigNotFoundException(999)
        
        # Execute
        response = client.get("/models/models/999")
        
        # Verify
        assert response.status_code == 404
        data = response.json()
        assert "不存在" in data["detail"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.get_current_user_id')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_update_model_config_success(
        self,
        mock_require_super_admin,
        mock_get_current_user_id,
        mock_provider_service_dep,
        mock_provider_service,
        mock_user_id,
        sample_model_config_entity
    ):
        """Test successful model config update"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_get_current_user_id.return_value = mock_user_id
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.update_model_config.return_value = sample_model_config_entity
        
        # Test data
        request_data = {
            "model_display_name": "Updated Model"
        }
        
        # Execute
        response = client.put("/models/models/1", json=request_data)
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "更新成功" in data["message"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_delete_model_config_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful model config deletion"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.delete_model_config.return_value = True
        
        # Execute
        response = client.delete("/models/models/1")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_activate_model_config_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful model config activation"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.activate_model_config.return_value = True
        
        # Execute
        response = client.post("/models/models/1/activate")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "激活成功" in data["message"]
    
    @patch('model.interface.provider_controller.provider_application_service')
    @patch('model.interface.provider_controller.require_super_admin')
    async def test_deactivate_model_config_success(
        self,
        mock_require_super_admin,
        mock_provider_service_dep,
        mock_provider_service
    ):
        """Test successful model config deactivation"""
        # Setup mocks
        mock_require_super_admin.return_value = None
        mock_provider_service_dep.return_value = mock_provider_service
        mock_provider_service.deactivate_model_config.return_value = True
        
        # Execute
        response = client.post("/models/models/1/deactivate")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "停用成功" in data["message"]
    
    def test_invalid_request_validation(self):
        """Test request validation for invalid data"""
        # Test missing required fields
        response = client.post("/models/providers", json={})
        assert response.status_code == 422
        
        # Test invalid field values
        response = client.post("/models/providers", json={
            "provider_name": "",  # empty name
            "provider_type": "test",
            "display_name": "Test",
            "base_url": "invalid-url"  # invalid URL
        })
        assert response.status_code == 422
    
    def test_query_parameter_validation(self):
        """Test query parameter validation"""
        # Test invalid page number
        response = client.get("/models/providers?page=0")
        assert response.status_code == 422
        
        # Test invalid size
        response = client.get("/models/providers?size=101")
        assert response.status_code == 422
        
        # Test invalid sort order
        response = client.get("/models/providers?sort_order=invalid")
        assert response.status_code == 422