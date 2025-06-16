from pyecharts.charts import Map3D
from pyecharts import options as opts
from pyecharts.globals import ChartType, GeoType, RenderType
import random

# 真实城市经纬度（简化示例）
# 城市经纬度（完整名称）
CITY_COORDS = {
    "北京市": [116.4074, 39.9042],
    "上海市": [121.4737, 31.2304],
    "广州市": [113.2644, 23.1291],
    "深圳市": [114.0579, 22.5431],
    "杭州市": [120.1536, 30.2448],
    "成都市": [104.0668, 30.5728],
    "武汉市": [114.3052, 30.5929],
    "西安市": [108.9480, 34.3416]
}


def create_map3d_schema():
    """创建Map3D的schema配置"""
    return (
        Map3D()
        .add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(
                color="rgb(5,101,123)",
                opacity=1,
                border_width=0.8,
                border_color="rgb(62,215,213)"
            ),
            light_opts=opts.Map3DLightOpts(
                main_color="#fff",
                main_intensity=1.2,
                ambient_intensity=0.3
            ),
            view_control_opts=opts.Map3DViewControlOpts(
                projection="perspective",
                auto_rotate=True,
                auto_rotate_speed=5,
                auto_rotate_after_still=1
            ),
            post_effect_opts=opts.Map3DPostEffectOpts(
                is_enable=True
            )
        )
    )

def generate_data():
    """生成模拟数据（使用真实城市坐标）"""
    cities = list(CITY_COORDS.keys())
    data = []
    for city in cities:
        lng, lat = CITY_COORDS[city]
        value = random.randint(500, 3000)  # 高度值
        data.append({
            "name": city,
            "value": [lng, lat, value]
        })
    return data

def render_3d_map():
    """主函数：创建并渲染3D地图"""
    map3d = create_map3d_schema()
    data = generate_data()

    # 添加数据系列
    map3d.add(
        series_name="城市指标",
        data_pair=[(item["name"], item["value"]) for item in data],
        type_=ChartType.BAR3D,
        shading="realistic",
        bar_size=1,
        label_opts=opts.LabelOpts(
            is_show=True,
            formatter="{b}",
            position="top"
        ),
        itemstyle_opts=opts.ItemStyleOpts(color="#FFA500")
    )

    # 设置全局选项
    map3d.set_global_opts(
        title_opts=opts.TitleOpts(title="中国主要城市3D指标图"),
        visualmap_opts=opts.VisualMapOpts(
            is_show=True,
            type_="color",
            min_=500,
            max_=3000,
            range_color=[
                "#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8",
                "#fee090", "#fdae61", "#f46d43", "#d73027"
            ]
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item",
            formatter=lambda params: f"{params.name}<br/>指标值: {params.value[2]}"
        )
    )

    output_path = "6 china_3d_map.html"
    map3d.render(output_path)
    print(f"3D地图已生成，请打开以下路径查看：{output_path}")

if __name__ == "__main__":
    render_3d_map()
