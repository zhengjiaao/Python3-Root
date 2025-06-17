import dask.array as da
import numpy as np
import time
from typing import Optional, Tuple


# 场景：处理超大型数组（如 1000x1000 矩阵），替代 NumPy。
#
# 优势：将大数组拆分为小块，分布式计算。

def create_chunked_array(shape: Tuple[int, int] = (1000, 1000),
                         chunks: Tuple[int, int] = (100, 100)) -> Optional[da.Array]:
    """
    创建一个分块的随机数组。

    :param shape: 数组维度
    :param chunks: 每个分块大小
    :return: Dask Array 或 None（失败时）
    """
    try:
        return da.random.random(shape, chunks=chunks)
    except Exception as e:
        print(f"创建数组失败：{e}")
        return None


def compute_transpose_sum(arr: da.Array) -> Optional[da.Array]:
    """
    执行转置加法操作 y = arr + arr.T。

    :param arr: 输入的 Dask Array
    :return: 转置加法结果或 None（失败时）
    """
    try:
        return arr + arr.T
    except Exception as e:
        print(f"转置加法出错：{e}")
        return None


def compute_global_mean(arr: da.Array) -> Optional[float]:
    """
    计算数组的全局均值。

    :param arr: 输入的 Dask Array
    :return: 均值或 None（失败时）
    """
    try:
        return arr.mean().compute()
    except Exception as e:
        print(f"计算均值出错：{e}")
        return None


def run_computation(use_distributed: bool = False,
                    array_shape: Tuple[int, int] = (1000, 1000),
                    chunk_size: Tuple[int, int] = (100, 100)) -> Optional[float]:
    """
    运行完整的科学计算流程。

    :param use_distributed: 是否启用分布式调度器
    :param array_shape: 数组形状
    :param chunk_size: 分块大小
    :return: 最终均值或 None（失败时）
    """
    client = None
    if use_distributed:
        from dask.distributed import Client
        client = Client(n_workers=4)
        print("✅ 已启动分布式调度器")

    start_time = time.time()

    x = create_chunked_array(array_shape, chunk_size)
    if x is None:
        return None

    y = compute_transpose_sum(x)
    if y is None:
        return None

    mean_value = compute_global_mean(y)

    end_time = time.time()
    print(f"⏱️ 总耗时：{end_time - start_time:.2f} 秒")
    if client:
        client.close()

    return mean_value


if __name__ == "__main__":
    result = run_computation(use_distributed=False)
    if result is not None:
        print(f"📊 全局均值：{result:.6f}")
