import subprocess  # 文件操作
import time  # 时间操作
import tkinter as tk  # 界面操作
from itertools import product  # 网格操作
from tkinter import filedialog, messagebox  # 交互操作

import numpy as np  # 数组操作
from PIL import Image, ImageTk  # 图像操作
from scipy.interpolate import griddata  # 插值操作


class GUI:
    '''交互界面'''


    ###########
    # 基本设置 #
    ###########

    # 常量
    IMAGE_SUFFIX = ('.tif', '.tiff', '.jpg', '.jpeg', '.png', '.gif', 'bmp')  # 图像文件的后缀名

    # 初始化
    def __init__(self):

        self.window = tk.Tk()  # 交互界面的主窗体
        self.window.title('Image Spatial Transformation')  # 交互界面的标题
        self.WINDOW_HEIGHT = self.window.winfo_screenheight() - 150  # 交互界面的高H，需要考虑减去Windows系统的任务栏高度
        self.WINDOW_WIDTH = self.window.winfo_screenwidth() - 60  # 交互界面的宽W
        self.window.geometry('%dx%d+%d+%d' % (self.WINDOW_WIDTH, self.WINDOW_HEIGHT, 30, 30))  # 交互界面的大小与位置，典型大小为1440x720
        self.window.resizable(height=False, width=False)  # 将交互界面设置为不可缩放的状态

        self.original_image = None  # 原始图像，格式为PIL.Image.Image
        self.reference_image = None  # 参考图像，格式为PIL.Image.Image
        self.resultant_image = None  # 结果图像，格式为PIL.Image.Image

        self.original_landmarks = dict()  # 原始图像的映射坐标点，键表示序号，值表示二维坐标
        self.reference_landmarks = dict()  # 参考图像的映射坐标点，键表示序号，值表示二维坐标

        self.original_landmarks_number = 0  # 原始图像的映射坐标点的数量
        self.reference_landmarks_number = 0  # 参考图像的映射坐标点的数量

        self.transform_algorithm = 'TPS'  # 图像形变算法，默认为薄板样条形变算法
        self.transform_execute_time = tk.StringVar()  # 执行图像空间变换所需时间的变量


    #############
    # 菜单栏部分 #
    #############

    # 文件操作：保存结果图像为文件
    def save_resultant_image(self):
        if self.resultant_image is None:  # 未生成结果图像
            messagebox.showwarning('Warning', 'No Resultant Image!')  # 弹出警告框提示无结果图像
        else:  # 已生成结果图像
            resultant_image_path = filedialog.asksaveasfilename(title='Save Resultant Image')  # 弹出对话框询问保存文件的位置与名称
            self.resultant_image.save(resultant_image_path + '.png')  # 保存结果图像，格式为png

    # 文件操作：退出交互界面
    def quit_program(self):
        self.window.destroy()  # 销毁交互界面主窗体
        exit()  # 终止Python程序的运行

    # 算法操作：将算法设置为TPS算法
    def set_algorithm_to_TPS(self):
        self.transform_algorithm = 'TPS'  # 设置图像形变算法为TPS算法

    # 算法操作：将算法设置为LARM算法
    def set_algorithm_to_LARM(self):
        self.transform_algorithm = 'LARM'  # 设置图像形变算法为LARM算法

    '''此处添加更多算法操作
    def set_algorithm_to_more_algorithm(self):
        pass
    '''

    # 帮助操作：打开本程序的帮助文档usage.txt
    def show_project_usage(self):
        subprocess.Popen('notepad usage.txt')  # 用记事本打开usage.txt

    # 帮助操作：显示TPS算法示例
    def show_example(self):

        scale = (self.WINDOW_WIDTH // 4) / 369  # 兼容不同分辨率

        self.open_original_image(original_image_path='./example/example_trump.tif')  # 打开示例原始图像
        self.original_landmarks_number = 23  # 示例映射坐标点的数量
        self.original_landmarks = dict(
            zip(
                range(1, self.original_landmarks_number + 1),
                tuple(
                    map(tuple, (scale * np.array([
                            (100, 161), (124, 154), (142, 164), (121, 167), (208, 161),
                            (229, 153), (248, 160), (229, 165), (160, 150), (187, 149),
                            (156, 195), (189, 194), (146, 228), (172, 235), (200, 229),
                            (137, 277), (163, 266), (176, 270), (188, 265), (216, 275),
                            (152, 289), (174, 291), (196, 288)
                        ])).astype(int)
                    )
                )
            )
        )  # 示例映射坐标点
        for i, (x, y) in self.original_landmarks.items():  # 遍历示例映射坐标点
            self.original_canvas.create_oval(
                x - 6, y - 6, x + 6, y + 6,  # 圆形的左上角坐标与右下角坐标
                fill='#FF5555', tags=('point%d' % i)  # 颜色为红色，标记为point[*]
            )  # 显示圆形映射坐标点
            self.original_canvas.create_text(
                x, y,  # 序号的坐标
                text=str(i), justify=tk.CENTER,  # 居中放置
                font=('Helvetica', '7'), tags=('text%d' % i)  # 标记为text[*]
            )  # 显示对应映射坐标点的序号

        self.open_reference_image(reference_image_path='./example/example_ape.tif')  # 打开示例参考图像
        self.reference_landmarks_number = 23  # 示例映射坐标点的数量
        self.reference_landmarks = dict(
            zip(
                range(1, self.reference_landmarks_number + 1),
                tuple(
                    map(tuple, (scale * np.array([
                            (97, 40), (127, 33), (158, 57), (122, 58), (208, 51),
                            (238, 28), (262, 34), (242, 56), (167, 26), (193, 26),
                            (155, 200), (201, 201), (111, 268), (171, 279), (233, 269),
                            (84, 293), (146, 331), (173, 335), (203, 335), (286, 296),
                            (121, 336), (172, 356), (232, 347)
                        ])).astype(int)
                    )
                )
            )
        )  # 示例映射坐标点
        for i, (x, y) in self.reference_landmarks.items():  # 遍历示例映射坐标点
            self.reference_canvas.create_oval(
                x - 6, y - 6, x + 6, y + 6,  # 圆形的左上角坐标与右下角坐标
                fill='#1E90FF', tags=('point%d' % i)  # 颜色为蓝色，标记为point[*]
            )  # 显示圆形映射坐标点
            self.reference_canvas.create_text(
                x, y,  # 序号的坐标
                text=str(i), justify=tk.CENTER,  # 居中放置
                font=('Helvetica', '7'), tags=('text%d' % i)  # 标记为text[*]
            )  # 显示对应映射坐标点的序号

        self.resultant_image = Image.open('./example/example_TPS.png').resize(
            (self.WINDOW_WIDTH // 4, self.WINDOW_WIDTH // 4)
        )  # 打开示例结果图像，面积调整至W//4*W//4，适应窗口大小
        self.tk_resultant_image = ImageTk.PhotoImage(self.resultant_image)  # 将示例结果图像转换为可渲染格式
        self.resultant_canvas.create_image(0, 0, image=self.tk_resultant_image, anchor=tk.NW) # 在画布上显示示例结果图像，以左上角为度量起点
        self.transform_execute_time.set('Execute time: 75.26 s')  # 显示示例变换所需的时间

    # 帮助操作：查看版本信息
    def show_project_information(self):
        messagebox.showinfo('Project Information', 'Version 4.1\nAuthor: Deng Qisheng')  # 弹出信息框展示版本信息

    # 渲染菜单栏部分
    def render_menu_bar(self):

        menu_bar = tk.Menu(self.window)  # 菜单栏的主体
        self.window.config(menu=menu_bar)  # 将菜单栏嵌入交互界面的主窗体中

        file_menu = tk.Menu(menu_bar, tearoff=0)  # 文件选项
        menu_bar.add_cascade(label='File', menu=file_menu)  # 命名文件选项为File
        file_menu.add_command(label='Save', command=self.save_resultant_image)  # 下拉选项：保存
        file_menu.add_separator()  # 分割线
        file_menu.add_command(label='Exit', command=self.quit_program)  # 下拉选项：退出

        alg_menu = tk.Menu(menu_bar, tearoff=0)  # 算法选项
        menu_bar.add_cascade(label='Algorithm', menu=alg_menu)  #命名算法选项为Algorithm
        alg_menu.add_radiobutton(label='TPS', command=self.set_algorithm_to_TPS)  # 下拉单选选项：选择TPS算法
        alg_menu.add_radiobutton(label='LARM', command=self.set_algorithm_to_LARM)  # 下拉单选选项：选择LARM算法

        '''此处添加更多算法选项
        alg_menu.add_radiobutton(label='more_algorithm', command=self.set_algorithm_to_more_algorithm)  # 下拉单选选项：选择更多算法
        '''

        help_menu = tk.Menu(menu_bar, tearoff=0)  # 帮助选项
        menu_bar.add_cascade(label='Help', menu=help_menu)  # 命名帮助选项为Help
        help_menu.add_command(label='Usage', command=self.show_project_usage)  # 下拉选项：使用文档
        help_menu.add_command(label='Example', command=self.show_example)  # 下拉选项：显示示例
        help_menu.add_separator()  # 分割线
        help_menu.add_command(label='About', command=self.show_project_information)  # 下拉选项：版本信息


    ###############
    # 原始图像部分 #
    ###############

    # 打开并展示原始图像
    def open_original_image(self, original_image_path=None):

        if original_image_path is None:  # 未指定原始图像
            original_image_path = filedialog.askopenfilename(title='Open Original Image File')  # 弹出对话框询问原始图像文件的位置与名称
            if original_image_path == '':  # 未返回文件路径，触发条件是点按了取消或者关闭
                return  # 未打开原始图像，操作结束
            elif not original_image_path.lower().endswith(self.IMAGE_SUFFIX):  # 未打开图像文件，触发条件是选择了非图像文件
                messagebox.showerror('Error', 'Wrong Image Format!')  # 弹出错误框告示文件格式错误
                return  # 未打开原始图像，操作结束

        self.delete_all_original_landmarks()  # 删除原有的映射坐标点，更换原始图像时起效
        self.original_image = Image.open(original_image_path).resize(
            (self.WINDOW_WIDTH // 4, self.WINDOW_WIDTH // 4)
        )  # 记录原始图像，面积调整至W//4*W//4，适应窗口大小
        self.tk_original_image = ImageTk.PhotoImage(self.original_image)  # 将原始图像转换为可渲染格式
        self.original_canvas.create_image(0, 0, image=self.tk_original_image, anchor=tk.NW)  # 在画布上显示原始图像，以左上角为度量起点

    # 双击标记原始图像的映射坐标点
    def set_original_landmarks(self, event):

        self.original_canvas.focus_set()  # 将原始图像画布设为焦点

        if self.original_image is None:  # 未打开原始图像
            self.open_original_image()  # 双击打开原始图像
        else:  # 已打开原始图像
            self.original_landmarks_number += 1  # 映射坐标点的数量增加1
            self.original_canvas.create_oval(
                event.x - 6, event.y - 6, event.x + 6, event.y + 6,  # 圆形的左上角坐标与右下角坐标
                fill='#FF5555', tags=('point%d' % self.original_landmarks_number)  # 颜色为红色，标记为point[*]
            )  # 显示圆形映射坐标点
            self.original_canvas.create_text(
                event.x, event.y,  # 序号的坐标
                text=str(self.original_landmarks_number), justify=tk.CENTER,  # 居中放置
                font=('Helvetica', '7'), tags=('text%d' % self.original_landmarks_number)  # 标记为text[*]
            )  # 显示对应映射坐标点的序号
            self.original_landmarks[self.original_landmarks_number] = (event.x, event.y)  # 记录映射坐标点的位置

    # 方向键移动原始图像画布上当前最后一个映射坐标点
    def move_last_original_landmark(self, event=None):
        if self.original_landmarks_number != 0:  # 画布上存在映射坐标点，不存在则结束操作
            (x, y) = self.original_landmarks[self.original_landmarks_number]  # 记录映射坐标点的原位置
            if event.keysym == 'Up':  # 上方向键
                self.original_canvas.move('point%d' % self.original_landmarks_number, 0, -1)  # 圆形映射坐标点往上移动一个像素
                self.original_canvas.move('text%d' % self.original_landmarks_number, 0, -1)  # 对应坐标往上移动一个像素
                self.original_landmarks[self.original_landmarks_number] = (x, y - 1)  # 记录映射坐标点的新位置
            elif event.keysym == 'Down':  # 下方向键
                self.original_canvas.move('point%d' % self.original_landmarks_number, 0, 1)  # 圆形映射坐标点往下移动一个像素
                self.original_canvas.move('text%d' % self.original_landmarks_number, 0, 1)  # 对应坐标往下移动一个像素
                self.original_landmarks[self.original_landmarks_number] = (x, y + 1)  # 记录映射坐标点的新位置
            elif event.keysym == 'Left':  # 左方向键
                self.original_canvas.move('point%d' % self.original_landmarks_number, -1, 0)  # 圆形映射坐标点往左移动一个像素
                self.original_canvas.move('text%d' % self.original_landmarks_number, -1, 0)  # 对应坐标往左移动一个像素
                self.original_landmarks[self.original_landmarks_number] = (x - 1, y)  # 记录映射坐标点的新位置
            elif event.keysym == 'Right':  # 右方向键
                self.original_canvas.move('point%d' % self.original_landmarks_number, 1, 0)  # 圆形映射坐标点往右移动一个像素
                self.original_canvas.move('text%d' % self.original_landmarks_number, 1, 0)  # 对应坐标往右移动一个像素
                self.original_landmarks[self.original_landmarks_number] = (x + 1, y)  # 记录映射坐标点的新位置

    # 删除原始图像画布上当前最后一个映射坐标点
    def cancel_last_original_landmark(self, event=None):
        if self.original_landmarks_number != 0:  # 画布上存在映射坐标点，不存在则结束操作
            self.original_canvas.delete('point%d' % self.original_landmarks_number)  # 删除最后一个映射坐标点
            self.original_canvas.delete('text%d' % self.original_landmarks_number)  # 删除对应映射坐标点的序号
            del self.original_landmarks[self.original_landmarks_number]  # 删除记录中最后一个映射坐标点
            self.original_landmarks_number -= 1  # 映射坐标点的数量减少1

    # 删除原始图像画布上所有映射坐标点
    def delete_all_original_landmarks(self, event=None):
        for i in range(1, self.original_landmarks_number + 1):  # 遍历所有映射坐标点的序号
            self.original_canvas.delete('point%d' % i)  # 删除映射坐标点
            self.original_canvas.delete('text%d' % i)  # 删除对应映射坐标点的序号
        self.original_landmarks.clear()  # 清空映射坐标点记录
        self.original_landmarks_number = 0  # 将映射坐标点的数量设为0

    # 渲染原始图像部分
    def render_original_part(self):

        self.original_label = tk.Label(
            self.window, text='Original Image', font=('Helvetica', '20'), justify=tk.CENTER
        )  # 原始图像标签Original Image
        self.original_label.place(
            x=self.WINDOW_WIDTH // 16, y=self.WINDOW_HEIGHT // 2 - 7 * self.WINDOW_WIDTH // 32,
            height=self.WINDOW_WIDTH // 16, width=self.WINDOW_WIDTH // 4
        )  # 原始图像标签的位置

        self.original_canvas = tk.Canvas(self.window, bg='#D7D7D7', bd=2, relief=tk.RIDGE)  # 原始图像画布
        self.original_canvas.place(
            x=self.WINDOW_WIDTH // 16, y=self.WINDOW_HEIGHT // 2 - 5 * self.WINDOW_WIDTH // 32,
            height=self.WINDOW_WIDTH // 4, width=self.WINDOW_WIDTH // 4
        )  # 原始图像画布的位置

        self.open_original_image_button = tk.Button(
            self.window, text='Open', font=('Helvetica', '15'), command=self.open_original_image
        )  # 打开原始图像按钮Open
        self.open_original_image_button.place(
            x=self.WINDOW_WIDTH // 16, y=self.WINDOW_HEIGHT // 2 + 53 * self.WINDOW_WIDTH // 480,
            height=self.WINDOW_WIDTH // 36, width=3 * self.WINDOW_WIDTH // 40
        )  # 打开原始图像按钮的位置

        self.cancel_last_original_landmark_button = tk.Button(
            self.window, text='Undo', font=('Helvetica', '15'), command=self.cancel_last_original_landmark
        )  # 撤销映射坐标点按钮Undo
        self.cancel_last_original_landmark_button.place(
            x=3 * self.WINDOW_WIDTH // 20, y=self.WINDOW_HEIGHT // 2 + 53 * self.WINDOW_WIDTH // 480,
            height=self.WINDOW_WIDTH // 36, width=3 * self.WINDOW_WIDTH // 40
        )  # 撤销映射坐标点按钮的位置

        self.delete_all_original_landmarks_button = tk.Button(
            self.window, text='Reset', font=('Helvetica', '15'), command=self.delete_all_original_landmarks
        )  # 重置映射坐标点按钮Reset
        self.delete_all_original_landmarks_button.place(
            x=19 * self.WINDOW_WIDTH // 80, y=self.WINDOW_HEIGHT // 2 + 53 * self.WINDOW_WIDTH // 480,
            height=self.WINDOW_WIDTH // 36, width=3 * self.WINDOW_WIDTH // 40
        )  # 重置映射坐标点按钮的位置


    ###############
    # 参考图像部分 #
    ###############

    # 打开并展示参考图像
    def open_reference_image(self, reference_image_path=None):

        if reference_image_path is None:  # 未指定参考图像
            reference_image_path = filedialog.askopenfilename(title='Open Reference Image File')  # 弹出对话框询问参考图像文件的位置与名称
            if reference_image_path == '':  # 未返回文件路径，触发条件是点按了取消或者关闭
                return  # 未打开参考图像，操作结束
            elif not reference_image_path.lower().endswith(self.IMAGE_SUFFIX):  # 未打开图像文件，触发条件是选择了非图像文件
                messagebox.showerror('Error', 'Wrong Image Format!')  # 弹出错误框告示文件格式错误
                return  # 未打开参考图像，操作结束

        self.delete_all_reference_landmarks()  # 删除原有的映射坐标点，更换参考图像时起效
        self.reference_image = Image.open(reference_image_path).resize(
            (self.WINDOW_WIDTH // 4, self.WINDOW_WIDTH // 4)
        )  # 记录参考图像，面积调整至W//4*W//4，适应窗口大小
        self.tk_reference_image = ImageTk.PhotoImage(self.reference_image)  # 将参考图像转换为可渲染格式
        self.reference_canvas.create_image(0, 0, image=self.tk_reference_image, anchor=tk.NW)  # 在画布上显示参考图像，以左上角为度量起点

    # 双击标记参考图像的映射坐标点
    def set_reference_landmarks(self, event):

        self.reference_canvas.focus_set()  # 将参考图像画布设为焦点

        if self.reference_image is None:  # 未打开参考图像
            self.open_reference_image()  # 双击打开参考图像
        else:  # 已打开参考图像
            self.reference_landmarks_number += 1  # 映射坐标点的数量增加1
            self.reference_canvas.create_oval(
                event.x - 6, event.y - 6, event.x + 6, event.y + 6,  # 圆形的左上角坐标与右下角坐标
                fill='#1E90FF', tags=('point%d' % self.reference_landmarks_number)  # 颜色为蓝色，标记为point[*]
            )  # 显示圆形映射坐标点
            self.reference_canvas.create_text(
                event.x, event.y,  # 序号的坐标
                text=str(self.reference_landmarks_number), justify=tk.CENTER,  # 居中放置
                font=('Helvetica', '7'), tags=('text%d' % self.reference_landmarks_number)  # 标记为text[*]
            )  # 显示对应映射坐标点的序号
            self.reference_landmarks[self.reference_landmarks_number] = (event.x, event.y)  # 记录映射坐标点的位置

    # 方向键移动参考图像画布上当前最后一个映射坐标点
    def move_last_reference_landmark(self, event=None):
        if self.reference_landmarks_number != 0:  # 画布上存在映射坐标点，不存在则结束操作
            (x, y) = self.reference_landmarks[self.reference_landmarks_number]  # 记录映射坐标点的原位置
            if event.keysym == 'Up':  # 上方向键
                self.reference_canvas.move('point%d' % self.reference_landmarks_number, 0, -1)  # 圆形映射坐标点往上移动一个像素
                self.reference_canvas.move('text%d' % self.reference_landmarks_number, 0, -1)  # 对应坐标往上移动一个像素
                self.reference_landmarks[self.reference_landmarks_number] = (x, y - 1)  # 记录映射坐标点的新位置
            elif event.keysym == 'Down':  # 下方向键
                self.reference_canvas.move('point%d' % self.reference_landmarks_number, 0, 1)  # 圆形映射坐标点往下移动一个像素
                self.reference_canvas.move('text%d' % self.reference_landmarks_number, 0, 1)  # 对应坐标往下移动一个像素
                self.reference_landmarks[self.reference_landmarks_number] = (x, y + 1)  # 记录映射坐标点的新位置
            elif event.keysym == 'Left':  # 左方向键
                self.reference_canvas.move('point%d' % self.reference_landmarks_number, -1, 0)  # 圆形映射坐标点往左移动一个像素
                self.reference_canvas.move('text%d' % self.reference_landmarks_number, -1, 0)  # 对应坐标往左移动一个像素
                self.reference_landmarks[self.reference_landmarks_number] = (x - 1, y)  # 记录映射坐标点的新位置
            elif event.keysym == 'Right':  # 右方向键
                self.reference_canvas.move('point%d' % self.reference_landmarks_number, 1, 0)  # 圆形映射坐标点往右移动一个像素
                self.reference_canvas.move('text%d' % self.reference_landmarks_number, 1, 0)  # 对应坐标往右移动一个像素
                self.reference_landmarks[self.reference_landmarks_number] = (x + 1, y)  # 记录映射坐标点的新位置

    # 删除参考图像画布上当前最后一个映射坐标点
    def cancel_last_reference_landmark(self, event=None):
        if self.reference_landmarks_number != 0:  # 画布上存在映射坐标点，不存在则结束操作
            self.reference_canvas.delete('point%d' % self.reference_landmarks_number)  # 删除最后一个映射坐标点
            self.reference_canvas.delete('text%d' % self.reference_landmarks_number)  # 删除对应映射坐标点的序号
            del self.reference_landmarks[self.reference_landmarks_number]  # 删除记录中最后一个映射坐标点
            self.reference_landmarks_number -= 1  # 映射坐标点的数量减少1

    # 删除参考图像画布上所有映射坐标点
    def delete_all_reference_landmarks(self, event=None):
        for i in range(1, self.reference_landmarks_number + 1):  # 遍历所有映射坐标点的序号
            self.reference_canvas.delete('point%d' % i)  # 删除映射坐标点
            self.reference_canvas.delete('text%d' % i)  # 删除对应映射坐标点的序号
        self.reference_landmarks.clear()  # 清空映射坐标点记录
        self.reference_landmarks_number = 0  # 将映射坐标点的数量设为0

    # 渲染参考图像部分
    def render_reference_part(self):

        self.reference_label = tk.Label(
            self.window, text='Reference Image', font=('Helvetica', '20'), justify=tk.CENTER
        )  # 参考图像标签Reference Image
        self.reference_label.place(
            x=3 * self.WINDOW_WIDTH // 8, y=self.WINDOW_HEIGHT // 2 - 7 * self.WINDOW_WIDTH // 32,
            height=self.WINDOW_WIDTH // 16, width=self.WINDOW_WIDTH // 4
        )  # 参考图像标签的位置

        self.reference_canvas = tk.Canvas(self.window, bg='#D7D7D7', bd=2, relief=tk.RIDGE)  # 参考图像画布
        self.reference_canvas.place(
            x=3 * self.WINDOW_WIDTH // 8, y=self.WINDOW_HEIGHT // 2 - 5 * self.WINDOW_WIDTH // 32,
            height=self.WINDOW_WIDTH // 4, width=self.WINDOW_WIDTH // 4
        )  # 参考图像画布的位置

        self.open_reference_button = tk.Button(
            self.window, text='Open', font=('Helvetica', '15'), command=self.open_reference_image
        )  # 打开参考图像按钮Open
        self.open_reference_button.place(
            x=3 * self.WINDOW_WIDTH // 8, y=self.WINDOW_HEIGHT // 2 + 53 * self.WINDOW_WIDTH // 480,
            height=self.WINDOW_WIDTH // 36, width=3 * self.WINDOW_WIDTH // 40
        )  # 打开参考图像按钮的位置

        self.cancel_last_reference_landmark_button = tk.Button(
            self.window, text='Undo', font=('Helvetica', '15'), command=self.cancel_last_reference_landmark
        )  # 撤销映射坐标点按钮Undo
        self.cancel_last_reference_landmark_button.place(
            x=37 * self.WINDOW_WIDTH // 80, y=self.WINDOW_HEIGHT // 2 + 53 * self.WINDOW_WIDTH // 480,
            height=self.WINDOW_WIDTH // 36, width=3 * self.WINDOW_WIDTH // 40
        )  # 撤销映射坐标点按钮的位置

        self.delete_all_reference_landmarks_button = tk.Button(
            self.window, text='Reset', font=('Helvetica', '15'), command=self.delete_all_reference_landmarks
        )  # 重置映射坐标点按钮Reset
        self.delete_all_reference_landmarks_button.place(
            x=11 * self.WINDOW_WIDTH // 20, y=self.WINDOW_HEIGHT // 2 + 53 * self.WINDOW_WIDTH // 480,
            height=self.WINDOW_WIDTH // 36, width=3 * self.WINDOW_WIDTH // 40
        )  # 重置映射坐标点按钮的位置


    ###############
    # 结果图像部分 #
    ###############

    # 使用图像形变算法对原始图像按照参考图像进行空间变换，点击时会出现未响应的情况，等待片刻即可
    def transform(self):
        if self.original_image is None or self.reference_image is None:  # 未打开原始图像或参考图像
            messagebox.showerror('Error', 'No original image or reference image!')  # 弹出错误框告示未打开原始图像或参考图像
            return  # 操作结束
        elif self.original_landmarks_number != self.reference_landmarks_number:  # 原始图像与参考图像的映射坐标点数量不相等
            messagebox.showerror('Error', 'The number of landmarks is not equal!')  # 弹出错误框告示映射坐标点数量不相等
            return  # 操作结束
        elif self.original_landmarks_number == 0 or self.reference_landmarks_number == 0:  # 原始图像或参考图像的映射坐标点数量为0
            messagebox.showerror('Error', 'No landmarks!')  # 弹出错误框告示无映射坐标点
            return  # 操作结束
        else:  # 正常情况
            mapping = {
                self.reference_landmarks[num][::-1]: self.original_landmarks[num][::-1]
                for num in range(1, self.original_landmarks_number + 1)
            }  # 建立坐标映射关系
            # 实例化用于执行空间变换的图像变换器，参数为原始图像、参考图像、坐标映射关系与图像形变算法
            self.deformer = Transform(self.original_image, self.reference_image, mapping, self.transform_algorithm)
            start = time.time()  # 空间变换开始时的时间
            self.resultant_image = Image.fromarray(self.deformer.spatial_transform())  # 进行空间变换，将得到的结果图像转换为PIL.Image.Image格式
            end = time.time()  # 空间变换结束时的时间
            self.tk_resultant_image = ImageTk.PhotoImage(self.resultant_image)  # 将结果图像转换为可渲染格式
            self.resultant_canvas.create_image(0, 0, image=self.tk_resultant_image, anchor=tk.NW)  # 在画布上显示结果图像，以左上角为度量起点
            self.transform_execute_time.set('Execute time: %.2f s' % (end - start))  # 显示执行图像空间变换所需的时间

    # 渲染结果图像部分
    def render_resultant_part(self):

        self.resultant_label = tk.Label(
            self.window, text='Resultant Image', font=('Helvetica', '20'), justify=tk.CENTER
        )  # 结果图像标签Resultant Image
        self.resultant_label.place(
            x=11 * self.WINDOW_WIDTH // 16, y=self.WINDOW_HEIGHT // 2 - 7 * self.WINDOW_WIDTH // 32,
            height=self.WINDOW_WIDTH // 16, width=self.WINDOW_WIDTH // 4
        )  # 结果图像标签的位置

        self.resultant_canvas = tk.Canvas(self.window, bg='#D7D7D7', bd=2, relief=tk.RIDGE)  # 结果图像画布
        self.resultant_canvas.place(
            x=11 * self.WINDOW_WIDTH // 16, y=self.WINDOW_HEIGHT // 2 - 5 * self.WINDOW_WIDTH // 32,
            height=self.WINDOW_WIDTH // 4, width=self.WINDOW_WIDTH // 4
        )  # 结果图像画布的位置

        self.transform_button = tk.Button(
            self.window, text='Transform', font=('Helvetica', '15'), command=self.transform
        )  # 图像空间变换按钮Transform
        self.transform_button.place(
            x=11 * self.WINDOW_WIDTH // 16, y=self.WINDOW_HEIGHT // 2 + 53 * self.WINDOW_WIDTH // 480,
            height=self.WINDOW_WIDTH // 36, width=5 * self.WINDOW_WIDTH // 64
        )  # 图像空间变换按钮的位置

        self.transform_execute_time_label = tk.Label(
            self.window, textvariable=self.transform_execute_time, font=('Helvetica', '15'), relief=tk.GROOVE
        )  # 图像空间变换执行时间显示框
        self.transform_execute_time_label.place(
            x=25 * self.WINDOW_WIDTH // 32, y=self.WINDOW_HEIGHT // 2 + 53 * self.WINDOW_WIDTH // 480,
            height=self.WINDOW_WIDTH // 36, width=5 * self.WINDOW_WIDTH // 32
        )  # 图像空间变换执行时间显示框的位置


    #########
    # 主程序 #
    #########

    # 渲染主窗体
    def render(self):
        self.render_menu_bar()  # 渲染菜单栏部分
        self.render_original_part()  # 渲染原始图像部分
        self.render_reference_part()  # 渲染参考图像部分
        self.render_resultant_part()  # 渲染结果图像部分

    # 绑定鼠标及按键与操作指令的关系
    def binding(self):

        self.original_canvas.bind('<Button-1>', lambda x: self.original_canvas.focus_set())  # 鼠标左键单击原始图像画布：将原始图像画布设为焦点
        self.original_canvas.bind('<Double-Button-1>', self.set_original_landmarks)  # 鼠标左键双击原始图像画布：标记原始图像的映射坐标点，未打开原始图像时打开原始图像

        # 以下操作仅在原始图像为焦点时有效
        self.original_canvas.bind('<Key-Up>', self.move_last_original_landmark)  # 键盘上方向键：将原始图像画布上当前最后一个映射坐标点往上移动一个像素，
        self.original_canvas.bind('<Key-Down>', self.move_last_original_landmark)  # 键盘下方向键：将原始图像画布上当前最后一个映射坐标点往下移动一个像素
        self.original_canvas.bind('<Key-Left>', self.move_last_original_landmark)  # 键盘左方向键：将原始图像画布上当前最后一个映射坐标点往左移动一个像素
        self.original_canvas.bind('<Key-Right>', self.move_last_original_landmark)  # 键盘右方向键：将原始图像画布上当前最后一个映射坐标点往右移动一个像素
        self.original_canvas.bind('<Key-BackSpace>', self.cancel_last_original_landmark)  # 键盘退格键：将原始图像画布上当前最后一个映射坐标点删除
        self.original_canvas.bind('<Key-Delete>', self.delete_all_original_landmarks)  # 键盘删除键：将原始图像画布上所有映射坐标点删除

        self.reference_canvas.bind('<Button-1>', lambda x: self.reference_canvas.focus_set())  # 鼠标左键单击参考图像画布：将参考图像画布设为焦点
        self.reference_canvas.bind('<Double-Button-1>', self.set_reference_landmarks)  # 鼠标左键双击参考图像画布：标记参考图像的映射坐标点，未打开参考图像时打开参考图像

        # 以下操作仅在原始图像为焦点时有效
        self.reference_canvas.bind('<Key-Up>', self.move_last_reference_landmark)  # 键盘上方向键：将参考图像画布上当前最后一个映射坐标点往上移动一个像素
        self.reference_canvas.bind('<Key-Down>', self.move_last_reference_landmark)  # 键盘下方向键：将参考图像画布上当前最后一个映射坐标点往下移动一个像素
        self.reference_canvas.bind('<Key-Left>', self.move_last_reference_landmark)  # 键盘左方向键：将参考图像画布上当前最后一个映射坐标点往左移动一个像素
        self.reference_canvas.bind('<Key-Right>', self.move_last_reference_landmark)  # 键盘右方向键：将参考图像画布上当前最后一个映射坐标点往右移动一个像素
        self.reference_canvas.bind('<Key-BackSpace>', self.cancel_last_reference_landmark)  # 键盘退格键：将参考图像画布上当前最后一个映射坐标点删除
        self.reference_canvas.bind('<Key-Delete>', self.delete_all_reference_landmarks)  # 键盘删除键：将参考图像画布上所有映射坐标点删除

    # 运行交互程序
    def run(self):
        self.render()  # 渲染主窗体
        self.binding()  # 绑定鼠标及按键关系
        self.window.mainloop()  # 运行交互界面


class Transform:
    '''图像变换器，内含图像形变算法'''

    # 初始化
    def __init__(self, ori_image, ref_image, mapping, alg):

        self.ori_image_matrix = np.array(ori_image.convert('RGB'))  # 将原始图像转换成原始图像矩阵
        self.ori_image_shape = self.ori_image_matrix.shape  # 原始图像的形状
        self.ori_image_height, self.ori_image_width, _ = self.ori_image_shape  # 原始图像的高与宽
        self.ori_image_grid = (np.array(list(product(range(self.ori_image_height), range(self.ori_image_width))))).reshape(-1, 2)  # 原始图像的坐标矩阵

        self.ref_image_matrix = np.array(ref_image.convert('RGB'))  # 将参考图像转换成参考图像矩阵
        self.ref_image_shape = self.ref_image_matrix.shape  # 参考图像的形状
        self.ref_image_height, self.ref_image_width, _ = self.ref_image_shape  # 参考图像的高与宽
        self.ref_image_grid = (np.array(list(product(range(self.ref_image_height), range(self.ref_image_width))))).reshape(-1, 2)  # 参考图像的坐标矩阵

        self.mapping = mapping  # 坐标映射关系
        self.mapping_number = len(self.mapping)  # 映射坐标点数量
        self.mapping_region = np.array(list(map(list, self.mapping.keys())))  # 原始图像的映射坐标点
        self.mapping_result = np.array(list(map(list, self.mapping.values())))  # 结果图像的映射坐标点

        self.spatial_transform_algorithm = getattr(self, alg)  # 图像形变算法函数

    # 薄板样条形变算法 - Thin Plate Spline Interpolation Method
    def TPS(self):

        ###############
        # 计算形变函数 #
        ######################################################################################################################
        # Transformation:                 # Solution:                                     # Description:                     #
        #                                 #   _param_     _   gamma   _       _homolog_   #                                  #
        #  ori          Phi(ref)          #  |   W   |   | S   1  X  Y |^(-1)|  X'  Y' |  #  v(') = [x('); y(')]             #
        #  _|_   __________|____________  #  |   C   | = | 1T  0  0  0 |     |  0   0  |  #  r(v) = ||v||_2                  #
        #   v' = CT + AT @ v + WT @ s(v)  #  |_  A  _|   | XT  0  0  0 |     |  0   0  |  #  sigma(v) = r(v)^2 * ln(r(v)^2)  #
        #   |     |    |   |    |    |    #   (N+3)*2    |_YT  0  0  0_|     |_ 0   0 _|  #  si(v) = sigma(v - vi)           #
        #  2*1   2*1  2*2 2*1  2*N  N*1   #               (N+3)*(N+3)         (N+3)*2     #  Sij = sigma(vi - vj)            #
        #                                 #  Parameter =    Gamma^(-1)    @    Homolog    #                                  #
        ######################################################################################################################
        sigma = np.vectorize(lambda v: np.sum(v**2) * np.log(np.sum(v**2) + 1e-16), signature='(m)->()')  # 写出sigma([x;y])函数：sigma(v) = r(v)^2 * ln(r(v)^2)
        s = lambda v: sigma(self.mapping_region - v).reshape(-1, 1)  # 写出s([x; y])函数：s(v) = [sigma(v1 - v); ...; sigma(vn - v)]
        Gamma = np.vstack((
            np.hstack((
                sigma(  # sigma([v1, v1, ..., v1; ...; vn, vn, ..., vn] - [v1, v2, ..., vn; ...; v1, v2, ..., vn])
                    np.tile(self.mapping_region, (1, self.mapping_number)).reshape(self.mapping_number, self.mapping_number, 2) -
                    np.tile(self.mapping_region, (self.mapping_number, 1)).reshape(self.mapping_number, self.mapping_number, 2)
                ),  # gamma矩阵前n行前n列，子矩阵S，计算方法为Sij = sigma(vi - vj)
                np.ones((self.mapping_number, 1)), # gamma矩阵前n行第n+1列，列向量1，形式为[1, 1, ..., 1]^T
                self.mapping_region  # gamma矩阵前n行第n+2列第n+3列，列向量X, Y，形式为[x1, x2, ..., xn]^T, [y1, y2, ..., yn]^T
            )),
            np.hstack((
                np.vstack(
                    (
                        np.ones(self.mapping_number),  # gamma矩阵第n+1行前n列，行向量1T，形式为[1, 1, ..., 1]
                        self.mapping_region.T  # gamma矩阵第n+2行第n+3行前n列，列向量XT, YT，形式为[x1, x2, ..., xn], [y1, y2, ..., yn]
                    )
                ),
                np.zeros((3, 3))  # gamma矩阵右下角3*3零矩阵，形式为[0, 0, 0; 0, 0, 0; 0, 0, 0]
            ))
        ))  # 计算Gamma矩阵：Gamma = [S, 1, X, Y; 1T, 0, 0, 0; XT, 0, 0, 0; YT, 0, 0, 0]
        Homolog = np.vstack((
            self.mapping_result,  # Homolog矩阵前n行第1列第2列，列向量X', Y'，形式为[x1', x2', ..., xn']^T, [y1', y2', ..., yn']^T
            np.zeros((3, 2))  # Homolog矩阵下方3*2零矩阵，形式为[0, 0; 0, 0; 0, 0]
        ))  # 计算Homolog矩阵：Homolog = [X', Y'; 0, 0; 0, 0; 0, 0]
        Parameter = np.linalg.inv(Gamma) @ Homolog  # 计算Parameter矩阵：Parameter = Gamma^(-1) @ Homolog
        W, C, A = np.vsplit(Parameter, [self.mapping_number, self.mapping_number + 1])  # 得到形变函数系数：[W; C; A] = Parameter
        Phi = np.vectorize(lambda v: C.T + A.T @ v.reshape(-1, 1) + W.T @ s(v), signature='(m)->(n,k)')  # 得到薄板样条形变函数：[x'; y'] = Phi([x; y])

        ###############
        # 应用形变函数 #
        ###########################################################################
        #  [x', y'] = (Phi([x; y]))^T = (CT + AT @ [x'; y'] + WT @ s([x; y]]))^T  #
        ###########################################################################
        self.mapping_matrix = Phi(self.ref_image_grid).reshape(self.ref_image_height, self.ref_image_width, 2)  # 建立参考图像坐标至原始图像坐标的映射关系

    # 局部仿射形变算法 - Locally Affine Registration Method
    def LARM(self):

        ###############
        # 计算形变矩阵 #
        #######################################################
        # Transformation:                      # Solution:    #
        #   _ ori _     _    T    _  _ ref _   #              #
        #  |   x'  |   | 1   0   a ||   x   |  #  a = x' - x  #
        #  |       | = |           ||   y   |  #              #
        #  |_  y' _|   |_0   1   b_||_  1  _|  #  b = y' - y  #
        #     2*1           2*3        3*1     #              #
        #######################################################
        translation = (self.mapping_result - self.mapping_region).reshape(-1, 1)  # 形变矩阵平移部分，形式为[a; b]
        shear = np.tile(np.array([[1, 0], [0, 1]]), (self.mapping_number, 1))  # 形变矩阵错切部分，形式为[1, 0; 0, 1]
        transformation = np.hstack((shear, translation)).reshape(-1, 2, 3)  # 合并得到仿射形变矩阵，形式为[1, 0, a; 0, 1, b]

        ###############
        # 应用形变函数 #
        ###################################################
        #  [x', y'] = (T @ [x; y; 1])^T = [x + a, y + b]  #
        ###################################################
        e = 2  # 距离指数
        self.mapping_matrix = np.zeros([self.ref_image_height, self.ref_image_width, 2])  # 建立参考图像坐标至原始图像坐标的映射关系
        for h in range(self.ref_image_height):  # 遍历参考图像垂直方向
            for w in range(self.ref_image_width):  # 遍历参考图像水平方向
                if (h, w) in self.mapping:  # 当前坐标点为映射坐标点
                    self.mapping_matrix[h, w] = self.mapping[(h, w)]  # 直接使用坐标映射关系得到结果坐标
                else:  # 当前坐标点为非映射坐标点
                    weights = np.power(np.linalg.norm(self.mapping_region - np.array([h, w]), axis=1), -e)  # 计算所有局部仿射形变矩阵的权重
                    self.mapping_matrix[h, w] = np.array([h, w, 1]) @ np.average(transformation, axis=0, weights=weights).T  # 将加权局部仿射形变矩阵作用于参考图像坐标

    '''此处添加更多算法
    # 更多算法
    def more_algorithm(self):
        pass
    '''

    # 反向图像空间变换算法
    def backward_warp(self):

        # 三次样条插值得到对应值
        R_matrix = griddata(self.ori_image_grid, self.ori_image_matrix[:, :, 0].reshape(-1), self.mapping_matrix, method='cubic').astype(np.uint8)  # R通道
        G_matrix = griddata(self.ori_image_grid, self.ori_image_matrix[:, :, 1].reshape(-1), self.mapping_matrix, method='cubic').astype(np.uint8)  # G通道
        B_matrix = griddata(self.ori_image_grid, self.ori_image_matrix[:, :, 2].reshape(-1), self.mapping_matrix, method='cubic').astype(np.uint8)  # B通道

        # 合并为彩色图像矩阵
        return np.hstack((R_matrix.reshape(-1, 1), G_matrix.reshape(-1, 1), B_matrix.reshape(-1, 1))).reshape(self.ref_image_height, self.ref_image_width, 3)

    # 执行图像空间变换
    def spatial_transform(self):
        self.spatial_transform_algorithm()  # 使用图像形变算法对图像执行形变
        return self.backward_warp()  # 使用反向变换算法对图像执行变换，返回得到的结果图像


if __name__ == '__main__':
    GUI().run()  # 主函数入口
