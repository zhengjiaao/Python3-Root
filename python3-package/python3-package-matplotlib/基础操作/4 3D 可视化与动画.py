import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import cm

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def create_3d_surface_plot(ax):
    """
    创建3D曲面图并添加等高线和样式设置
    """
    # 生成数据网格
    X = np.arange(-5, 5, 0.25)
    Y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X**2 + Y**2)  # 计算半径
    Z = np.sin(R)  # 计算高度值

    # 绘制3D曲面
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis,
                          linewidth=0, antialiased=True,
                          alpha=0.7, rstride=1, cstride=1)

    # 添加颜色条
    plt.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Z值')

    # 设置标签和标题
    ax.set_xlabel('X轴')
    ax.set_ylabel('Y轴')
    ax.set_zlabel('Z轴')
    ax.set_title('三维曲面图: z = sin(sqrt(x^2 + y^2))', fontsize=14)

    # 添加等高线投影
    cset = ax.contour(X, Y, Z, zdir='z', offset=-1.5, cmap=cm.coolwarm)
    cset = ax.contour(X, Y, Z, zdir='x', offset=-6, cmap=cm.coolwarm)
    cset = ax.contour(X, Y, Z, zdir='y', offset=6, cmap=cm.coolwarm)

    # 调整视角
    ax.view_init(elev=30, azim=45)

    return surf

def update(frame, ax):
    """
    动画更新函数，旋转视角
    """
    ax.view_init(elev=30, azim=frame)
    return ax.figure,

def main():
    """主函数，创建3D可视化并生成旋转动画"""
    # 创建画布
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.suptitle('3D可视化与动画', fontsize=18, fontweight='bold')

    # 创建3D曲面图
    create_3d_surface_plot(ax)

    # 创建动画
    ani = FuncAnimation(fig, update, frames=np.arange(0, 360, 2),
                       interval=50, blit=True, fargs=(ax,))

    # 调整布局
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为标题留出空间

    # 保存静态图片
    plt.savefig('3d_plot.png', dpi=150, bbox_inches='tight')

    # 保存动画（需要Pillow库）
    try:
        ani.save('3d_rotation.gif', writer='pillow', fps=20, dpi=100)
        print("动画已成功保存为3d_rotation.gif")
    except Exception as e:
        print(f"保存动画时发生错误: {e}")
        print("请先安装Pillow库: pip install pillow")

    # 显示图形
    plt.show()

# 3D 可视化与动画
if __name__ == "__main__":
    main()
