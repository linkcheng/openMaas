# OpenMaaS

<div align="center">

🚀 **企业级大模型即服务平台** - 基于微服务架构和领域驱动设计(DDD)构建的现代化 AI 服务平台

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

[功能特性](#-核心特性) • [快速开始](#-快速开始) • [开发指南](#-开发指南) • [API 文档](#-api文档)

</div>

This is a vibe coding project, by Claude Code, Kiro and etc.

## ✨ 核心特性

### 🤖 AI 能力平台

- **多模型支持** - 支持主流开源大模型(Llama、ChatGLM、Qwen、Baichuan 等)
- **模型微调** - 提供 LoRA、QLoRA、P-Tuning 等高效微调算法
- **模型推理** - 高性能推理服务，支持流式输出和批量处理
- **模型管理** - 完整的模型生命周期管理和版本控制

### 📚 知识服务

- **知识库构建** - RAG 检索增强生成，构建企业专属知识库
- **文档处理** - 支持多格式文档解析和向量化存储
- **智能检索** - 基于语义相似度的智能文档检索
- **知识图谱** - 实体关系抽取和知识图谱构建

### 🎯 应用构建

- **聊天机器人** - 快速构建智能客服和助手应用
- **文档问答** - 企业文档智能问答系统
- **工作流编排** - 可视化 AI 工作流设计和执行
- **API 集成** - 丰富的 API 接口和 SDK 支持

### 🔐 企业级特性

- **安全认证** - JWT + RBAC 权限管理，支持国密算法
- **审计追踪** - 完整的操作审计和合规管理
- **多租户** - 企业级多租户架构和资源隔离
- **监控运维** - 全面的性能监控和运维管理工具

## 🏗️ 系统架构

本平台采用前后端分离的微服务架构，基于领域驱动设计(DDD)原则构建：

### 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 前端应用层                             │
├─────────────────────────────────────────────────────────────┤
│    Vue 3 + TypeScript + Element Plus + Pinia               │
│    认证页面 | 仪表盘 | 用户管理 | 权限管理 | 审计日志          │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────┐
│                   ⚡ 后端服务层                              │
├─────────────────────────────────────────────────────────────┤
│  认证服务  │  用户服务  │  权限服务  │  审计服务  │  配置服务   │
│  FastAPI + SQLAlchemy + PostgreSQL + Redis + 国密加密       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   🛠️ 基础设施层                              │
├─────────────────────────────────────────────────────────────┤
│ PostgreSQL │ Redis │ Nginx │ Docker │ 监控告警 │ 日志收集      │
│ 主数据库   │ 缓存  │反向代理│ 容器化 │Prometheus│ ELK Stack    │
└─────────────────────────────────────────────────────────────┘
```

### DDD 分层架构

后端服务采用领域驱动设计，分为四个核心层次：

| 层次               | 职责       | 包含内容                         |
| ------------------ | ---------- | -------------------------------- |
| **Interface**      | 接口适配层 | REST API、控制器、路由定义       |
| **Application**    | 应用服务层 | 用例编排、业务流程、DTO 转换     |
| **Domain**         | 领域核心层 | 实体、值对象、领域服务、仓储接口 |
| **Infrastructure** | 基础设施层 | 数据访问、外部服务、配置管理     |

## 🛠️ 技术栈

### 前端 (maas-web)

- **Vue 3.5+** + Composition API + TypeScript 5.8+
- **Element Plus 2.10+** - UI 组件库 + 响应式设计
- **Vite (rolldown-vite)** - 构建工具 + 开发服务器
- **Pinia 3** - 状态管理 + Vue Router 4 路由
- **ESLint 9 + Oxlint** - 代码检查 + Prettier 格式化
- **Vitest 3** - 单元测试 + Playwright E2E 测试

### 后端 (maas-server)

- **Python 3.11+** + 严格类型注解 + 异步编程
- **FastAPI 0.115+** - Web 框架 + 自动 API 文档
- **SQLAlchemy 2.0** - ORM + Alembic 数据库迁移
- **PostgreSQL 15+** - 主数据库 + Redis 7+ 缓存
- **uv** - 包管理器 + 依赖解析工具
- **Ruff + Black + MyPy** - 代码检查、格式化、类型检查
- **Pytest 8.3+** - 测试框架 + Coverage 覆盖率

### 安全 & 监控

- **国密算法** - SM2/SM3/SM4 加密算法支持
- **JWT + RBAC** - 用户认证 + 基于角色的权限控制
- **审计日志** - 完整的操作记录和合规管理

## 📋 环境要求

### 开发环境

- **前端开发**:
  - Node.js >= 18.0 (推荐 20.x LTS)
  - npm >= 9.0 或 pnpm >= 8.0
- **后端开发**:
  - Python >= 3.11 (推荐 3.12)
  - uv 包管理器

### 基础设施

- **数据库**: PostgreSQL >= 15.0
- **缓存**: Redis >= 7.0
- **容器化**: Docker >= 20.10 + Docker Compose >= 2.0

## 🚀 快速开始

### 环境准备

- **Node.js** >= 18.0 (推荐 20.x LTS)
- **Python** >= 3.11 (推荐 3.12)
- **PostgreSQL** >= 15.0
- **Redis** >= 7.0

### 一键启动

#### 1. 启动基础服务

```bash
# 使用 Docker 启动数据库和缓存
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
docker run -d --name redis -p 6379:6379 redis:7
```

#### 2. 后端服务

```bash
cd maas-server

# 安装 uv 包管理器 (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖并启动
uv sync
cp .env.example .env
uv run alembic upgrade head
PYTHONPATH=src uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 前端应用

```bash
cd maas-web

# 安装依赖并启动
npm install
cp .env.example .env.development
npm run dev
```

#### 4. 访问应用

- **前端应用**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 在线 API 文档

启动后端服务后，可以通过以下地址访问完整的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔧 开发指南

### 代码质量检查

```bash
# 前端代码检查
cd maas-web
npm run type-check     # TypeScript 类型检查
npm run lint          # ESLint + Oxlint 代码检查
npm run format        # Prettier 代码格式化
npm run test:unit     # 单元测试

# 后端代码检查
cd maas-server
uv run ruff check src --fix    # 代码风格检查和自动修复
uv run mypy src               # MyPy 类型检查
uv run black src/             # Black 代码格式化
uv run pytest               # 单元测试和集成测试
```

### 数据库管理

```bash
cd maas-server

# 创建新的数据库迁移
uv run alembic revision --autogenerate -m "描述变更内容"

# 执行数据库迁移
uv run alembic upgrade head

# 回滚到上一个版本
uv run alembic downgrade -1

# 查看迁移历史
uv run alembic history
```

### 开发规范

- 遵循 **PEP 8** Python 代码规范
- 使用 **Conventional Commits** 提交格式
- 100% TypeScript 类型覆盖
- 新功能必须包含测试用例
- API 变更需更新文档

## 🏭 生产部署

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 仅构建镜像
docker-compose build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 环境配置

生产环境需要配置以下环境变量：

```env
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0

# 安全配置
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
SM2_PRIVATE_KEY=your-sm2-private-key

# 应用配置
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
```

## 🤝 贡献指南

### 开发流程

1. **Fork 项目** 并创建功能分支
2. **提交代码** 遵循 Conventional Commits 规范
3. **运行测试** 确保所有测试通过
4. **创建 PR** 并详细描述变更内容

### 提交格式

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**类型(type)**:

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档变更
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建或工具变更

## 📄 许可证

本项目采用 **Apache License 2.0** 开源许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- 📧 **邮件**: linkcheng1992@gmail.com
- 🐛 **Issue**: [GitHub Issues](https://github.com/your-org/openmaas/issues)
- 💡 **讨论**: [GitHub Discussions](https://github.com/your-org/openmaas/discussions)

---

<div align="center">

⭐ **如果这个项目对您有帮助，请给我们一个 Star！**

🚀 **现代化企业级认证授权平台，助力企业数字化转型**

[⬆ 回到顶部](#openmaas)

</div>
