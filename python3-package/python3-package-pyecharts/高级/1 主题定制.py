from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType


# 使用内置主题 - 暗黑风格
bar_builtin_theme = (
    Bar(init_opts=opts.InitOpts(theme=ThemeType.DARK))
    .add_xaxis(["A", "B", "C", "D", "E"])
    .add_yaxis("系列1", [10, 20, 15, 25, 30])
    .set_global_opts(
        title_opts=opts.TitleOpts(title="内置主题演示 - Dark"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(font_size=12)
        ),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(color="#333")
        )
    )
)

# 创建使用自定义主题的柱状图
bar_custom_theme = (
    Bar(
        init_opts=opts.InitOpts(
            bg_color="#f5f5f5",  # 背景色
        )
    )
    .add_xaxis(["A", "B", "C", "D", "E"])
    .add_yaxis(
        "系列1",
        [10, 20, 15, 25, 30],
        itemstyle_opts=opts.ItemStyleOpts(color="#c23531")  # 自定义颜色
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="自定义主题演示",
            title_textstyle_opts=opts.TextStyleOpts(color="#000", font_size=14, font_family="Microsoft YaHei")
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(font_size=12, font_family="Microsoft YaHei")
        ),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(color="#333")
        )
    )
)


# 渲染图表到HTML文件
def render_charts():
    bar_builtin_theme.render("1 内置主题演示.html")
    bar_custom_theme.render("1 自定义主题演示.html")
    print("✅ 图表已生成，请查看以下文件：")
    print("1 内置主题演示.html")
    print("1 自定义主题演示.html")


if __name__ == "__main__":
    render_charts()
