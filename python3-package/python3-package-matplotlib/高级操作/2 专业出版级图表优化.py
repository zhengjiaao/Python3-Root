import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def setup_latex_rendering():
    """
    配置LaTeX渲染设置，用于生成高质量数学公式
    需要系统安装了LaTeX环境
    """
    # plt.rcParams.update({
    #     "text.usetex": True,  # 启用LaTeX渲染
    #     "font.family": "serif",  # 使用衬线字体
    #     "font.serif": ["Computer Modern Serif"],  # 使用LaTeX的Computer Modern字体
    # })

    # 改为使用普通字体设置, 不需要系统安装了LaTeX环境
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "SimHei"],  # 使用系统中文字体
        "font.size": 12,
        "axes.unicode_minus": False  # 正常显示负号
    })

def create_sample_plot():
    """
    创建示例图表用于演示出版级格式设置
    返回图表和坐标轴对象
    """
    fig, ax = plt.subplots()
    
    # 生成示例数据
    x = np.linspace(0, 10, 100)
    y = np.sin(x) * 1e6  # 模拟百万级数据
    
    # 绘制曲线
    ax.plot(x, y, label=r"$y = \sin(x) \times 10^6$")
    
    return fig, ax

def millions_formatter(x, pos):
    """
    自定义Y轴刻度格式化函数
    将数值转换为百万(M)单位表示
    """
    return f'${x/1e6:.1f}M$'

def add_publication_elements(ax):
    """
    为图表添加适合出版的元素
    """
    # 添加注释
    ax.annotate('关键点', xy=(3, 0.5e6), xytext=(4, 0.8e6),
                arrowprops=dict(facecolor='black', shrink=0.05),
                fontsize=12)
    
    # 设置标题和标签
    ax.set_title(r"数学公式示例: $E = mc^2$ 和 $y = \sin(x)$")
    ax.set_xlabel("X 轴 (单位)")
    ax.set_ylabel("Y 轴 (百万单位)")
    
    # 设置自定义刻度格式
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    
    # 显示图例
    ax.legend()

def save_figures(fig):
    """
    保存图表到不同格式，适用于出版需求
    """
    # 保存为矢量图形PDF（推荐用于论文发表）
    fig.savefig('publication_quality.pdf', bbox_inches='tight')
    
    # 保存为高分辨率PNG（适用于无法使用矢量图的情况）
    fig.savefig('high_res.png', dpi=300, bbox_inches='tight')

def main():
    """主函数，创建并配置出版级图表"""
    try:
        # 设置LaTeX渲染（需要已安装LaTeX）
        setup_latex_rendering()
    except Exception as e:
        print(f"警告：无法启用LaTeX渲染 ({e})")
        print("继续使用默认渲染器")
    
    # 创建示例图表
    fig, ax = create_sample_plot()
    
    # 添加出版要素
    add_publication_elements(ax)
    
    # 保存图表
    save_figures(fig)
    
    # 显示图表
    plt.show()

if __name__ == "__main__":
    main()
