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

"""用户接口层 - 路由汇总"""

from fastapi import APIRouter

from user.interface.auth_controller import router as auth_router
from user.interface.role_controller import router as role_router
from user.interface.user_controller import router as user_router

# 创建用户模块的主路由
router = APIRouter(prefix="/api/v1", tags=["用户"])

# 包含子路由
router.include_router(auth_router)
router.include_router(role_router)
router.include_router(user_router)

# 导出路由
__all__ = ["router"]
