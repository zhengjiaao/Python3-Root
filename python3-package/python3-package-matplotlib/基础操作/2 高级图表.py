import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def create_histogram(ax):
    """
    创建直方图，比较两个数据集的分布
    """
    # 生成示例数据
    np.random.seed(42)
    data1 = np.random.normal(50, 10, 1000)  # 数据集1: 均值50，标准差10
    data2 = np.random.normal(70, 5, 800)    # 数据集2: 均值70，标准差5

    # 绘制直方图
    ax.hist(data1, bins=30, alpha=0.7, color='blue', label='数据集1')
    ax.hist(data2, bins=30, alpha=0.7, color='red', label='数据集2')

    # 添加统计信息
    ax.axvline(np.mean(data1), color='blue', linestyle='dashed', linewidth=1)
    ax.axvline(np.mean(data2), color='red', linestyle='dashed', linewidth=1)
    ax.text(40, 100, f'均值: {np.mean(data1):.1f}', color='blue')
    ax.text(75, 100, f'均值: {np.mean(data2):.1f}', color='red')

    # 设置图表属性
    ax.set_title('数据分布直方图')
    ax.set_xlabel('数值')
    ax.set_ylabel('频数')
    ax.legend()
    ax.grid(True, alpha=0.3)

def create_boxplot(ax):
    """
    创建箱线图，展示多组数据的分布特征
    """
    # 生成示例数据：不同标准差的正态分布数据
    data = [np.random.normal(0, std, 100) for std in range(1, 5)]

    # 绘制箱线图
    ax.boxplot(data, patch_artist=True,
              boxprops=dict(facecolor='lightblue', color='blue'),
              whiskerprops=dict(color='black'),
              capprops=dict(color='black'),
              medianprops=dict(color='red'))

    # 设置图表属性
    ax.set_title('多组数据箱线图')
    ax.set_xticklabels(['组1', '组2', '组3', '组4'])
    ax.set_ylabel('数值')
    ax.grid(True, axis='y', alpha=0.3)

def create_pie_chart(ax):
    """
    创建饼图，展示分类数据的比例关系
    """
    # 示例数据：月度支出分类
    categories = ['房租', '餐饮', '交通', '娱乐', '购物', '其他']
    expenses = [2500, 1800, 800, 700, 1200, 1000]
    explode = (0.1, 0, 0, 0, 0, 0)  # 突出显示房租
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6']

    # 绘制饼图
    ax.pie(expenses, explode=explode, labels=categories, colors=colors,
           autopct='%1.1f%%', startangle=90, shadow=True,
           textprops={'fontsize': 9})

    # 设置图表属性
    ax.set_title('月度支出分布')
    ax.axis('equal')  # 确保饼图是圆形

def create_heatmap(ax):
    """
    创建热力图，展示二维数据矩阵的强度变化
    """
    # 生成示例数据
    np.random.seed(10)
    data = np.random.rand(10, 12)  # 10行12列的随机数据

    # 定义坐标轴标签
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    years = [f'{2010+i}' for i in range(10)]  # 2010-2019年

    # 绘制热力图
    heatmap = ax.imshow(data, cmap='viridis', aspect='auto')

    # 设置坐标轴标签
    ax.set_xticks(np.arange(len(months)))
    ax.set_yticks(np.arange(len(years)))
    ax.set_xticklabels(months)
    ax.set_yticklabels(years)

    # 添加数值标签
    for i in range(len(years)):
        for j in range(len(months)):
            text = ax.text(j, i, f'{data[i, j]:.2f}',
                          ha="center", va="center", color="w", fontsize=8)

    # 添加颜色条
    cbar = fig.colorbar(heatmap, ax=ax)
    cbar.set_label('数值强度', rotation=270, labelpad=15)

    # 设置图表属性
    ax.set_title('月度数据热力图')

def main():
    """主函数，创建所有图表并显示"""
    # 创建画布和子图布局
    global fig  # 将fig声明为全局变量，以便在create_heatmap中使用
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('高级图表示例', fontsize=16, fontweight='bold')

    # 创建各个图表
    create_histogram(axs[0, 0])
    create_boxplot(axs[0, 1])
    create_pie_chart(axs[1, 0])
    create_heatmap(axs[1, 1])

    # 调整布局并保存
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为标题留出空间
    plt.savefig('advanced_plots.png', dpi=150, bbox_inches='tight')
    plt.show()

# 高级图表（直方图、箱线图、饼图）
if __name__ == "__main__":
    main()
