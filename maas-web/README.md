# MaaS Web Frontend

MaaS（Model-as-a-Service）平台的前端应用，基于 Vue 3 + TypeScript 构建的现代化 Web 应用程序。

## 项目特性

- 🚀 基于 Vue 3 Composition API 和 TypeScript
- 🎨 使用 Element Plus UI 框架
- 🔐 完整的用户认证和权限管理系统
- 📱 响应式设计，支持移动端
- 🌍 多环境构建支持（开发/测试/生产）
- ⚡ Vite 构建工具（使用 rolldown-vite）
- 🧪 完整的测试覆盖（单元测试 + E2E 测试）

## 技术栈

- **前端框架**: Vue 3 + TypeScript
- **UI 组件库**: Element Plus
- **构建工具**: Vite (rolldown-vite)
- **路由管理**: Vue Router 4
- **状态管理**: Pinia 3
- **HTTP 客户端**: Axios
- **单元测试**: Vitest
- **E2E 测试**: Playwright
- **代码规范**: ESLint + Oxlint + Prettier

## 功能模块

### 用户认证
- 用户注册/登录
- 密码重置
- 邮箱验证
- JWT Token 自动刷新

### 用户管理
- 个人资料管理
- 用户设置
- API 密钥管理
- 使用配额查看

### 管理员功能
- 用户管理
- 权限控制
- 系统监控

## 环境要求

- Node.js >= 18
- npm >= 9

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发环境

```bash
# 启动开发服务器
npm run dev

# 开发服务器将在 http://localhost:5173 启动
```

### 环境配置

项目支持多环境配置，创建对应的环境文件：

```bash
# 开发环境（默认）
.env.development

# 测试环境
.env.test

# 生产环境
.env.production
```

主要环境变量：
- `VITE_API_BASE_URL`: 后端 API 地址
- `VITE_APP_NAME`: 应用名称
- `VITE_APP_VERSION`: 应用版本

## 开发命令

```bash
# 开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码检查和修复
npm run lint

# 代码格式化
npm run format

# 单元测试
npm run test:unit

# E2E 测试（需先安装浏览器）
npx playwright install
npm run test:e2e
```

## 构建部署

```bash
# 构建生产版本
npm run build

# 构建开发版本
npm run build:dev

# 构建测试版本
npm run build:test

# 构建生产版本
npm run build:prod

# 预览构建结果
npm run preview
```

## 项目结构

```
src/
├── components/         # 公共组件
├── composables/       # Vue 3 组合式函数
│   └── useAuth.ts     # 认证相关逻辑
├── router/            # 路由配置
│   └── index.ts       # 路由定义和守卫
├── stores/            # Pinia 状态管理
│   ├── userStore.ts   # 用户状态管理
│   └── counter.ts     # 计数器示例
├── utils/             # 工具函数
│   └── api.ts         # API 客户端
├── views/             # 页面组件
│   ├── auth/          # 认证相关页面
│   ├── user/          # 用户管理页面
│   └── admin/         # 管理员页面
├── assets/            # 静态资源
├── App.vue            # 根组件
└── main.ts           # 应用入口
```

## 权限系统

项目实现了基于角色和权限的访问控制：

- **资源-动作权限模式**: `resource:action` (如 `user:read`, `admin:write`)
- **通配符权限**: 支持 `resource:*` 和 `*:*`
- **路由守卫**: 自动检查认证状态和权限
- **细粒度控制**: 组件级和功能级权限控制

## API 集成

- 统一的 API 客户端封装
- 自动 JWT Token 处理
- 请求/响应拦截器
- 错误处理和重试机制
- 支持认证、用户管理、管理员等模块 API

## 开发指南

### 添加新页面
1. 在 `src/views/` 对应模块下创建组件
2. 在 `src/router/index.ts` 添加路由配置
3. 设置适当的权限元数据 (`requiresAuth`, `requiresAdmin`)

### 状态管理
使用 Pinia 管理全局状态，主要包括：
- `userStore`: 用户信息、认证状态、权限检查
- 其他业务模块可按需添加 store

### 权限检查
```typescript
// 在组件中检查权限
const { hasPermission, hasRole } = useUserStore()

if (hasPermission('user', 'edit')) {
  // 用户有编辑权限
}

if (hasRole('admin')) {
  // 用户是管理员
}
```

## IDE 推荐配置

推荐使用 [VSCode](https://code.visualstudio.com/) 配合以下插件：

- [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) - Vue 3 支持
- [TypeScript Vue Plugin](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin) - TypeScript 支持
- [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) - 代码检查
- [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) - 代码格式化

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。