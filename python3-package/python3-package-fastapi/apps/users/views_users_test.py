import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import schemas
from ..core.database import Base
from .views import users_api

app = FastAPI()

# 添加路由
app.include_router(users_api, prefix="/api", tags=["users"])

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
def test_user():
    return schemas.UserCreate(username="testuser", email="test@example.com", password="testpassword")


@pytest.mark.asyncio
async def test_create_user(db, test_user):
    response = client.post("/api/users/", json=test_user.model_dump())  # 更新路由路径
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert "id" in data


@pytest.mark.asyncio
async def test_read_user(db, test_user):
    # 创建用户
    response = client.post("/api/users/", json=test_user.model_dump())  # 更新路由路径
    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]

    # 读取用户
    response = client.get(f"/api/users/{user_id}")  # 更新路由路径
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_read_users(db, test_user):
    # 创建用户
    response = client.post("/api/users/", json=test_user.model_dump())  # 更新路由路径
    assert response.status_code == 200

    # 读取用户列表
    response = client.get("/api/users/")  # 更新路由路径
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == test_user.username
    assert data[0]["email"] == test_user.email


@pytest.mark.asyncio
async def test_delete_user(db, test_user):
    # 创建用户
    response = client.post("/api/users/", json=test_user.model_dump())  # 更新路由路径
    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]

    # 删除用户
    response = client.delete(f"/api/users/{user_id}")  # 更新路由路径
    assert response.status_code == 200
    deleted_user = response.json()
    assert deleted_user["username"] == test_user.username
    assert deleted_user["email"] == test_user.email

    # 再次读取用户，确认用户已被删除
    response = client.get(f"/api/users/{user_id}")  # 更新路由路径
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_user_not_found(db):
    # 尝试删除不存在的用户
    response = client.delete("/api/users/9999")  # 更新路由路径
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
