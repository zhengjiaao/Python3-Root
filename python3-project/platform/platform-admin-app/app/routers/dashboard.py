from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.database.models import User, Role, Menu, Department
from app.dependencies.auth import get_current_user, get_current_user_info
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
from app.config import get_settings

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/stats", response_model=ApiResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取仪表盘统计数据（任何已认证用户可用）。"""
    stats = {
        "user_count": db.query(func.count(User.id)).scalar(),
        "role_count": db.query(func.count(Role.id)).scalar(),
        "menu_count": db.query(func.count(Menu.id)).scalar(),
        "dept_count": db.query(func.count(Department.id)).scalar(),
    }
    return ApiResponse.success(data=stats)


@router.get("/system-info", response_model=ApiResponse)
def get_system_info(current_user_info: CurrentUser = Depends(get_current_user_info)):
    """获取系统信息（任何已认证用户可用）。"""
    settings = get_settings()
    info = {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
    }
    return ApiResponse.success(data=info)
