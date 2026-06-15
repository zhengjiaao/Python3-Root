from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.schemas.response import ApiResponse
from app.services.permission_service import PermissionService
from app.dependencies.auth import require_permissions

router = APIRouter(prefix="/api/permissions", tags=["权限管理"])


@router.get("", response_model=ApiResponse)
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:perm:list")),
):
    """获取所有权限（扁平列表）。"""
    service = PermissionService(db)
    permissions = service.get_all()
    return ApiResponse.success(data=[PermissionResponse.model_validate(p) for p in permissions])


@router.get("/{perm_id}", response_model=ApiResponse)
def get_permission(
    perm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:perm:query")),
):
    """根据 ID 获取权限。"""
    service = PermissionService(db)
    perm = service.get_by_id(perm_id)
    return ApiResponse.success(data=PermissionResponse.model_validate(perm))


@router.post("", response_model=ApiResponse)
def create_permission(
    data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:perm:add")),
):
    """创建新权限。"""
    service = PermissionService(db)
    perm = service.create(data)
    return ApiResponse.success(data=PermissionResponse.model_validate(perm))


@router.put("/{perm_id}", response_model=ApiResponse)
def update_permission(
    perm_id: int,
    data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:perm:edit")),
):
    """更新权限信息。"""
    service = PermissionService(db)
    perm = service.update(perm_id, data)
    return ApiResponse.success(data=PermissionResponse.model_validate(perm))


@router.delete("/{perm_id}", response_model=ApiResponse)
def delete_permission(
    perm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:perm:remove")),
):
    """删除权限。"""
    service = PermissionService(db)
    service.delete(perm_id)
    return ApiResponse.success(message="权限删除成功")
