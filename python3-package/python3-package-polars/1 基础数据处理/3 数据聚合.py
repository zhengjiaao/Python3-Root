import polars as pl
from typing import Optional, List, Dict, Any
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
            "city": ["New York", "San Francisco", "Chicago", "New York", "Chicago"],
            "salary": [70000, 50000, 80000, 60000, 75000]
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
        new_columns: Optional[List[str]] = None
    ) -> pl.DataFrame:
        """读取 CSV 文件并可选重命名列"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        df = pl.read_csv(file_path)
        if new_columns:
            df = df.rename({col: new_columns[i] for i, col in enumerate(df.columns)})
        return df

    @staticmethod
    def group_aggregate(
        df: pl.DataFrame,
        group_by_column: str,
        aggregations: Dict[str, List[str]]
    ) -> pl.DataFrame:
        """
        对 DataFrame 进行分组聚合操作
        :param df: 输入 DataFrame
        :param group_by_column: 分组字段名
        :param aggregations: 聚合方式字典，格式为 {'列名': ['mean', 'sum']}
        :return: 聚合后的 DataFrame
        """
        agg_exprs = []
        for col, ops in aggregations.items():
            for op in ops:
                if op == "mean":
                    agg_exprs.append(pl.col(col).mean().alias(f"{col}_mean"))
                elif op == "sum":
                    agg_exprs.append(pl.col(col).sum().alias(f"{col}_sum"))
                elif op == "count":
                    agg_exprs.append(pl.col(col).count().alias(f"{col}_count"))
                elif op == "max":
                    agg_exprs.append(pl.col(col).max().alias(f"{col}_max"))
                elif op == "min":
                    agg_exprs.append(pl.col(col).min().alias(f"{col}_min"))

        return df.group_by(group_by_column).agg(agg_exprs)


# 示例用法
if __name__ == "__main__":
    csv_file = "data.csv"

    # 1. 先尝试读取 CSV，若不存在则生成 mock 数据并写入
    if os.path.exists(csv_file):
        print("正在从现有 CSV 文件读取数据...")
        df = DataProcessor.read_csv(csv_file, new_columns=["id", "name", "age", "city", "salary"])
    else:
        print("未找到数据文件，正在生成 mock 数据并写入 CSV...")
        df = DataProcessor.generate_mock_data()
        DataProcessor.write_csv(df, csv_file)

    # 2. 输出原始数据
    print("\n原始数据：")
    print(df)

    # 3. 执行分组聚合：按城市分组，计算平均年龄和总薪资
    aggregations = {
        "age": ["mean"],
        "salary": ["sum"]
    }

    aggregated_df = DataProcessor.group_aggregate(df, "city", aggregations)

    # 4. 输出结果
    print("\n分组聚合后的数据：")
    print(aggregated_df)

    # 5. 可选：将结果写入 Parquet 文件
    output_file = "aggregated_data.parquet"
    aggregated_df.write_parquet(output_file)
    print(f"\n结果已保存至: {output_file}")
