  1. 项目概述

  1.1 项目背景

  基于现有MaaS（Model-as-a-Service）平台，构建一个多用户Agent开发和使用系统。该系统允许开发者创建和发布智能Agent到AgentStore，用户可以发现、配置和使用这些Agent进行多轮对话。

  1.2 系统目标

  - 为开发者提供完整的Agent开发、测试、发布平台
  - 为用户提供丰富的Agent商店和便捷的使用体验
  - 支持Agent与大模型、MCP工具、RAG系统的深度集成
  - 实现多用户、多Agent、多对话的并发管理

  2. 需求分析

  2.1 用户角色定义

  2.1.1 Developer（开发者）

  主要职责：
  - 开发和调试Agent逻辑
  - 配置Agent参数和工具集成
  - 发布Agent到AgentStore
  - 管理Agent版本和更新

  核心需求：
  - 可视化Agent开发环境
  - 代码编辑和调试工具
  - 测试环境和沙箱执行
  - 版本控制和发布管理
  - 使用统计和反馈分析

  2.1.2 User（最终用户）

  主要职责：
  - 浏览和搜索AgentStore中的Agent
  - 配置个人API密钥和参数
  - 与Agent进行多轮对话
  - 管理对话历史和会话

  核心需求：
  - Agent发现和搜索功能
  - 个人配置管理界面
  - 直观的对话交互界面
  - 多会话并行管理
  - 对话历史查看和导出

  2.2 功能需求分析

  2.2.1 Agent开发平台

  核心功能：
  - 代码编辑器：支持Python、JavaScript等语言的Agent开发
  - 调试工具：断点调试、日志查看、变量监控
  - 测试环境：沙箱环境中测试Agent功能
  - 模板系统：提供常见Agent开发模板
  - 版本管理：Git风格的版本控制和分支管理

  技术要求：
  - 基于Web的IDE环境
  - LangGraph工作流可视化编辑
  - LangChain工具链集成
  - 安全的代码执行沙箱

  2.2.2 AgentStore商店系统

  核心功能：
  - 发布管理：Agent提交、审核、发布流程
  - 分类体系：按功能、行业、技术栈分类
  - 搜索推荐：基于关键词、标签、评分的智能搜索
  - 评价系统：用户评分、评论、使用统计
  - 版本管理：Agent更新通知和版本兼容性

  数据模型：
  Agent {
    id: UUID
    name: string
    description: string
    category: Category[]
    tags: string[]
    version: string
    author_id: UUID (Developer)
    model_requirements: ModelConfig[]
    tool_dependencies: string[]
    rag_requirements: boolean
    published_at: datetime
    rating: decimal
    download_count: integer
    created_at: datetime
    updated_at: datetime
  }

  2.2.3 多对话管理系统

  核心功能：
  - 会话创建：用户可为同一Agent创建多个独立会话
  - 并发对话：支持用户同时与多个Agent对话
  - 上下文管理：每个会话维护独立的对话历史和上下文
  - 消息持久化：所有对话消息安全存储
  - 实时通信：WebSocket支持实时消息推送

  数据关系：
  - User 1:N Conversation
  - Agent 1:N Conversation
  - Conversation 1:N Message

  2.2.4 配置管理系统

  核心功能：
  - API密钥管理：安全存储和管理各种API密钥
  - 模型配置：用户可选择和配置大模型参数
  - 工具配置：MCP工具的个性化配置
  - 偏好设置：界面主题、通知设置等个人偏好

  安全要求：
  - API密钥加密存储（国密SM4算法）
  - 细粒度权限控制
  - 审计日志记录

  2.2.5 MCP工具集成（基于FastMCP Client-Server架构）

  核心功能：
  - **工具CRUD管理**：客户端负责工具的创建、更新、删除和查询
  - **工具实现执行**：服务端负责工具的具体功能实现和执行
  - **Topic服务器管理**：支持多租户工具隔离和动态管理
  - **HTTP Streaming通信**：双向流式通信支持长时间任务和实时进度
  - **权限控制**：用户授权Agent使用特定工具
  - **工具商店**：第三方工具的发现和安装

  技术架构：
  - **Client-Server分离设计**：基于FastMCP框架的分离式架构
  - **HTTP Streaming协议**：替代传统SSE，支持HTTP/2多路复用
  - **Topic级别隔离**：每个Agent版本对应独立的Topic服务器
  - **连接池优化**：高性能连接管理和批量操作支持
  - **工具沙箱执行环境**：独立的MCP服务器确保安全隔离
  - **异步工具调用机制**：支持并发工具调用和流式响应

  2.2.6 RAG知识集成

  核心功能：
  - 知识库管理：用户可上传和管理知识文档
  - 向量化处理：文档自动向量化和索引
  - 知识检索：Agent运行时智能检索相关知识
  - 知识更新：支持知识库的增量更新

  技术选型：
  - Milvus向量数据库
  - 多种文档格式支持
  - 智能分块和向量化

  3. 系统架构设计

  3.1 整体架构

  基于现有MaaS系统的DDD架构，采用微服务设计模式：

  ┌─────────────────────────────────────────────────┐
  │                 Web Frontend                    │
  │              (Vue 3 + Element Plus)            │
  ├─────────────────────────────────────────────────┤
  │                API Gateway                      │
  │            (FastAPI + Middleware)              │
  ├─────────────────────────────────────────────────┤
  │  Agent    │ AgentStore │ Conversation │ Integration │
  │  Module   │   Module   │   Module     │   Module    │
  ├─────────────────────────────────────────────────┤
  │         Shared Infrastructure Layer             │
  │    (Database, Cache, Auth, Logging)            │
  ├─────────────────────────────────────────────────┤
  │          External Services                      │
  │  (LLM APIs, MCP Tools, Vector DB, Search)     │
  └─────────────────────────────────────────────────┘

  3.2 核心模块设计

  3.2.1 Agent模块 (src/agent/)

  DDD分层结构：
  src/agent/
  ├── domain/
  │   ├── models/
  │   │   ├── agent.py          # Agent聚合根
  │   │   ├── template.py       # Agent模板实体
  │   │   └── workflow.py       # LangGraph工作流
  │   ├── repositories/
  │   │   └── agent_repository.py
  │   └── services/
  │       ├── agent_service.py
  │       └── version_service.py
  ├── application/
  │   ├── agent_service.py      # Agent应用服务
  │   ├── development_service.py # 开发环境服务
  │   └── schemas.py
  ├── infrastructure/
  │   ├── repositories.py       # Agent仓储实现
  │   ├── sandbox.py           # 代码执行沙箱
  │   └── storage.py           # Agent代码存储
  └── interface/
      └── agent_controller.py   # Agent API控制器

  核心领域模型：
  class Agent(AggregateRoot):
      """Agent聚合根"""
      def __init__(self, id: UUID, name: str, description: str, 
                   developer_id: UUID, workflow: LangGraphWorkflow):
          self.id = id
          self.name = name
          self.description = description
          self.developer_id = developer_id
          self.workflow = workflow
          self.version = "1.0.0"
          self.status = AgentStatus.DRAFT
          self.model_requirements = []
          self.tool_dependencies = []
          self.rag_enabled = False

  3.2.2 AgentStore模块 (src/agentstore/)

  核心功能实现：
  class AgentStoreService:
      """AgentStore应用服务"""

      async def publish_agent(self, agent_id: UUID, developer_id: UUID):
          """发布Agent到商店"""

      async def search_agents(self, query: str, filters: dict):
          """搜索Agent"""

      async def get_recommendations(self, user_id: UUID):
          """获取推荐Agent"""

  3.2.3 Conversation模块 (src/conversation/)

  基于现有chat_controller扩展：
  class ConversationService:
      """对话服务"""

      async def create_conversation(self, user_id: UUID, agent_id: UUID):
          """创建新对话"""

      async def send_message(self, conversation_id: UUID, message: str):
          """发送消息并获取回复"""

      async def get_conversation_history(self, conversation_id: UUID):
          """获取对话历史"""

  LangGraph集成：
  class AgentExecutionGraph:
      """Agent执行图"""

      def __init__(self, agent: Agent):
          self.graph = StateGraph(ConversationState)
          self._build_graph(agent.workflow)

      async def execute(self, message: str, context: dict):
          """执行Agent工作流"""
          return await self.graph.ainvoke({
              "messages": [message],
              "context": context
          })

  3.2.4 Integration模块 (src/integration/)

  MCP工具集成（FastMCP Client-Server架构）：
  
  # 客户端：MCP工具CRUD管理
  class IntegratedMCPToolManager:
      """集成的MCP工具管理器 - 桥接Agent系统与MCP服务器"""
      
      def __init__(self, mcp_server_url: str):
          self.client = MCPStreamClient(mcp_server_url)
      
      async def prepare_agent_tools(self, agent_version_id: str, tool_dependencies: List[str]):
          """为Agent准备工具环境、创建Topic服务器"""
          
      async def call_agent_tool(self, agent_version_id: str, tool_name: str, parameters: dict):
          """调用Agent工具的统一接口"""
          
      async def call_agent_tool_stream(self, agent_version_id: str, tool_name: str, parameters: dict):
          """流式调用Agent工具"""
  
  # 服务端：MCP工具实现执行
  class MCPRootServer:
      """MCP根服务器 - 管理多个Topic服务器"""
      
      def __init__(self, app: FastAPI):
          self.topic_servers: Dict[str, MCPTopicServer] = {}
          self.tool_factory = ToolFactory()
      
      async def create_topic_server(self, name: str, server_id: str, description: str):
          """创建Topic服务器"""
          
      async def call_tool_stream(self, server_id: str, tool_name: str, arguments: dict):
          """流式工具调用"""

  RAG系统集成：
  class RAGService:
      """RAG知识检索服务"""

      async def create_knowledge_base(self, user_id: UUID, documents: list):
          """创建知识库"""

      async def query_knowledge(self, query: str, kb_id: UUID):
          """查询知识库"""

  3.3 数据库设计

  3.3.1 Agent相关表

  -- Agent分类表
  CREATE TABLE agent_categories (
      id UUID PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      parent_id UUID REFERENCES agent_categories(id),
      description TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- Agent表（完全基于版本设计，优化版）
  CREATE TABLE agents (
      id UUID PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      description TEXT,
      developer_id UUID REFERENCES users(id),
      category_id UUID REFERENCES agent_categories(id),
      tags TEXT[], -- Agent标签数组，支持动态添加和删除
      status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'published', 'archived'
      download_count INTEGER DEFAULT 0,
      average_rating DECIMAL(3,2),
      published_at TIMESTAMP,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );


  -- Agent版本表（集成现有模型配置系统）
  -- 作用：管理Agent的版本历史和工作流配置，引用平台模型配置
  -- 优化：移除model_requirements冗余，直接引用model_configs表
  -- 🎆 Agent版本表（支持Multi-Agent工作流的服务配置）
CREATE TABLE agent_versions (
      id UUID PRIMARY KEY,
      agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
      version VARCHAR(50) NOT NULL,
      
      -- 🚀 基于节点的服务依赖配置（支持Multi-Agent工作流）
      service_dependencies JSONB NOT NULL DEFAULT '{}', 
      -- 格式：{"node_name": {"service_type": config_id, ...}, ...}
      -- Multi-Agent示例：{
      --   "code_analyzer": {"llm_service": 20, "database_service": 8},
      --   "security_reviewer": {"llm_service": 15, "database_service": 12}, 
      --   "performance_checker": {"llm_service": 25, "database_service": 15, "vector_db": 18},
      --   "web_researcher": {"search_service": 23, "llm_service": 16}
      -- }
      -- 单Agent示例：{"main_agent": {"llm_service": 15, "search_service": 23, "vector_db": 12}}
      -- 注意：移除model_config_id，LLM也通过service_dependencies引用
      
      model_params_override JSONB,        -- 可选的模型参数覆盖
      
      -- Agent特定配置  
      workflow_definition JSONB NOT NULL, -- 核心工作流逻辑
      system_prompt TEXT,                 -- 系统提示词
      tool_dependencies TEXT[] NOT NULL DEFAULT '{}', -- 工具依赖列表
      
      rag_enabled BOOLEAN DEFAULT FALSE,  -- RAG功能开关（v2.0支持）
      
      -- 版本管理
      changelog TEXT,                     -- 版本变更说明
      is_current BOOLEAN DEFAULT FALSE,   -- 标识当前使用版本
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      
      CONSTRAINT unique_current_version UNIQUE (agent_id) WHERE is_current = TRUE
  );


  -- 用户Agent使用记录表
  -- 作用：记录用户使用Agent的历史，支持个人Agent库管理
  -- 用于统计Agent受欢迎程度和用户使用习惯分析
  CREATE TABLE agent_usage (
      id UUID PRIMARY KEY,
      user_id UUID REFERENCES users(id),
      agent_id UUID REFERENCES agents(id),
      first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      usage_count INTEGER DEFAULT 1,
      UNIQUE(user_id, agent_id)
  );

  -- 🚀 当前Agent配置视图（统一服务架构）
  CREATE VIEW current_agent_configs AS
  SELECT 
      -- Agent基础信息
      a.id,
      a.name,
      a.description,
      a.developer_id,
      a.category_id,
      a.tags,
      a.status,
      a.download_count,
      a.average_rating,
      a.published_at,
      a.created_at as agent_created_at,
      a.updated_at as agent_updated_at,
      
      -- Agent版本信息
      av.id as version_id,
      av.version,
      av.workflow_definition,
      av.system_prompt,
      av.tool_dependencies,
      av.service_dependencies,         -- 🎆 统一服务依赖配置
      av.rag_enabled,
      av.model_params_override,
      av.changelog,
      av.created_at as version_created_at
  FROM agents a
  JOIN agent_versions av ON a.id = av.agent_id 
  WHERE av.is_current = TRUE;
  
  -- 📝 说明：简化视图设计
  -- 1. 移除与model_configs的JOIN，因为所有服务配置现在都在service_configs中
  -- 2. 统一通过service_dependencies获取所有服务信息
  -- 3. 具体的服务配置通过get_agent_execution_config()函数获取

  3.3.2 聊天相关表

  -- 聊天会话表（版本锁定优化版）
  CREATE TABLE chats (
      id UUID PRIMARY KEY,
      user_id UUID REFERENCES users(id),
      agent_id UUID REFERENCES agents(id),
      agent_version_id UUID REFERENCES agent_versions(id), -- 锁定使用的Agent版本
      title VARCHAR(255),
      context JSONB,
      status VARCHAR(50) DEFAULT 'active', -- 'active', 'archived', 'deleted'
      expires_at TIMESTAMP,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- 聊天消息表（优化版）
  -- 🎯 聊天消息表（集成LangGraph工作流支持）
CREATE TABLE chat_messages (
      id UUID PRIMARY KEY,
      chat_id UUID REFERENCES chats(id),
      parent_message_id UUID REFERENCES chat_messages(id),
      role VARCHAR(50), -- 'user' or 'assistant'
      content TEXT,
      status VARCHAR(50) DEFAULT 'sent', -- 'sending', 'sent', 'failed', 'deleted'
      metadata JSONB,
      
      -- 🚀 LangGraph工作流集成字段
      workflow_execution_id UUID,                     -- 关联工作流执行ID
      workflow_node_name VARCHAR(128),                -- 产生此消息的工作流节点
      workflow_status VARCHAR(32) DEFAULT 'completed', -- 工作流状态：running, completed, failed, paused
      message_type VARCHAR(32) DEFAULT 'text',        -- 消息类型：text, progress, error, system
      is_intermediate BOOLEAN DEFAULT FALSE,          -- 是否为中间进度消息（可清理）
      
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- 🚀 工作流执行跟踪表（LangGraph集成支持）
  CREATE TABLE workflow_executions (
      execution_id UUID PRIMARY KEY,
      chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
      message_id UUID REFERENCES chat_messages(id) ON DELETE CASCADE,
      agent_version_id UUID NOT NULL REFERENCES agent_versions(id),
      
      -- LangGraph检查点集成
      thread_id VARCHAR(255) NOT NULL,              -- 对应LangGraph的thread_id (chat_{chat_id})
      checkpoint_id VARCHAR(255),                   -- 当前检查点ID
      checkpointer_schema VARCHAR(64) DEFAULT 'langgraph', -- PostgreSQL schema名称
      
      -- 执行状态
      status VARCHAR(32) NOT NULL DEFAULT 'running', -- running, completed, failed, paused, interrupted
      current_node VARCHAR(128),                     -- 当前执行的工作流节点
      
      -- 执行结果和错误
      final_result JSONB,                           -- 最终执行结果
      error_info JSONB,                             -- 错误详细信息
      
      -- 性能统计
      total_nodes INTEGER DEFAULT 0,                -- 总节点数
      completed_nodes INTEGER DEFAULT 0,            -- 已完成节点数
      failed_nodes INTEGER DEFAULT 0,               -- 失败节点数
      
      -- 时间戳
      started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      completed_at TIMESTAMP,
      paused_at TIMESTAMP,                          -- 暂停时间（人工干预）
      
      -- 约束
      UNIQUE (chat_id, thread_id)
  );

  -- 🔧 工作流节点执行记录表
  CREATE TABLE workflow_node_executions (
      id UUID PRIMARY KEY,
      execution_id UUID NOT NULL REFERENCES workflow_executions(execution_id) ON DELETE CASCADE,
      node_name VARCHAR(128) NOT NULL,
      
      -- 执行状态
      status VARCHAR(32) NOT NULL DEFAULT 'running', -- running, completed, failed, skipped
      
      -- 执行数据
      input_state JSONB,                            -- 节点输入状态
      output_state JSONB,                           -- 节点输出状态
      service_calls JSONB,                          -- 服务调用记录详情
      
      -- 性能信息
      started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      completed_at TIMESTAMP,
      duration_ms INTEGER,                          -- 执行耗时（毫秒）
      
      -- 重试和错误处理
      retry_count INTEGER DEFAULT 0,                -- 重试次数
      max_retries INTEGER DEFAULT 3,               -- 最大重试次数
      error_message TEXT,                           -- 错误信息
      
      -- 资源消耗统计
      tokens_consumed INTEGER,                      -- LLM token消耗
      cost_estimate DECIMAL(10,6),                  -- 预估成本
      
      CONSTRAINT fk_workflow_node_execution FOREIGN KEY (execution_id) REFERENCES workflow_executions(execution_id)
  );

  -- 📋 人工干预任务表（支持LangGraph人机协作）
  CREATE TABLE human_intervention_tasks (
      task_id UUID PRIMARY KEY,
      execution_id UUID NOT NULL REFERENCES workflow_executions(execution_id) ON DELETE CASCADE,
      node_name VARCHAR(128) NOT NULL,
      
      -- 任务信息
      instruction TEXT NOT NULL,                    -- 给人工的指导说明
      current_state JSONB NOT NULL,                 -- 当前工作流状态
      required_input_schema JSONB,                  -- 期望的人工输入格式
      
      -- 任务状态
      status VARCHAR(32) DEFAULT 'pending',         -- pending, in_progress, completed, cancelled
      assigned_to VARCHAR(128),                     -- 分配给谁处理
      
      -- 处理结果
      human_input JSONB,                            -- 人工提供的输入
      completion_note TEXT,                         -- 完成说明
      
      -- 时间戳
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      assigned_at TIMESTAMP,
      completed_at TIMESTAMP,
      
      -- 优先级和截止时间
      priority INTEGER DEFAULT 5,                   -- 1-10，数字越大优先级越高
      due_at TIMESTAMP                              -- 期望完成时间
  );

  3.3.3 统一服务配置系统（优化架构）

  -- 服务供应商表（扩展现有providers表）
  -- 位置：src/model/infrastructure/models.py
  CREATE TABLE providers (
      provider_id INTEGER PRIMARY KEY AUTOINCREMENT,    -- 供应商ID
      provider_name VARCHAR(64) NOT NULL,               -- 供应商名称（openai、google等）
      display_name VARCHAR(128) NOT NULL,               -- 显示名称
      service_type VARCHAR(50) NOT NULL DEFAULT 'llm',  -- 🎆 服务类型
      description TEXT,                                 -- 描述信息
      base_url VARCHAR(512) NOT NULL,                   -- 基础URL
      is_active BOOLEAN NOT NULL DEFAULT 1,             -- 是否启用
      created_by VARCHAR(64) NOT NULL,                  -- 创建人
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_by VARCHAR(64) NOT NULL,                  -- 更新人
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      is_delete BOOLEAN NOT NULL DEFAULT 0              -- 是否删除
  );
  -- 服务类型：'llm', 'search', 'code_executor', 'database', 'storage', 'api_service', 'vector_db'

  -- 🚀 统一服务配置表（替代model_configs，支持所有服务类型）
  CREATE TABLE service_configs (
      config_id INTEGER PRIMARY KEY AUTOINCREMENT,      -- 配置ID
      provider_id INTEGER NOT NULL,                     -- 服务供应商ID
      service_name VARCHAR(128) NOT NULL,               -- 服务名称（gpt-4、google_search等）
      service_display_name VARCHAR(128) NOT NULL,       -- 服务显示名称
      service_type VARCHAR(64) NOT NULL,                -- 服务类型（llm、search等）
      config_data JSONB NOT NULL,                       -- 通用配置数据
      credentials TEXT,                                 -- 加密认证信息
      pricing_config JSONB,                            -- 定价配置
      limits_config JSONB,                             -- 使用限制配置
      is_active BOOLEAN NOT NULL DEFAULT 1,             -- 是否启用
      created_by VARCHAR(64) NOT NULL,                  -- 创建人
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_by VARCHAR(64) NOT NULL,                  -- 更新人
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      is_delete BOOLEAN NOT NULL DEFAULT 0,             -- 是否删除
      
      FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
      UNIQUE (provider_id, service_name, is_delete)     -- 保证同一供应商下服务名唯一
  );
  
  -- 📝 重要说明：统一架构优化
  -- 1. 移除model_configs表，所有服务（包括LLM）统一在service_configs中管理
  -- 2. 通过service_type字段区分不同类型的服务
  -- 3. config_data字段灵活存储各种服务的特定配置
  -- 4. 简化Agent引用机制，所有服务使用统一的config_id

  -- 📈 示例数据：平台管理员预配置的各类服务
  
  -- 1. 服务供应商配置
  INSERT INTO providers (provider_name, display_name, service_type, description, base_url, created_by, updated_by) VALUES
  -- LLM服务供应商
  ('openai', 'OpenAI', 'llm', 'OpenAI大语言模型', 'https://api.openai.com/v1', 'admin', 'admin'),
  ('anthropic', 'Anthropic', 'llm', 'Claude大语言模型', 'https://api.anthropic.com', 'admin', 'admin'),
  -- 搜索服务供应商
  ('google', 'Google', 'search', 'Google搜索服务', 'https://api.google.com', 'admin', 'admin'),
  ('bing', 'Microsoft Bing', 'search', 'Bing搜索服务', 'https://api.bing.microsoft.com', 'admin', 'admin'),
  -- 代码执行服务
  ('code_runner', 'Code Runner', 'code_executor', '代码执行服务', 'https://api.coderunner.com', 'admin', 'admin'),
  -- 数据库服务
  ('postgresql', 'PostgreSQL', 'database', '数据库服务', 'postgresql://localhost:5432', 'admin', 'admin'),
  -- 向量数据库服务
  ('milvus', 'Milvus', 'vector_db', '向量数据库服务', 'https://milvus-server:19530', 'admin', 'admin');

  -- 2. 统一服务配置（所有类型的服务）
  INSERT INTO service_configs (provider_id, service_name, service_display_name, service_type,
                             config_data, credentials, pricing_config, limits_config, 
                             created_by, updated_by) VALUES
  -- LLM服务配置
  (1, 'gpt-4', 'GPT-4', 'llm',
   '{"model_params": {"temperature": 0.7, "max_tokens": 4000}, "context_length": 8000}',
   encrypt_sm4('sk-xxx'),
   '{"input_cost_per_1k": 0.03, "output_cost_per_1k": 0.06}',
   '{"requests_per_minute": 60, "requests_per_day": 1000}', 'admin', 'admin'),
   
  (1, 'gpt-4-turbo', 'GPT-4 Turbo', 'llm',
   '{"model_params": {"temperature": 0.7, "max_tokens": 4000}, "context_length": 16000}',
   encrypt_sm4('sk-xxx'),
   '{"input_cost_per_1k": 0.01, "output_cost_per_1k": 0.03}',
   '{"requests_per_minute": 100, "requests_per_day": 2000}', 'admin', 'admin'),
   
  (2, 'claude-3-sonnet', 'Claude 3 Sonnet', 'llm',
   '{"model_params": {"temperature": 0.7, "max_tokens": 4000}, "context_length": 20000}',
   encrypt_sm4('sk-ant-xxx'),
   '{"input_cost_per_1k": 0.003, "output_cost_per_1k": 0.015}',
   '{"requests_per_minute": 50, "requests_per_day": 1000}', 'admin', 'admin'),

  -- 搜索服务配置
  (3, 'google_custom_search', 'Google自定义搜索', 'search',
   '{"api_endpoint": "customsearch/v1", "params": {"num": 10, "safe": "medium", "lr": "lang_zh-CN"}}',
   encrypt_sm4('your-google-api-key'),
   '{"cost_per_request": 0.005}',
   '{"requests_per_day": 100, "requests_per_minute": 10}', 'admin', 'admin'),

  -- 代码执行服务配置
  (5, 'python_sandbox', 'Python沙箱环境', 'code_executor',
   '{"supported_languages": ["python"], "timeout": 30, "memory_limit": "512MB", "environment": "sandbox"}',
   NULL,
   '{"cost_per_execution": 0.01}',
   '{"executions_per_day": 50, "max_execution_time": 30}', 'admin', 'admin'),

  -- 数据库连接配置
  (6, 'main_db', '主数据库', 'database',
   '{"database": "maas_db", "pool_size": 10, "timeout": 30}',
   encrypt_sm4('{"username": "agent_user", "password": "agent_pass"}'),
   '{"cost_per_query": 0.001}',
   '{"queries_per_day": 1000}', 'admin', 'admin'),

  -- 向量数据库配置
  (7, 'knowledge_vector_db', '知识向量库', 'vector_db',
   '{"collection_name": "agent_knowledge", "dimension": 1536, "metric_type": "COSINE"}',
   encrypt_sm4('{"username": "milvus_user", "password": "milvus_pass"}'),
   '{"cost_per_search": 0.002}',
   '{"searches_per_day": 500}', 'admin', 'admin');

  -- 🔑 关键优化：Agent系统直接引用这些配置，实现：
  -- 1. 用户零配置体验：无需输入API密钥
  -- 2. 平台统一管理：API密钥、成本控制、安全策略
  -- 3. 开发者便利：选择平台模型，专注于Agent逻辑

  -- 🚀 扩展：支持多种外部服务类型
  -- 问题：model_configs表仅限于大模型，Agent还需要搜索、代码执行等服务
  -- 解决方案：扩展现有架构，支持多服务类型

  -- 📝 迁移说明：统一架构优化完成
  -- 所有服务配置（包括LLM）已统一在service_configs表中管理
  -- model_configs表已整合，无需单独维护
  -- 通过service_type字段区分不同类型的服务

  3.3.4 新增业务支撑表

  -- 注意：RAG知识库功能预留到v2.0版本实现
  -- 完整的RAG系统需要knowledge_bases、knowledge_documents、
  -- knowledge_chunks、vector_embeddings等多表设计
  -- 当前版本专注于Agent开发和对话管理核心功能

  -- MCP工具注册表（集成FastMCP Client-Server架构）
  CREATE TABLE mcp_tools (
      id UUID PRIMARY KEY,
      name VARCHAR(255) NOT NULL,                    -- 工具名称（关联key）
      version VARCHAR(50),                            -- 工具版本
      description TEXT,                               -- 工具描述
      tool_type VARCHAR(50) NOT NULL,                 -- 工具类型：http_api, code_tool, database, system
      manifest JSONB NOT NULL,                        -- 工具接口清单和配置
      
      server_endpoint VARCHAR(512),                   -- MCP服务器端点（独立部署）
      topic_server_id VARCHAR(255),                   -- 所属Topic服务器ID
      
      status VARCHAR(50) DEFAULT 'active',            -- 'active', 'inactive', 'deprecated'
      tags TEXT[],                                     -- 工具标签数组
      
      -- FastMCP集成字段
      is_streaming_supported BOOLEAN DEFAULT FALSE,   -- 是否支持流式调用
      max_execution_time INTEGER DEFAULT 300,         -- 最大执行时间（秒）
      resource_requirements JSONB,                    -- 资源需求配置
      
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      
      -- 外键约束（简化直接映射）
      FOREIGN KEY (topic_server_id) REFERENCES mcp_topic_servers(server_id) ON DELETE CASCADE,
      
      -- 索引优化
      UNIQUE(name, topic_server_id),
      INDEX idx_mcp_tools_topic_server (topic_server_id)
  );
  
  -- MCP服务器状态表（Topic服务器管理）
  CREATE TABLE mcp_topic_servers (
      id UUID PRIMARY KEY,
      server_id VARCHAR(255) NOT NULL UNIQUE,         -- Topic服务器标识
      name VARCHAR(255) NOT NULL,                     -- 服务器名称
      description TEXT,                               -- 描述信息
      
     agent_version_id UUID,                          -- 关联的Agent版本（可选）
      
      -- 服务配置
      endpoint_url VARCHAR(512) NOT NULL,             -- MCP服务器端点
      status VARCHAR(50) DEFAULT 'active',            -- 'active', 'inactive', 'error'
      tool_count INTEGER DEFAULT 0,                   -- 注册的工具数量
      
      -- 性能统计
      total_calls INTEGER DEFAULT 0,                  -- 总调用次数
      success_calls INTEGER DEFAULT 0,                -- 成功调用次数
      average_response_time DECIMAL(10,3),            -- 平均响应时间（毫秒）
      
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_health_check TIMESTAMP,                    -- 最后健康检查时间
      
      -- 外键约束（简化直接映射优化）
      FOREIGN KEY (agent_version_id) REFERENCES agent_versions(id) ON DELETE CASCADE,
      
     INDEX idx_mcp_topic_servers_agent_version (agent_version_id)
  );
  
  -- MCP工具调用日志表（性能监控和调试）
  CREATE TABLE mcp_tool_call_logs (
      id UUID PRIMARY KEY,
      tool_name VARCHAR(255) NOT NULL,
      topic_server_id VARCHAR(255) NOT NULL,
      agent_version_id UUID,
      chat_id UUID,
      
      -- 调用信息
      call_parameters JSONB,                          -- 调用参数
      call_type VARCHAR(50) DEFAULT 'sync',           -- 'sync', 'stream'
      
      -- 执行结果
      status VARCHAR(50) NOT NULL,                    -- 'success', 'error', 'timeout'
      result_data JSONB,                              -- 执行结果
      error_message TEXT,                             -- 错误信息
      
      -- 性能指标
      started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      completed_at TIMESTAMP,
      duration_ms INTEGER,                            -- 执行耗时（毫秒）
      
      -- 资源消耗
      tokens_used INTEGER,                            -- 消耗的token数（如适用）
      cost_estimate DECIMAL(10,6),                    -- 预估成本
      
      -- 索引
      INDEX idx_mcp_call_logs_tool_name (tool_name),
      INDEX idx_mcp_call_logs_server_id (topic_server_id),
      INDEX idx_mcp_call_logs_started_at (started_at),
      INDEX idx_mcp_call_logs_agent_version (agent_version_id)
  );

  -- 领域事件表
  CREATE TABLE domain_events (
      id UUID PRIMARY KEY,
      aggregate_id UUID NOT NULL,
      aggregate_type VARCHAR(100) NOT NULL,
      event_type VARCHAR(100) NOT NULL,
      event_data JSONB NOT NULL,
      version INTEGER NOT NULL,
      occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  3.3.5 性能优化索引

  -- Agent相关索引
  CREATE INDEX idx_agents_category ON agents(category_id);
  CREATE INDEX idx_agents_status ON agents(status);
  CREATE INDEX idx_agents_developer ON agents(developer_id);
  CREATE INDEX idx_agents_published_at ON agents(published_at);
  CREATE INDEX idx_agents_tags ON agents USING gin(tags); -- GIN索引支持标签数组查询
  CREATE INDEX idx_agent_usage_user ON agent_usage(user_id);
  CREATE INDEX idx_agent_usage_last_used ON agent_usage(last_used_at);
  CREATE INDEX idx_agent_versions_agent ON agent_versions(agent_id);
  CREATE INDEX idx_agent_versions_current ON agent_versions(agent_id) WHERE is_current = TRUE;
  -- 移除旧的model_config_id索引，使用统一的service_dependencies

  -- 聊天相关索引
  CREATE INDEX idx_chats_user ON chats(user_id);
  CREATE INDEX idx_chats_agent ON chats(agent_id);
  CREATE INDEX idx_chats_agent_version ON chats(agent_version_id); -- 支持版本相关查询
  CREATE INDEX idx_chats_status ON chats(status);
  CREATE INDEX idx_chats_user_agent ON chats(user_id, agent_id); -- 复合索引优化用户Agent查询
  CREATE INDEX idx_chat_messages_chat ON chat_messages(chat_id);
  CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
  CREATE INDEX idx_chat_messages_parent ON chat_messages(parent_message_id);
  
  -- 🚀 LangGraph工作流相关索引
  CREATE INDEX idx_chat_messages_workflow ON chat_messages(workflow_execution_id);
  CREATE INDEX idx_chat_messages_workflow_status ON chat_messages(workflow_status);
  CREATE INDEX idx_chat_messages_intermediate ON chat_messages(is_intermediate) WHERE is_intermediate = TRUE;
  
  -- 工作流执行索引
  CREATE INDEX idx_workflow_executions_chat ON workflow_executions(chat_id);
  CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);
  CREATE INDEX idx_workflow_executions_thread ON workflow_executions(thread_id);
  CREATE INDEX idx_workflow_executions_agent_version ON workflow_executions(agent_version_id);
  CREATE INDEX idx_workflow_executions_started_at ON workflow_executions(started_at);
  CREATE INDEX idx_workflow_executions_current_node ON workflow_executions(current_node);
  
  -- 节点执行索引
  CREATE INDEX idx_workflow_node_executions_execution ON workflow_node_executions(execution_id);
  CREATE INDEX idx_workflow_node_executions_node ON workflow_node_executions(node_name);
  CREATE INDEX idx_workflow_node_executions_status ON workflow_node_executions(status);
  CREATE INDEX idx_workflow_node_executions_started_at ON workflow_node_executions(started_at);
  CREATE INDEX idx_workflow_node_executions_duration ON workflow_node_executions(duration_ms);
  
  -- 人工干预任务索引
  CREATE INDEX idx_human_intervention_status ON human_intervention_tasks(status);
  CREATE INDEX idx_human_intervention_assigned ON human_intervention_tasks(assigned_to);
  CREATE INDEX idx_human_intervention_priority ON human_intervention_tasks(priority);
  CREATE INDEX idx_human_intervention_due_at ON human_intervention_tasks(due_at);
  CREATE INDEX idx_human_intervention_node ON human_intervention_tasks(node_name);

  -- 统一服务配置相关索引
  CREATE INDEX idx_providers_name ON providers(provider_name);
  CREATE INDEX idx_providers_service_type ON providers(service_type);
  CREATE INDEX idx_providers_active ON providers(is_active) WHERE is_active = 1;
  CREATE INDEX idx_service_configs_provider ON service_configs(provider_id);
  CREATE INDEX idx_service_configs_service_name ON service_configs(service_name);
  CREATE INDEX idx_service_configs_service_type ON service_configs(service_type);
  CREATE INDEX idx_service_configs_active ON service_configs(is_active) WHERE is_active = 1;
  CREATE INDEX idx_service_configs_provider_service ON service_configs(provider_id, service_name, is_delete);
  
  -- 业务支撑表索引
  CREATE INDEX idx_mcp_tools_name ON mcp_tools(name);
  CREATE INDEX idx_mcp_tools_status ON mcp_tools(status);

  -- JSONB字段索引
  CREATE INDEX idx_agent_versions_workflow ON agent_versions USING gin(workflow_definition);
  CREATE INDEX idx_agent_versions_params_override ON agent_versions USING gin(model_params_override);
  CREATE INDEX idx_agent_versions_service_deps ON agent_versions USING gin(service_dependencies); -- 新增
  -- 统一服务配置 JSONB 索引
  CREATE INDEX idx_service_configs_data ON service_configs USING gin(config_data);
  CREATE INDEX idx_service_configs_pricing ON service_configs USING gin(pricing_config);
  CREATE INDEX idx_service_configs_limits ON service_configs USING gin(limits_config);
  CREATE INDEX idx_domain_events_aggregate ON domain_events(aggregate_id, aggregate_type);
  CREATE INDEX idx_domain_events_type ON domain_events(event_type);

  -- 分区策略建议（针对大数据量表）
  -- chat_messages表可按时间分区以提升查询性能
  -- domain_events表可按时间分区以支持事件溯源

  3.3.6 数据库设计说明

  **设计原则：**
  - 遵循DDD聚合设计，明确聚合边界
  - 支持业务扩展和高并发访问  
  - 考虑数据安全和性能优化
  - 预留业务增长空间
  
  **🎆 表关系说明（统一服务架构）：**
  
  聚合根设计：
  - **🎆 Service聚合**：providers + service_configs（统一管理所有服务）
  - **Agent聚合**：agents + agent_versions + agent_categories
  - **Chat聚合**：chats + chat_messages  
  - **User聚合**：users + agent_usage
  - **Tool聚合**：mcp_tools（工具注册）
  - **Event聚合**：domain_events（事件溯源）
  
  关键外键约束：
  - agent_versions.agent_id → agents.id（版本历史）
  - **🎆 统一服务引用：service_dependencies JSONB 字段引用 service_configs.config_id**
  - **service_configs.provider_id → providers.provider_id（服务供应商关联）**
  - agent_usage.user_id/agent_id → users.id/agents.id（使用统计）
  - chats.user_id/agent_id → users.id/agents.id（会话关联）
  - chats.agent_version_id → agent_versions.id（版本锁定）
  - chat_messages.chat_id → chats.id（消息归属）

  **关键改进（统一服务架构优化版）：**
  - **🎆 统一服务架构**：所有服务（LLM、搜索、代码执行等）统一在service_configs表中管理
  - **🚀 实现零配置体验**：用户无需配置API密钥，直接使用Agent
  - **消除user_configs冗余**：移除用户配置表，简化架构设计
  - **多服务支持**：扩展支持搜索引擎、代码执行器、数据库、向量数据库等多种服务
  - **提高数据一致性**：所有服务配置由平台统一管理，确保一致性
  - **简化版本管理**：版本切换只需更新标志位，无需同步多表数据
  - **增强查询性能**：通过视图简化常用查询，统一服务信息获取
  - **成本统一控制**：平台管理所有服务API密钥和计费，用户按量付费
  - **开发者友好**：在成熟的服务基础上开发Agent逻辑
  - **安全优化**：API密钥集中加密管理，降低泄漏风险
  - **灵活配置**：通过JSONB字段支持各种服务的特定配置需求
  - **完整的索引策略**：优化查询性能，包含统一服务配置索引
  - **引入领域事件机制**：支持事件驱动架构

  **版本管理机制说明（优化版）：**
  
  版本表设计原则：
  - 单一数据源：所有配置数据仅存储在agent_versions表中
  - 完整性：保存影响Agent行为的所有配置参数
  - 一致性：消除数据冗余，避免同步问题
  - 可追溯：支持任意版本的完全恢复和对比
  
  版本创建流程：
  ```sql
  -- 1. 标记当前版本为非当前
  UPDATE agent_versions SET is_current = FALSE 
  WHERE agent_id = ? AND is_current = TRUE;
  
  -- 2. 创建新版本（基于当前版本或全新配置）
  INSERT INTO agent_versions (
      agent_id, version, workflow_definition, 
      service_dependencies, tool_dependencies, rag_enabled,
      changelog, is_current
  ) VALUES (
      ?, '2.1.0', ?::jsonb, ?::jsonb, ?, ?,
      '增加代码执行工具支持', TRUE
  );
  ```
  
  版本切换机制：
  ```sql
  -- 简化的版本切换，只需更新is_current标志
  BEGIN;
  UPDATE agent_versions SET is_current = FALSE 
  WHERE agent_id = ? AND is_current = TRUE;
  
  UPDATE agent_versions SET is_current = TRUE 
  WHERE id = ?; -- 目标版本ID
  COMMIT;
  ```
  
  **🚀 Multi-Agent工作流服务配置详细说明：**
  
  **配置架构原理：**
  
  为支持复杂的Multi-Agent工作流，service_dependencies字段采用基于节点的配置结构：
  - **格式**: `{"node_name": {"service_type": config_id, ...}, ...}`
  - **支持场景**: 单Agent、Multi-Agent、混合工作流
  - **精确映射**: 每个LangGraph节点可独立配置所需服务
  - **灵活扩展**: 支持任意数量的同类型服务
  
  **Multi-Agent配置示例：**
  
  ```json
  // 智能代码审查系统 - Multi-Agent工作流配置
  {
    "service_dependencies": {
      // 代码分析节点：使用Claude进行深度分析
      "code_analyzer": {
        "llm_service": 20,          // Claude-3-Sonnet config_id
        "database_service": 8       // 代码库数据库 config_id
      },
      
      // 安全审查节点：使用GPT-4专门做安全检查
      "security_reviewer": {
        "llm_service": 15,          // GPT-4-Turbo config_id
        "database_service": 12      // 漏洞知识库 config_id
      },
      
      // 性能检查节点：使用专用模型和多个数据源
      "performance_checker": {
        "llm_service": 25,          // 专门的代码性能模型 config_id
        "database_service": 15,     // 性能基准数据库 config_id
        "vector_db": 18            // 性能模式向量库 config_id
      },
      
      // Web研究节点：查找相关文档和最佳实践
      "web_researcher": {
        "search_service": 23,       // Google搜索 config_id
        "llm_service": 16          // GPT-3.5用于结果筛选 config_id
      },
      
      // 最终总结节点：整合所有结果
      "final_summarizer": {
        "llm_service": 15,          // GPT-4-Turbo config_id
        "database_service": 20      // 审查报告模板库 config_id
      }
    },
    
    "workflow_definition": {
      "nodes": {
        "code_analyzer": {
          "type": "llm_processor",
          "prompt_template": "分析以下代码的逻辑结构和潜在问题：{code}",
          "require_services": ["llm_service", "database_service"]
        },
        "security_reviewer": {
          "type": "llm_processor", 
          "prompt_template": "从安全角度审查代码：{code}，参考漏洞库：{security_patterns}",
          "require_services": ["llm_service", "database_service"]
        },
        "performance_checker": {
          "type": "multi_service_processor",
          "prompt_template": "分析代码性能问题：{code}",
          "require_services": ["llm_service", "database_service", "vector_db"]
        },
        "web_researcher": {
          "type": "search_processor",
          "search_query_template": "best practices for {code_type}",
          "require_services": ["search_service", "llm_service"]
        },
        "final_summarizer": {
          "type": "llm_processor",
          "prompt_template": "整合审查结果：分析={analysis}，安全={security}，性能={performance}，最佳实践={research}",
          "require_services": ["llm_service", "database_service"]
        }
      },
      "edges": [
        ("START", ["code_analyzer", "security_reviewer", "performance_checker"]),
        (["code_analyzer", "security_reviewer", "performance_checker"], "web_researcher"),
        ("web_researcher", "final_summarizer"),
        ("final_summarizer", "END")
      ]
    }
  }
  ```
  
  **运行时服务解析机制：**
  
  ```python
  # 1. 节点配置获取
  async def get_node_execution_config(chat_id: UUID, node_name: str) -> dict:
      """获取特定节点的执行配置"""
      chat = await get_chat(chat_id)
      agent_version = await get_agent_version(chat.agent_version_id)
      
      # 解析节点服务配置
      node_services = agent_version.service_dependencies.get(node_name, {})
      
      configs = {}
      for service_type, config_id in node_services.items():
          service_config = await get_service_config(config_id)
          configs[service_type] = {
              "service_name": service_config.service_name,
              "config_data": service_config.config_data,
              "credentials": decrypt_sm4(service_config.credentials),
              "base_url": service_config.provider.base_url
          }
      
      return configs
  
  # 2. Multi-Agent节点执行
  async def execute_multi_service_node(node_name: str, config: dict, state: dict) -> dict:
      """执行多服务节点"""
      results = {}
      
      # 并行调用多个服务
      tasks = []
      if "llm_service" in config:
          tasks.append(call_llm_service(config["llm_service"], state))
      if "database_service" in config:
          tasks.append(query_database(config["database_service"], state))
      if "vector_db" in config:
          tasks.append(search_vector_db(config["vector_db"], state))
      
      # 等待所有服务调用完成
      service_results = await asyncio.gather(*tasks)
      
      # 整合结果
      if "llm_service" in config:
          results["llm_analysis"] = service_results[0]
      if "database_service" in config:
          results["database_data"] = service_results[1]
      if "vector_db" in config:
          results["similar_patterns"] = service_results[2]
      
      return {f"{node_name}_result": results}
  ```
  
  **🎯 LangGraph框架集成详细说明：**
  
  **LangGraph基础概念**
  
  LangGraph是LangChain生态系统的核心组件，专门用于构建有状态的、多Actor的AI应用程序。在我们的系统中，`workflow_definition` 字段存储的就是LangGraph工作流的完整定义。
  
  **核心特性：**
  - **状态管理**：自动管理状态在节点间的传递和持久化
  - **Multi-Agent支持**：原生支持多个AI代理的协作
  - **条件分支**：支持基于状态的条件路由和决策
  - **人机协作**：支持需要人工干预的节点
  - **并行执行**：支持节点并行处理，提高效率
  - **错误恢复**：提供重试、回滚和检查点机制
  - **流式输出**：支持实时响应和增量结果返回
  
  **LangGraph工作流结构对应关系：**
  
  ```python
  # LangGraph原生代码结构
  from langgraph.graph import StateGraph, END
  from typing import TypedDict, Annotated
  import operator
  
  class CodeReviewState(TypedDict):
      """工作流状态定义（对应workflow_definition.state）"""
      code: str
      analysis_result: dict
      security_issues: list
      performance_score: float
      final_report: dict
  
  # 创建状态图（对应我们的workflow_definition）
  workflow = StateGraph(CodeReviewState)
  
  # 添加节点（对应workflow_definition.nodes）
  workflow.add_node("code_analyzer", code_analysis_node)
  workflow.add_node("security_reviewer", security_review_node) 
  workflow.add_node("performance_checker", performance_check_node)
  workflow.add_node("final_summarizer", result_synthesis_node)
  
  # 添加边（对应workflow_definition.edges）
  workflow.add_edge("code_analyzer", "security_reviewer")
  workflow.add_conditional_edges(
      "security_reviewer",
      performance_check_condition,  # 条件函数
      {
          "performance_checker": "performance_checker",
          "final_summarizer": "final_summarizer"
      }
  )
  workflow.add_edge("performance_checker", "final_summarizer")
  
  # 设置入口和出口
  workflow.set_entry_point("code_analyzer")
  workflow.add_edge("final_summarizer", END)
  
  # 编译工作流
  app = workflow.compile()
  ```
  
  **我们系统中的workflow_definition格式：**
  
  ```json
  {
    "workflow_definition": {
      "state_schema": {
        "code": {"type": "string", "description": "待审查的代码"},
        "analysis_result": {"type": "object", "description": "代码分析结果"},
        "security_issues": {"type": "array", "description": "安全问题列表"},
        "performance_score": {"type": "number", "description": "性能评分"},
        "final_report": {"type": "object", "description": "最终审查报告"}
      },
      
      "nodes": {
        "code_analyzer": {
          "type": "llm_processor",
          "prompt_template": "请分析以下代码的结构、逻辑和潜在问题：\\n{code}",
          "require_services": ["llm_service", "database_service"],
          "output_mapping": {
            "analysis_result": "$.analysis"
          },
          "retry_config": {
            "max_retries": 3,
            "backoff_factor": 1.5
          }
        },
        
        "security_reviewer": {
          "type": "llm_processor",
          "prompt_template": "基于代码分析结果：{analysis_result}，识别安全漏洞：\\n{code}",
          "require_services": ["llm_service", "database_service"],
          "input_dependencies": ["analysis_result"],
          "output_mapping": {
            "security_issues": "$.security_findings"
          }
        },
        
        "performance_checker": {
          "type": "multi_service_processor",
          "prompt_template": "评估代码性能，参考历史数据：{analysis_result}",
          "require_services": ["llm_service", "database_service", "vector_db"],
          "condition": "analysis_result.complexity_score > 7",
          "output_mapping": {
            "performance_score": "$.performance.score"
          }
        },
        
        "final_summarizer": {
          "type": "llm_processor",
          "prompt_template": "整合审查结果生成报告：\\n分析={analysis_result}\\n安全={security_issues}\\n性能={performance_score}",
          "require_services": ["llm_service", "database_service"],
          "input_dependencies": ["analysis_result", "security_issues"],
          "output_mapping": {
            "final_report": "$.report"
          }
        }
      },
      
      "edges": [
        {"from": "START", "to": "code_analyzer"},
        {"from": "code_analyzer", "to": "security_reviewer"},
        {
          "from": "security_reviewer",
          "to": "performance_checker",
          "condition": "analysis_result.complexity_score > 7"
        },
        {
          "from": "security_reviewer", 
          "to": "final_summarizer",
          "condition": "analysis_result.complexity_score <= 7"
        },
        {"from": "performance_checker", "to": "final_summarizer"},
        {"from": "final_summarizer", "to": "END"}
      ],
      
      "parallel_execution": [
        ["code_analyzer", "initial_scan"]  // 支持并行节点
      ],
      
      "human_intervention_nodes": [
        "security_reviewer"  // 需要人工确认的节点
      ],
      
      "checkpoints": {
        "enabled": true,
        "save_after": ["security_reviewer", "performance_checker"]
      }
    }
  }
  ```
  
  **Agent执行器实现：**
  
  ```python
  class LangGraphAgentExecutor:
      """基于LangGraph的Agent执行器"""
      
      def __init__(self, agent_version: AgentVersion, chat_id: UUID):
          self.agent_version = agent_version
          self.chat_id = chat_id
          self.workflow = self.build_langgraph_workflow()
          self.service_configs = {}
      
      async def build_langgraph_workflow(self) -> StateGraph:
          """从workflow_definition构建LangGraph工作流"""
          workflow_def = self.agent_version.workflow_definition
          
          # 创建状态类
          state_class = self.create_state_class(workflow_def["state_schema"])
          
          # 创建状态图
          workflow = StateGraph(state_class)
          
          # 预加载所有节点的服务配置
          await self.preload_service_configs()
          
          # 添加节点
          for node_name, node_def in workflow_def["nodes"].items():
              node_function = await self.create_node_function(node_name, node_def)
              workflow.add_node(node_name, node_function)
          
          # 添加边
          for edge in workflow_def["edges"]:
              await self.add_edge_to_workflow(workflow, edge)
          
          # 设置并行执行
          if "parallel_execution" in workflow_def:
              for parallel_nodes in workflow_def["parallel_execution"]:
                  # LangGraph会自动并行执行没有依赖关系的节点
                  pass
          
          # 启用检查点（用于状态持久化和恢复）
          if workflow_def.get("checkpoints", {}).get("enabled", False):
              from langgraph.checkpoint.sqlite import SqliteSaver
              memory = SqliteSaver.from_conn_string(f"agent_checkpoints_{self.chat_id}.db")
              return workflow.compile(checkpointer=memory)
          
          return workflow.compile()
      
      async def preload_service_configs(self):
          """预加载所有节点的服务配置，提升执行效率"""
          for node_name, node_services in self.agent_version.service_dependencies.items():
              node_config = {}
              for service_type, config_id in node_services.items():
                  service_config = await get_service_config(config_id)
                  node_config[service_type] = {
                      "service_name": service_config.service_name,
                      "config_data": service_config.config_data,
                      "credentials": decrypt_sm4(service_config.credentials),
                      "base_url": service_config.provider.base_url,
                      "limits": service_config.limits_config
                  }
              self.service_configs[node_name] = node_config
      
      async def create_node_function(self, node_name: str, node_def: dict):
          """为每个节点创建LangGraph执行函数"""
          async def node_function(state: dict) -> dict:
              try:
                  # 检查输入依赖
                  if "input_dependencies" in node_def:
                      for dependency in node_def["input_dependencies"]:
                          if dependency not in state or state[dependency] is None:
                              raise ValueError(f"节点 {node_name} 缺少必需输入: {dependency}")
                  
                  # 获取节点服务配置
                  node_config = self.service_configs.get(node_name, {})
                  
                  # 根据节点类型执行
                  if node_def["type"] == "llm_processor":
                      result = await self.execute_llm_node(node_name, node_def, node_config, state)
                  elif node_def["type"] == "search_processor":
                      result = await self.execute_search_node(node_name, node_def, node_config, state)
                  elif node_def["type"] == "multi_service_processor":
                      result = await self.execute_multi_service_node(node_name, node_def, node_config, state)
                  elif node_def["type"] == "human_intervention":
                      result = await self.execute_human_intervention_node(node_name, node_def, state)
                  else:
                      raise ValueError(f"未知节点类型: {node_def['type']}")
                  
                  # 应用输出映射
                  if "output_mapping" in node_def:
                      result = self.apply_output_mapping(result, node_def["output_mapping"])
                  
                  # 记录执行日志
                  await self.log_node_execution(node_name, state, result)
                  
                  return result
                  
              except Exception as e:
                  # 错误处理和重试逻辑
                  return await self.handle_node_error(node_name, node_def, state, e)
          
          return node_function
      
      async def execute_llm_node(self, node_name: str, node_def: dict, node_config: dict, state: dict) -> dict:
          """执行LLM处理节点"""
          llm_config = node_config.get("llm_service")
          if not llm_config:
              raise ValueError(f"节点 {node_name} 缺少LLM服务配置")
          
          # 构建提示词，支持模板变量
          prompt = node_def["prompt_template"].format(**state)
          
          # 调用LLM服务
          response = await call_llm_service(
              prompt=prompt,
              api_key=llm_config["credentials"],
              model=llm_config["service_name"],
              base_url=llm_config["base_url"],
              **llm_config["config_data"]
          )
          
          # 如果配置了数据库服务，进行相关查询
          if "database_service" in node_config:
              db_config = node_config["database_service"]
              context_data = await query_database(db_config, state)
              # 可以在这里进一步处理数据库结果
          
          return {f"{node_name}_result": response}
      
      async def execute_multi_service_node(self, node_name: str, node_def: dict, node_config: dict, state: dict) -> dict:
          """执行多服务协作节点"""
          results = {}
          
          # 并行调用多个服务
          tasks = []
          
          if "llm_service" in node_config:
              tasks.append(self.call_llm_service_async(node_config["llm_service"], node_def, state))
          
          if "database_service" in node_config:
              tasks.append(self.query_database_async(node_config["database_service"], state))
          
          if "vector_db" in node_config:
              tasks.append(self.search_vector_db_async(node_config["vector_db"], state))
          
          if "search_service" in node_config:
              tasks.append(self.call_search_service_async(node_config["search_service"], state))
          
          # 等待所有服务调用完成
          service_results = await asyncio.gather(*tasks, return_exceptions=True)
          
          # 整合结果
          service_types = [k for k in node_config.keys()]
          for i, result in enumerate(service_results):
              if not isinstance(result, Exception):
                  results[service_types[i]] = result
              else:
                  # 记录错误但继续执行
                  await self.log_service_error(node_name, service_types[i], result)
          
          return {f"{node_name}_result": results}
      
      async def execute_human_intervention_node(self, node_name: str, node_def: dict, state: dict) -> dict:
          """执行需要人工干预的节点"""
          # 暂停工作流，等待人工处理
          human_task = {
              "chat_id": self.chat_id,
              "node_name": node_name,
              "current_state": state,
              "instruction": node_def.get("human_instruction", "需要人工处理"),
              "created_at": datetime.now()
          }
          
          # 保存到人工任务队列
          task_id = await create_human_intervention_task(human_task)
          
          # 返回特殊状态，表示等待人工处理
          return {
              "human_intervention_required": True,
              "task_id": task_id,
              "status": "awaiting_human_input"
          }
      
      async def add_edge_to_workflow(self, workflow: StateGraph, edge: dict):
          """添加边到工作流"""
          if "condition" in edge:
              # 条件边
              condition_func = self.create_condition_function(edge["condition"])
              workflow.add_conditional_edges(
                  edge["from"],
                  condition_func,
                  {
                      "true": edge["to"],
                      "false": edge.get("else_to", "END")
                  }
              )
          else:
              # 普通边
              if edge["to"] == "END":
                  workflow.add_edge(edge["from"], END)
              else:
                  workflow.add_edge(edge["from"], edge["to"])
      
      def create_condition_function(self, condition_expr: str):
          """创建条件判断函数"""
          def condition_func(state: dict) -> str:
              try:
                  # 简单的条件表达式解析（生产环境建议使用更安全的表达式引擎）
                  result = eval(condition_expr, {"__builtins__": {}}, state)
                  return "true" if result else "false"
              except Exception:
                  return "false"
          
          return condition_func
      
      async def execute(self, initial_input: dict) -> dict:
          """执行完整的Agent工作流"""
          # 设置初始状态
          initial_state = {
              **initial_input,
              "chat_id": self.chat_id,
              "agent_id": self.agent_version.agent_id,
              "execution_start_time": datetime.now()
          }
          
          # 执行工作流
          final_state = await self.workflow.ainvoke(
              initial_state,
              config={"configurable": {"thread_id": str(self.chat_id)}}
          )
          
          return final_state
      
      async def stream_execute(self, initial_input: dict):
          """流式执行工作流，支持实时响应"""
          initial_state = {
              **initial_input,
              "chat_id": self.chat_id,
              "agent_id": self.agent_version.agent_id
          }
          
          async for chunk in self.workflow.astream(
              initial_state,
              config={"configurable": {"thread_id": str(self.chat_id)}}
          ):
              yield chunk
  ```
  
  **LangGraph集成优势：**
  
  1. **原生Multi-Agent支持**：每个节点就是一个独立的Agent
  2. **状态持久化**：自动保存工作流状态，支持长时间运行
  3. **错误恢复**：节点失败时可以重试或从检查点恢复
  4. **并行执行**：自动识别和并行执行独立节点
  5. **人机协作**：原生支持需要人工干预的流程
  6. **流式响应**：支持实时返回中间结果
  7. **可视化调试**：与LangSmith集成，便于监控和调试
  8. **灵活路由**：支持基于状态的条件分支决策
  
  **与service_dependencies的完美结合：**
  
  - workflow_definition定义"做什么"（业务逻辑）
  - service_dependencies定义"用什么做"（技术配置）
  - 两者分离但协同工作，实现了关注点分离和配置灵活性
  
  **🗄️ LangGraph PostgreSQL MemorySaver集成方案：**
  
  **集成架构设计**
  
  为了实现LangGraph工作流状态持久化与现有chat系统的深度集成，我们采用分层存储架构：
  
  1. **LangGraph层**：独立的PostgreSQL schema存储工作流检查点
  2. **业务层**：扩展的chat_messages表和新增的工作流跟踪表
  3. **关联层**：通过execution_id和thread_id建立两层之间的关联
  
  **PostgreSQL MemorySaver配置**
  
  ```python
  from langgraph.checkpoint.postgres import PostgresCheckpointer
  from sqlalchemy import create_engine
  
  class IntegratedPostgresCheckpointer(PostgresCheckpointer):
      """集成chat系统的PostgreSQL检查点存储器"""
      
      def __init__(self, database_url: str, schema: str = "langgraph"):
          """初始化检查点存储器
          
          Args:
              database_url: PostgreSQL连接字符串
              schema: 独立的schema名称，避免与业务表冲突
          """
          engine = create_engine(database_url)
          super().__init__(engine, schema=schema)
          
      async def setup_schema(self):
          """设置LangGraph专用schema和表结构"""
          await super().setup_schema()
          
          # LangGraph会自动创建如下表结构：
          # CREATE SCHEMA IF NOT EXISTS langgraph;
          # 
          # CREATE TABLE langgraph.checkpoints (
          #     thread_id TEXT NOT NULL,           -- 对应chat_{chat_id}
          #     checkpoint_id TEXT NOT NULL,       -- 检查点唯一ID
          #     parent_checkpoint_id TEXT,         -- 父检查点ID
          #     checkpoint JSONB NOT NULL,         -- 完整工作流状态
          #     metadata JSONB,                    -- 额外元数据
          #     created_at TIMESTAMP DEFAULT NOW(),
          #     PRIMARY KEY (thread_id, checkpoint_id)
          # );
          # 
          # CREATE TABLE langgraph.writes (
          #     thread_id TEXT NOT NULL,
          #     checkpoint_id TEXT NOT NULL,
          #     task_id TEXT NOT NULL,
          #     idx INTEGER NOT NULL,
          #     channel TEXT NOT NULL,
          #     value JSONB,
          #     PRIMARY KEY (thread_id, checkpoint_id, task_id, idx)
          # );
          
      def get_thread_id(self, chat_id: UUID) -> str:
          """生成标准化的thread_id"""
          return f"chat_{chat_id}"
          
      def get_checkpoint_namespace(self, agent_id: UUID) -> str:
          """生成检查点命名空间"""
          return f"agent_{agent_id}"
  ```
  
  **集成的Agent执行器**
  
  ```python
  class IntegratedLangGraphExecutor:
      """集成chat系统和LangGraph的Agent执行器"""
      
      def __init__(self, database_url: str):
          self.checkpointer = IntegratedPostgresCheckpointer(database_url)
          self.db_session = get_db_session()
          
      async def execute_agent_workflow(
          self, 
          chat_id: UUID, 
          message_id: UUID, 
          user_message: str,
          agent_version: AgentVersion
      ) -> dict:
          """执行Agent工作流并与chat系统深度集成"""
          
          # 1. 创建工作流执行记录
          execution_id = uuid4()
          thread_id = self.checkpointer.get_thread_id(chat_id)
          
          execution = await self.create_workflow_execution_record({
              "execution_id": execution_id,
              "chat_id": chat_id,
              "message_id": message_id,
              "agent_version_id": agent_version.id,
              "thread_id": thread_id,
              "checkpointer_schema": "langgraph",
              "status": "running"
          })
          
          try:
              # 2. 构建LangGraph工作流
              workflow = await self.build_integrated_workflow(agent_version, execution_id)
              
              # 3. 编译工作流（配置检查点存储）
              app = workflow.compile(
                  checkpointer=self.checkpointer,
                  interrupt_before=agent_version.workflow_definition.get("human_intervention_nodes", [])
              )
              
              # 4. 配置执行参数
              config = {
                  "configurable": {
                      "thread_id": thread_id,
                      "checkpoint_ns": self.checkpointer.get_checkpoint_namespace(agent_version.agent_id)
                  }
              }
              
              # 5. 初始状态设置
              initial_state = {
                  "user_message": user_message,
                  "chat_id": str(chat_id),
                  "execution_id": str(execution_id),
                  "messages": [{"role": "user", "content": user_message}],
                  "metadata": {
                      "agent_version": agent_version.version,
                      "started_at": datetime.now().isoformat()
                  }
              }
              
              # 6. 流式执行工作流，实时更新chat_messages
              final_result = None
              node_sequence = 1
              
              async for chunk in app.astream(initial_state, config=config):
                  # 获取当前检查点ID
                  current_checkpoint = await self.checkpointer.aget(config)
                  if current_checkpoint:
                      await self.update_execution_checkpoint(execution_id, current_checkpoint.config["checkpoint_id"])
                  
                  # 处理节点执行结果
                  await self.handle_workflow_chunk(execution_id, chunk, node_sequence)
                  final_result = chunk
                  node_sequence += 1
              
              # 7. 完成执行
              await self.complete_workflow_execution(execution_id, final_result)
              
              return final_result
              
          except Exception as e:
              await self.fail_workflow_execution(execution_id, str(e))
              raise
      
      async def handle_workflow_chunk(self, execution_id: UUID, chunk: dict, sequence: int):
          """处理工作流执行块，更新chat_messages和执行记录"""
          execution = await self.get_workflow_execution(execution_id)
          
          # 提取当前节点信息
          current_node = chunk.get("__metadata__", {}).get("source", "unknown")
          
          # 更新当前执行节点
          await self.update_current_node(execution_id, current_node)
          
          # 如果是中间节点，创建进度消息
          if current_node and current_node != "END":
              progress_content = self.format_progress_message(current_node, chunk)
              if progress_content:
                  await self.create_chat_message({
                      "id": uuid4(),
                      "chat_id": execution.chat_id,
                      "role": "assistant",
                      "content": progress_content,
                      "message_type": "progress",
                      "workflow_execution_id": execution_id,
                      "workflow_node_name": current_node,
                      "workflow_status": "running",
                      "is_intermediate": True
                  })
          
          # 如果是最终结果，创建正式AI回复
          if current_node == "END" or self.is_final_result(chunk):
              final_content = self.extract_final_response(chunk)
              if final_content:
                  await self.create_chat_message({
                      "id": uuid4(),
                      "chat_id": execution.chat_id,
                      "role": "assistant", 
                      "content": final_content,
                      "message_type": "text",
                      "workflow_execution_id": execution_id,
                      "workflow_status": "completed",
                      "is_intermediate": False
                  })
      
      async def resume_workflow(self, chat_id: UUID, human_input: dict = None) -> dict:
          """从检查点恢复被中断的工作流"""
          # 获取未完成的执行记录
          execution = await self.get_pending_execution(chat_id)
          if not execution:
              raise ValueError(f"No pending workflow execution for chat {chat_id}")
          
          # 构建恢复配置
          config = {
              "configurable": {
                  "thread_id": execution.thread_id,
                  "checkpoint_ns": self.checkpointer.get_checkpoint_namespace(execution.agent_version_id)
              }
          }
          
          # 获取Agent版本信息
          agent_version = await get_agent_version(execution.agent_version_id)
          workflow = await self.build_integrated_workflow(agent_version, execution.execution_id)
          app = workflow.compile(checkpointer=self.checkpointer)
          
          # 恢复执行
          await self.update_execution_status(execution.execution_id, "running")
          
          try:
              final_result = None
              async for chunk in app.astream(human_input, config=config):
                  await self.handle_workflow_chunk(execution.execution_id, chunk, 0)
                  final_result = chunk
              
              await self.complete_workflow_execution(execution.execution_id, final_result)
              return final_result
              
          except Exception as e:
              await self.fail_workflow_execution(execution.execution_id, str(e))
              raise
      
      async def get_workflow_history(self, chat_id: UUID) -> list[dict]:
          """获取工作流执行历史（用于调试和监控）"""
          thread_id = self.checkpointer.get_thread_id(chat_id)
          
          # 从LangGraph检查点获取历史
          checkpoints = await self.checkpointer.alist({"configurable": {"thread_id": thread_id}})
          
          # 结合业务数据
          execution = await self.get_workflow_execution_by_thread(thread_id)
          node_executions = await self.get_node_executions(execution.execution_id)
          
          history = []
          for checkpoint in checkpoints:
              history.append({
                  "checkpoint_id": checkpoint.config["checkpoint_id"],
                  "parent_id": checkpoint.parent_config.get("checkpoint_id") if checkpoint.parent_config else None,
                  "state": checkpoint.values,
                  "metadata": checkpoint.metadata,
                  "created_at": checkpoint.metadata.get("created_at"),
                  "node_executions": [
                      ne for ne in node_executions 
                      if ne.started_at >= checkpoint.metadata.get("created_at", datetime.min)
                  ]
              })
          
          return sorted(history, key=lambda x: x["created_at"])
      
      async def cleanup_old_checkpoints(self, days_to_keep: int = 30):
          """清理旧的检查点数据（定期维护任务）"""
          cutoff_date = datetime.now() - timedelta(days=days_to_keep)
          
          # 清理LangGraph检查点
          await self.checkpointer.delete_old_checkpoints(cutoff_date)
          
          # 清理业务表中的旧数据
          await self.cleanup_old_workflow_executions(cutoff_date)
          
          # 清理中间消息
          await self.cleanup_intermediate_messages(cutoff_date)
  ```
  
  **状态同步和一致性保证**
  
  ```python
  class WorkflowStateManager:
      """工作流状态管理器，确保LangGraph和chat系统状态一致"""
      
      async def sync_workflow_state(self, execution_id: UUID):
          """同步工作流状态到chat_messages"""
          execution = await get_workflow_execution(execution_id)
          
          # 获取最新检查点
          config = {"configurable": {"thread_id": execution.thread_id}}
          checkpoint = await self.checkpointer.aget(config)
          
          if checkpoint:
              # 更新执行记录中的检查点ID
              await update_execution_checkpoint(execution_id, checkpoint.config["checkpoint_id"])
              
              # 同步当前节点状态
              current_node = checkpoint.values.get("__current_node__")
              if current_node:
                  await update_current_node(execution_id, current_node)
      
      async def ensure_data_consistency(self, chat_id: UUID):
          """确保数据一致性检查"""
          # 检查是否有孤儿检查点
          thread_id = f"chat_{chat_id}"
          checkpoints = await self.checkpointer.alist({"configurable": {"thread_id": thread_id}})
          
          execution = await get_workflow_execution_by_thread(thread_id)
          
          if checkpoints and not execution:
              # 有检查点但没有执行记录，可能需要清理
              logger.warning(f"Found orphaned checkpoints for thread {thread_id}")
          
          if execution and not checkpoints:
              # 有执行记录但没有检查点，可能需要重建
              logger.warning(f"Missing checkpoints for execution {execution.execution_id}")
  ```
  
  **API接口设计**
  
  ```python
  @router.post("/chats/{chat_id}/messages")
  async def send_message_with_workflow(
      chat_id: UUID,
      message_request: SendMessageRequest,
      executor: IntegratedLangGraphExecutor = Depends(get_executor)
  ):
      """发送消息并执行Agent工作流（深度集成版）"""
      
      # 1. 检查是否有未完成的工作流
      pending_execution = await executor.get_pending_execution(chat_id)
      if pending_execution:
          return {
              "status": "workflow_pending",
              "execution_id": pending_execution.execution_id,
              "message": "有工作流正在执行中，请等待完成或提供人工输入"
          }
      
      # 2. 创建用户消息
      user_message = await create_chat_message({
          "id": uuid4(),
          "chat_id": chat_id,
          "role": "user",
          "content": message_request.content,
          "message_type": "text"
      })
      
      # 3. 获取Agent配置并执行工作流
      chat = await get_chat(chat_id)
      agent_version = await get_agent_version(chat.agent_version_id)
      
      try:
          result = await executor.execute_agent_workflow(
              chat_id=chat_id,
              message_id=user_message.id,
              user_message=message_request.content,
              agent_version=agent_version
          )
          
          return {
              "status": "completed",
              "execution_id": result.get("execution_id"),
              "final_result": result
          }
          
      except WorkflowInterruptedException as e:
          # 工作流被中断，需要人工干预
          return {
              "status": "interrupted",
              "execution_id": e.execution_id,
              "intervention_required": e.intervention_data,
              "message": "工作流需要人工干预，请提供必要信息"
          }
  
  @router.post("/chats/{chat_id}/resume")
  async def resume_workflow(
      chat_id: UUID,
      resume_request: WorkflowResumeRequest,
      executor: IntegratedLangGraphExecutor = Depends(get_executor)
  ):
      """恢复被中断的工作流"""
      result = await executor.resume_workflow(chat_id, resume_request.human_input)
      
      return {
          "status": "resumed",
          "final_result": result
      }
  
  @router.get("/chats/{chat_id}/workflow-history")
  async def get_workflow_history(
      chat_id: UUID,
      executor: IntegratedLangGraphExecutor = Depends(get_executor)
  ):
      """获取工作流执行历史"""
      history = await executor.get_workflow_history(chat_id)
      
      return {
          "chat_id": chat_id,
          "workflow_history": history
      }
  
  @router.get("/workflow-executions/{execution_id}/details")
  async def get_execution_details(execution_id: UUID):
      """获取工作流执行详情"""
      execution = await get_workflow_execution(execution_id)
      node_executions = await get_node_executions(execution_id)
      
      return {
          "execution": execution,
          "node_executions": node_executions,
          "performance_metrics": calculate_performance_metrics(node_executions)
      }
  ```
  
  **集成优势总结**
  
  1. **状态持久化**：LangGraph检查点确保工作流可以跨会话恢复
  2. **用户体验**：实时进度展示，最终结果作为正式聊天消息
  3. **数据一致性**：双层存储架构确保状态同步
  4. **可观测性**：完整的执行记录和性能监控
  5. **人机协作**：原生支持工作流中断和人工干预
  6. **错误恢复**：从任意检查点恢复执行
  7. **性能优化**：独立schema避免业务表查询影响
  8. **维护便利**：自动清理机制和一致性检查
  
  **配置验证规则：**
  
  ```python
  async def validate_multi_agent_configuration(agent_version: AgentVersion) -> list[str]:
      """验证Multi-Agent配置完整性"""
      errors = []
      
      workflow_nodes = set(agent_version.workflow_definition["nodes"].keys())
      config_nodes = set(agent_version.service_dependencies.keys())
      
      # 1. 检查节点配置完整性
      missing_configs = workflow_nodes - config_nodes
      if missing_configs:
          errors.append(f"缺少节点配置：{missing_configs}")
      
      # 2. 验证服务配置有效性
      for node_name, services in agent_version.service_dependencies.items():
          for service_type, config_id in services.items():
              service_config = await get_service_config(config_id)
              if not service_config or not service_config.is_active:
                  errors.append(f"节点 {node_name} 的服务配置 {config_id} 不存在或未激活")
      
      # 3. 检查节点需求匹配
      for node_name, node_def in agent_version.workflow_definition["nodes"].items():
          required_services = set(node_def.get("require_services", []))
          provided_services = set(agent_version.service_dependencies.get(node_name, {}).keys())
          
          missing_services = required_services - provided_services
          if missing_services:
              errors.append(f"节点 {node_name} 缺少必需服务：{missing_services}")
      
      return errors
  ```
  
  **单Agent兼容性：**
  
  对于传统单Agent场景，配置格式保持简洁：
  ```json
  {
    "service_dependencies": {
      "main_agent": {
        "llm_service": 15,
        "search_service": 23,
        "vector_db": 12
      }
    }
  }
  ```
  
  **配置优势：**
  - **精确控制**: 每个节点独立配置，避免资源浪费
  - **成本优化**: 不同节点可使用不同价格档次的服务
  - **性能调优**: 针对节点特点选择最适合的服务配置
  - **故障隔离**: 单个服务故障不影响整个工作流
  - **灵活扩展**: 新增节点或服务类型无需修改现有配置
  
  **🚀 FastMCP Client-Server分离架构集成详解**
  
  **FastMCP架构特点分析：**
  
  基于参考的FastMCP框架设计，我们采用客户端与服务端分离的架构：
  
  ```
  客户端层 (MaaS System)           服务端层 (MCP Tool Servers)
  ┌─────────────────────┐         ┌──────────────────────────┐
  │   Agent Executor    │◄──────► │   MCPRootServer          │
  │                     │         │   ┌────────────────────┐ │
  │ ┌─────────────────┐ │         │   │  Topic1: Agent-123 │ │
  │ │ MCPToolManager  │ │         │   │  - HttpApiTool     │ │
  │ └─────────────────┘ │         │   │  - CodeTool        │ │
  │                     │         │   │  - DBApiTool       │ │
  │ ┌─────────────────┐ │         │   └────────────────────┘ │
  │ │ StreamClient    │ │  HTTP   │                          │
  │ │                 │◄┼────────►│   ┌────────────────────┐ │
  │ └─────────────────┘ │Streaming│   │  Topic2: Agent-456 │ │
  └─────────────────────┘         │   │  - DatabaseTool    │ │
                                  │   │  - MLTool         │ │
                                  │   └────────────────────┘ │
                                  └──────────────────────────┘
  ```
  
  **核心优势：**
  
  1. **独立部署**：工具服务独立运行，不依赖主系统
  2. **动态管理**：支持运行时工具注册、注销
  3. **多租户隔离**：Topic级别的工具和资源隔离  
  4. **HTTP Streaming**：双向流式通信，支持长时间任务
  5. **高性能优化**：HTTP/2多路复用，连接池管理，批量处理
  6. **安全隔离**：独立的MCP服务器确保工具执行安全
  
  **Agent与FastMCP工具调用流程：**
  
  ```python
  # Agent工具调用集成示例
  async def execute_agent_with_mcp_tools(chat_id: UUID, user_message: str):
      \"\"\"Agent执行中集成FastMCP工具调用\"\"\"
      
      # 1. 获取Agent配置和工具依赖
      chat = await get_chat(chat_id)
      agent_version = await get_agent_version(chat.agent_version_id)
      
      # 2. 准备MCP工具环境
      async with IntegratedMCPToolManager(MCP_SERVER_URL) as mcp:
          # 为Agent版本创建专用Topic服务器
          await mcp.prepare_agent_tools(
              agent_version.id, 
              agent_version.tool_dependencies
          )
          
          # 3. 执行LangGraph工作流，集成工具调用
          executor = LangGraphAgentExecutor(agent_version, mcp)
          
          async for result in executor.stream_execute({
              \"user_message\": user_message,
              \"chat_id\": str(chat_id)
          }):
              # 处理工作流执行结果
              if result.get(\"type\") == \"tool_call\":
                  # 工具调用进度更新
                  await update_chat_message_progress(chat_id, result)
              elif result.get(\"type\") == \"final_result\":
                  # 最终结果
                  await create_chat_message({
                      \"chat_id\": chat_id,
                      \"role\": \"assistant\", 
                      \"content\": result[\"content\"],
                      \"workflow_execution_id\": result[\"execution_id\"]
                  })
  ```
  
  **🛡️ 分开设计注意事项与最佳实践：**
  
  **1. 配置一致性保障**
  
  ```python
  class AgentConfigValidator:
      """Agent配置验证器"""
      
      async def validate_agent_configuration(self, agent_version: AgentVersion) -> list[str]:
          """验证workflow_definition与service_dependencies的一致性"""
          errors = []
          
          workflow_nodes = set(agent_version.workflow_definition.get("nodes", {}).keys())
          service_nodes = set(agent_version.service_dependencies.keys())
          
          # 检查缺失的服务配置
          missing_configs = workflow_nodes - service_nodes
          if missing_configs:
              errors.append(f"工作流节点缺少服务配置: {missing_configs}")
          
          # 检查多余的服务配置
          extra_configs = service_nodes - workflow_nodes
          if extra_configs:
              errors.append(f"存在多余的服务配置: {extra_configs}")
          
          # 验证节点服务需求匹配
          for node_name, node_def in agent_version.workflow_definition.get("nodes", {}).items():
              required_services = set(node_def.get("require_services", []))
              provided_services = set(agent_version.service_dependencies.get(node_name, {}).keys())
              
              missing_services = required_services - provided_services
              if missing_services:
                  errors.append(f"节点 {node_name} 缺少必需服务: {missing_services}")
          
          # 验证服务配置有效性
          for node_name, services in agent_version.service_dependencies.items():
              for service_type, config_id in services.items():
                  if not await self.is_valid_service_config(config_id):
                      errors.append(f"节点 {node_name} 的服务配置 {config_id} 无效或已停用")
          
          return errors
      
      async def is_valid_service_config(self, config_id: int) -> bool:
          """检查服务配置是否有效"""
          service_config = await get_service_config(config_id)
          return service_config and service_config.is_active
  
  # 使用验证器
  validator = AgentConfigValidator()
  errors = await validator.validate_agent_configuration(agent_version)
  if errors:
      raise ConfigurationError("; ".join(errors))
  ```
  
  **2. 配置向导系统**
  
  ```python
  class AgentConfigWizard:
      """Agent配置向导，简化开发者配置过程"""
      
      SERVICE_SUGGESTIONS = {
          "llm_processor": ["llm_service"],
          "search_processor": ["search_service", "llm_service"],
          "multi_service_processor": ["llm_service", "database_service", "vector_db"],
          "code_executor": ["code_executor", "llm_service"]
      }
      
      async def create_agent_config_template(self, workflow_definition: dict) -> dict:
          """基于工作流定义生成服务配置模板"""
          service_template = {}
          
          for node_name, node_def in workflow_definition.get("nodes", {}).items():
              node_type = node_def.get("type", "default")
              suggested_services = self.SERVICE_SUGGESTIONS.get(node_type, ["llm_service"])
              
              # 为每个节点生成推荐的服务配置
              service_template[node_name] = await self.suggest_service_configs(suggested_services)
          
          return {
              "workflow_definition": workflow_definition,
              "service_dependencies_template": service_template,
              "configuration_guide": self.generate_config_guide(workflow_definition)
          }
      
      async def suggest_service_configs(self, service_types: list[str]) -> dict:
          """为服务类型推荐具体配置"""
          suggestions = {}
          
          for service_type in service_types:
              # 获取该服务类型的推荐配置
              recommended_configs = await get_recommended_service_configs(service_type)
              if recommended_configs:
                  suggestions[service_type] = recommended_configs[0].config_id  # 选择第一个推荐
          
          return suggestions
      
      def generate_config_guide(self, workflow_definition: dict) -> dict:
          """生成配置指南"""
          return {
              "steps": [
                  "1. 审查自动生成的服务配置模板",
                  "2. 根据业务需求调整服务配置",
                  "3. 运行配置验证确保一致性",
                  "4. 测试Agent功能"
              ],
              "node_count": len(workflow_definition.get("nodes", {})),
              "estimated_cost": self.estimate_usage_cost(workflow_definition)
          }
  ```
  
  **3. 配置模板和复用**
  
  ```python
  # 预定义配置模板，提高开发效率
  AGENT_CONFIG_TEMPLATES = {
      "code_analysis_suite": {
          "code_analyzer": {
              "llm_service": 15,      # GPT-4-Turbo 用于深度分析
              "database_service": 8   # 代码库数据库
          },
          "security_reviewer": {
              "llm_service": 20,      # Claude-3-Sonnet 专注安全
              "database_service": 12  # 漏洞知识库
          },
          "performance_checker": {
              "llm_service": 25,      # 专门的性能分析模型
              "database_service": 15, # 性能基准数据库
              "vector_db": 18        # 性能模式向量库
          }
      },
      
      "content_processing_suite": {
          "text_analyzer": {
              "llm_service": 16,      # GPT-3.5 用于文本分析
              "search_service": 23    # Google搜索引擎
          },
          "content_generator": {
              "llm_service": 15,      # GPT-4 用于内容生成
              "vector_db": 18        # 知识向量库
          }
      },
      
      "research_assistant_suite": {
          "web_researcher": {
              "search_service": 23,   # Google搜索
              "llm_service": 16      # GPT-3.5 用于结果筛选
          },
          "knowledge_synthesizer": {
              "llm_service": 15,      # GPT-4 用于知识整合
              "vector_db": 18,       # 知识向量库
              "database_service": 20  # 参考资料库
          }
      }
  }
  
  # 使用模板快速创建配置
  async def create_agent_from_template(template_name: str, workflow_definition: dict):
      """从模板创建Agent配置"""
      if template_name not in AGENT_CONFIG_TEMPLATES:
          raise ValueError(f"未知模板: {template_name}")
      
      service_dependencies = AGENT_CONFIG_TEMPLATES[template_name]
      
      # 验证模板与工作流的兼容性
      template_nodes = set(service_dependencies.keys())
      workflow_nodes = set(workflow_definition.get("nodes", {}).keys())
      
      if template_nodes != workflow_nodes:
          raise ValueError(f"模板节点 {template_nodes} 与工作流节点 {workflow_nodes} 不匹配")
      
      return await create_agent_version({
          "workflow_definition": workflow_definition,
          "service_dependencies": service_dependencies
      })
  ```
  
  **4. 配置同步和维护**
  
  ```python
  class ConfigSynchronizer:
      """配置同步器，维护配置一致性"""
      
      async def sync_workflow_and_services(self, agent_version_id: UUID) -> dict:
          """同步工作流定义和服务配置"""
          agent_version = await get_agent_version(agent_version_id)
          sync_report = {"added": [], "removed": [], "warnings": []}
          
          workflow_nodes = set(agent_version.workflow_definition.get("nodes", {}).keys())
          service_nodes = set(agent_version.service_dependencies.keys())
          
          # 自动添加缺失的服务配置
          missing_services = workflow_nodes - service_nodes
          for node in missing_services:
              node_def = agent_version.workflow_definition["nodes"][node]
              default_config = await self.suggest_default_services(node_def)
              agent_version.service_dependencies[node] = default_config
              sync_report["added"].append(f"为节点 {node} 添加默认服务配置")
          
          # 标记多余的服务配置（不自动删除，避免数据丢失）
          extra_services = service_nodes - workflow_nodes
          for node in extra_services:
              sync_report["warnings"].append(f"检测到多余的服务配置: {node}")
          
          # 保存更新
          if missing_services:
              await save_agent_version(agent_version)
              sync_report["status"] = "updated"
          else:
              sync_report["status"] = "no_changes"
          
          return sync_report
      
      async def suggest_default_services(self, node_definition: dict) -> dict:
          """为节点建议默认服务配置"""
          node_type = node_definition.get("type", "default")
          required_services = node_definition.get("require_services", ["llm_service"])
          
          default_config = {}
          for service_type in required_services:
              # 获取该服务类型的默认配置
              default_service = await get_default_service_config(service_type)
              if default_service:
                  default_config[service_type] = default_service.config_id
          
          return default_config
  ```
  
  **5. 查询优化和缓存**
  
  ```sql
  -- 创建优化视图，简化复杂查询
  CREATE VIEW agent_execution_configs AS
  SELECT 
      av.agent_id,
      av.version,
      av.id as version_id,
      node_key as node_name,
      
      -- 工作流节点定义
      (av.workflow_definition->'nodes'->node_key) as node_definition,
      
      -- 节点服务配置
      (av.service_dependencies->node_key) as node_services,
      
      -- 展开服务配置详情（需要后续JOIN）
      jsonb_object_keys(av.service_dependencies->node_key) as service_type,
      (av.service_dependencies->node_key->>jsonb_object_keys(av.service_dependencies->node_key))::int as config_id
      
  FROM agent_versions av,
       jsonb_object_keys(av.workflow_definition->'nodes') as node_key
  WHERE av.is_current = true
    AND av.service_dependencies ? node_key;
  
  -- 创建索引优化JSONB查询
  CREATE INDEX idx_agent_versions_workflow_nodes ON agent_versions USING gin((workflow_definition->'nodes'));
  CREATE INDEX idx_agent_versions_service_deps_keys ON agent_versions USING gin(service_dependencies);
  
  -- 缓存策略
  ```
  
  ```python
  from functools import lru_cache
  import asyncio
  
  class ConfigCache:
      """配置缓存管理器"""
      
      def __init__(self):
          self._cache = {}
          self._cache_ttl = 300  # 5分钟缓存
      
      @lru_cache(maxsize=1000)
      async def get_agent_execution_config(self, chat_id: UUID) -> dict:
          """缓存Agent执行配置"""
          cache_key = f"agent_config_{chat_id}"
          
          if cache_key in self._cache:
              cached_data, timestamp = self._cache[cache_key]
              if time.time() - timestamp < self._cache_ttl:
                  return cached_data
          
          # 缓存未命中，从数据库获取
          config = await self._fetch_agent_config_from_db(chat_id)
          self._cache[cache_key] = (config, time.time())
          
          return config
      
      async def invalidate_agent_config_cache(self, agent_id: UUID):
          """Agent配置更新时，失效相关缓存"""
          # 清理该Agent的所有缓存
          keys_to_remove = [k for k in self._cache.keys() if agent_id in k]
          for key in keys_to_remove:
              del self._cache[key]
  ```
  
  **6. 开发流程最佳实践**
  
  ```python
  class AgentDevelopmentWorkflow:
      """Agent开发工作流最佳实践"""
      
      async def create_agent_with_best_practices(self, agent_data: dict) -> UUID:
          """使用最佳实践创建Agent"""
          
          # 步骤1: 工作流设计和验证
          workflow_definition = agent_data["workflow_definition"]
          self.validate_workflow_design(workflow_definition)
          
          # 步骤2: 服务配置建议和选择
          config_wizard = AgentConfigWizard()
          config_template = await config_wizard.create_agent_config_template(workflow_definition)
          
          # 步骤3: 开发者审查和调整配置
          service_dependencies = agent_data.get("service_dependencies", config_template["service_dependencies_template"])
          
          # 步骤4: 配置一致性验证
          validator = AgentConfigValidator()
          agent_version = AgentVersion(
              workflow_definition=workflow_definition,
              service_dependencies=service_dependencies,
              **agent_data
          )
          errors = await validator.validate_agent_configuration(agent_version)
          if errors:
              raise ConfigurationError("配置验证失败: " + "; ".join(errors))
          
          # 步骤5: 创建Agent版本
          agent_version_id = await create_agent_version(agent_version)
          
          # 步骤6: 配置测试
          await self.test_agent_configuration(agent_version_id)
          
          return agent_version_id
      
      def validate_workflow_design(self, workflow_definition: dict):
          """验证工作流设计的合理性"""
          nodes = workflow_definition.get("nodes", {})
          edges = workflow_definition.get("edges", [])
          
          # 验证节点定义完整性
          for node_name, node_def in nodes.items():
              if not node_def.get("type"):
                  raise ValueError(f"节点 {node_name} 缺少type定义")
              if not node_def.get("require_services"):
                  raise ValueError(f"节点 {node_name} 缺少require_services定义")
          
          # 验证工作流连通性
          self.validate_workflow_connectivity(nodes, edges)
      
      def validate_workflow_connectivity(self, nodes: dict, edges: list):
          """验证工作流图的连通性"""
          # 检查是否所有节点都可达
          # 检查是否存在循环依赖
          # 检查开始和结束节点
          pass
      
      async def test_agent_configuration(self, agent_version_id: UUID):
          """测试Agent配置的有效性"""
          # 创建测试对话
          # 发送测试消息
          # 验证服务调用
          # 检查响应质量
          pass
  ```
  
  **重要提醒：**
  
  - ✅ **始终验证配置**: 每次更新后运行配置验证
  - ✅ **使用配置模板**: 提高开发效率，减少错误
  - ✅ **监控配置一致性**: 定期检查和同步配置
  - ✅ **合理使用缓存**: 平衡性能和数据一致性
  - ✅ **团队协作规范**: 明确工作流和服务配置的责任分工
  - ⚠️ **避免手动编辑**: 使用工具和API而非直接修改JSONB数据
  - ⚠️ **注意环境差异**: 测试和生产环境的服务配置可能不同
  - ⚠️ **版本兼容性**: 服务配置更新时考虑向后兼容性
  
  **用户版本使用策略：**
  
  采用**会话级版本锁定**机制，平衡用户体验和功能推广：
  
  1. **版本锁定原则**：
     - 每个对话会话锁定在创建时的Agent版本
     - 对话过程中Agent行为保持一致，避免突然变化
     - 新建对话自动使用最新版本，确保新功能推广
  
  2. **创建对话流程**：
     ```sql
     -- 1. 获取Agent当前版本
     SELECT id FROM agent_versions 
     WHERE agent_id = ? AND is_current = TRUE;
     
     -- 2. 创建对话并锁定版本
     INSERT INTO chats (user_id, agent_id, agent_version_id, title) 
     VALUES (?, ?, ?, ?);
     ```
  
  3. **消息处理流程**：
     ```sql
     -- 根据对话锁定的版本获取Agent配置
     SELECT av.workflow_definition, av.service_dependencies, 
            av.tool_dependencies, av.rag_enabled
     FROM chats c
     JOIN agent_versions av ON c.agent_version_id = av.id
     WHERE c.id = ?;
     ```
  
  4. **版本升级策略**：
     - **现有对话**：继续使用原版本，保证体验一致性
     - **新建对话**：自动使用最新版本，体验新功能
     - **升级提示**：UI提示用户Agent有新版本可用
     - **主动升级**：用户可选择升级现有对话到新版本
  
  5. **用户界面交互**：
     ```
     对话界面顶部提示：
     "💡 此Agent已发布新版本(v2.1.0)，包含代码执行功能"
     [创建新对话体验] [升级当前对话] [暂不升级]
     ```
  
  **业务场景示例：**
  
  1. **Agent使用统计更新**：
  ```sql
  -- 用户开始新对话时更新使用记录
  INSERT INTO agent_usage (user_id, agent_id, usage_count) 
  VALUES (?, ?, 1)
  ON CONFLICT (user_id, agent_id) 
  DO UPDATE SET 
      usage_count = agent_usage.usage_count + 1,
      last_used_at = CURRENT_TIMESTAMP;
  ```
  
  2. **获取Agent当前配置**：
  ```sql
  -- 使用视图简化查询，获取Agent完整信息
  SELECT name, description, version, workflow_definition, 
         service_dependencies, tool_dependencies, rag_enabled
  FROM current_agent_configs 
  WHERE id = ?;
  ```
  
  3. **对话升级到新版本**：
  ```sql
  -- 升级现有对话到Agent最新版本
  UPDATE chats 
  SET agent_version_id = (
      SELECT id FROM agent_versions 
      WHERE agent_id = chats.agent_id AND is_current = TRUE
  )
  WHERE id = ?; -- 对话ID
  ```
  
  4. **获取版本更新提示信息**：
  ```sql
  -- 检查用户的对话是否有新版本可用
  SELECT 
      c.id as chat_id,
      c.title,
      current_av.version as current_version,
      latest_av.version as latest_version,
      latest_av.changelog
  FROM chats c
  JOIN agent_versions current_av ON c.agent_version_id = current_av.id
  JOIN agent_versions latest_av ON c.agent_id = latest_av.agent_id
  WHERE c.user_id = ? 
    AND latest_av.is_current = TRUE 
    AND current_av.id != latest_av.id
    AND c.status = 'active';
  ```
  
  5. **版本使用统计分析**：
  ```sql
  -- 统计各版本的活跃对话数量
  SELECT 
      av.agent_id,
      av.version,
      COUNT(c.id) as active_chats,
      COUNT(DISTINCT c.user_id) as unique_users
  FROM agent_versions av
  JOIN chats c ON av.id = c.agent_version_id
  WHERE c.status = 'active'
  GROUP BY av.agent_id, av.version, av.id
  ORDER BY av.agent_id, av.created_at DESC;
  ```
  
  6. **个性化Agent推荐查询**：
  ```sql
  -- 基于使用历史推荐相似Agent
  WITH user_preferences AS (
      SELECT agent_id, usage_count 
      FROM agent_usage 
      WHERE user_id = ? 
      ORDER BY usage_count DESC LIMIT 5
  )
  SELECT DISTINCT c.* 
  FROM current_agent_configs c
  JOIN agent_categories ac ON c.category_id = ac.id
  WHERE ac.id IN (
      SELECT DISTINCT category_id 
      FROM current_agent_configs 
      WHERE id IN (SELECT agent_id FROM user_preferences)
  ) AND c.id NOT IN (SELECT agent_id FROM user_preferences)
  AND c.status = 'published';
  ```

  3.4 API设计

  3.4.1 Agent开发API

  @router.post("/agents")
  async def create_agent(agent_data: AgentCreateSchema):
      """创建Agent"""

  @router.put("/agents/{agent_id}/workflow")
  async def update_workflow(agent_id: UUID, workflow: WorkflowSchema):
      """更新Agent工作流"""

  @router.post("/agents/{agent_id}/test")
  async def test_agent(agent_id: UUID, test_input: str):
      """测试Agent"""

  @router.post("/agents/{agent_id}/publish")
  async def publish_agent(agent_id: UUID):
      """发布Agent到商店"""

  3.4.2 AgentStore API

  @router.get("/store/agents")
  async def search_agents(q: str, category: str = None):
      """搜索Agent"""

  @router.get("/store/agents/{agent_id}")
  async def get_agent_details(agent_id: UUID):
      """获取Agent详情"""

  @router.post("/store/agents/{agent_id}/install")
  async def install_agent(agent_id: UUID):
      """安装Agent"""

  @router.post("/store/agents/{agent_id}/review")
  async def submit_review(agent_id: UUID, review: ReviewSchema):
      """提交评价"""

  3.4.3 对话API（零配置体验）

  @router.post("/conversations")
  async def create_conversation(agent_id: UUID):
      """零配置创建对话 - 自动使用平台服务配置"""
      # 自动获取Agent的service_dependencies
      # 使用平台统一的API密钥和服务配置
      # 无需用户任何配置

  @router.post("/conversations/{conversation_id}/messages")
  async def send_message(conversation_id: UUID, message: str):
      """发送消息 - 自动应用Agent配置和平台服务设置"""
      # 从对话获取agent_version_id
      # 通过service_dependencies获取所有服务配置
      # 应用Agent开发者预配置的工作流和服务

  @router.get("/conversations/{conversation_id}/messages")
  async def get_messages(conversation_id: UUID):
      """获取对话历史"""

  @router.get("/conversations")
  async def list_conversations():
      """列出用户的所有对话"""

  3.4.4 零配置用户体验流程

  **核心优化**：基于统一的`providers`和`service_configs`表，实现真正的零配置用户体验。

  **Agent开发者流程**（支持多服务）：
  ```python
  # 1. 选择平台服务配置
  available_services = await get_platform_service_configs()
  
  selected_model = "gpt-4-turbo"  # config_id: 15
  selected_search = "google_custom_search"  # service_config_id: 101
  selected_executor = "python_sandbox"  # service_config_id: 102
  
  # 2. 配置Agent版本（支持Multi-Agent工作流）
  await create_agent_version({
      "agent_id": agent_id,
      "service_dependencies": {  # 🚀 基于节点的服务配置
          # 代码分析节点
          "code_analyzer": {
              "llm_service": 15,        # GPT-4模型服务
              "database_service": 8     # 代码库数据库
          },
          # 安全审查节点  
          "security_reviewer": {
              "llm_service": 20,        # Claude-3模型服务
              "database_service": 12    # 漏洞知识库
          },
          # Web研究节点
          "web_researcher": {
              "search_service": 101,    # Google搜索服务
              "llm_service": 16         # GPT-3.5筛选服务
          },
          # 最终总结节点
          "final_summarizer": {
              "llm_service": 15,        # GPT-4模型服务
              "vector_db": 103          # 知识向量库
          }
      },
      "workflow_definition": multi_agent_workflow,  # Multi-Agent工作流定义
      "system_prompt": "你是一个智能代码审查系统，包含多个专业Agent...",
      "tool_dependencies": ["web_search", "code_analyzer", "security_scanner"]
  })
  ```

  **用户使用流程**（真正零配置）：
  ```python
  # 1. 用户选择Agent
  agent_id = "coding-assistant-uuid"
  
  # 2. 直接创建对话（无配置步骤）
  chat = await create_conversation_zero_config(user_id, agent_id)
  
  # 3. 开始对话
  response = await send_message(chat.id, "分析这段Python代码")
  ```

  **🚀 Multi-Agent节点配置获取机制**：
  ```python
  async def get_node_execution_config(chat_id: UUID, node_name: str) -> dict:
      """获取特定节点的执行配置"""
      chat = await get_chat(chat_id)
      agent_version = await get_agent_version(chat.agent_version_id)
      
      # 获取节点的服务依赖配置
      node_services = agent_version.service_dependencies.get(node_name, {})
      
      configs = {}
      for service_type, config_id in node_services.items():
          service_config = await get_service_config(config_id)
          configs[service_type] = {
              "service_name": service_config.service_name,
              "config_data": service_config.config_data,
              "credentials": decrypt_sm4(service_config.credentials) if service_config.credentials else None,
              "limits": service_config.limits_config,
              "provider": service_config.provider.provider_name,
              "base_url": service_config.provider.base_url
          }
          
          # LLM服务特殊处理：应用模型参数覆盖
          if service_type == "llm_service" and agent_version.model_params_override:
              configs[service_type]["params"] = {
                  **service_config.config_data.get("model_params", {}),
                  **agent_version.model_params_override
              }
      
      return configs

  async def get_agent_execution_config(chat_id: UUID):
      """获取Agent完整执行配置（兼容单Agent和Multi-Agent）"""
      chat = await get_chat(chat_id)
      agent_version = await get_agent_version(chat.agent_version_id)
      
      configs = {}
      
      # 🎆 基于节点的服务配置获取（支持Multi-Agent工作流）
      if agent_version.service_dependencies:
          # Multi-Agent：每个节点独立配置
          for node_name, node_services in agent_version.service_dependencies.items():
              node_config = {}
              for service_type, config_id in node_services.items():
                  service_config = await get_service_config(config_id)
                  node_config[service_type] = {
                      "service_name": service_config.service_name,
                      "config_data": service_config.config_data,
                      "credentials": decrypt_sm4(service_config.credentials) if service_config.credentials else None,
                      "limits": service_config.limits_config,
                      "provider": service_config.provider.provider_name,
                      "base_url": service_config.provider.base_url
                  }
              
              configs[node_name] = node_config
      
      # 3. Agent特定配置
      configs['agent'] = {
          "system_prompt": agent_version.system_prompt,
          "workflow": agent_version.workflow_definition,
          "tools": agent_version.tool_dependencies,
          "rag_enabled": agent_version.rag_enabled
      }
      
      return configs
  
  # 使用示例：多服务调用
  execution_config = await get_agent_execution_config(chat_id)
  
  # LLM调用
  if 'llm_service' in execution_config:
      llm_response = await call_llm(
          credentials=execution_config['llm_service']['credentials'],
          model=execution_config['llm_service']['service_name'],
          base_url=execution_config['llm_service']['base_url'],
          params=execution_config['llm_service'].get('params', {}),
          prompt=user_message
      )
  
  # 搜索服务调用  
  if 'search_service' in execution_config:
      search_results = await call_search_service(
          credentials=execution_config['search_service']['credentials'],
          base_url=execution_config['search_service']['base_url'],
          query=search_query,
          config=execution_config['search_service']['config_data']
      )
  
  # 代码执行服务调用
  if 'code_executor' in execution_config:
      execution_result = await execute_code(
          code=python_code,
          base_url=execution_config['code_executor']['base_url'],
          config=execution_config['code_executor']['config_data']
      )
      
  # 向量数据库检索
  if 'vector_db' in execution_config:
      similar_docs = await query_vector_db(
          query=user_question,
          credentials=execution_config['vector_db']['credentials'],
          base_url=execution_config['vector_db']['base_url'],
          config=execution_config['vector_db']['config_data']
      )
  ```

  **📊 支持的服务类型分类**：
  
  | 服务类型 | 典型服务 | 配置内容 | 认证方式 |
  |---------|---------|----------|----------|
  | **llm** | GPT-4, Claude | 模型参数、提示词模板 | API Key |
  | **search** | Google搜索, Bing | 搜索参数、结果过滤 | API Key |
  | **code_executor** | Jupyter, Code Runner | 执行环境、资源限制 | Token/None |
  | **database** | PostgreSQL, Redis | 连接配置、查询限制 | 用户名密码 |
  | **storage** | AWS S3, 阿里云OSS | 存储桶、权限设置 | Access Key |
  | **api_service** | 天气API, 翻译API | 请求参数、响应格式 | API Key |
  | **vector_db** | Milvus, Pinecone | 索引配置、检索参数 | API Key |

  **成本和计费模式**：
  - 平台统一管理所有服务的API密钥和成本
  - 用户按使用量付费给平台（跨所有服务）
  - Agent开发者可获得分成收益
  - 支持精细化的服务使用限制和费用控制

  3.4.5 核心映射流程（简化直接映射架构）

  **系统架构映射关系：**

  采用简化的直接映射模式：`agent_version_id → topic_server_id → tool_execution`

  ```mermaid
  graph TB
      subgraph "Agent版本创建"
          A1[创建Agent版本]
          A2[解析tool_dependencies列表]
          A3[设置service_dependencies配置]
      end
      
      subgraph "Topic服务器管理"
          B1[生成Topic服务器ID: agent_{version_id}]
          B2[创建独立Topic服务器]
          B3[建立版本映射关系]
      end
      
      subgraph "工具注册管理"
          C1[按name匹配tool_dependencies]
          C2[注册tools到Topic服务器]
          C3[建立工具执行环境]
      end
      
      subgraph "执行调用链路"
          D1[用户发起对话]
          D2[LangGraph工作流调用工具]
          D3[通过agent_version_id定位Topic服务器]
          D4[执行工具调用]
          D5[记录到mcp_tool_call_logs]
      end
      
      A1 --> A2 --> A3
      A3 --> B1 --> B2 --> B3
      B3 --> C1 --> C2 --> C3
      C3 --> D1 --> D2 --> D3 --> D4 --> D5
  ```

  **核心映射流程实现：**

  ```python
  # 1. Agent版本创建时的映射建立
  async def create_agent_version_with_mapping(agent_data: dict) -> str:
      """创建Agent版本并建立工具映射"""
      
      # Step 1: 创建Agent版本
      agent_version = await create_agent_version({
          "agent_id": agent_data["agent_id"],
          "version": agent_data["version"],
          "workflow_definition": agent_data["workflow_definition"],
          "service_dependencies": agent_data["service_dependencies"],
          "tool_dependencies": agent_data["tool_dependencies"],  # ["web_search", "code_executor", "database_query"]
          "system_prompt": agent_data["system_prompt"]
      })
      
      # Step 2: 生成Topic服务器ID（基于版本ID）
      topic_server_id = f"agent_{agent_version.id}"
      
      # Step 3: 创建Topic服务器并建立映射关系
      await create_topic_server_with_mapping(
          server_id=topic_server_id,
          name=f"Agent-{agent_data['name']}-v{agent_data['version']}",
          agent_version_id=agent_version.id,
          description=f"Agent {agent_data['name']} 版本 {agent_data['version']} 专用工具服务器"
      )
      
      # Step 4: 按name匹配并注册工具到Topic服务器
      for tool_name in agent_version.tool_dependencies:
          # 从mcp_tools表中按name匹配工具
          tool = await get_mcp_tool_by_name(tool_name)
          if tool:
              await register_tool_to_topic_server(
                  topic_server_id=topic_server_id,
                  tool_name=tool_name,
                  tool_config=tool.manifest
              )
      
      return agent_version.id

  # 2. 工具执行时的映射解析
  async def execute_tool_via_mapping(chat_id: UUID, tool_name: str, params: dict) -> dict:
      """通过映射关系执行工具调用"""
      
      # Step 1: 从chat获取agent_version_id
      chat = await get_chat(chat_id)
      agent_version_id = chat.agent_version_id
      
      # Step 2: 通过agent_version_id定位Topic服务器
      topic_server_id = f"agent_{agent_version_id}"
      
      # Step 3: 验证Topic服务器存在
      topic_server = await get_mcp_topic_server(topic_server_id)
      if not topic_server:
          raise ValueError(f"Topic服务器 {topic_server_id} 不存在")
      
      # Step 4: 执行工具调用
      result = await call_tool_in_topic_server(
          topic_server_id=topic_server_id,
          tool_name=tool_name,
          parameters=params
      )
      
      # Step 5: 记录调用日志
      await log_tool_call({
          "tool_name": tool_name,
          "topic_server_id": topic_server_id,
          "agent_version_id": agent_version_id,
          "chat_id": chat_id,
          "call_parameters": params,
          "status": "success" if result else "error",
          "result_data": result,
          "started_at": datetime.now(),
          "completed_at": datetime.now(),
          "duration_ms": 0  # 实际计算执行时间
      })
      
      return result

  # 3. 数据库层面的映射关系维护
  async def create_topic_server_with_mapping(
      server_id: str, 
      name: str, 
      agent_version_id: UUID, 
      description: str
  ):
      """创建Topic服务器并维护映射关系"""
      
      topic_server = McpTopicServer(
          id=uuid4(),
          server_id=server_id,
          name=name,
          description=description,
          agent_version_id=agent_version_id,  # 🎯 核心映射关系
          endpoint_url=f"http://mcp-server:8000/topics/{server_id}",
          status="active",
          tool_count=0
      )
      
      await db.add(topic_server)
      await db.commit()
      
      return topic_server

  # 4. 映射关系查询优化
  async def get_topic_server_by_agent_version(agent_version_id: UUID) -> McpTopicServer:
      """通过Agent版本ID快速定位Topic服务器"""
      return await db.execute(
          select(McpTopicServer)
          .where(McpTopicServer.agent_version_id == agent_version_id)
          .where(McpTopicServer.status == "active")
      ).scalar_one_or_none()

  # 5. 工具调用统计和监控
  async def get_agent_tool_usage_stats(agent_version_id: UUID) -> dict:
      """获取Agent版本的工具使用统计"""
      stats = await db.execute(
          select(
              McpToolCallLog.tool_name,
              func.count(McpToolCallLog.id).label("call_count"),
              func.avg(McpToolCallLog.duration_ms).label("avg_duration"),
              func.count().filter(McpToolCallLog.status == "success").label("success_count"),
              func.count().filter(McpToolCallLog.status == "error").label("error_count")
          )
          .where(McpToolCallLog.agent_version_id == agent_version_id)
          .group_by(McpToolCallLog.tool_name)
      ).all()
      
      return {
          "agent_version_id": agent_version_id,
          "tool_stats": [
              {
                  "tool_name": stat.tool_name,
                  "call_count": stat.call_count,
                  "avg_duration_ms": float(stat.avg_duration or 0),
                  "success_rate": stat.success_count / stat.call_count if stat.call_count > 0 else 0,
                  "error_count": stat.error_count
              }
              for stat in stats
          ]
      }
  ```

  **映射关系的数据库约束优化：**

  ```sql
  -- 确保映射关系的数据完整性
  ALTER TABLE mcp_topic_servers 
  ADD CONSTRAINT fk_topic_server_agent_version 
  FOREIGN KEY (agent_version_id) REFERENCES agent_versions(id) ON DELETE CASCADE;

  -- 确保每个Agent版本只能有一个活跃的Topic服务器
  CREATE UNIQUE INDEX idx_unique_active_topic_per_version 
  ON mcp_topic_servers(agent_version_id, status) 
  WHERE status = 'active';

  -- 优化工具调用日志的查询性能
  CREATE INDEX idx_tool_call_logs_agent_version_tool 
  ON mcp_tool_call_logs(agent_version_id, tool_name, started_at);

  -- Topic服务器ID生成规则索引
  CREATE INDEX idx_topic_server_id_pattern 
  ON mcp_topic_servers(server_id) 
  WHERE server_id LIKE 'agent_%';
  ```

  **映射流程的关键优势：**

  1. **简化架构**: 直接通过agent_version_id生成topic_server_id，避免复杂的多级映射
  2. **高性能**: O(1)复杂度的映射查找，无需多表JOIN查询
  3. **数据一致性**: 严格的外键约束确保映射关系的完整性
  4. **易于监控**: 完整的调用链路追踪和统计分析
  5. **版本隔离**: 每个Agent版本拥有独立的工具执行环境
  6. **自动清理**: 级联删除确保数据库清洁性

  **实际业务流程示例：**

  ```python
  # 场景：用户与智能代码审查Agent对话
  
  # 1. 用户发起对话
  chat_id = await create_chat(user_id, agent_id="code-reviewer")
  
  # 2. 系统自动解析映射关系
  chat = await get_chat(chat_id)  # 获取锁定的agent_version_id
  topic_server_id = f"agent_{chat.agent_version_id}"  # 直接生成Topic服务器ID
  
  # 3. LangGraph工作流执行工具调用
  # 代码分析节点需要调用代码分析工具
  result = await execute_tool_via_mapping(
      chat_id=chat_id,
      tool_name="analyze_code",
      params={"code": user_code, "language": "python"}
  )
  
  # 4. 系统自动记录调用日志，便于监控和计费
  # mcp_tool_call_logs表中会记录完整的调用信息
  ```

  3.5 技术栈详细说明

  3.5.1 LangGraph集成

  - 状态管理：使用LangGraph的状态图管理对话流程
  - 工作流编排：可视化编辑Agent的执行逻辑
  - 条件分支：支持复杂的决策流程
  - 工具调用：集成各种外部工具和API

  3.5.2 LangChain集成

  - 模型抽象：统一的LLM接口调用
  - 提示模板：结构化的提示工程
  - 内存管理：对话上下文和长期记忆
  - 工具链：丰富的工具和组件生态

  3.5.3 安全设计

  - API密钥加密：使用国密SM4算法加密存储
  - 权限控制：基于RBAC的细粒度权限管理
  - 沙箱执行：Agent代码在安全沙箱中执行
  - 审计日志：完整的操作审计记录

  4. 实施计划

  4.1 开发阶段划分

  第一阶段：基础架构搭建（4周）

  1. 创建Agent模块DDD结构
    - 定义Agent领域模型和仓储接口
    - 实现基础的Agent CRUD操作
    - 创建Agent开发API
  2. 扩展用户系统
    - 为DEVELOPER角色添加Agent开发权限
    - 实现用户配置管理系统

  第二阶段：AgentStore商店系统（6周）

  3. 实现AgentStore核心功能
    - Agent发布和审核流程
    - 搜索和分类系统
    - 评价和推荐机制

  第三阶段：对话系统重构（5周）

  4. 扩展Conversation模块
    - 基于现有chat_controller扩展
    - 集成LangGraph状态管理
    - 实现多会话并发管理

  第四阶段：工具集成（6周）

  5. 构建Integration模块
    - MCP工具协议实现
    - RAG知识系统集成
    - LangGraph工作流优化

  第五阶段：系统优化（3周）

  6. 完善系统功能
    - 性能优化和缓存策略
    - 监控和日志系统
    - 测试覆盖和文档完善

  4.2 技术风险评估

  高风险项：

  - LangGraph工作流的复杂性管理
  - 多Agent并发执行的性能优化
  - MCP工具的安全沙箱实现

  缓解策略：

  - 建立原型验证关键技术点
  - 实施渐进式功能发布策略
  - 建立完善的监控和告警机制

  5. 总结

  本系统设计基于现有MaaS平台的成熟DDD架构，充分利用已有的用户管理、模型配置等基础设施。通过引入LangGraph和LangChain技术栈，构建一个功能完
  整、架构清晰的多用户Agent开发和使用平台。

  系统的核心优势：
  - 架构一致性：遵循现有DDD模式，易于维护和扩展
  - 技术先进性：采用LangGraph/LangChain主流Agent开发框架
  - 安全可靠性：完善的权限控制和数据加密机制
  - 用户体验：直观的开发工具和流畅的使用体验

  通过分阶段实施，可以在保证质量的前提下，逐步构建出一个完整的Agent生态系统。
  