from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentTreeNode
from app.schemas.response import ApiResponse
from app.services.department_service import DepartmentService
from app.dependencies.auth import require_permissions

router = APIRouter(prefix="/api/departments", tags=["部门管理"])


@router.get("/tree", response_model=ApiResponse)
def get_department_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:dept:list")),
):
    """获取部门树结构。"""
    service = DepartmentService(db)
    tree = service.get_tree()
    return ApiResponse.success(data=tree)


@router.get("", response_model=ApiResponse)
def list_departments(
    keyword: Optional[str] = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:dept:list")),
):
    """获取分页部门列表。"""
    service = DepartmentService(db)
    result = service.get_page(keyword=keyword, page=page, page_size=page_size)
    return ApiResponse.success(data=result)


@router.get("/all", response_model=ApiResponse)
def list_all_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:dept:list")),
):
    """获取所有部门（用于下拉选择）。"""
    service = DepartmentService(db)
    depts = service.get_all()
    return ApiResponse.success(data=[DepartmentResponse.model_validate(d) for d in depts])


@router.get("/{dept_id}", response_model=ApiResponse)
def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:dept:query")),
):
    """根据 ID 获取部门。"""
    service = DepartmentService(db)
    dept = service.get_by_id(dept_id)
    return ApiResponse.success(data=DepartmentResponse.model_validate(dept))


@router.post("", response_model=ApiResponse)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:dept:add")),
):
    """创建新部门。"""
    service = DepartmentService(db)
    dept = service.create(data)
    return ApiResponse.success(data=DepartmentResponse.model_validate(dept))


@router.put("/{dept_id}", response_model=ApiResponse)
def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:dept:edit")),
):
    """更新部门信息。"""
    service = DepartmentService(db)
    dept = service.update(dept_id, data)
    return ApiResponse.success(data=DepartmentResponse.model_validate(dept))


@router.delete("/{dept_id}", response_model=ApiResponse)
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:dept:remove")),
):
    """删除部门。"""
    service = DepartmentService(db)
    service.delete(dept_id)
    return ApiResponse.success(message="部门删除成功")
