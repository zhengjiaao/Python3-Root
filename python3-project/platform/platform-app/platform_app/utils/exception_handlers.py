"""平台应用端异常处理器注册。

为 FastAPI 应用提供统一的异常处理逻辑。
"""

import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from platform_app.utils.exceptions import AppException
from platform_app.utils.logger import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """为 FastAPI 应用注册统一的全局异常处理器。"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(
            "应用异常: %s %s -> %d %s",
            request.method, request.url.path, exc.status_code, exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail, "data": None},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_id = str(uuid.uuid4())
        logger.exception(
            "未处理异常 [%s]: %s %s -> %s",
            error_id, request.method, request.url.path, exc,
        )
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部错误", "error_id": error_id, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            loc = ".".join(str(l) for l in err.get("loc", []))
            msg = err.get("msg", "")
            errors.append(f"{loc}: {msg}" if loc else msg)
        message = "; ".join(errors) if errors else "请求参数校验失败"
        logger.warning("参数校验失败: %s %s -> %s", request.method, request.url.path, message)
        return JSONResponse(
            status_code=422,
            content={"code": 422, "message": message, "data": None},
        )
