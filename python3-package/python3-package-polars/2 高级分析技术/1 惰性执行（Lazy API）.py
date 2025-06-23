import polars as pl
from typing import Optional, List, Dict, Any
import os

class LazyDataProcessor:
    def __init__(self):
        pass

    @staticmethod
    def generate_mock_data() -> pl.DataFrame:
        """生成用于测试的 mock 数据"""
        return pl.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "age": [35, 28, 42, 29, 37],
            "gender": ["F", "M", "M", "M", "F"],
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
    def read_lazy_csv(
            file_path: str,
            columns: Optional[List[str]] = None
    ) -> pl.LazyFrame:
        """惰性读取 CSV 文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        lazy_df = pl.scan_csv(file_path)
        if columns:
            lazy_df = lazy_df.select(columns)
        return lazy_df

    @staticmethod
    def execute_lazy_query(
        lazy_df: pl.LazyFrame,
        filter_expr: pl.Expr,
        group_by_column: str,
        agg_exprs: List[pl.Expr]
    ) -> pl.DataFrame:
        """
        执行惰性查询计划
        :param lazy_df: 输入 LazyFrame
        :param filter_expr: 过滤表达式，如 pl.col("age") > 25
        :param group_by_column: 分组字段
        :param agg_exprs: 聚合表达式列表
        :return: 结果 DataFrame
        """
        return (
            lazy_df
            .filter(filter_expr)
            .group_by(group_by_column)
            .agg(agg_exprs)
            .collect()
        )


# 示例用法
if __name__ == "__main__":
    csv_file = "data.csv"

    # 1. 先尝试读取 CSV，若不存在则生成 mock 数据并写入
    if os.path.exists(csv_file):
        print("正在从现有 CSV 文件读取数据...")
        df = pl.read_csv(csv_file)
    else:
        print("未找到数据文件，正在生成 mock 数据并写入 CSV...")
        df = LazyDataProcessor.generate_mock_data()
        LazyDataProcessor.write_csv(df, csv_file)

    # 2. 输出原始数据
    print("\n原始数据：")
    print(df)

    # 3. 惰性读取数据
    lazy_df = LazyDataProcessor.read_lazy_csv(csv_file)

    # 4. 构建查询计划
    result_df = LazyDataProcessor.execute_lazy_query(
        lazy_df=lazy_df,
        filter_expr=pl.col("age") > 25,
        group_by_column="gender",
        agg_exprs=[pl.col("salary").mean().alias("avg_salary")]
    )

    # 5. 输出结果
    print("\n惰性执行后的分组聚合结果：")
    print(result_df)

    # 6. 可选：将结果写入 Parquet 文件
    output_file = "lazy_aggregated_result.parquet"
    result_df.write_parquet(output_file)
    print(f"\n结果已保存至: {output_file}")
