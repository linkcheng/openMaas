# OpenMaaS

<div align="center">

🚀 **企业级大模型即服务平台** - 基于微服务架构和领域驱动设计(DDD)构建的现代化 AI 服务平台

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

[功能特性](#-核心特性) • [快速开始](#-快速开始) • [系统架构](#-系统架构) • [技术文档](#-详细文档) • [部署指南](#-部署)

</div>

This is a vibe coding project, by Cursor, Claude Code and Kiro.

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

### 分层架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     🌐 客户端层                              │
├─────────────────────────────────────────────────────────────┤
│  Web控制台   │   移动App   │   第三方集成   │   开发者API    │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   ⚡ 应用服务层                              │
├─────────────────────────────────────────────────────────────┤
│  用户管理   │   模型服务   │   推理服务   │   知识库服务     │
│  权限控制   │   微调训练   │   应用构建   │   监控运维       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   🛠️ 基础设施层                              │
├─────────────────────────────────────────────────────────────┤
│ PostgreSQL │ Redis │ Milvus │ MinIO │ 消息队列 │ 监控告警     │
│ 关系数据库  │ 缓存  │向量库  │对象存储│ Celery  │ Prometheus  │
└─────────────────────────────────────────────────────────────┘
```

### 微服务架构

采用领域驱动设计(DDD)构建的微服务架构：

| 服务模块       | 技术栈               | 核心功能                     |
| -------------- | -------------------- | ---------------------------- |
| **用户服务**   | FastAPI + PostgreSQL | 用户认证、权限管理、多租户   |
| **模型服务**   | FastAPI + MinIO      | 模型存储、版本管理、元数据   |
| **推理服务**   | FastAPI + GPU        | 模型推理、负载均衡、缓存     |
| **微调服务**   | Celery + GPU         | 模型训练、进度监控、资源调度 |
| **知识库服务** | FastAPI + Milvus     | 文档处理、向量检索、RAG      |
| **应用服务**   | FastAPI + Redis      | 应用构建、工作流编排         |
| **审计服务**   | FastAPI + ES         | 操作日志、审计追踪、合规     |

## 📁 项目结构

```
openMaas/
├── 📱 maas-web/              # Vue 3 + TypeScript 前端应用
│   ├── src/
│   │   ├── views/           # 页面组件 (认证/用户/管理/业务)
│   │   ├── components/      # 可复用组件 (图表/布局/业务)
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── utils/           # 工具函数 (API/加密/通用)
│   │   └── router/          # 路由配置 + 权限守卫
│   ├── tests/               # 单元测试 + E2E 测试
│   └── dist/               # 构建输出
├── 🚀 maas-server/          # Python FastAPI 后端服务
│   ├── src/
│   │   ├── user/           # 👤 用户管理领域
│   │   ├── model/          # 🤖 模型管理领域
│   │   ├── inference/      # ⚡ 推理服务领域
│   │   ├── finetune/       # 🔧 微调服务领域
│   │   ├── knowledge/      # 📚 知识库领域
│   │   ├── apps/           # 📱 应用管理领域
│   │   ├── audit/          # 📋 审计日志领域
│   │   ├── shared/         # 🔧 共享组件层
│   │   └── config/         # ⚙️ 配置管理
│   ├── tests/              # 单元测试 + 集成测试
│   ├── alembic/            # 数据库迁移
│   └── docs/               # API 文档
├── 📚 docs/                 # 项目文档
│   ├── 系统架构设计文档.md
│   ├── 需求详细分析文档.md
│   ├── 数据库设计文档.md
│   ├── API接口设计文档.md
│   └── 部署运维文档.md
├── 🔧 scripts/             # 部署和工具脚本
│   ├── deploy/             # 部署脚本
│   ├── monitoring/         # 监控配置
│   └── backup/             # 备份脚本
├── 🐳 docker/              # 容器化配置
│   ├── docker-compose.yml  # 本地开发环境
│   ├── docker-compose.prod.yml # 生产环境
│   └── Dockerfile.*        # 各服务镜像构建
└── 📄 project/             # 项目配置和资源
    ├── nginx/              # 反向代理配置
    ├── k8s/                # Kubernetes 部署清单
    └── helm/               # Helm Charts
```

## 🛠️ 技术栈

### 前端技术栈 (maas-web)

<table>
<tr>
<td width="50%">

### 后端技术栈 (maas-server)

<table>
<tr>
<td width="50%">

## 📋 环境要求

### 基础环境

- **操作系统**: Linux/macOS (推荐 Ubuntu 22.04+)
- **Docker**: >= 20.10 (容器化部署)
- **Docker Compose**: >= 2.0

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
- **向量数据库**: Milvus >= 2.5.0 (可选)
- **对象存储**: MinIO 或兼容 S3 API (可选)

## 🚀 快速开始

### 方式一：Docker Compose 一键启动 (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/your-org/openmaas.git
cd openmaas

# 2. 启动所有服务
docker-compose up -d

# 3. 等待服务启动并初始化数据库
docker-compose logs -f maas-server

# 4. 访问应用
# 前端应用: http://localhost:5173
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 方式二：本地开发环境

#### 1. 环境准备

```bash
# 启动基础设施 (PostgreSQL + Redis)
docker-compose -f docker-compose.dev.yml up -d db redis

# 或手动安装
brew install postgresql redis  # macOS
sudo apt install postgresql redis-server  # Ubuntu
```

#### 2. 后端服务启动

```bash
cd maas-server

# 安装 uv 包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync --extra dev

# 配置环境变量
cp .env.template .env
vim .env  # 编辑数据库连接等配置

# 初始化数据库
uv run alembic upgrade head

# 启动开发服务器
PYTHONPATH=src uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 前端应用启动

```bash
cd maas-web

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.development
vim .env.development  # 编辑 API 地址等配置

# 启动开发服务器
npm run dev
```

#### 4. 验证安装

```bash
# 健康检查
curl http://localhost:8000/health
curl http://localhost:5173

# 默认管理员账户
# 用户名: admin
# 密码: Admin123!
```

## 🎯 核心功能演示

### 1. 用户管理和权限控制

```bash
# 用户注册
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "email": "demo@example.com", "password": "Demo123!"}'

# 用户登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "Demo123!"}'
```

### 2. 模型管理

```bash
# 获取模型列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/models"

# 模型推理
curl -X POST "http://localhost:8000/api/v1/inference" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "chatglm3-6b", "messages": [{"role": "user", "content": "你好"}]}'
```

### 3. 知识库问答

```bash
# 创建知识库
curl -X POST "http://localhost:8000/api/v1/knowledge/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "企业文档库", "description": "公司内部文档知识库"}'

# 上传文档
curl -X POST "http://localhost:8000/api/v1/knowledge/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "knowledge_base_id=1"

# 知识库问答
curl -X POST "http://localhost:8000/api/v1/knowledge/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"knowledge_base_id": 1, "question": "如何申请年假？"}'
```

## 📖 详细文档

### 架构设计文档

- [🏗️ 系统架构设计](docs/系统架构设计文档.md) - 整体架构和设计理念
- [📊 数据库设计](docs/数据库设计文档.md) - 数据模型和关系设计
- [🔗 API 接口设计](docs/API接口设计文档.md) - RESTful API 设计规范

### 开发指南

- [🎨 前端开发指南](maas-web/README.md) - Vue 3 前端开发完整指南
- [🚀 后端开发指南](maas-server/README.md) - FastAPI 后端开发完整指南
- [🗃️ 数据库管理](docs/数据库管理文档.md) - Alembic 迁移和最佳实践

### 部署运维

- [🐳 Docker 部署](docs/Docker部署文档.md) - 容器化部署指南
- [☸️ Kubernetes 部署](docs/K8s部署文档.md) - 生产环境 K8s 部署
- [📊 监控告警](docs/监控运维文档.md) - 系统监控和告警配置

### 用户手册

- [📘 用户使用手册](docs/用户使用手册.md) - 平台功能使用指南
- [🔧 管理员手册](docs/管理员手册.md) - 系统管理和配置指南
- [🛠️ 开发者手册](docs/开发者手册.md) - API 集成和 SDK 使用

## 🧪 测试

### 自动化测试

<table>
<tr>
<td width="50%">

### 性能测试

```bash
# API 性能测试
cd scripts/performance
python load_test.py --users 100 --duration 60s

# 数据库性能测试
python db_benchmark.py --connections 50 --queries 1000
```

## 🚢 部署

### 生产环境部署

#### 1. 使用 Docker Compose

```bash
# 生产环境部署
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 2. 使用 Kubernetes

```bash
# 创建命名空间
kubectl create namespace openmaas

# 部署应用
kubectl apply -f project/k8s/

# 或使用 Helm
helm install openmaas project/helm/openmaas/
```

### 扩容和负载均衡

```bash
# 扩容后端服务
docker-compose up -d --scale maas-server=3

# Kubernetes 扩容
kubectl scale deployment maas-server --replicas=3
```

### 备份和恢复

```bash
# 数据库备份
scripts/backup/backup_database.sh

# 恢复数据库
scripts/backup/restore_database.sh backup_20240101.sql
```

## 📊 监控和运维

### 系统监控

- **应用监控**: Prometheus + Grafana
- **日志管理**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **链路追踪**: Jaeger
- **告警通知**: AlertManager + 钉钉/企业微信

### 健康检查

```bash
# 应用健康状态
curl http://localhost:8000/health

# 数据库连接状态
curl http://localhost:8000/health/db

# Redis 连接状态
curl http://localhost:8000/health/redis

# Prometheus 指标
curl http://localhost:8000/metrics
```

### 性能指标

访问 Grafana 仪表板查看详细指标：

- **应用性能**: 响应时间、吞吐量、错误率
- **系统资源**: CPU、内存、磁盘、网络使用率
- **数据库性能**: 连接数、查询性能、锁等待
- **业务指标**: 用户活跃度、API 调用量、模型推理次数

## 🔧 开发工具

### IDE 配置

**VS Code 推荐插件**:

- **前端**: Volar, Vue VSCode Snippets, ESLint, Prettier
- **后端**: Python, Pylance, Black Formatter, MyPy
- **通用**: GitLens, Docker, REST Client

**配置文件**:

```bash
# 复制开发配置
cp .vscode/settings.example.json .vscode/settings.json
cp .vscode/launch.example.json .vscode/launch.json
```

### 代码质量

```bash
# 前端代码检查
cd maas-web && npm run lint && npm run type-check

# 后端代码检查
cd maas-server && uv run ruff check src && uv run mypy src

# 统一格式化
./scripts/format_all.sh
```

## 🤝 贡献指南

我们非常欢迎社区贡献！无论是 Bug 报告、功能建议还是代码贡献。

### 参与方式

1. **🐛 Bug 报告**: [GitHub Issues](https://github.com/your-org/openmaas/issues)
2. **💡 功能建议**: [GitHub Discussions](https://github.com/your-org/openmaas/discussions)
3. **📝 文档改进**: 直接提交 PR 改进文档
4. **💻 代码贡献**: Fork 项目并提交 PR

### 开发流程

```bash
# 1. Fork 并克隆项目
git clone https://github.com/your-username/openmaas.git
cd openmaas

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 进行开发
# ... 编写代码、测试

# 4. 提交代码
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-feature-name

# 5. 创建 Pull Request
```

### 代码规范

**提交信息规范** (遵循 [Conventional Commits](https://conventionalcommits.org/)):

- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**代码质量要求**:

- 前端: ESLint + Prettier, 类型检查通过
- 后端: Ruff + Black + MyPy, 测试覆盖率 > 85%
- 所有 PR 必须通过 CI/CD 检查

## 🏆 贡献者

感谢所有为 OpenMaaS 项目做出贡献的开发者！

<a href="https://github.com/your-org/openmaas/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=your-org/openmaas" />
</a>

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/your-org/openmaas?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-org/openmaas?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-org/openmaas)
![GitHub pull requests](https://img.shields.io/github/issues-pr/your-org/openmaas)
![GitHub last commit](https://img.shields.io/github/last-commit/your-org/openmaas)

## 📄 许可证

本项目采用 **Apache License 2.0** 开源许可证。

```
Copyright 2024 OpenMaaS Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### 第三方依赖许可证

- [前端依赖许可证](maas-web/THIRD-PARTY-LICENSES.md)
- [后端依赖许可证](maas-server/THIRD-PARTY-LICENSES.md)

## 🌟 致谢

特别感谢以下开源项目和技术社区：

- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能 Python Web 框架
- [Element Plus](https://element-plus.org/) - 基于 Vue 3 的桌面端组件库
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包和 ORM
- [PostgreSQL](https://www.postgresql.org/) - 世界上最先进的开源关系数据库

## 📞 联系我们

### 支持渠道

- 📧 **邮件联系**: linkcheng1992@gmail.com
- 💬 **QQ 群**: [待建群]
- 🐦 **微信群**: [扫码加入]
- 📱 **钉钉群**: [待建群]

---

<div align="center">

⭐ **如果这个项目对您有帮助，请给我们一个 Star！**

🚀 **让我们一起构建更智能的 AI 服务平台！**

💖 **感谢所有贡献者和用户的支持！**

[⬆ 回到顶部](#openmaas)

</div>
