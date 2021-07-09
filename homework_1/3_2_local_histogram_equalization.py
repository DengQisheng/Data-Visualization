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
        self.localMatrix = None    # 局部直方图均衡的灰度矩阵

        self.histogram = None    # 均衡前的图像直方图
        self.globalHistogram = None    # 全局直方图均衡后的图像直方图
        self.localHistogram = None    # 局部直方图均衡后的图像直方图

    def inputImage(self):
        image = Image.open(self.imagePath)    # 输入图像
        self.imageMatrix = np.array(image.convert('L'))    # 将图像转换成灰度矩阵
        self.imageHeight, self.imageWidth = self.imageMatrix.shape    # 图像大小
        self.histogram = np.histogram(self.imageMatrix.reshape(1, -1), range(257))[0]    # 计算均衡前的图像直方图

    def globalHistogramEqualization(self):    # 计算全局直方图均衡
        self.globalMatrix = copy.deepcopy(self.imageMatrix)    # 创建灰度矩阵的深拷贝
        mapping = {val: np.round(255 * np.sum(self.histogram[:val + 1]) / (self.imageHeight * self.imageWidth)) for val in range(256)}    # 全局直方图均衡
        for h in range(self.imageHeight):    # 遍历高方向
            for w in range(self.imageWidth):    # 遍历宽方向
                self.globalMatrix[h][w] = mapping[self.imageMatrix[h][w]]    # 映射均衡化后的像素值
        self.globalHistogram = np.histogram(self.globalMatrix.reshape(1, -1), range(257))[0]    # 计算全局均衡后的图像直方图

    def localHistogramEqualization(self):    # 计算局部直方图均衡
        self.localMatrix = copy.deepcopy(self.imageMatrix)    # 创建灰度矩阵的深拷贝
        roiHeight, roiWidth = 3, 3    # 感兴趣区域ROI的高和宽，规定为3*3邻域，能忽略边界造成的影响
        halfRoiHeight, halfRoiWidth = roiHeight // 2, roiWidth // 2    # 感兴趣区域ROI的半高和半宽
        roiHistogram = np.histogram(self.imageMatrix[:roiHeight, :roiWidth].reshape(1, -1), range(257))[0]    # 初始感兴趣区域ROI的直方图
        for h in range(self.imageHeight - roiHeight + 1):    # 遍历高方向，h代表感兴趣区域ROI的左上角纵坐标
            for w in range(self.imageWidth - roiWidth + 1):    # 遍历宽方向，w代表感兴趣区域ROI的左上角横坐标
                currentPixel = (halfRoiHeight + h, halfRoiWidth + w)    # 当前邻域中心像素位置
                currentValue = self.imageMatrix[currentPixel]    # 当前邻域中心像素值
                self.localMatrix[currentPixel] = np.round(255 * np.sum(roiHistogram[:currentValue + 1]) / (roiHeight * roiWidth))    # 映射均衡化后的像素值
                if w == self.imageWidth - roiWidth:    # 感兴趣区域ROI横向移动至末端，最后一次调用时处于越界状态，但不会对像素值赋值
                    roiHistogram = np.histogram(self.imageMatrix[h + 1:h + roiHeight + 1, :roiWidth].reshape(1, -1), range(257))[0]    # 计算次行首个感兴趣区域ROI的直方图
                else:    # 感兴趣区域ROI向右移动一个像素
                    roiHistogram -= np.histogram(self.imageMatrix[h:h + roiHeight, w], range(257))[0]    # 删除最左边一行
                    roiHistogram += np.histogram(self.imageMatrix[h:h + roiHeight, w + roiWidth], range(257))[0]    # 添加最右边一行
        self.localHistogram = np.histogram(self.localMatrix.reshape(1, -1), range(257))[0]    # 计算局部均衡后的图像直方图

    def outputHistogram(self):    # 可视化直方图
        plt.figure(figsize=(15, 5))    # 创建空白图像
        plt.subplot(1, 3, 1)    # 左子图
        plt.bar(range(256), self.histogram, width=1)    # 根据均衡前的直方图数据绘制直方图
        plt.title('Before HE', fontsize=10)    # 标注标题
        plt.xlabel('Intensity', fontsize=8)    # 标注x轴标签
        plt.ylabel('Frequency', fontsize=8)    # 标注y轴标签
        plt.xticks(range(0, 257, 64), fontsize=8)    # 设定x轴字号
        plt.yticks(fontsize=8)    # 设定y轴字号
        plt.subplot(1, 3, 2)    # 中子图
        plt.bar(range(256), self.globalHistogram, width=1)    # 根据全局均衡后的直方图数据绘制直方图
        plt.title('After GHE', fontsize=10)
        plt.xlabel('Intensity', fontsize=8)    # 标注x轴标签
        plt.ylabel('Frequency', fontsize=8)    # 标注y轴标签
        plt.xticks(range(0, 257, 64), fontsize=8)    # 设定x轴字号
        plt.yticks(fontsize=8)    # 设定y轴字号
        plt.subplots_adjust(wspace=0.5)    # 调整两子图间的距离
        plt.subplot(1, 3, 3)    # 右子图
        plt.bar(range(256), self.localHistogram, width=1)    # 根据全局均衡后的直方图数据绘制直方图
        plt.title('After LHE', fontsize=10)
        plt.xlabel('Intensity', fontsize=8)    # 标注x轴标签
        plt.ylabel('Frequency', fontsize=8)    # 标注y轴标签
        plt.xticks(range(0, 257, 64), fontsize=8)    # 设定x轴字号
        plt.yticks(fontsize=8)    # 设定y轴字号
        plt.subplots_adjust(wspace=0.3)    # 调整两子图间的距离
        plt.savefig(self.imageName + '_histogram_by_LHE.png', dpi=480)    # 导出两幅直方图为png文件，分辨率为480dpi
        # plt.show()    # 运行程序时显示直方图

    def outputImage(self):
        self.imageSplice = Image.new(mode='L', size=(self.imageWidth * 3, self.imageHeight))    # 生成空白拼接图像
        self.imageSplice.paste(im=Image.fromarray(self.imageMatrix))     # 生成灰度化图像
        self.imageSplice.paste(im=Image.fromarray(self.globalMatrix), box=(self.imageWidth, 0))     # 生成全局直方图均衡图像
        self.imageSplice.paste(im=Image.fromarray(self.localMatrix), box=(self.imageWidth * 2, 0))     # 生成局部直方图均衡图像
        self.imageSplice.save(self.imageName + '_by_local_histogram_equalization.png')    # 保存图像
        # self.imageSplice.show()    # 运行程序时显示图像

    def histogramProcessing(self):    # 计算直方图均衡的程序接口
        self.inputImage()    # 输入图像
        self.globalHistogramEqualization()    # 全局直方图均衡
        self.localHistogramEqualization()    # 局部直方图均衡
        self.outputHistogram()    # 输出直方图
        self.outputImage()    # 输出图像


if __name__ == '__main__':

    start = time.time()    # 程序开始运行时刻

    # 图像一
    imageName1 = 'square_noisy.tif'    # 图像的名称
    imageData1 = ImageData(imageName=imageName1)    # 实例化Image对象
    imageData1.histogramProcessing()    # 调用函数计算直方图均衡

    # 图像二
    imageName2 = 'lena_std.tif'    # 图像的名称
    imageData2 = ImageData(imageName=imageName2)    # 实例化Image对象
    imageData2.histogramProcessing()    # 调用函数计算直方图均衡

    end = time.time()    # 程序结束运行时刻

    print('Program execute time: %.2f s' % (end - start))    # 程序运行时长
