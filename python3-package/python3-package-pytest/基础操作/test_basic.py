"""
pytest 基础测试示例
演示基本的断言、测试函数组织和常见测试场景
"""

import pytest


# ========== 被测试的代码 ==========

def add(a, b):
    """加法"""
    return a + b


def divide(a, b):
    """除法"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


def get_full_name(first_name, last_name):
    """拼接全名"""
    return f"{first_name} {last_name}"


def filter_even_numbers(numbers):
    """过滤偶数"""
    return [n for n in numbers if n % 2 == 0]


def find_item(items, target):
    """查找元素"""
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1


# ========== 测试代码 ==========

class TestBasicAssertions:
    """基本断言测试"""

    def test_addition(self):
        """测试加法"""
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0

    def test_subtraction(self):
        """测试减法"""
        assert add(5, -3) == 2

    def test_string_concatenation(self):
        """测试字符串拼接"""
        result = get_full_name("John", "Doe")
        assert result == "John Doe"
        assert isinstance(result, str)

    def test_list_operations(self):
        """测试列表操作"""
        numbers = [1, 2, 3, 4, 5, 6]
        even_numbers = filter_even_numbers(numbers)
        
        assert even_numbers == [2, 4, 6]
        assert len(even_numbers) == 3
        assert all(n % 2 == 0 for n in even_numbers)

    def test_dictionary_operations(self):
        """测试字典操作"""
        user = {"name": "Alice", "age": 30, "city": "Beijing"}
        
        assert user["name"] == "Alice"
        assert user["age"] == 30
        assert "city" in user
        assert len(user) == 3

    def test_boolean_assertions(self):
        """测试布尔断言"""
        assert True
        assert not False
        
        result = 5 > 3
        assert result is True

    def test_none_assertions(self):
        """测试 None 断言"""
        value = None
        assert value is None
        
        non_none = "hello"
        assert non_none is not None

    def test_in_and_not_in(self):
        """测试包含关系"""
        fruits = ["apple", "banana", "orange"]
        
        assert "apple" in fruits
        assert "grape" not in fruits

    def test_almost_equal(self):
        """测试浮点数近似相等"""
        result = 10 / 3
        assert result == pytest.approx(3.3333, rel=1e-4)

    def test_list_equality(self):
        """测试列表相等"""
        expected = [1, 2, 3]
        actual = [1, 2, 3]
        
        assert actual == expected
        assert actual is not expected  # 不同的对象

    def test_greater_less_than(self):
        """测试大小比较"""
        assert 10 > 5
        assert 5 < 10
        assert 10 >= 10
        assert 5 <= 5


class TestStringOperations:
    """字符串操作测试"""

    def test_uppercase(self):
        """测试大写转换"""
        text = "hello world"
        assert text.upper() == "HELLO WORLD"

    def test_lowercase(self):
        """测试小写转换"""
        text = "HELLO WORLD"
        assert text.lower() == "hello world"

    def test_strip(self):
        """测试去除空白"""
        text = "  hello  "
        assert text.strip() == "hello"

    def test_split(self):
        """测试分割字符串"""
        text = "apple,banana,orange"
        result = text.split(",")
        
        assert result == ["apple", "banana", "orange"]
        assert len(result) == 3

    def test_join(self):
        """测试连接字符串"""
        items = ["apple", "banana", "orange"]
        result = ", ".join(items)
        
        assert result == "apple, banana, orange"


class TestListOperations:
    """列表操作测试"""

    def test_append(self):
        """测试追加元素"""
        items = [1, 2, 3]
        items.append(4)
        
        assert items == [1, 2, 3, 4]
        assert len(items) == 4

    def test_extend(self):
        """测试扩展列表"""
        items = [1, 2]
        items.extend([3, 4])
        
        assert items == [1, 2, 3, 4]

    def test_slicing(self):
        """测试切片"""
        numbers = [0, 1, 2, 3, 4, 5]
        
        assert numbers[0:3] == [0, 1, 2]
        assert numbers[::2] == [0, 2, 4]
        assert numbers[::-1] == [5, 4, 3, 2, 1, 0]

    def test_comprehension(self):
        """测试列表推导式"""
        numbers = [1, 2, 3, 4, 5]
        squared = [n ** 2 for n in numbers]
        
        assert squared == [1, 4, 9, 16, 25]


class TestSearchFunctions:
    """搜索功能测试"""

    def test_find_existing_item(self):
        """测试查找存在的元素"""
        items = ["apple", "banana", "orange"]
        index = find_item(items, "banana")
        
        assert index == 1

    def test_find_non_existing_item(self):
        """测试查找不存在的元素"""
        items = ["apple", "banana", "orange"]
        index = find_item(items, "grape")
        
        assert index == -1

    def test_find_first_element(self):
        """测试查找第一个元素"""
        items = ["apple", "banana", "orange"]
        index = find_item(items, "apple")
        
        assert index == 0

    def test_find_last_element(self):
        """测试查找最后一个元素"""
        items = ["apple", "banana", "orange"]
        index = find_item(items, "orange")
        
        assert index == 2


if __name__ == "__main__":
    # 运行测试: pytest test_basic.py -v
    pass
