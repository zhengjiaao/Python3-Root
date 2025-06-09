# numpy

## 介绍

NumPy 是一个高性能的数学库，主要用于数组计算，支持多维数组（ndarray）和矩阵运算，提供大量用 C 语言实现的底层函数，显著提升 Python 的数值计算效率。它是科学计算、数据分析和机器学习的基础库，许多其他库（如 Pandas 和 Scikit-learn）依赖其功能。

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
pip install numpy

# or
pip install -r requirements.txt
```

验证：

```shell
pip show pyqt5
```

## 示例

创建一个名为 `test_numpy.py` 的文件，并运行命令 `python test_numpy.py`

```python
import numpy as np

"""创建一个数组,  并打印出来"""
if __name__ == "__main__":
    a = np.array([1, 2, 3])
    print(a)
## 运行上述代码，Python 会在屏幕上打印出：[1 2 3]
```
