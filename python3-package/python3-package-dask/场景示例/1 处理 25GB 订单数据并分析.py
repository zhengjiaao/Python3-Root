from dask.distributed import Client
import dask.dataframe as dd
import logging
import time
from typing import Optional, Dict
import os

# 端到端工作流：处理 25GB 订单数据并分析

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start_dask_client(n_workers: int = 4) -> Optional[Client]:
    """
    启动 Dask 分布式客户端。

    :param n_workers: 工作线程数
    :return: Client 实例 或 None（失败时）
    """
    try:
        client = Client(n_workers=n_workers)
        logger.info("✅ 已启动分布式调度器")
        return client
    except Exception as e:
        logger.error(f"启动 Dask 客户端失败：{e}")
        return None


def load_data(input_pattern: str,
              file_format: str = 'csv',
              dtypes: Optional[Dict] = None,
              parse_dates: Optional[list] = None) -> Optional[dd.DataFrame]:
    """
    加载大规模数据集（CSV/Parquet）。

    :param input_pattern: 文件路径或通配符（如 orders_*.csv）
    :param file_format: 文件格式 ('csv' 或 'parquet')
    :param dtypes: 字段类型映射
    :param parse_dates: 需要解析为日期的字段
    :return: Dask DataFrame 或 None（失败时）
    """
    try:
        if file_format == 'csv':
            return dd.read_csv(input_pattern, dtype=dtypes, parse_dates=parse_dates)
        elif file_format == 'parquet':
            return dd.read_parquet(input_pattern)
        else:
            raise ValueError("仅支持 csv 或 parquet 格式")
    except Exception as e:
        logger.error(f"加载数据失败：{e}")
        return None


def clean_data(df: dd.DataFrame, filter_column: str, threshold: float = 0) -> Optional[dd.DataFrame]:
    """
    数据清洗：过滤异常值。

    :param df: 原始数据
    :param filter_column: 要过滤的列名
    :param threshold: 过滤阈值
    :return: 清洗后的数据 或 None（失败时）
    """
    try:
        return df[df[filter_column] > threshold]
    except Exception as e:
        logger.error(f"数据清洗失败：{e}")
        return None


def aggregate_daily_sales(df: dd.DataFrame,
                          group_column: str,
                          agg_column: str) -> Optional[dd.Series]:
    """
    按日期聚合销售额。

    :param df: 清洗后的数据
    :param group_column: 分组字段（如 order_date）
    :param agg_column: 聚合字段（如 price）
    :return: 每日销售额 或 None（失败时）
    """
    try:
        return df.groupby(group_column)[agg_column].sum()
    except Exception as e:
        logger.error(f"聚合计算失败：{e}")
        return None


def save_cleaned_data(df: dd.DataFrame, output_file: str, file_format: str = 'parquet') -> bool:
    """
    保存清洗后的数据。

    :param df: 清洗后的 Dask DataFrame
    :param output_file: 输出文件路径
    :param file_format: 输出格式（默认 parquet）
    :return: 成功与否
    """
    try:
        if file_format == 'parquet':
            df.to_parquet(output_file)
        elif file_format == 'csv':
            df.to_csv(output_file, single_file=True)
        else:
            raise ValueError("仅支持 parquet 或 csv 格式")
        logger.info(f"💾 数据已保存至 {output_file}")
        return True
    except Exception as e:
        logger.error(f"数据保存失败：{e}")
        return False


def run_pipeline(
    input_dir: str = './data',          # 新增输入目录参数
    input_prefix: str = 'orders', # 支持中文前缀
    input_suffix: str = 'csv',          # 输入格式：csv 或 parquet
    output_cleaned: str = 'cleaned_orders.parquet',
    output_daily_sales: str = 'daily_sales.csv',
    dtypes: Optional[Dict] = None,
    parse_dates: Optional[list] = None,
    filter_column: str = 'price',
    threshold: float = 0.0,
    group_column: str = 'order_date',
    agg_column: str = 'price'
) -> None:
    """
    执行完整的端到端数据分析流程。
    """
    start_time = time.time()

    # 启动客户端
    # client = start_dask_client(n_workers=4)
    # if client is None:
    #     return

    # 构建输入模式
    input_pattern = os.path.join(input_dir, f"{input_prefix}*.{input_suffix}")

    # 阶段1：加载数据
    load_start = time.time()
    ddf = load_data(input_pattern, file_format=input_suffix, dtypes=dtypes, parse_dates=parse_dates)
    if ddf is None:
        return
    load_end = time.time()
    logger.info(f"⏱️ 数据加载耗时：{load_end - load_start:.2f} 秒")

    # 阶段2：数据清洗
    clean_start = time.time()
    ddf_clean = clean_data(df=ddf, filter_column=filter_column, threshold=threshold)
    if ddf_clean is None:
        return
    clean_end = time.time()
    logger.info(f"⏱️ 数据清洗耗时：{clean_end - clean_start:.2f} 秒")

    # 阶段3：保存清洗后数据
    save_start = time.time()
    save_cleaned_data(df=ddf_clean, output_file=output_cleaned, file_format='parquet')
    save_end = time.time()
    logger.info(f"⏱️ 数据保存耗时：{save_end - save_start:.2f} 秒")

    # 阶段4：聚合销售数据
    agg_start = time.time()
    daily_sales = aggregate_daily_sales(df=ddf_clean, group_column=group_column, agg_column=agg_column)
    if daily_sales is None:
        return
    agg_end = time.time()
    logger.info(f"⏱️ 聚合计算耗时：{agg_end - agg_start:.2f} 秒")

    # 阶段5：执行计算并导出结果
    compute_start = time.time()
    result = daily_sales.compute()
    result.to_csv(output_daily_sales)
    compute_end = time.time()
    logger.info(f"⏱️ 结果导出耗时：{compute_end - compute_start:.2f} 秒")

    total_time = time.time() - start_time
    logger.info(f"✅ 总耗时：{total_time:.2f} 秒")

    # 清理资源
    # client.close()


if __name__ == "__main__":
    # 示例配置（根据你的实际路径修改）
    dtypes = {'order_id': 'int64', 'price': 'float64'}
    parse_dates = ['order_date']

    run_pipeline(
        input_dir=r"./data",                  # 中文路径也支持
        input_prefix="orders",                 # 匹配 orders_*.csv
        input_suffix="parquet",                    # 输入格式：csv 或 parquet
        dtypes=dtypes,
        parse_dates=parse_dates,
        filter_column='price',
        group_column='order_date',
        agg_column='price',
        output_cleaned='cleaned_orders.parquet',
        output_daily_sales='daily_sales.csv'
    )
