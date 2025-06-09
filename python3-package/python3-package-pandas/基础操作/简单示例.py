import pandas as pd
import os


def create_sample_data(file_path):
    """创建示例数据并保存为 CSV"""
    data = {
        "category": ["A", "B", "A", "C", "B", "C"],
        "col1": [10, 20, None, 30, 40, 50],
        "price": [100, 200, 150, 300, None, 350]
    }
    df_sample = pd.DataFrame(data)
    df_sample.to_csv(file_path, index=False)
    print(f"✅ 已创建示例文件: {file_path}")


def load_data(file_path):
    """读取 CSV 数据，若不存在则创建"""
    if not os.path.exists(file_path):
        print(f"⚠️ 文件 {file_path} 不存在，正在创建示例文件...")
        create_sample_data(file_path)
    return pd.read_csv(file_path)


def basic_inspection(df):
    """基础数据查看：前几行 + 统计摘要"""
    print("📊 数据预览（前5行）:")
    print(df.head())
    print("\n📈 数据统计摘要:")
    print(df.describe(include='all'))


def clean_data(df, fillna_value=0):
    """数据清洗：删除缺失值、新增列"""
    print("\n🧹 开始数据清洗...")

    # 确保是独立的 DataFrame，避免 SettingWithCopyWarning
    df = df.copy()

    # 缺失值处理
    if df.isnull().sum().sum() > 0:
        print("⚠️ 检测到缺失值，正在进行处理...")
        df = df.dropna()
        # 或者使用填充方式：
        # df = df.fillna(fillna_value)

    # 示例：新增列
    if "col1" in df.columns:
        df.loc[:, "new_col"] = df["col1"] * 2
        print("✅ 新增列 'new_col' 完成")

    return df

def perform_grouping(df, groupby_column="category", agg_column="price"):
    """分组聚合：按指定字段分组并计算平均值"""
    if groupby_column not in df.columns or agg_column not in df.columns:
        print(f"❌ 分组失败：'{groupby_column}' 或 '{agg_column}' 列不存在")
        return None

    print(f"\n🧮 正在按 '{groupby_column}' 分组并聚合 '{agg_column}' ...")
    result = (
        df.groupby(groupby_column)[agg_column]
        .mean()
        .sort_values(ascending=False)
    )
    print("✅ 分组完成")
    return result


def main():
    file_path = "data.csv"
    try:
        # Step 1: 加载数据（自动创建文件）
        print(f"📂 正在加载文件: {file_path}")
        df = load_data(file_path)

        # Step 2: 基础查看
        basic_inspection(df)

        # Step 3: 数据清洗
        df_cleaned = clean_data(df)

        # Step 4: 分组聚合
        result = perform_grouping(df_cleaned, groupby_column="category", agg_column="price")
        if result is not None:
            print("\n📌 聚合结果:")
            print(result)

    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    main()
