import pandas as pd
import numpy as np
import os

def generate_simulated_data(output_file='your_data.csv', num_rows=1000):
    """
    生成包含缺失值的模拟数据并保存为 CSV 文件

    参数:
        output_file (str): 输出文件路径
        num_rows (int): 生成的数据行数
    """
    np.random.seed(42)  # 固定随机种子以保证结果可复现

    # 构建原始数据（col1 数值型，col2 类别型）
    data = {
        'col1': np.random.normal(loc=5, scale=2, size=num_rows),
        'col2': np.random.choice(['A', 'B', 'C', np.nan], size=num_rows),
    }

    # 引入缺失值
    data['col1'][np.random.choice(num_rows, int(num_rows * 0.1), replace=False)] = np.nan
    data['col2'][np.random.choice(num_rows, int(num_rows * 0.15), replace=False)] = np.nan

    # 转换为 DataFrame 并保存
    df_simulated = pd.DataFrame(data)
    df_simulated.to_csv(output_file, index=False)

    print(f"模拟数据已保存至 {os.path.abspath(output_file)}")

if __name__ == "__main__":
    generate_simulated_data()
