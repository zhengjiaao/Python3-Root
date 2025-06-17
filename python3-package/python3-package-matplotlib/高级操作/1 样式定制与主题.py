import matplotlib.pyplot as plt

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def apply_custom_style():
    """
    应用自定义样式设置
    可以切换不同的内置样式，并自定义字体、颜色、布局等
    """
    # 使用内置样式
    # 可选样式: 'seaborn', 'bmh', 'dark_background', 'ggplot'
    plt.style.use('ggplot')
    
    # 自定义样式设置
    plt.rcParams.update({
        # 字体设置
        'font.size': 12,              # 全局字体大小
        'font.family': 'serif',       # 字体类型
        
        # 坐标轴设置
        'axes.labelsize': 14,         # 坐标轴标签大小
        'axes.titlesize': 16,         # 子图标题大小
        'axes.grid': True,            # 显示网格
        
        # 刻度设置
        'xtick.labelsize': 12,        # X轴刻度标签大小
        'ytick.labelsize': 12,        # Y轴刻度标签大小
        
        # 图例设置
        'legend.fontsize': 12,        # 图例字体大小
        
        # 图形尺寸和分辨率
        'figure.figsize': (10, 6),    # 默认图形尺寸（英寸）
        'figure.dpi': 100,            # 屏幕显示分辨率
        'savefig.dpi': 300,           # 保存图片的分辨率
        
        # 网格线设置
        'grid.alpha': 0.3,            # 网格线透明度
        
        # 线条样式
        'lines.linewidth': 2,         # 折线图线条宽度
        'lines.markersize': 8         # 标记点大小
    })

def create_sample_plot():
    """
    创建示例图表，展示应用样式的效果
    """
    x = range(1, 6)
    y1 = [i**2 for i in x]
    y2 = [i**1.5 for i in x]
    
    fig, ax = plt.subplots()
    ax.plot(x, y1, 's-', label='平方')
    ax.plot(x, y2, 'o--', label='1.5次方')
    
    ax.set_title('样式测试图')
    ax.set_xlabel('X值')
    ax.set_ylabel('Y值')
    ax.legend()
    
    return fig

def main():
    """主函数，应用样式并生成示例图表"""
    # 应用自定义样式
    apply_custom_style()
    
    # 创建示例图表
    fig = create_sample_plot()
    
    # 保存图表
    fig.savefig('styled_plot.png', bbox_inches='tight')
    
    # 显示图表
    plt.show()

if __name__ == "__main__":
    main()
