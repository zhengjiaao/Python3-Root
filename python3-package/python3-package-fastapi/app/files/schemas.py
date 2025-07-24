from pydantic import BaseModel
from datetime import datetime

class FileBase(BaseModel):
    filename: str


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int
    file_id: str  # 唯一文件ID
    created_at: datetime  # 创建时间

    class Config:
        from_attributes = True