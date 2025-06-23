# 快速开始

## 介绍

Polars 高性能数据处理、并行计算、大数据分析等需求。

#### 对比 Pandas 性能优势

|        | Pandas | Polars |
|--------|--------|--------|
| 运行速度   | 0.5 秒  | 0.01 秒 |
| 运行内存占用 | 1.5 GB | 0.1 GB |
| 运行效率   | 10 倍   | 100 倍  |

#### 运行效率

| **操作**         | **Pandas 耗时** | **Polars 耗时** | **加速比** |
|:---------------|:--------------|:--------------|:--------|
| 读取 10MB CSV    | 1.31s         | 0.05s         | 26x     |
| 合并两个 DataFrame | 0.09s         | 0.03s         | 3x      |
| 分组聚合           | 2.1s          | 0.5s          | 4x      |

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
pip install polars pandas numpy matplotlib seaborn openpyxl fastexcel

# or
pip install -r requirements.txt
```

验证：

```shell
pip show polars
```

## 示例


