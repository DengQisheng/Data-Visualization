import os  # 文件

import numpy as np  # 数组
import pandas as pd  # 数组
import pyecharts.options as opts  # 选项
from pyecharts.charts import Map, Timeline  # 图表
from pyecharts.globals import ThemeType  # 主题

# 路径设置
HOME_PATH = os.getcwd()  # 主目录
DATA_PATH = os.path.join(HOME_PATH, 'data')  # 数据目录
RESULT_PATH = os.path.join(HOME_PATH, 'result')  # 结果目录

# 数据导入
GDP = pd.read_csv(os.path.join(DATA_PATH, 'GDP.csv'), index_col='Country')  # GDP数据
YEAR = GDP.columns.tolist()[1:]  # 年份
COUNTRY = GDP.index.tolist()  # 国家
MIN_GDP = np.log(GDP.iloc[:, 1:].min().min())  # GDP最大值的对数
MAX_GDP = np.log(GDP.iloc[:, 1:].max().max())  # GDP最小值的对数

# 按年份添加图层
def add_chart_by_year(year):

    map_chart = (
        Map()  # 地图图层
        .add(
            series_name='',  # 系列名称
            data_pair=list(zip(COUNTRY, np.log(GDP[year]))),  # 数据项
            maptype='world',  # 地图类型
            is_roam=False,  # 禁止缩放
            is_map_symbol_show=False,  # 不显示标记
            label_opts=opts.LabelOpts(is_show=False),  # 不显示标签
        )  # 图层设置
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title='Variation of World GDP (1996-2016)',  # 标题
                pos_left='center',  # 标题水平位置
                pos_top='60px',  # 标题竖直位置
                title_textstyle_opts=opts.TextStyleOpts(
                    color='#000000',  # 字体颜色
                    font_style='normal',  # 字体风格
                    font_size=25,  # 字体大小
                ),  # 标题字体样式
            ),
            visualmap_opts=opts.VisualMapOpts(
                min_=MIN_GDP,  # 图例最小值
                max_=MAX_GDP,  # 图例最大值
                range_text=['      log(US$)'],  # 图例标识
                range_color=[
                    '#FACDAA',  # 浅 <-> 小
                    '#F4A49E',
                    '#EE7B91',
                    '#E85285',
                    '#BE408C',
                    '#942D93',
                    '#6A1B9A',
                    '#56167D',  # 深 <-> 大
                ],  # 图例过渡颜色
                pos_left='190px',  # 图例水平位置
                pos_top='380px',  # 图例竖直位置
                is_piecewise=True,  # 图例分段
                split_number=8,  # 图例分段数量
                pieces=[
                    {'min': 29.5, 'label': '   > 29.5'},
                    {'min': 28.7, 'max': 29.5, 'label': '28.7 - 29.5'},
                    {'min': 27.9, 'max': 28.7, 'label': '27.9 - 28.7'},
                    {'min': 27.1, 'max': 27.9, 'label': '27.1 - 27.9'},
                    {'min': 26.3, 'max': 27.1, 'label': '26.3 - 27.1'},
                    {'min': 25.5, 'max': 26.3, 'label': '25.5 - 26.3'},
                    {'min': 24.7, 'max': 25.5, 'label': '24.7 - 25.5'},
                    {'max': 24.7, 'label': '   < 24.8'},
                ],  # 图例分段标签
                border_color='#000000',  # 边框颜色
                border_width=1,  # 边框宽度
                textstyle_opts=opts.TextStyleOpts(
                    color='#000000',  # 字体颜色
                    font_style='normal',  # 字体风格
                    font_weight='bold',  # 字体粗细
                    font_size=12,  # 字体大小
                ),  # 图例字体样式
            ),
        )  # 全局设置
    )

    return map_chart  # 返回图层


if __name__ == '__main__':

    timeline = Timeline(init_opts=opts.InitOpts(
        height='750px',  # 画布高度
        width='1125px',  # 画布宽度
        theme=ThemeType.LIGHT,  # 画布主题
    ))  # 实例化时间轴轮播图

    for year in YEAR:
        timeline.add(chart=add_chart_by_year(year), time_point=year)  # 按年份添加图层

    timeline.add_schema(
        is_auto_play=True,  # 自动播放
        play_interval=1000,  # 播放速度
        pos_left='center',  # 时间轴水平位置
        pos_bottom='60px',  # 时间轴竖直位置
        width='800px',  # 时间轴长度
        label_opts=opts.LabelOpts(is_show=True),  # 显示时间轴标签
    )  # 时间轴设置

    timeline.render(path=os.path.join(RESULT_PATH, 'GDP_map.html'))  # 渲染动图
