import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import logging
import time
import os


# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_large_parquet_single_file(
    num_rows: int,
    chunk_size: int,
    output_file: str
):
    """
    分块生成模拟数据，并写入为单个 Parquet 文件。

    :param num_rows: 总行数
    :param chunk_size: 每次生成的行数（用于控制内存）
    :param output_file: 输出文件路径
    """
    if os.path.exists(output_file):
        os.remove(output_file)
    logger.info(f"开始生成 {num_rows} 行模拟数据到单个 Parquet 文件：{output_file}")

    # 初始化 schema 和 writer
    schema = None
    writer = None

    base_date = pd.to_datetime('2020-01-01')
    date_range = pd.date_range(base_date, periods=365 * 5, freq='D')  # 5 年日期循环使用

    start_time = time.time()

    for i in range(0, num_rows, chunk_size):
        current_chunk = min(chunk_size, num_rows - i)

        logger.info(f"生成第 {i // chunk_size + 1} 批数据，共 {current_chunk} 行...")

        df = pd.DataFrame({
            'order_id': np.arange(i + 1, i + current_chunk + 1),
            'customer_id': np.random.randint(1000, 9999, size=current_chunk),
            'product_id': np.random.randint(100, 999, size=current_chunk),
            'price': np.round(np.random.uniform(10, 1000, size=current_chunk), 2),
            'quantity': np.random.randint(1, 10, size=current_chunk),
            'date': np.random.choice(date_range, current_chunk)
        })

        table = pa.Table.from_pandas(df)

        if writer is None:
            schema = table.schema
            writer = pq.ParquetWriter(output_file, schema)

        writer.write_table(table)

    writer.close()

    elapsed = time.time() - start_time
    logger.info(f"✅ 单个 Parquet 文件生成完成，总耗时：{elapsed:.2f} 秒")


if __name__ == "__main__":
    output_file = "large_data.parquet"
    num_rows = 220_000_000   # 2.2 亿行
    chunk_size = 2_000_000    # 每次生成 200 万行

    generate_large_parquet_single_file(num_rows=num_rows, chunk_size=chunk_size, output_file=output_file)
