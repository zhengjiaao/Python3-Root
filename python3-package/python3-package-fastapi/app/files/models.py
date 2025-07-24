from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base
import uuid


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))  # 唯一文件ID
    created_at = Column(DateTime, default=func.now())  # 创建时间
