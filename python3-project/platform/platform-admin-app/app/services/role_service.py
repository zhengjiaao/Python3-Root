from typing import Optional
from sqlalchemy.orm import Session

from app.database.models import Role, Permission, Menu
from app.repositories.repository import RoleRepository, PermissionRepository, MenuRepository
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.response import PageResponse
from app.utils.exceptions import ConflictException, NotFoundException, BadRequestException
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RoleService:
    """角色管理业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.role_repo = RoleRepository(db)
        self.perm_repo = PermissionRepository(db)
        self.menu_repo = MenuRepository(db)

    def get_by_id(self, role_id: int) -> Role:
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("角色不存在")
        return role

    def get_page(self, keyword: Optional[str] = None, page: int = 1, page_size: int = 10) -> PageResponse:
        total, items = self.role_repo.get_list(keyword=keyword, page=page, page_size=page_size)
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[RoleResponse.model_validate(r) for r in items],
        )

    def get_all(self) -> list[Role]:
        return self.role_repo.get_all()

    def create(self, data: RoleCreate) -> Role:
        if self.role_repo.exists_by_name(data.name):
            raise ConflictException(f"角色名称 '{data.name}' 已存在")
        if self.role_repo.exists_by_key(data.role_key):
            raise ConflictException(f"角色标识 '{data.role_key}' 已存在")

        role = Role(
            name=data.name,
            role_key=data.role_key,
            sort_order=data.sort_order,
            status=data.status,
            remark=data.remark,
            data_scope=data.data_scope,
        )
        role = self.role_repo.create(role)

        if data.permission_ids:
            perms = self.perm_repo.get_by_ids(data.permission_ids)
            role.permissions = list(perms)
            self.db.flush()

        if data.menu_ids:
            menus = self.menu_repo.get_by_ids(data.menu_ids)
            role.menus = list(menus)
            self.db.flush()

        self.db.commit()
        self.db.refresh(role)
        logger.info("角色已创建: id=%d 名称='%s' 标识='%s'", role.id, role.name, role.role_key)
        return role

    def update(self, role_id: int, data: RoleUpdate) -> Role:
        role = self.get_by_id(role_id)

        if data.name is not None:
            if self.role_repo.exists_by_name(data.name, exclude_id=role_id):
                raise ConflictException(f"角色名称 '{data.name}' 已存在")
            role.name = data.name

        if data.role_key is not None:
            if self.role_repo.exists_by_key(data.role_key, exclude_id=role_id):
                raise ConflictException(f"角色标识 '{data.role_key}' 已存在")
            role.role_key = data.role_key

        simple_fields = ["sort_order", "status", "remark", "data_scope"]
        for field in simple_fields:
            value = getattr(data, field, None)
            if value is not None:
                setattr(role, field, value)

        role = self.role_repo.update(role)

        if data.permission_ids is not None:
            perms = self.perm_repo.get_by_ids(data.permission_ids)
            role.permissions = list(perms)
            self.db.flush()

        if data.menu_ids is not None:
            menus = self.menu_repo.get_by_ids(data.menu_ids)
            role.menus = list(menus)
            self.db.flush()

        self.db.commit()
        self.db.refresh(role)
        logger.info("角色已更新: id=%d 名称='%s'", role.id, role.name)
        return role

    def delete(self, role_id: int) -> None:
        role = self.get_by_id(role_id)
        if role.role_key == "super_admin":
            raise BadRequestException("不能删除超级管理员角色")
        # 检查是否有用户分配了该角色
        if role.users:
            user_names = ", ".join(u.username for u in role.users)
            raise BadRequestException(
                f"不能删除角色 '{role.name}'，因为它已分配给用户: {user_names}"
            )
        self.role_repo.delete(role)
        self.db.commit()
        logger.info("角色已删除: id=%d 名称='%s'", role_id, role.name)

    def get_role_permissions(self, role_id: int) -> list[Permission]:
        role = self.get_by_id(role_id)
        return list(role.permissions)

    def get_role_menus(self, role_id: int) -> list[Menu]:
        role = self.get_by_id(role_id)
        return list(role.menus)
