from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """审计日志响应模型。"""

    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    module: Optional[str] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
