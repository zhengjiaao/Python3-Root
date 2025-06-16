# 快速开始

## 介绍

PyEcharts 是一个强大的 Python 数据可视化库，基于百度开源的 ECharts 构建，提供丰富的图表类型和交互功能。

#### 核心优势

- **丰富的图表类型**：支持 30+ 种图表类型
- **交互式体验**：支持缩放、拖拽、数据筛选等交互
- **中国地图支持**：内置完善的中国省市级地理数据
- **链式调用**：优雅的 API 设计，代码简洁直观
- **主题定制**：多种内置主题，支持自定义主题
- **Web集成**：可嵌入 Flask/Django/FastAPI 等 Web 框架

#### 应用场景

1. **业务数据看板**：销售数据、用户行为分析
2. **地理数据可视化**：区域分布、热力图
3. **时序数据分析**：股票走势、气象数据
4. **关系网络展示**：社交网络、知识图谱
5. **大屏数据展示**：监控中心、指挥大屏

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
# 安装pyecharts
pip install pyecharts

# 安装附加地图包(老版本，新版本已经内置了), 所有地图资源都已整合进 pyecharts 主库，通过 Dataset 获取
#pip install echarts-countries-pypkg     # 全球国家地图
#pip install echarts-china-provinces-pypkg  # 中国省级地图
#pip install echarts-china-cities-pypkg     # 中国市级地图

# or
pip install -r requirements.txt
```

验证：

```shell
pip show setuptools
```

## 示例


