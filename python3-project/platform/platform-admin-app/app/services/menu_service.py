from sqlalchemy.orm import Session

from app.database.models import Menu
from app.repositories.repository import MenuRepository
from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse, MenuTreeNode
from app.utils.exceptions import NotFoundException, BadRequestException
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MenuService:
    """菜单管理业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.menu_repo = MenuRepository(db)

    def get_by_id(self, menu_id: int) -> Menu:
        menu = self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("菜单不存在")
        return menu

    def get_all(self) -> list[Menu]:
        return self.menu_repo.get_all()

    def get_tree(self) -> list[MenuTreeNode]:
        """从扁平列表构建菜单树。"""
        menus = self.get_all()
        nodes = {m.id: MenuTreeNode(
            id=m.id, name=m.name, parent_id=m.parent_id, path=m.path,
            component=m.component, icon=m.icon, menu_type=m.menu_type,
            permission_key=m.permission_key, sort_order=m.sort_order,
            visible=m.visible, status=m.status, is_external=m.is_external,
            is_cache=m.is_cache, created_at=m.created_at, children=[],
        ) for m in menus}

        tree = []
        for m in menus:
            node = nodes[m.id]
            if m.parent_id and m.parent_id in nodes:
                nodes[m.parent_id].children.append(node)
            else:
                tree.append(node)
        return tree

    def create(self, data: MenuCreate) -> Menu:
        menu = Menu(
            name=data.name,
            parent_id=data.parent_id,
            path=data.path,
            component=data.component,
            icon=data.icon,
            menu_type=data.menu_type,
            permission_key=data.permission_key,
            sort_order=data.sort_order,
            visible=data.visible,
            status=data.status,
            is_external=data.is_external,
            is_cache=data.is_cache,
        )
        menu = self.menu_repo.create(menu)
        self.db.commit()
        self.db.refresh(menu)
        logger.info("菜单已创建: id=%d 名称='%s'", menu.id, menu.name)
        return menu

    def update(self, menu_id: int, data: MenuUpdate) -> Menu:
        menu = self.get_by_id(menu_id)

        update_fields = [
            "name", "parent_id", "path", "component", "icon",
            "menu_type", "permission_key", "sort_order", "visible",
            "status", "is_external", "is_cache",
        ]
        for field in update_fields:
            value = getattr(data, field, None)
            if value is not None:
                setattr(menu, field, value)

        # 防止循环自引用: 上级不能是自己或自己的后代
        if menu.parent_id is not None:
            if menu.parent_id == menu_id:
                raise BadRequestException("菜单不能是自己的上级")
            if self._is_descendant(menu_id, menu.parent_id):
                raise BadRequestException("检测到循环引用: 上级是该菜单的后代")

        menu = self.menu_repo.update(menu)
        self.db.commit()
        self.db.refresh(menu)
        logger.info("菜单已更新: id=%d 名称='%s'", menu.id, menu.name)
        return menu

    def _is_descendant(self, ancestor_id: int, check_id: int) -> bool:
        """检查 check_id 是否是 ancestor_id 的后代。"""
        all_menus = self.menu_repo.get_all()
        menu_map = {m.id: m for m in all_menus}
        current_id = check_id
        visited = set()
        while current_id and current_id not in visited:
            visited.add(current_id)
            if current_id == ancestor_id:
                return True
            parent = menu_map.get(current_id)
            current_id = parent.parent_id if parent else None
        return False

    def delete(self, menu_id: int) -> None:
        menu = self.get_by_id(menu_id)
        # 检查子菜单
        all_menus = self.menu_repo.get_all()
        if any(m.parent_id == menu_id for m in all_menus):
            raise BadRequestException("不能删除有子菜单的菜单")
        self.menu_repo.delete(menu)
        self.db.commit()
        logger.info("菜单已删除: id=%d 名称='%s'", menu_id, menu.name)

    def get_menus_by_ids(self, ids: list[int]) -> list[Menu]:
        if not ids:
            return []
        return self.menu_repo.get_by_ids(ids)

    def build_user_menu_tree(self, menu_ids: list[int]) -> list[dict]:
        """根据用户的菜单 ID 构建菜单树。

        自动包含祖先菜单以确保树结构完整。
        例如，如果用户只有"用户管理"菜单，"系统管理"目录
        也会作为其父级被包含进来。
        """
        menus = self.get_menus_by_ids(menu_ids)

        # 构建所有菜单的 ID 映射
        all_menus_map = {m.id: m for m in self.get_all()}

        # 收集所有菜单 ID（包括祖先）
        full_ids = set()
        for m in menus:
            current_id = m.id
            while current_id and current_id not in full_ids:
                full_ids.add(current_id)
                parent = all_menus_map.get(current_id)
                current_id = parent.parent_id if parent else None

        # 构建可见的非按钮菜单映射
        menu_map = {}
        for mid in full_ids:
            m = all_menus_map.get(mid)
            if m and m.menu_type != "button" and m.visible:
                menu_map[m.id] = {
                    "id": m.id,
                    "name": m.name,
                    "parent_id": m.parent_id,
                    "path": m.path,
                    "component": m.component,
                    "icon": m.icon,
                    "menu_type": m.menu_type,
                    "permission_key": m.permission_key,
                    "sort_order": m.sort_order,
                    "visible": m.visible,
                    "is_external": m.is_external,
                    "children": [],
                }

        # 构建菜单树
        tree = []
        for mid in full_ids:
            if mid not in menu_map:
                continue
            node = menu_map[mid]
            parent_id = node["parent_id"]
            if parent_id and parent_id in menu_map:
                menu_map[parent_id]["children"].append(node)
            else:
                tree.append(node)
        return tree
