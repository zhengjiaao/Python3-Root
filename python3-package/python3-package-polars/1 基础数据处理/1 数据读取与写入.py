import polars as pl
from typing import Optional, List, Union
import os


class DataProcessor:
    def __init__(self):
        pass

    @staticmethod
    def read_csv(
        file_path: str,
        columns: Optional[List[str]] = None,
        skip_rows: int = 0,
        encoding: str = "utf8",
        has_header: bool = True,
        new_columns: Optional[List[str]] = None
    ) -> pl.DataFrame:
        """
        高效读取 CSV 文件，支持压缩文件如 `.csv.gz`
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定的文件不存在: {file_path}")
        return pl.read_csv(
            file_path,
            columns=columns,
            skip_rows=skip_rows,
            encoding=encoding,
            has_header=has_header,
            new_columns=new_columns
        )

    @staticmethod
    def write_csv(
        df: pl.DataFrame,
        file_path: str,
        separator: str = ","
    ) -> None:
        """
        写入 CSV 文件，支持自定义分隔符
        """
        df.write_csv(file_path, separator=separator)

    @staticmethod
    def read_excel(
            file_path: str,
            sheet_name: str,
            has_header: bool = True
    ) -> pl.DataFrame:
        """
        读取 Excel 文件，支持多个工作表
        """
        return pl.read_excel(file_path, sheet_name=sheet_name)

    @staticmethod
    def write_excel(
            df: pl.DataFrame,
            file_path: str,
            sheet_name: str = "Sheet1"
    ) -> None:
        """
        写入 Excel 文件（使用 pandas 作为后端）
        """
        df.to_pandas().to_excel(file_path, sheet_name=sheet_name, index=False)

    @staticmethod
    def read_parquet(
        file_path: str,
        columns: Optional[List[str]] = None
    ) -> pl.DataFrame:
        """
        读取 Parquet 列式存储文件，适合大数据量场景
        """
        return pl.read_parquet(file_path, columns=columns)

    @staticmethod
    def write_parquet(
        df: pl.DataFrame,
        file_path: str
    ) -> None:
        """
        写入 Parquet 文件，节省空间且读取速度快
        """
        df.write_parquet(file_path)


# 示例用法
# 场景：高效读取/写入 CSV、Excel、Parquet 等格式的大数据文件
if __name__ == "__main__":
    # 先写入测试 CSV 数据
    test_df = pl.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [30, 25, 35]
    })

    # 写入 CSV
    DataProcessor.write_csv(test_df, "data.csv")
    print("\n已生成测试 CSV 文件: data.csv")

    # 再读取 CSV 并重命名列（可选）
    df_csv = DataProcessor.read_csv("data.csv", new_columns=["id", "name", "age"])

    print("\n读取的 CSV 数据：")
    print(df_csv)

    # 写入测试 Excel 文件
    DataProcessor.write_excel(test_df, "data.xlsx")
    print("\n已生成测试 Excel 文件: data.xlsx")

    # 读取 Excel 文件（需准备 data.xlsx）
    try:
        df_excel = DataProcessor.read_excel("data.xlsx", sheet_name="Sheet1")
        print("\n读取的 Excel 数据：")
        print(df_excel)
    except Exception as e:
        print(f"\n读取 Excel 文件失败：{e}")

    # 写入 Parquet 文件
    DataProcessor.write_parquet(df_csv, "output.parquet")
    print("\n已生成 Parquet 文件: output.parquet")

    # 读取 Parquet 文件
    df_parquet = DataProcessor.read_parquet("output.parquet")
    print("\n读取的 Parquet 数据：")
    print(df_parquet)


