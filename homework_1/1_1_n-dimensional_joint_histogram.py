import os    # 文件操作
import time    # 时间操作

import numpy as np    # 数组操作
import seaborn as sns    # 二维联合直方图（热力图）绘制
from matplotlib import pyplot as plt    # 绘图操作


class Data:

    def __init__(self, dataName):
        self.dataName = dataName.split('.')[0]    # 图像的名称
        self.dataPath = os.getcwd() + '\\' + dataName    # 数据集的文件路径
        self.dataSet = None    # 数据集的读入数据
        self.dataType = np.int    # 数据集的数据类型，测试集的数据类型为整型
        self.dimension = None    # 数据集的维度，即联合直方图的维度

    def inputData(self):    # 读入数据集
        self.dataSet = np.loadtxt(fname=self.dataPath, dtype=self.dataType, delimiter=',')    # 数据集的格式为csv，分隔符为逗号
        self.dimension = self.dataSet.shape[1]    # 数据形式为n维行向量，shape[1]表示列数，即数据的维度

    def evaluateHistogram(self):    # 计算直方图数据并可视化直方图

        # 计算直方图
        maxVal = np.amax(self.dataSet, axis=0)    # 数据各维度的最大值
        minVal = np.amin(self.dataSet, axis=0)    # 数据各维度的最小值
        binLen = 3 * np.ones(shape=self.dimension, dtype=np.int)    # 直方图组距，不能取过小数值，否则会导致数据聚集在边界上
        binNum = ((maxVal - minVal) / binLen + 1).astype(np.int)    # 直方图组数，向下取为整数
        histogram = np.zeros([var for var in binNum[::-1]], dtype=np.int)    # 储存直方图数据的n维数组，大小为各维度组数之积，初始值为0
        for val in self.dataSet:    # 遍历数据集的行向量
            binNo = []    # 该行向量在直方图中的n维坐标
            for index in range(self.dimension):    # 遍历行向量的各维度分量，以索引形式访问
                loc = int((val[index] - minVal[index]) / binLen[index])    # 计算变量的组号，区间左闭右开，组号从0到组数减1
                loc = max(loc, 0)    # 边界检查，组号不能小于0
                loc = min(loc, binNum[index] - 1)    # 边界检查，组号不能大于组数减1
                binNo.append(loc)    # 储存分量的组号，注意组号的顺序
            histogram[tuple(binNo[::-1])] += 1    # 在行向量的位置记录数据

        # 可视化直方图
        if self.dimension == 2:    # 二维联合直方图的可视化
            sns.heatmap(data=histogram, cmap=sns.color_palette('Blues_r', 240),    # 借助颜色可视化频数，人眼难以分辨240种颜色，可以视为连续分布
                        annot=True, annot_kws={'size': 7}, fmt='d', linewidths=1,    # 标注频数
                        xticklabels=list(np.arange(minVal[0] + binLen[0] // 2, minVal[0] + binLen[0] // 2 + binLen[0] * binNum[0], binLen[0]).astype(np.int)),    # 标注x轴组中值
                        yticklabels=list(np.arange(minVal[1] + binLen[1] // 2, minVal[1] + binLen[1] // 2 + binLen[1] * binNum[1], binLen[1]).astype(np.int)))    # 标注y轴组中值
            plt.title('Height vs. Weight Joint Histogram', fontsize=10)    # 标注标题
            plt.xlabel('Height (cm)', fontsize=7)    # 标注x轴标签
            plt.ylabel('Weight (kg)', fontsize=7)    # 标注y轴标签
            plt.xticks(fontsize=7)    # 设定x轴字号
            plt.yticks(fontsize=7)    # 设定y轴字号
            plt.savefig(self.dataName + '_two-dimensional_joint_histogram.png', dpi=480)    # 导出直方图为png文件，分辨率为480dpi
            # plt.show()    # 运行程序时显示直方图
        else:    # histogram保存了直方图数据，可进行下一步计算
            pass    # 更高维联合直方图的可视化待补充

    def nDJointHistogram(self):    # 计算n维联合直方图的程序接口
        self.inputData()    # 读入数据
        self.evaluateHistogram()    # 计算直方图


if __name__ == '__main__':

    start = time.time()    # 程序开始运行时刻

    dataName = 'height_vs_weight.csv'    # 数据集的名称
    data = Data(dataName=dataName)    # 实例化Data对象
    data.nDJointHistogram()    # 调用函数计算n维联合直方图

    end = time.time()    # 程序结束运行时刻

    print('Program execute time: %.2f s' % (end - start))    # 程序运行时长
