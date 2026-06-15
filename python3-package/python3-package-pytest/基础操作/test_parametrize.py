"""
pytest 参数化测试示例
演示如何使用 parametrize 进行数据驱动测试
"""

import pytest


# ========== 被测试的代码 ==========

def multiply(a, b):
    """乘法"""
    return a * b


def is_palindrome(text):
    """检查是否是回文"""
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


def classify_number(n):
    """分类数字"""
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"


def get_grade(score):
    """根据分数获取等级"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def flatten_list(nested_list):
    """扁平化嵌套列表"""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


# ========== 基础参数化测试 ==========

class TestBasicParametrize:
    """基础参数化测试"""

    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 6),
        (-1, 5, -5),
        (0, 100, 0),
        (1, 1, 1),
        (10, 10, 100),
    ])
    def test_multiply(self, a, b, expected):
        """测试乘法 - 多组数据"""
        assert multiply(a, b) == expected

    @pytest.mark.parametrize("text,expected", [
        ("madam", True),
        ("racecar", True),
        ("hello", False),
        ("A man a plan a canal Panama", True),
        ("", True),
        ("a", True),
    ])
    def test_is_palindrome(self, text, expected):
        """测试回文检测"""
        assert is_palindrome(text) == expected

    @pytest.mark.parametrize("number,expected_type", [
        (-5, "negative"),
        (-1, "negative"),
        (0, "zero"),
        (1, "positive"),
        (100, "positive"),
    ])
    def test_classify_number(self, number, expected_type):
        """测试数字分类"""
        assert classify_number(number) == expected_type


# ========== 高级参数化测试 ==========

class TestAdvancedParametrize:
    """高级参数化测试"""

    @pytest.mark.parametrize("score,grade", [
        (95, "A"),
        (90, "A"),
        (85, "B"),
        (80, "B"),
        (75, "C"),
        (70, "C"),
        (65, "D"),
        (60, "D"),
        (55, "F"),
        (0, "F"),
    ])
    def test_get_grade(self, score, grade):
        """测试成绩等级转换"""
        assert get_grade(score) == grade

    @pytest.mark.parametrize("nested,expected", [
        ([1, 2, 3], [1, 2, 3]),
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([[1, [2, 3]], [4, 5]], [1, 2, 3, 4, 5]),
        ([], []),
        ([[[]]], []),
        ([1, [2, [3, [4]]]], [1, 2, 3, 4]),
    ])
    def test_flatten_list(self, nested, expected):
        """测试列表扁平化"""
        assert flatten_list(nested) == expected

    @pytest.mark.parametrize("input_data,operation,expected", [
        ((2, 3), multiply, 6),
        ((5, 0), multiply, 0),
        ((-2, -3), multiply, 6),
    ])
    def test_operations_with_functions(self, input_data, operation, expected):
        """测试带函数的参数化"""
        assert operation(*input_data) == expected


# ========== 使用字典参数化 ==========

class TestDictParametrize:
    """使用字典进行参数化"""

    @pytest.mark.parametrize("test_data", [
        {"name": "Alice", "age": 30, "expected_age_group": "adult"},
        {"name": "Bob", "age": 17, "expected_age_group": "minor"},
        {"name": "Charlie", "age": 65, "expected_age_group": "senior"},
    ])
    def test_user_profile(self, test_data):
        """测试用户档案"""
        age = test_data["age"]
        expected = test_data["expected_age_group"]
        
        if age < 18:
            age_group = "minor"
        elif age < 60:
            age_group = "adult"
        else:
            age_group = "senior"
        
        assert age_group == expected


# ========== 多个参数化装饰器 ==========

class TestMultipleParametrize:
    """多个参数化装饰器"""

    @pytest.mark.parametrize("x", [1, 2, 3])
    @pytest.mark.parametrize("y", [4, 5, 6])
    def test_cartesian_product(self, x, y):
        """测试笛卡尔积组合（会生成 3x3=9 个测试用例）"""
        result = multiply(x, y)
        assert result == x * y
        print(f"\n{x} * {y} = {result}")


# ========== 参数化 ID ==========

class TestParametrizeWithIds:
    """带自定义 ID 的参数化测试"""

    @pytest.mark.parametrize("base,exponent,expected", [
        (2, 3, 8),
        (3, 2, 9),
        (10, 0, 1),
    ], ids=["two_cubed", "three_squared", "ten_to_zero"])
    def test_power_with_ids(self, base, exponent, expected):
        """测试幂运算（带自定义测试ID）"""
        assert base ** exponent == expected


# ========== 从函数生成参数 ==========

def get_test_cases():
    """生成测试用例的函数"""
    return [
        (1, 2, 3),
        (4, 5, 9),
        (10, 20, 30),
        (-1, 1, 0),
    ]


class TestGeneratedParameters:
    """从函数生成的参数化测试"""

    @pytest.mark.parametrize("a,b,expected", get_test_cases())
    def test_addition_generated(self, a, b, expected):
        """测试加法（参数由函数生成）"""
        assert a + b == expected


# ========== 边界值测试 ==========

class TestBoundaryValues:
    """边界值测试"""

    @pytest.mark.parametrize("value", [
        -1000000,  # 极小值
        -1,        # 负数边界
        0,         # 零
        1,         # 正数边界
        1000000,   # 极大值
    ])
    def test_number_boundaries(self, value):
        """测试数字边界"""
        result = multiply(value, 1)
        assert result == value

    @pytest.mark.parametrize("text", [
        "",           # 空字符串
        " ",          # 空格
        "a",          # 单字符
        "a" * 1000,   # 长字符串
    ])
    def test_string_boundaries(self, text):
        """测试字符串边界"""
        # 回文检测应该能处理各种边界情况
        result = is_palindrome(text)
        assert isinstance(result, bool)


# ========== 性能测试参数化 ==========

class TestPerformanceParametrize:
    """性能相关的参数化测试"""

    @pytest.mark.parametrize("size", [10, 100, 1000, 10000])
    def test_flatten_performance(self, size):
        """测试不同规模数据的扁平化性能"""
        # 创建嵌套列表
        nested = [[i] for i in range(size)]
        
        import time
        start = time.time()
        result = flatten_list(nested)
        end = time.time()
        
        # 验证结果正确
        assert len(result) == size
        assert result == list(range(size))
        
        # 性能断言（应该在合理时间内完成）
        elapsed = end - start
        assert elapsed < 1.0, f"处理 {size} 个元素耗时 {elapsed:.4f}秒，超过预期"


if __name__ == "__main__":
    # 运行测试: pytest test_parametrize.py -v
    pass
