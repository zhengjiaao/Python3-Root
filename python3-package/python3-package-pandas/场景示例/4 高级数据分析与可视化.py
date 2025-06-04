import matplotlib.pyplot as plt
import pandas as pd
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def save_plot(title, filename):
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    print(f"📈 图表已保存至：{os.path.abspath(filename)}")
    plt.close()

# 场景：销售数据可视化与统计报告
if __name__ == '__main__':
    # 模拟数据
    daily_sales = pd.DataFrame({
        '日期': pd.date_range(start='2023-01-01', periods=7),
        '总销售额': [200, 220, 250, 230, 300, 280, 310]
    })

    final_df = pd.DataFrame({
        '产品': ['A', 'B', 'A', 'C', 'B', 'C'],
        '数量': [2, 3, 1, 4, 2, 5],
        '利润': [10, 15, 5, 20, 10, 25],
        '等级': ['VIP', '普通', '普通', 'VIP', '普通', 'VIP']
    })

    # 1. 销售额趋势图
    plt.figure(figsize=(10, 6))
    plt.plot(daily_sales['日期'], daily_sales['总销售额'], marker='o')
    plt.xlabel('日期')
    plt.ylabel('销售额')
    plt.grid(True)
    save_plot('每日销售额趋势', 'daily_sales.png')

    # 2. 产品销量饼图
    product_sales = final_df.groupby('产品')['数量'].sum()
    plt.figure(figsize=(8, 8))
    product_sales.plot.pie(
        autopct='%1.1f%%',
        startangle=90,
        labels=product_sales.index,
        colors=['#FF9999', '#66B2FF', '#99FF99'],
        shadow=True
    )
    plt.ylabel('')
    save_plot('产品销量占比', 'product_sales_pie.png')

    # 3. 客户等级利润分析
    vip_profit = final_df[final_df['等级'] == 'VIP']['利润'].sum()
    regular_profit = final_df[final_df['等级'] == '普通']['利润'].sum()

    plt.figure(figsize=(6, 6))
    plt.bar(['VIP客户', '普通客户'], [vip_profit, regular_profit], color=['gold', 'silver'])
    plt.ylabel('利润总额')
    save_plot('不同等级客户利润贡献', 'customer_profit.png')
