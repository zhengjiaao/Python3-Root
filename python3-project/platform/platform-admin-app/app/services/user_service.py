from typing import Optional, Union
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.database.models import User, Role
from app.repositories.repository import UserRepository, RoleRepository, DepartmentRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserProfileUpdate
from app.schemas.response import PageResponse
from app.utils.security import hash_password, verify_password
from app.utils.exceptions import ConflictException, NotFoundException, BadRequestException
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _resolve_data_scope(user: Optional[User]) -> int:
    """解析用户的数据范围（取所有角色中最宽泛的）。"""
    if not user:
        return 5
    if user.is_superuser:
        return 1
    if not user.roles:
        return 5
    # 数值越小范围越大
    return min(r.data_scope or 5 for r in user.roles)

# 登录失败锁定配置
MAX_LOGIN_FAIL_COUNT = 5          # 连续失败最大次数
LOGIN_LOCK_MINUTES = 30           # 锁定时长（分钟）


class UserService:
    """用户管理业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    def get_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("用户不存在")
        return user

    def get_by_username(self, username: str) -> Optional[User]:
        return self.user_repo.get_by_username(username)

    def get_page(
        self,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        current_user: Optional[User] = None,
    ) -> PageResponse:
        total, items = self.user_repo.get_list(keyword=keyword, page=page, page_size=page_size)

        # 数据范围过滤
        scope = _resolve_data_scope(current_user)
        if scope == 1:
            filtered = items
        elif scope == 3:
            # 仅本部门
            dept_id = current_user.department_id if current_user else None
            filtered = [u for u in items if u.department_id == dept_id or u.id == (current_user.id if current_user else None)]
        elif scope == 4:
            # 本部门及以下（递归）
            dept_id = current_user.department_id if current_user else None
            if dept_id:
                allowed_depts = set(DepartmentRepository(self.db).get_descendant_ids(dept_id))
                filtered = [u for u in items if u.department_id in allowed_depts or u.id == (current_user.id if current_user else None)]
            else:
                filtered = [u for u in items if u.id == (current_user.id if current_user else None)]
        elif scope == 5:
            # 仅本人
            uid = current_user.id if current_user else None
            filtered = [u for u in items if u.id == uid]
        else:
            filtered = items

        return PageResponse(
            total=len(filtered),
            page=page,
            page_size=page_size,
            items=[UserResponse.model_validate(u) for u in filtered],
        )

    def create(self, data: UserCreate) -> User:
        if self.user_repo.exists_by_username(data.username):
            logger.warning("创建用户失败: 用户名 '%s' 已存在", data.username)
            raise ConflictException(f"用户名 '{data.username}' 已存在")

        user = User(
            username=data.username,
            password=hash_password(data.password),
            nickname=data.nickname or data.username,
            email=data.email,
            phone=data.phone,
            gender=data.gender,
            status=data.status,
            department_id=data.department_id,
        )
        user = self.user_repo.create(user)

        if data.role_ids:
            user_roles = self.role_repo.get_by_ids(data.role_ids)
            self.user_repo.update_roles(user, user_roles)

        self.db.commit()
        self.db.refresh(user)
        logger.info("用户已创建: id=%d 用户名='%s'", user.id, user.username)
        return user

    def update(self, user_id: int, data: Union[UserUpdate, UserProfileUpdate]) -> User:
        user = self.get_by_id(user_id)

        update_fields = ["nickname", "email", "phone", "department_id"]
        for field in update_fields:
            value = getattr(data, field, None)
            if value is not None:
                setattr(user, field, value)

        # 布尔和整数字段: 允许显式的 False / 0 值
        for field in ("status", "gender"):
            value = getattr(data, field, None)
            if value is not None:
                setattr(user, field, value)

        user = self.user_repo.update(user)

        role_ids = getattr(data, 'role_ids', None)
        if role_ids is not None:
            user_roles = self.role_repo.get_by_ids(role_ids)
            self.user_repo.update_roles(user, user_roles)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if user.is_superuser:
            logger.warning("删除用户被拒绝: id=%d 是超级管理员", user_id)
            raise BadRequestException("不能删除超级管理员用户")
        username = user.username
        self.user_repo.delete(user)
        self.db.commit()
        logger.info("用户已删除: id=%d 用户名='%s'", user_id, username)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        user = self.get_by_id(user_id)
        if not verify_password(old_password, user.password):
            logger.warning("修改密码失败: 用户 id=%d 旧密码不正确", user_id)
            raise BadRequestException("旧密码不正确")
        user.password = hash_password(new_password)
        self.user_repo.update(user)
        self.db.commit()
        logger.info("密码已修改: 用户 id=%d", user_id)

    def reset_password(self, user_id: int, new_password: str) -> None:
        user = self.get_by_id(user_id)
        user.password = hash_password(new_password)
        self.user_repo.update(user)
        self.db.commit()
        logger.info("管理员重置密码: 用户 id=%d", user_id)

    def update_login_info(self, user: User, ip_address: Optional[str] = None) -> None:
        from datetime import datetime, timezone
        user.last_login_at = datetime.now(timezone.utc)
        user.last_login_ip = ip_address
        self.user_repo.update(user)
        self.db.commit()
        logger.info("用户登录: id=%d 用户名='%s' IP=%s", user.id, user.username, ip_address or "未知")

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户名密码，支持失败锁定（带行锁防止并发竞争）。"""
        # 使用行锁查询，防止并发下失败计数竞争
        user = self.user_repo.get_by_username(username, lock=True)
        if not user:
            logger.warning("登录失败: 用户名 '%s' 不存在", username)
            return None
        if not user.status:
            logger.warning("登录失败: 用户名 '%s' 已禁用", username)
            return None

        # 检查是否被锁定
        if user.login_locked_until and user.login_locked_until > datetime.now(timezone.utc):
            remaining = (user.login_locked_until - datetime.now(timezone.utc)).seconds // 60
            logger.warning("登录失败: 用户名 '%s' 已锁定，剩余 %d 分钟", username, remaining)
            return None

        if not verify_password(password, user.password):
            # 累加失败次数
            user.login_fail_count = (user.login_fail_count or 0) + 1
            if user.login_fail_count >= MAX_LOGIN_FAIL_COUNT:
                user.login_locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOGIN_LOCK_MINUTES)
                logger.warning("用户 '%s' 已被锁定 %d 分钟", username, LOGIN_LOCK_MINUTES)
            self.db.commit()
            logger.warning("登录失败: 用户名 '%s' 密码错误（第 %d 次）", username, user.login_fail_count)
            return None

        # 登录成功：重置失败计数
        user.login_fail_count = 0
        user.login_locked_until = None
        self.db.commit()
        return user
