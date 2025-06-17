import pandas as pd
import matplotlib.pyplot as plt

def create_sample_data():
    """
    创建示例数据集
    返回一个包含产品年度销售额的DataFrame
    """
    data = {
        'Year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        'Product_A': [20, 25, 30, 35, 40, 45, 50, 55, 60],
        'Product_B': [15, 20, 25, 30, 35, 40, 45, 50, 55],
        'Product_C': [10, 15, 20, 25, 30, 35, 40, 45, 50]
    }
    df = pd.DataFrame(data)
    df.set_index('Year', inplace=True)
    return df

def plot_sales_trend(df):
    """
    使用Pandas直接绘制产品销售趋势图
    """
    # 使用Pandas内置绘图功能
    ax = df.plot(figsize=(10, 6), style=['-o', '--s', ':^'], linewidth=2)

    # 自定义图表样式
    ax.set_title('产品年度销售额趋势', fontsize=16)
    ax.set_xlabel('年份')
    ax.set_ylabel('销售额 (百万元)')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(title='产品线', loc='upper left')

    return ax

def setup_chinese_font():
    """
    设置中文字体支持
    """
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号显示为方块

def main():
    """主函数，协调数据准备和可视化"""
    # 设置中文字体
    setup_chinese_font()

    # 创建示例数据
    df = create_sample_data()

    # 绘制图表
    ax = plot_sales_trend(df)

    # 调整布局并保存
    plt.tight_layout()
    plt.savefig('pandas_integration.png', dpi=150)

    # 显示图表
    plt.show()

if __name__ == "__main__":
    main()
