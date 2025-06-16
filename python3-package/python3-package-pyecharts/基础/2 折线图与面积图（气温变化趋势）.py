from pyecharts.charts import Line
from pyecharts import options as opts
import random


# 生成模拟气温数据
def generate_weather_data():
    """
    生成一个月的模拟最高温、最低温和平均温数据。

    Returns:
        tuple: (日期列表, 最高温列表, 最低温列表, 平均温列表)
    """
    days = [f"{i}日" for i in range(1, 31)]
    high_temp = [random.randint(22, 35) for _ in range(30)]
    low_temp = [random.randint(15, 25) for _ in range(30)]
    avg_temp = [(h + l) // 2 for h, l in zip(high_temp, low_temp)]
    return days, high_temp, low_temp, avg_temp


# 创建折线图
def create_line_chart(days, high_temp, low_temp, avg_temp):
    """
    创建并返回一个包含三种气温趋势的折线图对象。

    Args:
        days: 日期列表
        high_temp: 最高气温列表
        low_temp: 最低气温列表
        avg_temp: 平均气温列表

    Returns:
        Line: 配置好的折线图实例
    """
    chart = (
        Line()
        .add_xaxis(days)
        .add_yaxis(
            "最高气温",
            high_temp,
            is_smooth=True,
            symbol="circle",
            symbol_size=8,
            linestyle_opts=opts.LineStyleOpts(width=3),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color="#c23531")
        )
        .add_yaxis(
            "最低气温",
            low_temp,
            is_smooth=True,
            symbol="triangle",
            symbol_size=8,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=3),
            itemstyle_opts=opts.ItemStyleOpts(color="#2f4554")
        )
        .add_yaxis(
            "平均气温",
            avg_temp,
            is_smooth=True,
            symbol="diamond",
            symbol_size=10,
            label_opts=opts.LabelOpts(is_show=True, position="top"),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.1, color="#61a0a8"),
            linestyle_opts=opts.LineStyleOpts(width=4, type_="dashed"),
            itemstyle_opts=opts.ItemStyleOpts(color="#61a0a8")
        )
    )
    return chart


# 设置全局选项
def configure_global_options():
    """
    返回图表的全局配置项。

    Returns:
        dict: 包含所有全局配置的对象字典
    """
    return dict(
        title_opts=opts.TitleOpts(title="6月气温变化趋势", subtitle="模拟数据"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        legend_opts=opts.LegendOpts(pos_left="center", pos_top="top"),
        datazoom_opts=[
            opts.DataZoomOpts(range_start=0, range_end=100),  # 滑动条缩放
            opts.DataZoomOpts(type_="inside")  # 内置缩放
        ],
        yaxis_opts=opts.AxisOpts(
            name="温度(℃)",
            splitline_opts=opts.SplitLineOpts(is_show=True),
            axislabel_opts=opts.LabelOpts(formatter="{value} °C")
        ),
        xaxis_opts=opts.AxisOpts(
            name="日期",
            axispointer_opts=opts.AxisPointerOpts(type_="shadow")
        )
    )


# 设置系列选项（标记点）
def configure_series_options():
    """
    返回系列配置，添加最大值/最小值标记点。

    Returns:
        MarkPointOpts: 标记点配置
    """
    return opts.MarkPointOpts(
        data=[
            opts.MarkPointItem(type_="max", name="最大值"),
            opts.MarkPointItem(type_="min", name="最小值")
        ]
    )


# 渲染图表
def render_chart(chart):
    """
    在 Jupyter 中显示图表，并保存为 HTML 文件。

    Args:
        chart: 图表对象
    """
    chart.render_notebook()
    chart.render("3 temperature_trend_line_chart.html")


# 主程序入口
if __name__ == "__main__":
    # 生成数据
    days, high_temp, low_temp, avg_temp = generate_weather_data()

    # 创建图表
    line_chart = create_line_chart(days, high_temp, low_temp, avg_temp)

    # 应用全局配置
    line_chart.set_global_opts(**configure_global_options())

    # 应用系列配置（标记点）
    line_chart.set_series_opts(markpoint_opts=configure_series_options())

    # 渲染输出
    render_chart(line_chart)
