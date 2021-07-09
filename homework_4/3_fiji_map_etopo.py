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

    # 绘制文本
    plt.title(
        label='Map near Fiji',  # 标题文本
        fontsize=40,  # 字体大小
        fontweight='bold',  # 字体宽度
        pad=50,  # 标题位置
    )  # 标题

    # 保存地图
    plt.savefig(
        fname=os.path.join(RESULT_PATH, 'map_near_fiji_etopo.png'),  # 文件名
        dpi=240,  # 分辨率
    )  # 保存图像
    # plt.show()  # 显示图像
