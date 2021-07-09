import copy    # 复制操作
import os    # 文件操作
import time    # 时间操作

import numpy as np    # 数组操作
from matplotlib import pyplot as plt    # 绘图操作
from PIL import Image    # 图像操作


class ImageData:

    def __init__(self, imageName):
        self.imageName = imageName.split('.')[0]    # 图像的名称
        self.imagePath = os.getcwd() + '\\' + imageName    # 图像的路径
        self.imageHeight = None    # 图像的高
        self.imageWidth = None    # 图像的宽
        self.imageSplice = None    # 空白拼接图像

        self.imageMatrix = None    # 图像的灰度矩阵
        self.globalMatrix = None    # 全局直方图均衡的灰度矩阵

        self.histogram = None    # 均衡前的图像直方图
        self.globalHistogram = None    # 全局直方图均衡后的图像直方图

    def inputImage(self):
        image = Image.open(self.imagePath)    # 输入图像
        self.imageMatrix = np.array(image.convert('L'))    # 将图像转换成灰度矩阵
        self.imageHeight, self.imageWidth = self.imageMatrix.shape    # 图像大小
        self.histogram = np.histogram(self.imageMatrix.reshape(1, -1), range(257))[0]    # 计算均衡前的图像直方图

    def histogramEqualization(self):    # 计算全局直方图均衡
        self.globalMatrix = copy.deepcopy(self.imageMatrix)    # 创建灰度矩阵的深拷贝
        mapping = {val: np.round(255 * np.sum(self.histogram[:val + 1]) / (self.imageHeight * self.imageWidth)) for val in range(256)}    # 全局直方图均衡
        for h in range(self.imageHeight):    # 遍历高方向
            for w in range(self.imageWidth):    # 遍历宽方向
                self.globalMatrix[h][w] = mapping[self.imageMatrix[h][w]]    # 映射均衡化后的像素值
        self.globalHistogram = np.histogram(self.globalMatrix.reshape(1, -1), range(257))[0]    # 计算均衡后的图像直方图

    def outputHistogram(self):    # 可视化直方图
        plt.figure()    # 创建空白图像
        plt.subplot(1, 2, 1)    # 左子图
        plt.bar(range(256), self.histogram, width=1)    # 根据均衡前的直方图数据绘制直方图
        plt.title('Before Histogram Equalization', fontsize=10)    # 标注标题
        plt.xlabel('Intensity', fontsize=7)    # 标注x轴标签
        plt.ylabel('Frequency', fontsize=7)    # 标注y轴标签
        plt.xticks(range(0, 257, 32), fontsize=7)    # 设定x轴字号
        plt.yticks(fontsize=7)    # 设定y轴字号
        plt.subplot(1, 2, 2)    # 右子图
        plt.bar(range(256), self.globalHistogram, width=1)    # 根据均衡后的直方图数据绘制直方图
        plt.title('After Histogram Equalization', fontsize=10)
        plt.xlabel('Intensity', fontsize=7)    # 标注x轴标签
        plt.ylabel('Frequency', fontsize=7)    # 标注y轴标签
        plt.xticks(range(0, 257, 32), fontsize=7)    # 设定x轴字号
        plt.yticks(fontsize=7)    # 设定y轴字号
        plt.subplots_adjust(wspace=0.5)    # 调整两子图间的距离
        plt.savefig(self.imageName + '_histogram_by_GHE.png', dpi=480)    # 导出两幅直方图为png文件，分辨率为480dpi
        # plt.show()    # 运行程序时显示直方图

    def outputImage(self):
        self.imageSplice = Image.new(mode='L', size=(self.imageWidth * 2, self.imageHeight))    # 生成空白拼接图像
        self.imageSplice.paste(im=Image.fromarray(self.imageMatrix))     # 生成灰度化图像
        self.imageSplice.paste(im=Image.fromarray(self.globalMatrix), box=(self.imageWidth, 0))     # 生成直方图均衡图像
        self.imageSplice.save(self.imageName + '_by_global_histogram_equalization.png')    # 保存图像
        # self.imageSplice.show()    # 运行程序时显示图像

    def histogramProcessing(self):    # 计算直方图均衡的程序接口
        self.inputImage()    # 输入图像
        self.histogramEqualization()    # 全局直方图均衡
        self.outputHistogram()    # 输出直方图
        self.outputImage()    # 输出图像


if __name__ == '__main__':

    start = time.time()    # 程序开始运行时刻

    imageName = 'lena_std.tif'    # 图像的名称
    imageData = ImageData(imageName=imageName)    # 实例化Image对象
    imageData.histogramProcessing()    # 调用函数计算直方图均衡

    end = time.time()    # 程序结束运行时刻

    print('Program execute time: %.2f s' % (end - start))    # 程序运行时长
