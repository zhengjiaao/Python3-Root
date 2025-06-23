import polars as pl
from typing import Callable, List
import multiprocessing
from functools import partial


class ParallelProcessor:
    def __init__(self):
        pass

    @staticmethod
    def generate_mock_data() -> pl.DataFrame:
        """生成用于测试的 mock 数据（包含姓名字段）"""
        return pl.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice Smith", "Bob Johnson", "Charlie Brown", "David Lee", "Eve Wilson"]
        })

    @staticmethod
    def parse_name(name: str) -> List[str]:
        """复杂文本处理逻辑（如姓名解析）"""
        return name.split()

    @staticmethod
    def _process_batch(series: pl.Series, func: Callable) -> pl.Series:
        """
        单个批次的并行处理函数（不再使用 Pool）
        """
        return pl.Series([func(item) for item in series.to_list()])

    @classmethod
    def parallel_apply(cls, s: pl.Series, func: Callable) -> pl.Series:
        """
        并行处理 Series，适用于 map_batches
        """
        num_processes = multiprocessing.cpu_count()
        chunks = [s[i::num_processes] for i in range(num_processes)]

        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.map(partial(cls._process_batch, func=func), chunks)

        return pl.concat(results)

    @classmethod
    def add_parsed_name_column(cls, df: pl.DataFrame) -> pl.DataFrame:
        """
        添加解析后的姓名列
        """
        return df.with_columns(
            parsed_name=pl.col("name").map_batches(lambda s: cls.parallel_apply(s, cls.parse_name))
        )


# 示例用法
if __name__ == "__main__":
    # 1. 生成或读取数据
    df = ParallelProcessor.generate_mock_data()

    # 2. 打印原始数据
    print("原始数据：")
    print(df)

    # 3. 应用并行处理添加新列
    processed_df = ParallelProcessor.add_parsed_name_column(df)

    # 4. 打印处理后数据
    print("\n处理后数据（新增 parsed_name 列）：")
    print(processed_df)
