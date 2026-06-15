from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.session import get_db
from app.database.models import User
from app.schemas.user import LoginRequest, TokenResponse, UserResponse, UserProfileUpdate
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
from app.services.user_service import UserService
from app.services.audit_service import log_audit
from app.utils.security import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
from app.utils.token_store import revoke_token
from app.utils.exceptions import UnauthorizedException, BadRequestException
from app.dependencies.auth import get_current_user, get_current_user_info
from app.config import get_settings
from app.utils.logger import get_logger
import os

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["认证"])
_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
limiter = Limiter(key_func=get_remote_address, config_filename=os.path.join(_base_dir, "slowapi.env"))


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
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax",
        secure=secure,
    )
    response.delete_cookie(
        key="refresh_token",
        path="/api/auth/refresh",
        httponly=True,
        samesite="strict",
        secure=secure,
    )


@router.post("/login", response_model=ApiResponse)
@limiter.limit("10/minute")
def login(request: Request, login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """用户认证并返回 JWT Access + Refresh 双令牌。"""
    user_service = UserService(db)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # 先检查用户是否存在及锁定状态，返回更友好提示
    user = user_service.get_by_username(login_data.username)
    if user and user.login_locked_until:
        if user.login_locked_until > datetime.now(timezone.utc):
            remaining = (user.login_locked_until - datetime.now(timezone.utc)).seconds // 60
            log_audit(action="LOGIN", module="认证", description=f"登录失败: 账号已锁定", username=login_data.username, ip_address=client_ip, user_agent=user_agent, status=False)
            raise BadRequestException(f"账号已锁定，请 {remaining} 分钟后重试")

    user = user_service.authenticate(login_data.username, login_data.password)
    if not user:
        log_audit(action="LOGIN", module="认证", description="登录失败: 用户名或密码错误", username=login_data.username, ip_address=client_ip, user_agent=user_agent, status=False)
        raise UnauthorizedException("用户名或密码错误")

    # 创建双令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # 设置 Cookie
    _set_auth_cookies(response, access_token, refresh_token)

    # 使用客户端 IP 更新登录信息
    user_service.update_login_info(user, ip_address=client_ip)

    logger.info("用户登录: 用户名='%s' IP=%s", user.username, client_ip)
    log_audit(action="LOGIN", module="认证", description="登录成功", user_id=user.id, username=user.username, ip_address=client_ip, user_agent=user_agent, status=True)
    user_data = UserResponse.model_validate(user)
    return ApiResponse.success(data=TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data,
    ))


@router.post("/refresh", response_model=ApiResponse)
@limiter.limit("30/minute")
def refresh_token(request: Request, response: Response):
    """使用 Refresh Token 换取新的 Access Token。"""
    refresh_tok = request.cookies.get("refresh_token")
    if not refresh_tok:
        raise UnauthorizedException("缺少刷新令牌")

    payload = decode_refresh_token(refresh_tok)
    if not payload:
        raise UnauthorizedException("刷新令牌无效或已过期")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("令牌载荷无效")

    # 颁发新的 Access Token（Refresh Token 继续有效）
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
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """退出登录：将当前 Access/Refresh 令牌加入黑名单并清除 Cookie。"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # 尝试提取当前用户信息用于审计
    user_id = None
    username = None
    access_tok = request.cookies.get("access_token")
    if access_tok:
        payload = decode_access_token(access_tok)
        if payload:
            user_id = payload.get("sub")
            from datetime import timezone
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            revoke_token(payload["jti"], exp)

    # 撤销 Refresh Token
    refresh_tok = request.cookies.get("refresh_token")
    if refresh_tok:
        payload = decode_refresh_token(refresh_tok)
        if payload:
            from datetime import timezone
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            revoke_token(payload["jti"], exp)

    _clear_auth_cookies(response)
    log_audit(action="LOGOUT", module="认证", description="退出登录", user_id=int(user_id) if user_id else None, ip_address=client_ip, user_agent=user_agent, status=True)
    logger.info("用户退出登录")
    return ApiResponse.success(message="退出登录成功")


@router.get("/me", response_model=ApiResponse)
def get_current_user_info_endpoint(current_user_info: CurrentUser = Depends(get_current_user_info)):
    """获取当前用户信息，包括权限和菜单。"""
    return ApiResponse.success(data=current_user_info)


@router.put("/profile", response_model=ApiResponse)
def update_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新当前用户自己的资料（昵称、邮箱、电话、性别）。"""
    service = UserService(db)
    user = service.update(current_user.id, data)
    return ApiResponse.success(data=UserResponse.model_validate(user))
