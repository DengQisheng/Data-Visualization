import os  # 文件操作
import time  # 时间操作

import numpy as np  # 数组操作
from PIL import Image  # 图像操作


class ImageData:

    # 初始化
    def __init__(self, image_name):
        self.image_name = image_name  # 图像的名称

    # 矩阵标准化
    def normalize(self, matrix):
        positive_matrix = matrix - np.min(matrix)  # 平移至非负值
        return (255 * positive_matrix / np.max(positive_matrix)).astype(int)  # 映射至[0, 255]

    # 矩阵中心化
    def centerize(self, matrix):
        height, width = matrix.shape  # 矩阵的高与宽
        return matrix * np.array([[-1 if (x + y) % 2 else 1 for x in range(width)] for y in range(height)])  # 乘以平移因子

    # 矩阵频谱
    def spectrum(self, matrix):
        return self.normalize(np.log(1 + np.abs(matrix)))  # 使用对数变换标定频谱

    # 矩阵中心距离
    def distance(self, u, v):
        return np.sqrt((u - self.image_height)**2 + (v - self.image_width)**2)  # 频域点至滤波器中心的距离

    # 图像输入
    def input_image(self):
        image = Image.open(os.getcwd() + '\\' + self.image_name)  # 输入图像
        self.image_matrix = np.array(image.convert('L'))  # 将图像转换成灰度矩阵
        self.image_size = self.image_matrix.size  # 图像的面积
        self.image_shape = self.image_matrix.shape  # 图像的形状
        self.image_height, self.image_width = self.image_shape  # 图像的高与宽

    # 图像输出
    def output_image(self):
        image_splice = Image.new(mode='L', size=(self.image_width * 4 + 80, self.image_height + 32), color=215)  # 生成空白拼接图像
        image_splice.paste(im=Image.fromarray(self.image_matrix), box=(16, 16))  # 生成原图像
        image_splice.paste(im=Image.fromarray(self.spectrum(self.pre_frequency)).resize(self.image_shape), box=(self.image_width + 32, 16))  # 生成原图像频谱
        image_splice.paste(im=Image.fromarray(self.spectrum(self.post_frequency)).resize(self.image_shape), box=(self.image_width * 2 + 48, 16))  # 生成频域处理结果频谱
        image_splice.paste(im=Image.fromarray(self.result_matrix), box=(self.image_width * 3 + 64, 16))  # 生成频域处理结果
        image_splice.save(self.image_name.replace('.', '_') + '_' + self.processing_mode + '_by_' + self.filter_mode + '_filter_using_' + self.padding_mode + '_padding.png')  # 保存图像
        # image_splice.show()  # 运行程序时显示图像

    # 零扩展
    def zero_padding(self):
        pass  # 原扩展矩阵为零矩阵，不需要额外处理

    # 镜面扩展
    def mirror_padding(self):
        self.padding_matrix[self.image_height:, self.image_width:] = np.rot90(self.image_matrix, 2)  # 右下方
        self.padding_matrix[self.image_height:, :self.image_width] = np.flipud(self.image_matrix)  # 下方
        self.padding_matrix[:self.image_height, self.image_width:] = np.fliplr(self.image_matrix)  # 右方

    # 复制扩展
    def replicate_padding(self):
        self.padding_matrix[self.image_height:, self.image_width:] = self.image_matrix[-1, -1]  # 右下方
        self.padding_matrix[self.image_height:, :self.image_width] = self.image_matrix[-2:-1, :]  # 下方
        self.padding_matrix[:self.image_height, self.image_width:] = self.image_matrix[:, -2:-1]  # 右方

    # 扩展算法
    def padding(self):
        self.padding_matrix = np.zeros(2 * np.array(self.image_shape))  # 生成扩展矩阵
        self.padding_matrix[:self.image_height, :self.image_width] = self.image_matrix  # 将原图像复制至扩展矩阵左上角
        getattr(self, '%s_padding' % self.padding_mode)()  # 对原图像进行扩展

    # 理想低通滤波器
    def ideal_lowpass_filter(self, args):
        sigma = float(args[0])  # 标准差
        return np.array([[1 if self.distance(u, v) <= sigma else 0 for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 返回理想低通滤波器

    # 布特沃斯低通滤波器
    def butterworth_lowpass_filter(self, args):
        sigma, n = float(args[0]), int(args[1])  # 标准差，阶数
        return np.array([[1 / (1 + (self.distance(u, v) / sigma)**(2 * n)) for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 返回布特沃斯低通滤波器

    # 高斯低通滤波器
    def gaussian_lowpass_filter(self, args):
        sigma = float(args[0])  # 标准差
        return np.array([[np.exp(-self.distance(u, v)**2 / (2 * sigma**2)) for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 返回高斯低通滤波器

    # 陷波滤波器
    def notch_filter(self, args):

        ###########################################################################################################################
        # 调试时使用：                                                                                                            #
        # from matplotlib import pyplot as plt  # 绘图操作                                                                        #
        # plt.imshow(self.spectrum(self.pre_frequency))  # 计算原图频谱                                                           #
        # plt.savefig(self.image_name.replace('.', '_') + '_spectrum_using_' + self.padding_mode + '_padding.png') # 保存原图频谱 #
        # plt.show()  # 显示原图频谱                                                                                              #
        ###########################################################################################################################

        notch = np.array([
            (35, 35), (195, 35), (270, 35), (360, 35), (435, 35), (595, 35), (835, 35), (995, 35), (1070, 35), (1160, 35), (1235, 35), (1395, 35),  # 第一列
            (35, 195), (195, 195), (270, 195), (360, 195), (435, 195), (595, 195), (835, 195), (995, 195), (1070, 195), (1160, 195), (1235, 195), (1395, 195),  # 第二列
            (35, 270), (195, 270), (270, 270), (360, 270), (435, 270), (595, 270), (835, 270), (995, 270), (1070, 270), (1160, 270), (1235, 270), (1395, 270),  # 第三列
            (35, 360), (195, 360), (270, 360), (360, 360), (435, 360), (595, 360), (835, 360), (995, 360), (1070, 360), (1160, 360), (1235, 360), (1395, 360),  # 第四列
            (35, 435), (195, 435), (270, 435), (360, 435), (435, 435), (595, 435), (835, 435), (995, 435), (1070, 435), (1160, 435), (1235, 435), (1395, 435),  # 第五列
            (35, 595), (195, 595), (270, 595), (360, 595), (435, 595), (595, 595), (835, 595), (995, 595), (1070, 595), (1160, 595), (1235, 595), (1395, 595)  # 第六列
        ]) - self.image_shape  # 陷波中心

        NRF = np.ones(2 * np.array(self.image_shape))  # 陷波带阻滤波器
        if args[0] == 'ideal':  # 理想高通滤波器
            sigma = float(args[1])  # 标准差
            for (u_k, v_k) in notch:  # 遍历陷波中心
                NRF *= np.array([[0 if self.distance(u - u_k, v - v_k) <= sigma else 1 for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 陷波：(u_k, v_k)
                NRF *= np.array([[0 if self.distance(u + u_k, v + v_k) <= sigma else 1 for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 陷波：(-u_k, -v_k)
                print('Notch: u_k = %d, v_k = %d... Done!...' % (u_k, v_k))  # 调试信息
        elif args[0] == 'butterworth':  # 布特沃斯高通滤波器
            sigma, n = float(args[1]), int(args[2])  # 标准差，阶数
            for (u_k, v_k) in notch:  # 遍历陷波中心
                NRF *= np.array([[1 - 1 / (1 + (self.distance(u - u_k, v - v_k) / sigma)**(2 * n)) for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 陷波：(u_k, v_k)
                NRF *= np.array([[1 - 1 / (1 + (self.distance(u + u_k, v + v_k) / sigma)**(2 * n)) for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 陷波：(-u_k, -v_k)
                print('Notch: u_k = %d, v_k = %d... Done!...' % (u_k, v_k))  # 调试信息
        elif args[0] == 'gaussian':  # 高斯高通滤波器
            sigma = float(args[1])  # 标准差
            for (u_k, v_k) in notch:  # 遍历陷波中心
                NRF *= np.array([[1 - np.exp(-self.distance(u - u_k, v - v_k)**2 / (2 * sigma**2)) for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 陷波：(u_k, v_k)
                NRF *= np.array([[1 - np.exp(-self.distance(u + u_k, v + v_k)**2 / (2 * sigma**2)) for v in range(2 * self.image_width)] for u in range(2 * self.image_height)])  # 陷波：(-u_k, -v_k)
                print('Notch: u_k = %d, v_k = %d... Done!...' % (u_k, v_k))  # 调试信息

        return NRF  # 返回陷波带阻滤波器

    # 频域滤波算法
    def freqency_domain_filtering(self):

        # 频域滤波五步骤
        self.padding()  # 第一步：扩展图像
        self.pre_frequency = np.fft.fft2(self.centerize(self.padding_matrix))  # 第二步：计算傅里叶变换
        self.post_frequency = getattr(self, '%s_filter' % self.filter_mode.split('-')[0])(self.filter_mode.split('-')[1:]) * self.pre_frequency  # 第三步：计算频域滤波矩阵
        result = self.centerize(np.real(np.fft.ifft2(self.post_frequency))).astype(int)  # 第四步：计算傅里叶逆变换
        self.result_matrix = result[:self.image_height, :self.image_width]  # 第五步：提取图像

    # 频域滤波器
    def freqency_domain_filter(self, processing_mode, padding_mode, filter_mode):

        self.input_image()  # 输入图像

        self.processing_mode = processing_mode  # 设定处理模式
        self.padding_mode = padding_mode  # 设定扩展模式
        self.filter_mode = filter_mode  # 设定滤波模式

        self.freqency_domain_filtering()  # 生成频域滤波矩阵

        self.output_image()  # 输出图像

    # 测试接口
    def test(self, processing_mode, filters):
        print('\nImage: %s\n' % self.image_name)  # 图像名称
        for filter_mode in filters:  # 滤波类型
            for padding_mode in ['zero', 'mirror', 'replicate']:  # 扩展类型
                start = time.time()  # 开始测试时刻
                self.freqency_domain_filter(processing_mode, padding_mode, filter_mode)  # 使用频域滤波器处理图像
                end = time.time()  # 结束测试时刻
                print('Processing mode: %s & %s padding & %s filter' % (processing_mode, padding_mode, filter_mode))  # 测试模式
                print('Program execute time: %.2f s\n' % (end - start))  # 测试时长


if __name__ == '__main__':

    # 图像: integrated_circuit.tif，模式：低通平滑，滤波器：理想（标准差：60）、布特沃斯（标准差：60，阶数：2）、高斯（标准差：60）
    ImageData('integrated_circuit.tif').test(processing_mode='smoothing', filters=['ideal_lowpass-60', 'butterworth_lowpass-60-2', 'gaussian_lowpass-60'])

    # 图像: shepp_logan.tif，模式：选择陷波，滤波器：理想（标准差：30）、布特沃斯（标准差：30，阶数：4）、高斯（标准差：30）
    ImageData('shepp_logan.tif').test(processing_mode='selective', filters=['notch-ideal-30', 'notch-butterworth-30-4', 'notch-gaussian-30'])