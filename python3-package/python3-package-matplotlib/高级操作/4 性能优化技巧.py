import numpy as np
import matplotlib.pyplot as plt

def generate_data(num_points=1000000):
    """
    生成示例数据集
    """
    x = np.linspace(0, 10, num_points)
    y = np.sin(x)
    return x, y

def optimize_large_dataset_plot():
    """
    展示大数据集的高效绘图方法
    """
    # 生成大数据集（100万个点）
    x, y = generate_data()
    
    # 使用低级接口进行高效绘图
    fig, ax = plt.subplots()
    ax.plot(x, y, '-', linewidth=0.5, alpha=0.7)  # 细线和透明度提高性能
    
    ax.set_title('大数据集高效绘制 (100万数据点)')
    ax.set_xlabel('x')
    ax.set_ylabel('sin(x)')
    
    return fig, ax

def save_vector_graphics(fig, filename='vector_plot.svg'):
    """
    使用矢量格式保存简单图形
    SVG格式适合线条图和包含少量实体的图表
    """
    fig.savefig(filename)  # 保存为SVG格式

def reduce_sampling_rate_for_3d():
    """
    为复杂3D图形降低采样率
    原始建议：使用0.01步长，但会导致大量计算
    优化后：使用0.1步长提升性能
    """
    X = np.arange(-5, 5, 0.1)  # 替代0.01
    Y = np.arange(-5, 5, 0.1)
    X, Y = np.meshgrid(X, Y)
    Z = np.sin(np.sqrt(X**2 + Y**2))
    
    # 创建3D图表
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, cmap='viridis', linewidth=0.5, antialiased=True)
    
    ax.set_title('低采样率3D曲面图')
    return fig, ax

def batch_rendering_mode(enable=False):
    """
    控制交互模式
    在批量渲染或保存图表时关闭交互模式可以提高性能
    """
    if enable:
        plt.ioff()  # 关闭交互模式
    else:
        plt.ion()  # 开启交互模式

def setup_chinese_font():
    """
    设置中文字体支持
    """
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号显示为方块

def main():
    """主函数，协调各种性能优化技术"""
    print("开始展示Matplotlib性能优化技巧...")

    # 设置中文字体
    setup_chinese_font()
    
    # 1. 大数据集优化
    print("1/4 绘制大数据集（100万数据点）...")
    fig1, ax1 = optimize_large_dataset_plot()
    
    # 2. 矢量图形输出
    print("2/4 保存矢量图形...")
    save_vector_graphics(fig1)
    
    # 3. 3D图形优化
    print("3/4 创建低采样率3D图形...")
    batch_rendering_mode(enable=True)  # 开始批量处理
    fig2, ax2 = reduce_sampling_rate_for_3d()
    fig2.suptitle('性能优化的3D曲面图', fontsize=16)
    
    # 4. 批量渲染模式演示
    print("4/4 演示批量渲染模式...")
    fig2.savefig('optimized_3d_plot.png')
    batch_rendering_mode(enable=False)  # 结束批量处理
    
    # 显示所有图表
    plt.show()
    print("性能优化演示完成！")

if __name__ == "__main__":
    main()
