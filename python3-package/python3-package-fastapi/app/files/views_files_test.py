import os
import pytest
import urllib.parse

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import schemas
from ..core.database import Base
from .views import files_api

app = FastAPI()

# 添加路由
app.include_router(files_api, prefix="/api", tags=["files"])

# 创建一个内存数据库用于测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库表
Base.metadata.create_all(bind=engine)

# 创建测试客户端
client = TestClient(app)


@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def test_file():
    return schemas.FileCreate(filename="test.txt")


@pytest.fixture(scope="module")
def test_file_data():
    return b"Test file content"


@pytest.fixture(scope="module")
def test_pdf_file():
    return schemas.FileCreate(filename="test.pdf")


@pytest.fixture(scope="module")
def test_pdf_file_data():
    return b"%PDF-1.5\n%PDF-1.5\n%%EOF"


@pytest.mark.asyncio
async def test_create_file(db, test_file, test_file_data):
    response = client.post("/api/files/", files={"file": (test_file.filename, test_file_data)})
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == test_file.filename
    file_path = os.path.join("uploads", data["file_id"])  # 使用响应中的 file_id
    assert os.path.exists(file_path)
    with open(file_path, "rb") as f:
        assert f.read() == test_file_data


@pytest.mark.asyncio
async def test_read_file(db, test_file, test_file_data):
    response = client.post("/api/files/", files={"file": (test_file.filename, test_file_data)})
    assert response.status_code == 200
    data = response.json()
    file_id = data["file_id"]

    response = client.get(f"/api/files/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == test_file.filename


@pytest.mark.asyncio
async def test_read_files(db, test_file, test_file_data):
    response = client.post("/api/files/", files={"file": (test_file.filename, test_file_data)})
    assert response.status_code == 200

    response = client.get("/api/files/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == test_file.filename


@pytest.mark.asyncio
async def test_download_file(db, test_file, test_file_data):
    response = client.post("/api/files/", files={"file": (test_file.filename, test_file_data)})
    assert response.status_code == 200
    data = response.json()
    file_id = data["file_id"]

    response = client.get(f"/api/files/{file_id}/download")
    assert response.status_code == 200
    assert response.headers[
               "Content-Disposition"] == f"attachment; filename*=UTF-8''{urllib.parse.quote(test_file.filename)}"
    assert response.content == test_file_data


@pytest.mark.asyncio
async def test_delete_file(db, test_file, test_file_data):
    response = client.post("/api/files/", files={"file": (test_file.filename, test_file_data)})
    assert response.status_code == 200
    data = response.json()
    file_id = data["file_id"]

    response = client.delete(f"/api/files/{file_id}")
    file_path = os.path.join("uploads", file_id)

    assert response.status_code == 200
    assert not os.path.exists(file_path)


@pytest.mark.asyncio
async def test_preview_file(db, test_file, test_file_data, test_pdf_file, test_pdf_file_data):
    # Test preview for a text file
    response = client.post("/api/files/", files={"file": (test_file.filename, test_file_data)})
    assert response.status_code == 200
    data = response.json()
    file_id = data["file_id"]

    response = client.get(f"/api/files/{file_id}/preview")
    assert response.status_code == 200
    assert response.headers[
               "Content-Disposition"] == f"inline; filename*=UTF-8''{urllib.parse.quote(test_file.filename)}"
    assert response.content == test_file_data

    # Test download for a PDF file
    pdf_file_path = os.path.join("uploads", test_pdf_file.file_id)
    if os.path.exists(pdf_file_path):
        os.remove(pdf_file_path)

    response = client.post("/api/files/", files={"file": (test_pdf_file.filename, test_pdf_file_data)})
    assert response.status_code == 200
    data = response.json()
    pdf_file_id = data["file_id"]

    response = client.get(f"/api/files/{pdf_file_id}/preview")
    assert response.status_code == 200
    assert response.headers[
               "Content-Disposition"] == f"inline; filename*=UTF-8''{urllib.parse.quote(test_pdf_file.filename)}"
    assert response.content == test_pdf_file_data
