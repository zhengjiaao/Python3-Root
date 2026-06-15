from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.models import User, Role, Permission, Menu, Department


class UserRepository:
    """用户数据访问层。"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str, lock: bool = False) -> Optional[User]:
        query = self.db.query(User).filter(User.username == username)
        if lock:
            query = query.with_for_update()
        return query.first()

    def get_list(self, keyword: Optional[str] = None, page: int = 1, page_size: int = 10):
        query = self.db.query(User)
        if keyword:
            query = query.filter(
                or_(
                    User.username.contains(keyword),
                    User.nickname.contains(keyword),
                    User.email.contains(keyword),
                    User.phone.contains(keyword),
                )
            )
        total = query.count()
        items = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    def get_all(self) -> list[User]:
        return self.db.query(User).all()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.flush()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.flush()

    def update_roles(self, user: User, roles: list[Role]) -> None:
        user.roles = roles
        self.db.flush()

    def exists_by_username(self, username: str, exclude_id: Optional[int] = None) -> bool:
        query = self.db.query(User).filter(User.username == username)
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None


class RoleRepository:
    """角色数据访问层。"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_by_key(self, role_key: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.role_key == role_key).first()

    def get_list(self, keyword: Optional[str] = None, page: int = 1, page_size: int = 10):
        query = self.db.query(Role)
        if keyword:
            query = query.filter(
                or_(
                    Role.name.contains(keyword),
                    Role.role_key.contains(keyword),
                )
            )
        total = query.count()
        items = query.order_by(Role.sort_order.asc(), Role.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    def get_all(self) -> list[Role]:
        return self.db.query(Role).order_by(Role.sort_order.asc()).all()

    def create(self, role: Role) -> Role:
        self.db.add(role)
        self.db.flush()
        self.db.refresh(role)
        return role

    def update(self, role: Role) -> Role:
        self.db.flush()
        self.db.refresh(role)
        return role

    def delete(self, role: Role) -> None:
        self.db.delete(role)
        self.db.flush()

    def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        query = self.db.query(Role).filter(Role.name == name)
        if exclude_id:
            query = query.filter(Role.id != exclude_id)
        return query.first() is not None

    def exists_by_key(self, role_key: str, exclude_id: Optional[int] = None) -> bool:
        query = self.db.query(Role).filter(Role.role_key == role_key)
        if exclude_id:
            query = query.filter(Role.id != exclude_id)
        return query.first() is not None

    def get_by_ids(self, ids: list[int]) -> list[Role]:
        if not ids:
            return []
        return self.db.query(Role).filter(Role.id.in_(ids)).all()


class PermissionRepository:
    """权限数据访问层。"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, perm_id: int) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.id == perm_id).first()

    def get_all(self) -> list[Permission]:
        return self.db.query(Permission).order_by(Permission.sort_order.asc()).all()

    def get_by_ids(self, ids: list[int]) -> list[Permission]:
        if not ids:
            return []
        return self.db.query(Permission).filter(Permission.id.in_(ids)).all()

    def exists_by_key(self, permission_key: str, exclude_id: Optional[int] = None) -> bool:
        query = self.db.query(Permission).filter(Permission.permission_key == permission_key)
        if exclude_id:
            query = query.filter(Permission.id != exclude_id)
        return query.first() is not None

    def create(self, perm: Permission) -> Permission:
        self.db.add(perm)
        self.db.flush()
        self.db.refresh(perm)
        return perm

    def update(self, perm: Permission) -> Permission:
        self.db.flush()
        self.db.refresh(perm)
        return perm

    def delete(self, perm: Permission) -> None:
        self.db.delete(perm)
        self.db.flush()


class MenuRepository:
    """菜单数据访问层。"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, menu_id: int) -> Optional[Menu]:
        return self.db.query(Menu).filter(Menu.id == menu_id).first()

    def get_all(self) -> list[Menu]:
        return self.db.query(Menu).order_by(Menu.sort_order.asc()).all()

    def get_by_ids(self, ids: list[int]) -> list[Menu]:
        return self.db.query(Menu).filter(Menu.id.in_(ids)).all()

    def create(self, menu: Menu) -> Menu:
        self.db.add(menu)
        self.db.flush()
        self.db.refresh(menu)
        return menu

    def update(self, menu: Menu) -> Menu:
        self.db.flush()
        self.db.refresh(menu)
        return menu

    def delete(self, menu: Menu) -> None:
        self.db.delete(menu)
        self.db.flush()


class DepartmentRepository:
    """部门数据访问层。"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, dept_id: int) -> Optional[Department]:
        return self.db.query(Department).filter(Department.id == dept_id).first()

    def get_all(self) -> list[Department]:
        return self.db.query(Department).order_by(Department.sort_order.asc()).all()

    def get_list(self, keyword: Optional[str] = None, page: int = 1, page_size: int = 10):
        query = self.db.query(Department)
        if keyword:
            query = query.filter(Department.name.contains(keyword))
        total = query.count()
        items = query.order_by(Department.sort_order.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    def exists_by_name_under_parent(self, name: str, parent_id: Optional[int] = None, exclude_id: Optional[int] = None) -> bool:
        """检查同一父级下是否存在同名部门。"""
        query = self.db.query(Department).filter(Department.name == name)
        if parent_id is not None:
            query = query.filter(Department.parent_id == parent_id)
        else:
            query = query.filter(Department.parent_id.is_(None))
        if exclude_id:
            query = query.filter(Department.id != exclude_id)
        return query.first() is not None

    def get_descendant_ids(self, dept_id: int) -> list[int]:
        """获取指定部门及其所有后代部门的 ID（含自身）。"""
        all_depts = self.get_all()
        result = [dept_id]
        queue = [dept_id]
        while queue:
            current = queue.pop(0)
            for d in all_depts:
                if d.parent_id == current:
                    result.append(d.id)
                    queue.append(d.id)
        return result

    def create(self, dept: Department) -> Department:
        self.db.add(dept)
        self.db.flush()
        self.db.refresh(dept)
        return dept

    def update(self, dept: Department) -> Department:
        self.db.flush()
        self.db.refresh(dept)
        return dept

    def delete(self, dept: Department) -> None:
        self.db.delete(dept)
        self.db.flush()
