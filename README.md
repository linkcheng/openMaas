# OpenMaaS

一个基于微服务架构的多即服务(Multi-as-a-Service)平台，采用前后端分离设计。

## 项目架构

```
openMaas/
├── maas-web/           # Vue 3 + TypeScript 前端应用
└── maas-server/        # Python FastAPI 后端服务(DDD架构)
```

## 技术栈

### 前端 (maas-web)

- **Vue 3** + Composition API
- **TypeScript** 类型检查
- **Vite** 构建工具 (rolldown-vite)
- **Vue Router 4** 路由管理
- **Pinia 3** 状态管理
- **Vitest** 单元测试
- **Playwright** E2E测试
- **ESLint + Oxlint** 代码检查
- **Prettier** 代码格式化

### 后端 (maas-server)

- **Python 3.11+** 编程语言
- **FastAPI** Web框架
- **SQLAlchemy 2.0** ORM框架
- **PostgreSQL** 主数据库
- **Redis** 缓存和会话存储
- **Milvus** 向量数据库
- **Celery** 异步任务处理
- **uv** 包管理器
- **Ruff** 代码检查
- **Black** 代码格式化
- **MyPy** 静态类型检查
- **Pytest** 测试框架

## 快速开始

### 前端开发

```bash
cd maas-web
npm install
npm run dev
```

### 后端开发

```bash
cd maas-server
uv sync
uv run uvicorn src.main:app --reload
```

## 开发规范

- **架构模式**: 领域驱动设计(DDD) + 微服务架构
- **开发方法论**: 测试驱动开发(TDD)
- **代码风格**: Google 代码规范
- **版本控制**: GitOps 工作流

## 许可证

[添加许可证信息]
