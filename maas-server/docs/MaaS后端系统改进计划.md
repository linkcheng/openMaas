# MaaS后端系统改进计划

## 项目概述

本文档基于对MaaS后端系统的深度分析，制定了一份综合性的改进计划。该计划遵循"简单至上、避免过度设计"的原则，专注于解决实际问题，提升开发效率和系统可维护性。

## 一、改进目标

### 1.1 核心目标
- **解决事务嵌套冲突**：统一事务管理，明确分层职责
- **提升异常处理能力**：完善异常体系，增强问题排查效率  
- **优化开发体验**：简化开发流程，减少重复代码
- **增强系统可观测性**：提供必要的监控和日志功能

### 1.2 设计原则
- ✅ **简单至上**：避免过度设计，保持系统简洁
- ✅ **分层清晰**：明确各层职责边界
- ✅ **渐进改进**：分阶段实施，降低风险
- ✅ **实用主义**：解决实际痛点，提升开发效率

## 二、问题分析

### 2.1 事务管理问题
| 问题 | 影响 | 优先级 |
|------|------|--------|
| 多层级事务嵌套冲突 | 系统不稳定，难以调试 | 🔴 高 |
| Repository层承担事务职责 | 违反DDD原则，难以测试 | 🔴 高 |
| 读写操作未分离 | 性能浪费，架构不清晰 | 🟡 中 |

### 2.2 异常处理问题
| 问题 | 影响 | 优先级 |
|------|------|--------|
| 缺少trace_id链路追踪 | 问题排查困难 | 🔴 高 |
| 错误码缺少分类规范 | 维护困难，可读性差 | 🟡 中 |
| 异常监控不完善 | 运维被动，问题发现滞后 | 🟡 中 |

### 2.3 可观测性问题
| 问题 | 影响 | 优先级 |
|------|------|--------|
| Request ID与Trace ID概念混淆 | 追踪不清晰 | 🟡 中 |
| 缺少基础指标监控 | 系统状态不透明 | 🟢 低 |
| 日志格式不统一 | 问题排查效率低 | 🟢 低 |

## 三、改进方案

### 3.1 异常处理优化（高优先级）

#### 3.1.1 Request ID重构为Trace ID + 日志服务简化（推荐方案）

**详细方案参考：[request_id重构为trace_id方案.md](./request_id重构为trace_id方案.md)**

**核心思路**：
1. 直接将现有的`request_id`重构为`trace_id`，简化概念，避免冗余
2. 同时简化logging_service为纯粹的loguru基础配置服务
3. trace_id功能集成到RequestContextMiddleware中

```python


# 1. 简化logging_service为基础配置服务 + trace_id支持
import contextvars

# 保留trace_id上下文变量（业务代码友好）
trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('trace_id')

class LoggingService:
    """简化版日志服务 - 基础配置 + trace_id支持"""
    
    def configure(self) -> None:
        """配置日志系统 - 仅做基础配置"""
        if self._configured:
            return
            
        logger.remove()  # 清除默认handler
        
        # 配置文件日志
        if self.settings.log_file_enabled:
            logger.add(
                self.settings.log_dir / "app.log",
                level=self.settings.log_level,
                format=self.settings.log_format,
                rotation=self.settings.log_rotation,
                retention=self.settings.log_retention,
                compression="gz"
            )
        
        # 配置控制台日志  
        if self.settings.log_console_enabled:
            logger.add(
                sys.stdout,
                level=self.settings.log_level,
                format=self._get_console_format(),
                colorize=True
            )

# 便捷的trace_id功能（保留）
def get_trace_id() -> str | None:
    """获取当前上下文的trace_id"""
    try:
        return trace_id_var.get()
    except LookupError:
        return None

def set_trace_id(trace_id: str) -> None:
    """设置trace_id到上下文"""
    trace_id_var.set(trace_id)

def get_logger_with_trace():
    """获取自动包含trace_id的logger（业务代码友好）"""
    trace_id = get_trace_id()
    return logger.bind(trace_id=trace_id) if trace_id else logger

# 2. RequestContextMiddleware集成trace_id功能
class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件 - 统一使用trace_id"""

    async def dispatch(self, request: Request, call_next):
        # 生成trace_id（统一标识，短格式便于查看）
        trace_id = str(uuid.uuid4())[:8]
        
        # 设置到contextvar（业务代码可用！）
        set_trace_id(trace_id)
        
        # 设置到request.state（保持向后兼容）
        request.state.trace_id = trace_id
        request.state.request_id = trace_id  # 保持向后兼容
        
        # 使用便捷函数获取带trace_id的logger
        logger_with_trace = get_logger_with_trace()
        
        logger_with_trace.info(f"请求开始 - {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            process_time = time.time() - request.state.start_time
            
            # 添加响应头（保持兼容性）
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Request-ID"] = trace_id  # 保持兼容性
            
            logger_with_trace.info(
                f"请求完成 - Status: {response.status_code}, "
                f"Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger_with_trace.error(f"请求异常 - {e}", exc_info=True)
            raise
```

**简化重构优势**：
- ✅ **概念统一**：消除request_id和trace_id的混淆
- ✅ **职责清晰**：logging_service专注配置，middleware专注请求处理  
- ✅ **代码减少**：logging_service从284行简化到约100行（保留核心trace功能）
- ✅ **业务友好**：contextvars让业务代码轻松获取trace_id，无需传参
- ✅ **异步完美**：contextvars在FastAPI异步环境中自动传播
- ✅ **向后兼容**：保持现有API响应头不变
- ✅ **避免过度设计**：移除85%未使用功能，保留实用的trace支持
- ✅ **维护简单**：基于实际使用情况的务实设计

**业务代码使用示例**：
```python
# 在任何业务服务中，无需传参即可使用trace_id
from shared.infrastructure.logging_service import get_logger_with_trace, get_trace_id

class UserService:
    async def create_user(self, user_data):
        # 方式1：自动包含trace_id的logger
        logger = get_logger_with_trace()
        logger.info(f"创建用户: {user_data.email}")
        
        # 方式2：手动获取trace_id
        trace_id = get_trace_id()
        logger.bind(trace_id=trace_id, user_id=user.id).info("用户创建完成")
        
        return user
```

#### 3.1.2 错误码分类规范
```python
class ErrorCode(str, Enum):
    # 系统错误 (SYS_)
    SYS_INTERNAL_ERROR = "SYS_INTERNAL_ERROR"
    SYS_DATABASE_ERROR = "SYS_DATABASE_ERROR"
    
    # 认证错误 (AUTH_)
    AUTH_FAILED = "AUTH_FAILED"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    
    # 验证错误 (VAL_)
    VAL_INVALID_INPUT = "VAL_INVALID_INPUT"
    VAL_REQUIRED_FIELD = "VAL_REQUIRED_FIELD"
    
    # 资源错误 (RES_)
    RES_NOT_FOUND = "RES_NOT_FOUND"
    RES_ALREADY_EXISTS = "RES_ALREADY_EXISTS"
    
    # 业务错误 (BIZ_)
    BIZ_INSUFFICIENT_BALANCE = "BIZ_INSUFFICIENT_BALANCE"
    BIZ_INVALID_OPERATION = "BIZ_INVALID_OPERATION"
```

#### 3.1.3 基础异常监控
```python
class SimpleExceptionMonitor:
    def __init__(self):
        self.exception_counts = defaultdict(int)
        self.last_exceptions: List[dict] = []
    
    def record_exception(self, exc: ApplicationException, endpoint: str = None):
        self.exception_counts[exc.code] += 1
        self.last_exceptions.append({
            "code": exc.code,
            "message": exc.message,
            "trace_id": exc.trace_id,
            "endpoint": endpoint,
            "timestamp": exc.timestamp.isoformat()
        })
```

### 3.2 事务管理重构（高优先级）

#### 3.2.1 重构目标
- 消除事务嵌套冲突
- 明确各层事务职责
- 实现读写分离优化
- 提供声明式事务管理

#### 3.2.2 技术方案

**详细技术方案参考：[事务管理重构方案.md](./事务管理重构方案.md)**

**核心重构内容**：

```python
# 1. 基础设施层：仅提供session，不自动管理事务
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话，不自动管理事务"""
    async with async_session_factory() as session:
        try:
            yield session
            # ❌ 移除自动提交
            # await session.commit()
        except Exception as exc:
            # ❌ 移除自动回滚，由上层控制
            # await session.rollback()
            logger.error(f"Database session error: {exc}")
            raise
        finally:
            await session.close()

# 新增：读写分离的会话管理
async def get_readonly_session() -> AsyncGenerator[AsyncSession, None]:
    """提供只读数据库会话"""
    async with async_session_factory() as session:
        try:
            # 设置为只读模式
            await session.execute(text("SET TRANSACTION READ ONLY"))
            yield session
            # 读操作无需提交
        except Exception as exc:
            logger.error(f"Database readonly session error: {exc}")
            raise
        finally:
            await session.close()

# 2. Repository层：仅负责数据操作，使用flush代替commit
class UserRepository:
    async def save(self, user: User) -> User:
        """保存用户 - 仅负责数据持久化"""
        if hasattr(user, 'id') and user.id:
            # 更新操作
            user_orm = await self._get_orm_by_id(user.id)
            self._update_orm_from_domain(user_orm, user)
        else:
            # 创建操作
            user_orm = self._to_orm(user)
            self.session.add(user_orm)
        
        # ✅ 仅flush，确保获得ID等，但不提交
        await self.session.flush()
        # ❌ 移除事务提交
        # await self.session.commit()
        
        return self._to_domain(user_orm)

# 3. 应用服务层：声明式事务管理
def transactional(session_key: str = "session"):
    """声明式事务管理装饰器 - 仅用于写操作"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            session: AsyncSession = kwargs.get(session_key)
            if not session:
                raise ValueError(f"缺少session参数: {session_key}")
            
            try:
                result = await func(*args, **kwargs)
                await session.commit()  # 统一提交
                return result
            except Exception as exc:
                await session.rollback()  # 统一回滚
                logger.error(f"事务执行失败: {exc}")
                raise
        return wrapper
    return decorator

# 使用示例
@transactional()
async def create_user_with_roles(
    self, 
    command: CreateUserCommand, 
    session: AsyncSession = Depends(get_async_session)
) -> UserResponse:
    """创建用户并分配角色 - 事务操作"""
    # 验证邮箱唯一性
    existing_user = await self._user_repository.find_by_email(command.email)
    if existing_user:
        raise UserAlreadyExistsException(command.email)
    
    # 创建用户
    user = User.create(...)
    saved_user = await self._user_repository.save(user)
    
    # 分配角色
    if command.role_ids:
        await self._role_repository.assign_roles(saved_user.id, command.role_ids)
    
    # 事务在装饰器中自动提交
    return UserResponse.from_domain(saved_user)
```

**分层职责重新定义**：

```
┌─────────────────────────────────────────┐
│          接口层 (Controller)             │  
│  职责：参数验证、响应格式化                │
│  事务：不涉及                           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         应用服务层 (Service)              │
│  职责：编排业务逻辑、控制事务边界           │
│  事务：✅ 统一管理事务边界（读写分离）      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         仓储层 (Repository)              │
│  职责：数据持久化、查询优化               │
│  事务：❌ 不管理事务，只执行SQL           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        基础设施层 (Database)             │
│  职责：提供数据库会话                    │
│  事务：❌ 仅提供会话，不自动提交          │
└─────────────────────────────────────────┘
```

#### 3.2.3 实施步骤

**基于事务管理重构方案的详细实施步骤**：

1. **第一周**：基础设施层重构
   - 修改`src/shared/infrastructure/database.py`
   - 移除`get_async_session`中的自动commit/rollback
   - 新增`get_readonly_session`用于读操作
   - 实现`TransactionManager`工具类

2. **第二周**：Repository层去事务化
   - 修改所有Repository实现类
   - 将`await session.commit()`替换为`await session.flush()`
   - 移除所有`await session.rollback()`调用
   - 确保Repository只负责数据操作

3. **第三周**：应用服务层事务装饰器
   - 实现`@transactional()`和`@readonly_operation()`装饰器
   - 应用到所有应用服务方法
   - 区分读写操作，使用不同的session和装饰器

4. **第四周**：依赖注入调整和测试完善
   - 修改依赖注入配置，区分读写Repository
   - 调整Controller层的依赖注入
   - 完善单元测试和集成测试，验证事务边界正确性

**详细的代码修改示例和最佳实践请参考：[事务管理重构方案.md](./事务管理重构方案.md)**

### 3.3 领域驱动设计优化（中优先级）

#### 3.3.1 检查和优化DDD分层架构

**目标**：确保系统严格遵循DDD分层原则，明确各层职责边界。

**分层职责检查**：
```python
# Domain层：定义仓储接口，不依赖外部框架
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

class IUserRepository(ABC):
    """用户仓储接口 - 定义在Domain层"""
    
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """根据ID查找用户"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """根据邮箱查找用户"""
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """保存用户"""
        pass
    
    @abstractmethod
    async def delete(self, user: User) -> None:
        """删除用户"""
        pass

# Infrastructure层：实现仓储接口
from user.domain.repositories import IUserRepository
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository(IUserRepository):
    """用户仓储实现 - Infrastructure层"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        # SQLAlchemy实现细节
        query = select(UserORM).where(UserORM.id == user_id)
        result = await self.session.execute(query)
        user_orm = result.scalar_one_or_none()
        return self._to_domain(user_orm) if user_orm else None

# Application层：管理事务，编排业务逻辑
class UserApplicationService:
    """用户应用服务 - 负责事务管理和业务编排"""
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    @transactional()
    async def create_user_with_profile(
        self, 
        command: CreateUserCommand,
        session: AsyncSession = Depends(get_async_session)
    ) -> UserResponse:
        """创建用户 - Application层管理事务"""
        
        # 业务规则验证
        existing_user = await self._user_repository.find_by_email(command.email)
        if existing_user:
            raise UserAlreadyExistsException(command.email)
        
        # 创建领域对象
        user = User.create(
            email=command.email,
            username=command.username
        )
        
        # 持久化（Repository不管事务）
        saved_user = await self._user_repository.save(user)
        
        # 事务在@transactional装饰器中统一管理
        return UserResponse.from_domain(saved_user)
```

#### 3.3.2 DDD分层合规性检查清单

**Domain层检查**：
- ✅ 仓储接口定义在Domain层
- ✅ 实体和值对象不依赖外部框架
- ✅ 业务规则封装在领域模型中
- ✅ 不包含任何基础设施依赖

**Application层检查**：
- ✅ 应用服务协调多个聚合根
- ✅ 事务边界在应用服务层管理
- ✅ 依赖仓储接口，不依赖具体实现
- ✅ 处理跨聚合根的业务逻辑

**Infrastructure层检查**：
- ✅ 实现Domain层定义的仓储接口
- ✅ 包含ORM映射和数据库访问逻辑
- ✅ 不包含业务逻辑
- ✅ 负责外部系统集成

**Interface层检查**：
- ✅ 仅负责HTTP请求/响应转换
- ✅ 参数验证和格式化
- ✅ 调用应用服务，不直接操作仓储
- ✅ 异常处理和响应格式统一

#### 3.3.3 依赖注入优化

**确保依赖方向正确**：
```python
# 依赖注入配置 - 确保依赖方向符合DDD
from user.domain.repositories import IUserRepository  # 接口定义在Domain
from user.infrastructure.repositories import UserRepository  # 实现在Infrastructure

async def get_user_repository(
    session: AsyncSession = Depends(get_async_session)
) -> IUserRepository:  # 返回接口类型
    """返回仓储接口，隐藏具体实现"""
    return UserRepository(session=session)

async def get_user_application_service(
    user_repo: IUserRepository = Depends(get_user_repository)  # 依赖接口
) -> UserApplicationService:
    """应用服务依赖仓储接口，不依赖具体实现"""
    return UserApplicationService(user_repository=user_repo)
```

## 四、实施计划

### 4.1 时间安排

#### 第一阶段：核心重构（4周）

**参考文档**：
- 📄 [事务管理重构方案.md](./事务管理重构方案.md) - 详细的事务管理重构指南
- 📄 [request_id重构为trace_id方案.md](./request_id重构为trace_id方案.md) - Request ID统一重构方案
- 📄 [简化版异常处理最佳实践.md](./简化版异常处理最佳实践.md) - 异常处理优化方案
- 📄 [OpenTelemetry_vs_Jaeger_选择指南.md](./OpenTelemetry_vs_Jaeger_选择指南.md) - 可观测性工具选择

| 周次 | 任务 | 负责人 | 产出 | 参考文档 |
|------|------|--------|------|----------|
| 第1周 | Request ID重构为Trace ID + 日志服务简化 | 后端开发 | 重构中间件统一trace_id，简化logging_service | request_id重构为trace_id方案.md + logging_service简化 |
| 第2周 | 错误码分类重构 | 后端开发 | ErrorCode枚举更新，前缀分组 | 简化版异常处理最佳实践.md 2.2节 |
| 第3周 | 事务管理基础设施层重构 | 后端开发 | 修改database.py，新增readonly_session | 事务管理重构方案.md 3.1节 |
| 第4周 | Repository层去事务化 | 后端开发 | 修改所有Repository，移除commit调用 | 事务管理重构方案.md 3.2节 |

#### 第二阶段：优化完善（3周）
| 周次 | 任务 | 负责人 | 产出 | 参考文档 |
|------|------|--------|------|----------|
| 第5周 | 应用服务层事务装饰器 | 后端开发 | @transactional装饰器实现和应用 | 事务管理重构方案.md 3.3节 |
| 第6周 | DDD分层架构检查优化 | 后端开发 | 确保仓储接口在Domain层，依赖注入优化 | 本计划3.3节 |
| 第7周 | 异常监控和测试完善 | 后端开发 | SimpleExceptionMonitor，完整测试覆盖 | 简化版异常处理最佳实践.md 3.3节 |

#### 第三阶段：监控扩展（按需）
| 时间 | 任务 | 说明 | 参考文档 |
|------|------|------|----------|
| 2-3个月后 | 评估Prometheus指标监控 | 基于实际运维需求决定 | OpenTelemetry_vs_Jaeger_选择指南.md 5.1节 |
| 6个月后 | 评估Jaeger链路追踪 | 基于系统复杂度决定 | OpenTelemetry_vs_Jaeger_选择指南.md 4.2节 |

**重要说明**：第三阶段的监控扩展遵循"避免过度设计"原则，仅在确实需要时才实施。优先使用轻量级方案，如：
- **指标监控**：先用简单的异常统计，再考虑Prometheus
- **链路追踪**：先用统一的trace_id，再考虑Jaeger可视化

#### 4.1.1 日志服务简化详细方案

**背景分析**：
- 当前logging_service.py共284行，但90%的功能处于闲置状态
- 项目中12个文件直接使用`from loguru import logger`，绕过了统一日志服务
- 存在功能重复：logging_service与RequestContextMiddleware都在做日志记录

**简化策略**：
1. **专注核心配置**：logging_service仅负责loguru的基础配置
2. **移除冗余功能**：删除未使用的结构化日志、业务事件记录等功能
3. **保留trace_id支持**：保留contextvars机制，便于业务代码使用
4. **整合中间件**：在RequestContextMiddleware中设置trace_id到contextvar
5. **保持兼容性**：所有现有API保持不变

**实施细节**：
```python
# 简化后的logging_service.py结构（约100行，包含trace_id支持）
import contextvars

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('trace_id')

class LoggingService:
    def configure(self) -> None:
        """仅做基础loguru配置"""
        logger.remove()
        
        # 文件日志配置
        if self.settings.log_file_enabled:
            logger.add(...)  # 基础配置
        
        # 控制台日志配置  
        if self.settings.log_console_enabled:
            logger.add(...)  # 基础配置

# 保留的便捷trace_id功能
def get_trace_id() -> str | None:
    try:
        return trace_id_var.get()
    except LookupError:
        return None

def get_logger_with_trace():
    """业务代码友好的logger获取"""
    trace_id = get_trace_id()
    return logger.bind(trace_id=trace_id) if trace_id else logger
```

**预期收益**：
- 代码量减少>65%（从284行到约100行，包含实用的trace_id功能）
- 维护成本大幅降低
- 职责边界更清晰
- 业务代码使用trace_id更便捷（contextvars自动传播）
- 完全符合"简单至上"原则，同时保留实用功能

### 4.2 风险控制

#### 4.2.1 技术风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|--------|
| 事务重构引入bug | 中 | 高 | 充分测试，分阶段实施，保留回滚方案 |
| 性能回归 | 低 | 中 | 性能基准测试，读写分离优化 |
| 异常处理遗漏 | 中 | 中 | 代码审查，完善异常测试用例 |

#### 4.2.2 业务风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|--------|
| 功能回归 | 中 | 高 | 完整的回归测试，用户验收测试 |
| 接口兼容性 | 低 | 中 | 保持API响应格式不变 |
| 部署失败 | 低 | 高 | 灰度发布，快速回滚机制 |

### 4.3 质量保证

#### 4.3.1 测试策略
- **单元测试**：所有新增代码覆盖率>90%
- **集成测试**：重点测试事务边界和异常处理
- **性能测试**：确保改进后性能不下降
- **回归测试**：验证现有功能不受影响

#### 4.3.2 代码审查
- **架构审查**：确保符合DDD分层原则
- **代码审查**：双人审查，关注事务处理和异常处理
- **文档审查**：更新技术文档和API文档

## 五、成功标准

### 5.1 技术指标
- ✅ 事务嵌套冲突问题完全解决
- ✅ 所有异常都有trace_id可追踪
- ✅ logging_service代码量减少>65%（从284行到约100行，包含trace_id功能）
- ✅ 错误码规范化覆盖率100%
- ✅ Repository层单元测试覆盖率>95%
- ✅ 读写分离后读操作性能提升>20%

### 5.2 开发体验指标
- ✅ 问题排查时间减少50%
- ✅ 新功能开发无需关心底层事务管理
- ✅ 异常信息定位准确率>95%
- ✅ 开发人员满意度调查>8分

### 5.3 运维指标
- ✅ 生产环境异常率<1%
- ✅ 异常响应时间<2分钟
- ✅ 系统稳定性提升，零由于事务问题导致的故障

## 六、资源需求

### 6.1 人力资源
- **后端开发**：1人，全程参与（7周）
- **测试工程师**：0.5人，配合测试（3周）
- **运维工程师**：0.2人，监控配置支持（1周）

### 6.2 时间资源
- **开发时间**：35人天
- **测试时间**：15人天
- **部署上线**：3人天
- **总计**：约53人天

### 6.3 技术资源
- 无需额外硬件资源
- 无需引入新的中间件
- 基于现有技术栈进行优化

## 七、长期规划

### 7.1 持续改进
- **3个月后评估**：根据实际使用情况决定是否引入Prometheus监控
- **6个月后评估**：根据系统复杂度决定是否引入Jaeger链路追踪
- **1年后评估**：考虑是否需要更复杂的可观测性方案

### 7.2 技术演进
- **保持技术栈简洁**：不盲目追求新技术
- **关注业务价值**：技术改进服务于业务目标
- **团队能力建设**：通过改进过程提升团队技术水平

## 八、总结

本改进计划立足于MaaS系统的实际情况，遵循"简单至上、渐进改进"的原则，重点解决事务管理和异常处理两个核心痛点。通过7周的分阶段实施，预期能够：

1. **彻底解决事务嵌套冲突**，提升系统稳定性
2. **完善异常处理和追踪能力**，大幅提升问题排查效率  
3. **明确架构分层职责**，提高代码可维护性
4. **建立基础监控能力**，为后续运维奠定基础

同时避免了过度工程化的陷阱，没有引入不必要的复杂性，完全符合小到中型系统的发展需求。

---

## 📚 完整的文档体系

```
MaaS后端系统改进计划.md (总体规划)
├── 事务管理重构方案.md (详细的事务管理重构指南)
├── request_id重构为trace_id方案.md (Request ID统一重构方案)
├── 简化版异常处理最佳实践.md (异常处理优化方案)  
├── OpenTelemetry_vs_Jaeger_选择指南.md (可观测性工具选择)
└── 后端系统分析报告.md (问题分析基础)
```

---

**文档版本**：v1.2  
**创建时间**：2025年1月  
**最后更新**：2025年1月（调整改进方案顺序：异常处理优先，事务管理和DDD优化其次）  
**负责人**：后端技术团队