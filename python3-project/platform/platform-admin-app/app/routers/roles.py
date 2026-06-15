from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.response import ApiResponse
from app.services.role_service import RoleService
from app.dependencies.auth import require_permissions

router = APIRouter(prefix="/api/roles", tags=["角色管理"])


@router.get("", response_model=ApiResponse)
def list_roles(
    keyword: Optional[str] = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:role:list")),
):
    """获取分页角色列表。"""
    service = RoleService(db)
    result = service.get_page(keyword=keyword, page=page, page_size=page_size)
    return ApiResponse.success(data=result)


@router.get("/all", response_model=ApiResponse)
def list_all_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:role:list")),
):
    """获取所有角色（用于下拉选择）。"""
    service = RoleService(db)
    roles = service.get_all()
    return ApiResponse.success(data=[RoleResponse.model_validate(r) for r in roles])


@router.get("/{role_id}", response_model=ApiResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:role:query")),
):
    """根据 ID 获取角色。"""
    service = RoleService(db)
    role = service.get_by_id(role_id)
    return ApiResponse.success(data=RoleResponse.model_validate(role))


@router.post("", response_model=ApiResponse)
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:role:add")),
):
    """创建新角色。"""
    service = RoleService(db)
    role = service.create(data)
    return ApiResponse.success(data=RoleResponse.model_validate(role))


@router.put("/{role_id}", response_model=ApiResponse)
def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:role:edit")),
):
    """更新角色信息。"""
    service = RoleService(db)
    role = service.update(role_id, data)
    return ApiResponse.success(data=RoleResponse.model_validate(role))


@router.delete("/{role_id}", response_model=ApiResponse)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:role:remove")),
):
    """删除角色。"""
    service = RoleService(db)
    service.delete(role_id)
    return ApiResponse.success(message="角色删除成功")
