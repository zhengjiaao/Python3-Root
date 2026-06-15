import os
import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """从环境变量加载的应用配置。

    生产环境必须设置强密钥，否则启动失败。
    """

    # 应用配置
    ENVIRONMENT: str = "development"  # development / production
    APP_NAME: str = "Platform Admin"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = ""

    # 数据库配置
    DB_TYPE: str = "sqlite"
    SQLITE_DB_FILE: str = "data/platform_admin.db"

    # MySQL 配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "platform_admin"

    # PostgreSQL 配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DATABASE: str = "platform_admin"

    # JWT 配置
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    LOG_FILE: str = "app.log"

    # 管理员默认配置（仅首次初始化使用，生产环境请修改）
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = ""

    # 内部服务间通信密钥（管理端与应用端之间的 API 鉴权）
    INTERNAL_API_KEY: str = ""

    # CORS 配置
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "mysql":
            return (
                f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
            )
        elif self.DB_TYPE == "postgresql":
            return (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}"
            )
        else:
            # SQLite 作为内嵌数据库
            db_dir = os.path.dirname(self.SQLITE_DB_FILE)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            return f"sqlite:///{self.SQLITE_DB_FILE}"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """获取异步数据库 URL（用于未来异步支持）。"""
        if self.DB_TYPE == "mysql":
            return self.DATABASE_URL.replace("mysql+pymysql", "mysql+aiomysql")
        elif self.DB_TYPE == "postgresql":
            return self.DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg")
        return self.DATABASE_URL.replace("sqlite", "sqlite+aiosqlite")

    def validate_security(self) -> None:
        """生产环境安全校验。"""
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError("生产环境必须设置 SECRET_KEY（长度 ≥ 32）")
            if not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("生产环境必须设置 JWT_SECRET_KEY（长度 ≥ 32）")
            if self.DEBUG:
                raise ValueError("生产环境必须设置 DEBUG=false")
            if not self.ADMIN_PASSWORD or len(self.ADMIN_PASSWORD) < 8:
                raise ValueError("生产环境必须设置强管理员密码（长度 ≥ 8）")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_security()
    return settings
