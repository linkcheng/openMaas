# 许可证管理指南

本文档描述了 OpenMaaS 项目的许可证管理策略和最佳实践。

## 项目许可证

OpenMaaS 项目采用 **Apache License 2.0** 开源许可证。

### 选择 Apache 2.0 的原因

1. **商业友好**: 允许商业使用、修改和分发
2. **专利保护**: 提供明确的专利授权和保护
3. **兼容性好**: 与大多数开源许可证兼容
4. **企业认可**: 被广泛的企业和开源项目采用
5. **法律清晰**: 条款明确，法律风险较低

## 许可证文件结构

```
openMaas/
├── LICENSE                                    # 主许可证文件
├── NOTICE                                     # 版权声明和第三方组件信息
├── CONTRIBUTING.md                            # 贡献指南（包含许可证协议）
├── AUTHORS                                    # 贡献者列表
├── maas-server/THIRD-PARTY-LICENSES.md      # 后端第三方许可证
├── maas-web/THIRD-PARTY-LICENSES.md         # 前端第三方许可证
└── scripts/
    ├── check-licenses.py                     # 许可证合规检查
    └── add-license-headers.py                # 许可证头部添加
```

## 许可证合规要求

### 1. 第三方依赖

所有第三方依赖必须使用与 Apache 2.0 兼容的许可证：

#### ✅ 兼容的许可证

- MIT License
- BSD License (2-clause, 3-clause)
- Apache License 2.0
- ISC License
- Python Software Foundation License
- Unlicense / Public Domain

#### ❌ 不兼容的许可证

- GPL (任何版本)
- LGPL (任何版本)
- AGPL (任何版本)
- 其他 Copyleft 许可证

#### ⚠️ 需要审查的许可证

- Mozilla Public License (MPL)
- Eclipse Public License (EPL)
- LGPL with exceptions

### 2. 源代码头部

所有源代码文件都应包含 Apache 2.0 许可证头部：

#### Python 文件示例

```python
"""
Copyright 2025 MaaS Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
```

#### TypeScript/JavaScript 文件示例

```typescript
/*
 * Copyright 2025 MaaS Team
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
```

## 许可证管理工具

### 1. 许可证合规检查

```bash
# 检查所有依赖的许可证合规性
python scripts/check-licenses.py

# 输出示例：
# 🚀 OpenMaaS 许可证合规检查
# ============================================================
# 🔍 检查 Python 依赖许可证...
# 🔍 检查 NPM 依赖许可证...
#
# ============================================================
# 📋 许可证合规检查报告
# ============================================================
#
# 🐍 Python 依赖 (maas-server):
#    ✅ 兼容: 25 个
#    ❌ 不兼容: 0 个
#    ⚠️  需审查: 2 个
```

### 2. 许可证头部管理

```bash
# 预览将要添加许可证头部的文件
python scripts/add-license-headers.py --dry-run

# 为所有源代码文件添加许可证头部
python scripts/add-license-headers.py

# 为特定目录添加许可证头部
python scripts/add-license-headers.py --directory maas-server/src
```

### 3. CI/CD 集成

项目配置了 GitHub Actions 工作流 (`.github/workflows/license-check.yml`)，会在以下情况自动检查许可证合规性：

- 推送到主分支
- 创建 Pull Request
- 每周定期检查

## 添加新依赖的流程

### 1. 检查许可证兼容性

在添加新依赖前，必须确认其许可证与 Apache 2.0 兼容：

```bash
# Python 依赖
pip show <package-name>

# NPM 依赖
npm info <package-name> license
```

### 2. 更新第三方许可证文档

在相应的 `THIRD-PARTY-LICENSES.md` 文件中添加新依赖的信息：

```markdown
### Package Name

- **版本**: x.x.x
- **许可证**: MIT License
- **用途**: 功能描述
- **项目地址**: https://github.com/...
```

### 3. 运行合规检查

```bash
python scripts/check-licenses.py
```

## 贡献者许可证协议

### 贡献者许可证协议 (CLA)

通过向本项目提交贡献，贡献者同意：

1. **许可证授权**: 贡献将在 Apache License 2.0 下发布
2. **版权确认**: 贡献者拥有所提交代码的版权或已获得适当授权
3. **专利授权**: 如适用，贡献者授予项目使用相关专利的权利

### 签署流程

贡献者通过以下方式之一表示同意：

1. **Pull Request**: 在 PR 描述中包含 "I agree to the CLA"
2. **Commit 消息**: 在提交消息中包含 "Signed-off-by: Name <email>"
3. **贡献指南**: 阅读并遵循 CONTRIBUTING.md 中的指南

## 许可证变更流程

### 重大许可证变更

如需变更项目主许可证，需要：

1. **社区讨论**: 在 GitHub Discussions 中发起讨论
2. **贡献者同意**: 获得主要贡献者的同意
3. **法律审查**: 进行法律风险评估
4. **文档更新**: 更新所有相关文档和文件

### 依赖许可证变更

当依赖项许可证发生变更时：

1. **及时发现**: 通过定期检查或自动化工具发现
2. **兼容性评估**: 评估新许可证的兼容性
3. **决策制定**: 决定是否继续使用、寻找替代品或申请例外
4. **文档更新**: 更新第三方许可证文档

## 许可证违规处理

### 发现违规

如果发现许可证违规行为：

1. **立即停止**: 停止使用违规组件
2. **评估影响**: 评估对项目的影响范围
3. **寻找替代**: 寻找兼容的替代方案
4. **清理代码**: 移除违规代码或组件

### 报告违规

如果发现项目中的许可证违规，请：

1. **私下报告**: 发送邮件至 team@maas.com
2. **提供详情**: 包含违规组件和许可证信息
3. **建议解决**: 如有可能，提供解决建议

## 最佳实践

### 1. 定期审查

- 每月检查新增依赖的许可证
- 每季度全面审查所有依赖
- 每年更新第三方许可证文档

### 2. 自动化检查

- 在 CI/CD 中集成许可证检查
- 使用工具自动检测许可证变更
- 设置许可证违规告警

### 3. 文档维护

- 保持许可证文档的准确性和时效性
- 记录所有许可证相关的决策
- 提供清晰的许可证指南

### 4. 团队培训

- 定期进行许可证合规培训
- 建立许可证审查流程
- 培养团队的许可证意识

## 常见问题

### Q: 为什么选择 Apache 2.0 而不是 MIT？

A: Apache 2.0 提供了更好的专利保护，对企业用户更友好，同时保持了与 MIT 类似的宽松性。

### Q: 可以使用 LGPL 许可证的依赖吗？

A: 一般情况下不建议，但如果是动态链接且有明确的例外条款，可以考虑。需要法律审查。

### Q: 如何处理没有明确许可证的代码？

A: 不应使用没有明确许可证的代码。如果必须使用，需要联系原作者获得明确的许可。

### Q: 贡献者需要签署 CLA 吗？

A: 目前通过贡献指南中的声明即可，未来可能会引入正式的 CLA 流程。

## 联系方式

如有许可证相关问题，请联系：

- **邮箱**: team@maas.com
- **GitHub Issues**: 用于公开讨论
- **GitHub Discussions**: 用于社区讨论

---

**最后更新**: 2025 年 1 月 19 日
