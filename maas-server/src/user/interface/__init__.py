"""用户接口层 - 路由汇总"""

from fastapi import APIRouter

from .auth_controller import router as auth_router
from .user_controller import router as user_router


# 创建用户模块的主路由
router = APIRouter(prefix="/api/v1", tags=["用户"])

# 包含子路由
router.include_router(auth_router)
router.include_router(user_router)

# 导出路由
__all__ = ["router"]