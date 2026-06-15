from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_database_engine():
    """Create database engine based on configuration."""
    settings = get_settings()
    connect_args = {}
    if settings.DB_TYPE == "sqlite":
        connect_args = {"check_same_thread": False}

    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,  # SQL logging controlled via LOG_LEVEL in app/utils/logger.py
        connect_args=connect_args,
        pool_pre_ping=True if settings.DB_TYPE != "sqlite" else False,
    )
    return engine


engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 白名单：允许的表和列（防止 SQL 注入）
_MIGRATION_WHITELIST = {
    ("sys_user", "login_fail_count", "INTEGER DEFAULT 0"),
    ("sys_user", "login_locked_until", "DATETIME"),
    ("sys_permission", "updated_at", "DATETIME"),
}


def _migrate_add_column(table_name: str, column_name: str, column_type: str) -> None:
    """安全地为已有表添加缺失的列（仅 SQLite / MySQL / PostgreSQL 通用）。"""
    # 严格白名单校验
    if (table_name, column_name, column_type) not in _MIGRATION_WHITELIST:
        logger.error("非法迁移参数被拒绝: %s.%s %s", table_name, column_name, column_type)
        raise ValueError(f"未授权的迁移操作: {table_name}.{column_name}")

    insp = inspect(engine)
    if table_name not in insp.get_table_names():
        return
    existing = {col["name"] for col in insp.get_columns(table_name)}
    if column_name not in existing:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
        logger.info("数据库迁移: %s.%s 列已添加", table_name, column_name)


def migrate_db() -> None:
    """增量迁移: 为已有表补充模型中新增的列。

    ⚠️ 企业级建议：使用 Alembic 管理数据库版本迁移，替代此简易实现。
    """
    _migrate_add_column("sys_user", "login_fail_count", "INTEGER DEFAULT 0")
    _migrate_add_column("sys_user", "login_locked_until", "DATETIME")
    _migrate_add_column("sys_permission", "updated_at", "DATETIME")


def init_db():
    """Initialize database: create all tables + run incremental migration."""
    from app.database.base import Base
    # Import all models to ensure they are registered
    from app.database.models import (  # noqa: F401
        User, Role, Permission, Menu, Department, AuditLog,
        user_roles, role_permissions, role_menus,
    )
    Base.metadata.create_all(bind=engine)
    migrate_db()


def check_db_ready() -> bool:
    """检查数据库核心表是否已存在（供应用端启动时验证，不主动创建表）。"""
    insp = inspect(engine)
    return "sys_user" in insp.get_table_names()
