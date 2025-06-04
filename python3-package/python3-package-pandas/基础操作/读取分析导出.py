import pandas as pd

if __name__ == '__main__':

    print("Pandas 示例：创建示例数据")
    # 创建示例数据
    data = {
        '产品类别': ['电子产品', '服装', '电子产品', '食品', '服装', '食品'],
        '销售额': [15000, 8000, 20000, 500, 9000, 300],
        '地区': ['北京', '上海', '广州', '深圳', '杭州', '成都']
    }

    # 创建 DataFrame
    df = pd.DataFrame(data)

    # 导出到 Excel 文件 input.xlsx
    df.to_excel('input.xlsx', index=False)

    print("Pandas 示例：读取分析导出")
    # 读取 Excel
    df = pd.read_excel('input.xlsx', sheet_name='Sheet1')

    # 数据处理示例
    filtered = df[df['销售额'] > 10000]  # 筛选
    # grouped = df.groupby('产品类别').mean()  # 分组统计  # ❌ 错误：试图对所有列求均值
    # grouped = df.groupby('产品类别')[['销售额']].mean()  # ✅ 正确：仅对销售额列求均值
    grouped = df.groupby('产品类别').agg({'销售额': 'mean'})  # ✅ 正确：更具可读性的写法

    # 导出到 Excel
    with pd.ExcelWriter('output.xlsx') as writer:
        df.to_excel(writer, sheet_name='原始数据')
        grouped.to_excel(writer, sheet_name='分析结果')