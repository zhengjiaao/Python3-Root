# pandas 示例：数据分析与导出
import pandas as pd

if __name__ == '__main__':
    print("Pandas 示例：数据分析与导出")
    # 创建数据集
    data = {
        'Product': ['A', 'B', 'C', 'A', 'B'],
        'Region': ['North', 'South', 'North', 'South', 'North'],
        'Sales': [2400, 1800, 3500, 2100, 1900]
    }
    df = pd.DataFrame(data)

    # 数据分析：按产品和区域汇总
    report = df.pivot_table(
        index='Product',
        columns='Region',
        values='Sales',
        aggfunc='sum'
    )

    # 添加统计列
    report['Total'] = report.sum(axis=1)
    report.loc['Region Total'] = report.sum()

    # 导出到Excel
    report.to_excel("sales_summary.xlsx",
                    sheet_name="销售汇总",
                    float_format="%.2f")