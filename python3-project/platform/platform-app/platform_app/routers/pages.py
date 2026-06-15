from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse

from platform_app.dependencies.auth import get_current_user_optional, get_current_user
from platform_app.config import get_app_settings

router = APIRouter(tags=["页面"])


@router.get("/")
async def home_page(request: Request):
    """首页。"""
    templates = request.app.state.templates
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "首页",
    })


@router.get("/login")
async def login_page(request: Request):
    """登录页面。"""
    templates = request.app.state.templates
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "title": "用户登录",
    })


@router.get("/profile")
async def profile_page(request: Request, user=Depends(get_current_user_optional)):
    """个人中心页面（需登录）。"""
    if not user:
        return RedirectResponse(url="/login")
    templates = request.app.state.templates
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "title": "个人中心",
        "user": user,
    })


@router.get("/admin")
async def admin_redirect():
    """跳转到平台管理端。"""
    settings = get_app_settings()
    return RedirectResponse(url=settings.ADMIN_APP_URL)
