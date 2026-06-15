from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table,
    Unicode, UnicodeText, Index,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


# ============================================================
# Audit Log
# ============================================================

class AuditLog(Base):
    __tablename__ = "sys_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True, comment="操作用户ID")
    username = Column(Unicode(50), nullable=True, comment="操作用户名")
    action = Column(Unicode(50), nullable=False, comment="操作类型: LOGIN/LOGOUT/CREATE/UPDATE/DELETE/RESET_PASSWORD/CHANGE_PASSWORD")
    module = Column(Unicode(50), nullable=True, comment="操作模块")
    description = Column(UnicodeText, nullable=True, comment="操作描述")
    ip_address = Column(Unicode(50), nullable=True, comment="IP地址")
    user_agent = Column(Unicode(255), nullable=True, comment="User-Agent")
    status = Column(Boolean, default=True, comment="操作状态: true=成功, false=失败")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user='{self.username}')>"


# ============================================================
# Association tables (many-to-many relationships)
# ============================================================

user_roles = Table(
    "sys_user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("sys_role.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "sys_role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("sys_permission.id", ondelete="CASCADE"), primary_key=True),
)

role_menus = Table(
    "sys_role_menus",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.id", ondelete="CASCADE"), primary_key=True),
    Column("menu_id", Integer, ForeignKey("sys_menu.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================
# Department
# ============================================================

class Department(Base):
    __tablename__ = "sys_department"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(100), nullable=False, comment="部门名称")
    parent_id = Column(Integer, ForeignKey("sys_department.id"), nullable=True, default=None, comment="上级部门ID")
    sort_order = Column(Integer, default=0, comment="排序号")
    status = Column(Boolean, default=True, comment="启用状态")
    leader = Column(Unicode(50), nullable=True, comment="部门负责人")
    phone = Column(Unicode(20), nullable=True, comment="联系电话")
    email = Column(Unicode(100), nullable=True, comment="联系邮箱")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship("User", back_populates="department")
    children = relationship("Department", backref="parent", remote_side=[id], foreign_keys=[parent_id])

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"


# ============================================================
# User
# ============================================================

class User(Base):
    __tablename__ = "sys_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Unicode(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(Unicode(255), nullable=False, comment="密码哈希")
    nickname = Column(Unicode(50), nullable=True, comment="昵称")
    email = Column(Unicode(100), nullable=True, comment="邮箱")
    phone = Column(Unicode(20), nullable=True, comment="手机号")
    avatar = Column(Unicode(255), nullable=True, comment="头像地址")
    gender = Column(Integer, default=0, comment="0=未知, 1=男, 2=女")
    status = Column(Boolean, default=True, comment="账号启用状态")
    department_id = Column(Integer, ForeignKey("sys_department.id"), nullable=True, comment="所属部门")
    is_superuser = Column(Boolean, default=False, comment="超级管理员标识")
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(Unicode(50), nullable=True)
    login_fail_count = Column(Integer, default=0, comment="连续登录失败次数")
    login_locked_until = Column(DateTime, nullable=True, comment="锁定截止时间")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    department = relationship("Department", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

    @property
    def role_keys(self) -> list[str]:
        return [r.role_key for r in self.roles]

    @property
    def is_admin(self) -> bool:
        return self.is_superuser or "admin" in self.role_keys


# ============================================================
# Role
# ============================================================

class Role(Base):
    __tablename__ = "sys_role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(50), unique=True, nullable=False, comment="角色名称")
    role_key = Column(Unicode(50), unique=True, nullable=False, comment="角色标识键")
    sort_order = Column(Integer, default=0, comment="排序号")
    status = Column(Boolean, default=True, comment="启用状态")
    remark = Column(UnicodeText, nullable=True, comment="备注")
    data_scope = Column(Integer, default=1, comment="1=全部数据, 2=自定义, 3=本部门, 4=本部门及以下, 5=仅本人")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles", lazy="selectin")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles", lazy="selectin")
    menus = relationship("Menu", secondary=role_menus, back_populates="roles", lazy="selectin")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', key='{self.role_key}')>"


# ============================================================
# Permission
# ============================================================

class Permission(Base):
    __tablename__ = "sys_permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(100), nullable=False, comment="权限名称")
    permission_key = Column(Unicode(100), unique=True, nullable=False, comment="权限标识")
    type = Column(Unicode(20), nullable=False, default="menu", comment="类型: menu/button/api")
    parent_id = Column(Integer, ForeignKey("sys_permission.id"), nullable=True, default=None, comment="上级权限")
    path = Column(Unicode(255), nullable=True, comment="API路径或路由")
    method = Column(Unicode(10), nullable=True, comment="API权限的HTTP方法")
    sort_order = Column(Integer, default=0, comment="排序号")
    status = Column(Boolean, default=True, comment="启用状态")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    __table_args__ = (
        Index("ix_sys_permission_key", "permission_key", unique=True),
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, key='{self.permission_key}')>"


# ============================================================
# Menu
# ============================================================

class Menu(Base):
    __tablename__ = "sys_menu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(100), nullable=False, comment="菜单名称")
    parent_id = Column(Integer, ForeignKey("sys_menu.id"), nullable=True, default=None, comment="上级菜单ID")
    path = Column(Unicode(255), nullable=True, comment="路由路径")
    component = Column(Unicode(255), nullable=True, comment="组件路径")
    icon = Column(Unicode(100), nullable=True, comment="菜单图标")
    menu_type = Column(Unicode(20), default="directory", comment="类型: directory/menu/button")
    permission_key = Column(Unicode(100), nullable=True, comment="权限标识")
    sort_order = Column(Integer, default=0, comment="排序号")
    visible = Column(Boolean, default=True, comment="显示/隐藏")
    status = Column(Boolean, default=True, comment="启用状态")
    is_external = Column(Boolean, default=False, comment="是否外链")
    is_cache = Column(Boolean, default=False, comment="是否缓存")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    roles = relationship("Role", secondary=role_menus, back_populates="menus")
    children = relationship("Menu", backref="parent", remote_side=[id], foreign_keys=[parent_id])

    def __repr__(self):
        return f"<Menu(id={self.id}, name='{self.name}')>"
