from pyecharts import options as opts
from pyecharts.charts import Pie


# 准备数据（与之前一致）
def prepare_data():
    companies = ["阿里巴巴", "腾讯", "百度", "京东", "拼多多", "其他"]
    market_share = [28.5, 22.3, 15.8, 12.6, 10.2, 10.6]
    return companies, market_share


# 创建支持切换的图表对象（使用基础 Chart 类型）
def create_switchable_chart(companies, market_share):
    data_pair = [list(z) for z in zip(companies, market_share)]

    chart = (
        Pie()
        .add(
            "",
            data_pair,
            radius=["30%", "70%"],
            center=["50%", "50%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(position="outside"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="中国互联网公司市场份额", subtitle="2023年第一季度数据"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="left", pos_top="middle"),
            toolbox_opts=opts.ToolboxOpts(
                feature={
                    "saveAsImage": {},
                    "dataView": {"show": True, "readOnly": False},
                    "magicType": {
                        "show": False,
                        "type": ["pie", "bar", "line"],  # 支持切换饼图/柱状图/折线图，切换点击没响应
                    },
                }
            ),
        )
        .set_series_opts(
            label_line_opts=opts.PieLabelLineOpts(length=10, length_2=15),
            tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{a} <br/>{b}: {c}% ({d}%)"),
        )
    )

    return chart


# 渲染图表
def render_chart(chart):
    chart.render_notebook()
    chart.render("3 switchable_market_share_chart.html")


# 主程序入口
if __name__ == "__main__":
    companies, market_share = prepare_data()
    chart = create_switchable_chart(companies, market_share)
    render_chart(chart)
