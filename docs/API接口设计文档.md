# API接口设计文档

## 1. API设计规范

### 1.1 基础规范
- **协议**: HTTPS
- **格式**: JSON
- **编码**: UTF-8
- **版本**: URL路径版本控制 `/api/v1/`
- **认证**: JWT Bearer Token / API Key

### 1.2 响应格式标准
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "code": 200,
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

### 1.3 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

### 1.4 状态码规范
- `200` - 请求成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 权限不足
- `404` - 资源不存在
- `409` - 资源冲突
- `422` - 参数验证失败
- `429` - 请求频率限制
- `500` - 服务器内部错误

## 2. 认证与授权 API

### 2.1 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "organization": "Example Corp"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "verification_sent": true
  },
  "message": "注册成功，请查收验证邮件"
}
```

### 2.2 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "username": "john_doe",
      "email": "john@example.com",
      "roles": ["user"]
    }
  }
}
```

### 2.3 OAuth登录
```http
POST /api/v1/auth/oauth/{provider}
Content-Type: application/json

{
  "code": "oauth_authorization_code",
  "redirect_uri": "https://app.maas.com/callback"
}
```

### 2.4 刷新Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer {refresh_token}
```

### 2.5 退出登录
```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

## 3. 用户管理 API

### 3.1 获取用户信息
```http
GET /api/v1/users/me
Authorization: Bearer {access_token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://cdn.maas.com/avatars/uuid.jpg",
    "organization": "Example Corp",
    "roles": ["user"],
    "quota": {
      "api_calls_limit": 1000,
      "api_calls_used": 150,
      "storage_limit": 1073741824,
      "storage_used": 104857600
    },
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 3.2 更新用户信息
```http
PUT /api/v1/users/me
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "organization": "New Corp"
}
```

### 3.3 API密钥管理
```http
# 创建API密钥
POST /api/v1/users/me/api-keys
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "My App API Key",
  "permissions": ["model:read", "inference:create"],
  "expires_at": "2025-01-01T00:00:00Z"
}

# 列出API密钥
GET /api/v1/users/me/api-keys
Authorization: Bearer {access_token}

# 删除API密钥
DELETE /api/v1/users/me/api-keys/{key_id}
Authorization: Bearer {access_token}
```

## 4. 模型管理 API

### 4.1 模型列表
```http
GET /api/v1/models
Authorization: Bearer {access_token}

# 查询参数
?type=llm                    # 模型类型过滤
&category=text-generation    # 模型分类过滤
&visibility=public           # 可见性过滤
&search=chatglm             # 搜索关键词
&sort=download_count         # 排序字段
&order=desc                  # 排序方向
&page=1                      # 页码
&limit=20                    # 每页数量
```

**响应:**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "id": "uuid",
        "name": "ChatGLM-6B",
        "description": "ChatGLM-6B 是一个开源的、支持中英双语的对话语言模型",
        "type": "llm",
        "category": "text-generation",
        "owner": {
          "id": "uuid",
          "username": "thudm",
          "organization": "清华大学"
        },
        "visibility": "public",
        "license": "Apache-2.0",
        "tags": ["chatglm", "chinese", "dialogue"],
        "latest_version": "1.0.0",
        "download_count": 15420,
        "like_count": 892,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 156,
      "pages": 8
    }
  }
}
```

### 4.2 模型详情
```http
GET /api/v1/models/{model_id}
Authorization: Bearer {access_token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "ChatGLM-6B",
    "description": "详细描述...",
    "type": "llm",
    "metadata": {
      "parameters_count": 6200000000,
      "model_format": "transformers",
      "supported_tasks": ["text-generation", "dialogue"],
      "hardware_requirements": {
        "min_gpu_memory": "13GB",
        "recommended_gpu": "V100, A100",
        "cpu_cores": 8,
        "ram": "32GB"
      }
    },
    "versions": [
      {
        "version": "1.0.0",
        "description": "Initial release",
        "file_size": 12884901888,
        "created_at": "2024-01-01T00:00:00Z",
        "status": "ready"
      }
    ],
    "usage_examples": [
      {
        "task": "text-generation",
        "input": "你好，介绍一下你自己",
        "output": "你好！我是ChatGLM-6B..."
      }
    ]
  }
}
```

### 4.3 上传模型
```http
POST /api/v1/models
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

# 表单数据
name: ChatGLM-6B-Custom
description: 自定义微调模型
type: llm
category: text-generation
visibility: private
license: Apache-2.0
tags: ["chatglm", "custom"]
model_file: @model.bin
config_file: @config.json
```

### 4.4 模型版本管理
```http
# 上传新版本
POST /api/v1/models/{model_id}/versions
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

version: 1.1.0
description: Bug fixes and improvements
model_file: @model_v1.1.0.bin

# 获取版本列表
GET /api/v1/models/{model_id}/versions
Authorization: Bearer {access_token}

# 下载模型文件
GET /api/v1/models/{model_id}/versions/{version}/download
Authorization: Bearer {access_token}
```

## 5. 微调服务 API

### 5.1 数据集管理
```http
# 上传数据集
POST /api/v1/datasets
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

name: Customer Service Dataset
description: 客户服务对话数据
type: conversation
format: jsonl
file: @dataset.jsonl

# 数据集列表
GET /api/v1/datasets
Authorization: Bearer {access_token}

# 数据集详情
GET /api/v1/datasets/{dataset_id}
Authorization: Bearer {access_token}
```

### 5.2 创建微调任务
```http
POST /api/v1/finetune/jobs
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "ChatGLM Customer Service Fine-tune",
  "base_model_id": "uuid",
  "dataset_id": "uuid",
  "algorithm": "lora",
  "hyperparameters": {
    "learning_rate": 3e-4,
    "batch_size": 4,
    "num_epochs": 3,
    "warmup_steps": 100,
    "lora_r": 8,
    "lora_alpha": 32,
    "lora_dropout": 0.1
  },
  "config": {
    "evaluation_strategy": "steps",
    "eval_steps": 100,
    "save_steps": 500,
    "logging_steps": 10
  }
}
```

### 5.3 微调任务监控
```http
# 任务列表
GET /api/v1/finetune/jobs
Authorization: Bearer {access_token}

# 任务详情
GET /api/v1/finetune/jobs/{job_id}
Authorization: Bearer {access_token}

# 训练指标
GET /api/v1/finetune/jobs/{job_id}/metrics
Authorization: Bearer {access_token}

# 训练日志
GET /api/v1/finetune/jobs/{job_id}/logs
Authorization: Bearer {access_token}
?page=1&limit=100
```

**WebSocket 实时监控:**
```javascript
// 连接WebSocket
const ws = new WebSocket('wss://api.maas.com/v1/finetune/jobs/{job_id}/monitor');

// 接收训练进度
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Training progress:', data);
};
```

### 5.4 任务控制
```http
# 取消任务
POST /api/v1/finetune/jobs/{job_id}/cancel
Authorization: Bearer {access_token}

# 重启任务
POST /api/v1/finetune/jobs/{job_id}/restart
Authorization: Bearer {access_token}
```

## 6. 推理服务 API

### 6.1 模型部署
```http
# 创建部署
POST /api/v1/inference/deployments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "ChatGLM Production Deployment",
  "model_id": "uuid",
  "model_version": "1.0.0",
  "config": {
    "replicas": 2,
    "hardware_spec": {
      "gpu_type": "V100",
      "gpu_count": 1,
      "cpu_cores": 8,
      "memory": "32GB"
    },
    "auto_scaling": {
      "enabled": true,
      "min_replicas": 1,
      "max_replicas": 5,
      "target_cpu_utilization": 70
    },
    "inference_config": {
      "max_tokens": 2048,
      "temperature": 0.7,
      "top_p": 0.9,
      "stream": true
    }
  }
}
```

### 6.2 部署管理
```http
# 部署列表
GET /api/v1/inference/deployments
Authorization: Bearer {access_token}

# 部署详情
GET /api/v1/inference/deployments/{deployment_id}
Authorization: Bearer {access_token}

# 更新部署
PUT /api/v1/inference/deployments/{deployment_id}
Authorization: Bearer {access_token}

# 删除部署
DELETE /api/v1/inference/deployments/{deployment_id}
Authorization: Bearer {access_token}

# 部署状态
GET /api/v1/inference/deployments/{deployment_id}/status
Authorization: Bearer {access_token}

# 部署指标
GET /api/v1/inference/deployments/{deployment_id}/metrics
Authorization: Bearer {access_token}
```

### 6.3 推理请求
```http
# 聊天补全
POST /api/v1/inference/chat
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "deployment_id": "uuid",
  "messages": [
    {"role": "system", "content": "你是一个有用的AI助手"},
    {"role": "user", "content": "介绍一下人工智能的发展历史"}
  ],
  "parameters": {
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": true
  }
}
```

**流式响应:**
```
data: {"id": "uuid", "choices": [{"delta": {"content": "人工智能"}}]}

data: {"id": "uuid", "choices": [{"delta": {"content": "的发展"}}]}

data: {"id": "uuid", "choices": [{"finish_reason": "stop"}]}

data: [DONE]
```

### 6.4 文本补全
```http
POST /api/v1/inference/completion
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "deployment_id": "uuid",
  "prompt": "人工智能是",
  "parameters": {
    "max_tokens": 500,
    "temperature": 0.8
  }
}
```

### 6.5 向量化
```http
POST /api/v1/inference/embedding
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "deployment_id": "uuid",
  "texts": [
    "这是第一段文本",
    "这是第二段文本"
  ]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "embeddings": [
      [0.1, 0.2, 0.3, ...],
      [0.4, 0.5, 0.6, ...]
    ],
    "model": "text-embedding-ada-002",
    "usage": {
      "total_tokens": 20
    }
  }
}
```

### 6.6 批量推理
```http
POST /api/v1/inference/batch
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "deployment_id": "uuid",
  "requests": [
    {
      "id": "req_1",
      "type": "chat",
      "data": {
        "messages": [{"role": "user", "content": "问题1"}]
      }
    },
    {
      "id": "req_2", 
      "type": "completion",
      "data": {
        "prompt": "提示词2"
      }
    }
  ]
}
```

## 7. 知识库服务 API

### 7.1 知识库管理
```http
# 创建知识库
POST /api/v1/knowledge-bases
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "企业知识库",
  "description": "公司内部知识管理",
  "embedding_model": "text-embedding-ada-002",
  "config": {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "similarity_threshold": 0.7
  }
}

# 知识库列表
GET /api/v1/knowledge-bases
Authorization: Bearer {access_token}

# 知识库详情
GET /api/v1/knowledge-bases/{kb_id}
Authorization: Bearer {access_token}
```

### 7.2 文档管理
```http
# 上传文档
POST /api/v1/knowledge-bases/{kb_id}/documents
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

title: 产品使用手册
file: @manual.pdf
metadata: {"department": "产品部", "version": "1.0"}

# 文档列表
GET /api/v1/knowledge-bases/{kb_id}/documents
Authorization: Bearer {access_token}

# 文档详情
GET /api/v1/knowledge-bases/{kb_id}/documents/{doc_id}
Authorization: Bearer {access_token}

# 删除文档
DELETE /api/v1/knowledge-bases/{kb_id}/documents/{doc_id}
Authorization: Bearer {access_token}
```

### 7.3 知识检索
```http
# 相似度检索
POST /api/v1/knowledge-bases/{kb_id}/search
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "query": "如何重置密码",
  "top_k": 5,
  "filters": {
    "department": "产品部"
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "uuid",
        "content": "重置密码的步骤如下...",
        "similarity": 0.89,
        "document": {
          "id": "uuid",
          "title": "用户手册",
          "metadata": {"department": "产品部"}
        },
        "chunk_index": 5
      }
    ],
    "query_time": 0.12
  }
}
```

### 7.4 RAG问答
```http
POST /api/v1/knowledge-bases/{kb_id}/qa
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "question": "如何重置密码？",
  "model_deployment_id": "uuid",
  "config": {
    "top_k": 3,
    "include_sources": true,
    "temperature": 0.3
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "answer": "根据文档，重置密码的步骤如下：\n1. 进入登录页面\n2. 点击"忘记密码"\n3. 输入邮箱地址\n4. 查收重置邮件",
    "sources": [
      {
        "document_title": "用户手册",
        "content": "重置密码的步骤...",
        "similarity": 0.89
      }
    ],
    "tokens_used": 156
  }
}
```

## 8. 应用管理 API

### 8.1 应用创建
```http
POST /api/v1/applications
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "客服机器人",
  "description": "智能客服聊天机器人",
  "type": "chatbot",
  "model_id": "uuid",
  "knowledge_base_id": "uuid",
  "config": {
    "welcome_message": "您好，我是智能客服，有什么可以帮您的吗？",
    "max_conversation_length": 20,
    "enable_knowledge_base": true,
    "fallback_response": "抱歉，我没有理解您的问题，请换个方式表达。"
  },
  "ui_config": {
    "theme": "light",
    "primary_color": "#1890ff",
    "avatar_url": "https://cdn.maas.com/avatars/bot.png"
  },
  "access_control": {
    "is_public": false,
    "allowed_domains": ["example.com"],
    "require_auth": true
  }
}
```

### 8.2 应用管理
```http
# 应用列表
GET /api/v1/applications
Authorization: Bearer {access_token}

# 应用详情
GET /api/v1/applications/{app_id}
Authorization: Bearer {access_token}

# 更新应用
PUT /api/v1/applications/{app_id}
Authorization: Bearer {access_token}

# 发布应用
POST /api/v1/applications/{app_id}/publish
Authorization: Bearer {access_token}

# 删除应用
DELETE /api/v1/applications/{app_id}
Authorization: Bearer {access_token}
```

### 8.3 应用集成
```http
# 获取嵌入代码
GET /api/v1/applications/{app_id}/embed
Authorization: Bearer {access_token}

# 获取API密钥
GET /api/v1/applications/{app_id}/api-key
Authorization: Bearer {access_token}

# Webhook配置
POST /api/v1/applications/{app_id}/webhooks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "events": ["message.sent", "conversation.started"],
  "secret": "webhook_secret"
}
```

### 8.4 应用使用
```http
# 应用对话
POST /api/v1/applications/{app_id}/chat
Authorization: Bearer {app_api_key}
Content-Type: application/json

{
  "message": "你好",
  "session_id": "session_uuid",
  "user_id": "user_123"
}
```

## 9. 监控与统计 API

### 9.1 用户统计
```http
# 个人使用统计
GET /api/v1/users/me/stats
Authorization: Bearer {access_token}
?period=30d

# API调用统计
GET /api/v1/users/me/api-usage
Authorization: Bearer {access_token}
?start_date=2024-01-01&end_date=2024-01-31
```

### 9.2 系统监控
```http
# 系统状态
GET /api/v1/system/health
Authorization: Bearer {access_token}

# 系统指标
GET /api/v1/system/metrics
Authorization: Bearer {access_token}
?metrics=api_calls,active_users,deployments
```

### 9.3 使用分析
```http
# 模型使用排行
GET /api/v1/analytics/models/popular
Authorization: Bearer {access_token}

# 用户活跃度
GET /api/v1/analytics/users/activity
Authorization: Bearer {access_token}
```

## 10. WebSocket API

### 10.1 实时通知
```javascript
// 连接用户通知
const ws = new WebSocket('wss://api.maas.com/v1/notifications/stream');
ws.send(JSON.stringify({
  type: 'auth',
  token: 'Bearer ' + access_token
}));

// 接收通知
ws.onmessage = function(event) {
  const notification = JSON.parse(event.data);
  console.log('Notification:', notification);
};
```

### 10.2 实时推理
```javascript
// 流式聊天
const ws = new WebSocket('wss://api.maas.com/v1/inference/stream');
ws.send(JSON.stringify({
  type: 'chat',
  deployment_id: 'uuid',
  messages: [
    {role: 'user', content: '你好'}
  ]
}));
```

### 10.3 训练监控
```javascript
// 微调进度监控
const ws = new WebSocket('wss://api.maas.com/v1/finetune/jobs/{job_id}/monitor');
ws.onmessage = function(event) {
  const progress = JSON.parse(event.data);
  updateProgressBar(progress.percentage);
  updateMetrics(progress.metrics);
};
```

## 11. 错误码定义

### 11.1 认证相关
- `AUTH_001` - Token无效
- `AUTH_002` - Token过期
- `AUTH_003` - 权限不足
- `AUTH_004` - API密钥无效

### 11.2 资源相关
- `RESOURCE_001` - 资源不存在
- `RESOURCE_002` - 资源已存在
- `RESOURCE_003` - 资源正在使用中
- `RESOURCE_004` - 资源配额不足

### 11.3 验证相关
- `VALIDATION_001` - 参数缺失
- `VALIDATION_002` - 参数格式错误
- `VALIDATION_003` - 参数超出范围
- `VALIDATION_004` - 文件格式不支持

### 11.4 业务相关
- `MODEL_001` - 模型加载失败
- `MODEL_002` - 模型不支持该操作
- `INFERENCE_001` - 推理请求失败
- `FINETUNE_001` - 训练任务创建失败

## 12. 限流策略

### 12.1 API限流
```
# 用户级别
用户API调用: 1000次/小时
文件上传: 10次/小时
模型部署: 5次/小时

# IP级别
IP访问: 10000次/小时
注册请求: 10次/小时

# 应用级别
应用调用: 根据用户配额
Webhook调用: 1000次/小时
```

### 12.2 资源限制
```
# 文件大小
模型文件: 最大50GB
数据集文件: 最大10GB
文档文件: 最大100MB
头像文件: 最大2MB

# 并发限制
同时训练任务: 3个
同时部署数量: 10个
WebSocket连接: 100个
```

这份API设计文档涵盖了MAAS平台的所有核心功能模块，包括认证授权、用户管理、模型管理、微调服务、推理服务、知识库服务和应用管理等。每个API都有详细的请求格式、响应格式和使用示例，可以作为前后端开发的重要参考文档。