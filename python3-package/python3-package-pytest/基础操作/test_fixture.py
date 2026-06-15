"""
pytest Fixture 使用示例
演示 fixture 的各种用法：基本fixture、作用域、参数化、setup/teardown
"""

import pytest
import tempfile
import os


# ========== 被测试的代码 ==========

class Database:
    """模拟数据库类"""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connected = False
        self.data = {}
    
    def connect(self):
        """连接数据库"""
        self.connected = True
        return True
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        return True
    
    def insert(self, key, value):
        """插入数据"""
        if not self.connected:
            raise Exception("未连接到数据库")
        self.data[key] = value
    
    def get(self, key):
        """获取数据"""
        if not self.connected:
            raise Exception("未连接到数据库")
        return self.data.get(key)
    
    def delete(self, key):
        """删除数据"""
        if not self.connected:
            raise Exception("未连接到数据库")
        if key in self.data:
            del self.data[key]
            return True
        return False


class FileManager:
    """文件管理器"""
    
    def __init__(self, directory):
        self.directory = directory
    
    def create_file(self, filename, content):
        """创建文件"""
        filepath = os.path.join(self.directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    
    def read_file(self, filename):
        """读取文件"""
        filepath = os.path.join(self.directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def delete_file(self, filename):
        """删除文件"""
        filepath = os.path.join(self.directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False


# ========== Fixture 示例 ==========

@pytest.fixture
def db_connection():
    """基本 fixture：创建数据库连接"""
    db = Database("sqlite:///:memory:")
    db.connect()
    yield db  # yield 之前的代码是 setup，之后的是 teardown
    db.disconnect()


@pytest.fixture(scope="module")
def temp_directory():
    """模块级别的 fixture：创建临时目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理：删除临时目录及其内容
    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def file_manager(temp_directory):
    """依赖其他 fixture：创建文件管理器"""
    return FileManager(temp_directory)


@pytest.fixture(params=["small", "medium", "large"])
def dataset_size(request):
    """参数化 fixture"""
    sizes = {
        "small": 10,
        "medium": 100,
        "large": 1000
    }
    return sizes[request.param]


@pytest.fixture
def sample_data(dataset_size):
    """使用参数化 fixture 生成样本数据"""
    return list(range(dataset_size))


# ========== 测试代码 ==========

class TestDatabaseFixture:
    """数据库 fixture 测试"""
    
    def test_database_connection(self, db_connection):
        """测试数据库连接"""
        assert db_connection.connected is True
    
    def test_database_insert(self, db_connection):
        """测试插入数据"""
        db_connection.insert("user1", {"name": "Alice", "age": 30})
        assert db_connection.get("user1") == {"name": "Alice", "age": 30}
    
    def test_database_multiple_inserts(self, db_connection):
        """测试多次插入"""
        db_connection.insert("key1", "value1")
        db_connection.insert("key2", "value2")
        db_connection.insert("key3", "value3")
        
        assert db_connection.get("key1") == "value1"
        assert db_connection.get("key2") == "value2"
        assert db_connection.get("key3") == "value3"
    
    def test_database_delete(self, db_connection):
        """测试删除数据"""
        db_connection.insert("key1", "value1")
        result = db_connection.delete("key1")
        
        assert result is True
        assert db_connection.get("key1") is None
    
    def test_database_delete_nonexistent(self, db_connection):
        """测试删除不存在的数据"""
        result = db_connection.delete("nonexistent")
        assert result is False


class TestFileManagerFixture:
    """文件管理器 fixture 测试"""
    
    def test_create_and_read_file(self, file_manager):
        """测试创建和读取文件"""
        file_manager.create_file("test.txt", "Hello, World!")
        content = file_manager.read_file("test.txt")
        
        assert content == "Hello, World!"
    
    def test_create_multiple_files(self, file_manager):
        """测试创建多个文件"""
        file_manager.create_file("file1.txt", "Content 1")
        file_manager.create_file("file2.txt", "Content 2")
        file_manager.create_file("file3.txt", "Content 3")
        
        assert file_manager.read_file("file1.txt") == "Content 1"
        assert file_manager.read_file("file2.txt") == "Content 2"
        assert file_manager.read_file("file3.txt") == "Content 3"
    
    def test_delete_file(self, file_manager):
        """测试删除文件"""
        file_manager.create_file("to_delete.txt", "Some content")
        result = file_manager.delete_file("to_delete.txt")
        
        assert result is True
        
        # 验证文件已被删除
        import os
        assert not os.path.exists(
            os.path.join(file_manager.directory, "to_delete.txt")
        )
    
    def test_delete_nonexistent_file(self, file_manager):
        """测试删除不存在的文件"""
        result = file_manager.delete_file("nonexistent.txt")
        assert result is False


class TestParameterizedFixture:
    """参数化 fixture 测试"""
    
    def test_dataset_small(self, sample_data, dataset_size):
        """测试小数据集"""
        if dataset_size == 10:
            assert len(sample_data) == 10
            assert sample_data == list(range(10))
    
    def test_dataset_medium(self, sample_data, dataset_size):
        """测试中等数据集"""
        if dataset_size == 100:
            assert len(sample_data) == 100
    
    def test_dataset_large(self, sample_data, dataset_size):
        """测试大数据集"""
        if dataset_size == 1000:
            assert len(sample_data) == 1000


class TestFixtureSetupTeardown:
    """测试 fixture 的 setup 和 teardown"""
    
    def test_fixture_lifecycle(self, db_connection):
        """验证 fixture 的生命周期"""
        # Setup 已经完成（db 已连接）
        assert db_connection.connected is True
        
        # 执行测试操作
        db_connection.insert("test_key", "test_value")
        assert db_connection.get("test_key") == "test_value"
        
        # Teardown 将在测试结束后自动执行（断开连接）


# ========== 高级 Fixture 用法 ==========

@pytest.fixture
def mock_users():
    """提供模拟用户数据"""
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
    ]


@pytest.fixture
def user_lookup(mock_users):
    """基于用户列表创建查找字典"""
    return {user["id"]: user for user in mock_users}


class TestAdvancedFixtures:
    """高级 fixture 测试"""
    
    def test_user_lookup(self, user_lookup):
        """测试用户查找"""
        assert user_lookup[1]["name"] == "Alice"
        assert user_lookup[2]["name"] == "Bob"
        assert user_lookup[3]["name"] == "Charlie"
    
    def test_user_count(self, mock_users):
        """测试用户数量"""
        assert len(mock_users) == 3
    
    def test_user_emails(self, mock_users):
        """测试用户邮箱"""
        emails = [user["email"] for user in mock_users]
        assert "alice@example.com" in emails
        assert "bob@example.com" in emails


if __name__ == "__main__":
    # 运行测试: pytest test_fixture.py -v
    pass
