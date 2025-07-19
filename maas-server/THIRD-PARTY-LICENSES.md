# 第三方许可证声明 - MaaS Server

本文档列出了 MaaS Server 项目中使用的所有第三方依赖及其许可证信息。

## 运行时依赖

### FastAPI

- **版本**: >=0.115.0
- **许可证**: MIT License
- **用途**: Web 框架
- **项目地址**: https://github.com/tiangolo/fastapi

### Uvicorn

- **版本**: >=0.34.0
- **许可证**: BSD License
- **用途**: ASGI 服务器
- **项目地址**: https://github.com/encode/uvicorn

### SQLAlchemy

- **版本**: >=2.0.36
- **许可证**: MIT License
- **用途**: ORM 框架
- **项目地址**: https://github.com/sqlalchemy/sqlalchemy

### Alembic

- **版本**: >=1.14.0
- **许可证**: MIT License
- **用途**: 数据库迁移工具
- **项目地址**: https://github.com/sqlalchemy/alembic

### psycopg2-binary

- **版本**: >=2.9.10
- **许可证**: LGPL with exceptions (允许商业使用)
- **用途**: PostgreSQL 数据库适配器
- **项目地址**: https://github.com/psycopg/psycopg2

### Redis

- **版本**: >=5.2.0
- **许可证**: MIT License
- **用途**: Redis 客户端
- **项目地址**: https://github.com/redis/redis-py

### Pydantic

- **版本**: >=2.10.2
- **许可证**: MIT License
- **用途**: 数据验证和序列化
- **项目地址**: https://github.com/pydantic/pydantic

### PyJWT

- **版本**: >=2.8.0
- **许可证**: MIT License
- **用途**: JWT 令牌处理
- **项目地址**: https://github.com/jpadilla/pyjwt

### python-multipart

- **版本**: >=0.0.12
- **许可证**: Apache License 2.0
- **用途**: 多部分表单数据解析
- **项目地址**: https://github.com/andrew-d/python-multipart

### httpx

- **版本**: >=0.28.1
- **许可证**: BSD License
- **用途**: HTTP 客户端
- **项目地址**: https://github.com/encode/httpx

### Celery

- **版本**: >=5.4.0
- **许可证**: BSD License
- **用途**: 分布式任务队列
- **项目地址**: https://github.com/celery/celery

### pymilvus

- **版本**: >=2.5.2
- **许可证**: Apache License 2.0
- **用途**: Milvus 向量数据库客户端
- **项目地址**: https://github.com/milvus-io/pymilvus

### loguru

- **版本**: >=0.7.3
- **许可证**: MIT License
- **用途**: 日志记录
- **项目地址**: https://github.com/Delgan/loguru

### asyncpg

- **版本**: >=0.30.0
- **许可证**: Apache License 2.0
- **用途**: 异步 PostgreSQL 驱动
- **项目地址**: https://github.com/MagicStack/asyncpg

### cryptography

- **版本**: >=45.0.5
- **许可证**: Apache License 2.0 / BSD License (双许可证)
- **用途**: 加密库
- **项目地址**: https://github.com/pyca/cryptography

### uuid7

- **版本**: >=0.1.0
- **许可证**: MIT License
- **用途**: UUID7 生成
- **项目地址**: https://github.com/stevesimmons/uuid7

## 开发依赖

### pytest

- **版本**: >=8.3.4
- **许可证**: MIT License
- **用途**: 测试框架
- **项目地址**: https://github.com/pytest-dev/pytest

### pytest-asyncio

- **版本**: >=0.24.0
- **许可证**: Apache License 2.0
- **用途**: 异步测试支持
- **项目地址**: https://github.com/pytest-dev/pytest-asyncio

### pytest-cov

- **版本**: >=6.0.0
- **许可证**: MIT License
- **用途**: 测试覆盖率
- **项目地址**: https://github.com/pytest-dev/pytest-cov

### black

- **版本**: >=24.10.0
- **许可证**: MIT License
- **用途**: 代码格式化
- **项目地址**: https://github.com/psf/black

### ruff

- **版本**: >=0.4.0
- **许可证**: MIT License
- **用途**: 代码检查和格式化
- **项目地址**: https://github.com/astral-sh/ruff

### mypy

- **版本**: >=1.13.0
- **许可证**: MIT License
- **用途**: 静态类型检查
- **项目地址**: https://github.com/python/mypy

### pre-commit

- **版本**: >=4.0.1
- **许可证**: MIT License
- **用途**: Git 预提交钩子
- **项目地址**: https://github.com/pre-commit/pre-commit

## 许可证兼容性声明

所有列出的第三方依赖都与 Apache License 2.0 兼容，可以在本项目中安全使用。

### 许可证类型说明

- **MIT License**: 宽松的开源许可证，允许商业使用、修改和分发
- **BSD License**: 宽松的开源许可证，类似于 MIT，允许商业使用
- **Apache License 2.0**: 宽松的开源许可证，提供专利保护
- **LGPL with exceptions**: 允许动态链接的 LGPL 许可证

## 版权声明

本项目尊重所有第三方库的版权和许可证条款。如果您发现任何许可证信息错误或遗漏，请及时联系我们进行更正。

## 更新说明

本文档会随着依赖项的更新而定期维护。最后更新时间：2025 年 1 月 19 日

---

**注意**: 在生产环境部署前，请确保所有依赖项的许可证都符合您的使用要求。
