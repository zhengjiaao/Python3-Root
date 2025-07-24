# example-vue-frontend/apps/main.py
from fastapi import FastAPI
from .files.views import files_api
from .users.views import users_api

app = FastAPI(
    title="Your API Title",
    description="Your API Description",
    version="0.1.0",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,  # 默认不展开 Schemas
        "docExpansion": "none"  # 默认不展开路由
    }
)

# 包含 users.py 中的路由
app.include_router(users_api, prefix="/api", tags=["users"])
app.include_router(files_api, prefix="/api", tags=["files"])
# apps.include_router(users_api)
# apps.include_router(files_api)


# Mount the vue-frontend static files
# apps.mount("/static", StaticFiles(directory="example-vue-frontend/vue-frontend/dist"), name="static")


# Serve the vue-frontend index.html for all other routes
# @apps.get("/{full_path:path}", response_class=HTMLResponse)
# async def read_index(request: Request, full_path: str):
#     with open("example-vue-frontend/vue-frontend/dist/index.html") as f:
#         return HTMLResponse(content=f.read())
