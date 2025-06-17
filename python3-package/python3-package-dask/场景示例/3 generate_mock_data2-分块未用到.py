import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import os
import logging
import time


# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_orders(num_rows: int, chunk_size: int, output_dir: str):
    """
    分块生成订单模拟数据并保存为 Parquet 文件。

    :param num_rows: 总行数
    :param chunk_size: 每个分块的行数
    :param output_dir: 输出目录
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 清空旧文件
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))

    logger.info(f"开始生成 {num_rows} 行订单数据（Parquet 格式）...")

    total_chunks = (num_rows + chunk_size - 1) // chunk_size
    start_time = time.time()

    base_date = pd.to_datetime('2020-01-01')
    date_range = pd.date_range(base_date, periods=365 * 5, freq='D')  # 5 年内的日期循环使用

    for i in range(total_chunks):
        current_chunk = min(chunk_size, num_rows - i * chunk_size)
        logger.info(f"生成第 {i+1}/{total_chunks} 个分块，共 {current_chunk} 行...")

        df = pd.DataFrame({
            'order_id': np.arange(i * chunk_size + 1, (i + 1) * chunk_size + 1),
            'customer_id': np.random.randint(1000, 9999, size=current_chunk),
            'product_id': np.random.randint(100, 999, size=current_chunk),
            'price': np.round(np.random.uniform(10, 1000, size=current_chunk), 2),
            'quantity': np.random.randint(1, 10, size=current_chunk),
            'date': np.random.choice(date_range, current_chunk)
        })

        table = pa.Table.from_pandas(df)
        filename = os.path.join(output_dir, f"large_data_{i:03d}.parquet")
        pq.write_table(table, filename)

        logger.info(f"已写入：{filename}")

    elapsed = time.time() - start_time
    logger.info(f"✅ 数据生成完成，总耗时：{elapsed:.2f} 秒")


if __name__ == "__main__":
    output_dir = "data"
    num_rows = 220_000_000  # 2.2 亿行
    chunk_size = 2_000_000   # 每块 200 万行

    generate_orders(num_rows=num_rows, chunk_size=chunk_size, output_dir=output_dir)
