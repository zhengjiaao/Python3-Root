"""JWT 令牌黑名单存储。

提供内存黑名单（默认）和可扩展的 Redis/数据库接口。
Access Token 过期时间短（15分钟），Refresh Token 可撤销。
"""

import threading
import time
from datetime import datetime, timezone
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TokenBlacklist:
    """内存令牌黑名单，带自动清理。"""

    def __init__(self):
        self._store: dict[str, float] = {}  # jti -> exp_timestamp
        self._lock = threading.Lock()

    def add(self, jti: str, exp: datetime) -> None:
        """将令牌 jti 加入黑名单。"""
        with self._lock:
            self._store[jti] = exp.timestamp()
        logger.info("令牌已加入黑名单: jti=%s", jti)

    def is_blacklisted(self, jti: str) -> bool:
        """检查令牌是否已被撤销。"""
        with self._lock:
            return jti in self._store

    def cleanup(self) -> None:
        """清理已过期的黑名单记录。"""
        now = datetime.now(timezone.utc).timestamp()
        with self._lock:
            expired = [jti for jti, ts in self._store.items() if ts < now]
            for jti in expired:
                del self._store[jti]
            if expired:
                logger.debug("清理 %d 条过期黑名单记录", len(expired))


# 全局单例
_blacklist = TokenBlacklist()


def revoke_token(jti: str, exp: datetime) -> None:
    """撤销指定令牌。"""
    _blacklist.add(jti, exp)


def is_token_revoked(jti: str) -> bool:
    """检查令牌是否已被撤销。"""
    return _blacklist.is_blacklisted(jti)


def cleanup_expired_tokens() -> None:
    """手动触发清理过期令牌（可选，由中间件定期调用）。"""
    _blacklist.cleanup()
