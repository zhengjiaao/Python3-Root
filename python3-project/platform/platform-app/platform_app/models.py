"""应用端数据模型：不依赖 SQLAlchemy，从管理端 API 获取的数据使用 Pydantic 模型表示。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from platform_app.schemas.user import RoleBrief, DepartmentBrief


class UserInfo(BaseModel):
    """应用端用户信息模型（从管理端内部 API 获取，不依赖数据库 ORM）。

    替代原先直接使用 SQLAlchemy User 模型的方式，
    应用端所有路由和依赖注入统一使用此模型。
    """
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    gender: int = 0
    status: bool = True
    department_id: Optional[int] = None
    is_superuser: bool = False
    is_admin: bool = False
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    roles: list[RoleBrief] = []
    permissions: list[str] = []
    department: Optional[DepartmentBrief] = None

    model_config = {"from_attributes": True}

    def has_permission(self, required_perm: str) -> bool:
        """检查用户是否拥有指定权限（支持通配符）。"""
        if self.is_superuser:
            return True
        user_perms = set(self.permissions)
        return _has_permission(required_perm, user_perms)

    def has_role(self, role_key: str) -> bool:
        """检查用户是否拥有指定角色。"""
        if self.is_superuser:
            return True
        return role_key in {r.role_key for r in self.roles}


def _has_permission(required_perm: str, user_perms: set[str]) -> bool:
    """检查用户的权限集合是否满足所需权限。

    支持通配符匹配:
    - '*' 匹配所有
    - 'module:*' 匹配所有 'module:xxx' 权限
    - 'module:sub:*' 匹配所有 'module:sub:xxx' 权限
    """
    if required_perm in user_perms:
        return True
    parts = required_perm.split(":")
    for i in range(len(parts), 0, -1):
        wildcard = ":".join(parts[:i]) + ":*"
        if wildcard in user_perms:
            return True
    if "*" in user_perms:
        return True
    return False
