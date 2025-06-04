import pandas as pd
import numpy as np

# 场景：清洗销售数据中的异常值、缺失值和重复项

if __name__ == '__main__':

    # 创建模拟销售数据
    data = {
        '订单ID': [1001, 1002, 1003, 1004, 1005, 1006],
        '客户': ['Alice', 'Bob', 'Charlie', np.nan, 'Alice', 'David'],
        '产品': ['A', 'B', 'A', 'C', 'A', 'B'],
        '数量': [3, 5, 2, -1, 4, 3],
        '单价': [10.5, 20.0, 10.5, 15.0, 10.5, 20.0],
        '日期': ['2023-01-15', '2023-01-15', '2023-01-16', '2023-01-17', '2023-01-15', '2023-01-18']
    }
    df = pd.DataFrame(data)

    print("原始数据:")
    print(df)

    # 1. 处理缺失值
    df['客户'] = df['客户'].fillna('未知客户')

    # 2. 处理异常值（数量不能为负数）
    df.loc[df['数量'] < 0, '数量'] = 0

    # 3. 添加计算列
    df['总价'] = df['数量'] * df['单价']

    # 4. 日期处理
    df['日期'] = pd.to_datetime(df['日期'])
    df['星期'] = df['日期'].dt.day_name()

    # 5. 删除重复订单（保留第一条记录）
    df.drop_duplicates(subset=['客户', '日期'], keep='first', inplace=True)

    print("\n清洗后数据:")
    print(df)