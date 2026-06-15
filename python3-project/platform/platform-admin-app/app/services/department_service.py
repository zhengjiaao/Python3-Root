from sqlalchemy.orm import Session

from app.database.models import Department
from app.repositories.repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentTreeNode
from app.schemas.response import PageResponse
from app.utils.exceptions import NotFoundException, BadRequestException, ConflictException
from app.utils.logger import get_logger
from typing import Optional

logger = get_logger(__name__)


class DepartmentService:
    """部门管理业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.dept_repo = DepartmentRepository(db)

    def get_by_id(self, dept_id: int) -> Department:
        dept = self.dept_repo.get_by_id(dept_id)
        if not dept:
            raise NotFoundException("部门不存在")
        return dept

    def get_all(self) -> list[Department]:
        return self.dept_repo.get_all()

    def get_page(self, keyword: Optional[str] = None, page: int = 1, page_size: int = 10) -> PageResponse:
        total, items = self.dept_repo.get_list(keyword=keyword, page=page, page_size=page_size)
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[DepartmentResponse.model_validate(d) for d in items],
        )

    def get_tree(self) -> list[DepartmentTreeNode]:
        """从扁平列表构建部门树。"""
        depts = self.get_all()
        nodes = {d.id: DepartmentTreeNode(
            id=d.id, name=d.name, parent_id=d.parent_id,
            sort_order=d.sort_order, status=d.status,
            leader=d.leader, phone=d.phone, email=d.email,
            created_at=d.created_at, updated_at=d.updated_at, children=[],
        ) for d in depts}

        tree = []
        for d in depts:
            node = nodes[d.id]
            if d.parent_id and d.parent_id in nodes:
                nodes[d.parent_id].children.append(node)
            else:
                tree.append(node)
        return tree

    def create(self, data: DepartmentCreate) -> Department:
        if self.dept_repo.exists_by_name_under_parent(data.name, data.parent_id):
            raise ConflictException("同级下已存在同名部门")
        dept = Department(
            name=data.name,
            parent_id=data.parent_id,
            sort_order=data.sort_order,
            status=data.status,
            leader=data.leader,
            phone=data.phone,
            email=data.email,
        )
        dept = self.dept_repo.create(dept)
        self.db.commit()
        self.db.refresh(dept)
        logger.info("部门已创建: id=%d 名称='%s'", dept.id, dept.name)
        return dept

    def update(self, dept_id: int, data: DepartmentUpdate) -> Department:
        dept = self.get_by_id(dept_id)

        update_fields = ["name", "parent_id", "sort_order", "status", "leader", "phone", "email"]
        for field in update_fields:
            value = getattr(data, field, None)
            if value is not None:
                setattr(dept, field, value)

        # 检查同名部门（同级下名称唯一）
        new_name = data.name if data.name is not None else dept.name
        new_parent_id = data.parent_id if data.parent_id is not None else dept.parent_id
        if self.dept_repo.exists_by_name_under_parent(new_name, new_parent_id, exclude_id=dept_id):
            raise ConflictException("同级下已存在同名部门")

        # 防止循环自引用: 上级不能是自己或自己的后代
        if dept.parent_id is not None:
            if dept.parent_id == dept_id:
                raise BadRequestException("部门不能是自己的上级")
            if self._is_descendant(dept_id, dept.parent_id):
                raise BadRequestException("检测到循环引用: 上级是该部门的后代")

        dept = self.dept_repo.update(dept)
        self.db.commit()
        self.db.refresh(dept)
        logger.info("部门已更新: id=%d 名称='%s'", dept.id, dept.name)
        return dept

    def _is_descendant(self, ancestor_id: int, check_id: int) -> bool:
        """检查 check_id 是否是 ancestor_id 的后代。"""
        all_depts = self.dept_repo.get_all()
        dept_map = {d.id: d for d in all_depts}
        current_id = check_id
        visited = set()
        while current_id and current_id not in visited:
            visited.add(current_id)
            if current_id == ancestor_id:
                return True
            parent = dept_map.get(current_id)
            current_id = parent.parent_id if parent else None
        return False

    def delete(self, dept_id: int) -> None:
        dept = self.get_by_id(dept_id)
        # 检查子部门
        all_depts = self.dept_repo.get_all()
        if any(d.parent_id == dept_id for d in all_depts):
            raise BadRequestException("不能删除有子部门的部门")
        # 检查是否有用户属于该部门
        if dept.users:
            user_names = ", ".join(u.username for u in dept.users)
            raise BadRequestException(
                f"不能删除部门 '{dept.name}'，因为该部门下有用户: {user_names}"
            )
        self.dept_repo.delete(dept)
        self.db.commit()
        logger.info("部门已删除: id=%d 名称='%s'", dept_id, dept.name)
