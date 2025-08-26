# DDD重构方法论文档

## 1. 概述

本文档总结了MaaS后端系统进行领域驱动设计(DDD)重构的完整方法论，包括识别架构违规、系统化重构流程、最佳实践和验证标准。

## 2. 背景问题

### 2.1 发现的DDD架构违规

在重构过程中，发现了严重的DDD分层架构违规问题：

**Domain Service层违规统计**：
- `UserDomainService`: 18个Repository调用违规
- `PermissionDomainService`: 21个Repository调用违规
- `RoleDomainService`: 15个Repository调用违规
- `AuthDomainService`: 1个Repository调用违规

**总计：55个Repository调用违规**

### 2.2 核心问题

1. **分层违规**：Domain Service直接调用Repository，违反了DDD分层原则
2. **职责混乱**：Domain Service承担了数据访问职责
3. **事务管理缺失**：Repository层自动提交，缺乏统一事务管理
4. **测试困难**：Domain Service与数据层耦合，难以单元测试

## 3. DDD重构方法论

### 3.1 重构总体原则

#### 3.1.1 分层职责明确

**Domain Service层**：
- ✅ 纯业务逻辑处理
- ✅ 业务规则验证
- ✅ 实体操作和状态变更
- ❌ 不允许Repository调用
- ❌ 不允许数据库访问
- ❌ 不允许外部服务调用

**Application Service层**：
- ✅ 事务管理
- ✅ Repository调用
- ✅ Domain Service编排
- ✅ 数据传输对象(DTO)转换
- ✅ 外部服务协调

#### 3.1.2 事务管理原则

- **Repository层去事务化**：移除自动提交，只执行flush
- **Application Service管理事务**：使用装饰器统一管理
- **读写分离**：`@transactional`用于写操作，`@readonly_operation`用于读操作

### 3.2 系统化重构流程

#### 步骤1：违规识别
```bash
# 搜索Domain Service中的Repository调用
grep -r "await.*_repository\." src/user/domain/services/
grep -r "repository\." src/user/domain/services/
```

#### 步骤2：Domain Service重构

**重构前（违规代码）**：
```python
class UserDomainService:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository  # ❌ 违规依赖
    
    async def create_user(self, username: str) -> User:
        existing = await self._user_repository.find_by_username(username)  # ❌ 违规调用
        if existing:
            raise UserAlreadyExistsException()
        
        user = User.create(username)
        await self._user_repository.save(user)  # ❌ 违规调用
        return user
```

**重构后（符合DDD）**：
```python
class UserDomainService:
    def __init__(self, validation_service: UserValidationService):
        # ✅ 只依赖其他Domain Service
        self._validation_service = validation_service
    
    def validate_user_uniqueness(self, existing_user, username: str) -> None:
        """验证用户唯一性（纯业务逻辑）"""  # ✅ 同步方法
        if existing_user:
            raise UserAlreadyExistsException(f"用户名 {username} 已存在")
    
    def create_user_entity(self, username: str) -> User:
        """创建用户实体（纯业务逻辑）"""  # ✅ 同步方法
        self._validation_service.validate_username(username)
        return User.create(username)
```

#### 步骤3：Application Service重构

**重构后（正确架构）**：
```python
class UserApplicationService:
    def __init__(self, 
                 user_domain_service: UserDomainService,
                 user_repository: IUserRepository):
        self._user_domain_service = user_domain_service
        self._user_repository = user_repository  # ✅ Application层管理Repository
    
    @transactional()
    async def create_user(
        self, 
        command: UserCreateCommand,
        session: AsyncSession = Depends(get_write_session)
    ) -> UserResponse:
        # 1. Application Service查询Repository
        existing_user = await self._user_repository.find_by_username(command.username)
        
        # 2. Domain Service验证业务规则
        self._user_domain_service.validate_user_uniqueness(existing_user, command.username)
        
        # 3. Domain Service创建实体
        user = self._user_domain_service.create_user_entity(command.username)
        
        # 4. Application Service持久化
        saved_user = await self._user_repository.save(user)
        
        # 事务在装饰器中自动提交
        return self._to_user_response(saved_user)
```

#### 步骤4：Repository层去事务化

**重构前（违规自动提交）**：
```python
async def save(self, user: User) -> User:
    # ... 保存逻辑
    await session.commit()  # ❌ 违规自动提交
    return user
```

**重构后（只执行flush）**：
```python
async def save(self, user: User) -> User:
    # ... 保存逻辑
    await session.flush()  # ✅ 只flush，不提交
    # ✅ 移除自动提交 - 由上层事务管理
    return user
```

### 3.3 重构验证标准

#### 3.3.1 Domain Service验证

**通过标准**：
- ✅ 构造函数无Repository依赖
- ✅ 所有方法都是同步的（async方法数量 = 0）
- ✅ 无Repository调用
- ✅ 只包含纯业务逻辑

**验证命令**：
```bash
# 检查异步方法数量（应该为0）
grep -c "async def" src/user/domain/services/user_domain_service.py

# 检查Repository调用（应该为0）
grep -c "await.*repository" src/user/domain/services/user_domain_service.py
```

#### 3.3.2 Application Service验证

**通过标准**：
- ✅ 所有写操作方法都有`@transactional()`装饰器
- ✅ 所有读操作方法都有`@readonly_operation`装饰器
- ✅ 构造函数包含需要的Repository依赖
- ✅ 遵循：查询Repository → Domain Service处理 → Repository持久化

**验证示例**：
```python
# ✅ 正确的DDD流程示例
@transactional()
async def update_user_profile(self, command):
    # 1. 查询
    user = await self._user_repository.find_by_id(command.user_id)
    
    # 2. 业务逻辑
    updated_user = self._user_domain_service.update_user_profile_entity(
        user, command.first_name, command.last_name
    )
    
    # 3. 持久化
    saved_user = await self._user_repository.save(updated_user)
    return self._to_user_response(saved_user)
```

### 3.4 事务管理最佳实践

#### 3.4.1 装饰器使用规范

```python
# 写操作：使用@transactional()
@transactional()
async def create_user(self, session: AsyncSession = Depends(get_write_session)):
    # 事务操作
    pass

# 读操作：使用@readonly_operation
@readonly_operation
async def get_user(self, session: AsyncSession = Depends(get_readonly_session)):
    # 只读操作
    pass
```

#### 3.4.2 Session依赖注入

```python
# ✅ 正确的session注入
async def create_user(
    self,
    command: UserCreateCommand, 
    session: AsyncSession = Depends(get_write_session)  # 明确session来源
):
    pass

# ❌ 错误：缺少session参数
async def create_user(self, command: UserCreateCommand):
    pass
```

## 4. 重构成果统计

### 4.1 Domain Service重构成果

| Service | 重构前违规数 | 重构后违规数 | 异步方法变化 | 同步方法数量 |
|---------|-------------|-------------|-------------|-------------|
| UserDomainService | 18 | 0 | 13→0 | 14 |
| PermissionDomainService | 21 | 0 | 21→0 | 12 |
| RoleDomainService | 15 | 0 | 8→0 | 9 |
| AuthDomainService | 1 | 0 | 1→0 | 4 |
| **总计** | **55** | **0** | **43→0** | **39** |

### 4.2 Application Service重构成果

| Service | 事务装饰器方法数 | Repository依赖数 | DDD流程完整性 |
|---------|-----------------|-----------------|---------------|
| UserApplicationService | 15 | 2 | ✅ 完整 |
| PermissionApplicationService | 14 | 3 | ✅ 完整 |
| RoleApplicationService | 9 | 3 | ✅ 完整 |
| AuthService | 2 | 1 | ✅ 完整 |
| **总计** | **40** | **9** | **100%** |

## 5. 最佳实践总结

### 5.1 Domain Service设计原则

1. **纯业务逻辑**：只包含业务规则和实体操作
2. **同步方法**：所有方法都应该是同步的
3. **无副作用**：不执行I/O操作，不调用外部服务
4. **高内聚**：相关业务逻辑集中管理
5. **易测试**：可以通过单元测试验证业务逻辑

### 5.2 Application Service设计原则

1. **事务边界**：清晰的事务边界管理
2. **编排职责**：编排Domain Service和Repository
3. **DTO转换**：处理数据传输对象转换
4. **异常处理**：统一的异常处理和响应
5. **依赖注入**：明确的依赖关系管理

### 5.3 命名约定

#### Domain Service方法命名
- `validate_*_data()` - 数据格式验证
- `validate_*_uniqueness()` - 唯一性验证  
- `validate_*_rules()` - 业务规则验证
- `create_*_entity()` - 创建实体
- `update_*_entity()` - 更新实体
- `calculate_*()` - 计算逻辑
- `*_logic()` - 业务逻辑处理

#### Application Service方法命名
- 保持原有业务方法名
- 添加适当的事务装饰器
- 明确session参数注入

## 6. 常见问题与解决方案

### 6.1 问题：Domain Service需要查询数据怎么办？

**错误做法**：
```python
# ❌ Domain Service直接调用Repository
async def validate_user_creation(self, username: str):
    existing = await self._user_repository.find_by_username(username)
    if existing:
        raise UserAlreadyExistsException()
```

**正确做法**：
```python
# ✅ 拆分为两个方法
# Domain Service：纯业务逻辑
def validate_user_uniqueness(self, existing_user, username: str):
    if existing_user:
        raise UserAlreadyExistsException(f"用户名 {username} 已存在")

# Application Service：查询并调用Domain Service
@transactional()
async def create_user(self, command):
    existing_user = await self._user_repository.find_by_username(command.username)
    self._domain_service.validate_user_uniqueness(existing_user, command.username)
```

### 6.2 问题：复杂业务逻辑需要多次查询怎么办？

**解决方案**：在Application Service中进行所有查询，然后传递给Domain Service

```python
@transactional()
async def update_role_permissions(self, role_id: UUID, permission_ids: list[UUID]):
    # 1. 一次性查询所有需要的数据
    role = await self._role_repository.find_by_id(role_id)
    permissions = []
    for pid in permission_ids:
        perm = await self._permission_repository.find_by_id(pid)
        if perm:
            permissions.append(perm)
    users_with_role = await self._user_repository.find_by_role_id(role_id)
    
    # 2. 传递给Domain Service处理业务逻辑
    self._role_domain_service.validate_role_permission_update_rules(role)
    updated_role = self._role_domain_service.update_role_permissions_entity(role, permissions)
    updated_users = self._role_domain_service.invalidate_users_tokens_for_role_change(users_with_role)
    
    # 3. 批量保存
    await self._role_repository.save(updated_role)
    for user in updated_users:
        await self._user_repository.save(user)
```

### 6.3 问题：事务装饰器参数配置

```python
# ✅ 写操作配置
@transactional()  # 默认session参数名为"session"
async def create_user(self, session: AsyncSession = Depends(get_write_session)):
    pass

# ✅ 自定义session参数名
@transactional(session_key="db_session")
async def create_user(self, db_session: AsyncSession = Depends(get_write_session)):
    pass

# ✅ 只读操作配置
@readonly_operation
async def get_user(self, session: AsyncSession = Depends(get_readonly_session)):
    pass
```

## 7. 重构效果评估

### 7.1 代码质量提升

1. **分层清晰**：Domain Service和Application Service职责明确
2. **可测试性**：Domain Service可以进行纯单元测试
3. **可维护性**：业务逻辑集中，修改影响范围小
4. **扩展性**：新增业务功能遵循统一模式

### 7.2 架构健康度

- **DDD违规数量**：55 → 0（100%消除）
- **异步Domain方法**：43 → 0（100%同步化）
- **事务管理覆盖**：100%覆盖所有写操作
- **分层依赖**：完全符合DDD分层原则

### 7.3 开发效率

1. **统一模式**：所有Service遵循相同的重构模式
2. **清晰流程**：Application Service的标准化流程
3. **易于理解**：新开发者容易理解架构设计
4. **减少Bug**：统一的事务管理减少数据一致性问题

## 8. 未来改进建议

### 8.1 自动化检查

建议添加架构约束检查：
```python
# 架构测试示例
def test_domain_service_no_repository_dependencies():
    """确保Domain Service不依赖Repository"""
    pass

def test_domain_service_all_methods_sync():
    """确保Domain Service所有方法都是同步的"""
    pass

def test_application_service_transaction_coverage():
    """确保Application Service事务装饰器覆盖所有写操作"""
    pass
```

### 8.2 文档化

1. **架构决策记录(ADR)**：记录重要的架构决策
2. **代码注释**：标明DDD分层和职责
3. **开发指南**：新功能开发的DDD规范

### 8.3 工具支持

1. **静态分析**：检查DDD违规的工具
2. **代码生成**：基于模板生成符合DDD的Service代码
3. **架构可视化**：展示分层关系和依赖关系

---

**总结**：通过系统化的DDD重构方法论，成功消除了55个架构违规，建立了清晰的分层架构，提升了代码质量和可维护性。这套方法论可以作为未来类似项目重构的参考标准。