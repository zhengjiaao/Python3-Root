import polars as pl
from datetime import datetime
from typing import Optional, List


class TimeSeriesAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def generate_mock_data() -> pl.DataFrame:
        """生成用于测试的时间序列 mock 数据"""
        return pl.DataFrame({
            "date": [
                "2025-01-01", "2025-01-01", "2025-01-02",
                "2025-01-03", "2025-01-04", "2025-01-05",
                "2025-01-06", "2025-01-07", "2025-01-08"
            ],
            "sales": [100, 150, 200, 120, 180, 90, 250, 300, 220],
            "category": ["A", "B", "A", "B", "A", "B", "A", "B", "A"]
        })

    @staticmethod
    def parse_date_column(df: pl.DataFrame, date_col: str = "date") -> pl.DataFrame:
        """将字符串格式的日期列转换为 Date 类型"""
        return df.with_columns(pl.col(date_col).str.strptime(pl.Date, "%Y-%m-%d"))

    @staticmethod
    def group_by_daily(
        df: pl.DataFrame,
        date_col: str = "date",
        value_col: str = "sales"
    ) -> pl.DataFrame:
        """
        按天聚合销售数据
        :param df: 输入 DataFrame
        :param date_col: 日期列名
        :param value_col: 要聚合的数值列
        :return: 按天聚合后的 DataFrame
        """
        return (
            df.sort(date_col)
            .group_by_dynamic(date_col, every="1d")
            .agg(pl.col(value_col).sum().alias(f"daily_{value_col}"))
        )

    @staticmethod
    def fill_missing_dates(
            df: pl.DataFrame,
            date_col: str = "date",
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
    ) -> pl.DataFrame:
        """
        填充缺失的日期行，确保连续的时间轴
        """
        if not start_date:
            start_date = df[date_col].min().strftime("%Y-%m-%d")
        if not end_date:
            end_date = df[date_col].max().strftime("%Y-%m-%d")

        # 创建完整日期范围，并立即执行获取实际数据
        all_dates = pl.select(
            pl.date_range(
                start=datetime.strptime(start_date, "%Y-%m-%d"),
                end=datetime.strptime(end_date, "%Y-%m-%d"),
                interval="1d",
                closed="both"
            )
        ).to_series()

        # 构建完整日期表并左连接补全缺失
        full_df = pl.DataFrame({date_col: all_dates}).join(df, on=date_col, how="left")

        return full_df.fill_null(0)

    @classmethod
    def analyze_time_series(cls) -> pl.DataFrame:
        """
        完整时间序列分析流程
        """
        # 1. 生成数据
        df = cls.generate_mock_data()

        # 2. 解析日期
        df = cls.parse_date_column(df)

        # 3. 按天聚合销售额
        daily_sales = cls.group_by_daily(df, "date", "sales")

        # 4. 补全缺失日期
        filled_df = cls.fill_missing_dates(daily_sales)

        return filled_df


# 示例用法
if __name__ == "__main__":
    # 执行完整分析流程
    result_df = TimeSeriesAnalyzer.analyze_time_series()

    # 输出结果
    print("每日聚合销售数据（含补全）：")
    print(result_df)
