import secrets
import string
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from app.schemas.response import ApiResponse, PageResponse
from app.services.user_service import UserService
from app.services.audit_service import log_audit
from app.dependencies.auth import get_current_user, require_permissions

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=ApiResponse)
def list_users(
    keyword: Optional[str] = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:user:list")),
):
    """获取分页用户列表（支持数据范围权限）。"""
    service = UserService(db)
    result = service.get_page(keyword=keyword, page=page, page_size=page_size, current_user=current_user)
    return ApiResponse.success(data=result)


@router.get("/{user_id}", response_model=ApiResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:user:query")),
):
    """根据 ID 获取用户。"""
    service = UserService(db)
    user = service.get_by_id(user_id)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.post("", response_model=ApiResponse)
def create_user(
    request: Request,
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:user:add")),
):
    """创建新用户。"""
    service = UserService(db)
    user = service.create(data)
    log_audit(action="CREATE", module="用户管理", description=f"创建用户: {user.username}", user_id=current_user.id, username=current_user.username, ip_address=request.client.host if request.client else None, status=True)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.put("/{user_id}", response_model=ApiResponse)
def update_user(
    request: Request,
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:user:edit")),
):
    """更新用户信息。"""
    service = UserService(db)
    user = service.update(user_id, data)
    log_audit(action="UPDATE", module="用户管理", description=f"更新用户 id={user_id}", user_id=current_user.id, username=current_user.username, ip_address=request.client.host if request.client else None, status=True)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.delete("/{user_id}", response_model=ApiResponse)
def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:user:remove")),
):
    """删除用户。"""
    service = UserService(db)
    service.delete(user_id)
    log_audit(action="DELETE", module="用户管理", description=f"删除用户 id={user_id}", user_id=current_user.id, username=current_user.username, ip_address=request.client.host if request.client else None, status=True)
    return ApiResponse.success(message="用户删除成功")


@router.put("/{user_id}/reset-password", response_model=ApiResponse)
def reset_password(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:user:resetPwd")),
):
    """重置用户密码（管理员操作）：后端随机生成强密码并返回。"""
    service = UserService(db)
    # 生成 12 位随机强密码
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    service.reset_password(user_id, new_password)
    log_audit(action="RESET_PASSWORD", module="用户管理", description=f"管理员重置用户 id={user_id} 密码", user_id=current_user.id, username=current_user.username, ip_address=request.client.host if request.client else None, status=True)
    return ApiResponse.success(message="密码重置成功", data={"new_password": new_password})


@router.put("/{user_id}/change-password", response_model=ApiResponse)
def change_password(
    request: Request,
    user_id: int,
    data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改自己的密码。"""
    if current_user.id != user_id and not current_user.is_admin:
        from app.utils.exceptions import ForbiddenException
        raise ForbiddenException("不能修改其他用户的密码")
    service = UserService(db)
    service.change_password(user_id, data.old_password, data.new_password)
    log_audit(action="CHANGE_PASSWORD", module="用户管理", description=f"用户 id={user_id} 修改密码", user_id=current_user.id, username=current_user.username, ip_address=request.client.host if request.client else None, status=True)
    return ApiResponse.success(message="密码修改成功")
