import os  # 文件

import vtk  # 可视化

########
# PATH #
########

# 注意：所有路径必须为全英文！！！
HOME_PATH = os.getcwd()  # 主目录
DATA_PATH = os.path.join(HOME_PATH, 'data')  # 数据目录
RESULT_PATH = os.path.join(HOME_PATH, 'result')  # 结果目录

##########
# SOURCE #
##########

source = vtk.vtkNIFTIImageReader()  # 数据源
source.SetFileName(os.path.join(DATA_PATH, 'brain.nii.gz'))  # 读取体数据

############################
# TRANSFER FUNCTION: OUTER #
############################

########## color transfer function ##########

color_transfer_function_outer = vtk.vtkColorTransferFunction()  # 颜色传输函数
color_transfer_function_outer.AddRGBPoint(0, 0.4, 0.6, 1.0)
color_transfer_function_outer.AddRGBPoint(300, 0.4, 0.6, 1.0)
color_transfer_function_outer.AddRGBPoint(560, 0.9, 0.9, 0.9)

########## opacity transfer function ##########

opacity_transfer_function_outer = vtk.vtkPiecewiseFunction()  # 透明度传输函数
opacity_transfer_function_outer.AddPoint(0, 0.0)
opacity_transfer_function_outer.AddPoint(150, 0.0)
opacity_transfer_function_outer.AddPoint(500, 0.9)
opacity_transfer_function_outer.AddPoint(560, 0.9)
opacity_transfer_function_outer.AddPoint(650, 0.0)

########## gradient transfer function ##########

gradient_transfer_function_outer = vtk.vtkPiecewiseFunction()  # 梯度传输函数
gradient_transfer_function_outer.AddPoint(0, 0.0)
gradient_transfer_function_outer.AddPoint(100, 0.8)
gradient_transfer_function_outer.AddPoint(500, 1.1)
gradient_transfer_function_outer.AddPoint(700, 0.2)

########## property ##########

volume_property_outer = vtk.vtkVolumeProperty()  # 性质：外部体元素
volume_property_outer.SetColor(color_transfer_function_outer)  # 设定颜色传输函数
volume_property_outer.SetScalarOpacity(opacity_transfer_function_outer)  # 设定透明度传输函数
volume_property_outer.SetGradientOpacity(gradient_transfer_function_outer)  # 设定梯度传输函数
volume_property_outer.SetInterpolationTypeToLinear()  # 增强渲染效果
volume_property_outer.ShadeOn()  # 打开阴影
volume_property_outer.SetAmbient(1.0)  # 设定环境光系数
volume_property_outer.SetDiffuse(1.0)  # 设定散射光系数
volume_property_outer.SetSpecular(1.0)  # 设定反射光系数
volume_property_outer.SetSpecularPower(100)  # 设定反射光强

############################
# TRANSFER FUNCTION: INNER #
############################

########## color transfer function ##########

color_transfer_function_inner = vtk.vtkColorTransferFunction()  # 颜色传输函数
color_transfer_function_inner.AddRGBPoint(0, 1.0, 0.3, 0.5)
color_transfer_function_inner.AddRGBPoint(1000, 1.0, 0.3, 0.5)

########## opacity transfer function ##########

opacity_transfer_function_inner = vtk.vtkPiecewiseFunction()  # 透明度传输函数
opacity_transfer_function_inner.AddPoint(0, 0.6)
opacity_transfer_function_inner.AddPoint(450, 0.6)
opacity_transfer_function_inner.AddPoint(451, 0.0)

########## gradient transfer function ##########

gradient_transfer_function_inner = vtk.vtkPiecewiseFunction()  # 梯度传输函数
gradient_transfer_function_inner.AddPoint(0, 0.0)
gradient_transfer_function_inner.AddPoint(100, 5.0)

########## property ##########

volume_property_inner = vtk.vtkVolumeProperty()  # 性质：内部体元素
volume_property_inner.SetColor(color_transfer_function_inner)  # 设定颜色传输函数
volume_property_inner.SetScalarOpacity(opacity_transfer_function_inner)  # 设定透明度传输函数
volume_property_inner.SetGradientOpacity(gradient_transfer_function_inner)  # 设定梯度传输函数
volume_property_inner.SetInterpolationTypeToLinear()  # 增强渲染效果
volume_property_inner.ShadeOn()  # 打开阴影
volume_property_inner.SetAmbient(0.8)  # 设定环境光系数
volume_property_inner.SetDiffuse(0.8)  # 设定散射光系数
volume_property_inner.SetSpecular(0.8)  # 设定反射光系数
volume_property_inner.SetSpecularPower(10)  # 设定反射光强

##########
# FILTER #
##########

# VOI
source_inner = vtk.vtkExtractVOI()  # 过滤器：感兴趣区域
source_inner.SetInputConnection(source.GetOutputPort())  # 读取数据源
source_inner.SetVOI(100, 155, 75, 180, 47, 70)  # 划定区域
source_inner.SetSampleRate(1, 1, 1)  # 设定采样率

# CLIPPER
plane_filter = vtk.vtkPlane()  # 过滤器：切割面
plane_filter.SetOrigin(140, 127.5, 61.5)  # 设定原点
plane_filter.SetNormal(-1, 0, 0)  # 设定法向

# OUTLINE
outline_filter = vtk.vtkOutlineFilter()  # 过滤器：边框
outline_filter.SetInputConnection(source.GetOutputPort())  # 读取数据源

##########
# MAPPER #
##########

# VOLUME: outer
volume_mapper_outer = vtk.vtkFixedPointVolumeRayCastMapper()  # 映射器：外部体元素
volume_mapper_outer.SetInputConnection(source.GetOutputPort())  # 读取数据源
volume_mapper_outer.AddClippingPlane(plane_filter)  # 切割体元素

# VOLUME: inner
volume_mapper_inner = vtk.vtkFixedPointVolumeRayCastMapper()  # 映射器：内部体元素
volume_mapper_inner.SetInputConnection(source_inner.GetOutputPort())  # 读取数据源

# OUTLINE
outline_mapper = vtk.vtkPolyDataMapper()  # 映射器：边框
outline_mapper.SetInputConnection(outline_filter.GetOutputPort())  # 读取过滤器：边框

#########
# ACTOR #
#########

# VOLUME: outer
volume_actor_outer = vtk.vtkVolume()  # 演员：外部体元素
volume_actor_outer.SetMapper(volume_mapper_outer)  # 读取映射器：外部体元素
volume_actor_outer.SetProperty(volume_property_outer)  # 读取性质：外部体元素
volume_actor_outer.RotateX(90)  # 设定X轴旋转
volume_actor_outer.SetScale(1.2, 1.2, 1.2)  # 设定缩放

# VOLUME: inner
volume_actor_inner = vtk.vtkVolume()  # 演员：内部体元素
volume_actor_inner.SetMapper(volume_mapper_inner)  # 读取映射器：内部体元素
volume_actor_inner.SetProperty(volume_property_inner)  # 读取性质：内部体元素
volume_actor_inner.RotateX(90)  # 设定X轴旋转
volume_actor_inner.SetScale(1.2, 1.2, 1.2)  # 设定缩放

# OUTLINE
outline_actor = vtk.vtkActor()  # 演员：边框
outline_actor.SetMapper(outline_mapper)  # 读取映射器：边框
outline_actor.GetProperty().SetColor(0.5, 0.5, 0.5)  # 设定颜色
outline_actor.GetProperty().SetLineWidth(2.0)  # 设定宽度
outline_actor.RotateX(90)  # 设定X轴旋转
outline_actor.SetScale(1.2, 1.2, 1.2)  # 设定缩放

############
# RENDERER #
############

renderer = vtk.vtkRenderer()  # 渲染器
renderer.AddVolume(volume_actor_outer)  # 读取演员：外部体元素
renderer.AddVolume(volume_actor_inner)  # 读取演员：内部体元素
renderer.AddActor(outline_actor)  # 读取演员：边框
renderer.SetBackground(0.8, 0.8, 0.8)  # 设定背景颜色

##########
# WINDOW #
##########

window = vtk.vtkRenderWindow()  # 窗口
window.AddRenderer(renderer)  # 读取渲染器
window.Render()  # 渲染窗口
renderer.GetActiveCamera().Azimuth(90)  # 设定视角
window.SetSize(750, 750)  # 设定窗口大小
window.SetWindowName('Volume Rendering')  # 设定窗口名称

########
# SAVE #
########

writer_filter = vtk.vtkWindowToImageFilter()  # 过滤器：截图
writer_filter.SetInput(window)  # 读取窗口
writer = vtk.vtkPNGWriter()  # 图像生成器
writer.SetFileName(os.path.join(RESULT_PATH, 'volume_render.png'))  # 设定图像路径
writer.SetInputConnection(writer_filter.GetOutputPort())  # 读取窗口截图
writer.Write()  # 保存图片

##############
# INTERACTOR #
##############

def key_handle(obj, event):  # 按键交互功能

    key = obj.GetKeySym()  # 获取按键值

    # 自动旋转
    # 注意：旋转过程结束前不能进行交互！
    if key == 'Return':  # Enter键
        for _ in range(72):
            renderer.GetActiveCamera().Azimuth(5)  # 顺时针旋转
            window.Render()  # 渲染窗口

    # 手动旋转（调试用）
    elif key == 'Up':  # Up键
        renderer.GetActiveCamera().Elevation(5)  # 向上旋转
        print('Up')  # 打印调试信息
        window.Render()
    elif key == 'Down':  # Up键
        renderer.GetActiveCamera().Elevation(-5)  # 向下旋转
        print('Down')  # 打印调试信息
        window.Render()
    elif key == 'Left':  # Up键
        renderer.GetActiveCamera().Azimuth(5)  # 向左旋转
        print('Left')  # 打印调试信息
        window.Render()
    elif key == 'Right':  # Up键
        renderer.GetActiveCamera().Azimuth(-5)  # 向右旋转
        print('Right')  # 打印调试信息
        window.Render()

interactor = vtk.vtkRenderWindowInteractor()  # 交互器
interactor.SetRenderWindow(window)  # 读取窗口
interactor.AddObserver('KeyPressEvent', key_handle)  # 绑定按键功能
interactor.Initialize()  # 初始化交互器
interactor.Start()  # 运行交互器
