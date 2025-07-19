# MaaS Server

大模型 MaaS 平台后端服务

## 技术栈

- **Python 3.11+**
- **FastAPI** - Web 框架
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和消息队列
- **Milvus** - 向量数据库
- **Celery** - 异步任务队列
- **uv** - Python 包管理器

## 架构设计

采用领域驱动设计(DDD)分层架构：

```
src/
├── shared/                  # 共享组件
│   ├── domain/             # 共享领域对象
│   ├── infrastructure/     # 共享基础设施
│   └── interface/          # 共享接口定义
├── user/                   # 用户管理领域
├── model/                  # 模型管理领域
├── inference/              # 推理服务领域
├── finetune/              # 微调服务领域
├── knowledge/             # 知识库领域
└── apps/                  # 应用管理领域
```

## 开发环境设置

### 先决条件

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) 包管理器

### 安装与启动

```bash
# 同步依赖
uv sync

# 运行开发服务器
uv run uvicorn main:app --reload

# 或者使用主函数
uv run python -m main

# 运行测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=src --cov-report=html
```

### 代码质量检查

```bash
# 代码格式化
uv run black src/

# 代码检查和修复
uv run ruff check src --fix

# 类型检查
uv run mypy src/

# 运行所有检查
uv run ruff check src && uv run mypy src && uv run pytest
```

### 使用 Hatch 环境 (推荐)

```bash
# 使用默认环境运行测试
hatch run test

# 格式化代码
hatch run format

# 运行所有检查
hatch run all

# 类型检查
hatch run type-check
```

## 数据库迁移 (Alembic)

### 什么是 Alembic

Alembic 是一个 Python 数据库迁移工具，专门用于 SQLAlchemy ORM。在 MaaS 项目中，它的作用包括：

- **数据库版本控制** - 管理数据库结构的变更历史
- **迁移管理** - 自动生成数据库表结构变更脚本
- **环境同步** - 确保不同环境间数据库结构的一致性

### 项目配置

**配置文件 (alembic.ini)**
- 数据库连接：`postgresql://admin:123456@localhost:5432/maas_dev`
- 迁移脚本位置：`alembic/` 目录
- 集成了 Black 代码格式化工具

**迁移文件结构**
```
alembic/
├── env.py                           # 环境配置
├── script.py.mako                   # 迁移模板
└── versions/
    ├── 001_initial_user_tables.py   # 初始用户表结构
    └── 002_seed_data.py             # 种子数据
```

### 数据库准备

首次使用需要设置 PostgreSQL 数据库：

```bash
# 安装 PostgreSQL (如果还没安装)
brew install postgresql

# 启动 PostgreSQL 服务
brew services start postgresql

# 创建数据库和用户
psql postgres -c "CREATE USER admin WITH PASSWORD '123456';"
psql postgres -c "CREATE DATABASE maas_dev OWNER admin;"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE maas_dev TO admin;"
```

### 初始化数据库（首次使用）

```bash
# 激活虚拟环境
source .venv/bin/activate

# 升级到最新版本（会执行所有迁移文件）
alembic upgrade head

# 如果表已存在，标记为当前版本
alembic stamp head
```

### 日常操作命令

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history --verbose

# 查看待执行的迁移
alembic show head

# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision_id>

# 回滚一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>
```

### 创建新迁移

#### 方法一：自动生成迁移（推荐）

```bash
# 修改你的 SQLAlchemy 模型后，自动生成迁移文件
alembic revision --autogenerate -m "添加新表或字段的描述"
```

#### 方法二：手动创建迁移

```bash
# 创建空的迁移文件
alembic revision -m "手动创建的迁移描述"
```

### 迁移文件示例

```python
"""添加用户表

Revision ID: 001_initial_user_tables
Revises: 
Create Date: 2025-01-18 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_user_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """创建用户表"""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # 创建索引
    op.create_index('idx_users_username', 'users', ['username'])

def downgrade() -> None:
    """删除用户表"""
    op.drop_table('users')
```

### 当前数据库结构

项目已包含以下表结构：

**001_initial_user_tables.py** - 创建核心用户管理表：
- `users` - 用户基本信息
- `roles` - 角色权限
- `user_roles` - 用户角色关联
- `api_keys` - API 密钥管理
- `user_quotas` - 用户配额限制

**002_seed_data.py** - 初始化数据：
- 创建三个默认角色：admin、developer、user
- 创建默认管理员账户 (admin/Admin123!)
- 设置管理员的权限和配额

### 最佳实践

- **总是先备份数据库**再运行迁移
- **在开发环境测试**迁移后再应用到生产环境
- **使用描述性的迁移消息**，便于理解变更内容
- **检查自动生成的迁移**，确保符合预期
- **团队协作时**，及时同步迁移文件
- **避免直接修改已应用的迁移文件**

### 故障排除

#### 常见问题

1. **导入错误** - 确保 Python 路径配置正确
2. **数据库连接失败** - 检查数据库服务是否启动，连接配置是否正确
3. **表已存在错误** - 使用 `alembic stamp head` 标记当前状态
4. **迁移冲突** - 检查迁移文件的依赖关系

#### 重置迁移历史

```bash
# 删除所有表（谨慎操作）
# 然后重新运行迁移
alembic upgrade head
```

## 项目结构

```
├── src/                    # 源代码
├── tests/                  # 测试代码
├── alembic/               # 数据库迁移
├── pyproject.toml         # 项目配置
├── uv.lock               # 依赖锁文件
└── README.md             # 项目说明
```

## 环境变量

在项目根目录创建 `.env` 文件：

```bash
# 应用配置
MAAS_DEBUG=true
MAAS_ENVIRONMENT=development

# 数据库配置
MAAS_DATABASE_URL=postgresql+asyncpg://maas:maas@localhost:5432/maas
MAAS_DATABASE_URL_SYNC=postgresql://maas:maas@localhost:5432/maas

# Redis配置
MAAS_REDIS_URL=redis://localhost:6379/0

# JWT配置
MAAS_SECRET_KEY=your-secret-key-change-in-production
MAAS_ACCESS_TOKEN_EXPIRE_MINUTES=30

```

## 开发工具

### 预提交钩子

```bash
# 安装预提交钩子
uv run pre-commit install

# 手动运行预提交检查
uv run pre-commit run --all-files
```

### 开发服务器

```bash
# 启动开发服务器（支持热重载）
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 启动多进程生产服务器
uv run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API 文档

启动服务器后，访问：

- **OpenAPI 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 依赖管理

### 添加依赖

```bash
# 添加运行时依赖
uv add fastapi

# 添加开发依赖
uv add pytest --dev

# 添加可选依赖
uv add --optional dev pytest
```

### 更新依赖

```bash
# 更新所有依赖
uv sync --upgrade

# 更新特定依赖
uv sync --upgrade-package fastapi
```

## 测试

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_user.py

# 运行特定测试标记
uv run pytest -m "not slow"

# 运行并生成覆盖率报告
uv run pytest --cov=src --cov-report=html
```

### 测试分类

- `unit`: 单元测试
- `integration`: 集成测试
- `slow`: 慢速测试

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t maas-server .

# 运行容器
docker run -p 8000:8000 maas-server
```

### 生产环境

```bash
# 安装生产依赖
uv sync --no-dev

# 运行生产服务器
uv run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目使用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
