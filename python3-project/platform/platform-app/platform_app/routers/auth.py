"""应用端认证路由：登录/登出/刷新令牌。

所有用户认证操作通过管理端内部 API 完成，
应用端不再直接访问数据库，仅负责 JWT 令牌的颁发和 Cookie 管理。
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Response, Request

from platform_app.schemas.user import LoginRequest, TokenResponse, UserResponse
from platform_app.schemas.response import ApiResponse
from platform_app.utils.security import (
    create_access_token, create_refresh_token,
    decode_access_token, decode_refresh_token,
)
from platform_app.utils.token_store import revoke_token
from platform_app.utils.exceptions import UnauthorizedException, BadRequestException
from platform_app.config import get_settings
from platform_app.utils.logger import get_logger

from platform_app.dependencies.auth import get_current_user
from platform_app.client.admin_client import admin_client, AdminClientError
from platform_app.models import UserInfo

logger = get_logger(__name__)
router = APIRouter(prefix="/api/auth", tags=["认证"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """设置认证 Cookie（统一属性）。"""
    settings = get_settings()
    secure = not settings.DEBUG
    response.set_cookie(
        key="access_token",
        value=access_token,
        path="/",
        httponly=True,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=secure,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        path="/api/auth/refresh",
        httponly=True,
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        samesite="strict",
        secure=secure,
    )


def _clear_auth_cookies(response: Response) -> None:
    """清除认证 Cookie。"""
    settings = get_settings()
    secure = not settings.DEBUG
    response.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax", secure=secure)
    response.delete_cookie(key="refresh_token", path="/api/auth/refresh", httponly=True, samesite="strict", secure=secure)


@router.post("/login", response_model=ApiResponse)
def login(request: Request, login_data: LoginRequest, response: Response):
    """用户认证：调用管理端验证凭证，本地颁发 JWT 双令牌。"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # 通过管理端 API 验证用户凭证
    try:
        login_result = admin_client.login(login_data.username, login_data.password)
    except AdminClientError as e:
        # 管理端返回认证失败
        admin_client.log_audit(
            action="LOGIN", module="平台应用端",
            description="登录失败: 用户名或密码错误",
            username=login_data.username, ip_address=client_ip,
            user_agent=user_agent, status=False,
        )
        if e.status_code == 423:
            raise BadRequestException(e.message)
        raise UnauthorizedException(e.message)

    user_data = login_result.get("user", {})
    user_id = user_data.get("id")

    # 本地颁发 JWT 双令牌
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user_id)})

    _set_auth_cookies(response, access_token, refresh_token)

    # 通过管理端更新登录信息
    admin_client.update_login_info(user_id, ip_address=client_ip)

    logger.info("平台应用端用户登录: 用户名='%s' IP=%s", user_data.get("username"), client_ip)
    admin_client.log_audit(
        action="LOGIN", module="平台应用端", description="登录成功",
        user_id=user_id, username=user_data.get("username"),
        ip_address=client_ip, user_agent=user_agent, status=True,
    )

    user_resp = UserResponse.model_validate(user_data)
    return ApiResponse.success(data=TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_resp,
    ))


@router.post("/refresh", response_model=ApiResponse)
def refresh_token(request: Request, response: Response):
    """使用 Refresh Token 换取新的 Access Token（本地解码，无需调用管理端）。"""
    refresh_tok = request.cookies.get("refresh_token")
    if not refresh_tok:
        raise UnauthorizedException("缺少刷新令牌")
    payload = decode_refresh_token(refresh_tok)
    if not payload:
        raise UnauthorizedException("刷新令牌无效或已过期")
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("令牌载荷无效")
    new_access_token = create_access_token(data={"sub": str(user_id)})
    settings = get_settings()
    secure = not settings.DEBUG
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        path="/",
        httponly=True,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=secure,
    )
    return ApiResponse.success(data={"access_token": new_access_token})


@router.post("/logout", response_model=ApiResponse)
def logout(request: Request, response: Response):
    """退出登录：将当前 Access/Refresh 令牌加入黑名单并清除 Cookie。"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    user_id = None
    access_tok = request.cookies.get("access_token")
    if access_tok:
        payload = decode_access_token(access_tok)
        if payload:
            user_id = payload.get("sub")
            from datetime import timezone
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            revoke_token(payload["jti"], exp)
    refresh_tok = request.cookies.get("refresh_token")
    if refresh_tok:
        payload = decode_refresh_token(refresh_tok)
        if payload:
            from datetime import timezone
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            revoke_token(payload["jti"], exp)
    _clear_auth_cookies(response)

    # 清除用户缓存
    if user_id:
        admin_client.invalidate_user_cache(int(user_id))

    admin_client.log_audit(
        action="LOGOUT", module="平台应用端", description="退出登录",
        user_id=int(user_id) if user_id else None,
        ip_address=client_ip, user_agent=user_agent, status=True,
    )
    logger.info("平台应用端用户退出登录")
    return ApiResponse.success(message="退出登录成功")
