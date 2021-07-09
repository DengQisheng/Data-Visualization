import os  # 文件操作
import time  # 时间操作

import numpy as np  # 数组操作
from PIL import Image  # 图像操作


class ImageData:

    # 初始化
    def __init__(self, image_name):
        self.image_name = image_name  # 图像的名称

    # 矩阵标定化
    def normalize(self, matrix):
        positive_matrix = matrix - np.min(matrix)  # 平移至非负值
        return (255 * positive_matrix / np.max(positive_matrix)).astype(int)  # 映射至[0, 255]

    # 图像输入
    def input_image(self):
        image = Image.open(os.getcwd() + '\\' + self.image_name)  # 输入图像
        self.image_matrix = np.array(image.convert('L'))  # 将图像转换成灰度矩阵
        self.image_size = self.image_matrix.size  # 图像的面积
        self.image_shape = self.image_matrix.shape  # 图像的形状
        self.image_height, self.image_width = self.image_shape  # 图像的高与宽

    # 图像输出
    def output_image(self):
        image_splice = Image.new(mode='L', size=(self.image_width * 3 + 64, self.image_height + 32), color=215)  # 生成空白拼接图像
        image_splice.paste(im=Image.fromarray(self.image_matrix), box=(16, 16))  # 生成原图灰度化图像
        image_splice.paste(im=Image.fromarray(self.filter_matrix), box=(self.image_width + 32, 16))  # 生成平滑处理图像
        image_splice.paste(im=Image.fromarray(self.normalize(self.image_matrix - self.filter_matrix)), box=(self.image_width * 2 + 48, 16))  # 生成对比图像
        image_splice.save(self.image_name.replace('.', '_') + '_' + self.processing_mode + '_by_' + self.filter_mode + '_filter_using_' + self.padding_mode + '_padding.png')  # 保存图像
        # image_splice.show()  # 运行程序时显示图像

    # 零扩展
    def zero_padding(self):
        pass  # 原扩展矩阵为零矩阵，不需要额外处理

    # 镜面扩展
    def mirror_padding(self):

        # 四角
        self.padding_matrix[:self.pad_h, :self.pad_w] = np.rot90(self.image_matrix[1:1 + self.pad_h, 1:1 + self.pad_w], 2)  # 左上角
        self.padding_matrix[self.pad_h + self.image_height:, :self.pad_w] = np.rot90(self.image_matrix[-1 - self.pad_h:-1, 1:1 + self.pad_w], 2)  # 左下角
        self.padding_matrix[:self.pad_h, self.pad_w + self.image_width:] = np.rot90(self.image_matrix[1:1 + self.pad_h, -1 - self.pad_w:-1], 2)  # 右上角
        self.padding_matrix[self.pad_h + self.image_height:, self.pad_w + self.image_width:] = np.rot90(self.image_matrix[-1 - self.pad_h:-1, -1 - self.pad_w:-1], 2)  # 右下角

        # 四边
        self.padding_matrix[:self.pad_h, self.pad_w:self.pad_w + self.image_width] = np.flipud(self.image_matrix[1:1 + self.pad_h, :])  # 上边框
        self.padding_matrix[self.pad_h + self.image_height:, self.pad_w:self.pad_w + self.image_width] = np.flipud(self.image_matrix[-1 - self.pad_h:-1, :])  # 下边框
        self.padding_matrix[self.pad_h:self.pad_h + self.image_height, :self.pad_w] = np.fliplr(self.image_matrix[:, 1:1 + self.pad_w])  # 左边框
        self.padding_matrix[self.pad_h:self.pad_h + self.image_height, self.pad_w + self.image_width:] = np.fliplr(self.image_matrix[:, -1 - self.pad_w:-1])  # 右边框

    # 复制扩展
    def replicate_padding(self):

        # 四角
        self.padding_matrix[:self.pad_h, :self.pad_w] = self.image_matrix[0, 0]  # 左上角
        self.padding_matrix[self.pad_h + self.image_height:, :self.pad_w] = self.image_matrix[-1, 0]  # 左下角
        self.padding_matrix[:self.pad_h, self.pad_w + self.image_width:] = self.image_matrix[0, -1]  # 右上角
        self.padding_matrix[self.pad_h + self.image_height:, self.pad_w + self.image_width:] = self.image_matrix[-1, -1]  # 右下角

        # 四边
        self.padding_matrix[:self.pad_h, self.pad_w:self.pad_w + self.image_width] = self.image_matrix[0:1, :]  # 上边框
        self.padding_matrix[self.pad_h + self.image_height:, self.pad_w:self.pad_w + self.image_width] = self.image_matrix[-2:-1, :]  # 下边框
        self.padding_matrix[self.pad_h:self.pad_h + self.image_height, :self.pad_w] = self.image_matrix[:, 0:1]  # 左边框
        self.padding_matrix[self.pad_h:self.pad_h + self.image_height, self.pad_w + self.image_width:] = self.image_matrix[:, -2:-1]  # 右边框

    # 扩展算法
    def padding(self):
        self.padding_matrix = np.zeros(np.array(self.image_shape) + np.array(self.filter_shape) - 1)  # 生成扩展矩阵
        self.padding_matrix[self.pad_h:self.pad_h + self.image_height, self.pad_w:self.pad_w + self.image_width] = self.image_matrix  # 将原图像复制至扩展矩阵中心
        getattr(self, '%s_padding' % self.padding_mode)()  # 对原图像四周进行扩展

    # 均值滤波器
    def box_filter(self):
        return np.ones(self.filter_shape) / (self.filter_height * self.filter_width)  # 生成标准均值矩阵

    # 高斯滤波器
    def gaussian_filter(self):
        gaussian = lambda s, t: np.exp(-(s**2 + t**2) / (2 * self.sigma**2))  # 设定高斯函数
        gaussian_matrix = np.array([
            gaussian(h - self.pad_h, w - self.pad_w)  # 计算高斯函数
            for h in range(self.filter_height) for w in range(self.filter_width)  # 遍历图像矩阵
        ]).reshape(self.filter_shape)  # 生成高斯矩阵
        return gaussian_matrix / np.sum(gaussian_matrix)  # 生成归一化高斯矩阵

    # 中值滤波器
    def median_filter(self):
        return np.median  # 求中值

    # 最大值滤波器
    def max_filter(self):
        return np.max  # 求最大值

    # 最小值滤波器
    def min_filter(self):
        return np.min  # 求最小值

    # 拉普拉斯滤波器
    def laplacian_filter(self):
        return np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])  # 拉普拉斯模板

    # 对角拉普拉斯滤波器
    def diagonal_laplacian_filter(self):
        return np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])  # 带对角项的拉普拉斯模板

    # 高提升滤波器
    def highboost_filter(self):
        return self.gaussian_filter()  # 使用高斯滤波器进行平滑

    # 普鲁伊特滤波器
    def prewitt_filter(self):
        G_x, G_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]]), np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])  # 普鲁伊特算子
        return lambda matrix: np.sqrt(np.sum(G_x * matrix)**2 + np.sum(G_y * matrix)**2)  # 计算梯度矩阵

    # 索伯滤波器
    def sobel_filter(self):
        G_x, G_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]), np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])  # 索伯算子
        return lambda matrix: np.sqrt(np.sum(G_x * matrix)**2 + np.sum(G_y * matrix)**2)  # 计算梯度矩阵

    # 空间滤波算法
    def spatial_filtering(self, linear):

        kernel = getattr(self, '%s_filter' % self.filter_mode.split('-')[0])()  # 生成空间滤波窗口（线性滤波）或空间滤波函数（非线性滤波）

        if linear:  # 线性滤波
            self.filter_matrix = np.array(
                [
                    int(np.sum(kernel * self.padding_matrix[h:h + self.filter_height, w:w + self.filter_width]))  # 计算空间滤波窗口对应卷积
                    for h in range(self.image_height) for w in range(self.image_width)  # 遍历图像矩阵
                ],
                dtype=int).reshape(self.image_shape)  # 生成空间滤波矩阵
        else:  # 非线性滤波
            self.filter_matrix = np.array(
                [
                    int(kernel(self.padding_matrix[h:h + self.filter_height, w:w + self.filter_width]))  # 计算空间滤波函数
                    for h in range(self.image_height) for w in range(self.image_width)  # 遍历图像矩阵
                ],
                dtype=int).reshape(self.image_shape)  # 生成空间滤波矩阵

        if linear and self.processing_mode == 'sharpening':  # 线性锐化算法
            if self.filter_mode.split('-')[0] == 'highboost':  # 钝化或高提升滤波
                k = float(self.filter_mode.split('-')[1])  # 设定权重系数
                self.filter_matrix = ((k + 1) * self.image_matrix - k * self.filter_matrix).astype(int)  # 返回锐化矩阵
            else:  # 拉普拉斯滤波
                self.filter_matrix = self.image_matrix - self.filter_matrix  # 返回锐化矩阵

    # 设定滤波器尺寸
    def set_filter_shape(self, filter_mode):

        if filter_mode.split('-')[0] == 'gaussian':  # 高斯滤波器
            self.sigma = float(filter_mode.split('-')[1])  # 标准差
            G = int(np.ceil(6 * self.sigma))  # 利用3sigma原则设定滤波器边长为6sigma
            self.filter_shape = (G, G) if G % 2 else (G + 1, G + 1)  # 保证滤波器边长为奇数
        elif filter_mode.split('-')[0] == 'box':  # 均值滤波器
            self.filter_shape = tuple(map(int, filter_mode.split('-')[1:]))
        elif filter_mode.split('-')[0] == 'highboost':  # 高提升滤波器
            self.sigma = 3  # 标准差
            self.filter_shape = (19, 19)  # 设定滤波器边长为19
        else:  # 其他滤波器
            self.filter_shape = (3, 3)  # 设定滤波器边长为3

        self.filter_height, self.filter_width = self.filter_shape  # 滤波器的高与宽
        self.pad_h, self.pad_w = (self.filter_height - 1) // 2, (self.filter_width - 1) // 2  # 滤波器的中心位置

    # 空间滤波器
    def spatial_filter(self, linear, processing_mode, padding_mode, filter_mode):

        self.input_image()  # 输入图像

        self.processing_mode = processing_mode  # 设定处理模式
        self.padding_mode = padding_mode  # 设定扩展模式
        self.filter_mode = filter_mode  # 设定滤波模式
        self.set_filter_shape(filter_mode)  # 设定滤波器尺寸

        self.padding()  # 生成扩展矩阵
        self.spatial_filtering(linear)  # 生成空间滤波矩阵

        self.output_image()  # 输出图像

    # 测试接口
    def test(self, linear, processing_mode, filters):
        print('\nImage: %s\n' % self.image_name)  # 图像名称
        for filter_mode in filters:  # 滤波类型
            for padding_mode in ['zero', 'mirror', 'replicate']:  # 扩展类型
                start = time.time()  # 开始测试时刻
                self.spatial_filter(linear, processing_mode, padding_mode, filter_mode)  # 使用空间滤波器处理图像
                end = time.time()  # 结束测试时刻
                print('Processing mode: %s & %s padding & %s filter' % (processing_mode, padding_mode, filter_mode))  # 测试模式
                print('Program execute time: %.2f s\n' % (end - start))  # 测试时长


if __name__ == '__main__':

    # 图像: test_pattern.tif，模式：线性平滑，滤波器：均值（滤波器尺寸：11*11）、高斯（标准差：8）
    ImageData('test_pattern.tif').test(linear=True, processing_mode='smoothing', filters=['box-11-11', 'gaussian-8'])

    # 图像: circuit_board.tif，模式：非线性平滑，滤波器：中值
    ImageData('circuit_board.tif').test(linear=False, processing_mode='smoothing', filters=['median'])

    # 图像: hubble.tif，模式：非线性平滑，滤波器：最大值、最小值
    ImageData('hubble.tif').test(linear=False, processing_mode='smoothing', filters=['max', 'min'])

    # 图像: moon.tif，模式：线性锐化，滤波器：拉普拉斯、对角拉普拉斯
    ImageData('moon.tif').test(linear=True, processing_mode='sharpening', filters=['laplacian', 'diagonal_laplacian'])

    # 图像: text.tif，模式：线性锐化，滤波器：钝化（权重系数：1）、高提升（权重系数：4.5）
    ImageData('text.tif').test(linear=True, processing_mode='sharpening', filters=['highboost-1', 'highboost-4.5'])

    # 图像: lens.tif，模式：非线性锐化，滤波器：普鲁伊特、索伯
    ImageData('lens.tif').test(linear=False, processing_mode='sharpening', filters=['prewitt', 'sobel'])