from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from ...database.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    status = Column(String(20), default="active")  # e.g. active/completed

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status
        }