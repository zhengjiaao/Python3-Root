from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from .routers import files
from .config import settings

app = FastAPI(
    title="MinIO File Service API",
    description="API for file operations using MinIO storage",
    version="1.0.0",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,  # 默认不展开 Schemas
        "docExpansion": "none"  # 默认不展开路由
    }
)

# 包含路由
app.include_router(files.router, prefix="/files", tags=["files"])

# 挂载静态文件目录
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/")
def read_root():
    return {"message": "MinIO File Service is running"}

# 测试上传页面，直接读模版文件方式
@app.get("/test-upload")
async def test_upload_page():
    return FileResponse("templates/index.html")