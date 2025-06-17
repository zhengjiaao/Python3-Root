import pandas as pd
import numpy as np
import os
import argparse
import logging
import pyarrow as pa
import pyarrow.parquet as pq

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_orders(num_rows: int, chunk_size: int, output_dir: str, file_format: str):
    """
    分块生成订单模拟数据并保存为 CSV 或 Parquet 文件。

    :param num_rows: 总行数
    :param chunk_size: 每个分块的行数
    :param output_dir: 输出目录
    :param file_format: 输出格式 ('csv' 或 'parquet')
    """
    if file_format not in ('csv', 'parquet'):
        raise ValueError("仅支持 csv 或 parquet 格式")

    os.makedirs(output_dir, exist_ok=True)

    # 清空旧文件
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))

    logger.info(f"开始生成 {num_rows} 行订单数据（{file_format.upper()} 格式）...")

    total_chunks = (num_rows + chunk_size - 1) // chunk_size
    start_time = pd.Timestamp.now()

    # 设置合理的日期范围（比如只用一年内的日期循环）
    base_date = pd.to_datetime('2023-01-01')
    days_in_year = 365  # 只生成 1 年内的日期，循环使用

    for i in range(total_chunks):
        current_chunk = min(chunk_size, num_rows - i * chunk_size)
        logger.info(f"生成第 {i+1}/{total_chunks} 个分块，共 {current_chunk} 行...")

        # 使用模运算限制在一年内循环生成日期
        dates = [base_date + pd.Timedelta(days=d % days_in_year) for d in range(current_chunk)]

        df = pd.DataFrame({
            'order_id': np.arange(i * chunk_size + 1, (i + 1) * chunk_size + 1),
            'order_date': dates,
            'customer_id': np.random.randint(1000, 9999, size=current_chunk),
            'product_id': np.random.randint(100, 999, size=current_chunk),
            'price': np.round(np.random.uniform(10, 1000, size=current_chunk), 2)
        })

        if file_format == 'csv':
            filename = os.path.join(output_dir, f"orders_{i:03d}.csv")
            df.to_csv(filename, index=False)
        elif file_format == 'parquet':
            table = pa.Table.from_pandas(df)
            filename = os.path.join(output_dir, f"orders_{i:03d}.parquet")
            pq.write_table(table, filename)

        logger.info(f"已写入：{filename}")

    elapsed = (pd.Timestamp.now() - start_time).total_seconds()
    logger.info(f"✅ 数据生成完成，总耗时：{elapsed:.2f} 秒")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成模拟订单数据")
    parser.add_argument('--rows', type=int, default=10_000_000, help='总行数') # 默认生成 10 亿行数据
    parser.add_argument('--chunk', type=int, default=1_000_000, help='每块行数') # 默认每块 1 百万行
    parser.add_argument('--output', type=str, default='./data', help='输出目录')
    parser.add_argument('--format', type=str, default='csv', choices=['csv', 'parquet'], help='输出格式')

    args = parser.parse_args()

    generate_orders(
        num_rows=args.rows,
        chunk_size=args.chunk,
        output_dir=args.output,
        file_format=args.format
    )
