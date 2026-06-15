import os
import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache


class AppSettings(BaseSettings):
    """平台应用端独立配置。

    应用端不拥有独立的用户数据库，用户体系/权限完全依赖管理端（客户端），
    通过内部 API 获取用户、角色、权限等数据。
    """

    # 应用配置
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Platform App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = ""

    # 运行端口（与 admin 管理端区分，避免冲突）
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8001

    # 平台管理端地址（用于页面跳转或反向代理）
    ADMIN_APP_URL: str = "http://127.0.0.1:8000"

    # 管理端内部 API 密钥（必须与管理端 INTERNAL_API_KEY 一致）
    ADMIN_APP_INTERNAL_API_KEY: str = ""

    # JWT 配置（必须与管理端一致，否则 token 无法互通验证）
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    LOG_FILE: str = "platform_app.log"

    # CORS 配置
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    def validate_security(self) -> None:
        """生产环境安全校验。"""
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError("生产环境必须设置 SECRET_KEY（长度 ≥ 32）")
            if not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("生产环境必须设置 JWT_SECRET_KEY（长度 ≥ 32）")
            if self.DEBUG:
                raise ValueError("生产环境必须设置 DEBUG=false")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 别名：兼容 app-app 内部使用 get_settings() 的场景
@lru_cache()
def get_app_settings() -> AppSettings:
    settings = AppSettings()
    settings.validate_security()
    return settings


# 兼容旧引用 platform_common.config.get_settings
get_settings = get_app_settings
