import dask.dataframe as dd
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import time


def create_sample_df() -> dd.DataFrame:
    """
    创建一个包含 NaN 的示例 Dask DataFrame。

    :return: Dask DataFrame
    """
    pdf = pd.DataFrame({
        'A': [1, np.nan, 3],
        'B': [np.nan, 5, 6]
    })
    return dd.from_pandas(pdf, npartitions=2)


def count_missing_values(df: dd.DataFrame) -> Optional[Dict[str, int]]:
    """
    统计每列中的缺失值数量（包括 NaN）。

    :param df: 输入的 Dask DataFrame
    :return: 各列缺失值数量字典 或 None（失败时）
    """
    try:
        missing_counts = df.isnull().sum().compute()
        return dict(missing_counts)
    except Exception as e:
        print(f"统计缺失值失败：{e}")
        return None


def fill_missing_values(df: dd.DataFrame, fill_value: Any = 0) -> Optional[dd.DataFrame]:
    """
    填充缺失值。

    :param df: 输入的 Dask DataFrame
    :param fill_value: 填充值
    :return: 新的 Dask DataFrame 或 None（失败时）
    """
    try:
        return df.fillna(fill_value)
    except Exception as e:
        print(f"填充缺失值失败：{e}")
        return None


def drop_missing_rows(df: dd.DataFrame, subset: Optional[list] = None) -> Optional[dd.DataFrame]:
    """
    删除包含缺失值的行。

    :param df: 输入的 Dask DataFrame
    :param subset: 指定检查缺失值的列
    :return: 新的 Dask DataFrame 或 None（失败时）
    """
    try:
        return df.dropna(subset=subset)
    except Exception as e:
        print(f"删除缺失值失败：{e}")
        return None


def run_data_cleaning_pipeline() -> None:
    """
    运行完整的缺失值处理流程。
    """
    start_time = time.time()

    # 创建数据
    df = create_sample_df()
    print("📊 原始数据：")
    print(df.compute())

    # 缺失值统计
    missing_counts = count_missing_values(df)
    if missing_counts:
        print("🔍 缺失值统计：")
        for col, count in missing_counts.items():
            print(f"{col}: {count} 个缺失值")

    # 缺失值填充
    filled_df = fill_missing_values(df, fill_value=0)
    if filled_df is not None:
        print("\n✅ 填充后数据：")
        print(filled_df.compute())

    # 删除含缺失值的行
    dropped_df = drop_missing_rows(df)
    if dropped_df is not None:
        print("\n🗑️ 删除缺失值后数据：")
        print(dropped_df.compute())

    end_time = time.time()
    print(f"\n⏱️ 总耗时：{end_time - start_time:.4f} 秒")


if __name__ == "__main__":
    run_data_cleaning_pipeline()
