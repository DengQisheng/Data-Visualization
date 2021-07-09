import os  # 文件操作
import time  # 时间操作

import numpy as np  # 数组操作
from PIL import Image  # 图像操作


class ImageData:

    # 初始化实例
    def __init__(self, image_name):
        self.image_name = image_name.split('.')[0]  # 图像的名称
        self.image_path = os.getcwd() + '\\' + image_name  # 图像的路径

    # 图像输入
    def input_image(self):
        image = Image.open(self.image_path)  # 输入图像
        self.image_matrix = np.array(image.convert('L'))  # 将图像转换成灰度矩阵
        self.image_shape = self.image_matrix.shape  # 图像的形状
        self.image_height, self.image_width = self.image_shape  # 图像的高与宽

    # 基本全局阈值算法
    def global_threshoding(self):
        histogram = np.histogram(self.image_matrix, range(257))[0]  # 计算图像的全局直方图
        t_star = int(np.average(np.arange(256), weights=histogram))  # 设定初始全局阈值
        t, iteration = 0, 0  # 记录全局阈值与迭代次数
        while np.abs(t - t_star) > 1 and iteration < 10000:  # 最小阈值差值设为1，设定迭代上限防止死循环
            t = t_star  # 当前全局阈值
            m_1 = int(np.average(np.arange(t), weights=histogram[:t]))  # G_1像素组的灰度均值
            m_2 = int(np.average(np.arange(t, 256), weights=histogram[t:]))  # G_2像素组的灰度均值
            t_star = int(0.5 * (m_1 + m_2))  # 计算新的全局阈值
            iteration += 1  # 记录迭代次数
        self.global_matrix = np.where(self.image_matrix > t_star, 255, 0)  # 图像二值化处理

    # 图像输出
    def output_image(self):
        image_splice = Image.new(mode='L', size=(self.image_width * 2 + 48, self.image_height + 32), color=215)  # 生成空白拼接图像
        image_splice.paste(im=Image.fromarray(self.image_matrix), box=(16, 16))  # 生成原图灰度化图像
        image_splice.paste(im=Image.fromarray(self.global_matrix), box=(self.image_width + 32, 16))  # 生成全局阈值处理图像
        image_splice.save(self.image_name + '_by_global_threshoding.png')  # 保存图像
        # image_splice.show()  # 运行程序时显示图像

    # 图像分割处理接口
    def image_segmentation(self):

        # 输入
        self.input_image()  # 输入图像

        # 基本全局阈值处理
        self.global_threshoding()  # 调用基本全局阈值算法

        # 输出
        self.output_image()  # 输出图像


if __name__ == '__main__':

    print()  # 空行

    # 处理图像: noisy_fingerprint.tif
    image_name = 'noisy_fingerprint.tif'  # 图像的名称
    image_data = ImageData(image_name=image_name)  # 实例化ImageData对象
    print('Image: %s\n' % image_name)  # 实例的名称

    # 基本全局阈值算法
    start = time.time()  # 实例开始测试时刻
    image_data.image_segmentation()  # 调用基本全局阈值算法进行图像分割
    end = time.time()  # 实例结束测试时刻
    print('Program execute time: %.2f s\n' % (end - start))  # 实例测试时长
