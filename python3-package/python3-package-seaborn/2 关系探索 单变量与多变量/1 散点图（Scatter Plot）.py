import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


# 设置中文字体和负号显示正常
def set_chinese_font():
    try:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        print("⚠️ 中文字体设置失败，使用默认字体")
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']


# 设置 Seaborn 主题样式
def set_seaborn_theme():
    sns.set_theme(style="whitegrid")


# 构建模拟数据集
def build_mock_data():
    return pd.DataFrame({
        "GDP": [2.7, 1.8, 1.6],
        "Population": [39.3, 29.7, 19.5],
        "Region": ["West", "South", "Northeast"],
        "Importance": [5, 3, 4]
    })


# 绘制散点图（支持颜色与大小映射）
def plot_scatter(df, x_col="GDP", y_col="Population",
                 hue_col="Region", size_col="Importance",
                 title="GDP vs 人口（按区域和重要性）",
                 save_path=None):
    """
    绘制多变量散点图
    :param df: 输入 DataFrame
    :param x_col: X 轴列名
    :param y_col: Y 轴列名
    :param hue_col: 分类列名（颜色映射）
    :param size_col: 数值列名（点大小映射）
    :param title: 图表标题
    :param save_path: 输出路径，如不提供则只显示
    """
    plt.figure(figsize=(8, 6))
    scatter = sns.scatterplot(
        data=df,
        x=x_col,
        y=y_col,
        hue=hue_col,
        size=size_col,
        sizes=(50, 200),
        alpha=0.7,
        legend="auto"
    )

    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.legend(title="类别")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 图表已保存至：{save_path}")

    plt.tight_layout()
    return plt


# 主程序入口
def main():
    # 设置字体与主题
    set_chinese_font()
    # set_seaborn_theme() # 会导致字体显示异常

    # 生成或加载数据
    df = build_mock_data()

    # 绘图
    plotter = plot_scatter(
        df,
        x_col="GDP",
        y_col="Population",
        hue_col="Region",
        size_col="Importance",
        title="GDP vs 人口（按区域和重要性）",
        save_path="scatter_gdp_population.png"
    )

    # 显示图表
    plotter.show()


# CLI 入口点
if __name__ == "__main__":
    main()
