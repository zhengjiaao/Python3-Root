# 导入 pyecharts 模块
from pyecharts import options as opts
from pyecharts.charts import Bar


# 获取销售数据
def get_sales_data():
    """
    返回 2023 上半年的月份和两个产品的销售额。

    Returns:
        tuple: (月份列表, 产品A销售额, 产品B销售额)
    """
    months = ["1月", "2月", "3月", "4月", "5月", "6月"]
    sales_a = [120, 132, 101, 134, 90, 230]
    sales_b = [60, 72, 85, 106, 120, 180]
    return months, sales_a, sales_b


# 设置全局图表选项
def configure_global_opts():
    """
    返回配置好的全局设置（标题、提示框、工具箱等）。

    Returns:
        tuple: title, tooltip, toolbox, datazoom, yaxis, xaxis 配置
    """
    return (
        opts.TitleOpts(title="2023年上半年销售数据", subtitle="单位：万元"),
        opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        opts.ToolboxOpts(
            feature={
                "saveAsImage": {},
                "dataView": {"show": True, "readOnly": False},
                "magicType": {"show": True, "type": ["line", "bar"]},
            }
        ),
        [opts.DataZoomOpts(type_="inside")],
        opts.AxisOpts(name="销售额"),
        opts.AxisOpts(name="月份"),
    )


# 设置系列选项（如平均值标记线）
def configure_series_opts():
    """
    返回系列配置，添加平均值标记线。

    Returns:
        MarkLineOpts: 标记线配置
    """
    return opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average", name="平均值")])


# 创建柱状图
def create_bar_chart(months, sales_a, sales_b):
    """
    构建柱状图实例并添加数据。

    Args:
        months: X 轴数据（月份）
        sales_a: 产品 A 的销售额
        sales_b: 产品 B 的销售额

    Returns:
        Bar: 构建好的柱状图对象
    """
    bar = (
        Bar()
        .add_xaxis(months)
        .add_yaxis("产品A", sales_a,
                   label_opts=opts.LabelOpts(position="top"),
                   itemstyle_opts=opts.ItemStyleOpts(color="#5793f3"))
        .add_yaxis("产品B", sales_b,
                   label_opts=opts.LabelOpts(position="top"),
                   itemstyle_opts=opts.ItemStyleOpts(color="#d14a61"))
    )
    return bar


# 渲染图表
def render_chart(chart):
    """
    在 Jupyter 中显示图表，并保存为 HTML 文件。

    Args:
        chart: 图表对象
    """
    chart.render_notebook()
    chart.render("1 sales_bar_chart.html")


# 程序入口
if __name__ == "__main__":
    # 获取数据
    months, sales_a, sales_b = get_sales_data()

    # 创建图表
    bar = create_bar_chart(months, sales_a, sales_b)

    # 应用全局配置
    title_opts, tooltip_opts, toolbox_opts, datazoom_opts, yaxis_opts, xaxis_opts = configure_global_opts()
    bar.set_global_opts(
        title_opts=title_opts,
        tooltip_opts=tooltip_opts,
        toolbox_opts=toolbox_opts,
        datazoom_opts=datazoom_opts,
        yaxis_opts=yaxis_opts,
        xaxis_opts=xaxis_opts,
    )

    # 添加系列配置（平均值线）
    bar.set_series_opts(markline_opts=configure_series_opts())

    # 渲染输出
    render_chart(bar)
