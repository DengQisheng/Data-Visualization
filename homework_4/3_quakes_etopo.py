import os  # 文件

import matplotlib.colors as colors  # 颜色
import matplotlib.pyplot as plt  # 绘图
import numpy as np  # 数组
import pandas as pd  # 数组
from mpl_toolkits.basemap import Basemap  # 地图

# 路径
HOME_PATH = os.getcwd()  # 主目录
DATA_PATH = os.path.join(HOME_PATH, 'data')  # 数据目录
RESULT_PATH = os.path.join(HOME_PATH, 'result')  # 结果目录

# 颜色
SunsetOrange = colors.LinearSegmentedColormap.from_list(
    name='SunsetOrange',
    colors=[
        '#FDEDBE',  # 浅 <-> 小
        '#FFDF80',
        '#FFCB33',
        '#FFB200',
        '#FF8C00',
        '#FF6500',
        '#E6450F',
        '#B22C00',
        '#661900',  # 深 <-> 大
    ],
)  # 橙色系
LeafYellow = colors.LinearSegmentedColormap.from_list(
    name='LeafYellow',
    colors=[
        '#FFEBB0',  # 浅 <-> 小
        '#FFDF80',
        '#FACA3E',
        '#E6B80B',
        '#B5AC23',
        '#6A9A48',
        '#20876B',
        '#06746B',
        '#044E48',  # 深 <-> 大
    ],
)  # 绿色系
GeekBlue = colors.LinearSegmentedColormap.from_list(
    name='GeekBlue',
    colors=[
        '#D2EDC8',  # 浅 <-> 小
        '#A9DACC',
        '#75C6D1',
        '#42B3D5',
        '#3993C2',
        '#3073AE',
        '#27539B',
        '#1E3388',
        '#171E6D',  # 深 <-> 大
    ],
)  # 蓝色系
GoldenPurple = colors.LinearSegmentedColormap.from_list(
    name='GoldenPurple',
    colors=[
        '#FACDAA',  # 浅 <-> 小
        '#F4A49E',
        '#EE7B91',
        '#E85285',
        '#BE408C',
        '#942D93',
        '#6A1B9A',
        '#56167D',
        '#42105F',  # 深 <-> 大
    ],
)  # 紫色系
COLOR = SunsetOrange  # 选择颜色

# 数据导入
NUM_QUAKES = 1000  # 数据数量
QUAKE = pd.read_csv(
    os.path.join(DATA_PATH, 'quakes.csv'),  # 读取文件
    index_col=0,  # 首列设为序号
    nrows=NUM_QUAKES,  # 读取数量
)  # 地震数据
LATITUDE = QUAKE['lat']  # 纬度
LONGITUDE = QUAKE['long']  # 经度
DEPTH = QUAKE['depth']  # 震源深度
MAGNITUDE = QUAKE['mag']  # 地震等级

if __name__ == "__main__":

    # 初始化画布
    plt.figure(figsize=(18, 18))  # 画布大小

    # 初始化地图
    fiji_map = Basemap(
        llcrnrlat=-42,  # 地图下边界纬度：42°S
        llcrnrlon=163,  # 地图左边界经度：163°E
        urcrnrlat=-8,  # 地图上边界纬度：8°S
        urcrnrlon=192,  # 地图右边界经度：172°W
        projection='cyl',  # 投影方式：等距圆柱投影
        resolution='f',  # 分辨率：最高
    )

    # 绘制浮雕地形图
    fiji_map.etopo(scale=2)  # NOAA地形图

    # 绘制线
    fiji_map.drawparallels(
        circles=np.arange(-40.0, 5.0, 5.0),  # 纬线间隔：5°
        color='aliceblue',  # 纬线颜色
        linewidth=2,  # 纬线宽度
        labels=[False, True, False, False],  # 纬线刻度：右边界
        fontsize=28,  # 刻度大小
        zorder=20,  # 图层位置：次顶层
    )  # 纬线
    fiji_map.drawmeridians(
        meridians=np.arange(165.0, 195.0, 5.0),  # 经线间隔：5°
        color='aliceblue',  # 经线颜色
        linewidth=2,  # 经线宽度
        labels=[False, False, False, True],  # 经线刻度：下边界
        fontsize=28,  # 刻度大小
        zorder=20,  # 图层位置：次顶层
    )  # 经线
    fiji_map.drawmapboundary(
        color='black',  # 边框颜色
        linewidth=2,  # 边框宽度
        zorder=30,  # 图层位置：最顶层
    )  # 边框

    # 绘制地震数据
    quakes_position = plt.scatter(
        x=LONGITUDE,  # 经度
        y=LATITUDE,  # 纬度
        s=np.power(10, MAGNITUDE * 0.7),  # 地震等级
        c=DEPTH,  # 震源深度
        marker='.',  # 震源标记
        cmap=COLOR,  # 震源深度图例颜色
        alpha=0.75,  # 震源标记透明度
        linewidths=1.5,  # 震源标记边缘线宽度
        edgecolors='white',  # 震源标记边缘线颜色
        zorder=10,  # 图层位置：次次顶层
    )  # 地震数据
    color_bar = fiji_map.colorbar(
        mappable=quakes_position,  # 映射对象：地震数据
        location='left',  # 图例位置：左边界
        size='6%',  # 图例宽度
        pad='2%',  # 图例距离
    )  # 震源深度图例
    color_bar.set_alpha(1)  # 图例透明度
    color_bar.draw_all()  # 渲染图例
    color_bar.outline.set_linewidth(2)  # 图例边框宽度
    color_bar.set_label(
        label='Focal Depth (km)',  # 标签文本
        labelpad=-180,  # 标签位置
        size=32,  # 标签大小
    )  # 图例标签
    color_bar.ax.tick_params(
        axis='y',  # 刻度方向
        direction='inout',  # 刻度线形式
        length=10,  # 刻度线长度
        width=2,  # 刻度线宽度
        pad=10,  # 刻度位置
        labelsize=28,  # 刻度大小
        left=True,  # 左刻度线
        right=False,  # 不显示右刻度线
        labelleft=True,  # 左刻度
        labelright=False,  # 不显示右刻度
    )  # 图例刻度

    # 绘制文本
    plt.title(
        label='Locations of Earthquakes near Fiji since 1964',  # 标题文本
        fontsize=40,  # 字体大小
        fontweight='bold',  # 字体宽度
        pad=50,  # 标题位置
    )  # 标题

    # 保存地图
    plt.savefig(
        fname=os.path.join(RESULT_PATH, 'quakes_etopo_%d.png' % NUM_QUAKES),  # 文件名
        dpi=240,  # 分辨率
    )  # 保存图像
    # plt.show()  # 显示图像
