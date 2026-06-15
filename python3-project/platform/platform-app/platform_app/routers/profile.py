"""应用端个人中心路由：通过管理端 API 操作用户资料。"""

from fastapi import APIRouter, Depends

from platform_app.schemas.user import UserProfileUpdate, UserPasswordUpdate
from platform_app.schemas.response import ApiResponse
from platform_app.utils.exceptions import BadRequestException
from platform_app.utils.logger import get_logger

from platform_app.dependencies.auth import get_current_user
from platform_app.client.admin_client import admin_client, AdminClientError
from platform_app.models import UserInfo

logger = get_logger(__name__)
router = APIRouter(prefix="/api/profile", tags=["个人中心"])


@router.get("/me", response_model=ApiResponse)
def get_profile(current_user: UserInfo = Depends(get_current_user)):
    """获取当前用户资料（从管理端 API 缓存中获取）。"""
    return ApiResponse.success(data=current_user.model_dump())


@router.put("/me", response_model=ApiResponse)
def update_profile(
    data: UserProfileUpdate,
    current_user: UserInfo = Depends(get_current_user),
):
    """更新当前用户资料（调用管理端 API）。"""
    try:
        user_data = admin_client.update_profile(current_user.id, data.model_dump(exclude_none=True))
    except AdminClientError as e:
        raise BadRequestException(e.message)

    logger.info("平台应用端用户更新资料: id=%s username=%s", current_user.id, current_user.username)
    return ApiResponse.success(data=user_data)


@router.post("/change-password", response_model=ApiResponse)
def change_password(
    data: UserPasswordUpdate,
    current_user: UserInfo = Depends(get_current_user),
):
    """修改密码（调用管理端 API）。"""
    try:
        admin_client.change_password(current_user.id, data.old_password, data.new_password)
    except AdminClientError as e:
        raise BadRequestException(e.message)

    # 修改密码后清除用户缓存
    admin_client.invalidate_user_cache(current_user.id)

    logger.info("平台应用端用户修改密码: id=%s username=%s", current_user.id, current_user.username)
    return ApiResponse.success(message="密码修改成功")
