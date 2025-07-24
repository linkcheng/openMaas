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
