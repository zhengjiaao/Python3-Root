from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Grid


# 数据准备
def prepare_data():
    months = ["1月", "2月", "3月", "4月", "5月", "6月"]
    sales = [120, 132, 101, 134, 90, 230]
    growth_rate = [None, 10.0, -23.5, 32.7, -32.8, 155.6]

    return months, sales, growth_rate


# 创建柱状图：销售额
def create_bar_chart(months, sales):
    bar = (
        Bar()
        .add_xaxis(months)
        .add_yaxis("销售额", sales)
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(name="销售额 (万元)"),
            datazoom_opts=[opts.DataZoomOpts(type_="slider"), opts.DataZoomOpts(type_="inside")],
            legend_opts=opts.LegendOpts(pos_top="5%")
        )
    )
    return bar


# 创建折线图：增长率
def create_line_chart(months, growth_rate):
    line = (
        Line()
        .add_xaxis(months)
        .add_yaxis("增长率", growth_rate, is_smooth=True)
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(name="增长率 (%)"),
            datazoom_opts=[opts.DataZoomOpts(type_="slider"), opts.DataZoomOpts(type_="inside")],
            legend_opts=opts.LegendOpts(pos_top="5%", pos_left="50%")
        )
    )
    return line

# 组合图表
def create_combined_chart(bar, line):
    grid = (
        Grid(init_opts=opts.InitOpts(width="1200px", height="800px"))
        .add(
            bar,
            grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="10%", height="35%"),
            grid_index=0
        )
        .add(
            line,
            grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="50%", height="35%"),
            grid_index=1
        )
    )
    return grid


# 主程序入口
if __name__ == "__main__":
    # 准备数据
    months, sales, growth_rate = prepare_data()

    # 构建图表
    bar = create_bar_chart(months, sales)
    line = create_line_chart(months, growth_rate)

    # 图表联动（共享X轴）
    bar.extend_axis(yaxis=opts.AxisOpts())
    bar.set_series_opts(secondary_yaxis_index=0)
    bar.add_yaxis("增长率", growth_rate, yaxis_index=1, itemstyle_opts=opts.ItemStyleOpts(color="#91cc75"))

    # 组合图表
    combined_chart = create_combined_chart(bar, line)

    # 渲染输出
    output_path = "2 linked_charts.html"
    combined_chart.render(output_path)
    print(f"📊 图表已生成，请查看以下文件：{output_path}")
