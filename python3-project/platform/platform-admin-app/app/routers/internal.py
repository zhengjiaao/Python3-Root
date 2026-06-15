"""管理端内部 API 路由：供应用端（客户端）调用。

所有端点需要 X-Internal-API-Key 请求头进行服务间鉴权。
应用端通过这些 API 获取用户数据、完成认证、记录审计日志等，
不再拥有独立的用户数据库。
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.session import get_db
from app.database.models import User
from app.schemas.user import (
    LoginRequest, UserResponse, UserProfileUpdate, UserPasswordUpdate,
    RoleBrief, DepartmentBrief,
)
from app.schemas.response import ApiResponse
from app.services.user_service import UserService
from app.services.audit_service import log_audit
from app.utils.security import verify_password
from app.utils.exceptions import UnauthorizedException, BadRequestException, NotFoundException
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/internal", tags=["内部服务"])


# ============================================================
# 鉴权依赖
# ============================================================

async def verify_internal_api_key(x_internal_api_key: str = Header(...)):
    """校验服务间通信密钥。"""
    settings = get_settings()
    if not settings.INTERNAL_API_KEY:
        raise UnauthorizedException("管理端未配置 INTERNAL_API_KEY")
    if x_internal_api_key != settings.INTERNAL_API_KEY:
        raise UnauthorizedException("内部 API 密钥无效")


# ============================================================
# Schemas
# ============================================================

class InternalLoginResponse(BaseModel):
    """内部登录接口返回数据。"""
    user: UserResponse
    locked: bool = False
    lock_remaining_minutes: int = 0


class InternalAuditRequest(BaseModel):
    """内部审计日志请求。"""
    action: str
    module: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: bool = True


class InternalUpdateLoginInfoRequest(BaseModel):
    """更新登录信息请求。"""
    ip_address: Optional[str] = None


class InternalUserDetail(BaseModel):
    """内部用户详情（含权限信息）。"""
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    gender: int = 0
    status: bool = True
    department_id: Optional[int] = None
    is_superuser: bool = False
    is_admin: bool = False
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    roles: list[RoleBrief] = []
    permissions: list[str] = []
    department: Optional[DepartmentBrief] = None

    model_config = {"from_attributes": True}


# ============================================================
# 端点
# ============================================================

@router.post("/auth/login", response_model=ApiResponse)
def internal_login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
    _auth=Depends(verify_internal_api_key),
):
    """应用端登录认证：验证用户名密码，返回用户数据。

    不颁发 token（由应用端自行颁发），仅做凭证校验和账号状态检查。
    """
    user_service = UserService(db)

    # 检查账号是否被锁定
    user = user_service.get_by_username(login_data.username)
    if user and user.login_locked_until and user.login_locked_until > datetime.now(timezone.utc):
        remaining = (user.login_locked_until - datetime.now(timezone.utc)).seconds // 60
        return ApiResponse.error(
            message=f"账号已锁定，请 {remaining} 分钟后重试",
            code=423,
        )

    # 验证凭证
    user = user_service.authenticate(login_data.username, login_data.password)
    if not user:
        return ApiResponse.error(message="用户名或密码错误", code=401)

    user_data = UserResponse.model_validate(user)
    return ApiResponse.success(data=InternalLoginResponse(user=user_data))


@router.get("/users/{user_id}", response_model=ApiResponse)
def internal_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(verify_internal_api_key),
):
    """获取用户详情（含角色和权限列表）。"""
    user_service = UserService(db)
    try:
        user = user_service.get_by_id(user_id)
    except NotFoundException:
        return ApiResponse.error(message="用户不存在", code=404)

    if not user.status:
        return ApiResponse.error(message="用户账号已禁用", code=403)

    # 收集权限
    permissions = set()
    if user.is_superuser:
        permissions.add("*")
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.permission_key)

    detail = InternalUserDetail(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        gender=user.gender,
        status=user.status,
        department_id=user.department_id,
        is_superuser=user.is_superuser,
        is_admin=user.is_admin,
        last_login_at=user.last_login_at,
        last_login_ip=user.last_login_ip,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[RoleBrief(id=r.id, name=r.name, role_key=r.role_key) for r in user.roles],
        permissions=list(permissions),
        department=DepartmentBrief(id=user.department.id, name=user.department.name) if user.department else None,
    )
    return ApiResponse.success(data=detail)


@router.put("/users/{user_id}/profile", response_model=ApiResponse)
def internal_update_profile(
    user_id: int,
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(verify_internal_api_key),
):
    """更新用户资料（应用端个人中心调用）。"""
    user_service = UserService(db)
    try:
        user = user_service.update(user_id, data)
    except NotFoundException:
        return ApiResponse.error(message="用户不存在", code=404)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.post("/users/{user_id}/change-password", response_model=ApiResponse)
def internal_change_password(
    user_id: int,
    data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(verify_internal_api_key),
):
    """修改密码（应用端调用）。"""
    user_service = UserService(db)
    try:
        user = user_service.get_by_id(user_id)
    except NotFoundException:
        return ApiResponse.error(message="用户不存在", code=404)

    if not verify_password(data.old_password, user.password):
        return ApiResponse.error(message="原密码错误", code=400)

    user_service.reset_password(user_id, data.new_password)
    return ApiResponse.success(message="密码修改成功")


@router.post("/auth/update-login-info", response_model=ApiResponse)
def internal_update_login_info(
    data: InternalUpdateLoginInfoRequest,
    user_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(verify_internal_api_key),
):
    """更新用户登录信息（最后登录时间/IP）。"""
    user_service = UserService(db)
    try:
        user = user_service.get_by_id(user_id)
    except NotFoundException:
        return ApiResponse.error(message="用户不存在", code=404)
    user_service.update_login_info(user, ip_address=data.ip_address)
    return ApiResponse.success(message="登录信息已更新")


@router.post("/audit", response_model=ApiResponse)
def internal_audit(
    data: InternalAuditRequest,
    _auth=Depends(verify_internal_api_key),
):
    """应用端审计日志写入管理端数据库。"""
    log_audit(
        action=data.action,
        module=data.module,
        description=data.description,
        user_id=data.user_id,
        username=data.username,
        ip_address=data.ip_address,
        user_agent=data.user_agent,
        status=data.status,
    )
    return ApiResponse.success(message="审计日志已记录")


@router.get("/health", response_model=ApiResponse)
def internal_health(_auth=Depends(verify_internal_api_key)):
    """管理端健康检查（供应用端启动时验证连接）。"""
    return ApiResponse.success(data={"status": "ok"})
