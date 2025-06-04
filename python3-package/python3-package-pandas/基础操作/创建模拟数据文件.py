import pandas as pd
import os

if __name__ == '__main__':
    # 构建示例数据
    data = {
        "产品": ["产品A", "产品B"],
        "Q1 销售额": [10000, 8000],
        "Q2 销售额": [12000, 9000],
        "Q3 销售额": [15000, 10000]
    }

    df = pd.DataFrame(data)

    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"正在将模拟数据写入目录：{current_dir}")

    # 写入两个文件
    file1 = os.path.join(current_dir, "销售报表1.xlsx")
    file2 = os.path.join(current_dir, "销售报表2.xlsx")

    df.to_excel(file1, index=False)
    df.to_excel(file2, index=False)

    print("✅ 模拟数据文件创建完成：")
    print(f" - {file1}")
    print(f" - {file2}")
