# 快速开始

## 介绍

Dask 库的核心应用场景是在大规模数据处理、并行计算和分布式计算等方面。

Dask 库提供了一种简单、高效、可扩展的方式来处理大型数据集，并支持多种计算后端，如本地CPU、GPU、分布式集群、云平台等。

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
# 安装基本的 Dask 库
pip install dask

# 安装包含常用扩展的`完整版本`，如用于数据处理、机器学习等的扩展
pip install "dask[complete]"
# or 安装单个 扩展
# 用于分布式计算和并行任务调度
pip install "dask[distributed]"
# 用于机器学习
pip install dask-ml

# 安装用于处理arrow格式的库，例如：生成 .parquet 文件
pip install pyarrow

# or
pip install -r requirements.txt
```

验证：

```shell
pip show setuptools
```

## 示例


