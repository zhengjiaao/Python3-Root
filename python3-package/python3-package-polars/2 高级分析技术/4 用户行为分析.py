import os
import polars as pl
from datetime import datetime, timedelta
from typing import Optional, List


class UserBehaviorAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def generate_mock_data() -> pl.DataFrame:
        """生成用于测试的用户点击行为数据（含 user_id、event、timestamp）"""
        # 生成时间戳序列（每分钟一个事件）
        now = datetime.now()
        timestamps = [now + timedelta(minutes=i) for i in range(20)]

        return pl.DataFrame({
            "user_id": [101, 102, 101, 103, 104, 102, 101, 105, 106, 107,
                        101, 102, 108, 109, 110, 101, 102, 103, 104, 105],
            "event": ["click", "view", "click", "click", "click", "click", "click",
                      "view", "click", "click", "click", "click", "click", "click",
                      "click", "click", "click", "view", "click", "click"],
            "timestamp": timestamps
        })

    @staticmethod
    def read_parquet(file_path: str) -> pl.DataFrame:
        """读取 Parquet 文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        return pl.read_parquet(file_path)

    @staticmethod
    def write_csv(df: pl.DataFrame, file_path: str) -> None:
        """写入 CSV 文件"""
        df.write_csv(file_path)

    @classmethod
    def analyze_user_clicks(cls, parquet_file: Optional[str] = None) -> pl.DataFrame:
        """
        分析用户点击行为：统计每个用户的点击次数和最后点击时间
        :param parquet_file: 可选 Parquet 文件路径
        :return: 分析结果 DataFrame
        """
        if parquet_file:
            print("正在从 Parquet 文件加载数据...")
            df = cls.read_parquet(parquet_file)
        else:
            print("未提供文件，使用 mock 数据进行分析...")
            df = cls.generate_mock_data()

        # 惰性查询：筛选点击事件，并按用户分组聚合
        result = (
            df.lazy()
            .filter(pl.col("event") == "click")
            .group_by("user_id")
            .agg(
                click_count=pl.len(),  # ✅ 替换 pl.count() 为 pl.len()
                last_click=pl.col("timestamp").max()
            )
            .sort("click_count", descending=True)
            .collect(engine="auto")  # ✅ 替换 streaming=True 为 engine="auto"
        )

        return result

    @classmethod
    def run_analysis(cls, parquet_file: Optional[str] = None, output_file: str = "user_click_stats.csv"):
        """
        执行完整分析流程，并输出到 CSV
        """
        result_df = cls.analyze_user_clicks(parquet_file)
        cls.write_csv(result_df, output_file)
        print(f"\n分析完成，共统计 {len(result_df)} 个用户行为数据。")
        print(f"结果已保存至: {output_file}")
        return result_df


# 示例用法
if __name__ == "__main__":
    # 执行完整分析流程（使用 mock 数据）
    result_df = UserBehaviorAnalyzer.run_analysis()

    # 输出前几行示例数据
    print("\n分析结果预览：")
    print(result_df.head())
