"""应用端首页路由。"""

from fastapi import APIRouter, Depends

from platform_app.schemas.response import ApiResponse
from platform_app.dependencies.auth import get_current_user_optional
from platform_app.models import UserInfo

router = APIRouter(prefix="/api", tags=["首页"])


@router.get("/home/info", response_model=ApiResponse)
def get_home_info(current_user: UserInfo = Depends(get_current_user_optional)):
    """获取首页信息。"""
    data = {
        "title": "欢迎使用平台应用端",
        "description": "Platform App 是面向用户的统一服务平台，用户体系与权限控制依赖管理端（客户端）。",
        "features": [
            {"icon": "bi-person-check", "title": "统一认证", "desc": "依赖管理端用户体系，单点登录体验一致。"},
            {"icon": "bi-shield-lock", "title": "安全可靠", "desc": "JWT 双令牌机制，Cookie HttpOnly 防护，登录失败锁定策略。"},
            {"icon": "bi-speedometer2", "title": "高效稳定", "desc": "基于 FastAPI 构建，性能优异，日志完整，审计可追溯。"},
        ],
        "user": None,
    }
    if current_user:
        data["user"] = {
            "id": current_user.id,
            "username": current_user.username,
            "nickname": current_user.nickname,
        }
    return ApiResponse.success(data=data)
