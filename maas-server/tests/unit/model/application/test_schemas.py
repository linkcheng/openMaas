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

"""Tests for application schemas"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from pydantic import ValidationError

from model.application.schemas import (
    CreateProviderRequest,
    UpdateProviderRequest,
    ProviderResponse,
    ListProvidersParams,
    SearchProvidersParams,
    PaginatedProviderResponse,
    CreateModelConfigRequest,
    UpdateModelConfigRequest,
    ModelConfigResponse,
    ListModelConfigsParams,
    PaginatedModelConfigResponse,
    PaginatedResponse,
    MessageResponse,
    PaginationMeta,
    BaseListParams
)


class TestCreateProviderRequest:
    """Test cases for CreateProviderRequest"""
    
    def test_valid_request(self):
        """Test valid provider creation request"""
        request = CreateProviderRequest(
            provider_name="openai",
            provider_type="openai",
            display_name="OpenAI",
            description="OpenAI GPT models",
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
            additional_config={"organization": "org-test"},
            is_active=True
        )
        
        assert request.provider_name == "openai"
        assert request.provider_type == "openai"
        assert request.display_name == "OpenAI"
        assert request.description == "OpenAI GPT models"
        assert request.base_url == "https://api.openai.com/v1"
        assert request.api_key == "sk-test"
        assert request.additional_config == {"organization": "org-test"}
        assert request.is_active is True
    
    def test_minimal_request(self):
        """Test minimal valid request"""
        request = CreateProviderRequest(
            provider_name="test",
            provider_type="test",
            display_name="Test",
            base_url="https://api.test.com"
        )
        
        assert request.provider_name == "test"
        assert request.description is None
        assert request.api_key is None
        assert request.additional_config is None
        assert request.is_active is True  # default value
    
    def test_empty_provider_name(self):
        """Test validation error for empty provider name"""
        with pytest.raises(ValidationError) as exc_info:
            CreateProviderRequest(
                provider_name="",
                provider_type="test",
                display_name="Test",
                base_url="https://api.test.com"
            )
        
        errors = exc_info.value.errors()
        assert any("供应商名称不能为空" in str(error) for error in errors)
    
    def test_whitespace_provider_name(self):
        """Test validation strips whitespace from provider name"""
        request = CreateProviderRequest(
            provider_name="  test  ",
            provider_type="test",
            display_name="Test",
            base_url="https://api.test.com"
        )
        
        assert request.provider_name == "test"
    
    def test_invalid_base_url(self):
        """Test validation error for invalid base URL"""
        with pytest.raises(ValidationError) as exc_info:
            CreateProviderRequest(
                provider_name="test",
                provider_type="test",
                display_name="Test",
                base_url="invalid-url"
            )
        
        errors = exc_info.value.errors()
        assert any("基础URL必须以http://或https://开头" in str(error) for error in errors)
    
    def test_field_length_limits(self):
        """Test field length validation"""
        # Test provider_name max length
        with pytest.raises(ValidationError):
            CreateProviderRequest(
                provider_name="a" * 65,  # exceeds 64 char limit
                provider_type="test",
                display_name="Test",
                base_url="https://api.test.com"
            )
        
        # Test description max length
        with pytest.raises(ValidationError):
            CreateProviderRequest(
                provider_name="test",
                provider_type="test",
                display_name="Test",
                description="a" * 1001,  # exceeds 1000 char limit
                base_url="https://api.test.com"
            )


class TestUpdateProviderRequest:
    """Test cases for UpdateProviderRequest"""
    
    def test_valid_partial_update(self):
        """Test valid partial update request"""
        request = UpdateProviderRequest(
            display_name="Updated Name",
            description="Updated description"
        )
        
        assert request.display_name == "Updated Name"
        assert request.description == "Updated description"
        assert request.provider_name is None
        assert request.is_active is None
    
    def test_empty_update(self):
        """Test empty update request"""
        request = UpdateProviderRequest()
        
        assert request.provider_name is None
        assert request.display_name is None
        assert request.description is None
        assert request.is_active is None
    
    def test_whitespace_handling(self):
        """Test whitespace handling in update request"""
        request = UpdateProviderRequest(
            provider_name="  updated  "
        )
        
        assert request.provider_name == "updated"


class TestProviderResponse:
    """Test cases for ProviderResponse"""
    
    def test_valid_response(self):
        """Test valid provider response"""
        now = datetime.now(timezone.utc)
        response = ProviderResponse(
            provider_id=1,
            provider_name="openai",
            provider_type="openai",
            display_name="OpenAI",
            description="OpenAI GPT models",
            base_url="https://api.openai.com/v1",
            additional_config={"org": "test"},
            is_active=True,
            created_by="admin",
            created_at=now,
            updated_by="admin",
            updated_at=now
        )
        
        assert response.provider_id == 1
        assert response.provider_name == "openai"
        assert response.is_active is True
        assert response.created_at == now


class TestListProvidersParams:
    """Test cases for ListProvidersParams"""
    
    def test_default_values(self):
        """Test default parameter values"""
        params = ListProvidersParams()
        
        assert params.page == 1
        assert params.size == 20
        assert params.provider_type is None
        assert params.is_active is None
        assert params.sort_by == "created_at"
        assert params.sort_order == "desc"
    
    def test_custom_values(self):
        """Test custom parameter values"""
        params = ListProvidersParams(
            page=2,
            size=50,
            provider_type="openai",
            is_active=True,
            sort_by="display_name",
            sort_order="asc"
        )
        
        assert params.page == 2
        assert params.size == 50
        assert params.provider_type == "openai"
        assert params.is_active is True
        assert params.sort_by == "display_name"
        assert params.sort_order == "asc"
    
    def test_validation_limits(self):
        """Test parameter validation limits"""
        # Test minimum page
        with pytest.raises(ValidationError):
            ListProvidersParams(page=0)
        
        # Test minimum size
        with pytest.raises(ValidationError):
            ListProvidersParams(size=0)
        
        # Test maximum size
        with pytest.raises(ValidationError):
            ListProvidersParams(size=101)
        
        # Test invalid sort order
        with pytest.raises(ValidationError):
            ListProvidersParams(sort_order="invalid")


class TestSearchProvidersParams:
    """Test cases for SearchProvidersParams"""
    
    def test_valid_search(self):
        """Test valid search parameters"""
        params = SearchProvidersParams(
            keyword="openai",
            provider_type="openai",
            is_active=True
        )
        
        assert params.keyword == "openai"
        assert params.provider_type == "openai"
        assert params.is_active is True
    
    def test_keyword_whitespace_handling(self):
        """Test keyword whitespace handling"""
        params = SearchProvidersParams(keyword="  test  ")
        assert params.keyword == "test"
    
    def test_empty_keyword_validation(self):
        """Test empty keyword validation"""
        with pytest.raises(ValidationError) as exc_info:
            SearchProvidersParams(keyword="   ")
        
        errors = exc_info.value.errors()
        assert any("搜索关键词不能为空字符串" in str(error) for error in errors)


class TestCreateModelConfigRequest:
    """Test cases for CreateModelConfigRequest"""
    
    def test_valid_request(self):
        """Test valid model config creation request"""
        request = CreateModelConfigRequest(
            model_name="gpt-4",
            model_display_name="GPT-4",
            model_type="chat",
            model_params={"supports_functions": True},
            max_tokens=4096,
            max_input_tokens=3072,
            temperature=Decimal("0.7"),
            pricing_config={"input_price": 0.03},
            is_active=True
        )
        
        assert request.model_name == "gpt-4"
        assert request.model_display_name == "GPT-4"
        assert request.model_type == "chat"
        assert request.max_tokens == 4096
        assert request.max_input_tokens == 3072
        assert request.temperature == Decimal("0.7")
        assert request.is_active is True
    
    def test_default_values(self):
        """Test default values"""
        request = CreateModelConfigRequest(
            model_name="test",
            model_display_name="Test",
            model_type="chat"
        )
        
        assert request.max_tokens == 4096
        assert request.max_input_tokens == 3072
        assert request.temperature == Decimal("0.70")
        assert request.is_active is True
    
    def test_token_validation(self):
        """Test token limit validation"""
        # Test negative tokens
        with pytest.raises(ValidationError):
            CreateModelConfigRequest(
                model_name="test",
                model_display_name="Test",
                model_type="chat",
                max_tokens=-1
            )
        
        # Test zero tokens
        with pytest.raises(ValidationError):
            CreateModelConfigRequest(
                model_name="test",
                model_display_name="Test",
                model_type="chat",
                max_tokens=0
            )
    
    def test_temperature_validation(self):
        """Test temperature validation"""
        # Test negative temperature
        with pytest.raises(ValidationError):
            CreateModelConfigRequest(
                model_name="test",
                model_display_name="Test",
                model_type="chat",
                temperature=Decimal("-0.1")
            )
        
        # Test temperature too high
        with pytest.raises(ValidationError):
            CreateModelConfigRequest(
                model_name="test",
                model_display_name="Test",
                model_type="chat",
                temperature=Decimal("2.1")
            )
    
    def test_empty_model_name(self):
        """Test empty model name validation"""
        with pytest.raises(ValidationError) as exc_info:
            CreateModelConfigRequest(
                model_name="",
                model_display_name="Test",
                model_type="chat"
            )
        
        errors = exc_info.value.errors()
        assert any("模型名称不能为空" in str(error) for error in errors)


class TestPaginatedResponse:
    """Test cases for PaginatedResponse"""
    
    def test_create_method(self):
        """Test PaginatedResponse.create method"""
        items = ["item1", "item2", "item3"]
        response = PaginatedResponse.create(
            items=items,
            total=10,
            page=1,
            size=3
        )
        
        assert response.items == items
        assert response.total == 10
        assert response.page == 1
        assert response.size == 3
        assert response.pages == 4  # ceil(10/3) = 4
    
    def test_pages_calculation(self):
        """Test pages calculation"""
        # Test exact division
        response = PaginatedResponse.create(items=[], total=20, page=1, size=10)
        assert response.pages == 2
        
        # Test with remainder
        response = PaginatedResponse.create(items=[], total=21, page=1, size=10)
        assert response.pages == 3
        
        # Test zero total
        response = PaginatedResponse.create(items=[], total=0, page=1, size=10)
        assert response.pages == 0


class TestMessageResponse:
    """Test cases for MessageResponse"""
    
    def test_success_message(self):
        """Test success message creation"""
        response = MessageResponse.success_message("操作成功", {"id": 1})
        
        assert response.message == "操作成功"
        assert response.success is True
        assert response.data == {"id": 1}
    
    def test_error_message(self):
        """Test error message creation"""
        response = MessageResponse.error_message("操作失败", {"error_code": "E001"})
        
        assert response.message == "操作失败"
        assert response.success is False
        assert response.data == {"error_code": "E001"}


class TestPaginationMeta:
    """Test cases for PaginationMeta"""
    
    def test_create_method(self):
        """Test PaginationMeta.create method"""
        meta = PaginationMeta.create(total=100, page=3, size=20)
        
        assert meta.total == 100
        assert meta.page == 3
        assert meta.size == 20
        assert meta.pages == 5
        assert meta.has_prev is True
        assert meta.has_next is True
        assert meta.prev_page == 2
        assert meta.next_page == 4
    
    def test_first_page(self):
        """Test first page metadata"""
        meta = PaginationMeta.create(total=100, page=1, size=20)
        
        assert meta.has_prev is False
        assert meta.has_next is True
        assert meta.prev_page is None
        assert meta.next_page == 2
    
    def test_last_page(self):
        """Test last page metadata"""
        meta = PaginationMeta.create(total=100, page=5, size=20)
        
        assert meta.has_prev is True
        assert meta.has_next is False
        assert meta.prev_page == 4
        assert meta.next_page is None
    
    def test_single_page(self):
        """Test single page metadata"""
        meta = PaginationMeta.create(total=10, page=1, size=20)
        
        assert meta.pages == 1
        assert meta.has_prev is False
        assert meta.has_next is False
        assert meta.prev_page is None
        assert meta.next_page is None


class TestBaseListParams:
    """Test cases for BaseListParams"""
    
    def test_default_values(self):
        """Test default parameter values"""
        params = BaseListParams()
        
        assert params.page == 1
        assert params.size == 20
        assert params.sort_by == "created_at"
        assert params.sort_order == "desc"
    
    def test_get_offset(self):
        """Test offset calculation"""
        params = BaseListParams(page=3, size=10)
        assert params.get_offset() == 20  # (3-1) * 10
        
        params = BaseListParams(page=1, size=10)
        assert params.get_offset() == 0  # (1-1) * 10
    
    def test_get_limit(self):
        """Test limit calculation"""
        params = BaseListParams(size=25)
        assert params.get_limit() == 25