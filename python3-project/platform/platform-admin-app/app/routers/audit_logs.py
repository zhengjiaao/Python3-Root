from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.session import get_db
from app.database.models import User, AuditLog
from app.schemas.response import ApiResponse, PageResponse
from app.schemas.audit_log import AuditLogResponse
from app.dependencies.auth import require_permissions

router = APIRouter(prefix="/api/audit-logs", tags=["审计日志"])


@router.get("", response_model=ApiResponse)
def list_audit_logs(
    request: Request,
    action: Optional[str] = Query(None, max_length=50),
    module: Optional[str] = Query(None, max_length=50),
    username: Optional[str] = Query(None, max_length=50),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("system:audit:list")),
):
    """获取分页审计日志列表。"""
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if module:
        query = query.filter(AuditLog.module.contains(module))
    if username:
        query = query.filter(AuditLog.username.contains(username))

    total = query.count()
    items = (
        query.order_by(desc(AuditLog.id))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ApiResponse.success(
        data=PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[AuditLogResponse.model_validate(item) for item in items],
        )
    )
