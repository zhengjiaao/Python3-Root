# Platform Admin — 后台管理平台

基于 **FastAPI + SQLAlchemy + Jinja2 + Bootstrap 5** 构建的 RBAC 后台管理系统，支持多数据库（SQLite / MySQL / PostgreSQL）。

---

## 项目结构

```
platform-admin-app/
├── app/                          # 应用核心代码
│   ├── main.py                   # FastAPI 应用工厂 & lifespan
│   ├── config.py                 # pydantic-settings 配置管理
│   ├── database/                 # 数据库层
│   │   ├── base.py               # SQLAlchemy DeclarativeBase
│   │   ├── session.py            # Engine / SessionLocal / init_db / get_db
│   │   └── models/
│   │       └── __init__.py       # ORM 模型：User, Role, Permission, Menu, Department
│   ├── dependencies/             # FastAPI 依赖注入
│   │   └── auth.py               # get_current_user / require_permissions / require_roles
│   ├── middleware/                # 中间件（预留扩展）
│   ├── repositories/             # 数据访问层（Repository Pattern）
│   │   └── repository.py         # UserRepository / RoleRepository / PermissionRepository / MenuRepository / DepartmentRepository
│   ├── routers/                  # API 路由层
│   │   ├── auth.py               # 认证：登录 / 登出 / 用户信息 / 个人资料更新
│   │   ├── dashboard.py          # Dashboard 统计数据
│   │   ├── users.py              # 用户 CRUD + 重置密码 + 修改密码
│   │   ├── roles.py              # 角色 CRUD + 角色权限/菜单分配
│   │   ├── menus.py              # 菜单 CRUD + 树形结构
│   │   ├── departments.py        # 部门 CRUD + 树形结构
│   │   ├── permissions.py        # 权限 CRUD
│   │   └── pages.py              # 页面路由（SSR：登录页 / Dashboard / 管理页）
│   ├── schemas/                  # Pydantic 请求/响应模型
│   │   ├── response.py           # ApiResponse / PageResponse
│   │   ├── user.py               # UserCreate / UserUpdate / UserResponse / UserProfileUpdate / LoginRequest / TokenResponse / CurrentUser
│   │   ├── role.py               # RoleCreate / RoleUpdate / RoleResponse
│   │   ├── menu.py               # MenuCreate / MenuUpdate / MenuResponse / MenuTreeNode
│   │   ├── department.py         # DepartmentCreate / DepartmentUpdate / DepartmentResponse / DepartmentTreeNode
│   │   └── permission.py         # PermissionCreate / PermissionUpdate / PermissionResponse
│   ├── services/                 # 业务逻辑层
│   │   ├── user_service.py       # 用户：认证 / CRUD / 密码管理
│   │   ├── role_service.py       # 角色：CRUD / 权限分配 / 菜单分配
│   │   ├── menu_service.py       # 菜单：CRUD / 树形构建 / 用户菜单树
│   │   ├── department_service.py # 部门：CRUD / 树形构建 / 循环引用检测
│   │   └── permission_service.py # 权限：CRUD / 关联角色检测
│   └── utils/                    # 工具模块
│       ├── security.py           # JWT 创建/解码 + bcrypt 密码哈希/验证
│       ├── logger.py            # 集中日志配置（控制台 + RotatingFileHandler）
│       ├── exceptions.py         # 自定义异常：400 / 401 / 403 / 404 / 409
│       └── init_data.py          # 初始化测试数据（部门/菜单/权限/角色/用户）
├── data/                         # SQLite 数据库文件目录
│   └── platform_admin.db         # 默认 SQLite 数据库（自动创建）
├── static/                       # 静态资源
│   ├── css/
│   │   └── style.css             # 自定义样式（侧边栏 / 登录页 / 响应式）
│   └── js/
│       └── app.js                # 通用 JS：apiFetch / escapeHtml / renderPagination / formatDate / confirmAction
├── templates/                    # Jinja2 模板
│   ├── base.html                 # 基础模板（Bootstrap 5 CDN）
│   ├── admin_layout.html         # 管理后台布局（侧边栏 + 顶栏）
│   ├── dashboard.html            # Dashboard 页面（统计卡片）
│   ├── auth/
│   │   └── login.html            # 登录页
│   ├── users/
│   │   └── list.html             # 用户管理页
│   ├── roles/
│   │   └── list.html             # 角色管理页
│   ├── menus/
│   │   └── list.html             # 菜单管理页
│   └── departments/
│       └── list.html             # 部门管理页
├── .env                          # 环境变量配置文件
├── requirements.txt              # Python 依赖
└── run.py                        # 应用启动入口（uvicorn reload 模式）
```

---

## 快速开始

### 1. 安装依赖

```bash
cd platform-admin-app
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件（详见下方 [配置管理](#配置管理) 章节），默认配置可直接运行。

### 3. 启动应用

```bash
python run.py
```

启动后输出：

```
Platform Admin v1.0.0 已启动
数据库: sqlite
访问地址: http://127.0.0.1:8000
```

- 访问 `http://127.0.0.1:8000` 进入登录页
- 默认管理员账号：`admin` / `admin123`（可在 `.env` 中修改）
- API 文档：`http://127.0.0.1:8000/docs` （Swagger UI）

### 4. 关闭应用

开发模式（`run.py`）下直接 `Ctrl+C` 终止进程。

生产环境部署示例：

```bash
# 前台运行
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 后台运行
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
# 关闭：kill <PID> 或 pkill -f "uvicorn app.main:app"
```

---

## 配置管理

配置通过 `.env` 文件管理，使用 `pydantic-settings` 加载，支持环境变量覆盖。

### 应用配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `APP_NAME` | Platform Admin | 应用名称 |
| `APP_VERSION` | 1.0.0 | 版本号 |
| `DEBUG` | true | 调试模式（生产环境设为 `false`） |

### 数据库配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DB_TYPE` | sqlite | 数据库类型：`sqlite` / `mysql` / `postgresql` |
| `SQLITE_DB_FILE` | data/platform_admin.db | SQLite 数据库文件路径 |
| `MYSQL_HOST` | localhost | MySQL 主机 |
| `MYSQL_PORT` | 3306 | MySQL 端口 |
| `MYSQL_USER` | root | MySQL 用户名 |
| `MYSQL_PASSWORD` | root | MySQL 密码 |
| `MYSQL_DATABASE` | platform_admin | MySQL 数据库名 |
| `POSTGRES_HOST` | localhost | PostgreSQL 主机 |
| `POSTGRES_PORT` | 5432 | PostgreSQL 端口 |
| `POSTGRES_USER` | postgres | PostgreSQL 用户名 |
| `POSTGRES_PASSWORD` | postgres | PostgreSQL 密码 |
| `POSTGRES_DATABASE` | platform_admin | PostgreSQL 数据库名 |

切换到 MySQL：

```env
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=platform_admin
```

切换到 PostgreSQL：

```env
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=platform_admin
```

### JWT / 认证配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SECRET_KEY` | platform-admin-secret-key | 应用密钥（**生产环境必须修改**） |
| `JWT_SECRET_KEY` | jwt-secret-key | JWT 签名密钥（**生产环境必须修改**） |
| `JWT_ALGORITHM` | HS256 | JWT 签名算法 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 | Token 过期时间（分钟，默认 24 小时） |

### 管理员默认账号

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `ADMIN_USERNAME` | admin | 初始化超级管理员用户名 |
| `ADMIN_PASSWORD` | admin123 | 初始化超级管理员密码（**生产环境必须修改**） |

> 密码策略要求：至少 6 个字符，必须包含字母和数字。

### 日志配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `LOG_LEVEL` | INFO | 日志级别：`DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` |
| `LOG_DIR` | logs | 日志文件目录（相对项目根目录，留空禁用文件日志） |
| `LOG_FILE` | app.log | 日志文件名 |

---

## 日志管理

项目已实现集中式日志系统（`app/utils/logger.py`），开箱即用。

### 日志特性

- **控制台输出**：所有日志输出到 `stdout`，格式 `时间 | 级别 | 模块 | 消息`
- **文件持久化**：可选，通过 `LOG_DIR` 配置启用
- **日志轮转**：`RotatingFileHandler`，单文件 10MB，保留 5 个备份
- **第三方静默**：自动将 `uvicorn.access`、`sqlalchemy.*` 日志级别设为 `WARNING`，减少噪音
- **请求日志**：纯 ASGI 中间件 `RequestLoggingMiddleware`，记录每个请求的方法、路径、状态码、耗时
- **异常捕获**：请求异常自动记录完整堆栈；全局异常处理器兜底未捕获错误

### 日志级别控制

通过 `.env` 中的 `LOG_LEVEL` 统一控制所有日志输出级别：

```env
# 开发环境
LOG_LEVEL=DEBUG

# 生产环境
LOG_LEVEL=WARNING
```

> 注意：`DEBUG=true` 不再控制 SQL echo 日志，SQL 日志现在由 `LOG_LEVEL` 统一管理。

### 日志文件

默认配置下，日志文件写入 `logs/app.log`：

```env
# 启用文件日志（默认）
LOG_DIR=logs
LOG_FILE=app.log

# 禁用文件日志
LOG_DIR=
```

### 在代码中使用

```python
from app.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("应用启动")
logger.warning("警告信息")
logger.error("错误信息")
```

---

## 项目功能

### RBAC 权限模型

采用经典的 **用户 → 角色 → 权限/菜单** RBAC 模型：

```
User ──(多对多)──> Role ──(多对多)──> Permission
                   │
                   └──(多对多)──> Menu

Department ──(一对多)──> User （树形自引用）
Menu       ──(树形自引用，directory/menu/button 三级类型）
Permission ──(树形自引用，menu/button/api 三级类型）
```

- **超级管理员**（`is_superuser=True`）：自动获得所有权限，跳过权限检查
- **Admin 角色**：`role_key=admin`，`User.is_admin` 属性判定
- **数据权限**（`data_scope`）：1=全部数据 / 2=自定义 / 3=本部门 / 4=部门及子部门 / 5=仅本人（预留字段）

### 权限标识格式

```
system:user:list    → 用户列表
system:user:query   → 用户查询
system:user:add     → 用户添加
system:user:edit    → 用户编辑
system:user:remove  → 用户删除
system:user:resetPwd → 重置密码
```

支持通配符匹配：
- `*` 匹配所有权限
- `system:*` 匹配所有 `system:xxx` 权限
- `system:user:*` 匹配所有 `system:user:xxx` 权限

### 功能模块

| 模块 | API 端点 | 页面路由 | 功能 |
|------|----------|----------|------|
| **认证** | `/api/auth/login` | `/login` | JWT 登录（Cookie + Header 双模式）+ 更新登录 IP/时间 |
| | `/api/auth/logout` | — | 登出（清除 Cookie） |
| | `/api/auth/me` | — | 获取当前用户信息（权限 + 菜单树） |
| | `/api/auth/profile` | — | 更新个人资料（昵称/邮箱/手机/性别） |
| **Dashboard** | `/api/dashboard/stats` | `/dashboard` | 统计数据（用户/角色/菜单/部门数量） |
| **用户管理** | `/api/users` CRUD | `/users` | 分页列表 / 创建 / 编辑 / 删除 |
| | `/api/users/{id}/reset-password` | — | 管理员重置用户密码 |
| | `/api/users/{id}/change-password` | — | 用户修改自己密码（需验证旧密码） |
| **角色管理** | `/api/roles` CRUD | `/roles` | 分页列表 / 创建 / 编辑 / 删除 |
| | `/api/roles/all` | — | 获取所有角色（下拉选择） |
| **菜单管理** | `/api/menus` CRUD | `/menus` | 扁平列表 / 创建 / 编辑 / 删除 |
| | `/api/menus/tree` | — | 菜单树结构（层级展示） |
| **部门管理** | `/api/departments` CRUD | `/departments` | 分页列表 / 创建 / 编辑 / 删除 |
| | `/api/departments/tree` | — | 部门树结构（层级展示） |
| | `/api/departments/all` | — | 获取所有部门（下拉选择） |
| **权限管理** | `/api/permissions` CRUD | — | 列表 / 创建 / 编辑 / 删除 / 有角色关联时禁止删除 |

### 初始测试数据

首次启动自动创建：

| 类型 | 数据 |
|------|------|
| 部门 | 总部 → 技术/产品/人力资源 → 开发/测试 |
| 菜单 | 系统管理（目录）→ 用户管理/角色管理/菜单管理/部门管理 |
| 权限 | 每个模块 5-6 个权限（list/query/add/edit/remove/resetPwd） |
| 角色 | 超级管理员（全部权限）/ 管理员（增删改查）/ 普通用户（查看） |
| 用户 | admin（超级管理员）/ manager（管理员）/ zhangsan、lisi（普通用户）/ wangwu（已禁用） |

### 安全特性

- JWT Token 通过 `HttpOnly` Cookie 传递，防止 XSS 窃取
- Cookie `Secure` 标志：`DEBUG=false` 时自动启用（要求 HTTPS）
- Cookie `SameSite=Lax`：防止 CSRF 攻击
- 密码 bcrypt 哈希存储
- 密码复杂度校验：必须包含字母 + 数字
- 修改密码需验证旧密码，管理员重置密码无需旧密码
- 权限依赖注入：`require_permissions("system:user:list")` 精确控制每个 API
- 全局异常处理器：未捕获异常自动返回 500 + 记录完整堆栈
- Swagger UI 默认折叠（`docExpansion=none`），减少首次加载内容
- 超级管理员禁止删除
- 角色有用户关联时禁止删除
- 部门有子部门或有用户时禁止删除
- 权限有角色关联时禁止删除
- 菜单/部门循环引用检测

### 前端特性

- Bootstrap 5 响应式布局
- 侧边栏菜单根据用户权限动态渲染
- 表格搜索 / 分页（支持无限页数）
- Modal 弹窗创建 / 编辑（部门下拉带层级缩进）
- XSS 防护：`escapeHtml()` / `escapeAttr()` 全局工具函数
- 通用 `apiFetch()` 封装（自动 401 重定向，可配置 `noRedirect`）
- 通用 `renderPagination()` 分页组件（前后翻页 + 页码省略）
- 通用 `formatDate()` 日期格式化、`confirmAction()` 确认弹窗