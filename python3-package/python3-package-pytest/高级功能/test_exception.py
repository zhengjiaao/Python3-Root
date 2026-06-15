"""
pytest 异常测试示例
演示如何测试代码中的异常情况
"""

import pytest


# ========== 被测试的代码 ==========

class Calculator:
    """计算器类"""
    
    def divide(self, a, b):
        """除法"""
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        return a / b
    
    def sqrt(self, n):
        """平方根"""
        if n < 0:
            raise ValueError("不能对负数求平方根")
        return n ** 0.5
    
    def get_item(self, items, index):
        """获取列表元素"""
        try:
            return items[index]
        except IndexError:
            raise IndexError(f"索引 {index} 超出范围")


class ValidationError(Exception):
    """验证错误"""
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class UserValidator:
    """用户验证器"""
    
    def validate_email(self, email):
        """验证邮箱"""
        if not email:
            raise ValidationError("email", "邮箱不能为空")
        if "@" not in email:
            raise ValidationError("email", "邮箱格式不正确")
        return True
    
    def validate_age(self, age):
        """验证年龄"""
        if not isinstance(age, int):
            raise ValidationError("age", "年龄必须是整数")
        if age < 0 or age > 150:
            raise ValidationError("age", "年龄必须在 0-150 之间")
        return True
    
    def validate_user(self, name, email, age):
        """验证用户信息"""
        errors = []
        
        if not name:
            errors.append(ValidationError("name", "姓名不能为空"))
        
        try:
            self.validate_email(email)
        except ValidationError as e:
            errors.append(e)
        
        try:
            self.validate_age(age)
        except ValidationError as e:
            errors.append(e)
        
        if errors:
            raise ExceptionGroup("验证失败", errors)
        
        return True


class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        self.resources = []
    
    def acquire(self, resource):
        """获取资源"""
        if not resource:
            raise ValueError("资源不能为空")
        self.resources.append(resource)
        return resource
    
    def release(self, resource):
        """释放资源"""
        if resource not in self.resources:
            raise ValueError("资源未被获取")
        self.resources.remove(resource)
    
    def release_all(self):
        """释放所有资源"""
        self.resources.clear()


# ========== 基础异常测试 ==========

class TestBasicExceptions:
    """基础异常测试"""
    
    def test_divide_by_zero(self):
        """测试除以零异常"""
        calc = Calculator()
        
        with pytest.raises(ZeroDivisionError):
            calc.divide(10, 0)
    
    def test_divide_by_zero_with_message(self):
        """测试异常消息"""
        calc = Calculator()
        
        with pytest.raises(ZeroDivisionError, match="除数不能为零"):
            calc.divide(10, 0)
    
    def test_sqrt_negative(self):
        """测试负数平方根异常"""
        calc = Calculator()
        
        with pytest.raises(ValueError, match="不能对负数求平方根"):
            calc.sqrt(-4)
    
    def test_normal_division(self):
        """测试正常除法（不应抛出异常）"""
        calc = Calculator()
        result = calc.divide(10, 2)
        assert result == 5.0
    
    def test_normal_sqrt(self):
        """测试正常平方根（不应抛出异常）"""
        calc = Calculator()
        result = calc.sqrt(16)
        assert result == 4.0


# ========== 异常信息验证 ==========

class TestExceptionInfo:
    """异常信息验证"""
    
    def test_exception_value(self):
        """测试异常值捕获"""
        calc = Calculator()
        
        with pytest.raises(ZeroDivisionError) as exc_info:
            calc.divide(10, 0)
        
        # 验证异常消息
        assert "除数不能为零" in str(exc_info.value)
    
    def test_exception_type(self):
        """测试异常类型"""
        calc = Calculator()
        
        with pytest.raises(ValueError) as exc_info:
            calc.sqrt(-9)
        
        # 验证异常类型
        assert exc_info.type is ValueError
    
    def test_exception_traceback(self):
        """测试异常堆栈跟踪"""
        calc = Calculator()
        
        with pytest.raises(ZeroDivisionError) as exc_info:
            calc.divide(10, 0)
        
        # 可以访问堆栈跟踪信息
        assert exc_info.traceback is not None


# ========== 自定义异常测试 ==========

class TestCustomExceptions:
    """自定义异常测试"""
    
    def test_validate_empty_email(self):
        """测试空邮箱验证"""
        validator = UserValidator()
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email("")
        
        assert exc_info.value.field == "email"
        assert "邮箱不能为空" in exc_info.value.message
    
    def test_validate_invalid_email(self):
        """测试无效邮箱验证"""
        validator = UserValidator()
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email("invalid-email")
        
        assert exc_info.value.field == "email"
        assert "邮箱格式不正确" in exc_info.value.message
    
    def test_validate_invalid_age_type(self):
        """测试年龄类型验证"""
        validator = UserValidator()
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_age("thirty")
        
        assert exc_info.value.field == "age"
        assert "年龄必须是整数" in exc_info.value.message
    
    def test_validate_age_out_of_range(self):
        """测试年龄范围验证"""
        validator = UserValidator()
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_age(200)
        
        assert exc_info.value.field == "age"
        assert "年龄必须在 0-150 之间" in exc_info.value.message
    
    def test_validate_valid_user(self):
        """测试有效用户验证（不应抛出异常）"""
        validator = UserValidator()
        
        # 不应抛出异常
        result = validator.validate_user("Alice", "alice@example.com", 30)
        assert result is True


# ========== 多个异常测试 ==========

class TestMultipleExceptions:
    """多个异常测试"""
    
    @pytest.mark.parametrize("a,b,expected_exception", [
        (10, 0, ZeroDivisionError),
        (-4, 1, None),  # 不期望异常
    ])
    def test_parametrized_exceptions(self, a, b, expected_exception):
        """参数化异常测试"""
        calc = Calculator()
        
        if expected_exception:
            with pytest.raises(expected_exception):
                calc.divide(a, b)
        else:
            # 不应抛出异常
            result = calc.divide(a, b)
            assert result == -4.0
    
    def test_index_error(self):
        """测试索引错误"""
        calc = Calculator()
        items = [1, 2, 3]
        
        with pytest.raises(IndexError, match="索引 10 超出范围"):
            calc.get_item(items, 10)
    
    def test_get_valid_item(self):
        """测试获取有效元素（不应抛出异常）"""
        calc = Calculator()
        items = [1, 2, 3]
        
        result = calc.get_item(items, 1)
        assert result == 2


# ========== 异常组测试（Python 3.11+）==========

class TestExceptionGroup:
    """异常组测试"""
    
    def test_validate_multiple_errors(self):
        """测试多个验证错误"""
        validator = UserValidator()
        
        # Python 3.11+ 支持 ExceptionGroup
        with pytest.raises(ExceptionGroup) as exc_info:
            validator.validate_user("", "invalid", -5)
        
        # 验证有多个错误
        assert len(exc_info.value.exceptions) >= 2
    
    def test_validate_no_errors(self):
        """测试无错误的情况"""
        validator = UserValidator()
        
        # 不应抛出异常
        result = validator.validate_user("Bob", "bob@example.com", 25)
        assert result is True


# ========== Fixture 中的异常测试 ==========

class TestFixtureExceptions:
    """Fixture 中的异常测试"""
    
    @pytest.fixture
    def resource_manager(self):
        """创建资源管理器"""
        manager = ResourceManager()
        yield manager
        # 清理：确保所有资源被释放
        manager.release_all()
    
    def test_acquire_resource(self, resource_manager):
        """测试获取资源"""
        resource = resource_manager.acquire("database_connection")
        assert resource == "database_connection"
    
    def test_release_resource(self, resource_manager):
        """测试释放资源"""
        resource_manager.acquire("database_connection")
        resource_manager.release("database_connection")
        
        assert len(resource_manager.resources) == 0
    
    def test_release_unacquired_resource(self, resource_manager):
        """测试释放未获取的资源"""
        with pytest.raises(ValueError, match="资源未被获取"):
            resource_manager.release("nonexistent")
    
    def test_acquire_empty_resource(self, resource_manager):
        """测试获取空资源"""
        with pytest.raises(ValueError, match="资源不能为空"):
            resource_manager.acquire("")


# ========== 警告测试 ==========

class TestWarnings:
    """警告测试"""
    
    def test_deprecation_warning(self):
        """测试弃用警告"""
        import warnings
        
        with pytest.warns(DeprecationWarning, match="此函数已弃用"):
            warnings.warn("此函数已弃用", DeprecationWarning)
    
    def test_no_warning(self):
        """测试没有警告"""
        # 正常执行，不抛出异常
        result = 1 + 1
        assert result == 2


# ========== 断言重写 ==========

class TestAssertRewrite:
    """pytest 断言重写示例"""
    
    def test_assert_with_message(self):
        """测试带消息的断言"""
        value = 5
        
        # pytest 会提供详细的失败信息
        assert value == 5, f"期望值为 5，实际为 {value}"
    
    def test_assert_in_collection(self):
        """测试集合包含"""
        items = [1, 2, 3, 4, 5]
        
        # pytest 会显示哪些元素在集合中
        assert 3 in items
        assert 10 not in items
    
    def test_assert_dict_subset(self):
        """测试字典子集"""
        user = {"name": "Alice", "age": 30, "city": "Beijing"}
        
        # 验证特定键值对
        assert user["name"] == "Alice"
        assert user["age"] == 30


if __name__ == "__main__":
    # 运行测试: pytest test_exception.py -v
    pass
