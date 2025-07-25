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

"""数据初始化器抽象接口"""

from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class DataInitializer(ABC):
    """数据初始化器抽象基类"""

    @abstractmethod
    async def initialize(self, session: AsyncSession) -> bool:
        """初始化模块数据

        Args:
            session: 数据库会话

        Returns:
            bool: 初始化是否成功
        """
        pass

    @abstractmethod
    def get_module_name(self) -> str:
        """获取模块名称"""
        pass

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """获取依赖的模块列表

        Returns:
            list[str]: 依赖模块名称列表，空列表表示无依赖
        """
        pass
