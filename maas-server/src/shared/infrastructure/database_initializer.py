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

"""数据库初始化协调器 - 管理各模块数据初始化"""

from shared.infrastructure.logging_service import get_logger

from shared.domain.initializer import DataInitializer
from shared.infrastructure.database import async_session_factory

logger = get_logger()


class DatabaseInitializationCoordinator:
    """数据库初始化协调器"""

    def __init__(self) -> None:
        self._initializers: list[DataInitializer] = []
        self._register_initializers()

    def _register_initializers(self) -> None:
        """注册各模块初始化器"""
        # 动态导入并注册各模块的初始化器
        try:
            from user.infrastructure.data_initializer import UserDataInitializer
            self._initializers.append(UserDataInitializer())
        except ImportError:
            logger.warning("用户模块初始化器未找到")

    def _sort_by_dependencies(self) -> list[DataInitializer]:
        """根据依赖关系对初始化器进行拓扑排序"""
        sorted_initializers = []
        processed_modules = set()
        remaining_initializers = self._initializers.copy()

        while remaining_initializers:
            # 找到没有未满足依赖的初始化器
            ready_initializers = []
            for initializer in remaining_initializers:
                dependencies = initializer.get_dependencies()
                if all(dep in processed_modules for dep in dependencies):
                    ready_initializers.append(initializer)

            if not ready_initializers:
                # 如果没有可处理的初始化器，说明存在循环依赖
                remaining_modules = [init.get_module_name() for init in remaining_initializers]
                logger.error(f"检测到循环依赖，剩余模块: {remaining_modules}")
                # 直接按原顺序处理剩余的初始化器
                sorted_initializers.extend(remaining_initializers)
                break

            # 处理就绪的初始化器
            for initializer in ready_initializers:
                sorted_initializers.append(initializer)
                processed_modules.add(initializer.get_module_name())
                remaining_initializers.remove(initializer)

        return sorted_initializers

    async def initialize_all_data(self) -> bool:
        """初始化所有模块的数据"""
        logger.info("开始初始化数据库数据...")

        if not self._initializers:
            logger.warning("没有找到任何数据初始化器")
            return True

        # 根据依赖关系排序
        sorted_initializers = self._sort_by_dependencies()

        async with async_session_factory() as session:
            try:
                success_count = 0
                total_count = len(sorted_initializers)

                for initializer in sorted_initializers:
                    module_name = initializer.get_module_name()
                    logger.info(f"正在初始化 {module_name} 模块数据...")

                    try:
                        success = await initializer.initialize(session)
                        if success:
                            success_count += 1
                            logger.info(f"{module_name} 模块数据初始化成功")
                        else:
                            logger.warning(f"{module_name} 模块数据初始化失败")
                    except Exception as e:
                        logger.error(f"{module_name} 模块数据初始化异常: {e}")

                await session.commit()
                logger.info(f"数据库初始化完成: {success_count}/{total_count} 个模块成功")
                return success_count == total_count

            except Exception as e:
                await session.rollback()
                logger.error(f"数据库初始化失败: {e}")
                return False


async def init_initial_data() -> bool:
    """初始化数据库初始数据的入口函数"""
    try:
        coordinator = DatabaseInitializationCoordinator()
        return await coordinator.initialize_all_data()
    except Exception as e:
        logger.error(f"初始化数据库初始数据失败: {e}")
        return False
