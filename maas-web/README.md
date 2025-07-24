# MaaS Web 前端应用

<div align="center">

🚀 **OpenMaaS 平台前端应用** - 基于 Vue 3 + TypeScript 构建的现代化企业级大模型服务前端

[![Vue](https://img.shields.io/badge/Vue-3.5+-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Element Plus](https://img.shields.io/badge/Element%20Plus-2.10+-409EFF?logo=element&logoColor=white)](https://element-plus.org/)
[![Vite](https://img.shields.io/badge/Vite-rolldown--vite-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE)

[功能特性](#-核心特性) • [快速开始](#-快速开始) • [开发指南](#-开发指南) • [API 文档](#-api-集成) • [贡献指南](#-贡献指南)

</div>

## ✨ 核心特性

- 🎯 **现代化架构** - Vue 3 Composition API + TypeScript
- 🎨 **企业级 UI** - Element Plus + 响应式设计
- 🔐 **完善权限** - RBAC 权限系统 + JWT Token 自动刷新
- 📊 **数据可视化** - ECharts 图表 + 仪表板监控
- 🌐 **国际化支持** - 多语言切换 + 本地化配置
- 🛡️ **安全加密** - 国密 SM2/SM3/SM4 算法支持
- 🧪 **测试完备** - Vitest 单元测试 + Playwright E2E 测试
- ⚡ **性能优化** - Vite(rolldown-vite) + 代码分割

## 🛠️ 技术栈

### 核心框架
- **Vue 3.5+** - 最新 Composition API + 响应式系统
- **TypeScript 5.8+** - 严格类型检查
- **Element Plus 2.10+** - 企业级 Vue 3 组件库
- **Vue Router 4** - 官方路由管理器
- **Pinia 3** - 现代状态管理

### 开发工具
- **Vite (rolldown-vite)** - 超快构建工具
- **ESLint 9 + Oxlint** - 代码质量检查
- **Prettier 3.5** - 代码格式化
- **TypeScript Vue Plugin** - Vue 3 类型支持

### 测试框架
- **Vitest 3** - 单元测试框架
- **Playwright 1.53** - E2E 测试框架
- **Vue Test Utils 2** - Vue 组件测试工具

### 业务功能
- **Axios 1.10** - HTTP 客户端 + 拦截器
- **ECharts 5.6** - 数据可视化图表
- **sm-crypto 0.3** - 国密算法库

## 🏗️ 功能模块

### 🔐 用户认证模块
- 用户注册/登录（支持国密加密）
- 密码重置和邮箱验证
- JWT Token 自动刷新机制
- 多因素认证（MFA）

### 👤 用户管理模块
- 个人资料管理和头像上传
- 账户设置和偏好配置
- API 密钥生成和管理
- 使用配额和计费查看

### 🤖 模型服务模块
- 模型仓库浏览和搜索
- 模型部署和版本管理
- 模型推理和批量处理
- 模型微调和训练监控

### 📚 知识库模块
- 文档上传和解析
- 向量化处理和检索
- RAG 问答和知识图谱
- 知识库权限管理

### 📱 应用构建模块
- 聊天机器人构建
- 工作流编排器
- API 集成和测试
- 应用发布和分享

### 🛡️ 管理员功能
- 用户和权限管理
- 系统监控和日志
- 审计追踪和合规
- 资源配额管理

## 📋 环境要求

- **Node.js** >= 18.0 (推荐 20.x LTS)
- **npm** >= 9.0 或 **pnpm** >= 8.0
- **浏览器支持**:
  - Chrome >= 90
  - Firefox >= 88
  - Safari >= 14
  - Edge >= 90

## 🚀 快速开始

### 1. 项目初始化

```bash
# 克隆项目
git clone <repository-url>
cd openMaas/maas-web

# 安装依赖
npm install

# 或使用 pnpm (推荐)
pnpm install
```

### 2. 环境配置

创建环境配置文件：

```bash
# 开发环境
cp .env.example .env.development

# 测试环境  
cp .env.example .env.test

# 生产环境
cp .env.example .env.production
```

**主要环境变量**：

```bash
# API 配置
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_WS_BASE_URL=ws://127.0.0.1:8000/ws

# 应用配置
VITE_APP_NAME=OpenMaaS Platform
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=企业级大模型即服务平台

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEVTOOLS=true
VITE_ENABLE_PWA=false

# 安全配置
VITE_ENABLE_CRYPTO=true
VITE_RSA_PUBLIC_KEY=your-rsa-public-key
```

### 3. 启动开发

```bash
# 启动开发服务器
npm run dev

# 开发服务器地址
# - 本地访问: http://localhost:5173
# - 网络访问: http://0.0.0.0:5173
```

### 4. 验证安装

```bash
# 类型检查
npm run type-check

# 代码检查
npm run lint

# 单元测试
npm run test:unit
```

## 💻 开发命令

### 开发服务
```bash
# 启动开发服务器（热重载）
npm run dev

# 预览构建结果
npm run preview
```

### 代码质量
```bash
# TypeScript 类型检查
npm run type-check

# ESLint + Oxlint 代码检查
npm run lint

# Prettier 代码格式化
npm run format
```

### 测试命令
```bash
# 单元测试
npm run test:unit

# 单元测试（观察模式）
npm run test:unit -- --watch

# E2E 测试（需先安装浏览器）
npx playwright install
npm run test:e2e

# E2E 测试（交互模式）
npm run test:e2e -- --ui
```

### 构建部署
```bash
# 多环境构建
npm run build           # 生产环境（默认）
npm run build:dev       # 开发环境
npm run build:test      # 测试环境  
npm run build:prod      # 生产环境

# 构建分析
npm run build -- --mode analyze

# 构建清理
rm -rf dist/
```

## 📁 项目结构

```
maas-web/
├── public/                    # 静态资源
│   └── favicon.ico           # 网站图标
├── src/
│   ├── components/           # 🧩 可复用组件
│   │   ├── charts/          #   图表组件 (EChart, PieChart)
│   │   ├── dashboard/       #   仪表板组件 (StatCard, QuickActions)
│   │   └── layout/          #   布局组件 (Header, Sidebar, MainLayout)
│   ├── composables/         # 🎣 Vue 3 组合式函数
│   │   ├── useAuth.ts       #   认证逻辑 (登录/登出/权限检查)
│   │   └── useDashboard.ts  #   仪表板数据逻辑
│   ├── router/              # 🛣️ 路由配置
│   │   └── index.ts         #   路由定义 + 权限守卫
│   ├── stores/              # 🗃️ Pinia 状态管理
│   │   ├── userStore.ts     #   用户状态 (信息/权限/设置)
│   │   └── counter.ts       #   计数器示例
│   ├── utils/               # 🔧 工具函数
│   │   ├── api.ts           #   API 客户端 + 拦截器
│   │   └── crypto.ts        #   加密工具 (国密算法)
│   ├── views/               # 📄 页面组件
│   │   ├── auth/            #   认证页面 (登录/注册/重置密码)
│   │   ├── user/            #   用户页面 (资料/设置)
│   │   ├── admin/           #   管理页面 (用户管理/审计日志)
│   │   └── maas/            #   业务页面 (模型/知识库/应用)
│   ├── types/               # 📝 TypeScript 类型定义
│   │   └── sm-crypto.d.ts   #   国密算法类型声明
│   ├── assets/              # 🎨 样式资源
│   │   ├── base.css         #   基础样式
│   │   └── main.css         #   主题样式
│   ├── App.vue              # 🏠 根组件
│   └── main.ts              # 🚀 应用入口
├── tests/                   # 🧪 测试文件
│   ├── e2e/                 #   E2E 测试
│   └── unit/                #   单元测试
├── dist/                    # 📦 构建输出
├── node_modules/            # 📚 依赖包
├── .env.*                   # 🔧 环境配置
├── package.json             # 📋 项目配置
├── vite.config.ts           # ⚡ Vite 配置
├── tsconfig.json            # 📘 TypeScript 配置
├── eslint.config.ts         # 📏 ESLint 配置
└── playwright.config.ts     # 🎭 Playwright 配置
```

## 🔐 权限系统

实现了企业级 RBAC (Role-Based Access Control) 权限管理：

### 权限模型
- **资源-动作模式**: `resource:action` 格式
- **示例权限**: `user:read`, `model:deploy`, `admin:*`
- **通配符支持**: `resource:*` 和 `*:*`
- **继承机制**: 角色权限自动继承和聚合

### 权限检查
```typescript
// 组件中使用权限检查
const { hasPermission, hasRole, checkPermissions } = useUserStore()

// 单个权限检查
if (hasPermission('model', 'deploy')) {
  // 用户有模型部署权限
}

// 多个权限检查（AND 逻辑）
if (checkPermissions(['user:read', 'user:edit'])) {
  // 用户同时拥有读取和编辑权限
}

// 角色检查
if (hasRole('admin')) {
  // 用户是管理员
}
```

### 路由守卫
- **全局认证守卫**: 自动检查登录状态
- **权限路由守卫**: 基于路由元数据验证权限
- **角色路由守卫**: 特殊角色访问控制
- **动态路由**: 根据权限动态生成菜单

## 🌐 API 集成

### HTTP 客户端特性
- **统一封装**: 基于 Axios 的 API 客户端
- **自动认证**: JWT Token 自动添加和刷新
- **请求拦截**: 自动添加认证头和加密
- **响应拦截**: 统一错误处理和数据转换
- **重试机制**: 网络异常自动重试
- **取消请求**: 组件卸载时自动取消

### API 模块
```typescript
// 认证 API
export const authApi = {
  login: (credentials: LoginRequest) => post('/auth/login', credentials),
  register: (data: RegisterRequest) => post('/auth/register', data),
  refreshToken: () => post('/auth/refresh'),
  logout: () => post('/auth/logout')
}

// 用户 API  
export const userApi = {
  getProfile: () => get('/user/profile'),
  updateProfile: (data: ProfileUpdate) => put('/user/profile', data),
  changePassword: (data: PasswordChange) => post('/user/password', data)
}

// 模型 API
export const modelApi = {
  list: (params: ModelListParams) => get('/models', { params }),
  deploy: (id: string, config: DeployConfig) => post(`/models/${id}/deploy`, config),
  inference: (id: string, input: InferenceInput) => post(`/models/${id}/inference`, input)
}
```

## 🛠️ 开发指南

### 添加新功能页面

1. **创建页面组件**
```bash
# 在对应模块下创建 Vue 组件
touch src/views/maas/NewFeatureView.vue
```

2. **配置路由**
```typescript
// src/router/index.ts
{
  path: '/maas/new-feature',
  name: 'NewFeature',
  component: () => import('@/views/maas/NewFeatureView.vue'),
  meta: {
    requiresAuth: true,        // 需要登录
    requiredPermissions: ['feature:read'], // 需要权限
    title: '新功能',            // 页面标题
    icon: 'new-feature'        // 菜单图标
  }
}
```

3. **更新侧边栏菜单**
```typescript
// src/components/layout/SidebarComponent.vue
const menuItems = [
  {
    title: '新功能',
    path: '/maas/new-feature',
    icon: 'new-feature',
    permission: 'feature:read'
  }
]
```

### 状态管理模式

**用户状态管理**:
```typescript
// stores/userStore.ts - 核心用户状态
interface UserState {
  user: User | null           // 用户信息
  token: string | null        // 认证令牌
  permissions: string[]       // 用户权限
  roles: string[]            // 用户角色
  preferences: UserPreferences // 用户偏好
}
```

**创建新的状态管理**:
```typescript
// stores/modelStore.ts - 模型管理状态
export const useModelStore = defineStore('model', () => {
  const models = ref<Model[]>([])
  const loading = ref(false)
  
  const fetchModels = async () => {
    loading.value = true
    try {
      models.value = await modelApi.list()
    } finally {
      loading.value = false
    }
  }
  
  return { models, loading, fetchModels }
})
```

### 组件开发规范

**组件文件结构**:
```vue
<!-- NewComponent.vue -->
<template>
  <div class="new-component">
    <!-- 模板内容 -->
  </div>
</template>

<script setup lang="ts">
// 导入依赖
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/userStore'

// 定义属性和事件
interface Props {
  title: string
  data?: any[]
}

interface Emits {
  change: [value: any]
  submit: [data: FormData]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const loading = ref(false)

// 计算属性
const isValid = computed(() => {
  return props.data && props.data.length > 0
})

// 生命周期
onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped>
.new-component {
  /* 组件样式 */
}
</style>
```

### API 调用最佳实践

```typescript
// composables/useModel.ts
export function useModel() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const models = ref<Model[]>([])
  
  const fetchModels = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await modelApi.list()
      models.value = response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取模型列表失败'
      console.error('Fetch models error:', err)
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading: readonly(loading),
    error: readonly(error), 
    models: readonly(models),
    fetchModels
  }
}
```

## 🧪 测试

### 单元测试

**运行测试**:
```bash
# 运行所有单元测试
npm run test:unit

# 观察模式（文件变更时自动测试）
npm run test:unit -- --watch

# 生成覆盖率报告
npm run test:unit -- --coverage
```

**测试示例**:
```typescript
// components/__tests__/StatCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatCard from '../dashboard/StatCard.vue'

describe('StatCard', () => {
  it('renders stat card with correct props', () => {
    const wrapper = mount(StatCard, {
      props: {
        title: '用户总数',
        value: '1,234',
        icon: 'user',
        trend: 'up'
      }
    })
    
    expect(wrapper.find('.stat-title').text()).toBe('用户总数')
    expect(wrapper.find('.stat-value').text()).toBe('1,234')
  })
})
```

### E2E 测试

**运行测试**:
```bash
# 安装浏览器
npx playwright install

# 运行 E2E 测试
npm run test:e2e

# 交互模式
npm run test:e2e -- --ui

# 指定浏览器
npm run test:e2e -- --project=chromium
```

**测试示例**:
```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('用户认证', () => {
  test('用户可以成功登录', async ({ page }) => {
    await page.goto('/auth/login')
    
    await page.fill('[data-testid="username"]', 'admin')
    await page.fill('[data-testid="password"]', 'Admin123!')
    await page.click('[data-testid="login-button"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
  })
})
```

## 🚀 部署

### Docker 部署

**Dockerfile**:
```dockerfile
# 多阶段构建
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build:prod

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**构建和运行**:
```bash
# 构建镜像
docker build -t maas-web:latest .

# 运行容器
docker run -p 80:80 \
  -e API_BASE_URL=https://api.example.com \
  maas-web:latest
```

### 静态部署

```bash
# 构建生产版本
npm run build:prod

# 部署到 CDN 或静态服务器
cp -r dist/* /var/www/html/

# 配置 Nginx
sudo systemctl reload nginx
```

## 🛠️ IDE 推荐配置

### VS Code 插件

**必需插件**:
- [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) - Vue 3 语言支持
- [TypeScript Vue Plugin](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin) - Vue TypeScript 支持
- [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) - 代码检查
- [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) - 代码格式化

**推荐插件**:
- [Auto Rename Tag](https://marketplace.visualstudio.com/items?itemName=formulahendry.auto-rename-tag) - 自动重命名标签
- [Bracket Pair Colorizer](https://marketplace.visualstudio.com/items?itemName=CoenraadS.bracket-pair-colorizer) - 括号配对高亮
- [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) - Git 增强
- [Thunder Client](https://marketplace.visualstudio.com/items?itemName=rangav.vscode-thunder-client) - API 测试

### VS Code 配置

**.vscode/settings.json**:
```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.formatDocument": true
  },
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "typescript.preferences.importModuleSpecifier": "relative",
  "vue.codeActions.enabled": true,
  "vue.complete.casing.tags": "kebab",
  "vue.complete.casing.props": "camel"
}
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请按照以下步骤参与项目：

### 开发流程

1. **Fork 项目**
```bash
# Fork 项目到你的 GitHub 账户
# 然后克隆到本地
git clone https://github.com/your-username/openMaas.git
cd openMaas/maas-web
```

2. **创建功能分支**
```bash
# 从 main 分支创建新的功能分支
git checkout -b feature/your-feature-name

# 或修复分支
git checkout -b fix/your-bug-fix
```

3. **开发和测试**
```bash
# 安装依赖
npm install

# 开发过程中持续运行测试
npm run test:unit -- --watch

# 提交前进行完整检查
npm run lint
npm run type-check
npm run test:unit
```

4. **提交代码**
```bash
# 使用规范的提交信息
git commit -m "feat: 添加新的模型管理功能"
git commit -m "fix: 修复用户登录权限检查问题"
git commit -m "docs: 更新 API 文档"
```

5. **推送和创建 PR**
```bash
# 推送到你的 Fork 仓库
git push origin feature/your-feature-name

# 在 GitHub 上创建 Pull Request
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
- 使用 ESLint + Prettier 自动格式化
- 遵循 Vue 3 + TypeScript 最佳实践
- 组件名使用 PascalCase
- 文件名使用 kebab-case

**测试要求**:
- 新功能必须包含单元测试
- 重要功能需要 E2E 测试
- 测试覆盖率不低于 80%

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
- Vue 3 (MIT License)
- Element Plus (MIT License)
- TypeScript (Apache 2.0 License)
- Vite (MIT License)
- 更多信息请查看 [THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md)

## 📞 支持与反馈

### 获取帮助
- 📚 **文档**: [项目文档](../docs/)
- 🐛 **问题报告**: [GitHub Issues](https://github.com/your-org/openmaas/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/your-org/openmaas/discussions)
- 📧 **邮件联系**: linkcheng1992@gmail.com

### 问题反馈模板

**Bug 报告**:
```markdown
**描述问题**
清楚简洁地描述遇到的问题。

**复现步骤**
1. 访问 '...'
2. 点击 '....'
3. 下拉到 '....'
4. 看到错误

**期望行为**
描述你期望发生的情况。

**环境信息**
- 操作系统: [如 macOS 13.0]
- 浏览器: [如 Chrome 108.0]
- Node.js 版本: [如 18.12.0]
```

---

⭐ **如果这个项目对你有帮助，请给我们一个 Star！**

💖 **感谢所有贡献者的支持！**