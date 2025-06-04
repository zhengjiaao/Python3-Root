# pandas 用于操作Excel应用程序

pandas 实际应用场景的完整示例，涵盖数据处理、分析、可视化和报告生成等常见任务。

1. 数据清洗：缺失值处理、异常值修正、重复数据删除
2. 数据转换：类型转换、日期处理、特征工程
3. 数据分析：分组聚合、透视表、RFM分析
4. 数据可视化：Matplotlib集成、图表导出
5. 报告生成：Excel多表操作、图表嵌入、格式设置
6. 高级分析：时间序列预测、异常检测
7. 性能优化：向量化操作、避免循环

## 介绍

openpyxl 和 pandas 这两个 Python Excel 处理库的详细对比与推荐，两者都不依赖 Windows 环境，可跨平台使用：

### 核心功能对比

| **特性**         | **openpyxl**                        | **pandas**                            |
| :--------------- | :---------------------------------- | :------------------------------------ |
| **核心定位**     | Excel 文件精细操作 (读写/样式/图表) | 数据分析与处理 (Excel 仅作为输入输出) |
| **文件格式**     | `.xlsx`, `.xlsm`                    | `.xlsx`, `.xls`, `.csv`, 等           |
| **样式控制**     | ✅ 完整支持 (字体/边框/颜色/对齐)    | ⚠️ 仅基础样式                          |
| **公式计算**     | ✅ 读写公式                          | ⚠️ 仅读取公式结果                      |
| **数据处理能力** | ⚠️ 基础行列操作                      | ✅ 强大 (过滤/聚合/合并/统计)          |
| **图表操作**     | ✅ 支持创建图表                      | ❌ 不支持                              |
| **VBA 宏支持**   | ✅ 读取/保存宏 (.xlsm)               | ❌ 不支持                              |
| **内存效率**     | ⚠️ 中等 (支持只读模式)               | ✅ 高 (优化数据存储)                   |


### 推荐场景

#### 选择 **openpyxl** 当您需要：

1. 创建复杂格式的 Excel 报表（如财务报表）
2. 动态生成带样式/图表/公式的模板
3. 处理宏或 VBA 脚本
4. 需要精确控制单元格样式

1. 需要精确控制单元格样式

```python
# openpyxl 示例：创建带样式的报表
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

wb = Workbook()
ws = wb.active

# 写入标题（带样式）
title_cell = ws['A1']
title_cell.value = "销售报告"
title_cell.font = Font(bold=True, size=14)
title_cell.alignment = Alignment(horizontal='center')

# 合并单元格
ws.merge_cells('A1:D1')

# 写入数据
data = [["产品", "季度", "销量", "增长率"],
        ["A", "Q1", 1500, "15%"],
        ["B", "Q1", 2400, "22%"]]
for row in data:
    ws.append(row)

# 保存
wb.save("sales_report.xlsx")
```

#### 选择 **pandas** 当您需要：

1. 清洗/分析大量数据
2. 从多种数据源合并处理
3. 执行统计计算或机器学习预处理
4. 快速导出分析结果

```python
# pandas 示例：数据分析与导出
import pandas as pd

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
```

------

### 📦 安装与基础用法

#### 1. openpyxl

```bash
pip install openpyxl
```

基础操作：

```python
from openpyxl import load_workbook

# 读取文件
wb = load_workbook('data.xlsx')
ws = wb.active

# 遍历数据
for row in ws.iter_rows(values_only=True):
    print(row)  # 输出每行数据元组

# 修改单元格
ws['B2'] = "新值"
ws.cell(row=3, column=4).value = 100

# 保存修改
wb.save('modified.xlsx')
```

#### 2. pandas

```bash
pip install pandas openpyxl  # openpyxl 作为 Excel 引擎
```

基础操作：

```python
import pandas as pd

# 读取 Excel
df = pd.read_excel('input.xlsx', sheet_name='Sheet1')

# 数据处理示例
filtered = df[df['销售额'] > 10000]  # 筛选
grouped = df.groupby('产品类别').mean()  # 分组统计

# 导出到 Excel
with pd.ExcelWriter('output.xlsx') as writer:
    df.to_excel(writer, sheet_name='原始数据')
    grouped.to_excel(writer, sheet_name='分析结果')
```

------

### 💡 终极选择建议

| **需求场景**                | **推荐工具** |
| :-------------------------- | :----------- |
| 需要创建精美格式的报表      | ✅ openpyxl   |
| 需要处理 Excel 公式/宏/图表 | ✅ openpyxl   |
| 数据清洗/统计分析           | ✅ pandas     |
| 大数据处理 (>10万行)        | ✅ pandas     |
| 简单读写 + 基础格式         | ⚖️ 两者皆可   |

> **高效组合方案**：
> 使用 `pandas` 做核心数据处理 → 用 `openpyxl` 加载结果并应用精细样式

```python
import pandas as pd
from openpyxl import load_workbook
 
# pandas 处理数据
df = pd.read_csv('big_data.csv')
processed = df.groupby(...).sum()
 
# openpyxl 应用样式
processed.to_excel('temp.xlsx')  # 先导出
wb = load_workbook('temp.xlsx')
ws = wb.active
for cell in ws['A']:  # 设置A列样式
    cell.font = Font(bold=True)
wb.save('final_report.xlsx')
```

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖库
pip install pandas openpyxl matplotlib scikit-learn  # openpyxl 作为 Excel 引擎

# or
pip install -r requirements.txt
```

验证：

```shell
pip install pyqt5
```

## 示例

创建 一个名为 `test.py` 的文件，并运行命令 `python test.py`

```python
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
```