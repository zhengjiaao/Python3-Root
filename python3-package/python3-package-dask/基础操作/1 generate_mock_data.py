import pandas as pd
import numpy as np
import os
import argparse
import logging
import pyarrow as pa
import pyarrow.parquet as pq

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_mock_data(
    num_rows: int = 1_000_000,
    chunk_size: int = 100_000,
    categories: list = None,
    output_file: str = 'large_dataset.csv'
) -> None:
    """
    分块生成大规模模拟数据集，并写入 CSV 或 Parquet 文件。

    :param num_rows: 总行数
    :param chunk_size: 每次写入的数据量
    :param categories: 类别列表
    :param output_file: 输出文件路径（支持 .csv 或 .parquet）
    """
    categories = categories or ['Electronics', 'Clothing', 'Home', 'Books', 'Beauty']
    file_ext = os.path.splitext(output_file)[1].lower()

    if file_ext not in ('.csv', '.parquet'):
        raise ValueError("仅支持 .csv 或 .parquet 格式")

    # 删除已有文件
    if os.path.exists(output_file):
        logger.warning(f"删除已存在的文件：{output_file}")
        os.remove(output_file)

    try:
        for i in range(0, num_rows, chunk_size):
            current_chunk = min(chunk_size, num_rows - i)
            df = pd.DataFrame({
                'category': np.random.choice(categories, size=current_chunk),
                'price': np.round(np.random.uniform(10, 1000, size=current_chunk), 2)
            })

            mode = 'w' if i == 0 else 'a'
            header = (i == 0)

            if file_ext == '.csv':
                df.to_csv(output_file, index=False, mode=mode, header=header)
            elif file_ext == '.parquet':
                table = pa.Table.from_pandas(df)
                if i == 0:
                    pq.write_table(table, output_file, compression='snappy')
                else:
                    with pq.ParquetWriter(output_file, table.schema, compression='snappy') as writer:
                        writer.write_table(table)

            logger.info(f"已写入 {min(i + chunk_size, num_rows)} / {num_rows} 行")

        logger.info(f"✅ 数据已成功写入：{os.path.abspath(output_file)}")

    except Exception as e:
        logger.error(f"❌ 数据生成失败：{e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="生成大规模模拟数据")
    parser.add_argument('--rows', type=int, default=1_000_000, help='总行数') # 默认生成 1 亿行数据
    parser.add_argument('--chunk', type=int, default=100_000, help='每块大小') # 默认每块 100 000 行
    # parser.add_argument('--output', type=str, default='large_dataset.csv', help='输出文件路径')
    parser.add_argument('--output', type=str, default='large_dataset.parquet', help='输出文件路径')

    args = parser.parse_args()

    generate_mock_data(
        num_rows=args.rows,
        chunk_size=args.chunk,
        output_file=args.output
    )
