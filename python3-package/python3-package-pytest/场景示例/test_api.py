"""
pytest API 测试示例
演示如何测试 RESTful API 端点
"""

import pytest
from unittest.mock import Mock, patch
import requests


# ========== 被测试的代码 ==========

class APIClient:
    """API 客户端"""
    
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def get_users(self):
        """获取所有用户"""
        response = self.session.get(f"{self.base_url}/users")
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id):
        """获取单个用户"""
        response = self.session.get(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    def create_user(self, name, email):
        """创建用户"""
        data = {"name": name, "email": email}
        response = self.session.post(f"{self.base_url}/users", json=data)
        response.raise_for_status()
        return response.json()
    
    def update_user(self, user_id, **kwargs):
        """更新用户"""
        response = self.session.put(
            f"{self.base_url}/users/{user_id}",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def delete_user(self, user_id):
        """删除用户"""
        response = self.session.delete(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.status_code == 204


class UserService:
    """用户服务 - 业务逻辑层"""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def get_active_users(self):
        """获取活跃用户"""
        users = self.api_client.get_users()
        return [u for u in users if u.get("active", False)]
    
    def find_user_by_email(self, email):
        """通过邮箱查找用户"""
        users = self.api_client.get_users()
        for user in users:
            if user.get("email") == email:
                return user
        return None
    
    def create_validated_user(self, name, email):
        """创建经过验证的用户"""
        # 验证输入
        if not name or len(name) < 2:
            raise ValueError("姓名至少需要2个字符")
        
        if not email or "@" not in email:
            raise ValueError("邮箱格式不正确")
        
        return self.api_client.create_user(name, email)


# ========== API 客户端测试 ==========

class TestAPIClient:
    """API 客户端测试"""
    
    @patch('requests.Session.get')
    def test_get_users_success(self, mock_get):
        """测试成功获取用户列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
        mock_get.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        users = client.get_users()
        
        assert len(users) == 2
        assert users[0]["name"] == "Alice"
        mock_get.assert_called_once_with("https://api.example.com/users")
    
    @patch('requests.Session.get')
    def test_get_user_by_id(self, mock_get):
        """测试通过ID获取用户"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30
        }
        mock_get.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        user = client.get_user(1)
        
        assert user["id"] == 1
        assert user["name"] == "Alice"
        mock_get.assert_called_once_with("https://api.example.com/users/1")
    
    @patch('requests.Session.post')
    def test_create_user(self, mock_post):
        """测试创建用户"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 3,
            "name": "Charlie",
            "email": "charlie@example.com"
        }
        mock_post.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        user = client.create_user("Charlie", "charlie@example.com")
        
        assert user["id"] == 3
        assert user["name"] == "Charlie"
        
        # 验证请求数据
        call_args = mock_post.call_args
        assert call_args[1]["json"] == {
            "name": "Charlie",
            "email": "charlie@example.com"
        }
    
    @patch('requests.Session.put')
    def test_update_user(self, mock_put):
        """测试更新用户"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "name": "Alice Updated",
            "email": "alice@example.com"
        }
        mock_put.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        user = client.update_user(1, name="Alice Updated")
        
        assert user["name"] == "Alice Updated"
    
    @patch('requests.Session.delete')
    def test_delete_user(self, mock_delete):
        """测试删除用户"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        result = client.delete_user(1)
        
        assert result is True
    
    @patch('requests.Session.get')
    def test_api_error_handling(self, mock_get):
        """测试 API 错误处理"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_user(999)


# ========== 用户服务测试 ==========

class TestUserService:
    """用户服务测试"""
    
    @pytest.fixture
    def api_client(self):
        """创建模拟的 API 客户端"""
        client = Mock()
        return client
    
    @pytest.fixture
    def user_service(self, api_client):
        """创建用户服务"""
        return UserService(api_client)
    
    def test_get_active_users(self, user_service, api_client):
        """测试获取活跃用户"""
        # 设置 mock 返回值
        api_client.get_users.return_value = [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False},
            {"id": 3, "name": "Charlie", "active": True},
        ]
        
        active_users = user_service.get_active_users()
        
        assert len(active_users) == 2
        assert all(u["active"] for u in active_users)
    
    def test_find_user_by_email_found(self, user_service, api_client):
        """测试通过邮箱找到用户"""
        api_client.get_users.return_value = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
        
        user = user_service.find_user_by_email("bob@example.com")
        
        assert user is not None
        assert user["name"] == "Bob"
    
    def test_find_user_by_email_not_found(self, user_service, api_client):
        """测试通过邮箱未找到用户"""
        api_client.get_users.return_value = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
        ]
        
        user = user_service.find_user_by_email("nonexistent@example.com")
        
        assert user is None
    
    def test_create_validated_user_success(self, user_service, api_client):
        """测试成功创建验证用户"""
        api_client.create_user.return_value = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com"
        }
        
        user = user_service.create_validated_user("Alice", "alice@example.com")
        
        assert user["name"] == "Alice"
        api_client.create_user.assert_called_once()
    
    def test_create_validated_user_invalid_name(self, user_service):
        """测试创建用户 - 无效姓名"""
        with pytest.raises(ValueError, match="姓名至少需要2个字符"):
            user_service.create_validated_user("A", "test@example.com")
    
    def test_create_validated_user_invalid_email(self, user_service):
        """测试创建用户 - 无效邮箱"""
        with pytest.raises(ValueError, match="邮箱格式不正确"):
            user_service.create_validated_user("Alice", "invalid-email")


# ========== 集成测试示例 ==========

class TestAPIIntegration:
    """API 集成测试示例"""
    
    @pytest.mark.integration
    @patch('requests.Session.get')
    @patch('requests.Session.post')
    def test_full_user_lifecycle(self, mock_post, mock_get):
        """测试完整的用户生命周期"""
        # 1. 创建用户
        mock_post_response = Mock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com"
        }
        mock_post.return_value = mock_post_response
        
        # 2. 获取用户
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com"
        }
        mock_get.return_value = mock_get_response
        
        client = APIClient("https://api.example.com")
        
        # 创建
        created_user = client.create_user("Test User", "test@example.com")
        assert created_user["name"] == "Test User"
        
        # 获取
        fetched_user = client.get_user(1)
        assert fetched_user["email"] == "test@example.com"


# ========== 认证测试 ==========

class TestAuthentication:
    """认证相关测试"""
    
    def test_api_client_with_auth(self):
        """测试带认证的 API 客户端"""
        client = APIClient(
            "https://api.example.com",
            api_key="secret_token_123"
        )
        
        # 验证认证头已设置
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer secret_token_123"
    
    def test_api_client_without_auth(self):
        """测试不带认证的 API 客户端"""
        client = APIClient("https://api.example.com")
        
        # 验证没有认证头
        assert "Authorization" not in client.session.headers


# ========== 性能测试 ==========

class TestAPIPerformance:
    """API 性能测试"""
    
    @pytest.mark.performance
    @patch('requests.Session.get')
    def test_get_users_performance(self, mock_get):
        """测试获取用户的性能"""
        import time
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": i, "name": f"User {i}"} for i in range(100)
        ]
        mock_get.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        
        start = time.time()
        for _ in range(10):
            client.get_users()
        end = time.time()
        
        elapsed = end - start
        assert elapsed < 1.0, f"API 调用耗时 {elapsed:.4f}秒，超过预期"


if __name__ == "__main__":
    # 运行测试: pytest test_api.py -v
    pass
