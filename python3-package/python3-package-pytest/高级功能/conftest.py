"""
conftest.py - 共享 fixture 配置
在测试目录中自动被 pytest 发现和使用
"""

import pytest
import tempfile
import os


# ========== 全局 Fixture ==========

@pytest.fixture(scope="session")
def global_config():
    """会话级别的配置 fixture"""
    config = {
        "database_url": "sqlite:///:memory:",
        "api_base_url": "https://api.example.com",
        "timeout": 30,
        "retry_count": 3,
    }
    return config


@pytest.fixture
def sample_user():
    """样本用户数据"""
    return {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
    }


@pytest.fixture
def sample_users():
    """多个样本用户"""
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
    ]


@pytest.fixture
def temp_file():
    """临时文件 fixture"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("test content")
        temp_path = f.name
    
    yield temp_path
    
    # 清理
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def temp_directory():
    """临时目录 fixture"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # 清理
    import shutil
    shutil.rmtree(temp_dir)


# ========== 数据库 Fixture ==========

class MockDatabase:
    """模拟数据库"""
    
    def __init__(self):
        self.data = {}
        self.connected = False
    
    def connect(self):
        self.connected = True
    
    def disconnect(self):
        self.connected = False
    
    def insert(self, table, record):
        if table not in self.data:
            self.data[table] = []
        self.data[table].append(record)
    
    def query(self, table):
        return self.data.get(table, [])
    
    def clear(self):
        self.data.clear()


@pytest.fixture
def mock_db():
    """模拟数据库 fixture"""
    db = MockDatabase()
    db.connect()
    yield db
    db.disconnect()
    db.clear()


# ========== API Fixture ==========

class MockAPIClient:
    """模拟 API 客户端"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.responses = {}
    
    def get(self, endpoint):
        return self.responses.get(endpoint, {"status": 404})
    
    def post(self, endpoint, data):
        return {"status": 201, "data": data}
    
    def set_mock_response(self, endpoint, response):
        self.responses[endpoint] = response


@pytest.fixture
def api_client():
    """API 客户端 fixture"""
    client = MockAPIClient("https://api.example.com")
    return client


# ========== 自定义标记注册 ==========

def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line(
        "markers",
        "smoke: 冒烟测试 - 核心功能快速验证"
    )
    config.addinivalue_line(
        "markers",
        "regression: 回归测试 - 确保旧功能正常工作"
    )
    config.addinivalue_line(
        "markers",
        "slow: 慢速测试 - 耗时较长的测试"
    )
    config.addinivalue_line(
        "markers",
        "integration: 集成测试 - 多个组件协同工作"
    )
    config.addinivalue_line(
        "markers",
        "unit: 单元测试 - 独立的功能单元"
    )
    config.addinivalue_line(
        "markers",
        "database: 需要数据库的测试"
    )
    config.addinivalue_line(
        "markers",
        "network: 需要网络的测试"
    )
    config.addinivalue_line(
        "markers",
        "security: 安全检查测试"
    )
    config.addinivalue_line(
        "markers",
        "performance: 性能测试"
    )
    config.addinivalue_line(
        "markers",
        "windows: Windows 平台特定测试"
    )
    config.addinivalue_line(
        "markers",
        "linux: Linux 平台特定测试"
    )


# ========== Hook 函数 ==========

def pytest_runtest_setup(item):
    """测试设置钩子"""
    # 在每个测试运行前执行
    if item.get_closest_marker("slow"):
        print(f"\n[SETUP] 运行慢速测试: {item.name}")


def pytest_runtest_teardown(item, nextitem):
    """测试清理钩子"""
    # 在每个测试运行后执行
    if item.get_closest_marker("slow"):
        print(f"[TEARDOWN] 完成慢速测试: {item.name}")


# ========== 辅助函数 ==========

def create_test_data(size=10):
    """创建测试数据的辅助函数"""
    return [{"id": i, "value": f"value_{i}"} for i in range(size)]


def assert_response_success(response):
    """断言响应成功的辅助函数"""
    assert response.get("status") == 200 or response.get("status") == 201


def assert_response_error(response):
    """断言响应错误的辅助函数"""
    assert response.get("status") >= 400
