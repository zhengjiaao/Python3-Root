"""
pytest 数据库测试示例
演示如何测试数据库操作，包括 CRUD、事务和连接管理
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


# ========== 被测试的代码 ==========

class DatabaseConnection:
    """数据库连接管理器"""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
        self.is_connected = False
    
    def connect(self):
        """建立数据库连接"""
        # 实际实现会连接到真实数据库
        self.is_connected = True
        self.connection = Mock()
        return self.connection
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
        self.is_connected = False
        self.connection = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class UserRepository:
    """用户数据访问层"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_table(self):
        """创建用户表"""
        cursor = self.db.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.connection.commit()
    
    def insert_user(self, name, email, age=None):
        """插入用户"""
        cursor = self.db.connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            (name, email, age)
        )
        self.db.connection.commit()
        return cursor.lastrowid
    
    def get_user_by_id(self, user_id):
        """通过ID获取用户"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
    
    def get_user_by_email(self, email):
        """通过邮箱获取用户"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cursor.fetchone()
    
    def update_user(self, user_id, **kwargs):
        """更新用户"""
        if not kwargs:
            return False
        
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        cursor = self.db.connection.cursor()
        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        self.db.connection.commit()
        return cursor.rowcount > 0
    
    def delete_user(self, user_id):
        """删除用户"""
        cursor = self.db.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.db.connection.commit()
        return cursor.rowcount > 0
    
    def get_all_users(self):
        """获取所有用户"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    
    def count_users(self):
        """统计用户数量"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]


class TransactionManager:
    """事务管理器"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def execute_transaction(self, operations):
        """执行事务"""
        try:
            for operation in operations:
                operation()
            self.db.connection.commit()
            return True
        except Exception as e:
            self.db.connection.rollback()
            raise e
    
    def transfer_funds(self, from_account, to_account, amount):
        """转账操作（事务示例）"""
        cursor = self.db.connection.cursor()
        
        # 扣款
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, from_account)
        )
        
        # 检查余额是否足够
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (from_account,))
        balance = cursor.fetchone()
        if balance[0] < 0:
            raise ValueError("余额不足")
        
        # 收款
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, to_account)
        )
        
        self.db.connection.commit()


# ========== 数据库连接测试 ==========

class TestDatabaseConnection:
    """数据库连接测试"""
    
    def test_connect(self):
        """测试连接数据库"""
        db = DatabaseConnection("sqlite:///:memory:")
        db.connect()
        
        assert db.is_connected is True
        assert db.connection is not None
    
    def test_disconnect(self):
        """测试断开连接"""
        db = DatabaseConnection("sqlite:///:memory:")
        db.connect()
        db.disconnect()
        
        assert db.is_connected is False
        assert db.connection is None
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with DatabaseConnection("sqlite:///:memory:") as db:
            assert db.is_connected is True
        
        assert db.is_connected is False


# ========== 用户仓库测试 ==========

class TestUserRepository:
    """用户仓库测试"""
    
    @pytest.fixture
    def db_connection(self):
        """创建模拟数据库连接"""
        db = DatabaseConnection("sqlite:///:memory:")
        db.connect()
        return db
    
    @pytest.fixture
    def user_repo(self, db_connection):
        """创建用户仓库"""
        return UserRepository(db_connection)
    
    def test_create_table(self, user_repo):
        """测试创建表"""
        # 不应该抛出异常
        user_repo.create_table()
        
        # 验证 execute 被调用
        user_repo.db.connection.cursor.return_value.execute.assert_called()
    
    def test_insert_user(self, user_repo):
        """测试插入用户"""
        user_repo.db.connection.cursor.return_value.lastrowid = 1
        
        user_id = user_repo.insert_user("Alice", "alice@example.com", 30)
        
        assert user_id == 1
        user_repo.db.connection.commit.assert_called()
    
    def test_get_user_by_id(self, user_repo):
        """测试通过ID获取用户"""
        expected_user = (1, "Alice", "alice@example.com", 30)
        user_repo.db.connection.cursor.return_value.fetchone.return_value = expected_user
        
        user = user_repo.get_user_by_id(1)
        
        assert user == expected_user
        assert user[1] == "Alice"
    
    def test_get_user_by_email(self, user_repo):
        """测试通过邮箱获取用户"""
        expected_user = (1, "Alice", "alice@example.com", 30)
        user_repo.db.connection.cursor.return_value.fetchone.return_value = expected_user
        
        user = user_repo.get_user_by_email("alice@example.com")
        
        assert user is not None
        assert user[2] == "alice@example.com"
    
    def test_update_user(self, user_repo):
        """测试更新用户"""
        user_repo.db.connection.cursor.return_value.rowcount = 1
        
        result = user_repo.update_user(1, name="Alice Updated", age=31)
        
        assert result is True
        user_repo.db.connection.commit.assert_called()
    
    def test_update_user_no_changes(self, user_repo):
        """测试更新用户 - 无变化"""
        user_repo.db.connection.cursor.return_value.rowcount = 0
        
        result = user_repo.update_user(999, name="NonExistent")
        
        assert result is False
    
    def test_delete_user(self, user_repo):
        """测试删除用户"""
        user_repo.db.connection.cursor.return_value.rowcount = 1
        
        result = user_repo.delete_user(1)
        
        assert result is True
        user_repo.db.connection.commit.assert_called()
    
    def test_delete_nonexistent_user(self, user_repo):
        """测试删除不存在的用户"""
        user_repo.db.connection.cursor.return_value.rowcount = 0
        
        result = user_repo.delete_user(999)
        
        assert result is False
    
    def test_get_all_users(self, user_repo):
        """测试获取所有用户"""
        expected_users = [
            (1, "Alice", "alice@example.com", 30),
            (2, "Bob", "bob@example.com", 25),
        ]
        user_repo.db.connection.cursor.return_value.fetchall.return_value = expected_users
        
        users = user_repo.get_all_users()
        
        assert len(users) == 2
        assert users[0][1] == "Alice"
    
    def test_count_users(self, user_repo):
        """测试统计用户数量"""
        user_repo.db.connection.cursor.return_value.fetchone.return_value = (5,)
        
        count = user_repo.count_users()
        
        assert count == 5


# ========== 事务管理测试 ==========

class TestTransactionManager:
    """事务管理测试"""
    
    @pytest.fixture
    def db_connection(self):
        """创建模拟数据库连接"""
        db = DatabaseConnection("sqlite:///:memory:")
        db.connect()
        return db
    
    @pytest.fixture
    def transaction_manager(self, db_connection):
        """创建事务管理器"""
        return TransactionManager(db_connection)
    
    def test_execute_transaction_success(self, transaction_manager):
        """测试成功执行事务"""
        operations = [
            Mock(),
            Mock(),
        ]
        
        result = transaction_manager.execute_transaction(operations)
        
        assert result is True
        transaction_manager.db.connection.commit.assert_called()
    
    def test_execute_transaction_rollback(self, transaction_manager):
        """测试事务回滚"""
        def failing_operation():
            raise Exception("操作失败")
        
        operations = [Mock(), failing_operation, Mock()]
        
        with pytest.raises(Exception, match="操作失败"):
            transaction_manager.execute_transaction(operations)
        
        # 验证已回滚
        transaction_manager.db.connection.rollback.assert_called()
        # 验证未提交
        transaction_manager.db.connection.commit.assert_not_called()
    
    def test_transfer_funds_success(self, transaction_manager):
        """测试成功转账"""
        # 模拟查询返回足够的余额
        transaction_manager.db.connection.cursor.return_value.fetchone.return_value = (500,)
        
        transaction_manager.transfer_funds(1, 2, 100)
        
        # 验证提交
        transaction_manager.db.connection.commit.assert_called()
    
    def test_transfer_funds_insufficient_balance(self, transaction_manager):
        """测试余额不足的转账"""
        # 模拟查询返回不足的余额（负数）
        cursor_mock = Mock()
        cursor_mock.fetchone.return_value = (-50,)  # 扣款后余额为负
        transaction_manager.db.connection.cursor.return_value = cursor_mock
        
        with pytest.raises(ValueError, match="余额不足"):
            transaction_manager.transfer_funds(1, 2, 100)


# ========== 集成测试示例 ==========

class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_full_user_crud(self):
        """测试完整的用户 CRUD 操作"""
        # 使用真实数据库进行集成测试
        import sqlite3
        
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER
            )
        """)
        conn.commit()
        
        # 插入
        cursor.execute(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            ("Alice", "alice@example.com", 30)
        )
        conn.commit()
        user_id = cursor.lastrowid
        assert user_id == 1
        
        # 查询
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        assert user[1] == "Alice"
        assert user[2] == "alice@example.com"
        
        # 更新
        cursor.execute(
            "UPDATE users SET age = ? WHERE id = ?",
            (31, user_id)
        )
        conn.commit()
        
        cursor.execute("SELECT age FROM users WHERE id = ?", (user_id,))
        updated_age = cursor.fetchone()[0]
        assert updated_age == 31
        
        # 删除
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        assert count == 0
        
        conn.close()


# ========== 性能测试 ==========

class TestDatabasePerformance:
    """数据库性能测试"""
    
    @pytest.mark.performance
    def test_bulk_insert_performance(self):
        """测试批量插入性能"""
        import sqlite3
        import time
        
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT
            )
        """)
        conn.commit()
        
        start = time.time()
        
        # 批量插入 1000 条记录
        for i in range(1000):
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (f"User {i}", f"user{i}@example.com")
            )
        conn.commit()
        
        end = time.time()
        elapsed = end - start
        
        assert elapsed < 5.0, f"批量插入耗时 {elapsed:.4f}秒，超过预期"
        
        # 验证插入数量
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        assert count == 1000
        
        conn.close()


if __name__ == "__main__":
    # 运行测试: pytest test_database.py -v
    pass
