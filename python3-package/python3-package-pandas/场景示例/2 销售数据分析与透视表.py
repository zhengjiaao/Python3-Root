import pandas as pd
import matplotlib.pyplot as plt
import os

# 方法一：设置 matplotlib 支持中文字体（推荐）
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

def load_data():
    """创建模拟清洗后的销售数据"""
    data = {
        '订单ID': [1001, 1002, 1003, 1004, 1005, 1006],
        '客户': ['Alice', 'Bob', 'Charlie', '未知客户', 'Alice', 'David'],
        '产品': ['A', 'B', 'A', 'C', 'A', 'B'],
        '数量': [3, 5, 2, 0, 4, 3],
        '单价': [10.5, 20.0, 10.5, 15.0, 10.5, 20.0],
        '日期': pd.to_datetime(['2023-01-15', '2023-01-15', '2023-01-16',
                               '2023-01-17', '2023-01-15', '2023-01-18']),
        '总价': [31.5, 100.0, 21.0, 0.0, 42.0, 60.0]
    }
    return pd.DataFrame(data)

def analyze_by_product(df):
    """按产品维度统计销量、均价、订单数"""
    result = df.groupby('产品', as_index=False).agg(
        总销量=('数量', 'sum'),
        平均单价=('单价', 'mean'),
        订单数量=('订单ID', 'count')
    )
    return result

def create_pivot_table(df):
    """创建客户-产品矩阵透视表"""
    pivot = pd.pivot_table(
        df,
        values='数量',
        index='客户',
        columns='产品',
        aggfunc='sum',
        fill_value=0
    )
    return pivot

def analyze_daily_sales(df):
    """按天分析总销售额和订单量"""
    daily = df.groupby('日期', as_index=False).agg(
        总销售额=('总价', 'sum'),
        订单量=('订单ID', 'count')
    ).sort_values('日期')
    return daily

def visualize_daily_sales(daily_df):
    """绘制每日销售趋势图"""
    # 设置中文字体
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False

    plt.figure(figsize=(10, 5))
    plt.plot(daily_df['日期'], daily_df['总销售额'], marker='o', linestyle='-')
    plt.title("每日销售趋势")
    plt.xlabel("日期")
    plt.ylabel("总销售额 (元)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("每日销售趋势.png")
    print("📊 图表已保存：每日销售趋势.png")

def export_to_excel(results):
    """将多个分析结果写入同一个 Excel 文件的不同 Sheet"""
    output_path = "销售分析报告.xlsx"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df in results.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"✅ 分析结果已导出至：{output_path}")

def main():
    # 1. 加载或生成数据
    df = load_data()
    print("📄 原始数据预览:")
    print(df.head())

    # 2. 分析逻辑
    product_analysis = analyze_by_product(df)
    pivot_table = create_pivot_table(df)
    daily_sales = analyze_daily_sales(df)

    # 3. 打印分析结果
    print("\n📈 按产品分析:")
    print(product_analysis)

    print("\n🧮 客户-产品透视表:")
    print(pivot_table)

    print("\n📅 每日销售趋势:")
    print(daily_sales)

    # 4. 可视化
    visualize_daily_sales(daily_sales)

    # 5. 导出到 Excel
    export_results = {
        "产品分析": product_analysis,
        "客户产品矩阵": pivot_table.reset_index(),
        "每日销售趋势": daily_sales
    }

    export_to_excel(export_results)

if __name__ == '__main__':
    main()
