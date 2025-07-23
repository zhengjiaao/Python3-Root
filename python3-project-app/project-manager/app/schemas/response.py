from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    per_page: int
    items: List[T]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

class MessageResponse(BaseModel):
    message: str