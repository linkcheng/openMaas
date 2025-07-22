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

"""环境变量工具 - 提供.env文件查找和管理功能"""

from pathlib import Path

# 缓存查找结果，避免重复查找
_env_file_cache: Path | None = None


def find_env_file(start_path: Path | None = None) -> Path | None:
    """查找.env文件
    
    Args:
        start_path: 开始查找的路径，默认为当前文件所在目录
        
    Returns:
        找到的.env文件路径，如果没找到返回None
    """
    global _env_file_cache

    # 如果已经有缓存结果，直接返回
    if _env_file_cache is not None:
        return _env_file_cache

    if start_path is None:
        start_path = Path(__file__).resolve().parent

    # 可能的.env文件位置（按优先级排序）
    possible_paths = [
        # 项目根目录 (maas-server/.env)
        start_path.parent.parent.parent / ".env",
        # src 目录 (maas-server/src/.env)
        start_path.parent.parent / ".env",
        # config 目录 (maas-server/src/config/.env)
        start_path.parent / ".env",
        # 当前工作目录 (.env)
        Path.cwd() / ".env",
        # 用户主目录 (.env)
        Path.home() / ".env",
    ]

    # 按优先级查找存在的.env文件
    for env_path in possible_paths:
        if env_path.exists() and env_path.is_file():
            _env_file_cache = env_path
            return _env_file_cache

    # 缓存 None 结果，避免重复查找
    _env_file_cache = None
    return None


def clear_env_file_cache() -> None:
    """清除.env文件缓存
    
    当需要重新查找.env文件时调用此函数
    """
    global _env_file_cache
    _env_file_cache = None


def get_env_file_path() -> str:
    """获取环境变量配置文件路径
    
    按优先级查找 .env 文件:
    1. 项目根目录 (maas-server/.env)
    2. src 目录 (maas-server/src/.env)  
    3. config 目录 (maas-server/src/config/.env)
    4. 当前工作目录 (.env)
    5. 用户主目录 (.env)
    
    Returns:
        .env文件路径字符串，如果没找到返回空字符串
    """
    env_file = find_env_file()
    if env_file:
        return str(env_file)

    print("未找到 .env 文件, 将使用默认配置")
    return ""
