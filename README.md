# OpenMaaS

一个基于微服务架构的模型即服务(Model-as-a-Service)平台，采用前后端分离设计。

This is a vibe coding project.

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
- **Playwright** E2E 测试
- **ESLint + Oxlint** 代码检查
- **Prettier** 代码格式化

### 后端 (maas-server)

- **Python 3.11+** 编程语言
- **FastAPI** Web 框架
- **SQLAlchemy 2.0** ORM 框架
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
cd src
uv run uvicorn main:app --reload
```

## 开发规范

- **架构模式**: 领域驱动设计(DDD) + 微服务架构
- **开发方法论**: 测试驱动开发(TDD)
- **代码风格**: Google 代码规范
- **版本控制**: GitOps 工作流

## 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献指南。

### 快速开始贡献

1. Fork 项目到您的 GitHub 账户
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 许可证协议

通过向本项目提交贡献，您同意您的贡献将在 Apache License 2.0 下发布。

## 许可证

本项目使用 Apache License 2.0 开源许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

### 第三方依赖

- 前端依赖许可证信息：[maas-web/THIRD-PARTY-LICENSES.md](maas-web/THIRD-PARTY-LICENSES.md)
- 后端依赖许可证信息：[maas-server/THIRD-PARTY-LICENSES.md](maas-server/THIRD-PARTY-LICENSES.md)

### 许可证合规

项目提供了许可证合规检查工具：

```bash
# 检查所有依赖的许可证合规性
python scripts/check-licenses.py

# 为源代码添加许可证头部
python scripts/add-license-headers.py --dry-run  # 预览
python scripts/add-license-headers.py            # 实际添加
```
