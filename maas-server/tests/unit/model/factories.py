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

"""Test data factories for model module"""

import factory
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional

from model.domain.models.provider_model import ProviderEntity, ModelConfigEntity
from model.infrastructure.models import ProviderORM, ModelConfigORM


class ProviderEntityFactory(factory.Factory):
    """Provider entity factory for testing"""
    
    class Meta:
        model = ProviderEntity
    
    provider_id = factory.Sequence(lambda n: n)
    provider_name = factory.Sequence(lambda n: f"provider_{n}")
    provider_type = factory.Iterator(["openai", "anthropic", "google", "azure", "huggingface"])
    display_name = factory.Faker("company")
    description = factory.Faker("text", max_nb_chars=200)
    base_url = factory.LazyAttribute(lambda obj: f"https://api.{obj.provider_name.lower()}.com/v1")
    api_key = factory.Faker("uuid4")
    additional_config = factory.LazyFunction(lambda: {"timeout": 30, "retry_count": 3})
    is_active = True
    created_by = "test_user"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_by = "test_user"
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    is_delete = False


class ModelConfigEntityFactory(factory.Factory):
    """Model config entity factory for testing"""
    
    class Meta:
        model = ModelConfigEntity
    
    config_id = factory.Sequence(lambda n: n)
    provider_id = factory.SubFactory(ProviderEntityFactory)
    model_name = factory.Sequence(lambda n: f"model_{n}")
    model_display_name = factory.LazyAttribute(lambda obj: f"{obj.model_name.replace('_', ' ').title()}")
    model_type = factory.Iterator(["chat", "completion", "embedding", "image", "audio"])
    model_params = factory.LazyFunction(lambda: {"context_window": 4096, "supports_streaming": True})
    max_tokens = factory.Faker("random_int", min=1000, max=100000)
    max_input_tokens = factory.LazyAttribute(lambda obj: int(obj.max_tokens * 0.75))
    temperature = factory.LazyFunction(lambda: Decimal("0.70"))
    pricing_config = factory.LazyFunction(lambda: {
        "input_price_per_1k": 0.001,
        "output_price_per_1k": 0.002,
        "currency": "USD"
    })
    is_active = True
    created_by = "test_user"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_by = "test_user"
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    is_delete = False


class ProviderORMFactory(factory.Factory):
    """Provider ORM factory for testing"""
    
    class Meta:
        model = ProviderORM
    
    provider_id = factory.Sequence(lambda n: n)
    provider_name = factory.Sequence(lambda n: f"provider_{n}")
    provider_type = factory.Iterator(["openai", "anthropic", "google", "azure", "huggingface"])
    display_name = factory.Faker("company")
    description = factory.Faker("text", max_nb_chars=200)
    base_url = factory.LazyAttribute(lambda obj: f"https://api.{obj.provider_name.lower()}.com/v1")
    api_key = factory.Faker("uuid4")
    additional_config = factory.LazyFunction(lambda: {"timeout": 30, "retry_count": 3})
    is_active = True
    created_by = "test_user"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_by = "test_user"
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    is_delete = False


class ModelConfigORMFactory(factory.Factory):
    """Model config ORM factory for testing"""
    
    class Meta:
        model = ModelConfigORM
    
    config_id = factory.Sequence(lambda n: n)
    provider_id = factory.SubFactory(ProviderORMFactory)
    model_name = factory.Sequence(lambda n: f"model_{n}")
    model_display_name = factory.LazyAttribute(lambda obj: f"{obj.model_name.replace('_', ' ').title()}")
    model_type = factory.Iterator(["chat", "completion", "embedding", "image", "audio"])
    model_params = factory.LazyFunction(lambda: {"context_window": 4096, "supports_streaming": True})
    max_tokens = factory.Faker("random_int", min=1000, max=100000)
    max_input_tokens = factory.LazyAttribute(lambda obj: int(obj.max_tokens * 0.75))
    temperature = factory.LazyFunction(lambda: Decimal("0.70"))
    pricing_config = factory.LazyFunction(lambda: {
        "input_price_per_1k": 0.001,
        "output_price_per_1k": 0.002,
        "currency": "USD"
    })
    is_active = True
    created_by = "test_user"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_by = "test_user"
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    is_delete = False


# Helper functions for creating test data
def create_provider_entity(**kwargs) -> ProviderEntity:
    """Create a provider entity with optional overrides"""
    return ProviderEntityFactory(**kwargs)


def create_model_config_entity(**kwargs) -> ModelConfigEntity:
    """Create a model config entity with optional overrides"""
    return ModelConfigEntityFactory(**kwargs)


def create_provider_orm(**kwargs) -> ProviderORM:
    """Create a provider ORM with optional overrides"""
    return ProviderORMFactory(**kwargs)


def create_model_config_orm(**kwargs) -> ModelConfigORM:
    """Create a model config ORM with optional overrides"""
    return ModelConfigORMFactory(**kwargs)


def create_test_provider_data() -> Dict[str, Any]:
    """Create test provider data dictionary"""
    return {
        "provider_name": "test_provider",
        "provider_type": "openai",
        "display_name": "Test Provider",
        "description": "Test provider for unit testing",
        "base_url": "https://api.test.com/v1",
        "api_key": "test-api-key",
        "additional_config": {"timeout": 30},
        "is_active": True
    }


def create_test_model_config_data(provider_id: Optional[int] = None) -> Dict[str, Any]:
    """Create test model config data dictionary"""
    return {
        "provider_id": provider_id or 1,
        "model_name": "test_model",
        "model_display_name": "Test Model",
        "model_type": "chat",
        "model_params": {"context_window": 4096},
        "max_tokens": 4096,
        "max_input_tokens": 3072,
        "temperature": Decimal("0.70"),
        "pricing_config": {"input_price_per_1k": 0.001},
        "is_active": True
    }