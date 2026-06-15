from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


# ============================================================
# User Schemas
# ============================================================

class UserBase(BaseModel):
    """用户基础模型。"""
    username: str = Field(..., min_length=3, max_length=50)
    nickname: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    gender: int = Field(0, ge=0, le=2)
    status: bool = True
    department_id: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)
    role_ids: list[int] = []

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-=+\[\]\\/]', v):
            raise ValueError('密码必须包含至少一个特殊字符 (!@#$%^&*等)')
        return v


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[int] = Field(None, ge=0, le=2)
    status: Optional[bool] = None
    department_id: Optional[int] = None
    role_ids: Optional[list[int]] = None


class UserPasswordUpdate(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-=+\[\]\\/]', v):
            raise ValueError('密码必须包含至少一个特殊字符 (!@#$%^&*等)')
        return v


class UserResetPassword(BaseModel):
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-=+\[\]\\/]', v):
            raise ValueError('密码必须包含至少一个特殊字符 (!@#$%^&*等)')
        return v


class RoleBrief(BaseModel):
    id: int
    name: str
    role_key: str

    model_config = {"from_attributes": True}


class DepartmentBrief(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserResponse(UserBase):
    id: int
    is_superuser: bool
    avatar: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    roles: list[RoleBrief] = []
    department: Optional[DepartmentBrief] = None

    model_config = {"from_attributes": True}


# ============================================================
# Auth Schemas
# ============================================================

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class CurrentUser(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    is_superuser: bool
    is_admin: bool
    roles: list[RoleBrief] = []
    permissions: list[str] = []
    menus: list[dict] = []

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    """用户更新自己资料的模型。"""
    nickname: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[int] = Field(None, ge=0, le=2)
