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

"""共享领域测试 - 基础类测试"""

import pytest
from datetime import datetime
from uuid import uuid4

from src.shared.domain.base import (
    Entity, 
    AggregateRoot, 
    ValueObject, 
    DomainEvent,
    DomainException,
    BusinessRuleViolationException,
    EmailAddress
)


class TestEntity:
    """实体测试"""
    
    def test_entity_creation(self):
        """测试实体创建"""
        entity_id = uuid4()
        entity = Entity(entity_id)
        
        assert entity.id == entity_id
        assert str(entity) == str(entity_id)
    
    def test_entity_equality(self):
        """测试实体相等性"""
        entity_id = uuid4()
        entity1 = Entity(entity_id)
        entity2 = Entity(entity_id)
        entity3 = Entity(uuid4())
        
        assert entity1 == entity2
        assert entity1 != entity3
        assert hash(entity1) == hash(entity2)
        assert hash(entity1) != hash(entity3)


class TestValueObject:
    """值对象测试"""
    
    def test_value_object_creation(self):
        """测试值对象创建"""
        from dataclasses import dataclass
        
        @dataclass(frozen=True)
        class TestValue(ValueObject):
            name: str
            value: int
            
            def _validate(self):
                if not self.name:
                    raise ValueError("名称不能为空")
                if self.value < 0:
                    raise ValueError("值不能为负数")
        
        # 正常创建
        value = TestValue("test", 10)
        assert value.name == "test"
        assert value.value == 10
        
        # 验证失败
        with pytest.raises(ValueError, match="名称不能为空"):
            TestValue("", 10)
        
        with pytest.raises(ValueError, match="值不能为负数"):
            TestValue("test", -1)
    
    def test_value_object_equality(self):
        """测试值对象相等性"""
        from dataclasses import dataclass
        
        @dataclass(frozen=True)
        class TestValue(ValueObject):
            name: str
            value: int
        
        value1 = TestValue("test", 10)
        value2 = TestValue("test", 10)
        value3 = TestValue("test", 20)
        
        assert value1 == value2
        assert value1 != value3
        assert hash(value1) == hash(value2)
        assert hash(value1) != hash(value3)


class TestDomainEvent:
    """领域事件测试"""
    
    def test_domain_event_creation(self):
        """测试领域事件创建"""
        event_id = uuid4()
        aggregate_id = uuid4()
        occurred_at = datetime.utcnow()
        
        event = DomainEvent(
            event_id=event_id,
            occurred_at=occurred_at,
            event_type="test.event",
            aggregate_id=aggregate_id,
            aggregate_type="TestAggregate",
            event_data={"key": "value"}
        )
        
        assert event.event_id == event_id
        assert event.occurred_at == occurred_at
        assert event.event_type == "test.event"
        assert event.aggregate_id == aggregate_id
        assert event.aggregate_type == "TestAggregate"
        assert event.event_data == {"key": "value"}


class TestAggregateRoot:
    """聚合根测试"""
    
    def test_aggregate_root_creation(self):
        """测试聚合根创建"""
        aggregate_id = uuid4()
        aggregate = AggregateRoot(aggregate_id)
        
        assert aggregate.id == aggregate_id
        assert aggregate.version == 0
        assert len(aggregate.domain_events) == 0
    
    def test_add_domain_event(self):
        """测试添加领域事件"""
        aggregate = AggregateRoot(uuid4())
        
        event = DomainEvent(
            event_id=uuid4(),
            occurred_at=datetime.utcnow(),
            event_type="test.event",
            aggregate_id=aggregate.id,
            aggregate_type="TestAggregate",
            event_data={}
        )
        
        aggregate.add_domain_event(event)
        
        assert len(aggregate.domain_events) == 1
        assert aggregate.domain_events[0] == event
    
    def test_clear_domain_events(self):
        """测试清除领域事件"""
        aggregate = AggregateRoot(uuid4())
        
        event = DomainEvent(
            event_id=uuid4(),
            occurred_at=datetime.utcnow(),
            event_type="test.event",
            aggregate_id=aggregate.id,
            aggregate_type="TestAggregate",
            event_data={}
        )
        
        aggregate.add_domain_event(event)
        assert len(aggregate.domain_events) == 1
        
        aggregate.clear_domain_events()
        assert len(aggregate.domain_events) == 0
    
    def test_increment_version(self):
        """测试版本增加"""
        aggregate = AggregateRoot(uuid4())
        
        assert aggregate.version == 0
        aggregate.increment_version()
        assert aggregate.version == 1


class TestDomainException:
    """领域异常测试"""
    
    def test_domain_exception(self):
        """测试领域异常"""
        exception = DomainException("测试异常")
        
        assert str(exception) == "测试异常"
        assert exception.message == "测试异常"
    
    def test_business_rule_violation_exception(self):
        """测试业务规则违反异常"""
        exception = BusinessRuleViolationException("业务规则违反")
        
        assert str(exception) == "业务规则违反"
        assert exception.message == "业务规则违反"
        assert isinstance(exception, DomainException)


class TestEmailAddress:
    """邮箱地址测试"""
    
    def test_valid_email(self):
        """测试有效邮箱"""
        email = EmailAddress("test@example.com")
        
        assert email.value == "test@example.com"
        assert str(email) == "test@example.com"
    
    def test_invalid_email(self):
        """测试无效邮箱"""
        with pytest.raises(ValueError, match="无效的邮箱地址"):
            EmailAddress("invalid-email")
        
        with pytest.raises(ValueError, match="无效的邮箱地址"):
            EmailAddress("test@")
        
        with pytest.raises(ValueError, match="无效的邮箱地址"):
            EmailAddress("@example.com")
    
    def test_email_equality(self):
        """测试邮箱相等性"""
        email1 = EmailAddress("test@example.com")
        email2 = EmailAddress("test@example.com")
        email3 = EmailAddress("other@example.com")
        
        assert email1 == email2
        assert email1 != email3
        assert hash(email1) == hash(email2)
        assert hash(email1) != hash(email3)