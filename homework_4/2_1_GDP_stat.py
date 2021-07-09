import csv  # 数据
import os  # 文件

import matplotlib.pyplot as plt  # 绘图
import numpy as np  # 数组

# 路径
HOME_PATH = os.getcwd()  # 主目录
DATA_PATH = os.path.join(HOME_PATH, 'data')  # 数据目录
RESULT_PATH = os.path.join(HOME_PATH, 'result')  # 结果目录

# 颜色
COLOR = [
    '#FF0000',  # 红色 (255, 0, 0)
    '#FF5200',  # 深橙色 (255, 82, 0)
    '#FFA500',  # 橙色 (255, 165, 0)
    '#00FF00',  # 绿色 (0, 255, 0)
    '#00D2D2',  # 青色 (0, 210, 210)
    '#006400',  # 深绿色 (0, 100, 0)
    '#64D2FF',  # 淡蓝色 (100, 210, 255)
    '#007FFF',  # 天蓝色 (0, 127, 255)
    '#0000FF',  # 蓝色 (0, 0, 255)
    '#808080',  # 灰色 (128, 128, 128)
]

# 标记
MARKER = [
    'o',  # 圆形
    'v',  # 倒三角形
    's',  # 正方形
    '^',  # 正三角形
    'D',  # 菱形
    '<',  # 左三角形
    'd',  # 窄菱形
    '>',  # 右三角形
    'x',  # 十字形
    'p',  # 正五边形
]

# 数据数量
NUM_COUNTRIES = 10  # 1 <= NUM_COUNTRIES <= 10

# 数据导入
with open(os.path.join(DATA_PATH, 'GDP.csv'), 'r') as csv_file:  # 打开csv文件
    csv_reader = csv.reader(csv_file, delimiter=',')  # 读取csv文件
    csv_reader.__next__()  # 跳过首行标题行
    data = np.array([next(csv_reader) for _ in range(NUM_COUNTRIES)])  # 提取前NUM_COUNTRIES个国家的数据

# 年份
YEAR = [year for year in range(1996, 2017)]  # 1996-2016

# 国家
COUNTRY = data[:, 0]

# GDP
GDP = data[:, 2:].astype(np.float) / 10e12  # 单位为trillion


# 折线图
def plot_line_chart():
    plt.figure(num=1, figsize=(10, 8))  # 创建新图片
    for rank in range(NUM_COUNTRIES):
        plt.plot(
            YEAR,  # 年份
            GDP[rank],  # GDP总量
            label=COUNTRY[rank],  # 国家
            color=COLOR[rank],  # 颜色
            marker=MARKER[rank],  # 标记
            markersize=6,  # 标记大小
            linestyle='-',  # 折线形式
            linewidth=1  # 折线粗细
        )
    plt.title('Country GDP 1996-2016')  # 标题
    plt.xlabel('Year')  # X轴标签
    plt.ylabel('GDP (Trillions of US$)')  # Y轴标签
    plt.grid(ls='--')  # 背景网格
    plt.xticks(ticks=YEAR[::5])  # X轴刻度
    plt.yticks(
        ticks=[0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75],  # Y轴刻度位置
        labels=[0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75]  # Y轴刻度标签
    )  # Y轴刻度
    plt.legend(loc='best')  # 图例
    plt.savefig(os.path.join(RESULT_PATH, 'GDP_stat_line.png'))  # 保存折线图
    # plt.show()  # 显示折线图


# 折线图（对数坐标）
def plot_line_log_chart():
    _, axis = plt.subplots(num=3, figsize=(10, 8))  # 创建新图片
    axis.set_yscale('log')  # 对数坐标
    for rank in range(NUM_COUNTRIES):
        plt.plot(
            YEAR,  # 年份
            GDP[rank],  # GDP总量
            label=COUNTRY[rank],  # 国家
            color=COLOR[rank],  # 颜色
            marker=MARKER[rank],  # 标记
            markersize=6,  # 标记大小
            linestyle='-',  # 折线形式
            linewidth=1  # 折线粗细
        )
    plt.title('Country GDP 1996-2016')  # 标题
    plt.xlabel('Year')  # X轴标签
    plt.ylabel('GDP (Trillions of US$)')  # Y轴标签
    plt.grid(ls='--', which='both')  # 背景网格
    plt.xticks(ticks=YEAR[::5])  # X轴刻度
    plt.yticks(
        ticks=[0.05, 0.1, 0.5, 1, 2],  # Y轴刻度位置
        labels=[0.05, 0.1, 0.5, 1, 2]  # Y轴刻度标签
    )  # Y轴刻度
    plt.legend(loc='best')  # 图例
    plt.savefig(os.path.join(RESULT_PATH, 'GDP_stat_line_log.png'))  # 保存折线图
    # plt.show()  # 显示折线图


# 折线图（除中美）
def plot_line_chart_except_USA_and_China():
    plt.figure(num=5, figsize=(10, 8))  # 创建新图片
    for rank in range(2, NUM_COUNTRIES):
        plt.plot(
            YEAR,  # 年份
            GDP[rank],  # GDP总量
            label=COUNTRY[rank],  # 国家
            color=COLOR[rank],  # 颜色
            marker=MARKER[rank],  # 标记
            markersize=6,  # 标记大小
            linestyle='-',  # 折线形式
            linewidth=1  # 折线粗细
        )
    plt.title('Country GDP 1996-2016')  # 标题
    plt.xlabel('Year')  # X轴标签
    plt.ylabel('GDP (Trillions of US$)')  # Y轴标签
    plt.grid(ls='--')  # 背景网格
    plt.xticks(ticks=YEAR[::5])  # X轴刻度
    plt.legend(loc='best', ncol=2)  # 图例
    plt.savefig(os.path.join(RESULT_PATH, 'GDP_stat_line_except_USA_and_China.png'))  # 保存折线图
    # plt.show()  # 显示折线图


# 散点图
def plot_scatter_chart():
    plt.figure(num=2, figsize=(10, 8))  # 创建新图片
    for rank in range(NUM_COUNTRIES):
        plt.plot(
            YEAR,  # 年份
            GDP[rank],  # GDP总量
            label=COUNTRY[rank],  # 国家
            color=COLOR[rank],  # 颜色
            marker=MARKER[rank],  # 标记
            markersize=6,  # 标记大小
            linestyle=''  # 散点形式
        )
    plt.title('Country GDP 1996-2016')  # 标题
    plt.xlabel('Year')  # X轴标签
    plt.ylabel('GDP (Trillions of US$)')  # Y轴标签
    plt.grid(ls='--')  # 背景网格
    plt.xticks(ticks=YEAR[::5])  # X轴刻度
    plt.yticks(
        ticks=[0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75],  # Y轴刻度位置
        labels=[0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75]  # Y轴刻度标签
    )  # Y轴刻度
    plt.legend(loc='best')  # 图例
    plt.savefig(os.path.join(RESULT_PATH, 'GDP_stat_scatter.png'))  # 保存折线图
    # plt.show()  # 显示折线图


# 散点图（对数坐标）
def plot_scatter_log_chart():
    _, axis = plt.subplots(num=4, figsize=(10, 8))  # 创建新图片
    axis.set_yscale('log')  # 对数坐标
    for rank in range(NUM_COUNTRIES):
        plt.plot(
            YEAR,  # 年份
            GDP[rank],  # GDP总量
            label=COUNTRY[rank],  # 国家
            color=COLOR[rank],  # 颜色
            marker=MARKER[rank],  # 标记
            markersize=6,  # 标记大小
            linestyle=''  # 散点形式
        )
    plt.title('Country GDP 1996-2016')  # 标题
    plt.xlabel('Year')  # X轴标签
    plt.ylabel('GDP (Trillions of US$)')  # Y轴标签
    plt.grid(ls='--', which='both')  # 背景网格
    plt.xticks(ticks=YEAR[::5])  # X轴刻度
    plt.yticks(
        ticks=[0.05, 0.1, 0.5, 1, 2],  # Y轴刻度位置
        labels=[0.05, 0.1, 0.5, 1, 2]  # Y轴刻度标签
    )  # Y轴刻度
    plt.legend(loc='best')  # 图例
    plt.savefig(os.path.join(RESULT_PATH, 'GDP_stat_scatter_log.png'))  # 保存折线图
    # plt.show()  # 显示折线图


# 散点图（除中美）
def plot_scatter_chart_except_USA_and_China():
    plt.figure(num=6, figsize=(10, 8))  # 创建新图片
    for rank in range(2, NUM_COUNTRIES):
        plt.plot(
            YEAR,  # 年份
            GDP[rank],  # GDP总量
            label=COUNTRY[rank],  # 国家
            color=COLOR[rank],  # 颜色
            marker=MARKER[rank],  # 标记
            markersize=6,  # 标记大小
            linestyle=''  # 散点形式
        )
    plt.title('Country GDP 1996-2016')  # 标题
    plt.xlabel('Year')  # X轴标签
    plt.ylabel('GDP (Trillions of US$)')  # Y轴标签
    plt.grid(ls='--')  # 背景网格
    plt.xticks(ticks=YEAR[::5])  # X轴刻度
    plt.legend(loc='best', ncol=2)  # 图例
    plt.savefig(os.path.join(RESULT_PATH, 'GDP_stat_scatter_except_USA_and_China.png'))  # 保存折线图
    # plt.show()  # 显示折线图


if __name__ == "__main__":
    plot_line_chart()  # 折线图
    plot_line_log_chart()  # 折线图（对数坐标）
    plot_line_chart_except_USA_and_China()  # 折线图（除中美）
    plot_scatter_chart()  # 散点图
    plot_scatter_log_chart()  # 散点图（对数坐标）
    plot_scatter_chart_except_USA_and_China()  # 散点图（除中美）