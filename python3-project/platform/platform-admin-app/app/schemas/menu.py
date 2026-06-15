from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MenuBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = None
    path: Optional[str] = Field(None, max_length=255)
    component: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    menu_type: str = Field("directory", pattern="^(directory|menu|button)$")
    permission_key: Optional[str] = Field(None, max_length=100)
    sort_order: int = 0
    visible: bool = True
    status: bool = True
    is_external: bool = False
    is_cache: bool = False


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[int] = None
    path: Optional[str] = Field(None, max_length=255)
    component: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    menu_type: Optional[str] = Field(None, pattern="^(directory|menu|button)$")
    permission_key: Optional[str] = Field(None, max_length=100)
    sort_order: Optional[int] = None
    visible: Optional[bool] = None
    status: Optional[bool] = None
    is_external: Optional[bool] = None
    is_cache: Optional[bool] = None


class MenuResponse(MenuBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MenuTreeNode(MenuResponse):
    children: list["MenuTreeNode"] = []

    model_config = {"from_attributes": True}
