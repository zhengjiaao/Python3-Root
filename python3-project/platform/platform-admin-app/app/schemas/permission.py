from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    permission_key: str = Field(..., min_length=1, max_length=100)
    type: str = Field("menu", pattern="^(menu|button|api)$")
    parent_id: Optional[int] = None
    path: Optional[str] = Field(None, max_length=255)
    method: Optional[str] = Field(None, pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    sort_order: int = 0
    status: bool = True


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    permission_key: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(menu|button|api)$")
    parent_id: Optional[int] = None
    path: Optional[str] = Field(None, max_length=255)
    method: Optional[str] = Field(None, pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    sort_order: Optional[int] = None
    status: Optional[bool] = None


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PermissionTreeNode(PermissionResponse):
    children: list["PermissionTreeNode"] = []

    model_config = {"from_attributes": True}
