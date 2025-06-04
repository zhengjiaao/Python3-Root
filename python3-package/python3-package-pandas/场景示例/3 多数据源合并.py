import pandas as pd

def create_sales_data():
    return pd.DataFrame({
        '订单ID': [101, 102, 103, 104],
        '客户': ['Alice', 'Bob', 'Charlie', 'David'],
        '产品': ['A', 'B', 'C', 'A'],
        '数量': [2, 1, 3, 2],
        '总价': [50.0, 30.0, 90.0, 40.0]
    })

def create_products():
    return pd.DataFrame({
        '产品': ['A', 'B', 'C'],
        '类别': ['电子', '家居', '食品'],
        '成本价': [7.5, 15.0, 10.0]
    })

def create_customers():
    return pd.DataFrame({
        '客户': ['Alice', 'Bob', 'Charlie', 'David'],
        '等级': ['VIP', '普通', '普通', 'VIP'],
        '地区': ['北京', '上海', '广州', '深圳']
    })

if __name__ == '__main__':
    df = create_sales_data()
    products = create_products()
    customers = create_customers()

    try:
        # 合并销售与产品信息
        merged_df = pd.merge(df, products, on='产品', how='left')

        # 合并客户信息
        final_df = pd.merge(merged_df, customers, on='客户', how='left')

        # 处理可能的缺失值
        final_df['成本价'] = final_df['成本价'].fillna(0)
        final_df['数量'] = final_df['数量'].fillna(0)

        # 计算利润
        final_df['利润'] = final_df['总价'] - (final_df['成本价'] * final_df['数量'])

        # 输出结果
        result = final_df[['订单ID', '客户', '产品', '数量', '总价', '利润', '地区']]
        print("\n合并后完整数据:")
        print(result.sort_values(by='利润', ascending=False))

    except KeyError as e:
        print(f"缺少必要列: {e}")
