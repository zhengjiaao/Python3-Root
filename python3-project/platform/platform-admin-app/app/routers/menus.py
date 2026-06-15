from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User
from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse, MenuTreeNode
from app.schemas.response import ApiResponse
from app.services.menu_service import MenuService
from app.dependencies.auth import require_permissions

router = APIRouter(prefix="/api/menus", tags=["菜单管理"])


@router.get("/tree", response_model=ApiResponse)
def get_menu_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:menu:list")),
):
    """获取菜单树结构。"""
    service = MenuService(db)
    tree = service.get_tree()
    return ApiResponse.success(data=tree)


@router.get("", response_model=ApiResponse)
def list_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:menu:list")),
):
    """获取所有菜单（扁平列表）。"""
    service = MenuService(db)
    menus = service.get_all()
    return ApiResponse.success(data=[MenuResponse.model_validate(m) for m in menus])


@router.get("/{menu_id}", response_model=ApiResponse)
def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:menu:query")),
):
    """根据 ID 获取菜单。"""
    service = MenuService(db)
    menu = service.get_by_id(menu_id)
    return ApiResponse.success(data=MenuResponse.model_validate(menu))


@router.post("", response_model=ApiResponse)
def create_menu(
    data: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:menu:add")),
):
    """创建新菜单。"""
    service = MenuService(db)
    menu = service.create(data)
    return ApiResponse.success(data=MenuResponse.model_validate(menu))


@router.put("/{menu_id}", response_model=ApiResponse)
def update_menu(
    menu_id: int,
    data: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:menu:edit")),
):
    """更新菜单信息。"""
    service = MenuService(db)
    menu = service.update(menu_id, data)
    return ApiResponse.success(data=MenuResponse.model_validate(menu))


@router.delete("/{menu_id}", response_model=ApiResponse)
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:menu:remove")),
):
    """删除菜单。"""
    service = MenuService(db)
    service.delete(menu_id)
    return ApiResponse.success(message="菜单删除成功")
