from pydantic import BaseModel, Field
# from pydantic_settings import ConfigDict
from datetime import datetime
from typing import Optional


class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100, example="Website Redesign")
    description: Optional[str] = Field(None, example="Redesign company website")
    end_date: Optional[datetime] = None
    status: Optional[str] = Field("active", example="active")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(None, max_length=100, example="Website Redesign v2")


class ProjectResponse(ProjectBase):
    id: int
    start_date: datetime
    description: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

    # model_config = ConfigDict(from_attributes=True)