import os
import sys
from fastapi import FastAPI
from app.routers.api_router import api_router
from app.database.session import engine
from app.database.models import project as project_model
from app.utils.exceptions import http_exception_handler, validation_exception_handler
from app.utils.exceptions import NotFoundException, ValidationException

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

# swagger-ui：http://127.0.0.1:8000/docs
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='main:app', host="0.0.0.0", port=8000, reload=False, workers=1)