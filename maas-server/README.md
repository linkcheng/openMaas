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

## 数据库迁移

```bash
# 生成迁移
uv run alembic revision --autogenerate -m "描述"

# 执行迁移
uv run alembic upgrade head

# 回滚迁移
uv run alembic downgrade -1
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
