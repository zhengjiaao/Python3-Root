from pyecharts import options as opts
from pyecharts.charts import Bar, Timeline


# 数据准备函数
def prepare_data():
    years = [2018, 2019, 2020, 2021, 2022, 2023]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    data = {
        2018: [120, 135, 142, 168],
        2019: [145, 156, 178, 192],
        2020: [132, 118, 125, 140],
        2021: [155, 168, 182, 210],
        2022: [178, 192, 205, 230],
        2023: [195, 210, 225, 248]
    }
    return years, quarters, data


# 创建柱状图
def create_bar_chart(year, quarters, sales):
    bar = (
        Bar()
        .add_xaxis(quarters)
        .add_yaxis("销售额(百万)", sales)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年季度销售数据"),
            yaxis_opts=opts.AxisOpts(name="销售额 (百万)"),
            xaxis_opts=opts.AxisOpts(name="季度"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            datazoom_opts=[opts.DataZoomOpts(type_="inside")],
            legend_opts=opts.LegendOpts(pos_top="10%")
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="top"))
    )
    return bar


# 创建时间线图表
def create_timeline_charts(years, quarters, data):
    tl = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    for year in years:
        chart = create_bar_chart(year, quarters, data[year])
        tl.add(chart, str(year))

    # 设置时间轴样式
    tl.add_schema(
        play_interval=2000,
        is_timeline_show=True,
        is_auto_play=True,
        is_loop_play=True,
        pos_left="10%",
        pos_right="10%",
        label_opts=opts.LabelOpts(position="bottom"),
        control_position="left"
    )

    return tl


# 主程序入口
if __name__ == "__main__":
    years, quarters, data = prepare_data()
    timeline_chart = create_timeline_charts(years, quarters, data)

    output_path = "3 timeline_sales.html"
    timeline_chart.render(output_path)
    print(f"📊 时间线图表已生成，请查看以下文件：{output_path}")
