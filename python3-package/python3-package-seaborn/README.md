# 快速开始

## 介绍

Seaborn是一个基于matplotlib的Python数据可视化库，提供了高级接口来绘制各种统计图形。用户可能是一位数据科学家或数据分析师，希望通过Seaborn创建更加美观和专业的可视化图表。

适合：结合数据分布可视化、多变量关系探索、分类数据分析等高频需求。

#### 适用场景总结

| **场景类型**  | **推荐图表**  | **典型用例**    | **Seaborn 函数**               |
|:----------|:----------|:------------|:-----------------------------|
| **分布分析**  | 直方图 + KDE | 年龄/收入分布     | `histplot()`, `kdeplot()`    |
| **异常值检测** | 箱线图       | 产品质量数据      | `boxplot()`                  |
| **类别对比**  | 小提琴图      | 不同群体指标分布    | `violinplot()`               |
| **相关性探索** | 散点图/热力图   | 广告投入 vs 销售额 | `scatterplot()`, `heatmap()` |
| **多变量关系** | 成对关系图     | 机器学习特征相关性   | `pairplot()`                 |
| **分组统计**  | 分面网格      | 不同地区销售趋势    | `FacetGrid()`                |

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
pip install seaborn matplotlib

# or
pip install -r requirements.txt
```

验证：

```shell
pip show seaborn
```

## 示例


