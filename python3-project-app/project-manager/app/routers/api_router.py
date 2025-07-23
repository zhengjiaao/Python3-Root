from fastapi import APIRouter
from ..routers import projects

api_router = APIRouter()

api_router.include_router(projects.router)