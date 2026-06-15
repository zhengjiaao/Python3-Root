"""管理端 API 客户端：应用端通过此客户端调用管理端内部 API。

所有用户认证、权限校验、审计日志等操作均通过 HTTP 调用管理端完成，
应用端不再拥有独立的用户数据库。
"""

import time
from typing import Optional, Any

import httpx

from platform_app.config import get_app_settings
from platform_app.utils.logger import get_logger

logger = get_logger(__name__)

# 用户数据内存缓存: user_id -> (data, timestamp)
_user_cache: dict[int, tuple[dict, float]] = {}
_CACHE_TTL = 60  # 缓存有效期（秒）


class AdminClientError(Exception):
    """管理端 API 调用异常。"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AdminClient:
    """管理端内部 API 的 HTTP 客户端。"""

    def __init__(self):
        self._settings = None

    @property
    def settings(self):
        if self._settings is None:
            self._settings = get_app_settings()
        return self._settings

    @property
    def _base_url(self) -> str:
        return self.settings.ADMIN_APP_URL.rstrip("/")

    @property
    def _api_key(self) -> str:
        return self.settings.ADMIN_APP_INTERNAL_API_KEY

    @property
    def _headers(self) -> dict[str, str]:
        return {"X-Internal-API-Key": self._api_key, "Content-Type": "application/json"}

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """发送 HTTP 请求到管理端内部 API。"""
        url = f"{self._base_url}{path}"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.request(
                    method, url, headers=self._headers, **kwargs
                )
        except httpx.ConnectError:
            logger.error("无法连接管理端: %s", self._base_url)
            raise AdminClientError("无法连接管理端服务", 503)
        except httpx.TimeoutException:
            logger.error("管理端请求超时: %s %s", method, path)
            raise AdminClientError("管理端请求超时", 504)

        try:
            data = response.json()
        except Exception:
            logger.error("管理端返回非 JSON 响应: %s", response.text[:200])
            raise AdminClientError("管理端返回无效响应", 502)

        if response.status_code >= 400:
            message = data.get("message", data.get("detail", "管理端请求失败"))
            logger.warning("管理端返回错误: %s %s -> %s %s", method, path, response.status_code, message)
            raise AdminClientError(message, response.status_code)

        return data

    # ============================================================
    # 认证
    # ============================================================

    def login(self, username: str, password: str) -> dict:
        """调用管理端登录认证。返回用户数据或抛出异常。"""
        result = self._request("POST", "/api/internal/auth/login", json={
            "username": username,
            "password": password,
        })
        api_data = result.get("data", {})
        code = result.get("code", 200)

        if code != 200:
            raise AdminClientError(result.get("message", "登录失败"), code)

        user_data = api_data.get("user", {})
        # 缓存用户数据
        if user_data and "id" in user_data:
            self._cache_user(user_data["id"], user_data)

        return api_data

    def get_user(self, user_id: int, use_cache: bool = True) -> Optional[dict]:
        """获取用户详情（含角色和权限）。优先从缓存读取。"""
        if use_cache:
            cached = self._get_cached_user(user_id)
            if cached is not None:
                return cached

        result = self._request("GET", f"/api/internal/users/{user_id}")
        code = result.get("code", 200)
        if code == 404:
            return None
        if code != 200:
            raise AdminClientError(result.get("message", "获取用户失败"), code)

        user_data = result.get("data")
        if user_data:
            self._cache_user(user_id, user_data)
        return user_data

    def update_login_info(self, user_id: int, ip_address: Optional[str] = None) -> None:
        """更新用户登录信息。"""
        self._request(
            "POST",
            "/api/internal/auth/update-login-info",
            params={"user_id": user_id},
            json={"ip_address": ip_address},
        )

    # ============================================================
    # 个人中心
    # ============================================================

    def update_profile(self, user_id: int, profile_data: dict) -> dict:
        """更新用户资料。"""
        result = self._request("PUT", f"/api/internal/users/{user_id}/profile", json=profile_data)
        code = result.get("code", 200)
        if code != 200:
            raise AdminClientError(result.get("message", "更新资料失败"), code)

        user_data = result.get("data", {})
        # 更新缓存
        if user_data and "id" in user_data:
            self._cache_user(user_data["id"], user_data)
        return user_data

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        """修改密码。"""
        result = self._request("POST", f"/api/internal/users/{user_id}/change-password", json={
            "old_password": old_password,
            "new_password": new_password,
        })
        code = result.get("code", 200)
        if code != 200:
            raise AdminClientError(result.get("message", "修改密码失败"), code)

    # ============================================================
    # 审计日志
    # ============================================================

    def log_audit(
        self,
        action: str,
        module: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: bool = True,
    ) -> None:
        """记录审计日志到管理端数据库。"""
        try:
            self._request("POST", "/api/internal/audit", json={
                "action": action,
                "module": module,
                "description": description,
                "user_id": user_id,
                "username": username,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "status": status,
            })
        except AdminClientError as e:
            # 审计日志写入失败不应阻断主流程
            logger.error("审计日志写入管理端失败: %s", e.message)

    # ============================================================
    # 健康检查
    # ============================================================

    def health_check(self) -> bool:
        """检查管理端是否可用。"""
        try:
            result = self._request("GET", "/api/internal/health")
            return result.get("code") == 200
        except AdminClientError:
            return False

    # ============================================================
    # 缓存管理
    # ============================================================

    def _cache_user(self, user_id: int, data: dict) -> None:
        """缓存用户数据。"""
        _user_cache[user_id] = (data, time.time())

    def _get_cached_user(self, user_id: int) -> Optional[dict]:
        """从缓存读取用户数据（未命中或已过期返回 None）。"""
        entry = _user_cache.get(user_id)
        if entry is None:
            return None
        data, ts = entry
        if time.time() - ts > _CACHE_TTL:
            del _user_cache[user_id]
            return None
        return data

    def invalidate_user_cache(self, user_id: int) -> None:
        """使缓存失效（登出、修改密码等场景）。"""
        _user_cache.pop(user_id, None)


# 全局单例
admin_client = AdminClient()
