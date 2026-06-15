"""
pytest 数据处理测试示例
演示如何测试数据清洗、转换和分析逻辑
"""

import pytest


# ========== 被测试的代码 ==========

class DataCleaner:
    """数据清洗器"""
    
    @staticmethod
    def remove_duplicates(data):
        """去除重复项"""
        seen = set()
        result = []
        for item in data:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    
    @staticmethod
    def remove_none_values(data):
        """去除 None 值"""
        return [item for item in data if item is not None]
    
    @staticmethod
    def normalize_strings(strings):
        """标准化字符串（去除空白、转小写）"""
        return [s.strip().lower() for s in strings if isinstance(s, str)]
    
    @staticmethod
    def filter_by_condition(data, condition):
        """根据条件过滤数据"""
        return [item for item in data if condition(item)]


class DataTransformer:
    """数据转换器"""
    
    @staticmethod
    def convert_to_uppercase(strings):
        """转换为大写"""
        return [s.upper() for s in strings if isinstance(s, str)]
    
    @staticmethod
    def square_numbers(numbers):
        """计算平方"""
        return [n ** 2 for n in numbers if isinstance(n, (int, float))]
    
    @staticmethod
    def flatten_nested_list(nested_list):
        """扁平化嵌套列表"""
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(DataTransformer.flatten_nested_list(item))
            else:
                result.append(item)
        return result
    
    @staticmethod
    def transpose_matrix(matrix):
        """转置矩阵"""
        if not matrix:
            return []
        rows = len(matrix)
        cols = len(matrix[0])
        return [[matrix[i][j] for i in range(rows)] for j in range(cols)]


class DataAnalyzer:
    """数据分析器"""
    
    @staticmethod
    def calculate_mean(numbers):
        """计算平均值"""
        if not numbers:
            return 0
        return sum(numbers) / len(numbers)
    
    @staticmethod
    def calculate_median(numbers):
        """计算中位数"""
        if not numbers:
            return 0
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        mid = n // 2
        
        if n % 2 == 0:
            return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
        else:
            return sorted_nums[mid]
    
    @staticmethod
    def calculate_mode(numbers):
        """计算众数"""
        if not numbers:
            return None
        
        from collections import Counter
        counts = Counter(numbers)
        max_count = max(counts.values())
        modes = [num for num, count in counts.items() if count == max_count]
        
        return modes[0] if len(modes) == 1 else modes
    
    @staticmethod
    def calculate_std_dev(numbers):
        """计算标准差"""
        if len(numbers) < 2:
            return 0
        
        mean = DataAnalyzer.calculate_mean(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)
        return variance ** 0.5
    
    @staticmethod
    def find_outliers(numbers, threshold=2):
        """查找异常值（超过均值±threshold倍标准差）"""
        if len(numbers) < 2:
            return []
        
        mean = DataAnalyzer.calculate_mean(numbers)
        std_dev = DataAnalyzer.calculate_std_dev(numbers)
        
        lower_bound = mean - threshold * std_dev
        upper_bound = mean + threshold * std_dev
        
        return [x for x in numbers if x < lower_bound or x > upper_bound]
    
    @staticmethod
    def group_by_key(data, key_func):
        """按键函数分组"""
        groups = {}
        for item in data:
            key = key_func(item)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        return groups


# ========== 数据清洗测试 ==========

class TestDataCleaner:
    """数据清洗器测试"""
    
    def test_remove_duplicates_basic(self):
        """测试去除基本重复项"""
        data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
        result = DataCleaner.remove_duplicates(data)
        
        assert result == [1, 2, 3, 4, 5]
        assert len(result) == 5
    
    def test_remove_duplicates_strings(self):
        """测试去除字符串重复项"""
        data = ["apple", "banana", "apple", "orange", "banana"]
        result = DataCleaner.remove_duplicates(data)
        
        assert result == ["apple", "banana", "orange"]
    
    def test_remove_duplicates_empty(self):
        """测试空列表去重"""
        data = []
        result = DataCleaner.remove_duplicates(data)
        
        assert result == []
    
    def test_remove_none_values_basic(self):
        """测试去除 None 值"""
        data = [1, None, 2, None, 3, None, 4, 5]
        result = DataCleaner.remove_none_values(data)
        
        assert result == [1, 2, 3, 4, 5]
        assert None not in result
    
    def test_remove_none_values_all_none(self):
        """测试全部为 None 的情况"""
        data = [None, None, None]
        result = DataCleaner.remove_none_values(data)
        
        assert result == []
    
    def test_remove_none_values_no_none(self):
        """测试没有 None 的情况"""
        data = [1, 2, 3, 4, 5]
        result = DataCleaner.remove_none_values(data)
        
        assert result == data
    
    def test_normalize_strings_basic(self):
        """测试字符串标准化"""
        data = ["  Hello  ", "WORLD", "  Python  ", "TEST"]
        result = DataCleaner.normalize_strings(data)
        
        assert result == ["hello", "world", "python", "test"]
    
    def test_normalize_strings_with_non_strings(self):
        """测试包含非字符串的标准化"""
        data = ["  Hello  ", 123, None, "WORLD"]
        result = DataCleaner.normalize_strings(data)
        
        assert result == ["hello", "world"]
    
    def test_filter_by_condition_even_numbers(self):
        """测试过滤偶数"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = DataCleaner.filter_by_condition(data, lambda x: x % 2 == 0)
        
        assert result == [2, 4, 6, 8, 10]
    
    def test_filter_by_condition_positive_numbers(self):
        """测试过滤正数"""
        data = [-5, -2, 0, 3, 7, -1, 10]
        result = DataCleaner.filter_by_condition(data, lambda x: x > 0)
        
        assert result == [3, 7, 10]


# ========== 数据转换测试 ==========

class TestDataTransformer:
    """数据转换器测试"""
    
    def test_convert_to_uppercase_basic(self):
        """测试转换为大写"""
        data = ["hello", "world", "python"]
        result = DataTransformer.convert_to_uppercase(data)
        
        assert result == ["HELLO", "WORLD", "PYTHON"]
    
    def test_square_numbers_basic(self):
        """测试计算平方"""
        data = [1, 2, 3, 4, 5]
        result = DataTransformer.square_numbers(data)
        
        assert result == [1, 4, 9, 16, 25]
    
    def test_square_numbers_negative(self):
        """测试负数平方"""
        data = [-2, -1, 0, 1, 2]
        result = DataTransformer.square_numbers(data)
        
        assert result == [4, 1, 0, 1, 4]
    
    def test_flatten_nested_list_simple(self):
        """测试简单嵌套列表扁平化"""
        data = [[1, 2], [3, 4], [5, 6]]
        result = DataTransformer.flatten_nested_list(data)
        
        assert result == [1, 2, 3, 4, 5, 6]
    
    def test_flatten_nested_list_deep(self):
        """测试深度嵌套列表扁平化"""
        data = [1, [2, [3, [4, [5]]]]]
        result = DataTransformer.flatten_nested_list(data)
        
        assert result == [1, 2, 3, 4, 5]
    
    def test_flatten_nested_list_empty(self):
        """测试空列表扁平化"""
        data = [[], [[]], [[[]]]]
        result = DataTransformer.flatten_nested_list(data)
        
        assert result == []
    
    def test_transpose_matrix_square(self):
        """测试方阵转置"""
        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        result = DataTransformer.transpose_matrix(matrix)
        
        expected = [
            [1, 4, 7],
            [2, 5, 8],
            [3, 6, 9]
        ]
        assert result == expected
    
    def test_transpose_matrix_rectangular(self):
        """测试矩形矩阵转置"""
        matrix = [
            [1, 2],
            [3, 4],
            [5, 6]
        ]
        result = DataTransformer.transpose_matrix(matrix)
        
        expected = [
            [1, 3, 5],
            [2, 4, 6]
        ]
        assert result == expected
    
    def test_transpose_empty_matrix(self):
        """测试空矩阵转置"""
        matrix = []
        result = DataTransformer.transpose_matrix(matrix)
        
        assert result == []


# ========== 数据分析测试 ==========

class TestDataAnalyzer:
    """数据分析器测试"""
    
    def test_calculate_mean_basic(self):
        """测试计算基本平均值"""
        data = [1, 2, 3, 4, 5]
        result = DataAnalyzer.calculate_mean(data)
        
        assert result == 3.0
    
    def test_calculate_mean_single_value(self):
        """测试单值平均值"""
        data = [10]
        result = DataAnalyzer.calculate_mean(data)
        
        assert result == 10.0
    
    def test_calculate_mean_empty(self):
        """测试空列表平均值"""
        data = []
        result = DataAnalyzer.calculate_mean(data)
        
        assert result == 0
    
    def test_calculate_mean_negative(self):
        """测试负数平均值"""
        data = [-5, -10, -15]
        result = DataAnalyzer.calculate_mean(data)
        
        assert result == -10.0
    
    def test_calculate_median_odd(self):
        """测试奇数个元素的中位数"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        result = DataAnalyzer.calculate_median(data)
        
        assert result == 5
    
    def test_calculate_median_even(self):
        """测试偶数个元素的中位数"""
        data = [1, 2, 3, 4, 5, 6]
        result = DataAnalyzer.calculate_median(data)
        
        assert result == 3.5
    
    def test_calculate_median_single(self):
        """测试单值中位数"""
        data = [42]
        result = DataAnalyzer.calculate_median(data)
        
        assert result == 42
    
    def test_calculate_mode_single(self):
        """测试单个众数"""
        data = [1, 2, 2, 3, 3, 3, 4, 4]
        result = DataAnalyzer.calculate_mode(data)
        
        assert result == 3
    
    def test_calculate_mode_multiple(self):
        """测试多个众数"""
        data = [1, 1, 2, 2, 3]
        result = DataAnalyzer.calculate_mode(data)
        
        # 应该返回所有众数
        assert isinstance(result, list)
        assert 1 in result
        assert 2 in result
    
    def test_calculate_std_dev_basic(self):
        """测试计算标准差"""
        data = [2, 4, 4, 4, 5, 5, 7, 9]
        result = DataAnalyzer.calculate_std_dev(data)
        
        # 样本标准差约为 2.0
        assert pytest.approx(result, rel=0.1) == 2.0
    
    def test_calculate_std_dev_small_dataset(self):
        """测试小数据集标准差"""
        data = [1, 2]
        result = DataAnalyzer.calculate_std_dev(data)
        
        assert pytest.approx(result) == 0.7071067811865476
    
    def test_find_outliers_basic(self):
        """测试查找异常值"""
        data = [10, 12, 12, 13, 12, 11, 14, 13, 12, 100]
        outliers = DataAnalyzer.find_outliers(data)
        
        assert 100 in outliers
        assert len(outliers) >= 1
    
    def test_find_outliers_none(self):
        """测试没有异常值"""
        data = [10, 12, 12, 13, 12, 11, 14, 13, 12, 11]
        outliers = DataAnalyzer.find_outliers(data)
        
        assert len(outliers) == 0
    
    def test_group_by_key_basic(self):
        """测试基本分组"""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 30},
            {"name": "David", "age": 25},
        ]
        
        groups = DataAnalyzer.group_by_key(data, lambda x: x["age"])
        
        assert len(groups) == 2
        assert len(groups[30]) == 2
        assert len(groups[25]) == 2
    
    def test_group_by_key_string(self):
        """测试字符串键分组"""
        data = ["apple", "banana", "avocado", "blueberry", "cherry"]
        
        groups = DataAnalyzer.group_by_key(data, lambda x: x[0])
        
        assert len(groups['a']) == 2
        assert len(groups['b']) == 2
        assert len(groups['c']) == 1


# ========== 综合数据处理测试 ==========

class TestDataProcessingPipeline:
    """数据处理流水线测试"""
    
    def test_full_data_pipeline(self):
        """测试完整的数据处理流程"""
        # 原始数据（包含噪声）
        raw_data = [
            "  Hello  ", "WORLD", None, "  Python  ", 
            "hello", None, "WORLD", "  TEST  "
        ]
        
        # 步骤1：去除 None
        cleaned = DataCleaner.remove_none_values(raw_data)
        assert None not in cleaned
        
        # 步骤2：标准化字符串
        normalized = DataCleaner.normalize_strings(cleaned)
        assert normalized == ["hello", "world", "python", "hello", "world", "test"]
        
        # 步骤3：去重
        unique = DataCleaner.remove_duplicates(normalized)
        assert unique == ["hello", "world", "python", "test"]
        
        # 步骤4：转换
        uppercased = DataTransformer.convert_to_uppercase(unique)
        assert uppercased == ["HELLO", "WORLD", "PYTHON", "TEST"]
    
    def test_numerical_analysis_pipeline(self):
        """测试数值分析流程"""
        # 原始数据（包含异常值）
        data = [10, 12, 12, 13, 12, 11, 14, 13, 12, 100, 11, 13]
        
        # 步骤1：查找异常值
        outliers = DataAnalyzer.find_outliers(data)
        assert 100 in outliers
        
        # 步骤2：去除异常值
        filtered = [x for x in data if x not in outliers]
        
        # 步骤3：计算统计量
        mean = DataAnalyzer.calculate_mean(filtered)
        median = DataAnalyzer.calculate_median(filtered)
        std_dev = DataAnalyzer.calculate_std_dev(filtered)
        
        # 验证统计量合理
        assert 11 <= mean <= 13
        assert 11 <= median <= 13
        assert std_dev < 2.0


# ========== 边界情况测试 ==========

class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_datasets(self):
        """测试空数据集"""
        assert DataAnalyzer.calculate_mean([]) == 0
        assert DataAnalyzer.calculate_median([]) == 0
        assert DataAnalyzer.calculate_mode([]) is None
        assert DataAnalyzer.calculate_std_dev([]) == 0
    
    def test_single_element_datasets(self):
        """测试单元素数据集"""
        assert DataAnalyzer.calculate_mean([5]) == 5
        assert DataAnalyzer.calculate_median([5]) == 5
        assert DataAnalyzer.calculate_std_dev([5]) == 0
    
    def test_large_numbers(self):
        """测试大数"""
        data = [1e10, 2e10, 3e10]
        mean = DataAnalyzer.calculate_mean(data)
        
        assert mean == 2e10
    
    def test_very_small_numbers(self):
        """测试极小数"""
        data = [1e-10, 2e-10, 3e-10]
        mean = DataAnalyzer.calculate_mean(data)
        
        assert pytest.approx(mean) == 2e-10
    
    def test_mixed_positive_negative(self):
        """测试混合正负数"""
        data = [-5, -3, 0, 3, 5]
        mean = DataAnalyzer.calculate_mean(data)
        
        assert mean == 0


if __name__ == "__main__":
    # 运行测试: pytest test_data_processing.py -v
    pass
