# MaaS Server 后端服务

<div align="center">

🚀 **OpenMaaS 平台后端服务** - 基于 FastAPI 和领域驱动设计(DDD)构建的企业级大模型服务后端

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE)

[架构设计](#-架构设计) • [快速开始](#-快速开始) • [开发指南](#-开发指南) • [API 文档](#-api-文档) • [数据库管理](#-数据库管理)

</div>

## ✨ 核心特性

- 🏗️ **DDD 架构** - 领域驱动设计，高内聚低耦合
- ⚡ **高性能** - FastAPI + 异步编程，支持高并发
- 🔒 **企业级安全** - JWT 认证、RBAC 权限、国密算法
- 📊 **完整监控** - 性能监控、日志管理、健康检查
- 🧪 **测试驱动** - 完整的单元测试和集成测试
- 🔄 **CI/CD 就绪** - 自动化测试、代码质量检查
- 🛡️ **数据安全** - 数据加密、审计追踪、合规管理
- 🚀 **可扩展性** - 微服务架构、容器化部署

## 🛠️ 技术栈

### 核心框架

- **Python 3.11+** - 现代 Python 特性 + 严格类型注解
- **FastAPI 0.115+** - 高性能 Web 框架 + 自动 API 文档
- **SQLAlchemy 2.0** - 现代 ORM + 异步支持
- **Alembic 1.14+** - 数据库迁移管理
- **Pydantic 2.10+** - 数据验证和序列化

### 数据存储

- **PostgreSQL 15+** - 主数据库 + ACID 事务
- **Redis 7+** - 缓存 + 会话存储 + 消息队列
- **Milvus 2.5+** - 向量数据库 + 相似度检索

### 开发工具

- **uv** - 现代 Python 包管理器
- **Ruff 0.4+** - 现代化代码检查工具
- **Black 24.10+** - 代码格式化
- **MyPy 1.13+** - 静态类型检查
- **Pytest 8.3+** - 测试框架

### 安全加密

- **JWT** - 认证令牌
- **国密算法** - SM2/SM3/SM4 加密算法
- **Cryptography** - 密码学库
- **UUID7** - 时间有序的唯一标识符

### 异步处理

- **Celery 5.4+** - 分布式任务队列
- **asyncpg 0.30+** - 异步 PostgreSQL 驱动
- **httpx 0.28+** - 异步 HTTP 客户端

## 🏗️ 架构设计

采用领域驱动设计(DDD)分层架构，实现高内聚低耦合：

```
src/
├── shared/                  # 🔧 共享组件层
│   ├── domain/             #   共享领域对象(值对象、异常等)
│   │   ├── base.py         #   基础领域模型
│   │   └── initializer.py  #   领域初始化器
│   ├── application/        #   共享应用层(异常、响应)
│   │   ├── exceptions.py   #   应用异常定义
│   │   └── response.py     #   统一响应格式
│   ├── infrastructure/     #   共享基础设施(数据库、缓存等)
│   │   ├── database.py     #   数据库连接管理
│   │   ├── cache.py        #   Redis 缓存服务
│   │   ├── crypto_service.py #  加密服务(国密)
│   │   ├── logging_service.py # 日志服务
│   │   ├── health_check.py #   健康检查
│   │   └── batch_operations.py # 批量操作
│   └── interface/          #   共享接口定义(中间件、装饰器等)
│       ├── auth_middleware.py # 认证中间件
│       └── dependencies.py #   依赖注入
├── user/                   # 👤 用户管理领域
│   ├── domain/             #   用户聚合根、实体、值对象
│   │   ├── models.py       #   用户领域模型
│   │   └── repositories.py #   用户仓储接口
│   ├── application/        #   用户应用服务、命令处理
│   │   ├── services.py     #   用户应用服务
│   │   ├── auth_service.py #   认证服务
│   │   └── schemas.py      #   数据传输对象
│   ├── infrastructure/     #   用户数据访问、外部服务
│   │   ├── models.py       #   SQLAlchemy 模型
│   │   ├── repositories.py #   仓储实现
│   │   └── data_initializer.py # 数据初始化
│   └── interface/          #   用户API控制器、DTO
│       ├── auth_controller.py # 认证控制器
│       └── user_controller.py # 用户控制器
├── audit/                  # 📋 审计日志领域
│   ├── domain/             #   审计聚合根、实体
│   ├── application/        #   审计应用服务
│   ├── infrastructure/     #   审计数据存储
│   ├── interface/          #   审计API接口
│   └── shared/             #   审计共享组件
│       ├── config.py       #   审计配置
│       ├── decorators.py   #   审计装饰器
│       └── middleware.py   #   审计中间件
├── model/                  # 🤖 模型管理领域
├── inference/              # ⚡ 推理服务领域
├── finetune/              # 🔧 微调服务领域
├── knowledge/             # 📚 知识库领域
├── apps/                  # 📱 应用管理领域
└── config/                # ⚙️ 配置管理
    ├── settings.py         #   应用配置
    ├── schemas.py          #   配置模式
    ├── env_utils.py        #   环境变量工具
    └── config_utils.py     #   配置工具
```

### 领域服务职责

| 领域服务      | 核心职责     | 主要功能                                     |
| ------------- | ------------ | -------------------------------------------- |
| **User**      | 用户认证授权 | 注册登录、权限管理、配额控制、审计日志       |
| **Audit**     | 审计追踪     | 操作记录、合规管理、日志分析、风险监控       |
| **Model**     | 模型仓库管理 | 模型上传、版本控制、元数据管理、生命周期管理 |
| **Inference** | 模型推理服务 | API 推理、流式输出、性能监控、负载均衡       |
| **Finetune**  | 模型微调训练 | 训练任务、进度监控、模型评估、资源调度       |
| **Knowledge** | 知识库构建   | 文档处理、向量化、RAG 问答、知识图谱         |
| **Apps**      | 应用构建发布 | 应用创建、配置管理、集成服务、工作流编排     |

## 📋 环境要求

### 基础环境

- **Python** >= 3.11 (推荐 3.12)
- **PostgreSQL** >= 15.0
- **Redis** >= 7.0
- **操作系统**: Linux/macOS (兼容 Windows)

### 可选组件

- **Docker** >= 20.10 (容器化部署)
- **Milvus** >= 2.5 (向量数据库)
- **RabbitMQ** >= 3.12 (消息队列，可选)

## 🚀 快速开始

### 1. 安装 uv 包管理器

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 2. 项目初始化

```bash
# 克隆项目
git clone <repository-url>
cd openMaas/maas-server

# 安装依赖（自动创建虚拟环境）
uv sync

# 或安装开发依赖
uv sync --extra dev
```

### 3. 环境配置

```bash
# 创建环境配置文件
cp .env.template .env

# 编辑环境变量
vim .env
```

**主要环境变量**：

```bash
# 应用配置
MAAS_DEBUG=true
MAAS_ENVIRONMENT=development
MAAS_HOST=0.0.0.0
MAAS_PORT=8000

# 数据库配置
MAAS_DATABASE_URL=postgresql+asyncpg://maas:maas@localhost:5432/maas_dev
MAAS_DATABASE_URL_SYNC=postgresql://maas:maas@localhost:5432/maas_dev

# Redis配置
MAAS_REDIS_URL=redis://localhost:6379/0

# JWT配置
MAAS_SECRET_KEY=your-secret-key-change-in-production
MAAS_ACCESS_TOKEN_EXPIRE_MINUTES=30
MAAS_REFRESH_TOKEN_EXPIRE_DAYS=7

# 安全配置
MAAS_ENABLE_CORS=true
MAAS_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

# 日志配置
MAAS_LOG_LEVEL=INFO
MAAS_LOG_FORMAT=detailed

# 审计配置
MAAS_AUDIT_ENABLED=true
MAAS_AUDIT_BATCH_SIZE=100
MAAS_AUDIT_FLUSH_INTERVAL=5
```

### 4. 数据库初始化

```bash
# 启动 PostgreSQL 服务
brew services start postgresql  # macOS
sudo systemctl start postgresql # Linux

# 创建数据库和用户
psql postgres -c "CREATE USER maas WITH PASSWORD 'maas';"
psql postgres -c "CREATE DATABASE maas_dev OWNER maas;"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE maas_dev TO maas;"

# 运行数据库迁移
uv run alembic upgrade head
```

### 5. 启动服务

```bash
# 启动开发服务器（推荐）
PYTHONPATH=src uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 或使用脚本命令
uv run python -m src.main

# 或使用 hatch
hatch run python -m src.main
```

### 6. 验证安装

```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs

# 检查数据库连接
curl http://localhost:8000/health/db

# 检查 Redis 连接
curl http://localhost:8000/health/redis
```

## 💻 开发命令

### 包管理

```bash
# 安装依赖
uv sync

# 添加运行时依赖
uv add fastapi

# 添加开发依赖
uv add pytest --group dev

# 更新依赖
uv sync --upgrade

# 查看依赖树
uv tree
```

### 代码质量

```bash
# 代码格式化
uv run black src/ tests/

# 代码检查和修复
uv run ruff check src/ tests/ --fix

# 类型检查
uv run mypy src/

# 运行所有质量检查
uv run ruff check src/ && uv run mypy src/ && uv run pytest
```

### 使用 Hatch 环境 (推荐)

```bash
# 运行测试
hatch run test

# 格式化代码
hatch run format

# 类型检查
hatch run type-check

# 运行所有检查
hatch run all

# 生成覆盖率报告
hatch run test-cov
hatch run cov-html
```

### 测试命令

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/unit/user/test_services.py

# 运行特定测试标记
uv run pytest -m "not slow"

# 生成覆盖率报告
uv run pytest --cov=src --cov-report=html

# 并行测试
uv run pytest -n auto
```

### 服务器运行

```bash
# 开发服务器（热重载）
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 生产服务器（多进程）
uv run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker

# 使用环境变量
MAAS_DEBUG=true PYTHONPATH=src uv run uvicorn src.main:app --reload
```

## 🗃️ 数据库管理

### Alembic 迁移

**什么是 Alembic**：
Alembic 是 SQLAlchemy 官方的数据库迁移工具，用于管理数据库结构的版本控制。

**核心功能**：

- 数据库版本控制和迁移历史管理
- 自动生成迁移脚本
- 支持多环境迁移（开发/测试/生产）
- 与 SQLAlchemy 深度集成

### 日常迁移操作

```bash
# 查看当前版本
uv run alembic current

# 查看迁移历史
uv run alembic history --verbose

# 升级到最新版本
uv run alembic upgrade head

# 升级到指定版本
uv run alembic upgrade <revision_id>

# 回滚一个版本
uv run alembic downgrade -1

# 回滚到指定版本
uv run alembic downgrade <revision_id>
```

### 创建新迁移

```bash
# 自动生成迁移（推荐）
uv run alembic revision --autogenerate -m "添加新的业务模型"

# 手动创建迁移
uv run alembic revision -m "手动创建的特殊迁移"

# 检查迁移文件
ls alembic/versions/
```

### 迁移最佳实践

1. **总是先备份生产数据库**
2. **在开发环境测试迁移**
3. **使用描述性的迁移消息**
4. **检查自动生成的迁移脚本**
5. **避免直接修改已应用的迁移文件**

## 📁 项目结构详解

### 共享组件层 (shared/)

**领域层** (`shared/domain/`):

- `base.py` - 基础领域模型和值对象
- `initializer.py` - 领域模型初始化器

**应用层** (`shared/application/`):

- `exceptions.py` - 应用层异常定义
- `response.py` - 统一 API 响应格式

**基础设施层** (`shared/infrastructure/`):

- `database.py` - 数据库连接和会话管理
- `cache.py` - Redis 缓存服务封装
- `crypto_service.py` - 加密服务（支持国密算法）
- `logging_service.py` - 结构化日志服务
- `health_check.py` - 健康检查服务
- `batch_operations.py` - 批量操作工具

**接口层** (`shared/interface/`):

- `auth_middleware.py` - JWT 认证中间件
- `dependencies.py` - FastAPI 依赖注入

### 用户管理领域 (user/)

**领域模型** (`user/domain/`):

```python
# models.py - 用户聚合根
class User:
    """用户聚合根"""
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        self.is_active = True

    def change_password(self, new_password: str) -> None:
        """修改密码（领域逻辑）"""
        # 密码复杂度验证等业务规则
        pass
```

**应用服务** (`user/application/`):

```python
# services.py - 用户应用服务
class UserService:
    """用户应用服务"""

    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """创建用户"""
        # 应用层业务逻辑
        pass

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        # 认证逻辑
        pass
```

### 审计日志领域 (audit/)

**审计配置** (`audit/shared/config.py`):

```python
class AuditConfig:
    """审计配置"""
    enabled: bool = True
    batch_size: int = 100
    flush_interval: int = 5  # 秒
    retention_days: int = 90
```

**审计装饰器** (`audit/shared/decorators.py`):

```python
@audit_log(action="user.login", resource="user")
async def login_user(username: str, password: str):
    """自动记录用户登录审计日志"""
    pass
```

## 📖 API 文档

### 自动生成文档

启动服务后访问：

- **OpenAPI 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 主要 API 端点

**认证接口**:

```
POST /api/v1/auth/login      # 用户登录
POST /api/v1/auth/register   # 用户注册
POST /api/v1/auth/refresh    # 刷新令牌
POST /api/v1/auth/logout     # 用户登出
```

**用户管理**:

```
GET  /api/v1/users/profile   # 获取用户资料
PUT  /api/v1/users/profile   # 更新用户资料
POST /api/v1/users/password  # 修改密码
GET  /api/v1/users/quota     # 查看配额
```

**管理员接口**:

```
GET  /api/v1/admin/users     # 用户列表
POST /api/v1/admin/users     # 创建用户
PUT  /api/v1/admin/users/{id} # 更新用户
DELETE /api/v1/admin/users/{id} # 删除用户
```

**审计日志**:

```
GET  /api/v1/audit/logs      # 审计日志列表
GET  /api/v1/audit/logs/{id} # 审计日志详情
GET  /api/v1/audit/stats     # 审计统计
```

**健康检查**:

```
GET  /health                 # 应用健康状态
GET  /health/db              # 数据库连接状态
GET  /health/redis           # Redis 连接状态
GET  /metrics                # Prometheus 指标
```

## 🛠️ 开发指南

### 添加新的领域服务

1. **创建领域结构**

```bash
mkdir -p src/new_domain/{domain,application,infrastructure,interface}
touch src/new_domain/__init__.py
touch src/new_domain/domain/{__init__.py,models.py,repositories.py}
touch src/new_domain/application/{__init__.py,services.py,schemas.py}
touch src/new_domain/infrastructure/{__init__.py,models.py,repositories.py}
touch src/new_domain/interface/{__init__.py,controller.py}
```

2. **定义领域模型**

```python
# src/new_domain/domain/models.py
from dataclasses import dataclass
from typing import Optional
from shared.domain.base import Entity

@dataclass
class NewEntity(Entity):
    """新领域实体"""
    name: str
    description: Optional[str] = None

    def update_name(self, new_name: str) -> None:
        """更新名称（领域逻辑）"""
        if not new_name.strip():
            raise ValueError("名称不能为空")
        self.name = new_name
```

3. **实现仓储接口**

```python
# src/new_domain/domain/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional
from .models import NewEntity

class NewEntityRepository(ABC):
    """新实体仓储接口"""

    @abstractmethod
    async def save(self, entity: NewEntity) -> NewEntity:
        """保存实体"""
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: str) -> Optional[NewEntity]:
        """根据ID查找实体"""
        pass
```

4. **注册路由**

```python
# src/main.py 中添加
from new_domain.interface.controller import router as new_domain_router

app.include_router(new_domain_router, prefix="/api/v1/new-domain")
```

### 认证和权限

**JWT 认证**:

```python
from shared.interface.dependencies import get_current_user
from user.domain.models import User

@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """需要认证的端点"""
    return {"user_id": current_user.id}
```

**权限检查**:

```python
from shared.interface.dependencies import require_permission

@router.post("/admin-only")
@require_permission("admin:write")
async def admin_only_endpoint():
    """只有管理员可以访问"""
    return {"message": "Admin access granted"}
```

### 审计日志集成

```python
from audit.shared.decorators import audit_log

@audit_log(action="model.deploy", resource="model")
async def deploy_model(model_id: str, config: DeployConfig):
    """部署模型（自动记录审计日志）"""
    # 业务逻辑
    pass
```

### 异常处理

```python
from shared.application.exceptions import BusinessException

class UserNotFoundError(BusinessException):
    """用户不存在异常"""
    def __init__(self, user_id: str):
        super().__init__(f"用户 {user_id} 不存在", error_code="USER_NOT_FOUND")

# 控制器中使用
async def get_user(user_id: str):
    user = await user_service.get_by_id(user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return user
```

## 🧪 测试

### 测试结构

```
tests/
├── unit/                    # 单元测试
│   ├── user/               #   用户模块测试
│   │   ├── test_models.py  #   领域模型测试
│   │   ├── test_services.py #  应用服务测试
│   │   └── test_controllers.py # 控制器测试
│   ├── audit/              #   审计模块测试
│   └── shared/             #   共享组件测试
├── integration/            # 集成测试
│   ├── test_database.py    #   数据库集成测试
│   ├── test_api.py         #   API 集成测试
│   └── test_auth.py        #   认证集成测试
└── conftest.py             # 测试配置和夹具
```

### 测试命令

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest tests/unit/

# 运行集成测试
uv run pytest tests/integration/

# 运行特定标记的测试
uv run pytest -m "not slow"

# 生成覆盖率报告
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### 测试示例

**单元测试**:

```python
# tests/unit/user/test_models.py
import pytest
from user.domain.models import User

class TestUser:
    """用户模型测试"""

    def test_create_user(self):
        """测试创建用户"""
        user = User(username="test", email="test@example.com")
        assert user.username == "test"
        assert user.email == "test@example.com"
        assert user.is_active is True

    def test_change_password(self):
        """测试修改密码"""
        user = User(username="test", email="test@example.com")
        user.change_password("new_password")
        # 验证密码修改逻辑
```

**集成测试**:

```python
# tests/integration/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """测试登录成功"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
```

### 测试配置

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    """事件循环夹具"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """HTTP 客户端夹具"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_db():
    """测试数据库夹具"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # 创建表结构
    yield engine
    await engine.dispose()
```

## 🚀 部署

### Docker 部署

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --frozen --no-cache

# 复制源代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV MAAS_ENVIRONMENT=production

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MAAS_DATABASE_URL=postgresql+asyncpg://maas:maas@db:5432/maas
      - MAAS_REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: maas
      POSTGRES_USER: maas
      POSTGRES_PASSWORD: maas
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 生产环境部署

```bash
# 构建镜像
docker build -t maas-server:latest .

# 启动服务
docker-compose up -d

# 运行迁移
docker-compose exec app uv run alembic upgrade head

# 查看日志
docker-compose logs -f app

# 健康检查
curl http://localhost:8000/health
```

### 环境变量配置

**生产环境** (`.env.production`):

```bash
MAAS_ENVIRONMENT=production
MAAS_DEBUG=false
MAAS_SECRET_KEY=your-production-secret-key-very-long-and-secure
MAAS_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/maas_prod
MAAS_REDIS_URL=redis://localhost:6379/0
MAAS_LOG_LEVEL=INFO
MAAS_CORS_ORIGINS=["https://your-domain.com"]
```

## 🛠️ 开发工具集成

### Pre-commit 钩子

```bash
# 安装 pre-commit 钩子
uv run pre-commit install

# 手动运行所有检查
uv run pre-commit run --all-files

# 配置文件 .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
```

### VS Code 配置

**.vscode/settings.json**:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.py[cod]": true
  }
}
```

### 推荐扩展

- **Python** - Python 语言支持
- **Pylance** - Python 语言服务器
- **Black Formatter** - 代码格式化
- **autoDocstring** - 自动生成文档字符串
- **Thunder Client** - API 测试客户端

## 🔧 监控和运维

### 健康检查

```python
# 健康检查端点
@app.get("/health")
async def health_check():
    """应用健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@app.get("/health/db")
async def db_health_check():
    """数据库健康检查"""
    try:
        await database.execute("SELECT 1")
        return {"status": "healthy", "service": "database"}
    except Exception as e:
        return {"status": "unhealthy", "service": "database", "error": str(e)}
```

### 日志管理

```python
from loguru import logger

# 结构化日志配置
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            "level": "INFO",
        },
        {
            "sink": "logs/app.log",
            "rotation": "10 MB",
            "retention": "7 days",
            "level": "DEBUG",
        }
    ]
)

# 使用日志
logger.info("User {user_id} logged in", user_id=user.id)
logger.error("Database connection failed", error=str(e))
```

### 性能监控

集成 Prometheus 指标：

```python
from prometheus_client import Counter, Histogram, generate_latest

# 定义指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """指标收集中间件"""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(duration)

    return response

@app.get("/metrics")
async def metrics():
    """Prometheus 指标端点"""
    return Response(generate_latest(), media_type="text/plain")
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请按照以下步骤参与项目：

### 开发流程

1. **Fork 项目并创建分支**

```bash
git clone https://github.com/your-username/openMaas.git
cd openMaas/maas-server
git checkout -b feature/your-feature-name
```

2. **设置开发环境**

```bash
uv sync --extra dev
uv run pre-commit install
```

3. **开发和测试**

```bash
# 运行测试
hatch run test

# 代码质量检查
hatch run all

# 启动开发服务器
PYTHONPATH=src uv run uvicorn src.main:app --reload
```

4. **提交代码**

```bash
git add .
git commit -m "feat: 添加新的模型管理功能"
git push origin feature/your-feature-name
```

### 代码规范

**提交信息规范** (遵循 [Conventional Commits](https://conventionalcommits.org/)):

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 其他修改

**代码风格**:

- 使用 Black 进行代码格式化
- 使用 Ruff 进行代码检查
- 使用 MyPy 进行类型检查
- 遵循 PEP 8 和 Google 风格文档字符串

**测试要求**:

- 新功能必须包含单元测试
- 测试覆盖率不低于 85%
- 集成测试覆盖关键业务流程

## 📄 许可证

本项目采用 **Apache License 2.0** 开源许可证。

**许可证摘要**:

- ✅ 商业使用
- ✅ 修改
- ✅ 分发
- ✅ 专利使用
- ✅ 私人使用
- ❌ 责任
- ❌ 保修

查看 [LICENSE](../LICENSE) 文件了解完整许可证条款。

### 第三方依赖

项目使用的主要开源依赖：

- FastAPI (MIT License)
- SQLAlchemy (MIT License)
- Pydantic (MIT License)
- PostgreSQL (PostgreSQL License)
- Redis (BSD License)
- 更多信息请查看 [THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md)

## 📞 支持与反馈

### 获取帮助

- 📚 **文档**: [项目文档](../docs/)
- 🐛 **问题报告**: [GitHub Issues](https://github.com/your-org/openmaas/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/your-org/openmaas/discussions)
- 📧 **邮件联系**: linkcheng1992@gmail.com

### 问题反馈模板

**功能请求**:

```markdown
**功能描述**
简要描述您希望添加的功能。

**使用场景**
描述这个功能的具体使用场景。

**预期实现**
描述您期望的功能实现方式。

**替代方案**
描述您考虑过的其他解决方案。
```

**Bug 报告**:

```markdown
**描述问题**
清楚简洁地描述遇到的问题。

**复现步骤**

1. 运行命令 '...'
2. 发送请求 '....'
3. 查看响应 '....'
4. 看到错误

**环境信息**

- Python 版本: [如 3.11.5]
- FastAPI 版本: [如 0.115.0]
- 数据库: [如 PostgreSQL 15.4]
- 操作系统: [如 Ubuntu 22.04]
```

---

⭐ **如果这个项目对你有帮助，请给我们一个 Star！**

🚀 **让我们一起构建更好的大模型服务平台！**

💖 **感谢所有贡献者的支持！**
