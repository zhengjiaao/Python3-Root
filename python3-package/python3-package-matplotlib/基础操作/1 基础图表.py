import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def create_line_plot(ax):
    """
    创建折线图
    显示正弦和余弦函数曲线
    """
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)

    ax.plot(x, y1, 'b-', linewidth=2, label='sin(x)')
    ax.plot(x, y2, 'r--', linewidth=2, label='cos(x)')
    ax.set_title('三角函数曲线')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    ax.set_ylim(-1.2, 1.2)

def create_scatter_plot(ax):
    """
    创建散点图
    显示随机数据点及其回归线
    """
    np.random.seed(42)
    x = np.random.randn(100)
    y = 2 * x + np.random.randn(100)

    ax.scatter(x, y, c=np.abs(x), cmap='viridis', alpha=0.7, s=50, edgecolors='black')
    ax.set_title('随机散点图')
    ax.set_xlabel('X值')
    ax.set_ylabel('Y值')
    ax.grid(True, linestyle=':')

    # 添加回归线
    m, b = np.polyfit(x, y, 1)
    ax.plot(x, m*x + b, 'r-', linewidth=2)

def create_bar_chart(ax):
    """
    创建柱状图
    显示不同水果的销售量
    """
    categories = ['苹果', '香蕉', '橙子', '葡萄', '西瓜']
    sales = [45, 30, 55, 25, 40]

    bars = ax.bar(categories, sales, color=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#C2C2F0'])
    ax.set_title('水果销售额')
    ax.set_ylabel('销量 (公斤)')
    ax.grid(axis='y', alpha=0.3)

    # 添加数据标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height}', ha='center', va='bottom', fontsize=10)

def create_horizontal_bar_chart(ax):
    """
    创建水平条形图
    显示国家GDP排名
    """
    countries = ['美国', '中国', '日本', '德国', '英国']
    gdp = [22.94, 16.86, 5.08, 4.26, 3.19]  # 万亿美元

    ax.barh(countries, gdp, color='skyblue', edgecolor='black')
    ax.set_title('2023年GDP排名 (万亿美元)')
    ax.set_xlabel('GDP')
    ax.invert_yaxis()  # 从上到下排序
    ax.grid(axis='x', alpha=0.3)

def main():
    """主函数，创建所有图表并显示"""
    # 创建画布和子图布局
    fig, axs = plt.subplots(2, 2, figsize=(12, 8), dpi=100)
    fig.suptitle('基础图表示例', fontsize=16, fontweight='bold')

    # 创建各个图表
    create_line_plot(axs[0, 0])
    create_scatter_plot(axs[0, 1])
    create_bar_chart(axs[1, 0])
    create_horizontal_bar_chart(axs[1, 1])

    # 调整布局
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为标题留出空间

    # 保存和显示图表
    plt.savefig('basic_plots.png', bbox_inches='tight')
    plt.show()

# 基础图表（折线图、散点图、柱状图）
if __name__ == "__main__":
    main()
