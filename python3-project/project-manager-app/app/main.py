import os
import sys
from fastapi import FastAPI
from .routers.api_router import api_router
from .database.session import engine
from .database.models import project as project_model
from .utils.exceptions import http_exception_handler, validation_exception_handler
from .utils.exceptions import NotFoundException, ValidationException

# 创建数据库表
project_model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Project Management API",
    description="API for managing projects",
    version="1.0.0",
    openapi_url="/openapi.json" if os.getenv("APP_ENV") != "production" else None,
    docs_url="/docs" if os.getenv("APP_ENV") != "production" else None,
    redoc_url=None
)

# 注册自定义异常处理器
app.add_exception_handler(NotFoundException, http_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}