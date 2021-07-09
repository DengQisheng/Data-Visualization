import copy    # 复制操作
import os  # 文件操作
import time    # 时间操作

import numpy as np  # 数组操作
from PIL import Image  # 图像操作


class ImageData:

    def __init__(self, imageName):
        self.imageName = imageName.split('.')[0]    # 图像的名称
        self.imagePath = os.getcwd() + '\\' + imageName    # 图像的路径
        self.imageHeight = None    # 图像的高
        self.imageWidth = None    # 图像的宽
        self.imageSplice = None    # 空白拼接图像
        self.imageMatrix = None    # 图像的灰度矩阵
        self.transMatrix = None    # 分段线性变换的灰度矩阵

    def inputImage(self):
        image = Image.open(self.imagePath)    # 输入图像
        self.imageMatrix = np.array(image.convert('L'))    # 将图像转换成灰度矩阵
        self.imageHeight, self.imageWidth = self.imageMatrix.shape    # 图像大小

    def piecewiseLinearTransformation(self, r1=85, r2=170, k=0.4):    # 应用分段线性变换处理图像
        assert 0 <= r1 <= r2 <= 255 and k >= 0, 'wrong parameters'    # 给定参数范围，为了完成对比度拉伸的效果，k需要小于1
        self.transMatrix = copy.deepcopy(self.imageMatrix)    # 创建灰度矩阵的深拷贝
        for h in range(self.imageHeight):    # 遍历高方向
            for w in range(self.imageWidth):    # 遍历宽方向
                val = self.imageMatrix[h][w]    # 某点的灰度值
                if val < r1:
                    val = val * k    # 将暗端调暗
                elif r1 <= val < r2:
                    val = val * k + 255 * (1 - k) * (val - r1) / (r2 - r1)    # 提高对比度
                else:
                    val = val * k + 255 * (1 - k)    # 将亮端调亮
                self.transMatrix[h][w] = val    # 处理后的灰度值

    def outputImage(self):
        self.imageSplice = Image.new(mode='L', size=(self.imageWidth * 2, self.imageHeight))    # 生成空白拼接图像
        self.imageSplice.paste(im=Image.fromarray(self.imageMatrix))     # 生成灰度化图像
        self.imageSplice.paste(im=Image.fromarray(self.transMatrix), box=(self.imageWidth, 0))     # 生成分段线性变换图像
        self.imageSplice.save(self.imageName + '_by_image_contrast_stretching.png')    # 保存图像
        # self.imageSplice.show()    # 运行程序时显示图像

    def imageContrastStretching(self):    # 图像对比度拉伸的程序接口
        self.inputImage()    # 输入图像
        self.piecewiseLinearTransformation()    # 分段线性变换对比度拉伸
        self.outputImage()    # 输出图像


if __name__ == '__main__':

    start = time.time()    # 程序开始运行时刻

    imageName = 'lena_std.tif'    # 图像的名称
    imageData = ImageData(imageName=imageName)    # 实例化Image对象
    imageData.imageContrastStretching()    # 调用函数处理对比度拉伸

    end = time.time()    # 程序结束运行时刻

    print('Program execute time: %.2f s' % (end - start))    # 程序运行时长
