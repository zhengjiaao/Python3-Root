import os
import time
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# 设置中文字体和负号显示正常
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def measure_time(func):
    """装饰器：测量函数执行时间"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        return result, duration
    return wrapper


@measure_time
def read_with_pandas(path):
    return pd.read_csv(path)


@measure_time
def read_with_polars(path):
    return pl.read_csv(path)


@measure_time
def filter_with_pandas(df: pd.DataFrame):
    return df[df["age"] > 40]


@measure_time
def filter_with_polars(df: pl.DataFrame):
    return df.filter(pl.col("age") > 40)


@measure_time
def groupby_with_pandas(df: pd.DataFrame):
    return df.groupby("city")["income"].mean().reset_index()


@measure_time
def groupby_with_polars(df: pl.DataFrame):
    return df.group_by("city").agg(pl.col("income").mean()).to_pandas()


@measure_time
def sort_with_pandas(df: pd.DataFrame):
    return df.sort_values("income", ascending=False)


@measure_time
def sort_with_polars(df: pl.DataFrame):
    return df.sort("income", descending=True).to_pandas()


@measure_time
def write_csv_pandas(df: pd.DataFrame, path):
    df.to_csv(path, index=False)


@measure_time
def write_csv_polars(df: pl.DataFrame, path):
    df.write_csv(path)


def plot_results(results, title="性能对比"):
    """绘制性能对比图"""
    sns.set(style="whitegrid")
    df = pd.DataFrame(results)
    df_melted = df.melt(id_vars=["Operation"], value_vars=["Pandas", "Polars"],
                        var_name='Library', value_name='Time (s)')
    plt.figure(figsize=(10, 6))
    bar = sns.barplot(x="Operation", y="Time (s)", hue="Library", data=df_melted)
    plt.title(title)
    plt.ylabel("耗时（秒）")
    plt.xticks(rotation=45)
    for p in bar.patches:
        bar.annotate(format(p.get_height(), '.2f'),
                     (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center',
                     xytext=(0, 9),
                     textcoords='offset points')
    plt.tight_layout()
    plt.savefig("performance_comparison.png")
    print("📊 性能对比图表已保存为 performance_comparison.png")
    plt.show()


def run_benchmark(file_path: str):
    """运行完整性能测试流程"""
    print(f"\n🚀 开始测试文件：{file_path}")
    results = []

    # 读取测试
    print("📌 正在进行【读取】性能测试...")
    _, t_pd_read = read_with_pandas(file_path)
    _, t_pl_read = read_with_polars(file_path)
    results.append({"Operation": "Read", "Pandas": t_pd_read, "Polars": t_pl_read})

    # 过滤测试
    print("📌 正在进行【过滤】性能测试...")
    pd_df, _ = read_with_pandas(file_path)
    pl_df = pl.read_csv(file_path)
    _, t_pd_filter = filter_with_pandas(pd_df)
    _, t_pl_filter = filter_with_polars(pl_df)
    results.append({"Operation": "Filter", "Pandas": t_pd_filter, "Polars": t_pl_filter})

    # 分组测试
    print("📌 正在进行【分组】性能测试...")
    _, t_pd_group = groupby_with_pandas(pd_df)
    _, t_pl_group = groupby_with_polars(pl_df)
    results.append({"Operation": "GroupBy", "Pandas": t_pd_group, "Polars": t_pl_group})

    # 排序测试
    print("📌 正在进行【排序】性能测试...")
    _, t_pd_sort = sort_with_pandas(pd_df)
    _, t_pl_sort = sort_with_polars(pl_df)
    results.append({"Operation": "Sort", "Pandas": t_pd_sort, "Polars": t_pl_sort})

    # 写入测试
    print("📌 正在进行【写入】性能测试...")
    temp_pd_file = "temp_pd_output.csv"
    temp_pl_file = "temp_pl_output.csv"
    _, t_pd_write = write_csv_pandas(pd_df, temp_pd_file)
    _, t_pl_write = write_csv_polars(pl_df, temp_pl_file)
    results.append({"Operation": "Write CSV", "Pandas": t_pd_write, "Polars": t_pl_write})

    # 清理临时文件
    os.remove(temp_pd_file)
    os.remove(temp_pl_file)

    return results


# Polars vs Pandas 性能对比脚本
if __name__ == "__main__":
    import sys
    import os

    print("📊 Polars vs Pandas 性能对比工具")

    # 1. 获取文件路径
    if len(sys.argv) == 2:
        csv_file = sys.argv[1]
        if not os.path.exists(csv_file):
            print(f"❌ 文件不存在: {csv_file}")
            exit()
    else:
        while True:
            csv_file = input("请输入 CSV 文件路径（输入 q 退出）：").strip()
            if csv_file.lower() in ['q', 'quit', 'exit']:
                print("👋 程序已退出")
                exit()
            if os.path.exists(csv_file):
                break
            else:
                print(f"❌ 路径无效，请重新输入！")

    print(f"\n🚀 开始测试文件：{csv_file}")

    # 2. 执行性能测试
    benchmark_result = run_benchmark(csv_file)

    # 3. 显示结果图表
    plot_results(benchmark_result, title=f"Polars vs Pandas - {os.path.basename(csv_file)}")

