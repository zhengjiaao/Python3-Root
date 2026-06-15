"""
pytest 标记和分组示例
演示如何使用 mark 对测试进行分类和管理
"""

import pytest


# ========== 被测试的代码 ==========

def add(a, b):
    """加法"""
    return a + b


def multiply(a, b):
    """乘法"""
    return a * b


def is_even(n):
    """检查是否是偶数"""
    return n % 2 == 0


def fibonacci(n):
    """斐波那契数列"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


class DatabaseConnection:
    """数据库连接（模拟）"""
    
    def __init__(self):
        self.connected = False
    
    def connect(self):
        """连接数据库"""
        self.connected = True
        return True
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        return True


# ========== 内置标记 ==========

@pytest.mark.skip(reason="此功能尚未实现")
def test_unimplemented_feature():
    """跳过的测试"""
    assert False


@pytest.mark.skipif(True, reason="条件满足时跳过")
def test_skip_if_condition():
    """条件跳过"""
    assert True


@pytest.mark.xfail(reason="已知会失败的测试")
def test_expected_failure():
    """预期失败的测试"""
    assert False


@pytest.mark.xfail(reason="已知bug，但应该通过")
def test_xfail_should_pass():
    """预期失败但实际通过的测试"""
    assert True


# ========== 自定义标记 ==========

@pytest.mark.smoke
class TestSmokeTests:
    """冒烟测试 - 核心功能快速验证"""
    
    def test_basic_addition(self):
        """测试基本加法"""
        assert add(2, 3) == 5
    
    def test_basic_multiplication(self):
        """测试基本乘法"""
        assert multiply(2, 3) == 6
    
    def test_is_even_true(self):
        """测试偶数判断"""
        assert is_even(4) is True


@pytest.mark.regression
class TestRegressionTests:
    """回归测试 - 确保旧功能正常工作"""
    
    def test_addition_negative(self):
        """测试负数加法"""
        assert add(-1, -1) == -2
    
    def test_multiplication_zero(self):
        """测试乘以零"""
        assert multiply(100, 0) == 0
    
    def test_is_even_odd(self):
        """测试奇数判断"""
        assert is_even(3) is False


@pytest.mark.slow
class TestSlowTests:
    """慢速测试 - 耗时较长的测试"""
    
    def test_fibonacci_large(self):
        """测试大数斐波那契"""
        result = fibonacci(100)
        assert result == 354224848179261915075
    
    def test_fibonacci_sequence(self):
        """测试斐波那契数列"""
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        for i, exp in enumerate(expected):
            assert fibonacci(i) == exp


@pytest.mark.integration
class TestIntegrationTests:
    """集成测试 - 多个组件协同工作"""
    
    def test_database_connection_lifecycle(self):
        """测试数据库连接生命周期"""
        db = DatabaseConnection()
        
        # 初始状态
        assert db.connected is False
        
        # 连接
        db.connect()
        assert db.connected is True
        
        # 断开
        db.disconnect()
        assert db.connected is False


@pytest.mark.unit
class TestUnitTests:
    """单元测试 - 独立的功能单元"""
    
    def test_add_positive_numbers(self):
        """测试正数加法"""
        assert add(10, 20) == 30
    
    def test_multiply_by_one(self):
        """测试乘以1"""
        assert multiply(5, 1) == 5
    
    def test_is_even_zero(self):
        """测试零是否为偶数"""
        assert is_even(0) is True


# ========== 组合标记 ==========

@pytest.mark.smoke
@pytest.mark.unit
def test_combined_marks():
    """同时标记为冒烟测试和单元测试"""
    assert add(1, 1) == 2


@pytest.mark.regression
@pytest.mark.slow
def test_slow_regression():
    """慢速回归测试"""
    result = fibonacci(50)
    assert result == 12586269025


# ========== 参数化标记 ==========

class TestParametrizeWithMarks:
    """带标记的参数化测试"""
    
    @pytest.mark.parametrize("a,b,expected", [
        pytest.param(2, 3, 5, marks=pytest.mark.smoke),
        pytest.param(-1, 1, 0, marks=pytest.mark.regression),
        pytest.param(100, 200, 300, marks=pytest.mark.slow),
    ])
    def test_add_with_marks(self, a, b, expected):
        """不同参数的测试有不同标记"""
        assert add(a, b) == expected


# ========== 类级别标记 ==========

@pytest.mark.feature_auth
class TestAuthentication:
    """认证功能测试"""
    
    def test_login_success(self):
        """测试登录成功"""
        # 模拟登录逻辑
        username = "admin"
        password = "password123"
        
        # 验证
        assert username == "admin"
        assert len(password) >= 8
    
    def test_login_invalid_password(self):
        """测试无效密码"""
        password = "123"
        assert len(password) < 8


@pytest.mark.feature_api
class TestAPI:
    """API 功能测试"""
    
    def test_get_endpoint(self):
        """测试 GET 端点"""
        status_code = 200
        assert status_code == 200
    
    def test_post_endpoint(self):
        """测试 POST 端点"""
        status_code = 201
        assert status_code == 201


# ========== 标记优先级 ==========

@pytest.mark.high_priority
class TestHighPriority:
    """高优先级测试"""
    
    def test_critical_functionality(self):
        """测试关键功能"""
        assert add(1, 1) == 2


@pytest.mark.medium_priority
class TestMediumPriority:
    """中优先级测试"""
    
    def test_normal_functionality(self):
        """测试普通功能"""
        assert multiply(2, 2) == 4


@pytest.mark.low_priority
class TestLowPriority:
    """低优先级测试"""
    
    def test_nice_to_have(self):
        """测试锦上添花的功能"""
        assert is_even(100) is True


# ========== 使用 conftest 中的自定义标记 ==========

class TestCustomMarkers:
    """使用自定义标记的测试"""
    
    @pytest.mark.database
    def test_requires_database(self):
        """需要数据库的测试"""
        db = DatabaseConnection()
        db.connect()
        assert db.connected is True
        db.disconnect()
    
    @pytest.mark.network
    def test_requires_network(self):
        """需要网络的测试"""
        # 模拟网络请求
        response_status = 200
        assert response_status == 200
    
    @pytest.mark.security
    def test_security_check(self):
        """安全检查测试"""
        password = "SecureP@ss123"
        assert len(password) >= 12
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)


# ========== 动态标记 ==========

def get_test_markers():
    """动态获取测试标记"""
    import sys
    if sys.platform.startswith("win"):
        return pytest.mark.windows
    else:
        return pytest.mark.linux


@pytest.mark.windows
def test_windows_specific():
    """Windows 特定测试"""
    import platform
    if platform.system() == "Windows":
        assert True
    else:
        pytest.skip("仅在 Windows 上运行")


@pytest.mark.linux
def test_linux_specific():
    """Linux 特定测试"""
    import platform
    if platform.system() == "Linux":
        assert True
    else:
        pytest.skip("仅在 Linux 上运行")


# ========== 性能标记 ==========

@pytest.mark.performance
class TestPerformance:
    """性能测试"""
    
    def test_add_performance(self):
        """测试加法性能"""
        import time
        
        start = time.time()
        for _ in range(10000):
            add(1, 1)
        end = time.time()
        
        # 应该在合理时间内完成
        assert (end - start) < 1.0
    
    def test_fibonacci_performance(self):
        """测试斐波那契性能"""
        import time
        
        start = time.time()
        fibonacci(100)
        end = time.time()
        
        # 应该在合理时间内完成
        assert (end - start) < 1.0


# ========== 文档字符串标记 ==========

class TestDocumentation:
    """带文档的测试"""
    
    @pytest.mark.smoke
    def test_with_docstring(self):
        """
        测试用例：基本加法验证
        
        目的：验证加法函数的基本功能
        前置条件：无
        测试步骤：
            1. 调用 add(2, 3)
        预期结果：返回 5
        """
        assert add(2, 3) == 5


if __name__ == "__main__":
    # 运行所有测试: pytest test_mark.py -v
    # 只运行冒烟测试: pytest test_mark.py -v -m smoke
    # 只运行回归测试: pytest test_mark.py -v -m regression
    # 运行慢速测试: pytest test_mark.py -v -m slow
    # 排除慢速测试: pytest test_mark.py -v -m "not slow"
    # 运行多个标记: pytest test_mark.py -v -m "smoke or regression"
    pass
