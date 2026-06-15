from typing import Optional, Any, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageRequest(BaseModel):
    """分页请求参数。"""
    page: int = 1
    page_size: int = 10
    keyword: Optional[str] = None


class PageResponse(BaseModel, Generic[T]):
    """分页响应包装（泛型化以提升类型安全）。"""
    total: int = 0
    page: int = 1
    page_size: int = 10
    items: list[T] = Field(default_factory=list)


class ApiResponse(BaseModel):
    """标准 API 响应包装。"""
    code: int = 200
    message: str = "成功"
    data: Any = None

    @classmethod
    def success(cls, data: Any = None, message: str = "成功") -> "ApiResponse":
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, message: str = "错误", code: int = 400) -> "ApiResponse":
        return cls(code=code, message=message, data=None)

    @classmethod
    def unauthorized(cls, message: str = "未授权") -> "ApiResponse":
        return cls(code=401, message=message, data=None)

    @classmethod
    def forbidden(cls, message: str = "禁止访问") -> "ApiResponse":
        return cls(code=403, message=message, data=None)
