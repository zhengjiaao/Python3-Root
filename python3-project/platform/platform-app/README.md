# Platform App - 平台应用端

Platform App 是面向终端用户的平台应用端，基于 FastAPI + Jinja2 构建，复用 **platform-admin-app** 的用户体系、数据库、认证机制与权限控制能力。

## 项目架构

```
platform-app/
├── platform_app/           # 业务代码包（与 admin 的 app 区分）
│   ├── main.py             # FastAPI 应用工厂
│   ├── config.py           # 独立配置（端口、应用名等）
│   ├── dependencies/
│   │   └── auth.py         # 认证依赖（复用 admin JWT + 数据库）
│   └── routers/
│       ├── auth.py         # 认证 API（登录/刷新/退出）
│       ├── home.py         # 首页 API
│       ├── profile.py      # 个人中心 API
│       └── pages.py        # 页面路由（HTML 渲染）
├── templates/              # Jinja2 模板
│   ├── base.html
│   ├── home.html
│   ├── profile.html
│   └── auth/login.html
├── static/                 # 静态资源
│   ├── css/style.css
│   └── js/app.js
├── .env                    # 环境配置
├── requirements.txt
└── run.py                  # 启动入口
```

## 与 platform-admin-app 的关系

| 能力 | 方式 |
|------|------|
| 用户模型 | 复用 `platform-admin-app/app/database/models` 的 `User`、`Role` 等 |
| 数据库 | 独立数据库文件（`data/platform_app.db`），表结构复用管理端模型 |
| 认证机制 | 复用 JWT 双令牌、Cookie HttpOnly、token 黑名单 |
| 密码安全 | 复用 `passlib` bcrypt 哈希与校验 |
| 审计日志 | 复用 `AuditLog` 模型与 `log_audit` 服务 |
| 配置 | 独立 `.env`，但 JWT 密钥需与 admin 一致以互通 |

**依赖注入原理**：`platform_app/__init__.py` 将 `platform-admin-app` 目录加入 `sys.path`，使其 `app` 包可被直接导入；同时通过环境变量预设独立的数据库路径，确保应用端数据与管理员端物理隔离。

## 运行环境

- Python 3.10+
- 复用 `platform-admin-app` 的 `.venv` 虚拟环境即可（依赖完全一致）

## 启动方式

### 开发环境

```powershell
# 进入项目目录
cd python3-project/platform/platform-app

# 使用 platform-admin-app 的虚拟环境
..\platform-admin-app\.venv\Scripts\Activate.ps1

# 启动服务（默认 127.0.0.1:8001）
python run.py
```

### 同时启动 admin + app

```powershell
# Terminal 1: 启动管理端
cd python3-project/platform/platform-admin-app
python run.py          # http://127.0.0.1:8000

# Terminal 2: 启动应用端
cd python3-project/platform/platform-app
python run.py          # http://127.0.0.1:8001
```

## 默认账号

复用 platform-admin-app 的初始数据，默认管理员账号：
- 用户名：`admin`
- 密码：`Admin@1234`

> 在应用端登录后，与在管理端登录使用同一套用户体系，token 互通。

## 主要页面

| 路径 | 说明 |
|------|------|
| `/` | 首页（展示平台介绍，登录后显示欢迎信息） |
| `/login` | 用户登录页 |
| `/profile` | 个人中心（资料修改 + 修改密码） |
| `/admin` | 跳转到平台管理后台 |
| `/docs` | Swagger API 文档 |

## 注意事项

1. **端口冲突**：应用端默认使用 `8001`，与管理端 `8000` 区分。
2. **数据库隔离**：应用端使用独立的数据库文件 `data/platform_app.db`，启动时会自动创建表结构，但不会自动同步管理端的用户数据。
3. **JWT 密钥**：两个应用的 `JWT_SECRET_KEY` 必须一致，否则 token 无法互通验证。
4. **用户数据**：应用端独立数据库中初始无用户，如需测试登录，可调用管理端的用户创建 API 将用户同步到应用端，或在应用端自行实现注册功能。
