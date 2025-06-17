from dask.distributed import Client
import dask.dataframe as dd
import logging
import time
from typing import Optional


# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start_dask_client(memory_limit: str = '32GB') -> Optional[Client]:
    """
    启动 Dask 分布式客户端。

    :param memory_limit: 每个工作节点的内存限制
    :return: Client 实例 或 None（失败时）
    """
    try:
        client = Client(memory_limit=memory_limit)
        logger.info("✅ 已启动 Dask 分布式客户端")
        return client
    except Exception as e:
        logger.error(f"❌ 启动 Dask 客户端失败：{e}")
        return None


def load_parquet_data(file_path: str, engine: str = 'pyarrow') -> Optional[dd.DataFrame]:
    """
    加载 Parquet 格式的 DataFrame。

    :param file_path: 文件路径
    :param engine: 使用的引擎（默认 pyarrow）
    :return: Dask DataFrame 或 None（失败时）
    """
    try:
        df = dd.read_parquet(file_path, engine=engine)
        logger.info(f"✅ 数据加载完成：{file_path}")
        return df
    except Exception as e:
        logger.error(f"❌ 数据加载失败：{e}")
        return None


def repartition_data(df: dd.DataFrame, partition_size: str = '100MB') -> Optional[dd.DataFrame]:
    """
    重新分区以适应内存压力。

    :param df: 输入的 Dask DataFrame
    :param partition_size: 每个分块大小
    :return: 重新分区后的 DataFrame 或 None（失败时）
    """
    try:
        df_repart = df.repartition(partition_size=partition_size)
        logger.info(f"✅ 数据已重新分区，分区大小：{partition_size}")
        return df_repart
    except Exception as e:
        logger.error(f"❌ 数据重新分区失败：{e}")
        return None


def set_date_index(df: dd.DataFrame, index_column: str = 'date', sort: bool = True) -> Optional[dd.DataFrame]:
    """
    设置日期列作为索引，并启用排序标记。

    :param df: 输入的 Dask DataFrame
    :param index_column: 索引字段名
    :param sort: 是否启用排序
    :return: 设置索引后的 DataFrame 或 None（失败时）
    """
    try:
        df_indexed = df.set_index(index_column, sorted=sort)
        logger.info(f"✅ 已设置索引字段：{index_column}，排序：{sort}")
        return df_indexed
    except Exception as e:
        logger.error(f"❌ 设置索引失败：{e}")
        return None


def save_sorted_data(df: dd.DataFrame, output_file: str = 'sorted_data.parquet') -> bool:
    """
    将排序后的数据保存为 Parquet 文件。

    :param df: 排序后的 Dask DataFrame
    :param output_file: 输出文件路径
    :return: 成功与否
    """
    try:
        df.to_parquet(output_file)
        logger.info(f"💾 数据已保存至 {output_file}")
        return True
    except Exception as e:
        logger.error(f"❌ 数据保存失败：{e}")
        return False


def run_pipeline(
    input_file: str = 'large_data.parquet',
    output_file: str = 'sorted_data.parquet',
    index_column: str = 'date',
    partition_size: str = '100MB',
    memory_limit: str = '32GB'
):
    """
    执行完整的“按日期索引”流水线任务。
    """
    start_time = time.time()

    # 启动 Dask 客户端
    # client = start_dask_client(memory_limit=memory_limit)
    # if client is None:
    #     return

    # 阶段1：加载数据
    load_start = time.time()
    ddf = load_parquet_data(input_file)
    if ddf is None:
        return
    load_end = time.time()
    logger.info(f"⏱️ 数据加载耗时：{load_end - load_start:.2f} 秒")

    # 阶段2：重新分区
    repart_start = time.time()
    ddf_repart = repartition_data(df=ddf, partition_size=partition_size)
    if ddf_repart is None:
        return
    repart_end = time.time()
    logger.info(f"⏱️ 数据重新分区耗时：{repart_end - repart_start:.2f} 秒")

    # 阶段3：设置索引
    index_start = time.time()
    ddf_sorted = set_date_index(df=ddf_repart, index_column=index_column, sort=True)
    if ddf_sorted is None:
        return
    index_end = time.time()
    logger.info(f"⏱️ 设置索引耗时：{index_end - index_start:.2f} 秒")

    # 阶段4：保存结果
    save_start = time.time()
    success = save_sorted_data(df=ddf_sorted, output_file=output_file)
    save_end = time.time()
    logger.info(f"⏱️ 数据保存耗时：{save_end - save_start:.2f} 秒")

    total_time = time.time() - start_time
    logger.info(f"✅ 总耗时：{total_time:.2f} 秒")
    logger.info(f"🚀 流水线执行 {'成功' if success else '失败'}")

    # 清理资源
    # client.close()


if __name__ == "__main__":
    run_pipeline(
        input_file='large_data.parquet',
        output_file='sorted_data.parquet',
        index_column='date',
        partition_size='100MB',
        memory_limit='32GB'
    )
