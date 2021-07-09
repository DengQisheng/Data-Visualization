import itertools  # 迭代操作
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
        self.image_size = self.image_matrix.size  # 图像的面积
        self.image_shape = self.image_matrix.shape  # 图像的形状
        self.image_height, self.image_width = self.image_shape  # 图像的高与宽

    # 任意区域OTSU算法
    def region_otsu(self, matrix):
        region_histogram = np.histogram(matrix, range(257))[0] / matrix.size  # 计算区域的归一化直方图
        prob_K = np.cumsum(region_histogram)  # 计算区域的累积和P1(k)，256维行向量
        mean_K = np.cumsum(region_histogram * np.array(range(256)))  # 计算区域的累积均值m(k)，256维行向量
        mean_G = mean_K[-1]  # 计算区域的灰度均值mG，标量
        epsilon = 1e-7  # 防止方差出现nan值，标量
        var_B_K = (mean_G * prob_K - mean_K)**2 / ((prob_K + epsilon) * (1 - prob_K - epsilon))  # 计算区域的类间方差sigmaB^2(k)，256维行向量
        k_star = int(np.mean(np.where(var_B_K == np.nanmax(var_B_K[1:-1]))))  # 找到最大化类间方差的k值平均值
        return np.where(matrix > k_star, 255, 0)  # 图像二值化处理

    # 全局OTSU算法
    def global_otsu(self):
        self.global_otsu_matrix = self.region_otsu(self.image_matrix)  # 应用OTSU算法的最佳全局阈值处理

    # 局部OTSU算法
    def local_otsu(self, height, width):
        self.local_adaptive_matrix = np.zeros(self.image_shape)  # 新建图像矩阵
        horizontal = zip(range(0, self.image_width, width), range(width, self.image_width + width, width))  # 将图像横向切割为等宽窗口，边界除外
        vertical = zip(range(0, self.image_height, height), range(height, self.image_height + height, height))  # 将图像纵向切割为等高窗口，边界除外
        for (hl, hr), (vt, vb) in itertools.product(horizontal, vertical):  # 将图像划分为等大小窗口，边界除外
            self.local_adaptive_matrix[vt:vb, hl:hr] = self.region_otsu(self.image_matrix[vt:vb, hl:hr])  # 应用OTSU算法的局部阈值处理

    # 移动平均算法
    def moving_average(self, length, const):

        # 输入阶段
        mean = np.zeros(self.image_shape)  # 新建均值矩阵
        mean[::2, :] = self.image_matrix[::2, :]  # 偶数行不变
        mean[1::2, :] = self.image_matrix[1::2, ::-1]  # 奇数行翻转
        mean = mean.reshape(-1)  # 将Z字形矩阵转换成均值数组

        # 输出阶段
        threshold = np.concatenate((mean[:length], (mean[length:self.image_size] - mean[:self.image_size - length]) / length))  # 新建阈值数组
        threshold[length - 1:] = np.cumsum(threshold[length - 1:])  # 计算移动平均
        threshold = threshold.reshape(self.image_shape)  # 将阈值数组转换成阈值矩阵
        threshold[1::2, :] = threshold[1::2, ::-1]  # 奇数行翻转

        self.local_adaptive_matrix = np.where(self.image_matrix > const * threshold, 255, 0)  # 图像二值化处理

    # 图像输出
    def output_image(self):
        image_splice = Image.new(mode='L', size=(self.image_width * 3 + 64, self.image_height + 32), color=215)  # 生成空白拼接图像
        image_splice.paste(im=Image.fromarray(self.image_matrix), box=(16, 16))  # 生成原图灰度化图像
        image_splice.paste(im=Image.fromarray(self.global_otsu_matrix), box=(self.image_width + 32, 16))  # 生成全局OTSU处理图像
        image_splice.paste(im=Image.fromarray(self.local_adaptive_matrix), box=(self.image_width * 2 + 48, 16))  # 生成局部可变阈值处理图像
        image_splice.save(self.image_name + '_by_' + self.mode + '.png')  # 保存图像
        # image_splice.show()  # 运行程序时显示图像

    # 局部阈值处理接口
    def adaptive_threshoding(self, mode='moving_average', height=512, width=512, length=20, const=0.5):

        # 输入
        self.input_image()  # 输入图像

        # 全局阈值处理
        self.global_otsu()  # 调用全局OTSU算法

        # 局部可变阈值处理
        self.mode = mode  # 局部阈值处理的模式
        if mode == 'local_otsu':
            self.local_otsu(height, width)  # 调用局部OTSU算法
        elif mode == 'moving_average':
            self.moving_average(length, const)  # 调用移动平均算法
        else:
            raise BaseException('wrong mode')  # 抛出模式错误异常

        # 输出
        self.output_image()  # 输出图像


if __name__ == '__main__':

    print()  # 空行

    # 处理图像: writing_round.tif
    image_name = 'writing_round.tif'  # 图像的名称
    image_data = ImageData(image_name=image_name)  # 实例化ImageData对象
    print('Image: %s\n' % image_name)  # 实例的名称

    # 局部OTSU算法
    start = time.time()  # 实例开始测试时刻
    image_data.adaptive_threshoding(mode='local_otsu', height=50, width=50)  # 调用局部OTSU算法进行局部可变阈值处理
    end = time.time()  # 实例结束测试时刻
    print('Processing mode: %s' % 'local OTSU')  # 实例测试的算法
    print('Program execute time: %.2f s\n' % (end - start))  # 实例测试时长

    # 移动平均算法
    start = time.time()  # 实例开始测试时刻
    image_data.adaptive_threshoding(mode='moving_average', length=20, const=0.5)  # 调用移动平均算法进行局部可变阈值处理
    end = time.time()  # 实例结束测试时刻
    print('Processing mode: %s' % 'moving average')  # 实例测试的算法
    print('Program execute time: %.2f s\n' % (end - start))  # 实例测试时长

    print()  # 空行

    # 处理图像: writing_stripe.tif
    image_name = 'writing_stripe.tif'  # 图像的名称
    image_data = ImageData(image_name=image_name)  # 实例化ImageData对象
    print('Image: %s\n' % image_name)  # 实例的名称

    # 局部OTSU算法
    start = time.time()  # 实例开始测试时刻
    image_data.adaptive_threshoding(mode='local_otsu', height=350, width=16)  # 调用局部OTSU算法进行局部可变阈值处理
    end = time.time()  # 实例结束测试时刻
    print('Processing mode: %s' % 'local OTSU')  # 实例测试的算法
    print('Program execute time: %.2f s\n' % (end - start))  # 实例测试时长

    # 移动平均算法
    start = time.time()  # 实例开始测试时刻
    image_data.adaptive_threshoding(mode='moving_average', length=20, const=0.5)  # 调用移动平均算法进行局部可变阈值处理
    end = time.time()  # 实例结束测试时刻
    print('Processing mode: %s' % 'moving average')  # 实例测试的算法
    print('Program execute time: %.2f s\n' % (end - start))  # 实例测试时长
