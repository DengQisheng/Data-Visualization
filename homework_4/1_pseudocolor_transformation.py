import os  # 文件
import time  # 时间

import numpy as np  # 数组
from PIL import Image, ImageColor  # 图像

HOME_PATH = os.getcwd()
DATA_PATH = os.path.join(HOME_PATH, 'data')
RESULT_PATH = os.path.join(HOME_PATH, 'result')


class ImageData:

    # 初始化
    def __init__(self, image_name):
        self.image_name = image_name  # 图像的名称

    # 图像输入
    def input_image(self):
        image = Image.open(os.path.join(DATA_PATH, self.image_name))  # 输入图像
        self.full_image_matrix = np.array(image.convert('RGB'))  # 图像的全彩色矩阵
        self.gray_image_matrix = np.array(image.convert('L'))  # 图像的灰度矩阵
        self.pseudo_image_matrix = np.zeros(self.full_image_matrix.shape, dtype=np.uint8)  # 图像的伪彩色矩阵
        self.image_height, self.image_width = image.size  # 图像的高与宽

    # 图像输出
    def output_image(self):
        canvas = Image.new(mode='RGB', size=(self.image_width * 3 + 64, self.image_height + 32), color='#D7D7D7')  # 生成空白画布
        canvas.paste(im=Image.fromarray(self.full_image_matrix), box=(16, 16))  # 生成全彩色图像（原图）
        canvas.paste(im=Image.fromarray(self.gray_image_matrix), box=(self.image_width + 32, 16))  # 生成灰度图像
        canvas.paste(im=Image.fromarray(self.pseudo_image_matrix), box=(self.image_width * 2 + 48, 16))  # 生成伪彩色图像
        canvas.save(os.path.join(RESULT_PATH, '%s_by_%s_transformation.png' % (self.image_name.split('.')[0], self.algorithm)))  # 保存图像
        # canvas.show()  # 显示图像

    # 灰度分层
    def intensity_slicing(self):
        for h in range(self.image_height):
            for w in range(self.image_width):
                intensity = self.gray_image_matrix[h, w]
                if 0 <= intensity <= 18:
                    self.pseudo_image_matrix[h, w, :] = np.array([127, 0, 255], dtype=np.uint8)
                elif 19 <= intensity <= 40:
                    self.pseudo_image_matrix[h, w, :] = np.array([0, 0, 255], dtype=np.uint8)
                elif 41 <= intensity <= 62:
                    self.pseudo_image_matrix[h, w, :] = np.array([0, 63, 255], dtype=np.uint8)
                elif 63 <= intensity <= 84:
                    self.pseudo_image_matrix[h, w, :] = np.array([0, 127, 255], dtype=np.uint8)
                elif 85 <= intensity <= 106:
                    self.pseudo_image_matrix[h, w, :] = np.array([0, 210, 210], dtype=np.uint8)
                elif 107 <= intensity <= 128:
                    self.pseudo_image_matrix[h, w, :] = np.array([0, 255, 0], dtype=np.uint8)
                elif 129 <= intensity <= 150:
                    self.pseudo_image_matrix[h, w, :] = np.array([127, 255, 0], dtype=np.uint8)
                elif 151 <= intensity <= 172:
                    self.pseudo_image_matrix[h, w, :] = np.array([255, 255, 0], dtype=np.uint8)
                elif 173 <= intensity <= 194:
                    self.pseudo_image_matrix[h, w, :] = np.array([255, 210, 0], dtype=np.uint8)
                elif 195 <= intensity <= 216:
                    self.pseudo_image_matrix[h, w, :] = np.array([255, 165, 0], dtype=np.uint8)
                elif 217 <= intensity <= 238:
                    self.pseudo_image_matrix[h, w, :] = np.array([255, 82, 0], dtype=np.uint8)
                elif 239 <= intensity < 256:
                    self.pseudo_image_matrix[h, w, :] = np.array([255, 0, 0], dtype=np.uint8)

    # 灰度彩色变换
    def intensity_to_color(self):
        for h in range(self.image_height):
            for w in range(self.image_width):
                intensity = self.gray_image_matrix[h, w]
                if 0 <= intensity < 42:
                    self.pseudo_image_matrix[h, w, :] = np.array([-3 * intensity + 128, 0, 255], dtype=np.uint8)
                elif 42 <= intensity < 85:
                    self.pseudo_image_matrix[h, w, :] = np.array([0, 6 * intensity - 252, 255], dtype=np.uint8)
                elif 85 <= intensity < 128:
                    self.pseudo_image_matrix[h, w, :] = np.array([0, 255, -6 * intensity + 765], dtype=np.uint8)
                elif 128 <= intensity < 170:
                    self.pseudo_image_matrix[h, w, :] = np.array([6 * intensity - 768, 255, 0], dtype=np.uint8)
                elif 170 <= intensity < 256:
                    self.pseudo_image_matrix[h, w, :] = np.array([255, -3 * intensity + 765, 0], dtype=np.uint8)

    # 伪彩色变换
    def pseudo_color_transformation(self, alg):

        self.input_image()  # 输入图像

        self.algorithm = alg  # 伪彩色变换算法
        getattr(self, alg)()  # 伪彩色变换

        self.output_image()  # 输出图像

    # 测试接口
    def test(self, alg):
        print('\nImage: %s\n' % self.image_name)  # 图像名称
        start = time.time()  # 开始测试时刻
        self.pseudo_color_transformation(alg)  # 使用伪彩色变换算法处理图像
        end = time.time()  # 结束测试时刻
        print('Algorithm: %s transformation' % ' '.join(alg.split('_')))  # 变换算法
        print('Program execute time: %.2f s\n' % (end - start))  # 测试时长


if __name__ == '__main__':

    # 图像: NGC2237.jpg，算法：灰度分层
    ImageData('NGC2237.jpg').test(alg='intensity_slicing')
    # 图像: NGC2237.jpg，算法：灰度彩色变换
    ImageData('NGC2237.jpg').test(alg='intensity_to_color')

    # 图像: lena_std.tif，算法：灰度分层
    ImageData('lena_std.tif').test(alg='intensity_slicing')
    # 图像: lena_std.tif，算法：灰度彩色变换
    ImageData('lena_std.tif').test(alg='intensity_to_color')
