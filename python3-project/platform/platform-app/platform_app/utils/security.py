import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt as pyjwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

from platform_app.config import get_app_settings
from platform_app.utils.token_store import is_token_revoked

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """哈希明文密码。"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配。"""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    """创建 JWT 令牌（内部通用）。"""
    settings = get_app_settings()
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    expire = now + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": jti,
        "type": token_type,
    })
    return pyjwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 访问令牌（有效期短）。"""
    settings = get_app_settings()
    delta = expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, delta, "access")


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 刷新令牌（有效期长）。"""
    settings = get_app_settings()
    delta = expires_delta or timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, delta, "refresh")


def _decode_token(token: str, expected_type: Optional[str] = None) -> Optional[dict]:
    """解码并校验 JWT 令牌。"""
    settings = get_app_settings()
    try:
        payload = pyjwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "jti", "type"]},
        )
        if expected_type and payload.get("type") != expected_type:
            return None
        # 检查黑名单
        jti = payload.get("jti")
        if jti and is_token_revoked(jti):
            return None
        return payload
    except PyJWTError:
        return None


def decode_access_token(token: str) -> Optional[dict]:
    """解码 JWT 访问令牌。无效或已撤销时返回 None。"""
    return _decode_token(token, expected_type="access")


def decode_refresh_token(token: str) -> Optional[dict]:
    """解码 JWT 刷新令牌。无效或已撤销时返回 None。"""
    return _decode_token(token, expected_type="refresh")
