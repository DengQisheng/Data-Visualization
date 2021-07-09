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
        self.imageMatrix = None    # 图像的灰度矩阵

    def inputImage(self):
        image = Image.open(self.imagePath)    # 输入图像
        self.imageMatrix = np.array(image.convert('L'))    # 将图像转换成灰度矩阵
        self.imageHeight, self.imageWidth = self.imageMatrix.shape    # 图像大小

    def evaluateHistogram(self):    # 计算局部直方图数据并可视化直方图

        # 计算局部直方图
        localMatrix = copy.deepcopy(self.imageMatrix)    # 创建灰度矩阵的深拷贝
        roiHeight, roiWidth = 3, 3    # 感兴趣区域ROI的高和宽，规定为3*3邻域，能忽略边界造成的影响
        halfRoiHeight, halfRoiWidth = roiHeight // 2, roiWidth // 2    # 感兴趣区域ROI的半高和半宽
        roiHistogram = np.histogram(self.imageMatrix[:roiHeight, :roiWidth].reshape(1, -1), range(257))[0]    # 初始感兴趣区域ROI的直方图
        for h in range(self.imageHeight - roiHeight + 1):    # 遍历高方向，h代表感兴趣区域ROI的左上角纵坐标
            for w in range(self.imageWidth - roiWidth + 1):    # 遍历宽方向，w代表感兴趣区域ROI的左上角横坐标
                currentPixel = (halfRoiHeight + h, halfRoiWidth + w)    # 当前邻域中心像素位置
                currentValue = self.imageMatrix[currentPixel]    # 当前邻域中心像素值
                localMatrix[currentPixel] = np.round(255 * np.sum(roiHistogram[:currentValue + 1]) / (roiHeight * roiWidth))    # 映射均衡化后的像素值
                if w == self.imageWidth - roiWidth:    # 感兴趣区域ROI横向移动至末端，最后一次调用时处于越界状态，但不会对像素值赋值
                    roiHistogram = np.histogram(self.imageMatrix[h + 1:h + roiHeight + 1, :roiWidth].reshape(1, -1), range(257))[0]    # 计算次行首个感兴趣区域ROI的直方图
                else:    # 感兴趣区域ROI向右移动一个像素
                    roiHistogram -= np.histogram(self.imageMatrix[h:h + roiHeight, w], range(257))[0]    # 删除最左边一行
                    roiHistogram += np.histogram(self.imageMatrix[h:h + roiHeight, w + roiWidth], range(257))[0]    # 添加最右边一行
        histogram = np.histogram(localMatrix.reshape(1, -1), range(257))[0]    # 计算局部均衡后的图像直方图

        # 可视化直方图
        plt.figure()    # 创建空白图像
        plt.bar(range(256), histogram, width=1)    # 根据直方图数据绘制直方图
        plt.title('Local Histogram Equalization', fontsize=10)    # 标注标题
        plt.xlabel('Intensity', fontsize=8)    # 标注x轴标签
        plt.ylabel('Frequency', fontsize=8)    # 标注y轴标签
        plt.xticks(range(0, 257, 64), fontsize=8)    # 设定x轴字号
        plt.yticks(fontsize=8)    # 设定y轴字号
        plt.savefig(self.imageName + '_histogram_by_local_histogram_algorithm.png', dpi=480)    # 导出直方图为png文件，分辨率为480dpi
        # plt.show()    # 运行程序时显示直方图

    def localHistogram(self):
        self.inputImage()    # 输入图像
        self.evaluateHistogram()    # 计算局部直方图


if __name__ == '__main__':

    start = time.time()    # 程序开始运行时刻

    imageName = 'lena_std.tif'    # 图像的名称
    imageData = ImageData(imageName=imageName)    # 实例化Image对象
    imageData.localHistogram()    # 调用函数生成局部直方图

    end = time.time()    # 程序结束运行时刻

    print('Program execute time: %.2f s' % (end - start))    # 程序运行时长
