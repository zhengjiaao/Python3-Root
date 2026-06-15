"""平台应用端主入口。

应用端不拥有独立的用户数据库，用户体系/权限完全依赖管理端（客户端），
通过管理端内部 API 完成认证、权限校验等操作。
"""

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from platform_app.config import get_app_settings, get_settings
from platform_app.utils.logger import setup_logging, get_logger
from platform_app.utils.exceptions import AppException
from platform_app.utils.exception_handlers import register_exception_handlers
from platform_app.client.admin_client import admin_client

# 设置日志
_settings = get_settings()
setup_logging(
    level=_settings.LOG_LEVEL,
    log_dir=_settings.LOG_DIR or None,
    log_file="platform_app.log",
    app_name="app",
)

logger = get_logger(__name__)

from platform_app.routers import auth, pages, home, profile


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
                existing_keys = {h[0].lower() for h in headers}
                for key, val in security_headers:
                    if key.lower() not in existing_keys:
                        headers.append([key, val])
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)


class RequestLoggingMiddleware:
    """纯 ASGI 中间件: 请求日志记录。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = None

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
    app_settings = get_app_settings()

    # 检查管理端是否可用
    if admin_client.health_check():
        logger.info("管理端连接验证成功: %s", app_settings.ADMIN_APP_URL)
    else:
        logger.warning(
            "⚠ 管理端连接验证失败: %s — 用户认证/权限功能将不可用！",
            app_settings.ADMIN_APP_URL,
        )

    logger.info("%s v%s 已启动", app_settings.APP_NAME, app_settings.APP_VERSION)
    logger.info("运行环境: %s", app_settings.ENVIRONMENT)
    logger.info("访问地址: http://%s:%s", app_settings.APP_HOST, app_settings.APP_PORT)
    logger.info("用户体系依赖管理端: %s", app_settings.ADMIN_APP_URL)

    yield

    logger.info("应用正在关闭")


def create_app() -> FastAPI:
    """应用工厂。"""
    app_settings = get_app_settings()

    app = FastAPI(
        title=app_settings.APP_NAME,
        version=app_settings.APP_VERSION,
        debug=app_settings.DEBUG,
        lifespan=lifespan,
        swagger_ui_parameters={"docExpansion": "none", "defaultModelsExpandDepth": -1},
    )

    # ============================================================
    # 静态文件与模板
    # ============================================================
    base_dir = Path(__file__).resolve().parent.parent
    app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")
    templates = Jinja2Templates(directory=str(base_dir / "templates"))
    app.state.templates = templates

    # ============================================================
    # 中间件
    # ============================================================
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    # ============================================================
    # 异常处理器
    # ============================================================
    register_exception_handlers(app)

    from fastapi.middleware.cors import CORSMiddleware
    # ============================================================
    # CORS 中间件
    # ============================================================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.CORS_ORIGINS,
        allow_credentials=app_settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=app_settings.CORS_ALLOW_METHODS,
        allow_headers=app_settings.CORS_ALLOW_HEADERS,
    )


    # ============================================================
    # 注册路由
    # ============================================================
    app.include_router(auth.router)
    app.include_router(home.router)
    app.include_router(profile.router)
    app.include_router(pages.router)

    return app


app = create_app()
