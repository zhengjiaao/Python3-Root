"""
pytest Mock 和补丁示例
演示如何使用 mock 来隔离测试依赖
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import time


# ========== 被测试的代码 ==========

class UserService:
    """用户服务 - 依赖外部 API"""
    
    def __init__(self, api_url):
        self.api_url = api_url
    
    def get_user(self, user_id):
        """从 API 获取用户信息"""
        response = requests.get(f"{self.api_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    def create_user(self, name, email):
        """创建用户"""
        data = {"name": name, "email": email}
        response = requests.post(f"{self.api_url}/users", json=data)
        response.raise_for_status()
        return response.json()


class PaymentProcessor:
    """支付处理器 - 依赖第三方支付网关"""
    
    def __init__(self, gateway_url, api_key):
        self.gateway_url = gateway_url
        self.api_key = api_key
    
    def process_payment(self, amount, currency="USD"):
        """处理支付"""
        # 模拟调用外部支付网关
        response = requests.post(
            f"{self.gateway_url}/charge",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"amount": amount, "currency": currency}
        )
        response.raise_for_status()
        return response.json()


class DataAnalyzer:
    """数据分析器 - 依赖时间函数"""
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        return time.time()
    
    def calculate_age(self, birth_year):
        """计算年龄"""
        current_year = time.localtime().tm_year
        return current_year - birth_year
    
    def is_business_hours(self):
        """检查是否是工作时间（9-17点）"""
        current_hour = time.localtime().tm_hour
        return 9 <= current_hour < 17


class FileProcessor:
    """文件处理器 - 依赖文件系统"""
    
    def read_config(self, filepath):
        """读取配置文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_report(self, filepath, content):
        """写入报告"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


# ========== Mock 测试 ==========

class TestUserServiceMock:
    """用户服务 Mock 测试"""
    
    @patch('requests.get')
    def test_get_user_success(self, mock_get):
        """测试成功获取用户"""
        # 配置 mock 返回值
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com"
        }
        mock_get.return_value = mock_response
        
        # 执行测试
        service = UserService("https://api.example.com")
        user = service.get_user(1)
        
        # 验证结果
        assert user["name"] == "Alice"
        assert user["email"] == "alice@example.com"
        
        # 验证 mock 被正确调用
        mock_get.assert_called_once_with("https://api.example.com/users/1")
    
    @patch('requests.get')
    def test_get_user_not_found(self, mock_get):
        """测试用户不存在"""
        # 配置 mock 抛出异常
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        service = UserService("https://api.example.com")
        
        with pytest.raises(requests.exceptions.HTTPError):
            service.get_user(999)
    
    @patch('requests.post')
    def test_create_user(self, mock_post):
        """测试创建用户"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 2,
            "name": "Bob",
            "email": "bob@example.com"
        }
        mock_post.return_value = mock_response
        
        service = UserService("https://api.example.com")
        user = service.create_user("Bob", "bob@example.com")
        
        assert user["id"] == 2
        assert user["name"] == "Bob"
        
        # 验证 POST 请求的参数
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"] == {"name": "Bob", "email": "bob@example.com"}


class TestPaymentProcessorMock:
    """支付处理器 Mock 测试"""
    
    @patch('requests.post')
    def test_process_payment_success(self, mock_post):
        """测试支付成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transaction_id": "tx_123456",
            "status": "success",
            "amount": 100.00
        }
        mock_post.return_value = mock_response
        
        processor = PaymentProcessor("https://payment.gateway.com", "secret_key")
        result = processor.process_payment(100.00)
        
        assert result["status"] == "success"
        assert result["transaction_id"] == "tx_123456"
        
        # 验证授权头
        call_args = mock_post.call_args
        assert "Authorization" in call_args[1]["headers"]
    
    @patch('requests.post')
    def test_process_payment_failure(self, mock_post):
        """测试支付失败"""
        mock_response = Mock()
        mock_response.status_code = 402  # Payment Required
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response
        
        processor = PaymentProcessor("https://payment.gateway.com", "secret_key")
        
        with pytest.raises(requests.exceptions.HTTPError):
            processor.process_payment(100.00)


class TestDataAnalyzerMock:
    """数据分析器 Mock 测试"""
    
    def test_calculate_age_with_mock_time(self):
        """使用 patch 模拟时间"""
        analyzer = DataAnalyzer()
        
        # Mock time.localtime 返回特定年份
        with patch('time.localtime') as mock_localtime:
            mock_localtime.return_value.tm_year = 2026
            
            age = analyzer.calculate_age(1990)
            assert age == 36
    
    @patch('time.time')
    def test_get_timestamp_mocked(self, mock_time):
        """测试获取时间戳"""
        mock_time.return_value = 1234567890.0
        
        analyzer = DataAnalyzer()
        timestamp = analyzer.get_current_timestamp()
        
        assert timestamp == 1234567890.0
        mock_time.assert_called_once()
    
    @patch('time.localtime')
    def test_is_business_hours_during_workday(self, mock_localtime):
        """测试工作时间检测 - 工作时间内"""
        mock_time = Mock()
        mock_time.tm_hour = 14  # 下午2点
        mock_localtime.return_value = mock_time
        
        analyzer = DataAnalyzer()
        assert analyzer.is_business_hours() is True
    
    @patch('time.localtime')
    def test_is_business_hours_outside_workday(self, mock_localtime):
        """测试工作时间检测 - 非工作时间"""
        mock_time = Mock()
        mock_time.tm_hour = 20  # 晚上8点
        mock_localtime.return_value = mock_time
        
        analyzer = DataAnalyzer()
        assert analyzer.is_business_hours() is False


class TestFileProcessorMock:
    """文件处理器 Mock 测试"""
    
    @patch('builtins.open')
    def test_read_config(self, mock_open):
        """测试读取配置文件"""
        # 配置 mock 文件对象
        mock_file = MagicMock()
        mock_file.read.return_value = "config_value=123"
        mock_open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_open.return_value.__exit__ = Mock(return_value=False)
        
        processor = FileProcessor()
        content = processor.read_config("config.txt")
        
        assert content == "config_value=123"
        mock_open.assert_called_once_with("config.txt", 'r', encoding='utf-8')
    
    @patch('builtins.open')
    def test_write_report(self, mock_open):
        """测试写入报告"""
        mock_file = Mock()
        mock_open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_open.return_value.__exit__ = Mock(return_value=False)
        
        processor = FileProcessor()
        processor.write_report("report.txt", "Report content")
        
        mock_file.write.assert_called_once_with("Report content")


# ========== MagicMock 示例 ==========

class TestMagicMock:
    """MagicMock 使用示例"""
    
    def test_magicmock_basic(self):
        """测试 MagicMock 基本用法"""
        mock = MagicMock()
        
        # 设置返回值
        mock.some_method.return_value = "result"
        assert mock.some_method() == "result"
        
        # 设置属性
        mock.name = "test"
        assert mock.name == "test"
        
        # 验证调用
        mock.some_method.assert_called_once()
    
    def test_magicmock_side_effect(self):
        """测试 side_effect"""
        mock = MagicMock()
        
        # 每次调用返回不同值
        mock.side_effect = [1, 2, 3]
        assert mock() == 1
        assert mock() == 2
        assert mock() == 3
        
        # 使用函数作为 side_effect
        def custom_side_effect(x):
            return x * 2
        
        mock.side_effect = custom_side_effect
        assert mock(5) == 10
    
    def test_magicmock_exception(self):
        """测试模拟异常"""
        mock = MagicMock()
        mock.side_effect = ValueError("Invalid value")
        
        with pytest.raises(ValueError, match="Invalid value"):
            mock()


# ========== Context Manager Mock ==========

class TestContextManagerMock:
    """上下文管理器 Mock 测试"""
    
    def test_mock_context_manager(self):
        """测试模拟上下文管理器"""
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = "resource"
        mock_cm.__exit__.return_value = None
        
        with mock_cm as resource:
            assert resource == "resource"
        
        mock_cm.__enter__.assert_called_once()
        mock_cm.__exit__.assert_called_once()


if __name__ == "__main__":
    # 运行测试: pytest test_mock.py -v
    pass
