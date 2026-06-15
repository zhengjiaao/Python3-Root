from sqlalchemy.orm import Session

from app.database.models import Permission
from app.repositories.repository import PermissionRepository
from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.utils.exceptions import NotFoundException, BadRequestException, ConflictException
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PermissionService:
    """权限管理业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.perm_repo = PermissionRepository(db)

    def get_by_id(self, perm_id: int) -> Permission:
        perm = self.perm_repo.get_by_id(perm_id)
        if not perm:
            raise NotFoundException("权限不存在")
        return perm

    def get_all(self) -> list[Permission]:
        return self.perm_repo.get_all()

    def create(self, data: PermissionCreate) -> Permission:
        if self.perm_repo.exists_by_key(data.permission_key):
            raise ConflictException(f"权限标识 '{data.permission_key}' 已存在")
        perm = Permission(
            name=data.name,
            permission_key=data.permission_key,
            type=data.type,
            parent_id=data.parent_id,
            path=data.path,
            method=data.method,
            sort_order=data.sort_order,
            status=data.status,
        )
        perm = self.perm_repo.create(perm)
        self.db.commit()
        self.db.refresh(perm)
        logger.info("权限已创建: id=%d 标识='%s'", perm.id, perm.permission_key)
        return perm

    def update(self, perm_id: int, data: PermissionUpdate) -> Permission:
        perm = self.get_by_id(perm_id)

        if data.permission_key is not None and self.perm_repo.exists_by_key(data.permission_key, exclude_id=perm_id):
            raise ConflictException(f"权限标识 '{data.permission_key}' 已存在")

        update_fields = [
            "name", "permission_key", "type", "parent_id",
            "path", "method", "sort_order", "status",
        ]
        for field in update_fields:
            value = getattr(data, field, None)
            if value is not None:
                setattr(perm, field, value)

        perm = self.perm_repo.update(perm)
        self.db.commit()
        self.db.refresh(perm)
        logger.info("权限已更新: id=%d 标识='%s'", perm.id, perm.permission_key)
        return perm

    def delete(self, perm_id: int) -> None:
        perm = self.get_by_id(perm_id)
        # 检查是否有角色使用了该权限
        if perm.roles:
            role_names = ", ".join(r.name for r in perm.roles)
            raise BadRequestException(
                f"不能删除权限 '{perm.name}'，因为它被角色使用: {role_names}"
            )
        self.perm_repo.delete(perm)
        self.db.commit()
        logger.info("权限已删除: id=%d 标识='%s'", perm_id, perm.permission_key)
