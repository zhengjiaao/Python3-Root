import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def create_stack_area_chart(ax):
    """
    创建堆叠面积图，展示产品销售额趋势
    """
    years = np.arange(2010, 2021)
    product_a = np.array([20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70])
    product_b = np.array([15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65])
    product_c = np.array([10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60])

    ax.stackplot(years, product_a, product_b, product_c,
                 labels=['产品A', '产品B', '产品C'],
                 colors=['#FF9999', '#66B2FF', '#99FF99'])

    ax.set_title('产品销售额趋势 (2010-2020)', fontsize=14)
    ax.set_xlabel('年份')
    ax.set_ylabel('销售额 (百万元)')
    ax.legend(loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_xlim(2010, 2020)


def create_radar_chart(ax):
    """
    创建雷达图，展示部门能力评估
    """
    categories = ['技术', '销售', '市场', '财务', 'HR', '研发']
    values = [0.9, 0.7, 0.8, 0.6, 0.5, 0.85]
    theta = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)

    # 闭合图形
    values = np.concatenate((values, [values[0]]))
    theta = np.concatenate((theta, [theta[0]]))

    ax.plot(theta, values, 'o-', linewidth=2)
    ax.fill(theta, values, 'b', alpha=0.2)
    ax.set_xticks(theta[:-1])
    ax.set_xticklabels(categories)
    ax.set_title('部门能力评估雷达图', fontsize=14)
    ax.set_rlabel_position(30)


def create_dual_axis_chart(ax):
    """
    创建双Y轴图，展示月度气温与降雨量关系
    """
    months = ['1月', '2月', '3月', '4月', '5月', '6月',
              '7月', '8月', '9月', '10月', '11月', '12月']
    temperature = [2.1, 3.8, 8.5, 14.3, 19.8, 23.5,
                   26.1, 25.3, 20.9, 15.2, 8.7, 3.9]
    rainfall = [42, 38, 45, 58, 82, 105, 132, 127, 89, 64, 57, 46]

    color1 = 'tab:red'
    ax.plot(months, temperature, color=color1, marker='o', linewidth=2)
    ax.set_xlabel('月份')
    ax.set_ylabel('温度 (°C)', color=color1)
    ax.tick_params(axis='y', labelcolor=color1)

    ax2 = ax.twinx()
    color2 = 'tab:blue'
    ax2.bar(months, rainfall, color=color2, alpha=0.4, width=0.6)
    ax2.set_ylabel('降雨量 (mm)', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    ax.set_title('2023年月度气温与降雨量', fontsize=14)
    ax.grid(True, alpha=0.3)


def create_k_line_chart(ax):
    """
    创建K线图，展示模拟股票价格走势
    """
    # 生成模拟股票数据
    np.random.seed(42)
    n = 30
    dates = pd.date_range('2023-01-01', periods=n)
    open_prices = np.cumprod(1 + np.random.normal(0.001, 0.02, n)) * 100
    high_prices = open_prices * (1 + np.abs(np.random.normal(0.01, 0.005, n)))
    low_prices = open_prices * (1 - np.abs(np.random.normal(0.01, 0.005, n)))
    close_prices = open_prices * (1 + np.random.normal(0.001, 0.015, n))

    # 绘制K线图
    for i in range(n):
        color = 'green' if close_prices[i] > open_prices[i] else 'red'

        # 绘制实体
        ax.bar(i, height=abs(close_prices[i] - open_prices[i]),
               bottom=min(open_prices[i], close_prices[i]),
               width=0.6, color=color)

        # 绘制影线
        ax.plot([i, i], [low_prices[i], high_prices[i]], color=color, linewidth=1)

    # 设置图表属性
    ax.set_title('股票K线图 (模拟数据)', fontsize=14)
    ax.set_ylabel('价格')
    ax.set_xticks(np.arange(0, n, 5))
    ax.set_xticklabels([dates[i].strftime('%m-%d') for i in range(0, n, 5)])
    ax.grid(True, linestyle='--', alpha=0.3)

    # 添加移动平均线
    sma5 = pd.Series(close_prices).rolling(window=5).mean()
    sma10 = pd.Series(close_prices).rolling(window=10).mean()
    ax.plot(np.arange(n), sma5, 'b-', linewidth=1.5, label='5日均线')
    ax.plot(np.arange(n), sma10, 'orange', linewidth=1.5, label='10日均线')
    ax.legend()


def main():
    """主函数，创建所有专业图表并显示"""
    # 创建画布和子图布局
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 2, fig, height_ratios=[1, 1, 1.5])
    fig.suptitle('专业图表组合', fontsize=18, fontweight='bold', y=0.95)

    # 创建各个图表
    create_stack_area_chart(fig.add_subplot(gs[0, :]))
    create_radar_chart(fig.add_subplot(gs[1, 0], projection='polar'))
    create_dual_axis_chart(fig.add_subplot(gs[1, 1]))
    create_k_line_chart(fig.add_subplot(gs[2, :]))

    # 调整布局并保存
    plt.tight_layout(rect=[0, 0, 1, 0.93])  # 为标题留出空间
    plt.savefig('professional_plots.png', dpi=150, bbox_inches='tight')
    plt.show()

# 多图组合与专业图表
if __name__ == "__main__":
    main()
