import time
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pathlib import Path
from contextlib import asynccontextmanager
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import get_settings
from app.utils.logger import setup_logging, get_logger

_settings = get_settings()
setup_logging(
    level=_settings.LOG_LEVEL,
    log_dir=_settings.LOG_DIR or None,
    log_file=_settings.LOG_FILE,
    app_name="admin",
)

from app.database.session import init_db, SessionLocal
from app.utils.init_data import init_test_data
from app.utils.exceptions import AppException
from app.utils.exception_handlers import register_exception_handlers
from app.routers import auth, users, roles, menus, departments, pages, permissions, audit_logs, dashboard, internal

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
import os


logger = get_logger(__name__)


class SecurityHeadersMiddleware:
    """ASGI 安全响应头中间件。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                security_headers = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"x-xss-protection", b"1; mode=block"),
                ]
                # 生产环境添加 HSTS
                settings = get_settings()
                if not settings.DEBUG:
                    security_headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))
                # 避免重复添加
                existing_keys = {h[0].lower() for h in headers}
                for key, val in security_headers:
                    if key.lower() not in existing_keys:
                        headers.append([key, val])
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)


class RequestLoggingMiddleware:
    """纯 ASGI 中间件: 请求日志记录。

    与使用 BaseHTTPMiddleware 的 ``@app.middleware("http")`` 不同，
    此实现直接拦截 ASGI scope/send/receive，确保路由处理器中
    抛出的异常能被正确捕获和记录，不会被 anyio 包装为 ExceptionGroup。
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code: int | None = None

        async def send_wrapper(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status")
            await send(message)

        path = scope.get("path", "")
        method = scope.get("method", "")

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "请求异常: %s %s (%.1fms) -> %s",
                method, path, duration_ms, exc,
            )
            raise

        if not path.startswith("/static"):
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "%s %s -> %s (%.1fms)",
                method, path, status_code, duration_ms,
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期: 启动和关闭逻辑。"""
    # 日志已在模块导入阶段初始化，此处跳过重复初始化
    settings = get_settings()

    init_db()
    db = SessionLocal()
    try:
        if settings.ENVIRONMENT == "development":
            init_test_data(db)
        else:
            logger.info("生产环境跳过测试数据初始化")
    finally:
        db.close()

    logger.info("%s v%s 已启动", settings.APP_NAME, settings.APP_VERSION)
    logger.info("运行环境: %s", settings.ENVIRONMENT)
    logger.info("数据库: %s", settings.DB_TYPE)
    logger.info("访问地址: http://127.0.0.1:8000")

    yield

    logger.info("应用正在关闭")


def create_app() -> FastAPI:
    """应用工厂。"""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        swagger_ui_parameters={"docExpansion": "none", "defaultModelsExpandDepth": -1},
    )

    # ============================================================
    # 速率限制器（SlowAPI）
    # ============================================================
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    limiter = Limiter(key_func=get_remote_address, config_filename=os.path.join(_base_dir, "slowapi.env"))
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ============================================================
    # 静态文件与模板
    # ============================================================
    base_dir = Path(__file__).resolve().parent.parent
    app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")
    templates = Jinja2Templates(directory=str(base_dir / "templates"))
    app.state.templates = templates

    # ============================================================
    # CORS 中间件
    # ============================================================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # ============================================================
    # 中间件（顺序: 最外层优先）
    # ============================================================
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    # ============================================================
    # 异常处理器
    # ============================================================
    register_exception_handlers(app)

    # ============================================================
    # 注册路由
    # ============================================================
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(roles.router)
    app.include_router(menus.router)
    app.include_router(departments.router)
    app.include_router(pages.router)
    app.include_router(permissions.router)
    app.include_router(audit_logs.router)

    app.include_router(dashboard.router)

    # 内部服务 API（供应用端调用）
    app.include_router(internal.router)

    return app


app = create_app()
