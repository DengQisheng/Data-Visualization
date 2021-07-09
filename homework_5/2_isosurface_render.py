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

##########
# FILTER #
##########

########## inner ##########

# VOI
source_inner = vtk.vtkExtractVOI()  # 过滤器：感兴趣区域
source_inner.SetInputConnection(source.GetOutputPort())  # 读取数据源
source_inner.SetVOI(95, 160, 75, 180, 47, 76)  # 划定区域
source_inner.SetSampleRate(1, 1, 1)  # 设定采样率

# EXTRACTOR
filter_extractor_inner = vtk.vtkMarchingCubes()  # 过滤器：三角面片
filter_extractor_inner.SetInputConnection(source_inner.GetOutputPort())  # 读取数据源
filter_extractor_inner.ComputeNormalsOn()  # 计算等值面法向量以增强渲染效果
filter_extractor_inner.SetValue(0, 380)  # 设定内部等值面

# STRIPPER
filter_isosurface_inner = vtk.vtkStripper()  # 过滤器：等值面
filter_isosurface_inner.SetInputConnection(filter_extractor_inner.GetOutputPort())  # 读取过滤器：三角面片

########## median ##########

# EXTRACTOR
filter_extractor_median = vtk.vtkMarchingCubes()  # 过滤器：三角面片
filter_extractor_median.SetInputConnection(source.GetOutputPort())  # 读取数据源
filter_extractor_median.ComputeNormalsOn()  # 计算等值面法向量以增强渲染效果
filter_extractor_median.SetValue(0, 500)  # 设定中部等值面

# STRIPPER
filter_isosurface_median = vtk.vtkStripper()  # 过滤器：等值面
filter_isosurface_median.SetInputConnection(filter_extractor_median.GetOutputPort())  # 读取过滤器：三角面片

# CLIPPER
filter_plane_median = vtk.vtkPlane()  # 过滤器：切割面
filter_plane_median.SetOrigin(140, 127.5, 61.5)  # 设定原点
filter_plane_median.SetNormal(-1, 0, 0)  # 设定法向

########## outer ##########

# EXTRACTOR
filter_extractor_outer = vtk.vtkMarchingCubes()  # 过滤器：三角面片
filter_extractor_outer.SetInputConnection(source.GetOutputPort())  # 读取数据源
filter_extractor_outer.ComputeNormalsOn()  # 计算等值面法向量以增强渲染效果
filter_extractor_outer.SetValue(0, 10)  # 设定外部等值面

# STRIPPER
filter_isosurface_outer = vtk.vtkStripper()  # 过滤器：等值面
filter_isosurface_outer.SetInputConnection(filter_extractor_outer.GetOutputPort())  # 读取过滤器：三角面片

########## outline ##########

# OUTLINE
filter_outline = vtk.vtkOutlineFilter()  # 过滤器：边框
filter_outline.SetInputConnection(source.GetOutputPort())  # 读取数据源

##########
# Mapper #
##########

# STRIPPER: inner
mapper_isosurface_inner = vtk.vtkPolyDataMapper()  # 映射器：等值面
mapper_isosurface_inner.SetInputConnection(filter_isosurface_inner.GetOutputPort())  # 读取过滤器：等值面
mapper_isosurface_inner.ScalarVisibilityOff()  # 关闭颜色映射关系

# STRIPPER: median
mapper_isosurface_median = vtk.vtkPolyDataMapper()  # 映射器：等值面
mapper_isosurface_median.SetInputConnection(filter_isosurface_median.GetOutputPort())  # 读取过滤器：等值面
mapper_isosurface_median.ScalarVisibilityOff()  # 关闭颜色映射关系
mapper_isosurface_median.AddClippingPlane(filter_plane_median)  # 切割等值面

# STRIPPER: outer
mapper_isosurface_outer = vtk.vtkPolyDataMapper()  # 映射器：等值面
mapper_isosurface_outer.SetInputConnection(filter_isosurface_outer.GetOutputPort())  # 读取过滤器：等值面
mapper_isosurface_outer.ScalarVisibilityOff()  # 关闭颜色映射关系

# OUTLINE
mapper_outline = vtk.vtkPolyDataMapper()  # 映射器：边框
mapper_outline.SetInputConnection(filter_outline.GetOutputPort())  # 读取过滤器：边框

#########
# ACTOR #
#########

# STRIPPER: inner
actor_isosurface_inner = vtk.vtkActor()  # 演员：等值面
actor_isosurface_inner.SetMapper(mapper_isosurface_inner)  # 读取映射器：等值面
actor_isosurface_inner.GetProperty().SetColor(0.5, 0.5, 1.0)  # 设定颜色
actor_isosurface_inner.GetProperty().SetAmbient(0.4)  # 设定环境光系数
actor_isosurface_inner.GetProperty().SetDiffuse(0.6)  # 设定散射光系数
actor_isosurface_inner.GetProperty().SetSpecular(0.5)  # 设定反射光系数
actor_isosurface_inner.GetProperty().SetOpacity(1.0)  # 设定透射光系数
actor_isosurface_inner.RotateX(90)  # 设定X轴旋转
actor_isosurface_inner.SetScale(1.2, 1.2, 1.2)  # 设定缩放

# STRIPPER: median
actor_isosurface_median = vtk.vtkActor()  # 演员：等值面
actor_isosurface_median.SetMapper(mapper_isosurface_median)  # 读取映射器：等值面
actor_isosurface_median.GetProperty().SetColor(0.95, 0.95, 0.95)  # 设定颜色
actor_isosurface_median.GetProperty().SetAmbient(0.4)  # 设定环境光系数
actor_isosurface_median.GetProperty().SetDiffuse(0.6)  # 设定散射光系数
actor_isosurface_median.GetProperty().SetSpecular(0.6)  # 设定反射光系数
actor_isosurface_median.GetProperty().SetSpecularPower(1000)  # 设定反射光强
actor_isosurface_median.GetProperty().SetOpacity(1.0)  # 设定透射光系数
actor_isosurface_median.RotateX(90)  # 设定X轴旋转
actor_isosurface_median.SetScale(1.2, 1.2, 1.2)  # 设定缩放

# STRIPPER: outer
actor_isosurface_outer = vtk.vtkActor()  # 演员：等值面
actor_isosurface_outer.SetMapper(mapper_isosurface_outer)  # 读取映射器：等值面
actor_isosurface_outer.GetProperty().SetColor(1.0, 0.4, 0.4)  # 设定颜色
actor_isosurface_outer.GetProperty().SetAmbient(0.3)  # 设定环境光系数
actor_isosurface_outer.GetProperty().SetDiffuse(0.6)  # 设定散射光系数
actor_isosurface_outer.GetProperty().SetSpecular(0.8)  # 设定反射光系数
actor_isosurface_outer.GetProperty().SetOpacity(0.2)  # 设定透射光系数
actor_isosurface_outer.RotateX(90)  # 设定X轴旋转
actor_isosurface_outer.SetScale(1.2, 1.2, 1.2)  # 设定缩放

# OUTLINE
actor_outline = vtk.vtkActor()  # 演员：边框
actor_outline.SetMapper(mapper_outline)  # 读取映射器：边框
actor_outline.GetProperty().SetColor(0.5, 0.5, 0.5)  # 设定颜色
actor_outline.GetProperty().SetLineWidth(2.0)  # 设定宽度
actor_outline.RotateX(90)  # 设定X轴旋转
actor_outline.SetScale(1.2, 1.2, 1.2)  # 设定缩放

############
# RENDERER #
############

renderer = vtk.vtkRenderer()  # 渲染器
renderer.AddActor(actor_isosurface_inner)  # 读取演员：内部等值面
renderer.AddActor(actor_isosurface_median)  # 读取演员：中部等值面
renderer.AddActor(actor_isosurface_outer)  # 读取演员：外部等值面
renderer.AddActor(actor_outline)  # 读取演员：边框
renderer.SetBackground(0.8, 0.8, 0.8)  # 设定背景颜色

##########
# WINDOW #
##########

window = vtk.vtkRenderWindow()  # 窗口
window.AddRenderer(renderer)  # 读取渲染器
window.Render()  # 渲染窗口
renderer.GetActiveCamera().Azimuth(90)  # 设定视角
window.SetSize(750, 750)  # 设定窗口大小
window.SetWindowName('Isosurface Rendering')  # 设定窗口名称

########
# SAVE #
########

writer_filter = vtk.vtkWindowToImageFilter()  # 过滤器：截图
writer_filter.SetInput(window)  # 读取窗口
writer = vtk.vtkPNGWriter()  # 图像生成器
writer.SetFileName(os.path.join(RESULT_PATH, 'isosurface_render.png'))  # 设定图像路径
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
        for _ in range(360):
            renderer.GetActiveCamera().Azimuth(1)  # 顺时针旋转
            window.Render()  # 渲染窗口

    # 动态调整位置（调试用）
    elif key == 'Up':  # 上方向键
        actor_isosurface_inner.AddPosition(0, 1, 0)  # 偏置为一
        print('bias + 1')  # 打印调试信息
        window.Render()  # 渲染窗口
    elif key == 'Down':  # 下方向键
        actor_isosurface_inner.AddPosition(0, -1, 0)  # 偏置为负一
        print('bias - 1')  # 打印调试信息
        window.Render()  # 渲染窗口

    # 动态显示等值面值（调试用）
    elif key == 'Right':  # 右方向键
        iso_value = filter_extractor_inner.GetValue(0)  # 获取等值面值
        iso_value += 10  # 等值面值加十
        print('isosurface value =', iso_value)  # 打印调试信息
        filter_extractor_inner.SetValue(0, iso_value)  # 调整等值面值
        window.Render()  # 渲染窗口
    elif key == 'Left':  # 左方向键
        iso_value = filter_extractor_inner.GetValue(0)  # 获取等值面值
        iso_value -= 10  # 等值面值减十
        print('isosurface value =', iso_value)  # 打印调试信息
        filter_extractor_inner.SetValue(0, iso_value)  # 调整等值面值
        window.Render()  # 渲染窗口

interactor = vtk.vtkRenderWindowInteractor()  # 交互器
interactor.SetRenderWindow(window)  # 读取窗口
interactor.AddObserver('KeyPressEvent', key_handle)  # 绑定按键功能
interactor.Initialize()  # 初始化交互器
interactor.Start()  # 运行交互器
