from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User
from app.dependencies.auth import get_current_user, get_current_user_info
from app.schemas.user import CurrentUser
from app.utils.security import decode_access_token, decode_refresh_token
from app.utils.token_store import revoke_token
from app.config import get_settings

router = APIRouter(tags=["页面"])


def _has_any_permission(user: CurrentUser, *perm_prefixes: str) -> bool:
    """检查用户是否拥有给定前缀的任意权限。"""
    if user.is_superuser:
        return True
    for perm in user.permissions:
        for prefix in perm_prefixes:
            if perm == "*" or perm.startswith(prefix):
                return True
    return False


def _clear_all_auth_cookies(response: Response) -> None:
    """清除所有认证 Cookie。"""
    settings = get_settings()
    secure = not settings.DEBUG
    response.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax", secure=secure)
    response.delete_cookie(key="refresh_token", path="/api/auth/refresh", httponly=True, samesite="strict", secure=secure)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """根页面 - 重定向到登录页或仪表盘。"""
    token = request.cookies.get("access_token")
    if token:
        payload = decode_access_token(token)
        if payload:
            return RedirectResponse(url="/dashboard", status_code=302)
    # Access Token 无效/已过期，尝试 Refresh Token
    refresh_tok = request.cookies.get("refresh_token")
    if refresh_tok and decode_refresh_token(refresh_tok):
        # Refresh Token 仍有效，前端会自动刷新，先进入仪表盘
        return RedirectResponse(url="/dashboard", status_code=302)
    # 全部无效，清除 Cookie 并跳转到登录页
    response = RedirectResponse(url="/login", status_code=302)
    _clear_all_auth_cookies(response)
    return response


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """渲染登录页面。"""
    return request.app.state.templates.TemplateResponse("auth/login.html", {
        "request": request,
    })


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user_info: CurrentUser = Depends(get_current_user_info),
):
    """渲染仪表盘页面。"""
    return request.app.state.templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user_info,
        "active_menu": "dashboard",
    })


@router.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request,
    current_user_info: CurrentUser = Depends(get_current_user_info),
):
    """渲染用户管理页面。"""
    if not _has_any_permission(current_user_info, "system:user:"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return request.app.state.templates.TemplateResponse("users/list.html", {
        "request": request,
        "user": current_user_info,
        "active_menu": "system:user",
    })


@router.get("/roles", response_class=HTMLResponse)
async def roles_page(
    request: Request,
    current_user_info: CurrentUser = Depends(get_current_user_info),
):
    """渲染角色管理页面。"""
    if not _has_any_permission(current_user_info, "system:role:"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return request.app.state.templates.TemplateResponse("roles/list.html", {
        "request": request,
        "user": current_user_info,
        "active_menu": "system:role",
    })


@router.get("/menus", response_class=HTMLResponse)
async def menus_page(
    request: Request,
    current_user_info: CurrentUser = Depends(get_current_user_info),
):
    """渲染菜单管理页面。"""
    if not _has_any_permission(current_user_info, "system:menu:"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return request.app.state.templates.TemplateResponse("menus/list.html", {
        "request": request,
        "user": current_user_info,
        "active_menu": "system:menu",
    })


@router.get("/departments", response_class=HTMLResponse)
async def departments_page(
    request: Request,
    current_user_info: CurrentUser = Depends(get_current_user_info),
):
    """渲染部门管理页面。"""
    if not _has_any_permission(current_user_info, "system:dept:"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return request.app.state.templates.TemplateResponse("departments/list.html", {
        "request": request,
        "user": current_user_info,
        "active_menu": "system:dept",
    })


@router.get("/permissions", response_class=HTMLResponse)
async def permissions_page(
    request: Request,
    current_user_info: CurrentUser = Depends(get_current_user_info),
):
    """渲染权限管理页面。"""
    if not _has_any_permission(current_user_info, "system:perm:"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return request.app.state.templates.TemplateResponse("permissions/list.html", {
        "request": request,
        "user": current_user_info,
        "active_menu": "system:perm",
    })


@router.get("/audit-logs", response_class=HTMLResponse)
async def audit_logs_page(
    request: Request,
    current_user_info: CurrentUser = Depends(get_current_user_info),
):
    """渲染审计日志页面。"""
    if not _has_any_permission(current_user_info, "system:audit:"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return request.app.state.templates.TemplateResponse("audit_logs/list.html", {
        "request": request,
        "user": current_user_info,
        "active_menu": "system:audit",
    })


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user_info: CurrentUser = Depends(get_current_user_info),
):
    """渲染个人中心页面。"""
    return request.app.state.templates.TemplateResponse("profile.html", {
        "request": request,
        "user": current_user_info,
        "active_menu": "profile",
    })
