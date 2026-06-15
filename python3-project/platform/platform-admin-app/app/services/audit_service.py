"""审计日志服务。"""

from typing import Optional

from app.database.models import AuditLog
from app.database.session import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


def log_audit(
    action: str,
    module: Optional[str] = None,
    description: Optional[str] = None,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: bool = True,
) -> None:
    """记录审计日志（使用独立的数据库会话，避免污染主业务事务）。"""
    db = SessionLocal()
    try:
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            module=module,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
        )
        db.add(log)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("审计日志记录失败: %s", exc)
    finally:
        db.close()
