# 贡献指南

感谢您对 OpenMaaS 项目的关注！我们欢迎所有形式的贡献，包括但不限于代码、文档、测试、问题报告和功能建议。

## 许可证协议

通过向本项目提交贡献，您同意：

1. **许可证授权**：您的贡献将在 Apache License 2.0 下发布
2. **版权声明**：您确认拥有所提交代码的版权或已获得适当授权
3. **开源承诺**：您的贡献符合开源软件的原则和精神

## 贡献类型

### 代码贡献

- 新功能开发
- Bug 修复
- 性能优化
- 代码重构

### 文档贡献

- API 文档完善
- 使用指南编写
- 示例代码提供
- 翻译工作

### 测试贡献

- 单元测试编写
- 集成测试完善
- 性能测试添加
- 测试用例优化

## 开发流程

### 1. 准备工作

```bash
# Fork 项目到您的 GitHub 账户
# 克隆您的 Fork
git clone https://github.com/YOUR_USERNAME/openMaas.git
cd openMaas

# 添加上游仓库
git remote add upstream https://github.com/ORIGINAL_OWNER/openMaas.git
```

### 2. 创建功能分支

```bash
# 从主分支创建新分支
git checkout -b feature/your-feature-name

# 或者修复分支
git checkout -b fix/issue-number
```

### 3. 开发环境设置

#### 后端开发环境

```bash
cd maas-server
uv sync
uv run pre-commit install
```

#### 前端开发环境

```bash
cd maas-web
npm install
```

### 4. 代码开发

- 遵循项目的代码规范
- 编写必要的测试
- 确保所有测试通过
- 更新相关文档

### 5. 提交代码

```bash
# 添加更改
git add .

# 提交更改（使用有意义的提交信息）
git commit -m "feat: add new feature description"

# 推送到您的 Fork
git push origin feature/your-feature-name
```

### 6. 创建 Pull Request

1. 在 GitHub 上创建 Pull Request
2. 填写 PR 模板
3. 等待代码审查
4. 根据反馈进行修改

## 代码规范

### 后端 (Python)

- 使用 Black 进行代码格式化
- 使用 Ruff 进行代码检查
- 使用 MyPy 进行类型检查
- 遵循 PEP 8 规范

```bash
# 运行代码检查
uv run ruff check src --fix
uv run black src/
uv run mypy src/
```

### 前端 (TypeScript/Vue)

- 使用 Prettier 进行代码格式化
- 使用 ESLint 进行代码检查
- 遵循 Vue 3 最佳实践

```bash
# 运行代码检查
npm run lint
npm run format
```

## 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 类型说明

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 示例

```
feat(auth): add JWT token refresh mechanism

Implement automatic token refresh to improve user experience
and reduce login frequency.

Closes #123
```

## 测试要求

### 后端测试

```bash
# 运行所有测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=src --cov-report=html
```

### 前端测试

```bash
# 运行单元测试
npm run test:unit

# 运行 E2E 测试
npm run test:e2e
```

## 代码审查

所有代码贡献都需要经过代码审查：

1. **自动检查**：CI/CD 流水线会自动运行测试和代码检查
2. **人工审查**：至少需要一名维护者的审查和批准
3. **反馈处理**：根据审查意见及时修改代码

## 问题报告

### Bug 报告

请包含以下信息：

- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Python/Node.js 版本等）
- 错误日志

### 功能请求

请包含以下信息：

- 功能描述
- 使用场景
- 预期收益
- 实现建议

## 许可证兼容性

在添加第三方依赖时，请确保：

1. **许可证兼容**：新依赖的许可证与 Apache 2.0 兼容
2. **许可证记录**：在相应的 THIRD-PARTY-LICENSES.md 文件中记录
3. **版权声明**：保留原始版权声明

### 兼容的许可证

- MIT License
- BSD License (2-clause, 3-clause)
- Apache License 2.0
- ISC License

### 不兼容的许可证

- GPL (任何版本)
- LGPL (任何版本)
- AGPL (任何版本)
- 其他 Copyleft 许可证

## 社区准则

### 行为准则

- 尊重所有参与者
- 保持友好和专业的态度
- 欢迎新手和不同观点
- 避免人身攻击和歧视性言论

### 沟通方式

- GitHub Issues：问题报告和功能请求
- GitHub Discussions：一般讨论和问答
- Pull Request：代码审查和讨论

## 版权和署名

### 代码版权

- 所有贡献者保留其贡献的版权
- 贡献将在 Apache 2.0 许可证下发布
- 项目维护者有权管理和分发代码

### 署名政策

- 重要贡献者将被添加到 AUTHORS 文件
- 所有贡献者都会在 Git 历史中得到记录
- 特殊贡献可能会在发布说明中提及

## 发布流程

### 版本号规范

遵循 [Semantic Versioning](https://semver.org/)：

- MAJOR.MINOR.PATCH
- 主版本号：不兼容的 API 修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

### 发布检查清单

- [ ] 所有测试通过
- [ ] 文档更新完成
- [ ] 变更日志更新
- [ ] 版本号更新
- [ ] 许可证信息检查

## 联系方式

如有任何问题或建议，请通过以下方式联系我们：

- GitHub Issues: [项目问题页面]
- GitHub Discussions: [项目讨论页面]
- Email: linkcheng1992@gmail.com

感谢您的贡献！🎉
