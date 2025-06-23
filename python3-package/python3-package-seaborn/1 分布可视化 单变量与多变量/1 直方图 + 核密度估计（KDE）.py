import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置中文字体和负号显示正常
def set_chinese_font():
    try:
        # 手动指定 SimHei 字体路径（Windows 示例）
        zh_font_path = "C:/Windows/Fonts/simhei.ttf"

        if os.path.exists(zh_font_path):
            zh_font = matplotlib.font_manager.FontProperties(fname=zh_font_path)
            plt.rcParams['font.sans-serif'] = [zh_font.get_name()]
        else:
            print(f"⚠️ 字体文件不存在：{zh_font_path}，使用备用字体 DejaVu Sans")
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

        plt.rcParams['axes.unicode_minus'] = False

    except Exception as e:
        print(f"⚠️ 设置中文字体时发生异常：{e}")
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False


# 设置 Seaborn 主题样式
def set_seaborn_theme():
    sns.set_theme(style="whitegrid")


# 生成模拟数据
def generate_mock_data(num_samples=1000):
    np.random.seed(0)
    data1 = np.random.normal(loc=0, scale=1, size=num_samples)
    data2 = np.random.normal(loc=2, scale=1.5, size=num_samples)
    return pd.DataFrame({"Group1": data1, "Group2": data2})


# 绘制直方图 + KDE 图
def plot_distribution(data, columns=None, title="多变量分布对比", output_path=None):
    """
    绘制多变量分布图（直方图 + KDE）
    :param data: 输入 DataFrame
    :param columns: 要绘制的列名列表，默认全部
    :param title: 图表标题
    :param output_path: 输出路径，如不提供则只显示
    """
    if columns is None:
        columns = data.columns.tolist()

    sns.displot(
        data=data[columns],
        kind="hist",
        bins=30,
        kde=True,
        alpha=0.5,
        palette="viridis",
        height=6,
        aspect=1.5
    )

    plt.title(title)
    plt.xlabel("数值")
    plt.ylabel("频率")
    plt.legend(title="分组")

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 图表已保存至：{output_path}")

    plt.tight_layout()
    plt.show()


# 主程序入口
def main():
    # 1. 设置字体与主题
    # set_chinese_font()
    # set_seaborn_theme()

    # 2. 生成模拟数据
    df = generate_mock_data()

    # 3. 绘图
    plot_distribution(
        data=df,
        title="多变量分布对比 - 直方图 + 核密度估计 (KDE)",
        output_path="multi_variable_distribution.png"
    )


# CLI 入口点
if __name__ == "__main__":
    main()
