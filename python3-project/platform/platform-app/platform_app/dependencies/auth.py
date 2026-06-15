"""应用端认证依赖：通过管理端 API 验证用户身份和权限。

应用端不直接访问数据库，所有用户数据通过 admin_client 从管理端获取。
JWT 令牌在本地解码（与管理端共享密钥），用户详情通过 API 查询。
"""

from typing import Optional

from fastapi import Depends, Request

from platform_app.utils.security import decode_access_token
from platform_app.utils.exceptions import UnauthorizedException, ForbiddenException
from platform_app.utils.logger import get_logger
from platform_app.client.admin_client import admin_client, AdminClientError
from platform_app.models import UserInfo

logger = get_logger(__name__)


def get_current_user(request: Request) -> UserInfo:
    """从 JWT Access 令牌中提取用户 ID，然后从管理端获取用户详情。

    JWT 解码在本地完成（与管理端共享 JWT_SECRET_KEY），
    用户详情通过管理端内部 API 获取（带内存缓存）。
    """
    token = _extract_access_token(request)
    if not token:
        logger.warning("认证失败: 未提供令牌，来源 %s", request.url.path)
        raise UnauthorizedException("未认证")

    payload = decode_access_token(token)
    if not payload:
        logger.warning("认证失败: 令牌无效或已过期，来源 %s", request.url.path)
        raise UnauthorizedException("令牌无效或已过期")

    user_id = payload.get("sub")
    if not user_id:
        logger.warning("认证失败: 令牌缺少 'sub' 声明，来源 %s", request.url.path)
        raise UnauthorizedException("令牌载荷无效")

    # 从管理端 API 获取用户详情（带缓存）
    try:
        user_data = admin_client.get_user(int(user_id))
    except AdminClientError as e:
        logger.error("从管理端获取用户失败: user_id=%s, error=%s", user_id, e.message)
        raise UnauthorizedException("用户验证服务不可用")

    if user_data is None:
        logger.warning("认证失败: 用户 id=%s 不存在", user_id)
        raise UnauthorizedException("用户不存在")

    if not user_data.get("status", True):
        logger.warning("认证失败: 用户 '%s' 已禁用", user_data.get("username"))
        raise UnauthorizedException("用户账号已禁用")

    return UserInfo.model_validate(user_data)


def get_current_user_optional(request: Request) -> Optional[UserInfo]:
    """可选认证：已登录返回用户，未登录返回 None。"""
    try:
        return get_current_user(request)
    except UnauthorizedException:
        return None


def _extract_access_token(request: Request) -> Optional[str]:
    """从 Cookie 或 Authorization 请求头中提取 Access Token。"""
    token = request.cookies.get("access_token")
    if token:
        return token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def require_permissions(*required_perms: str):
    """依赖注入工厂: 检查当前用户是否拥有所需权限（从管理端获取权限列表）。"""
    def permission_checker(user: UserInfo = Depends(get_current_user)) -> UserInfo:
        for perm in required_perms:
            if not user.has_permission(perm):
                raise ForbiddenException(f"缺少所需权限: {perm}")
        return user
    return permission_checker


def require_roles(*required_roles: str):
    """依赖注入工厂: 检查当前用户是否拥有所需角色。"""
    def role_checker(user: UserInfo = Depends(get_current_user)) -> UserInfo:
        for role_key in required_roles:
            if not user.has_role(role_key):
                raise ForbiddenException(f"缺少所需角色: {role_key}")
        return user
    return role_checker
