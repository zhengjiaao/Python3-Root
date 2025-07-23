import os
import urllib.parse
import mimetypes

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Response
from sqlalchemy.orm import Session
# from . import services, schemas, database, models
from . import services, schemas, models
from ..core import database

models.Base.metadata.create_all(bind=database.engine)

files_api = APIRouter()


async def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@files_api.post("/files/", response_model=schemas.File)
async def create_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_data = await file.read()
    file_create = schemas.FileCreate(filename=file.filename)
    return await services.create_file(db=db, file=file_create, file_data=file_data)


@files_api.post("/files/batch", response_model=list[schemas.File])
async def create_multiple_files(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    """
    批量上传多个文件

    Args:
        files: 文件列表
        db: 数据库会话

    Returns:
        上传文件的信息列表
    """
    if len(files) > 10:  # 限制一次最多上传10个文件
        raise HTTPException(status_code=400, detail="Cannot upload more than 10 files at once")

    uploaded_files = []

    for file in files:
        # 检查文件大小（例如限制为 50MB）
        contents = await file.read()
        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File {file.filename} is too large (max 50MB)")

        # 重置文件指针
        await file.seek(0)

        file_create = schemas.FileCreate(filename=file.filename)
        db_file = await services.create_file(db=db, file=file_create, file_data=contents)
        uploaded_files.append(db_file)

    return uploaded_files

@files_api.get("/files/{file_id}", response_model=schemas.File)
async def read_file(file_id: str, db: Session = Depends(get_db)):
    db_file = await services.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file


@files_api.get("/files/", response_model=list[schemas.File])
async def read_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    files = await services.get_files(db, skip=skip, limit=limit)
    return files


@files_api.get("/files/{file_id}/download")
async def download_file(file_id: str, db: Session = Depends(get_db)):
    db_file = await services.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    file_path = os.path.join("uploads", db_file.file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # 使用 urllib.parse.quote 对文件名进行编码
    encoded_filename = urllib.parse.quote(db_file.filename)
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}

    return Response(content=open(file_path, "rb").read(), media_type="application/octet-stream", headers=headers)


@files_api.delete("/files/{file_id}", response_model=schemas.File)
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    db_file = await services.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    await services.delete_file(db, file_id=file_id)
    return db_file


@files_api.get("/files/{file_id}/preview")
async def preview_file(file_id: str, db: Session = Depends(get_db)):
    db_file = await services.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    file_path = os.path.join("uploads", db_file.file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # 获取文件的 MIME 类型
    mime_type, _ = mimetypes.guess_type(db_file.filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    # 支持预览的 MIME 类型列表
    previewable_mime_types = ["application/pdf", "text/plain", "image/jpeg", "image/png", "image/gif"]

    if mime_type in previewable_mime_types:
        disposition = "inline"
    else:
        disposition = "attachment"

    # 使用 urllib.parse.quote 对文件名进行编码
    encoded_filename = urllib.parse.quote(db_file.filename)
    headers = {"Content-Disposition": f"{disposition}; filename*=UTF-8''{encoded_filename}"}

    return Response(content=open(file_path, "rb").read(), media_type=mime_type, headers=headers)
