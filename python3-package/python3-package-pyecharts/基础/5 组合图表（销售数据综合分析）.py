from pyecharts.charts import Bar, Line, Grid
from pyecharts.components import Table
from pyecharts import options as opts
from pyecharts.options import ComponentTitleOpts, LabelOpts, TooltipOpts, AxisOpts, LegendOpts, ItemStyleOpts, \
    LineStyleOpts, SplitLineOpts, TextStyleOpts, AnimationOpts


# 数据准备
def prepare_data():
    months = ["1月", "2月", "3月", "4月", "5月", "6月"]
    sales = [125, 140, 155, 130, 165, 180]
    costs = [85, 90, 105, 95, 110, 120]
    profits = [40, 50, 50, 35, 55, 60]
    growth_rate = [None, 12.0, 10.7, -16.1, 26.9, 9.1]  # 增长率(%)

    return months, sales, costs, profits, growth_rate


# 创建柱状图：销售额与成本
def create_bar_chart(months, sales, costs):
    bar = (
        Bar(
            init_opts=opts.InitOpts(
                theme="light",
                animation_opts=opts.AnimationOpts(animation_duration=1000)
            )
        )
        .add_xaxis(months)
        .add_yaxis(
            "销售额(万元)",
            sales,
            itemstyle_opts=ItemStyleOpts(color="#5793f3"),
            label_opts=LabelOpts(position="top")
        )
        .add_yaxis(
            "成本(万元)",
            costs,
            itemstyle_opts=ItemStyleOpts(color="#d14a61"),
            label_opts=LabelOpts(position="top")
        )
        .set_global_opts(
            legend_opts=LegendOpts(pos_top="7%", textstyle_opts=TextStyleOpts(font_size=12)),
            tooltip_opts=TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axislabel_opts=LabelOpts(formatter="{value} 万")
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=LabelOpts(rotate=45)
            )
        )
    )
    return bar


# 创建折线图：利润与增长率
def create_line_chart(months, profits, growth_rate):
    line = (
        Line(
            init_opts=opts.InitOpts(
                theme="light",
                animation_opts=opts.AnimationOpts(animation_duration=1000)
            )
        )
        .add_xaxis(months)
        .add_yaxis(
            "利润(万元)",
            profits,
            yaxis_index=0,
            symbol="diamond",
            symbol_size=10,
            label_opts=LabelOpts(is_show=True, position="top"),
            linestyle_opts=LineStyleOpts(width=3, type_="solid"),
            itemstyle_opts=ItemStyleOpts(color="#675bba")
        )
        .add_yaxis(
            "增长率(%)",
            growth_rate,
            yaxis_index=1,
            symbol="circle",
            symbol_size=8,
            label_opts=LabelOpts(is_show=True, formatter="{c}%"),
            linestyle_opts=LineStyleOpts(width=2, type_="dashed"),
            itemstyle_opts=ItemStyleOpts(color="#91cc75")
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="增长率(%)",
                type_="value",
                position="right",
                offset=80,
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#91cc75")),
                axislabel_opts=LabelOpts(formatter="{value}%")
            )
        )
        .set_global_opts(
            title_opts=ComponentTitleOpts(title="利润与增长率趋势", subtitle="数据来源：销售分析"),
            yaxis_opts=opts.AxisOpts(
                name="利润(万元)",
                type_="value",
                position="right",
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#675bba")),
                axislabel_opts=LabelOpts(formatter="{value} 万"),
                splitline_opts=SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.3))
            ),
            tooltip_opts=TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            legend_opts=LegendOpts(textstyle_opts=TextStyleOpts(font_size=12))
        )
    )
    return line


# 组合图表
def create_combined_chart(bar, line):
    grid = (
        Grid(
            init_opts=opts.InitOpts(
                theme="light",
                animation_opts=opts.AnimationOpts(animation_duration=1000)
            )
        )
        .add(
            bar,
            grid_opts=opts.GridOpts(pos_left="8%", pos_right="6%", pos_top="12%", height="35%")
        )
        .add(
            line,
            grid_opts=opts.GridOpts(pos_left="8%", pos_right="6%", pos_top="52%", height="35%")
        )
    )
    return grid


# 渲染图表
def render_chart(chart, output_path="5 sales_analysis.html"):
    chart.render(output_path)
    print(f"图表已保存至: {output_path}")


# 主程序入口
if __name__ == "__main__":
    months, sales, costs, profits, growth_rate = prepare_data()

    bar_chart = create_bar_chart(months, sales, costs)
    line_chart = create_line_chart(months, profits, growth_rate)
    combined_chart = create_combined_chart(bar_chart, line_chart)

    render_chart(combined_chart)
