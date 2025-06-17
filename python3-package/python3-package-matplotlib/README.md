# 快速开始

## 介绍

Matplotlib 是 Python 最基础且功能强大的数据可视化库，为科学计算和数据可视化提供了坚实基础。

#### 核心优势

- **基础绘图能力**：提供各种基本图表类型（线图、散点图、柱状图等）
- **高度可定制性**：可精细控制图表的每个元素（颜色、线型、标签等）
- **出版级质量**：支持多种输出格式（PNG、PDF、SVG）和分辨率控制
- **多平台支持**：可在 Jupyter、Web 应用、GUI 程序等多种环境使用
- **丰富扩展**：Seaborn、Pandas 等库基于 Matplotlib 构建

#### 应用场景

1. **科研数据可视化**：实验数据、数值模拟结果展示
2. **商业分析报表**：销售趋势、市场份额分析
3. **金融数据分析**：股票走势、投资组合可视化
4. **机器学习结果展示**：模型性能评估、特征重要性
5. **工程制图**：信号处理、控制系统分析

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
pip install matplotlib

# 常用扩展
#pip install pandas seaborn scipy

# or
pip install -r requirements.txt
```

验证：

```shell
pip show matplotlib
```

## 示例


## 中间件（必须）


## 中间件（可选地）

方案一：安装 LaTeX（推荐用于需要高质量数学公式的用户）

1. 安装 MiKTeX（Windows 推荐）:
2. 下载地址: https://miktex.org/download
3. 安装后确保 latex.exe 在系统 PATH 环境变量中
4. 验证安装:  latex --version
5. 配置环境变量: 确保安装目录下的 miktex\bin\x64 文件夹在系统 PATH 中

方案二：禁用 LaTeX 渲染（适合不需要 LaTeX 公式渲染的用户）
```python
def setup_latex_rendering():
    """
    配置LaTeX渲染设置，用于生成高质量数学公式
    需要系统安装了LaTeX环境
    """
    # 注释掉或删除启用LaTeX的代码
    # plt.rcParams.update({
    #     "text.usetex": True,  # 启用LaTeX渲染
    #     "font.family": "serif",  # 使用衬线字体
    #     "font.serif": ["Computer Modern Serif"],  # 使用LaTeX的Computer Modern字体
    # })
    
    # 改为使用普通字体设置
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "SimHei"],  # 使用系统中文字体
        "font.size": 12,
        "axes.unicode_minus": False  # 正常显示负号
    })

```

方案三：使用 matplotlib 内置的 mathtext 引擎（适合只需要基本数学公式支持）

```python
def setup_latex_rendering():
    """
    配置数学公式渲染引擎
    使用内置的 mathtext 引擎代替 LaTeX
    """
    plt.rcParams.update({
        "text.usetex": False,  # 不使用完整LaTeX
        "mathtext.fontset": "dejavusans",  # 使用内置的 mathtext 字体
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "SimHei"],
        "font.size": 12
    })

```

建议：对于大多数中文用户，如果不需要复杂的 LaTeX 功能，可以使用以下简化版配置
```python
# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
plt.rcParams['font.size'] = 12  # 设置字体大小

```
并注释掉所有与 LaTeX 相关的代码部分。