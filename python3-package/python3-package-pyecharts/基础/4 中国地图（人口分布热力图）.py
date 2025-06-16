from pyecharts import options as opts
from pyecharts.charts import Map


# 标准省份名称映射（适配 pyecharts 内置地图）
NAME_MAP = {
    "北京市": "北京市",
    "天津市": "天津市",
    "河北省": "河北省",
    "山西省": "山西省",
    "内蒙古自治区": "内蒙古自治区",
    "辽宁省": "辽宁省",
    "吉林省": "吉林省",
    "黑龙江省": "黑龙江省",
    "上海市": "上海市",
    "江苏省": "江苏省",
    "浙江省": "浙江省",
    "安徽省": "安徽省",
    "福建省": "福建省",
    "江西省": "江西省",
    "山东省": "山东省",
    "河南省": "河南省",
    "湖北省": "湖北省",
    "湖南省": "湖南省",
    "广东省": "广东省",
    "广西壮族自治区": "广西壮族自治区",
    "海南省": "海南省",
    "重庆市": "重庆市",
    "四川省": "四川省",
    "贵州省": "贵州省",
    "云南省": "云南省",
    "西藏自治区": "西藏自治区",
    "陕西省": "陕西省",
    "甘肃省": "甘肃省",
    "青海省": "青海省",
    "宁夏回族自治区": "宁夏回族自治区",
    "新疆维吾尔自治区": "新疆维吾尔自治区",
    "台湾省": "台湾省",
    "香港特别行政区": "香港特别行政区",
    "澳门特别行政区": "澳门特别行政区"
}


# 准备模拟人口数据
def prepare_population_data():
    """
    返回中国各省标准全称及模拟人口数据（单位：万人）

    Returns:
        tuple: 省份列表, 人口数据列表
    """
    provinces = [
        "北京市", "天津市", "河北省", "山西省", "内蒙古自治区",
        "辽宁省", "吉林省", "黑龙江省", "上海市", "江苏省",
        "浙江省", "安徽省", "福建省", "江西省", "山东省",
        "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区",
        "海南省", "重庆市", "四川省", "贵州省", "云南省",
        "西藏自治区", "陕西省", "甘肃省", "青海省", "宁夏回族自治区",
        "新疆维吾尔自治区", "台湾省", "香港特别行政区", "澳门特别行政区"
    ]
    population = [
        2189, 1387, 7592, 3718, 2534, 4359, 2704, 3773,
        2487, 8051, 5850, 6324, 3973, 4666, 10153, 9605,
        5917, 6918, 11521, 4960, 1008, 3102, 8367, 3856,
        4858, 351, 3953, 2637, 603, 688, 2523, 5631, 1832, 3238
    ]
    return provinces, population


# 创建地图图表
def create_china_population_map(provinces, population):
    """
    创建并返回一个中国地图可视化图表对象。
    """
    data_pair = [list(z) for z in zip(provinces, population)]

    china_map = (
        Map()
        .add(
            series_name="人口数量(万人)",
            data_pair=data_pair,
            maptype="china",
            # name_map=NAME_MAP,
            is_map_symbol_show=False,  # 不显示标记点
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True, position="inside"),
            tooltip_opts=opts.TooltipOpts(formatter="{b}<br/>人口: {c}万人"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="中国各省人口分布热力图",
                subtitle="数据来源: 国家统计局 (模拟数据)",
                pos_left="center"
            ),
            visualmap_opts=opts.VisualMapOpts(
                min_=0,
                max_=12000,
                is_piecewise=True,
                is_calculable=True,
                range_text=["高密度", "低密度"],
                pieces=[
                    {"min": 10000, "label": ">1亿人", "color": "#8A0808"},
                    {"min": 8000, "max": 9999, "label": "8000万-1亿", "color": "#B40404"},
                    {"min": 6000, "max": 7999, "label": "6000万-8000万", "color": "#DF0101"},
                    {"min": 4000, "max": 5999, "label": "4000万-6000万", "color": "#F5A9A9"},
                    {"min": 2000, "max": 3999, "label": "2000万-4000万", "color": "#F5D0A9"},
                    {"min": 0, "max": 1999, "label": "<2000万", "color": "#F2F5A9"}
                ],
                textstyle_opts=opts.TextStyleOpts(color="#333")
            ),
            legend_opts=opts.LegendOpts(pos_top="10%", pos_left="right"),
            # toolbox_opts=opts.ToolboxOpts(
            #     feature=opts.ToolBoxFeatureOpts(
            #         save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(name="中国人口热力图"),
            #         magic_type=opts.ToolBoxFeatureMagicTypeOpts(is_show=True, type_=["map", "bar"]),
            #         restore=opts.ToolBoxFeatureRestoreOpts()
            #     )
            # ),
            toolbox_opts=opts.ToolboxOpts(
                feature=opts.ToolBoxFeatureOpts(
                    save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(
                        name="中国人口热力图",  # 自定义图片名称
                        background_color="#FFFFFF",  # 背景颜色
                        pixel_ratio=2,  # 分辨率提升到 2x
                        type_="png"  # 图片类型（png / jpeg）
                    ),
                    magic_type=opts.ToolBoxFeatureMagicTypeOpts(is_show=False, type_=["map", "bar"]),
                    restore=opts.ToolBoxFeatureRestoreOpts()
                )
            ),
            xaxis_opts=opts.AxisOpts(is_show=False),
            yaxis_opts=opts.AxisOpts(is_show=False)
        )
    )

    return china_map


# 渲染图表
def render_chart(chart):
    """
    在 Jupyter 中渲染地图，并保存为 HTML 文件。
    """
    chart.render_notebook()
    chart.render("4 china_population_heatmap.html")


# 主程序入口
if __name__ == "__main__":
    provinces, population = prepare_population_data()
    map_chart = create_china_population_map(provinces, population)
    render_chart(map_chart)
