from sklearn.linear_model import LinearRegression
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 场景：使用历史销售数据进行简单预测
if __name__ == '__main__':
    # 1. 创建扩展数据集（模拟30天数据）
    dates = pd.date_range(start='2023-01-01', periods=30)
    sales_data = {
        '日期': dates,
        '销售额': np.random.randint(1000, 5000, size=30) *
                  [1 + 0.05 * i for i in range(30)]  # 添加增长趋势
    }
    sales_df = pd.DataFrame(sales_data)

    # 数据平滑处理（移动平均）
    sales_df['销售额'] = sales_df['销售额'].rolling(window=3).mean().fillna(sales_df['销售额'])

    # 2. 准备预测数据
    sales_df['天数'] = (sales_df['日期'] - sales_df['日期'].min()).dt.days

    # 3. 训练线性回归模型
    model = LinearRegression()
    model.fit(sales_df[['天数']], sales_df['销售额'])

    # 4. 预测未来7天
    # future_days = np.array(range(30, 37)).reshape(-1, 1)
    # future_sales = model.predict(future_days)
    future_days_df = pd.DataFrame({'天数': range(30, 37)})
    future_sales = model.predict(future_days_df)

    # 5. 创建结果DataFrame
    future_dates = pd.date_range(start=sales_df['日期'].max() + pd.Timedelta(days=1), periods=7)
    forecast_df = pd.DataFrame({
        '日期': future_dates,
        '预测销售额': future_sales.round(2),
        '类型': '预测'
    })

    # 合并历史数据
    history_df = sales_df[['日期', '销售额']].rename(columns={'销售额': '预测销售额'})
    history_df['类型'] = '历史'

    combined_df = pd.concat([history_df, forecast_df])

    # 6. 可视化结果
    plt.figure(figsize=(12, 6))
    for label, group in combined_df.groupby('类型'):
        plt.plot(group['日期'], group['预测销售额'],
                 label=label,
                 marker='o' if label == '历史' else 's',
                 linestyle='--' if label == '预测' else '-')

    plt.title('销售额历史数据与预测')
    plt.xlabel('日期')
    plt.ylabel('销售额')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.axvline(x=sales_df['日期'].max(), color='gray', linestyle='--', linewidth=1)
    plt.tight_layout()
    plt.savefig('sales_forecast.png')
    plt.close()

    print(f"\n📈 预测图表已保存至：{os.path.abspath('sales_forecast.png')}")
    print("\n📅 未来7天销售额预测:")
    print(forecast_df[['日期', '预测销售额']])
