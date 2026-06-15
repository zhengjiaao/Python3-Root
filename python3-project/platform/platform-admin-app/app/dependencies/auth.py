import time
from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session import get_db
from app.utils.security import decode_access_token
from app.utils.exceptions import UnauthorizedException, ForbiddenException
from app.utils.logger import get_logger
from app.schemas.user import CurrentUser, RoleBrief
from app.services.user_service import UserService
from app.services.menu_service import MenuService

logger = get_logger(__name__)

# 菜单树缓存: (user_id, tuple(menu_ids)) -> (menu_tree, timestamp)
_menu_tree_cache: dict[tuple[int, tuple[int, ...]], tuple[list, float]] = {}
_MENU_CACHE_TTL = 60  # 秒


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """从 JWT Access 令牌（Cookie 或请求头）中提取并验证当前用户。"""
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

    user_service = UserService(db)
    user = user_service.get_by_id(int(user_id))
    if user is None:
        logger.warning("认证失败: 用户 id=%s 不存在", user_id)
        raise UnauthorizedException("用户不存在")
    if not user.status:
        logger.warning("认证失败: 用户 '%s' 已禁用", user.username)
        raise UnauthorizedException("用户账号已禁用")

    return user


def get_current_user_info(request: Request, db: Session = Depends(get_db)) -> CurrentUser:
    """获取当前用户详细信息，包括权限和菜单。"""
    user = get_current_user(request, db)

    # 从用户角色中收集所有权限和菜单 ID
    permissions = set()
    menu_ids = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.permission_key)
        for menu in role.menus:
            menu_ids.add(menu.id)

    # 超级管理员获取所有权限 + 所有菜单
    if user.is_superuser:
        permissions.add("*")
        menu_service = MenuService(db)
        for m in menu_service.get_all():
            menu_ids.add(m.id)

    # 构建菜单树（带 TTL 缓存，减少重复计算）
    cache_key = (user.id, tuple(sorted(menu_ids)))
    now = time.time()
    cached = _menu_tree_cache.get(cache_key)
    if cached and now - cached[1] < _MENU_CACHE_TTL:
        menu_tree = cached[0]
    else:
        menu_service = MenuService(db)
        menu_tree = menu_service.build_user_menu_tree(list(menu_ids)) if menu_ids else []
        _menu_tree_cache[cache_key] = (menu_tree, now)

    return CurrentUser(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        is_superuser=user.is_superuser,
        is_admin=user.is_admin,
        roles=[RoleBrief(id=r.id, name=r.name, role_key=r.role_key) for r in user.roles],
        permissions=list(permissions),
        menus=menu_tree,
    )


def require_permissions(*required_perms: str):
    """依赖注入工厂: 检查当前用户是否拥有所需权限。

    支持通配符匹配:
    - '*' 匹配任何所需权限
    - 'system:*' 匹配所有 'system:xxx' 权限
    - 'system:user:*' 匹配所有 'system:user:xxx' 权限
    """
    def permission_checker(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:
            return user

        user_perms = set()
        for role in user.roles:
            for perm in role.permissions:
                user_perms.add(perm.permission_key)

        for perm in required_perms:
            if not _has_permission(perm, user_perms):
                raise ForbiddenException(f"缺少所需权限: {perm}")

        return user
    return permission_checker


def require_roles(*required_roles: str):
    """依赖注入工厂: 检查当前用户是否拥有所需角色。"""
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:
            return user

        user_role_keys = set()
        for role in user.roles:
            user_role_keys.add(role.role_key)

        for role_key in required_roles:
            if role_key not in user_role_keys:
                raise ForbiddenException(f"缺少所需角色: {role_key}")

        return user
    return role_checker


def _has_permission(required_perm: str, user_perms: set[str]) -> bool:
    """检查用户的权限集合是否满足所需权限。

    支持通配符匹配:
    - '*' 匹配所有
    - 'module:*' 匹配所有 'module:xxx' 权限
    - 'module:sub:*' 匹配所有 'module:sub:xxx' 权限
    """
    if required_perm in user_perms:
        return True
    # 检查通配符匹配
    parts = required_perm.split(":")
    for i in range(len(parts), 0, -1):
        wildcard = ":".join(parts[:i]) + ":*"
        if wildcard in user_perms:
            return True
    # 检查全局通配符
    if "*" in user_perms:
        return True
    return False


def _extract_access_token(request: Request) -> Optional[str]:
    """从 Cookie 或 Authorization 请求头中提取 Access Token。"""
    # 优先从 Cookie 获取
    token = request.cookies.get("access_token")
    if token:
        return token

    # 尝试从 Authorization 请求头获取
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


def _extract_refresh_token(request: Request) -> Optional[str]:
    """从 Cookie 中提取 Refresh Token。"""
    return request.cookies.get("refresh_token")
