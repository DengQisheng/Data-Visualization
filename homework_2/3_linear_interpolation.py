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

    # 整数倍像素矩阵化处理方法
    def integral_pixel_method(self, row, col):
        pixel = np.array(self.image_matrix[row:row + 2, col:col + 2])  # 原图对应2*2区域
        weight = np.array([np.arange(self.zoom, -1, -1), np.arange(self.zoom + 1)])  # 梯度比例矩阵
        return (np.linalg.multi_dot([weight.T, pixel, weight]) / (self.zoom)**2).astype(int)  # 双线性插值的矩阵形式

    # 整数倍放大双线性插值算法
    def integral_linear_interpolation(self, zoom):
        self.zoom = zoom  # 整数倍放大倍数
        self.zoom_height = (self.image_height - 1) * zoom + 1  # 整数倍放大后图像高度
        self.zoom_width = (self.image_width - 1) * zoom + 1  # 整数倍放大后图像宽度
        self.zoom_matrix = np.zeros((self.zoom_height, self.zoom_width), dtype=int)  # 新建图像矩阵
        for x in range(self.image_height - 1):  # 遍历原图像水平方向像素
            for y in range(self.image_width - 1):  # 遍历新图像垂直方向像素
                self.zoom_matrix[x * zoom:(x + 1) * zoom + 1, y * zoom:(y + 1) * zoom + 1] = self.integral_pixel_method(x, y)  # 对每个等容新正方形区域调用像素矩阵化方法

    # 任意倍像素处理方法
    def pixel_method(self, row, col):
        y, p_row = np.modf(row / self.zoom)  # y表示新正方形区域中的水平方向比例，p_row表示原图对应2*2区域的左上角横坐标
        x, p_col = np.modf(col / self.zoom)  # x表示新正方形区域中的垂直方向比例，p_col表示原图对应2*2区域的左上角纵坐标
        p_row, p_col = int(p_row), int(p_col)  # modf函数得到的整数部分为float类型，转换为int类型
        if p_col == self.image_width - 1:  # 右侧边界
            x, p_col = 1, p_col - 1  # 使用左方的新正方形区域计算
        if p_row == self.image_height - 1:  # 下侧边界
            y, p_row = 1, p_row - 1  # 使用上方的新正方形区域计算
        return int((1 - x) * (1 - y) * self.image_matrix[p_row, p_col] + x * (1 - y) * self.image_matrix[p_row, p_col + 1] +
                   (1 - x) * y * self.image_matrix[p_row + 1, p_col] + x * y * self.image_matrix[p_row + 1, p_col + 1])  # 双线性插值

    # 任意倍放缩双线性插值算法
    def linear_interpolation(self, zoom):
        self.zoom = zoom  # 放缩倍数
        self.zoom_height = int(self.image_height * zoom)  # 放缩后图像高度
        self.zoom_width = int(self.image_width * zoom)  # 放缩后图像宽度
        self.zoom_matrix = np.zeros((self.zoom_height, self.zoom_width), dtype=int)  # 新建图像矩阵
        for x in range(self.zoom_height):  # 遍历新图像水平方向像素
            for y in range(self.zoom_width):  # 遍历新图像垂直方向像素
                self.zoom_matrix[x, y] = self.pixel_method(x, y)  # 对每个像素调用像素方法

    # 图像输出
    def output_image(self):
        small_width = abs((self.zoom_width - self.image_width) // 2) + 16  # 较小图像的水平位置
        small_height = abs((self.zoom_height - self.image_height) // 2) + 16  # 较小图像的垂直位置
        if self.zoom > 1:
            image_splice = Image.new(mode='L', size=(self.zoom_width * 2 + 48, self.zoom_height + 32), color=215)  # 生成空白拼接图像
            image_splice.paste(im=Image.fromarray(self.image_matrix), box=(small_width, small_height))  # 生成原图灰度化图像
            image_splice.paste(im=Image.fromarray(self.zoom_matrix), box=(self.zoom_width + 32, 16))  # 生成双线性插值图像
        else:
            image_splice = Image.new(mode='L', size=(self.image_width * 2 + 48, self.image_height + 32), color=215)  # 生成空白拼接图像
            image_splice.paste(im=Image.fromarray(self.image_matrix), box=(16, 16))  # 生成原图灰度化图像
            image_splice.paste(im=Image.fromarray(self.zoom_matrix), box=(self.image_width + 16 + small_width, small_height))  # 生成双线性插值图像
        image_splice.save(self.image_name + '_zoom_' + str(self.zoom) + '_by_linear_interpolation.png')  # 保存图像
        # image_splice.show()  # 运行程序时显示图像

    # 放缩空间分辨率接口
    def modify_spatial_resolution(self, zoom=2):

        # 输入
        self.input_image()  # 输入图像

        # 双线性插值
        if isinstance(zoom, int):  # 整数倍放大
            self.integral_linear_interpolation(zoom)  # 调用整数倍放大双线性插值算法
        else:  # 任意倍放缩，数据量大时慢于整数倍放大
            self.linear_interpolation(zoom)  # 调用任意倍放缩双线性插值算法

        # 输出
        self.output_image()  # 输出图像


if __name__ == '__main__':

    print()  # 空行

    # 处理图像: lena_std.tif
    image_name = 'lena_std.tif'  # 图像的名称
    image_data = ImageData(image_name=image_name)  # 实例化ImageData对象
    print('Image: %s\n' % image_name)  # 实例的名称

    # 放大双线性插值算法
    start = time.time()  # 实例开始测试时刻
    image_data.modify_spatial_resolution(zoom=2)  # 调用函数放大空间分辨率
    end = time.time()  # 实例结束测试时刻
    print('Zoom: %d' % image_data.zoom)  # 放大倍数
    print('Program execute time: %.2f s\n' % (end - start))  # 实例测试时长

    # 缩小双线性插值算法
    start = time.time()  # 实例开始测试时刻
    image_data.modify_spatial_resolution(zoom=0.5)  # 调用函数缩小空间分辨率
    end = time.time()  # 实例结束测试时刻
    print('Zoom: %.1f' % image_data.zoom)  # 缩小倍数
    print('Program execute time: %.2f s\n' % (end - start))  # 实例测试时长
