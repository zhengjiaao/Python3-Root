from flask import Flask, render_template
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType

app = Flask(__name__)

# def create_bar_chart():
#     bar = (
#         Bar()
#         .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
#         .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
#         .add_yaxis("商家B", [15, 6, 45, 20, 35, 66])
#         .set_global_opts(
#             title_opts=opts.TitleOpts(title="商品销售情况"),
#             toolbox_opts=opts.ToolboxOpts(is_show=True)
#         )
#     )
#     return bar.dump_options_with_quotes()

# 创建柱状图
def create_bar_chart():
    bar = (
        # Bar()
        Bar(
            init_opts=opts.InitOpts(
            # theme=ThemeType.DARK, # 使用暗黑主题
            theme=ThemeType.WHITE, # 使用白色主题
            bg_color="#f5f5f5",  # 背景色
            )
        )
        .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
        .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
        .add_yaxis("商家B", [15, 6, 45, 20, 35, 66])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="商品销售情况"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(name="商品类别"),
            yaxis_opts=opts.AxisOpts(name="销售额 (万元)")
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="top"))
    )
    return bar.dump_options_with_quotes()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/barChart")
def bar_chart():
    return create_bar_chart()

if __name__ == "__main__":
    app.run(debug=False)