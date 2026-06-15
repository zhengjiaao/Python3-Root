from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    role_key: str = Field(..., min_length=1, max_length=50)
    sort_order: int = 0
    status: bool = True
    remark: Optional[str] = None
    data_scope: int = Field(1, ge=1, le=5)


class RoleCreate(RoleBase):
    permission_ids: list[int] = []
    menu_ids: list[int] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    role_key: Optional[str] = Field(None, min_length=1, max_length=50)
    sort_order: Optional[int] = None
    status: Optional[bool] = None
    remark: Optional[str] = None
    data_scope: Optional[int] = Field(None, ge=1, le=5)
    permission_ids: Optional[list[int]] = None
    menu_ids: Optional[list[int]] = None


class PermissionBrief(BaseModel):
    id: int
    name: str
    permission_key: str
    type: str

    model_config = {"from_attributes": True}


class MenuBrief(BaseModel):
    id: int
    name: str
    path: Optional[str] = None
    icon: Optional[str] = None

    model_config = {"from_attributes": True}


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: list[PermissionBrief] = []
    menus: list[MenuBrief] = []

    model_config = {"from_attributes": True}
