from sqlalchemy.orm import Session

from app.database.models import User, Role, Permission, Menu, Department
from app.utils.security import hash_password
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def init_test_data(db: Session) -> None:
    """Initialize test data if database is empty."""
    # Only initialize if no users exist
    if db.query(User).first():
        return

    settings = get_settings()

    # ============================================================
    # 1. Departments
    # ============================================================
    dept_root = Department(name="总部", sort_order=1, status=True, leader="总经理", email="hq@platform.com")
    db.add(dept_root)
    db.flush()

    dept_tech = Department(name="技术部", parent_id=dept_root.id, sort_order=1, status=True, leader="技术总监", email="tech@platform.com")
    dept_product = Department(name="产品部", parent_id=dept_root.id, sort_order=2, status=True, leader="产品总监", email="product@platform.com")
    dept_hr = Department(name="人力资源部", parent_id=dept_root.id, sort_order=3, status=True, leader="人事总监", email="hr@platform.com")
    db.add_all([dept_tech, dept_product, dept_hr])
    db.flush()

    dept_dev = Department(name="研发部", parent_id=dept_tech.id, sort_order=1, status=True)
    dept_qa = Department(name="测试部", parent_id=dept_tech.id, sort_order=2, status=True)
    db.add_all([dept_dev, dept_qa])
    db.flush()

    # ============================================================
    # 2. Menus
    # ============================================================
    menu_system = Menu(name="系统管理", menu_type="directory", icon="gear", sort_order=99, visible=True, status=True)
    db.add(menu_system)
    db.flush()

    menu_user = Menu(name="用户管理", parent_id=menu_system.id, menu_type="menu", icon="people", path="/users", sort_order=1, visible=True, status=True, permission_key="system:user")
    menu_role = Menu(name="角色管理", parent_id=menu_system.id, menu_type="menu", icon="shield-lock", path="/roles", sort_order=2, visible=True, status=True, permission_key="system:role")
    menu_menu = Menu(name="菜单管理", parent_id=menu_system.id, menu_type="menu", icon="menu-button-wide", path="/menus", sort_order=3, visible=True, status=True, permission_key="system:menu")
    menu_dept = Menu(name="部门管理", parent_id=menu_system.id, menu_type="menu", icon="building", path="/departments", sort_order=4, visible=True, status=True, permission_key="system:dept")
    menu_perm = Menu(name="权限管理", parent_id=menu_system.id, menu_type="menu", icon="key", path="/permissions", sort_order=5, visible=True, status=True, permission_key="system:perm")
    menu_audit = Menu(name="审计日志", parent_id=menu_system.id, menu_type="menu", icon="journal-text", path="/audit-logs", sort_order=6, visible=True, status=True, permission_key="system:audit")
    db.add_all([menu_user, menu_role, menu_menu, menu_dept, menu_perm, menu_audit])
    db.flush()

    # ============================================================
    # 3. Permissions
    # ============================================================
    # User permissions
    perms_data = [
        # 用户
        ("用户列表", "system:user:list", "menu", menu_user.id, "/api/users", "GET", 1),
        ("用户查询", "system:user:query", "button", menu_user.id, "/api/users/{id}", "GET", 2),
        ("新增用户", "system:user:add", "button", menu_user.id, "/api/users", "POST", 3),
        ("编辑用户", "system:user:edit", "button", menu_user.id, "/api/users/{id}", "PUT", 4),
        ("删除用户", "system:user:remove", "button", menu_user.id, "/api/users/{id}", "DELETE", 5),
        ("重置密码", "system:user:resetPwd", "button", menu_user.id, "/api/users/{id}/reset-password", "PUT", 6),
        # 角色
        ("角色列表", "system:role:list", "menu", menu_role.id, "/api/roles", "GET", 1),
        ("角色查询", "system:role:query", "button", menu_role.id, "/api/roles/{id}", "GET", 2),
        ("新增角色", "system:role:add", "button", menu_role.id, "/api/roles", "POST", 3),
        ("编辑角色", "system:role:edit", "button", menu_role.id, "/api/roles/{id}", "PUT", 4),
        ("删除角色", "system:role:remove", "button", menu_role.id, "/api/roles/{id}", "DELETE", 5),
        # 菜单
        ("菜单列表", "system:menu:list", "menu", menu_menu.id, "/api/menus", "GET", 1),
        ("菜单查询", "system:menu:query", "button", menu_menu.id, "/api/menus/{id}", "GET", 2),
        ("新增菜单", "system:menu:add", "button", menu_menu.id, "/api/menus", "POST", 3),
        ("编辑菜单", "system:menu:edit", "button", menu_menu.id, "/api/menus/{id}", "PUT", 4),
        ("删除菜单", "system:menu:remove", "button", menu_menu.id, "/api/menus/{id}", "DELETE", 5),
        # 部门
        ("部门列表", "system:dept:list", "menu", menu_dept.id, "/api/departments", "GET", 1),
        ("部门查询", "system:dept:query", "button", menu_dept.id, "/api/departments/{id}", "GET", 2),
        ("新增部门", "system:dept:add", "button", menu_dept.id, "/api/departments", "POST", 3),
        ("编辑部门", "system:dept:edit", "button", menu_dept.id, "/api/departments/{id}", "PUT", 4),
        ("删除部门", "system:dept:remove", "button", menu_dept.id, "/api/departments/{id}", "DELETE", 5),
        # 权限
        ("权限列表", "system:perm:list", "menu", menu_perm.id, "/api/permissions", "GET", 1),
        ("权限查询", "system:perm:query", "button", menu_perm.id, "/api/permissions/{id}", "GET", 2),
        ("新增权限", "system:perm:add", "button", menu_perm.id, "/api/permissions", "POST", 3),
        ("编辑权限", "system:perm:edit", "button", menu_perm.id, "/api/permissions/{id}", "PUT", 4),
        ("删除权限", "system:perm:remove", "button", menu_perm.id, "/api/permissions/{id}", "DELETE", 5),
        # 审计日志
        ("审计日志列表", "system:audit:list", "menu", menu_audit.id, "/api/audit-logs", "GET", 1),
    ]

    permissions = []
    for name, key, ptype, parent_id, path, method, sort in perms_data:
        perm = Permission(name=name, permission_key=key, type=ptype, parent_id=parent_id, path=path, method=method, sort_order=sort, status=True)
        permissions.append(perm)
    db.add_all(permissions)
    db.flush()

    # ============================================================
    # 4. Roles
    # ============================================================
    role_super_admin = Role(name="超级管理员", role_key="super_admin", sort_order=1, status=True, data_scope=1, remark="拥有所有权限的超级管理员")
    role_admin = Role(name="管理员", role_key="admin", sort_order=2, status=True, data_scope=1, remark="系统管理员")
    role_user = Role(name="普通用户", role_key="user", sort_order=3, status=True, data_scope=5, remark="普通用户，权限有限")
    db.add_all([role_super_admin, role_admin, role_user])
    db.flush()

    # Assign all permissions to super_admin
    role_super_admin.permissions = permissions

    # Assign view/list permissions to admin
    admin_perms = [p for p in permissions if p.permission_key.endswith((":list", ":query", ":add", ":edit"))]
    role_admin.permissions = admin_perms

    # Assign basic view permissions to user
    user_perms = [p for p in permissions if p.permission_key.endswith((":list", ":query"))]
    role_user.permissions = user_perms

    # Assign menus to roles
    all_menus = [menu_system, menu_user, menu_role, menu_menu, menu_dept, menu_perm, menu_audit]
    role_super_admin.menus = all_menus
    role_admin.menus = all_menus
    role_user.menus = [menu_system, menu_user]

    # ============================================================
    # 5. Users
    # ============================================================
    admin = User(
        username=settings.ADMIN_USERNAME,
        password=hash_password(settings.ADMIN_PASSWORD),
        nickname="超级管理员",
        email="admin@platform.com",
        gender=1,
        status=True,
        department_id=dept_root.id,
        is_superuser=True,
    )
    db.add(admin)
    db.flush()
    admin.roles = [role_super_admin]

    # Admin user
    user_admin = User(
        username="manager",
        password=hash_password("Manager@1234"),
        nickname="系统管理员",
        email="manager@platform.com",
        gender=1,
        status=True,
        department_id=dept_tech.id,
        is_superuser=False,
    )
    db.add(user_admin)
    db.flush()
    user_admin.roles = [role_admin]

    # Regular user
    user_normal = User(
        username="zhangsan",
        password=hash_password("Zhangsan@1234"),
        nickname="张三",
        email="zhangsan@platform.com",
        phone="13800000001",
        gender=1,
        status=True,
        department_id=dept_dev.id,
        is_superuser=False,
    )
    db.add(user_normal)
    db.flush()
    user_normal.roles = [role_user]

    # Another regular user
    user_lisi = User(
        username="lisi",
        password=hash_password("Lisi@1234"),
        nickname="李四",
        email="lisi@platform.com",
        phone="13800000002",
        gender=2,
        status=True,
        department_id=dept_qa.id,
        is_superuser=False,
    )
    db.add(user_lisi)
    db.flush()
    user_lisi.roles = [role_user]

    # Disabled user
    user_disabled = User(
        username="wangwu",
        password=hash_password("Wangwu@1234"),
        nickname="王五",
        email="wangwu@platform.com",
        gender=1,
        status=False,
        department_id=dept_hr.id,
        is_superuser=False,
    )
    db.add(user_disabled)
    db.flush()

    db.commit()
    logger.info("测试数据初始化成功")
    logger.info("超级管理员账号密码: 请查看 .env 配置文件")
