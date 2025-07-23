import os
from sqlalchemy.orm import Session
from . import models, schemas
import uuid

# 定义文件存储路径
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


async def create_file(db: Session, file: schemas.FileCreate, file_data: bytes):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id)
    with open(file_path, "wb") as f:
        f.write(file_data)

    db_file = models.File(filename=file.filename, file_id=file_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


async def get_file(db: Session, file_id: str):
    return db.query(models.File).filter(models.File.file_id == file_id).first()


async def get_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.File).offset(skip).limit(limit).all()


async def delete_file(db: Session, file_id: str):
    db_file = db.query(models.File).filter(models.File.file_id == file_id).first()
    if db_file:
        os.remove(os.path.join(UPLOAD_DIR, db_file.file_id))  # 删除本地文件
        db.delete(db_file)
        db.commit()
