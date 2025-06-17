from dask import delayed, compute
from dask_ml.impute import SimpleImputer
import pandas as pd
from dask.distributed import Client
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@delayed
def impute_mean(data):
    """对数据进行均值填充"""
    return SimpleImputer(strategy='mean').fit_transform(data)

@delayed
def impute_freq(data):
    """对数据进行众数填充"""
    return SimpleImputer(strategy='most_frequent').fit_transform(data)

def load_data(file_path):
    """加载数据"""
    try:
        df = pd.read_csv(file_path)
        logger.info("数据加载成功。")
        return df
    except FileNotFoundError:
        logger.error("文件未找到，请检查文件路径。")
        raise
    except Exception as e:
        logger.error(f"加载数据时发生错误: {e}")
        raise

def process_data(df, col1, col2):
    """处理数据"""
    if col1 in df.columns and col2 in df.columns:
        # 并行执行两个填充任务
        result_mean = impute_mean(df[[col1]])
        result_freq = impute_freq(df[[col2]])

        # 合并结果
        combined = delayed(pd.concat)([result_mean, result_freq], axis=1)

        # 执行计算
        final_result = compute(combined)[0]

        logger.info("填充完成，合并结果已生成。")
        return final_result
    else:
        raise ValueError(f"DataFrame 中缺少 {col1} 或 {col2} 列，请检查输入数据。")

if __name__ == "__main__":
    file_path = 'your_data.csv'  # 替换为实际文件路径
    col1 = 'col1'
    col2 = 'col2'

    # client = Client()  # 启动分布式调度器
    # client = Client(n_workers=2)  # 启动分布式调度器

    try:
        df = load_data(file_path)
        final_result = process_data(df, col1, col2)
        print(final_result.head())  # 输出前几行查看结果
    except Exception as e:
        logger.error(f"主程序中发生错误: {e}")
    # finally:
        # client.close()
