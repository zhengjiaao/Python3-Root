import numpy as np
import pandas as pd
import os

def generate_large_data(file_path: str, num_rows: int = 10_000_000):
    """
    生成大型数据集用于测试
    :param file_path: 输出文件路径
    :param num_rows: 行数
    """
    data = {
        "user_id": np.random.randint(1, 100_000, size=num_rows),
        "age": np.random.randint(18, 90, size=num_rows),
        "city": np.random.choice(["Beijing", "Shanghai", "Guangzhou", "Shenzhen"], size=num_rows),
        "income": np.round(np.random.normal(5000, 2000, size=num_rows), 2),
        "purchases": np.random.poisson(3, size=num_rows)
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"✅ 已生成 {num_rows} 行数据，保存至：{file_path}")

# 模拟数据生成器（支持 1GB~100GB）
if __name__ == "__main__":
    # 示例：生成约 1GB 的数据（约 1000万行）
    generate_large_data("data_10m.csv", num_rows=10_000_000)  # ~1GB
    # 可选：生成更大数据集
    # generate_large_data("data_100m.csv", num_rows=100_000_000)  # ~10GB
