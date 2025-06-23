import polars as pl
from typing import Optional
import os

class DataProcessor:
    def __init__(self):
        pass

    @staticmethod
    def generate_mock_data() -> pl.DataFrame:
        """生成用于测试的 mock 数据"""
        return pl.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "age": [35, 28, 42, 29, 37],
            "city": ["New York", "San Francisco", "Chicago", "New York", "Chicago"]
        })

    @staticmethod
    def write_csv(
        df: pl.DataFrame,
        file_path: str
    ) -> None:
        """将 DataFrame 写入 CSV 文件"""
        df.write_csv(file_path)

    @staticmethod
    def read_csv(
        file_path: str,
        new_columns: Optional[list] = None
    ) -> pl.DataFrame:
        """读取 CSV 文件并可选重命名列"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        df = pl.read_csv(file_path)
        if new_columns:
            df = df.rename({col: new_columns[i] for i, col in enumerate(df.columns)})
        return df

    @staticmethod
    def filter_and_sort(
        df: pl.DataFrame,
        filter_column: str,
        filter_value: float,
        sort_column: str,
        descending: bool = True
    ) -> pl.DataFrame:
        """
        通用数据过滤和排序方法
        :param df: 输入 DataFrame
        :param filter_column: 过滤列名
        :param filter_value: 过滤值（如 age > 30）
        :param sort_column: 排序列名
        :param descending: 是否降序
        :return: 处理后的 DataFrame
        """
        return df.filter(pl.col(filter_column) > filter_value).sort(sort_column, descending=descending)


# 示例用法
if __name__ == "__main__":
    csv_file = "data.csv"

    # 1. 先尝试读取 CSV，若不存在则生成 mock 数据并写入
    if os.path.exists(csv_file):
        print("正在从现有 CSV 文件读取数据...")
        df = DataProcessor.read_csv(csv_file, new_columns=["id", "name", "age", "city"])
    else:
        print("未找到数据文件，正在生成 mock 数据并写入 CSV...")
        df = DataProcessor.generate_mock_data()
        DataProcessor.write_csv(df, csv_file)

    print("\n原始数据：")
    print(df)

    # 2. 执行过滤和排序：年龄 > 30，并按城市降序排列
    result_df = DataProcessor.filter_and_sort(df, "age", 30, "city", descending=True)

    # 3. 输出结果
    print("\n过滤并排序后的数据：")
    print(result_df)

    # 4. 可选：将结果写入 Parquet 文件
    output_file = "filtered_data.parquet"
    result_df.write_parquet(output_file)
    print(f"\n结果已保存至: {output_file}")
