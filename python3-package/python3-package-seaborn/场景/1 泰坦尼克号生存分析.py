import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os


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


# 加载数据集
def load_data():
    return sns.load_dataset("titanic")


# 绘制性别与生存率关系图
def plot_survival_by_sex(df, output_path=None):
    plt.figure(figsize=(10, 4))
    plt.subplot(121)
    sns.countplot(x="sex", hue="survived", data=df, palette="RdBu_r")
    plt.title("性别 vs 生存率")
    plt.xlabel("性别")
    plt.ylabel("人数")
    if output_path:
        plt.savefig(os.path.join(output_path, "gender_survival.png"), dpi=300, bbox_inches='tight')


# 绘制舱位等级与年龄分布图（带生存状态）
def plot_age_by_class(df, output_path=None):
    plt.subplot(122)
    sns.violinplot(x="class", y="age", hue="survived", data=df, split=True)
    plt.title("舱位等级 vs 年龄分布")
    plt.xlabel("舱位等级")
    plt.ylabel("年龄")
    if output_path:
        plt.savefig(os.path.join(output_path, "class_age_distribution.png"), dpi=300, bbox_inches='tight')


# 分面网格：舱位等级 + 是否独行 对生存率的影响
def plot_facet_grid(df, output_path=None):
    g = sns.FacetGrid(df, col="alone", row="pclass", margin_titles=True)
    g.map_dataframe(sns.countplot, x="survived", hue="sex", palette="viridis")
    g.add_legend()
    g.set_axis_labels("生存状态", "人数")
    plt.suptitle("舱位等级+独行状态对生存率的影响", y=1.05)
    if output_path:
        plt.savefig(os.path.join(output_path, "facet_survival_analysis.png"), dpi=300, bbox_inches='tight')


# 将所有图表导出为一个 PDF 报告
def export_to_pdf(figures, output_file="titanic_analysis_report.pdf"):
    with PdfPages(output_file) as pdf:
        for fig in figures:
            pdf.savefig(fig, bbox_inches='tight')
    print(f"📄 图表已导出为 PDF：{output_file}")


# 主程序入口
def main(save_dir="output", export_pdf=True):
    # 创建输出目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 设置字体与主题
    set_chinese_font()
    # set_seaborn_theme()

    # 加载数据
    df = load_data()

    # 图表集合
    figures = []

    # 图表 1：性别与生存率
    plt.figure(figsize=(10, 4))
    plot_survival_by_sex(df, save_dir)
    figures.append(plt.gcf())

    # 图表 2：舱位等级与年龄分布
    plt.figure(figsize=(10, 4))
    plot_age_by_class(df, save_dir)
    figures.append(plt.gcf())

    # 图表 3：分面网格分析
    plt.figure(figsize=(10, 6))
    plot_facet_grid(df, save_dir)
    figures.append(plt.gcf())

    # 导出为 PDF 报告
    if export_pdf:
        export_to_pdf(figures, os.path.join(save_dir, "titanic_analysis_report.pdf"))

    # 显示图表
    # plt.show()


# CLI 入口点
if __name__ == "__main__":
    main(save_dir="titanic_output", export_pdf=True)
