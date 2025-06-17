import dask.dataframe as dd
from typing import Optional
import time

# 场景：处理超过单机内存的 CSV/Parquet 文件（如 25GB+ 数据）。
#
# 优势：分块（chunk）加载数据，并行执行操作。

def load_large_dataset(file_path: str, file_format: str = 'csv', chunk_size: int = 25e6) -> Optional[dd.DataFrame]:
    """
    加载大规模数据集（CSV 或 Parquet 格式），按分块方式读取以节省内存。将 CSV 转换为 Parquet，提升 I/O 性能。

    :param file_path: 文件路径
    :param file_format: 文件格式 ('csv' 或 'parquet')
    :param chunk_size: 每个分块大小（字节）
    :return: Dask DataFrame 或 None（失败时）
    """
    try:
        if file_format == 'csv':
            return dd.read_csv(file_path, blocksize=chunk_size)
        elif file_format == 'parquet':
            return dd.read_parquet(file_path)
        else:
            raise ValueError("不支持的文件格式，请使用 'csv' 或 'parquet'")
    except Exception as e:
        print(f"读取文件时出错：{e}")
        return None


def compute_grouped_mean(df: dd.DataFrame, group_column: str, agg_column: str) -> Optional:
    """
    执行分组聚合操作并返回结果。

    :param df: Dask DataFrame
    :param group_column: 分组字段
    :param agg_column: 聚合字段
    :return: 聚合结果或 None（失败时）
    """
    try:
        result = df.groupby(group_column)[agg_column].mean().compute()
        return result
    except Exception as e:
        print(f"执行分组聚合时出错：{e}")
        return None


# 示例使用
if __name__ == "__main__":
    start_time = time.time()  # 开始计时

    # 设置合适的线程数（根据 CPU 核心数调整）
    # from dask.distributed import Client
    # client = Client(n_workers=4)  # 启动本地集群，利用多核优势
    # 不启用 Client，Dask 默认使用多线程调度器

    # 加载数据（建议优先使用 Parquet 格式）
    ddf = load_large_dataset('large_dataset.parquet', file_format='parquet')
    # ddf = load_large_dataset('large_dataset.csv', file_format='csv')


    if ddf is not None:
        # 执行并行计算：分组聚合
        result = compute_grouped_mean(ddf, 'category', 'price')
        if result is not None:
            print(result)

    end_time = time.time()  # 结束计时
    elapsed_time = end_time - start_time
    print(f"✅ 程序总耗时：{elapsed_time:.2f} 秒")